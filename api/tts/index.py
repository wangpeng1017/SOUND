from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="TTS API", version="0.1.0")

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

@app.post("/")
@app.post("/api/tts")
async def create_tts(req: TTSRequest):
    text = (req.text or '').strip()
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="文本长度不能超过500字符")

    task_id = uuid.uuid4().hex
    # 直接完成（演示用），音频由 /api/audio 提供固定文件
    _tasks[task_id] = {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "audio_url": "/api/audio/dummy.wav",
        "text": text,
        "voice_id": req.voice_id or "default",
        "created_at": datetime.utcnow().isoformat()
    }
    return {"success": True, "data": {"task_id": task_id, "status": "processing"}}

@app.get("/status/{task_id}")
@app.get("/api/tts/status/{task_id}")
async def get_tts_status(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"success": True, "data": task}
