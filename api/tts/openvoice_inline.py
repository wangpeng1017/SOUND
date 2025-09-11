# 内联的OpenVoice TTS服务（避免导入问题）
import httpx
import base64
import uuid
import os
from typing import Optional, Dict, Any

OPENVOICE_SPACES = ["https://myshell-openvoice-openvoice-v2.hf.space"]
EDGE_TTS_ENABLED = True

async def text_to_speech_inline(
    text: str,
    voice_id: str = "default", 
    reference_audio_url: Optional[str] = None
) -> Dict[str, Any]:
    """简化的TTS实现"""
    
    # 如果有参考音频，尝试OpenVoice
    if reference_audio_url and voice_id != "default":
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 下载参考音频
                ref_resp = await client.get(reference_audio_url)
                if ref_resp.status_code == 200:
                    ref_audio = ref_resp.content
                    
                    # 调用OpenVoice Space
                    payload = {
                        "fn_index": 0,
                        "data": [
                            text,
                            "zh",
                            {
                                "name": "ref.wav",
                                "data": f"data:audio/wav;base64,{base64.b64encode(ref_audio).decode()}"
                            },
                            1.0,
                            "default"
                        ]
                    }
                    
                    for space_url in OPENVOICE_SPACES:
                        try:
                            api_url = f"{space_url}/api/predict"
                            resp = await client.post(api_url, json=payload)
                            
                            if resp.status_code == 200:
                                result = resp.json()
                                if "data" in result and result["data"]:
                                    audio_data = result["data"][0]
                                    
                                    # 如果是base64音频
                                    if isinstance(audio_data, str) and audio_data.startswith("data:audio"):
                                        base64_audio = audio_data.split(",")[1]
                                        audio_bytes = base64.b64decode(base64_audio)
                                        
                                        # 上传到Blob
                                        token = os.getenv("BLOB_READ_WRITE_TOKEN")
                                        if token:
                                            blob_name = f"tts/audio_{uuid.uuid4().hex}.wav"
                                            blob_resp = await client.put(
                                                "https://blob.vercel-storage.com",
                                                headers={
                                                    "authorization": f"Bearer {token}",
                                                    "x-content-type": "audio/wav",
                                                },
                                                params={"filename": blob_name},
                                                content=audio_bytes,
                                            )
                                            if blob_resp.status_code == 200:
                                                blob_url = blob_resp.json().get("url")
                                                return {
                                                    "success": True,
                                                    "audio_url": blob_url,
                                                    "method": "openvoice"
                                                }
                                    
                                    # 如果是URL
                                    elif isinstance(audio_data, str) and audio_data.startswith("http"):
                                        return {
                                            "success": True,
                                            "audio_url": audio_data,
                                            "method": "openvoice"
                                        }
                        except Exception as e:
                            print(f"OpenVoice失败: {e}")
                            continue
        except Exception as e:
            print(f"OpenVoice处理错误: {e}")
    
    # 尝试Edge TTS
    if EDGE_TTS_ENABLED:
        try:
            import edge_tts
            voice = "zh-CN-XiaoxiaoNeural"
            communicate = edge_tts.Communicate(text, voice)
            tmp = f"/tmp/edge_{uuid.uuid4().hex}.mp3"
            await communicate.save(tmp)
            
            with open(tmp, "rb") as f:
                audio_data = f.read()
            os.remove(tmp)
            
            # 上传到Blob
            token = os.getenv("BLOB_READ_WRITE_TOKEN")
            if token:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    blob_name = f"tts/edge_{uuid.uuid4().hex}.mp3"
                    blob_resp = await client.put(
                        "https://blob.vercel-storage.com",
                        headers={
                            "authorization": f"Bearer {token}",
                            "x-content-type": "audio/mpeg",
                        },
                        params={"filename": blob_name},
                        content=audio_data,
                    )
                    if blob_resp.status_code == 200:
                        blob_url = blob_resp.json().get("url")
                        return {
                            "success": True,
                            "audio_url": blob_url,
                            "method": "edge-tts"
                        }
        except Exception as e:
            print(f"Edge TTS失败: {e}")
    
    # 回退到dummy音频
    return {
        "success": True,
        "audio_url": "/api/audio/dummy.wav",
        "method": "dummy"
    }
