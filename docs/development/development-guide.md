# 开发指南

## 项目结构详解

```
teacher-call-me-to-school/
├── frontend/                 # 前端 PWA 应用
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── views/          # 页面视图
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── services/       # API 服务
│   │   ├── utils/          # 工具函数
│   │   └── assets/         # 静态资源
│   ├── public/             # 公共文件
│   └── package.json        # 前端依赖
├── backend/                 # 后端 API 服务
│   ├── app/
│   │   ├── routers/        # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── config.py       # 配置文件
│   ├── migrations/         # 数据库迁移
│   └── requirements.txt    # Python 依赖
├── ai-service/             # AI 语音处理服务
│   ├── mockingbird/        # MockingBird 集成
│   ├── tts/               # TTS 引擎
│   └── models/            # AI 模型文件
├── docs/                   # 项目文档
├── scripts/               # 部署和工具脚本
└── tests/                 # 测试文件
```

## 开发工作流

### 1. 功能开发流程

1. **创建功能分支**
```bash
git checkout -b feature/voice-cloning
```

2. **前端开发**
```bash
cd frontend
npm run dev  # 启动开发服务器
```

3. **后端开发**
```bash
cd backend
source venv/bin/activate
python main.py  # 启动 API 服务
```

4. **测试验证**
```bash
# 前端测试
npm run test

# 后端测试
pytest

# 集成测试
npm run test:e2e
```

5. **代码审查和合并**
```bash
git add .
git commit -m "feat: add voice cloning functionality"
git push origin feature/voice-cloning
# 创建 Pull Request
```

### 2. 代码规范

#### 2.1 前端代码规范

**Vue 组件命名**
```javascript
// 使用 PascalCase
components/
├── VoiceRecorder.vue
├── AudioPlayer.vue
└── VoiceList.vue
```

**组件结构**
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup>
// 导入
import { ref, computed, onMounted } from 'vue'
import { useVoiceStore } from '@/stores/voice'

// 响应式数据
const isRecording = ref(false)
const audioBlob = ref(null)

// 计算属性
const canRecord = computed(() => !isRecording.value)

// 方法
const startRecording = () => {
  // 录音逻辑
}

// 生命周期
onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
/* 组件样式 */
</style>
```

**API 服务封装**
```javascript
// services/voiceApi.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const voiceApi = {
  // 上传音频
  uploadAudio: (file, voiceName) => {
    const formData = new FormData()
    formData.append('audio_file', file)
    formData.append('voice_name', voiceName)
    
    return api.post('/voice/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 开始克隆
  startCloning: (uploadId, options) => {
    return api.post('/voice/clone', { upload_id: uploadId, ...options })
  },

  // 获取音色列表
  getVoiceList: (params = {}) => {
    return api.get('/voice/list', { params })
  }
}
```

#### 2.2 后端代码规范

**路由组织**
```python
# app/routers/voice.py
from fastapi import APIRouter, Depends, UploadFile, File
from app.services.voice_service import VoiceService
from app.models.voice import VoiceCreate, VoiceResponse

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/upload", response_model=VoiceResponse)
async def upload_audio(
    audio_file: UploadFile = File(...),
    voice_name: str,
    voice_service: VoiceService = Depends()
):
    """上传音频文件用于声音克隆"""
    return await voice_service.upload_audio(audio_file, voice_name)
```

**服务层设计**
```python
# app/services/voice_service.py
from typing import List
from app.models.voice import Voice, VoiceCreate
from app.utils.audio_processor import AudioProcessor

class VoiceService:
    def __init__(self, db_session, audio_processor: AudioProcessor):
        self.db = db_session
        self.audio_processor = audio_processor
    
    async def upload_audio(self, file: UploadFile, voice_name: str) -> Voice:
        # 验证音频文件
        if not self.audio_processor.is_valid_audio(file):
            raise ValueError("Invalid audio file")
        
        # 保存文件
        file_path = await self.audio_processor.save_file(file)
        
        # 创建数据库记录
        voice = Voice(name=voice_name, file_path=file_path)
        self.db.add(voice)
        await self.db.commit()
        
        return voice
```

**数据模型定义**
```python
# app/models/voice.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class VoiceStatus(PyEnum):
    UPLOADED = "uploaded"
    TRAINING = "training"
    READY = "ready"
    FAILED = "failed"

class Voice(Base):
    __tablename__ = "voices"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    status = Column(Enum(VoiceStatus), default=VoiceStatus.UPLOADED)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic 模型
class VoiceCreate(BaseModel):
    name: str
    description: str = None

class VoiceResponse(BaseModel):
    id: int
    name: str
    status: VoiceStatus
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 3. 测试策略

#### 3.1 前端测试

**单元测试 (Vitest)**
```javascript
// tests/components/VoiceRecorder.test.js
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import VoiceRecorder from '@/components/VoiceRecorder.vue'

describe('VoiceRecorder', () => {
  it('should start recording when button is clicked', async () => {
    const wrapper = mount(VoiceRecorder)
    
    const recordButton = wrapper.find('[data-testid="record-button"]')
    await recordButton.trigger('click')
    
    expect(wrapper.vm.isRecording).toBe(true)
    expect(wrapper.text()).toContain('录音中...')
  })
})
```

**E2E 测试 (Playwright)**
```javascript
// tests/e2e/voice-cloning.spec.js
import { test, expect } from '@playwright/test'

test('voice cloning workflow', async ({ page }) => {
  await page.goto('/')
  
  // 上传音频文件
  await page.setInputFiles('[data-testid="audio-upload"]', 'test-audio.wav')
  await page.fill('[data-testid="voice-name"]', '测试音色')
  await page.click('[data-testid="upload-button"]')
  
  // 验证上传成功
  await expect(page.locator('[data-testid="upload-success"]')).toBeVisible()
  
  // 开始克隆
  await page.click('[data-testid="start-cloning"]')
  
  // 等待克隆完成
  await expect(page.locator('[data-testid="cloning-complete"]')).toBeVisible({ timeout: 60000 })
})
```

#### 3.2 后端测试

**单元测试 (pytest)**
```python
# tests/test_voice_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.voice_service import VoiceService

@pytest.fixture
def voice_service():
    db_mock = Mock()
    audio_processor_mock = Mock()
    return VoiceService(db_mock, audio_processor_mock)

@pytest.mark.asyncio
async def test_upload_audio_success(voice_service):
    # 准备测试数据
    file_mock = Mock()
    file_mock.filename = "test.wav"
    
    voice_service.audio_processor.is_valid_audio.return_value = True
    voice_service.audio_processor.save_file = AsyncMock(return_value="/path/to/file.wav")
    
    # 执行测试
    result = await voice_service.upload_audio(file_mock, "测试音色")
    
    # 验证结果
    assert result.name == "测试音色"
    voice_service.audio_processor.save_file.assert_called_once_with(file_mock)
```

**API 测试 (FastAPI TestClient)**
```python
# tests/test_voice_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_audio():
    with open("test_audio.wav", "rb") as f:
        response = client.post(
            "/api/voice/upload",
            files={"audio_file": ("test.wav", f, "audio/wav")},
            data={"voice_name": "测试音色"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "测试音色"
```

### 4. 调试技巧

#### 4.1 前端调试

**Vue DevTools**
```javascript
// 在组件中添加调试信息
export default {
  name: 'VoiceRecorder',
  setup() {
    const debugInfo = computed(() => ({
      isRecording: isRecording.value,
      audioBlob: audioBlob.value?.size,
      permissions: permissions.value
    }))
    
    // 在 DevTools 中可见
    return { debugInfo }
  }
}
```

**网络请求调试**
```javascript
// services/api.js
const api = axios.create({
  baseURL: '/api'
})

// 请求拦截器
api.interceptors.request.use(config => {
  console.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.data)
    return response
  },
  error => {
    console.error('API Error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)
```

#### 4.2 后端调试

**日志配置**
```python
# app/utils/logger.py
import logging
from loguru import logger

# 配置 loguru
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# 在服务中使用
class VoiceService:
    async def upload_audio(self, file, voice_name):
        logger.info(f"Uploading audio: {file.filename}, voice_name: {voice_name}")
        
        try:
            result = await self._process_audio(file)
            logger.info(f"Audio upload successful: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Audio upload failed: {str(e)}")
            raise
```

**性能监控**
```python
# app/utils/performance.py
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

# 使用装饰器
@monitor_performance
async def clone_voice(self, audio_data):
    # 声音克隆逻辑
    pass
```

### 5. 性能优化

#### 5.1 前端优化

**代码分割**
```javascript
// router/index.js
const routes = [
  {
    path: '/',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/voice-cloning',
    component: () => import('@/views/VoiceCloning.vue')
  }
]
```

**资源优化**
```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          audio: ['@/utils/audioProcessor', '@/services/audioApi']
        }
      }
    }
  }
})
```

#### 5.2 后端优化

**数据库查询优化**
```python
# 使用索引
class Voice(Base):
    __tablename__ = "voices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(Enum(VoiceStatus), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# 预加载关联数据
async def get_user_voices(user_id: int):
    return await db.query(Voice).options(
        selectinload(Voice.user)
    ).filter(Voice.user_id == user_id).all()
```

**缓存策略**
```python
# app/utils/cache.py
from functools import wraps
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

这个开发指南提供了完整的开发流程、代码规范、测试策略和优化技巧，帮助团队高效协作开发。
