# OpenVoice v2 TTS 服务
# 使用 Hugging Face Spaces 的公开 Demo 进行语音克隆
import os
import httpx
import json
import base64
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

# 公开的 OpenVoice v2 Spaces（可根据可用性调整）
OPENVOICE_SPACES = [
    "https://myshell-openvoice-openvoice-v2.hf.space",
    # 可追加更多公开Space作为备选
]

# Edge TTS 作为备用方案（可选）
EDGE_TTS_ENABLED = True  # 启用Edge TTS作为备用方案

class OpenVoiceTTSService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")

    async def close(self):
        await self.client.aclose()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "default",
        reference_audio_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文字转语音主入口
        
        Args:
            text: 要合成的文本
            voice_id: 音色ID
            reference_audio_url: 参考音频URL（用于语音克隆）
            
        Returns:
            包含音频URL和任务信息的字典
        """
        try:
            # 如果是默认音色或没有参考音频，使用Edge TTS
            if voice_id == "default" or not reference_audio_url:
                if EDGE_TTS_ENABLED:
                    return await self._edge_tts_fallback(text)
                else:
                    return await self._generate_dummy_audio(text)
            
            # 使用OpenVoice进行语音克隆
            audio_url = await self._openvoice_synthesis(text, reference_audio_url)
            
            if audio_url:
                return {
                    "success": True,
                    "audio_url": audio_url,
                    "method": "openvoice",
                    "voice_id": voice_id
                }
            
            # 如果OpenVoice失败，回退到Edge TTS
            if EDGE_TTS_ENABLED:
                return await self._edge_tts_fallback(text)
            else:
                return await self._generate_dummy_audio(text)
                
        except Exception as e:
            print(f"TTS服务错误: {str(e)}")
            # 最终回退到dummy音频
            return await self._generate_dummy_audio(text)
    
    async def _openvoice_synthesis(
        self, 
        text: str, 
        reference_audio_url: str
    ) -> Optional[str]:
        """
        使用 OpenVoice v2 Space 进行语音克隆合成
        """
        for space_url in OPENVOICE_SPACES:
            try:
                # 1) 下载参考音频
                ref_audio = await self._download(reference_audio_url)
                if not ref_audio:
                    continue

                # 2) 组装 Gradio /api/predict 参数
                # 注意：不同 Space 的 fn_index/data 结构可能略有差异
                payload = {
                    "fn_index": 0,
                    "data": [
                        text,
                        "zh",  # 语言
                        {
                            "name": "ref.wav",
                            "data": "data:audio/wav;base64," + base64.b64encode(ref_audio).decode(),
                        },
                        1.0,  # 语速
                        "default",  # 风格
                    ],
                }

                api_url = f"{space_url}/api/predict"
                resp = await self.client.post(api_url, json=payload, headers={"Content-Type": "application/json"})
                if resp.status_code != 200:
                    print(f"OpenVoice Space 返回 {resp.status_code}")
                    continue

                result = resp.json()
                # 解析返回。常见返回结构中 data[0] 可能是 base64 音频或 URL
                if isinstance(result, dict) and "data" in result and result["data"]:
                    first = result["data"][0]
                    if isinstance(first, str):
                        if first.startswith("data:audio"):
                            # base64 音频
                            base64_audio = first.split(",", 1)[1]
                            audio_bytes = base64.b64decode(base64_audio)
                            return await self._upload_blob(audio_bytes, "audio/wav")
                        if first.startswith("http"):
                            # 直接 URL
                            return first
                
            except Exception as e:
                print(f"调用 OpenVoice Space 失败: {e}")
                continue
        return None
    
    async def _edge_tts_fallback(self, text: str) -> Dict[str, Any]:
        try:
            import edge_tts  # 仅在启用时使用
            voice = "zh-CN-XiaoxiaoNeural"
            communicate = edge_tts.Communicate(text, voice)
            tmp = f"/tmp/edge_{uuid.uuid4().hex}.mp3"
            await communicate.save(tmp)
            with open(tmp, "rb") as f:
                data = f.read()
            os.remove(tmp)
            url = await self._upload_blob(data, "audio/mpeg")
            if url:
                return {"success": True, "audio_url": url, "method": "edge-tts"}
        except Exception as e:
            print(f"Edge TTS 回退失败: {e}")
        return await self._generate_dummy_audio(text)
    
    async def _generate_dummy_audio(self, text: str) -> Dict[str, Any]:
        """
        生成占位音频（最终备用）
        """
        return {
            "success": True,
            "audio_url": "/api/audio/dummy.wav",
            "method": "dummy",
            "voice_id": "default"
        }
    
    async def _download_audio(self, url: str) -> Optional[bytes]:
        """
        下载音频文件
        """
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"下载音频失败: {str(e)}")
        return None
    
    async def _upload_to_blob(
        self, 
        data: bytes, 
        content_type: str = "audio/wav"
    ) -> Optional[str]:
        """
        上传音频到Vercel Blob Storage
        """
        if not self.blob_token:
            # 如果没有Blob token，返回本地URL
            return f"/api/audio/generated_{uuid.uuid4().hex}.wav"
        
        try:
            filename = f"tts/audio_{uuid.uuid4().hex}.wav"
            
            response = await self.client.put(
                "https://blob.vercel-storage.com",
                headers={
                    "authorization": f"Bearer {self.blob_token}",
                    "x-content-type": content_type,
                },
                params={"filename": filename},
                content=data,
                timeout=30.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("url")
                
        except Exception as e:
            print(f"上传到Blob失败: {str(e)}")
        
        return None

# 单例实例
tts_service = OpenVoiceTTSService()
