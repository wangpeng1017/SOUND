# 开发环境搭建指南

## 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Node.js**: 18.0.0 或更高版本
- **Python**: 3.8 或更高版本
- **Git**: 最新版本
- **GPU**: 推荐NVIDIA GPU (用于AI模型训练和推理)

## 环境搭建步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd teacher-call-me-to-school
```

### 2. 前端环境搭建

```bash
cd frontend
npm install
```

### 3. 后端环境搭建

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. AI服务环境搭建

```bash
cd ai-service

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装MockingBird (需要根据官方文档调整)
# git clone https://github.com/babysor/MockingBird.git
# cd MockingBird
# pip install -r requirements.txt
```

### 5. 环境变量配置

在项目根目录创建 `.env` 文件：

```env
# 开发环境配置
NODE_ENV=development
PYTHON_ENV=development

# API配置
API_HOST=localhost
API_PORT=8000
FRONTEND_PORT=3000

# 数据库配置
DATABASE_URL=sqlite:///./app.db

# AI服务配置
AI_SERVICE_HOST=localhost
AI_SERVICE_PORT=8001

# 文件存储配置
UPLOAD_MAX_SIZE=50MB
AUDIO_MAX_DURATION=30

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

## 开发服务器启动

### 启动前端开发服务器

```bash
cd frontend
npm run dev
```

访问: http://localhost:3000

### 启动后端API服务器

```bash
cd backend
python main.py
```

API文档: http://localhost:8000/docs

### 启动AI服务

```bash
cd ai-service
python main.py
```

## 开发工具推荐

### VS Code 扩展

- Vue Language Features (Volar)
- Python
- Prettier - Code formatter
- ESLint
- GitLens

### 代码格式化

```bash
# 前端代码格式化
cd frontend
npm run format
npm run lint

# 后端代码格式化
cd backend
black .
isort .
flake8 .
```

## 常见问题

### 1. Node.js版本问题

如果遇到Node.js版本兼容问题，推荐使用nvm管理Node.js版本：

```bash
# 安装指定版本
nvm install 18.17.0
nvm use 18.17.0
```

### 2. Python依赖安装失败

某些依赖可能需要编译，确保安装了必要的构建工具：

**Windows:**
```bash
# 安装Visual Studio Build Tools
# 或安装完整的Visual Studio
```

**macOS:**
```bash
xcode-select --install
```

**Ubuntu:**
```bash
sudo apt-get install build-essential python3-dev
```

### 3. GPU支持

如果需要GPU加速，确保安装了正确的CUDA版本：

```bash
# 检查CUDA版本
nvidia-smi

# 安装对应的PyTorch版本
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 下一步

环境搭建完成后，可以开始：

1. 研究MockingBird的集成方案
2. 开发基础的TTS功能
3. 创建前端界面原型
4. 实现前后端通信

详细的开发指南请参考 `docs/development/` 目录下的其他文档。
