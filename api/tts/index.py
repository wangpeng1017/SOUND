from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid
import httpx
import os
from typing import Optional, List
import logging

# 禁用httpx的INFO日志
logging.getLogger("httpx").setLevel(logging.WARNING)

# 引入内联OpenVoice实现（避免导入问题）
from .openvoice_inline import text_to_speech_inline
# 尝试导入voices模块中的内存数据库（同一无服务器实例内可用）
try:
    from ..voices.index import user_voices_db  # type: ignore
except Exception:
    user_voices_db = {}

app = FastAPI(title="TTS API", version="0.2.0 (openvoice)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice_id: str | None = None

# 简易内存任务表
_tasks = {}

# 从 voices API 获取音色列表
async def _get_voices() -> Optional[List[dict]]:
    """从内部voices API获取音色列表"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 调用内部API
            r = await client.get("http://localhost:3000/api/voices")
            if r.status_code == 200:
                data = r.json()
                if data.get("success") and data.get("data"):
                    return data["data"]
    except Exception:
        pass
    return None

# 系统预设音色映射
SYSTEM_VOICE_MAPPING = {
    "teacher-female": "zh-CN-XiaoxiaoNeural",  # 女老师
    "teacher-male": "zh-CN-YunxiNeural",        # 男老师
    "mom": "zh-CN-XiaohanNeural",               # 妈妈
    "dad": "zh-CN-YunjianNeural",               # 爸爸
    "default": "zh-CN-XiaoxiaoNeural"           # 默认
}

async def _get_reference_audio_url(voice_id: str) -> Optional[str]:
    # 系统音色不需要参考音频
    if voice_id in SYSTEM_VOICE_MAPPING:
        return None
        
    # 从内存数据库获取用户音色的参考音频
    # 注意：由于无服务器函数是独立的，内存不共享
    # 所以目前暂时禁用自定义音色，只使用系统音色
    voice = user_voices_db.get(voice_id)
    if voice and voice.get("audio_url"):
        return voice["audio_url"]
    return None

@app.post("/")
@app.post("/api/tts")
async def create_tts(req: TTSRequest):
    text = (req.text or '').strip()
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="文本长度不能超过500字符")

    task_id = uuid.uuid4().hex
    voice_id = req.voice_id or "default"

    # 先记录任务为processing
    _tasks[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "progress": 0,
        "audio_url": None,
        "text": text,
        "voice_id": voice_id,
        "created_at": datetime.utcnow().isoformat(),
    }

    # 查找参考音频
    reference_audio_url = await _get_reference_audio_url(voice_id)

    # 调用内联OpenVoice实现
    result = await text_to_speech_inline(text, voice_id=voice_id, reference_audio_url=reference_audio_url)

    # 更新任务状态
    if result and result.get("success"):
        _tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "audio_url": result.get("audio_url"),
            "method": result.get("method", "openvoice"),
            "completed_at": datetime.utcnow().isoformat(),
        })
    else:
        _tasks[task_id].update({
            "status": "failed",
            "progress": 100,
            "error": "TTS生成失败",
            "completed_at": datetime.utcnow().isoformat(),
        })

    # 返回任务ID，前端继续轮询获取完成状态
    return {"success": True, "data": {"task_id": task_id, "status": _tasks[task_id]["status"]}}

@app.get("/status/{task_id}")
@app.get("/api/tts/status/{task_id}")
async def get_tts_status(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"success": True, "data": task}
