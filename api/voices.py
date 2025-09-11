from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
import uuid
from datetime import datetime
import json
import httpx

app = FastAPI(title="Voices API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单内存存储（Serverless 仅用于演示）
voices_db = {
    "default": {
        "id": "default",
        "name": "默认音色",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat(),
    }
}

async def _read_manifest() -> Optional[List[dict]]:
    url = "https://blob.vercel-storage.com/voices/manifest.json"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10.0)
            if r.status_code == 200:
                return r.json()
    except Exception:
        return None
    return None

async def _write_manifest(entries: List[dict]) -> bool:
    token = os.getenv("BLOB_READ_WRITE_TOKEN")
    if not token:
        return False
    try:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                "https://blob.vercel-storage.com",
                headers={
                    "authorization": f"Bearer {token}",
                    "x-content-type": "application/json",
                },
                params={"filename": "voices/manifest.json"},
                content=json.dumps(entries).encode("utf-8"),
                timeout=15.0,
            )
            return r.status_code == 200
    except Exception:
        return False

@app.get("/")
@app.get("/api/voices")
async def list_voices():
    # 优先返回持久化的清单
    manifest = await _read_manifest()
    if isinstance(manifest, list) and manifest:
        data = [
            {"id": it.get("id"), "name": it.get("name"), "status": it.get("status", "ready")}
            for it in manifest
            if it.get("id") and it.get("name")
        ]
        return {"success": True, "data": data}

    # 回退到内存
    data = [
        {"id": v["id"], "name": v["name"], "status": v["status"]}
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

    # 更新持久化清单
    try:
      manifest = await _read_manifest() or []
      manifest.append({
          "id": voice_id,
          "name": name.strip(),
          "status": "ready",
          "created_at": datetime.utcnow().isoformat(),
          "audio_url": blob_url,
          "user_id": user_id
      })
      await _write_manifest(manifest)
    except Exception:
      pass

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
