"""
老师喊我去上学 - 后端API服务 v3.0
集成Vercel Blob存储和PostgreSQL数据库
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json
import httpx

# 导入自定义模块
try:
    from app.database import connect_database, disconnect_database, get_database
    from app.storage import storage
    from app.models import *
except ImportError:
    # Vercel部署时的备用导入
    import sys
    sys.path.append('.')
    from database import connect_database, disconnect_database, get_database
    from storage import storage
    from models import *

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("🚀 启动应用...")
    await connect_database()
    print("✅ 数据库连接成功")
    
    yield
    
    # 关闭时
    print("🔄 关闭应用...")
    await disconnect_database()
    print("✅ 数据库连接已关闭")

# 创建FastAPI应用实例
app = FastAPI(
    title="老师喊我去上学 API v3.0",
    description="集成云存储和数据库的AI语音克隆应用",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI服务配置
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "services": {
            "database": "connected",
            "storage": "connected",
            "ai_service": AI_SERVICE_URL
        }
    }

# ==================== 用户管理 ====================

@app.post("/api/users", response_model=BaseResponse)
async def create_user(user_data: UserCreate, db = Depends(get_database)):
    """创建用户"""
    try:
        async with db:
            # 检查用户是否已存在
            existing_user = None
            if user_data.email:
                existing_user = await db.user.find_unique(where={"email": user_data.email})
            elif user_data.wechat_open_id:
                existing_user = await db.user.find_unique(where={"wechatOpenId": user_data.wechat_open_id})
            
            if existing_user:
                return BaseResponse(
                    success=False,
                    message="用户已存在"
                )
            
            # 创建新用户
            user = await db.user.create(
                data={
                    "email": user_data.email,
                    "username": user_data.username,
                    "nickname": user_data.nickname,
                    "wechatOpenId": user_data.wechat_open_id
                }
            )
            
            return BaseResponse(
                success=True,
                message="用户创建成功",
                data={"user_id": user.id}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db = Depends(get_database)):
    """获取用户信息"""
    try:
        async with db:
            user = await db.user.find_unique(where={"id": user_id})
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            return UserResponse.from_orm(user)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户失败: {str(e)}")

# ==================== 音色管理 ====================

@app.post("/api/voices", response_model=BaseResponse)
async def create_voice(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    user_id: str = Form(...),
    audio_file: UploadFile = File(...),
    db = Depends(get_database)
):
    """创建音色"""
    try:
        # 验证音频文件
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="请上传音频文件")
        
        if audio_file.size > 10 * 1024 * 1024:  # 10MB限制
            raise HTTPException(status_code=400, detail="文件过大，请上传小于10MB的文件")
        
        async with db:
            # 检查用户是否存在
            user = await db.user.find_unique(where={"id": user_id})
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 上传音频文件到Vercel Blob
            upload_result = await storage.upload_file(
                file=audio_file,
                folder="voices",
                custom_filename=f"{user_id}_{uuid.uuid4().hex[:8]}_{audio_file.filename}"
            )
            
            # 创建音色记录
            voice = await db.voice.create(
                data={
                    "name": name,
                    "description": description,
                    "audioUrl": upload_result["url"],
                    "audioSize": upload_result["size"],
                    "audioDuration": 0.0,  # 需要AI服务分析
                    "audioFormat": upload_result["content_type"],
                    "userId": user_id,
                    "status": VoiceStatus.PENDING
                }
            )
            
            # 创建训练任务
            task = await db.task.create(
                data={
                    "type": TaskType.VOICE_TRAINING,
                    "voiceId": voice.id,
                    "userId": user_id,
                    "status": TaskStatus.PENDING
                }
            )
            
            # 异步调用AI服务开始训练
            asyncio.create_task(start_voice_training(voice.id, task.id))
            
            return BaseResponse(
                success=True,
                message="音色创建成功，开始训练",
                data={
                    "voice_id": voice.id,
                    "task_id": task.id
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建音色失败: {str(e)}")

@app.get("/api/voices", response_model=VoiceListResponse)
async def list_voices(
    user_id: Optional[str] = None,
    status: Optional[VoiceStatus] = None,
    limit: int = 20,
    offset: int = 0,
    db = Depends(get_database)
):
    """获取音色列表"""
    try:
        async with db:
            # 构建查询条件
            where_conditions = {}
            if user_id:
                where_conditions["userId"] = user_id
            if status:
                where_conditions["status"] = status
            
            # 查询音色列表
            voices = await db.voice.find_many(
                where=where_conditions,
                skip=offset,
                take=limit,
                order_by={"createdAt": "desc"}
            )
            
            # 查询总数
            total = await db.voice.count(where=where_conditions)
            
            return VoiceListResponse(
                voices=[VoiceResponse.from_orm(voice) for voice in voices],
                total=total
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音色列表失败: {str(e)}")

@app.get("/api/voices/{voice_id}", response_model=VoiceResponse)
async def get_voice(voice_id: str, db = Depends(get_database)):
    """获取音色详情"""
    try:
        async with db:
            voice = await db.voice.find_unique(where={"id": voice_id})
            if not voice:
                raise HTTPException(status_code=404, detail="音色不存在")
            
            return VoiceResponse.from_orm(voice)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音色失败: {str(e)}")

@app.delete("/api/voices/{voice_id}", response_model=BaseResponse)
async def delete_voice(voice_id: str, db = Depends(get_database)):
    """删除音色"""
    try:
        async with db:
            voice = await db.voice.find_unique(where={"id": voice_id})
            if not voice:
                raise HTTPException(status_code=404, detail="音色不存在")
            
            # 删除云存储中的文件
            await storage.delete_file(voice.audioUrl)
            if voice.modelUrl:
                await storage.delete_file(voice.modelUrl)
            
            # 删除数据库记录
            await db.voice.delete(where={"id": voice_id})
            
            return BaseResponse(
                success=True,
                message="音色删除成功"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除音色失败: {str(e)}")

# ==================== TTS语音合成 ====================

@app.post("/api/tts", response_model=TTSResponse)
async def create_tts_task(
    request: TTSRequest,
    user_id: str = Form(...),
    db = Depends(get_database)
):
    """创建TTS任务"""
    try:
        async with db:
            # 检查音色是否存在
            voice = await db.voice.find_unique(where={"id": request.voice_id})
            if not voice:
                raise HTTPException(status_code=404, detail="音色不存在")
            
            if voice.status != VoiceStatus.COMPLETED:
                raise HTTPException(status_code=400, detail="音色尚未训练完成")
            
            # 创建TTS任务
            task = await db.task.create(
                data={
                    "type": TaskType.TTS_SYNTHESIS,
                    "inputText": request.text,
                    "voiceId": request.voice_id,
                    "userId": user_id,
                    "status": TaskStatus.PENDING
                }
            )
            
            # 异步调用AI服务进行语音合成
            asyncio.create_task(start_tts_synthesis(task.id))
            
            return TTSResponse(
                task_id=task.id,
                status=TaskStatus.PENDING,
                message="TTS任务创建成功"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建TTS任务失败: {str(e)}")

# ==================== 任务管理 ====================

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db = Depends(get_database)):
    """获取任务状态"""
    try:
        async with db:
            task = await db.task.find_unique(where={"id": task_id})
            if not task:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            return TaskResponse.from_orm(task)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")

# ==================== AI服务集成 ====================

async def start_voice_training(voice_id: str, task_id: str):
    """开始音色训练"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/train",
                json={
                    "voice_id": voice_id,
                    "task_id": task_id
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                # 更新任务状态为失败
                async with get_database() as db:
                    await db.task.update(
                        where={"id": task_id},
                        data={
                            "status": TaskStatus.FAILED,
                            "error": f"AI服务调用失败: {response.status_code}"
                        }
                    )
                    
    except Exception as e:
        print(f"音色训练启动失败: {str(e)}")
        # 更新任务状态为失败
        try:
            async with get_database() as db:
                await db.task.update(
                    where={"id": task_id},
                    data={
                        "status": TaskStatus.FAILED,
                        "error": str(e)
                    }
                )
        except:
            pass

async def start_tts_synthesis(task_id: str):
    """开始TTS语音合成"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/synthesize",
                json={"task_id": task_id},
                timeout=30.0
            )
            
            if response.status_code != 200:
                # 更新任务状态为失败
                async with get_database() as db:
                    await db.task.update(
                        where={"id": task_id},
                        data={
                            "status": TaskStatus.FAILED,
                            "error": f"AI服务调用失败: {response.status_code}"
                        }
                    )
                    
    except Exception as e:
        print(f"TTS合成启动失败: {str(e)}")
        # 更新任务状态为失败
        try:
            async with get_database() as db:
                await db.task.update(
                    where={"id": task_id},
                    data={
                        "status": TaskStatus.FAILED,
                        "error": str(e)
                    }
                )
        except:
            pass

# ==================== 启动应用 ====================

if __name__ == "__main__":
    uvicorn.run(
        "main_v3:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
