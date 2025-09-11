from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import uuid
from datetime import datetime

app = FastAPI(title="Voices API", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

voices_db = {
    "default": {
        "id": "default",
        "name": "默认音色",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat(),
    }
}

@app.get("/")
@app.get("/api/voices")
async def list_voices():
    data = [
        {"id": v["id"], "name": v["name"], "status": v["status"]}
        for v in voices_db.values()
        if v.get("status") in ("ready", "training")
    ]
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
            import httpx
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
