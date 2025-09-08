# 部署指南

## 部署架构概览

本项目采用前后端分离的部署架构：

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EdgeOne       │    │   云服务器       │    │   GPU 服务器    │
│   Pages         │    │   (API 服务)    │    │   (AI 计算)     │
│                 │    │                 │    │                 │
│   前端 PWA      │◄──►│  FastAPI 后端   │◄──►│   MockingBird   │
│   Vue.js        │    │  数据库         │    │   TTS 引擎      │
│   静态资源      │    │  文件存储       │    │   模型训练      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1. 前端部署 (EdgeOne Pages)

### 1.1 准备工作

1. **构建前端应用**
```bash
cd frontend
npm install
npm run build
```

2. **验证构建产物**
```bash
# 检查 dist 目录
ls -la dist/
```

### 1.2 EdgeOne Pages 部署

1. **登录腾讯云控制台**
   - 访问 EdgeOne 控制台
   - 选择 "Pages" 服务

2. **创建新项目**
   - 项目名称: `teacher-call-me-to-school`
   - 连接 Git 仓库 (推荐)
   - 或直接上传构建产物

3. **配置构建设置**
```yaml
# 构建命令
npm install && npm run build

# 构建输出目录
dist

# 环境变量
NODE_ENV=production
VITE_API_BASE_URL=https://your-api-domain.com/api
```

4. **配置自定义域名** (可选)
   - 添加 CNAME 记录
   - 配置 SSL 证书

### 1.3 PWA 配置优化

确保以下文件正确配置：

**vite.config.js**
```javascript
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/your-api-domain\.com\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              }
            }
          }
        ]
      }
    })
  ]
})
```

## 2. 后端 API 服务部署

### 2.1 服务器要求

**最低配置**
- CPU: 2核
- 内存: 4GB
- 存储: 50GB SSD
- 带宽: 5Mbps
- 操作系统: Ubuntu 20.04 LTS

**推荐配置**
- CPU: 4核
- 内存: 8GB
- 存储: 100GB SSD
- 带宽: 10Mbps

### 2.2 环境准备

1. **更新系统**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **安装 Python 3.8+**
```bash
sudo apt install python3 python3-pip python3-venv -y
```

3. **安装 Nginx**
```bash
sudo apt install nginx -y
```

4. **安装 PostgreSQL** (生产环境)
```bash
sudo apt install postgresql postgresql-contrib -y
```

### 2.3 应用部署

1. **克隆代码**
```bash
git clone <repository-url>
cd teacher-call-me-to-school/backend
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 创建 .env 文件
cat > .env << EOF
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost/dbname

# 安全配置
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 文件存储
UPLOAD_DIR=/var/www/uploads
MAX_FILE_SIZE=50MB

# AI 服务配置
AI_SERVICE_URL=http://localhost:8001

# 环境配置
ENVIRONMENT=production
DEBUG=False
EOF
```

5. **数据库初始化**
```bash
# 创建数据库
sudo -u postgres createdb teacher_call_me_to_school

# 运行迁移
python -m alembic upgrade head
```

6. **创建系统服务**
```bash
sudo tee /etc/systemd/system/teacher-api.service > /dev/null << EOF
[Unit]
Description=Teacher Call Me To School API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/teacher-call-me-to-school/backend
Environment=PATH=/path/to/teacher-call-me-to-school/backend/venv/bin
ExecStart=/path/to/teacher-call-me-to-school/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable teacher-api
sudo systemctl start teacher-api
```

### 2.4 Nginx 配置

```nginx
# /etc/nginx/sites-available/teacher-api
server {
    listen 80;
    server_name your-api-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-api-domain.com;

    # SSL 配置
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 文件上传大小限制
        client_max_body_size 50M;
    }

    # 静态文件服务
    location /uploads/ {
        alias /var/www/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /audio/ {
        alias /var/www/audio/;
        expires 1d;
        add_header Cache-Control "public";
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/teacher-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 3. AI 语音服务部署

### 3.1 GPU 服务器要求

**最低配置**
- GPU: NVIDIA GTX 1060 6GB 或同等性能
- CPU: 4核
- 内存: 16GB
- 存储: 100GB SSD
- CUDA: 11.8+

**推荐配置**
- GPU: NVIDIA RTX 3080 或更高
- CPU: 8核
- 内存: 32GB
- 存储: 200GB NVMe SSD

### 3.2 CUDA 环境配置

1. **安装 NVIDIA 驱动**
```bash
sudo apt install nvidia-driver-470 -y
sudo reboot
```

2. **安装 CUDA Toolkit**
```bash
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

3. **配置环境变量**
```bash
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 3.3 MockingBird 部署

1. **克隆 MockingBird**
```bash
cd /opt
sudo git clone https://github.com/babysor/MockingBird.git
cd MockingBird
```

2. **安装依赖**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **下载预训练模型**
```bash
# 根据 MockingBird 文档下载必要的模型文件
wget <model-download-url>
```

4. **创建 AI 服务**
```python
# ai-service/main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="AI Voice Service")

@app.post("/clone")
async def clone_voice(audio_file, voice_name):
    # 集成 MockingBird 声音克隆逻辑
    pass

@app.post("/synthesize")
async def synthesize_speech(text, voice_id):
    # 集成 TTS 合成逻辑
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 4. 监控和维护

### 4.1 日志管理

```bash
# 查看 API 服务日志
sudo journalctl -u teacher-api -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 4.2 备份策略

1. **数据库备份**
```bash
# 每日备份脚本
#!/bin/bash
pg_dump teacher_call_me_to_school > backup_$(date +%Y%m%d).sql
```

2. **文件备份**
```bash
# 备份用户上传文件
rsync -av /var/www/uploads/ /backup/uploads/
```

### 4.3 性能监控

推荐使用以下工具：
- **Prometheus + Grafana**: 系统监控
- **Sentry**: 错误追踪
- **New Relic**: 应用性能监控

## 5. 安全配置

### 5.1 防火墙设置

```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000  # 只允许内部访问
```

### 5.2 SSL 证书

使用 Let's Encrypt 免费证书：
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-api-domain.com
```

### 5.3 定期更新

```bash
# 创建自动更新脚本
sudo crontab -e

# 添加以下行 (每周日凌晨2点更新)
0 2 * * 0 apt update && apt upgrade -y
```

## 6. 故障排除

### 6.1 常见问题

1. **API 服务无法启动**
   - 检查端口占用: `sudo netstat -tlnp | grep 8000`
   - 查看服务日志: `sudo journalctl -u teacher-api`

2. **数据库连接失败**
   - 检查 PostgreSQL 状态: `sudo systemctl status postgresql`
   - 验证连接字符串和权限

3. **文件上传失败**
   - 检查目录权限: `ls -la /var/www/uploads`
   - 验证 Nginx 配置中的文件大小限制

### 6.2 性能优化

1. **数据库优化**
   - 添加适当的索引
   - 配置连接池
   - 定期 VACUUM

2. **缓存策略**
   - Redis 缓存热点数据
   - CDN 加速静态资源

3. **负载均衡**
   - 多实例部署
   - Nginx 负载均衡配置

这个部署指南提供了完整的生产环境部署流程，确保应用的稳定性和可扩展性。
