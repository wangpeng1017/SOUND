from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
import uuid
from datetime import datetime
import json
import httpx
import logging

# Silence httpx INFO logs to avoid noisy 404 logs
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(title="Voices API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 系统预设音色（始终可用）
_system_voices = [
    {
        "id": "teacher-female",
        "name": "女老师",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "teacher-male",
        "name": "男老师",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "mom",
        "name": "妈妈",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "dad",
        "name": "爸爸",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat(),
    }
]

# 简单内存存储（Serverless 仅用于演示）
voices_db = {v["id"]: v for v in _system_voices}

# 不再使用外部 manifest，返回 None
aSYNC_READ_MANIFEST_REMOVED = True
async def _read_manifest() -> Optional[List[dict]]:
    return None

# 外部持久化已移除，写入操作不执行
async def _write_manifest(entries: List[dict]) -> bool:
    return True

@app.get("/")
@app.get("/api/voices")
async def list_voices():
    # 仅返回内存与系统音色，彻底避免外部请求
    data = [
        {"id": v["id"], "name": v["name"], "status": v.get("status", "ready")}
        for v in voices_db.values()
        if v.get("status") in ("ready", "training")
    ]
    return {"success": True, "data": data}

@app.post("/")
@app.post("/api/voices")
async def create_voice(
    audio_file: UploadFile = File(...),
    name: str = Form(...),
    user_id: str = Form(...),
    description: Optional[str] = Form(None),
):
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="请上传音频文件")
    if len(name.strip()) == 0 or len(name) > 20:
        raise HTTPException(status_code=400, detail="音色名称长度应在1-20字符之间")

    voice_id = uuid.uuid4().hex
    task_id = uuid.uuid4().hex

    # 可选：上传到 Vercel Blob
    blob_url = None
    token = os.getenv("BLOB_READ_WRITE_TOKEN")
    if token:
        try:
            content = await audio_file.read()
            async with httpx.AsyncClient() as client:
                resp = await client.put(
                    "https://blob.vercel-storage.com",
                    headers={
                        "authorization": f"Bearer {token}",
                        "x-content-type": audio_file.content_type or "application/octet-stream",
                    },
                    params={"filename": f"voices/{user_id}_{voice_id}_{audio_file.filename}"},
                    content=content,
                    timeout=30.0,
                )
                if resp.status_code == 200:
                    blob_url = resp.json().get("url")
        except Exception:
            blob_url = None

    voices_db[voice_id] = {
        "id": voice_id,
        "name": name.strip(),
        "status": "ready",
        "type": "cloned",
        "created_at": datetime.utcnow().isoformat(),
        "audio_url": blob_url,
        "user_id": user_id,
        "description": description or "",
    }

    # 不再更新外部 manifest，保持内存即可

    return {
        "success": True,
        "data": {
            "voice_id": voice_id,
            "name": name.strip(),
            "status": "ready",
            "estimated_time": 30,
            "audio_url": blob_url,
            "task_id": task_id,
        },
    }
