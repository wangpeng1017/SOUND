"""
老师喊我去上学 - 后端API服务
极简设计的AI语音克隆应用后端服务
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import uuid
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json

# 创建FastAPI应用实例
app = FastAPI(
    title="老师喊我去上学 API",
    description="极简AI语音克隆应用后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
MODELS_DIR = Path("models")
AUDIO_DIR = Path("audio")
TEMP_DIR = Path("temp")

for directory in [UPLOAD_DIR, MODELS_DIR, AUDIO_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# 静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# 数据模型
class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "default"

class VoiceInfo(BaseModel):
    id: str
    name: str
    status: str
    created_at: str

# AI服务配置
AI_SERVICE_URL = "http://localhost:8001"

# HTTP客户端
import httpx

# 内存存储（MVP版本使用，生产环境应使用数据库）
voices_db = {}
tasks_db = {}

# 初始化时从AI服务获取音色列表
async def init_voices_from_ai_service():
    """从AI服务初始化音色列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/voices", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    for voice in data.get("data", []):
                        voices_db[voice["id"]] = {
                            "id": voice["id"],
                            "name": voice["name"],
                            "status": voice["status"],
                            "type": voice.get("type", "system"),
                            "created_at": voice.get("created_at", datetime.now().isoformat())
                        }
                    print(f"✅ 从AI服务加载了 {len(voices_db)} 个音色")
                else:
                    print("⚠️ AI服务返回错误")
            else:
                print(f"⚠️ AI服务连接失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 无法连接AI服务: {str(e)}")
        # 使用默认音色作为备选
        voices_db.update({
            "default": {
                "id": "default",
                "name": "默认音色",
                "status": "ready",
                "type": "system",
                "created_at": datetime.now().isoformat()
            }
        })

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "app": "老师喊我去上学",
        "version": "1.0.0",
        "status": "running",
        "description": "极简AI语音克隆应用"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "teacher-call-me-to-school-api"
    }

# ==================== 核心API接口 ====================

@app.get("/api/voices")
async def get_voices():
    """获取可用音色列表 - 从AI服务获取"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/voices", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 更新本地缓存
                    for voice in data.get("data", []):
                        voices_db[voice["id"]] = {
                            "id": voice["id"],
                            "name": voice["name"],
                            "status": voice["status"],
                            "type": voice.get("type", "system")
                        }

                    # 返回简化的音色列表
                    voices = [
                        {
                            "id": voice["id"],
                            "name": voice["name"],
                            "status": voice["status"]
                        }
                        for voice in data.get("data", [])
                        if voice["status"] == "ready"
                    ]

                    return {
                        "success": True,
                        "data": voices
                    }
    except Exception as e:
        print(f"获取AI服务音色失败: {str(e)}")

    # 备选方案：返回本地缓存
    voices = [
        {
            "id": voice["id"],
            "name": voice["name"],
            "status": voice["status"]
        }
        for voice in voices_db.values()
        if voice["status"] == "ready"
    ]

    return {
        "success": True,
        "data": voices
    }

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """文字转语音 - 使用AI服务"""

    # 验证输入
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    if len(request.text) > 200:
        raise HTTPException(status_code=400, detail="文本长度不能超过200字符")

    try:
        # 调用AI服务进行语音合成
        async with httpx.AsyncClient() as client:
            form_data = {
                "text": request.text,
                "voice_id": request.voice_id or "default"
            }

            response = await client.post(
                f"{AI_SERVICE_URL}/synthesize",
                data=form_data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    ai_task_id = data["data"]["task_id"]

                    # 创建本地任务映射
                    local_task_id = str(uuid.uuid4())
                    task = {
                        "id": local_task_id,
                        "ai_task_id": ai_task_id,
                        "text": request.text,
                        "voice_id": request.voice_id or "default",
                        "voice_name": voices_db.get(request.voice_id or "default", {}).get("name", "未知音色"),
                        "status": "processing",
                        "progress": 0,
                        "audio_url": None,
                        "created_at": datetime.now().isoformat()
                    }

                    tasks_db[local_task_id] = task

                    # 启动状态轮询
                    asyncio.create_task(poll_ai_service_task(local_task_id))

                    return {
                        "success": True,
                        "data": {
                            "task_id": local_task_id,
                            "status": "processing",
                            "message": "正在生成语音..."
                        }
                    }
                else:
                    raise HTTPException(status_code=500, detail="AI服务返回错误")
            else:
                raise HTTPException(status_code=500, detail=f"AI服务请求失败: {response.status_code}")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI服务响应超时")
    except Exception as e:
        print(f"TTS请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="语音合成服务暂时不可用")

@app.get("/api/tts/status/{task_id}")
async def get_tts_status(task_id: str):
    """获取TTS任务状态"""

    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks_db[task_id]

    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "status": task["status"],
            "progress": task["progress"],
            "audio_url": task["audio_url"],
            "voice_name": task["voice_name"],
            "text": task["text"]
        }
    }

@app.get("/api/audio/{filename}")
async def get_audio_file(filename: str):
    """获取音频文件"""
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

@app.post("/api/voice/upload")
async def upload_voice_sample(
    audio_file: UploadFile = File(...),
    voice_name: str = Form(...)
):
    """上传音频样本用于声音克隆 - 使用AI服务"""

    # 验证文件类型
    if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="请上传音频文件")

    # 验证音色名称
    if not voice_name.strip() or len(voice_name) > 20:
        raise HTTPException(status_code=400, detail="音色名称长度应在1-20字符之间")

    try:
        # 准备文件数据
        content = await audio_file.read()

        # 调用AI服务上传音频
        async with httpx.AsyncClient() as client:
            files = {
                "audio_file": (audio_file.filename, content, audio_file.content_type)
            }
            data = {
                "voice_name": voice_name.strip()
            }

            response = await client.post(
                f"{AI_SERVICE_URL}/voice/upload",
                files=files,
                data=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    upload_data = result["data"]

                    # 添加到本地音色数据库
                    voice_id = upload_data["voice_id"]
                    voices_db[voice_id] = {
                        "id": voice_id,
                        "name": voice_name.strip(),
                        "status": "training",
                        "type": "cloned",
                        "created_at": datetime.now().isoformat(),
                        "ai_task_id": upload_data["task_id"]
                    }

                    # 启动训练状态轮询
                    asyncio.create_task(poll_training_status(voice_id, upload_data["task_id"]))

                    return {
                        "success": True,
                        "data": {
                            "voice_id": voice_id,
                            "name": voice_name,
                            "status": "training",
                            "estimated_time": upload_data.get("estimated_time", 60),
                            "message": "正在训练音色模型..."
                        }
                    }
                else:
                    raise HTTPException(status_code=400, detail=result.get("error", "上传失败"))
            else:
                error_text = response.text
                raise HTTPException(status_code=response.status_code, detail=f"AI服务错误: {error_text}")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="上传超时，请重试")
    except HTTPException:
        raise
    except Exception as e:
        print(f"音频上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail="上传服务暂时不可用")

# ==================== 异步任务处理 ====================

async def poll_ai_service_task(local_task_id: str):
    """轮询AI服务的TTS任务状态"""
    try:
        task = tasks_db[local_task_id]
        ai_task_id = task["ai_task_id"]

        max_attempts = 60  # 最多轮询60次 (60秒)
        attempt = 0

        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{AI_SERVICE_URL}/synthesize/status/{ai_task_id}",
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            ai_task = data["data"]

                            # 更新本地任务状态
                            task["status"] = ai_task["status"]
                            task["progress"] = ai_task["progress"]

                            if ai_task["status"] == "completed":
                                # 获取音频URL
                                if ai_task["audio_url"]:
                                    # 转换AI服务的URL为本地URL
                                    audio_filename = ai_task["audio_url"].split("/")[-1]
                                    task["audio_url"] = f"/api/audio/{audio_filename}"

                                task["completed_at"] = datetime.now().isoformat()
                                break
                            elif ai_task["status"] == "failed":
                                task["error"] = ai_task.get("error", "AI服务处理失败")
                                break

            except Exception as e:
                print(f"轮询AI服务状态失败: {str(e)}")

            attempt += 1
            await asyncio.sleep(1)  # 等待1秒后重试

        # 如果超时仍未完成
        if attempt >= max_attempts and task["status"] == "processing":
            task["status"] = "failed"
            task["error"] = "处理超时"

    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)

async def poll_training_status(voice_id: str, ai_task_id: str):
    """轮询AI服务的训练任务状态"""
    try:
        voice = voices_db[voice_id]

        max_attempts = 300  # 最多轮询5分钟
        attempt = 0

        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{AI_SERVICE_URL}/voice/training/status/{ai_task_id}",
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            ai_task = data["data"]

                            # 更新本地音色状态
                            if ai_task["status"] == "completed":
                                voice["status"] = "ready"
                                voice["completed_at"] = datetime.now().isoformat()
                                break
                            elif ai_task["status"] == "failed":
                                voice["status"] = "failed"
                                voice["error"] = ai_task.get("error", "训练失败")
                                break

            except Exception as e:
                print(f"轮询训练状态失败: {str(e)}")

            attempt += 1
            await asyncio.sleep(2)  # 等待2秒后重试

        # 如果超时仍未完成
        if attempt >= max_attempts and voice["status"] == "training":
            voice["status"] = "failed"
            voice["error"] = "训练超时"

    except Exception as e:
        voice["status"] = "failed"
        voice["error"] = str(e)

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    print("🔄 正在初始化音色列表...")
    await init_voices_from_ai_service()
    print("✅ 初始化完成")

if __name__ == "__main__":
    print("🎤 老师喊我去上学 API 服务启动中...")
    print("📱 极简AI语音克隆应用 - 集成真实AI服务")
    print("🔗 AI服务地址: http://localhost:8001")
    print("🌐 API文档: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
