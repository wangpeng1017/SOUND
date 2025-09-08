"""
Pydantic数据模型 - Vercel部署版本
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# 枚举类型
class VoiceStatus(str, Enum):
    PENDING = "PENDING"
    TRAINING = "TRAINING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskType(str, Enum):
    VOICE_TRAINING = "VOICE_TRAINING"
    TTS_SYNTHESIS = "TTS_SYNTHESIS"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

# 基础响应模型
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# 用户相关模型
class UserCreate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    wechat_open_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# 音色相关模型
class VoiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class VoiceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    audio_url: str
    audio_size: int
    audio_duration: float
    audio_format: str
    model_url: Optional[str] = None
    model_size: Optional[int] = None
    status: VoiceStatus
    quality: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class VoiceListResponse(BaseModel):
    voices: List[VoiceResponse]
    total: int

# 任务相关模型
class TaskCreate(BaseModel):
    type: TaskType
    input_text: Optional[str] = None
    voice_id: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    type: TaskType
    status: TaskStatus
    input_text: Optional[str] = None
    voice_id: Optional[str] = None
    output_url: Optional[str] = None
    output_size: Optional[int] = None
    progress: float = 0
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    class Config:
        from_attributes = True

# TTS请求模型
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    voice_id: str

class TTSResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str

# 文件上传响应
class FileUploadResponse(BaseModel):
    url: str
    size: int
    filename: str
    content_type: str
