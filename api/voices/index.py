from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
import uuid
from datetime import datetime
import json
import httpx
import logging

# 禁用httpx的INFO日志，避免404错误输出
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(title="Voices API", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 系统预设音色
system_voices = [
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

# 内存中的音色数据库
voices_db = {v["id"]: v for v in system_voices}

# 使用内存存储用户音色，避免外部请求
# 这个字典会在创建新音色时更新
user_voices_db = {}

# 导出供TTS API使用
__all__ = ['user_voices_db']

async def _read_manifest() -> Optional[List[dict]]:
    """返回用户创建的音色列表"""
    return list(user_voices_db.values()) if user_voices_db else None

async def _write_manifest(entries: List[dict]) -> bool:
    """更新内存中的用户音色列表"""
    global user_voices_db
    user_voices_db = {entry["id"]: entry for entry in entries if entry.get("id")}
    return True

@app.post("/init")
@app.post("/api/voices/init")
async def init_manifest():
    """初始化manifest文件，创建空的manifest.json"""
    token = os.getenv("BLOB_READ_WRITE_TOKEN")
    if not token:
        return {"success": False, "error": "No blob token"}
        
    # 检查manifest是否已存在
    existing = await _read_manifest()
    if existing is not None:
        return {"success": True, "message": "Manifest already exists", "count": len(existing)}
        
    # 创建空的manifest
    success = await _write_manifest([])
    return {"success": success, "message": "Manifest initialized" if success else "Failed to initialize"}

@app.get("/")
@app.get("/api/voices")
async def list_voices():
    # 读取持久化清单（如果存在）
    manifest = await _read_manifest()

    # 合并系统音色 + 持久化音色 + 内存音色，按id去重
    merged_map = {v["id"]: {"id": v["id"], "name": v["name"], "status": v.get("status", "ready")} for v in voices_db.values()}

    if isinstance(manifest, list):
        for it in manifest:
            vid = it.get("id")
            name = it.get("name")
            if vid and name:
                merged_map[vid] = {"id": vid, "name": name, "status": it.get("status", "ready")}

    data = list(merged_map.values())
    return {"success": True, "data": data}

@app.post("/")
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

    # 同时存储到两个地方
    voice_data = {
        "id": voice_id,
        "name": name.strip(),
        "status": "ready",  # 演示直接可用
        "type": "cloned",
        "created_at": datetime.utcnow().isoformat(),
        "audio_url": blob_url,
        "user_id": user_id,
        "description": description or "",
    }
    
    voices_db[voice_id] = voice_data
    user_voices_db[voice_id] = voice_data

    # 不再需要更新manifest，因为已经存储在内存中

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
