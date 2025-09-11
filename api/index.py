from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import uuid
from datetime import datetime

# 轻量可用的无服务器 API（避免外部循环重写导致 508）
# 说明：
# - 满足前端对 /api/voices 的最小预期（POST 创建音色 + GET 列表）
# - 内存存储适合演示与初步联调。如需持久化，请接入数据库/Blob（见注释）

app = FastAPI(title="Teacher Call API (Serverless Minimal)", version="0.1.0")

# 基础 CORS（按需收敛）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单内存存储（无状态平台不保证持久，演示/验证足够）
voices_db = {
    "default": {
        "id": "default",
        "name": "默认音色",
        "status": "ready",
        "type": "system",
        "created_at": datetime.utcnow().isoformat()
    }
}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "serverless-minimal",
    }

@app.get("/voices")
async def list_voices():
    # 返回前端期望的结构：{ success, data: [{id,name,status}, ...] }
    data = [
        {"id": v["id"], "name": v["name"], "status": v["status"]}
        for v in voices_db.values()
        if v.get("status") in ("ready", "training")
    ]
    return {"success": True, "data": data}

@app.post("/voices")
async def create_voice(
    audio_file: UploadFile = File(...),
    name: str = Form(...),
    user_id: str = Form(...),
    description: Optional[str] = Form(None),
):
    # 校验音频
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="请上传音频文件")
    if len(name.strip()) == 0 or len(name) > 20:
        raise HTTPException(status_code=400, detail="音色名称长度应在1-20字符之间")

    # 生成ID并模拟任务
    voice_id = uuid.uuid4().hex
    task_id = uuid.uuid4().hex

    # 可选：上传到 Vercel Blob（若配置了 BLOB_READ_WRITE_TOKEN）
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
            # 忽略 Blob 上传失败，继续流程
            blob_url = None

    # 写入内存“数据库”：初始标记 training，短期内可立即置为 ready 以便前端展示
    voices_db[voice_id] = {
        "id": voice_id,
        "name": name.strip(),
        "status": "training",
        "type": "cloned",
        "created_at": datetime.utcnow().isoformat(),
        "audio_url": blob_url,
        "user_id": user_id,
        "description": description or "",
    }

    # 为了前端立即可见体验，直接变更状态为 ready（演示用；真实应轮训 AI 任务）
    voices_db[voice_id]["status"] = "ready"

    return {
        "success": True,
        "data": {
            "voice_id": voice_id,
            "name": name.strip(),
            "status": voices_db[voice_id]["status"],
            "estimated_time": 30,
            "audio_url": blob_url,
            "task_id": task_id,
        },
    }
