# 🗄️ Vercel数据库和存储部署指南

## 📋 部署概述

本指南将帮你完成"老师喊我去上学"应用的Vercel Blob存储和PostgreSQL数据库集成部署。

## 1. 环境变量配置

### 🔧 Vercel项目配置

在Vercel项目设置中添加以下环境变量：

```bash
# Vercel Blob存储
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_AUL5HsnQWN21BR8h_YbxChFzoaGO9Lb16sDGUYq3rCEVWKy

# PostgreSQL数据库
POSTGRES_URL=postgres://70b463f0b437de031fed82ef1e60a31c4764574b5b85f2971518520d47db953d:sk_ppgr1YQhsciDLwChczX1t@db.prisma.io:5432/postgres?sslmode=require

PRISMA_DATABASE_URL=prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqd3RfaWQiOjEsInNlY3VyZV9rZXkiOiJza19wcGdyMVlRaHNjaURMd0NoY3pYMXQiLCJhcGlfa2V5IjoiMDFLNE1NM0c3OVZaMVZIR0ZXUjRCUEZYQ1ciLCJ0ZW5hbnRfaWQiOiI3MGI0NjNmMGI0MzdkZTAzMWZlZDgyZWYxZTYwYTMxYzQ3NjQ1NzRiNWI4NWYyOTcxNTE4NTIwZDQ3ZGI5NTNkIiwiaW50ZXJuYWxfc2VjcmV0IjoiN2VlOGViZDUtOWJmZi00OWRhLWFiZjgtYTk1YjZkNDhjNGQ0In0.KiikocrUoD_b0eIOShgAkr4cCJm7rNcJ4x2DgUNWfbU

# JWT配置
JWT_SECRET_KEY=your_production_jwt_secret_here_make_it_very_long_and_secure
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# API配置
API_DEBUG=False
AI_SERVICE_URL=https://your-ai-service.herokuapp.com

# CORS配置
CORS_ORIGINS=["https://teacher-call-me-to-school.vercel.app"]
```

## 2. 数据库初始化

### 📊 Prisma数据库设置

```bash
# 1. 安装Prisma CLI
npm install -g prisma

# 2. 生成Prisma客户端
cd backend
prisma generate

# 3. 推送数据库模式
prisma db push

# 4. 查看数据库状态
prisma studio
```

### 🔧 Python环境设置

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 初始化数据库
python scripts/init_database.py init

# 3. 检查数据库状态
python scripts/init_database.py status
```

## 3. 后端API部署

### 🚀 Heroku部署 (推荐)

```bash
# 1. 创建Heroku应用
heroku create teacher-call-backend

# 2. 设置环境变量
heroku config:set BLOB_READ_WRITE_TOKEN=vercel_blob_rw_AUL5HsnQWN21BR8h_YbxChFzoaGO9Lb16sDGUYq3rCEVWKy
heroku config:set PRISMA_DATABASE_URL=prisma+postgres://accelerate.prisma-data.net/?api_key=...

# 3. 部署应用
git subtree push --prefix=backend heroku master

# 4. 运行数据库初始化
heroku run python scripts/init_database.py init
```

### 📋 Procfile配置

```bash
# backend/Procfile
web: uvicorn main_v3:app --host=0.0.0.0 --port=${PORT:-8000}
release: python scripts/init_database.py init
```

## 4. 前端配置更新

### 🌐 API基础URL更新

```javascript
// frontend/src/services/api.js
const getApiBaseUrl = () => {
  if (import.meta.env.PROD) {
    return 'https://teacher-call-backend.herokuapp.com'
  }
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}
```

### 🔧 环境变量配置

```bash
# frontend/.env.production
VITE_API_BASE_URL=https://teacher-call-backend.herokuapp.com
VITE_APP_TITLE=老师喊我去上学
VITE_APP_DESCRIPTION=极简AI语音克隆应用
```

## 5. 测试部署

### 🧪 功能测试脚本

```python
# scripts/test_production.py
import asyncio
import httpx

async def test_production_api():
    """测试生产环境API"""
    base_url = "https://teacher-call-backend.herokuapp.com"
    
    async with httpx.AsyncClient() as client:
        # 测试健康检查
        response = await client.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 测试音色列表
        response = await client.get(f"{base_url}/api/voices")
        print(f"Voices list: {response.status_code}")
        
        # 测试用户创建
        response = await client.post(
            f"{base_url}/api/users",
            json={
                "email": "test@example.com",
                "nickname": "测试用户"
            }
        )
        print(f"User creation: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_production_api())
```

## 6. 监控和维护

### 📊 数据库监控

```sql
-- 查看数据库使用情况
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public';

-- 查看表大小
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables
WHERE schemaname = 'public';
```

### 🔍 日志监控

```bash
# Heroku日志查看
heroku logs --tail --app teacher-call-backend

# 特定时间段日志
heroku logs --since="2024-01-01" --until="2024-01-02"
```

## 7. 安全配置

### 🔒 数据库安全

```python
# 数据库连接池配置
DATABASE_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}
```

### 🛡️ API安全

```python
# 限流配置
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 应用限流
@app.post("/api/voices")
@limiter.limit("5/minute")
async def create_voice(request: Request, ...):
    pass
```

## 8. 性能优化

### ⚡ 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_voices_user_id ON voices(user_id);
CREATE INDEX idx_voices_status ON voices(status);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

### 🚀 缓存配置

```python
# Redis缓存 (可选)
import redis
from functools import wraps

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

## 9. 故障排除

### 🔧 常见问题

#### 1. 数据库连接失败
```bash
# 检查环境变量
echo $PRISMA_DATABASE_URL

# 测试数据库连接
python -c "
import asyncio
from app.database import connect_database
asyncio.run(connect_database())
"
```

#### 2. Blob存储上传失败
```python
# 测试Blob存储
import os
from app.storage import storage

async def test_blob():
    # 测试上传
    with open("test.txt", "w") as f:
        f.write("test content")
    
    with open("test.txt", "rb") as f:
        result = await storage.upload_bytes(
            f.read(), 
            "test.txt", 
            folder="test"
        )
    print(f"Upload result: {result}")

asyncio.run(test_blob())
```

#### 3. API响应慢
```python
# 添加性能监控
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 10. 部署检查清单

### ✅ 部署前检查

- [ ] 环境变量配置完整
- [ ] 数据库连接正常
- [ ] Blob存储配置正确
- [ ] API接口测试通过
- [ ] 前端构建成功
- [ ] CORS配置正确

### ✅ 部署后验证

- [ ] 健康检查接口正常
- [ ] 用户注册功能正常
- [ ] 音频上传功能正常
- [ ] 音色创建功能正常
- [ ] TTS合成功能正常
- [ ] 错误处理正常

### ✅ 性能检查

- [ ] API响应时间 < 2秒
- [ ] 数据库查询优化
- [ ] 文件上传速度正常
- [ ] 内存使用合理
- [ ] 并发处理正常

通过以上配置，你的应用将拥有完整的云数据库和存储能力，支持大规模用户使用！🚀
