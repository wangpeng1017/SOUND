"""
Pydantic数据模型
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
    email: Optional[str]
    username: Optional[str]
    nickname: Optional[str]
    avatar: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 音色相关模型
class VoiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class VoiceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    audio_url: str
    audio_size: int
    audio_duration: float
    audio_format: str
    voice_model_url: Optional[str]
    voice_model_size: Optional[int]
    status: VoiceStatus
    quality: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # 解决Pydantic保护命名空间冲突
        protected_namespaces = ()

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
    input_text: Optional[str]
    voice_id: Optional[str]
    output_url: Optional[str]
    output_size: Optional[int]
    progress: float
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
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
