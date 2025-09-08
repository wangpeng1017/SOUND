# API 接口规范文档

## 概述

本文档描述了"老师喊我去上学"应用的后端API接口规范，包括文字转语音、声音克隆、用户管理等核心功能的API设计。

## 基础信息

- **Base URL**: `http://localhost:8000/api` (开发环境)
- **Content-Type**: `application/json`
- **认证方式**: JWT Bearer Token
- **API版本**: v1

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体数据
  },
  "message": "操作成功",
  "timestamp": "2025-09-08T15:30:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息"
  },
  "timestamp": "2025-09-08T15:30:00Z"
}
```

## 1. 文字转语音 API

### 1.1 基础TTS转换

**POST** `/tts/convert`

将文本转换为语音文件。

#### 请求参数
```json
{
  "text": "要转换的文本内容",
  "voice_id": "voice_123", // 可选，音色ID
  "speed": 1.0,           // 可选，语速 (0.5-2.0)
  "pitch": 1.0,           // 可选，音调 (0.5-2.0)
  "format": "mp3"         // 可选，输出格式 (mp3/wav)
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "audio_url": "http://localhost:8000/audio/tts_123456.mp3",
    "duration": 5.2,
    "file_size": 102400,
    "task_id": "tts_task_123"
  }
}
```

### 1.2 获取TTS任务状态

**GET** `/tts/status/{task_id}`

查询TTS转换任务的状态。

#### 响应
```json
{
  "success": true,
  "data": {
    "task_id": "tts_task_123",
    "status": "completed", // pending/processing/completed/failed
    "progress": 100,
    "audio_url": "http://localhost:8000/audio/tts_123456.mp3",
    "created_at": "2025-09-08T15:30:00Z",
    "completed_at": "2025-09-08T15:30:05Z"
  }
}
```

## 2. 声音克隆 API

### 2.1 上传音频样本

**POST** `/voice/upload`

上传音频文件用于声音克隆。

#### 请求参数
- **Content-Type**: `multipart/form-data`
- **audio_file**: 音频文件 (支持 wav, mp3, m4a)
- **voice_name**: 音色名称
- **description**: 音色描述 (可选)

#### 响应
```json
{
  "success": true,
  "data": {
    "upload_id": "upload_123",
    "file_name": "sample.wav",
    "file_size": 1024000,
    "duration": 10.5,
    "status": "uploaded"
  }
}
```

### 2.2 开始声音克隆训练

**POST** `/voice/clone`

基于上传的音频样本开始训练声音模型。

#### 请求参数
```json
{
  "upload_id": "upload_123",
  "voice_name": "李老师",
  "description": "我的班主任老师的声音",
  "training_steps": 1000 // 可选，训练步数
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "clone_task_id": "clone_task_456",
    "voice_id": "voice_789",
    "status": "training",
    "estimated_time": 300 // 预估完成时间(秒)
  }
}
```

### 2.3 获取克隆任务状态

**GET** `/voice/clone/status/{clone_task_id}`

查询声音克隆任务的进度。

#### 响应
```json
{
  "success": true,
  "data": {
    "clone_task_id": "clone_task_456",
    "voice_id": "voice_789",
    "status": "training", // training/completed/failed
    "progress": 65,
    "current_step": 650,
    "total_steps": 1000,
    "estimated_remaining": 120,
    "created_at": "2025-09-08T15:30:00Z"
  }
}
```

### 2.4 获取用户音色列表

**GET** `/voice/list`

获取用户已创建的所有音色。

#### 查询参数
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 10)
- `status`: 状态筛选 (可选)

#### 响应
```json
{
  "success": true,
  "data": {
    "voices": [
      {
        "voice_id": "voice_789",
        "name": "李老师",
        "description": "我的班主任老师的声音",
        "status": "ready",
        "created_at": "2025-09-08T15:30:00Z",
        "sample_url": "http://localhost:8000/audio/sample_789.mp3"
      }
    ],
    "total": 5,
    "page": 1,
    "limit": 10
  }
}
```

### 2.5 删除音色

**DELETE** `/voice/{voice_id}`

删除指定的音色模型。

#### 响应
```json
{
  "success": true,
  "message": "音色删除成功"
}
```

## 3. 用户管理 API

### 3.1 用户注册

**POST** `/users/register`

#### 请求参数
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123"
}
```

### 3.2 用户登录

**POST** `/users/login`

#### 请求参数
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "user_id": "user_123",
      "username": "user123",
      "email": "user@example.com"
    }
  }
}
```

### 3.3 获取用户信息

**GET** `/users/profile`

需要认证。

#### 响应
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "username": "user123",
    "email": "user@example.com",
    "created_at": "2025-09-08T15:30:00Z",
    "voice_count": 3,
    "usage_stats": {
      "tts_requests": 150,
      "voice_clones": 3
    }
  }
}
```

## 4. 系统 API

### 4.1 健康检查

**GET** `/health`

#### 响应
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600,
    "services": {
      "database": "healthy",
      "ai_service": "healthy",
      "storage": "healthy"
    }
  }
}
```

### 4.2 系统信息

**GET** `/system/info`

#### 响应
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "build": "20250908-1530",
    "environment": "development",
    "supported_formats": ["mp3", "wav", "m4a"],
    "max_file_size": "50MB",
    "max_audio_duration": 30
  }
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| INVALID_REQUEST | 400 | 请求参数无效 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| FILE_TOO_LARGE | 413 | 文件过大 |
| UNSUPPORTED_FORMAT | 415 | 不支持的文件格式 |
| RATE_LIMITED | 429 | 请求频率过高 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

## 使用示例

### JavaScript/Fetch 示例

```javascript
// TTS转换
const response = await fetch('/api/tts/convert', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    text: '老师喊我去上学了！',
    voice_id: 'voice_123',
    speed: 1.2
  })
});

const result = await response.json();
console.log(result.data.audio_url);
```

### Python/requests 示例

```python
import requests

# 声音克隆
files = {'audio_file': open('sample.wav', 'rb')}
data = {'voice_name': '李老师', 'description': '班主任的声音'}

response = requests.post(
    'http://localhost:8000/api/voice/upload',
    files=files,
    data=data,
    headers={'Authorization': f'Bearer {token}'}
)

result = response.json()
print(result['data']['upload_id'])
```
