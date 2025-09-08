# 老师喊我去上学 - AI语音克隆应用

## 项目简介

"老师喊我去上学"是一款轻量级的移动端PWA应用，核心功能是将用户输入的文字转换成特定人物（如老师、爸爸、妈妈、奶奶）音色的语音。用户可以录制或上传少量音频样本来克隆音色，并保存以便后续使用，实现个性化的语音合成。

## 技术架构

### 前端
- **框架**: Vue.js 3 + Vite
- **类型**: Progressive Web App (PWA)
- **UI库**: 待定（考虑Vuetify或Element Plus）
- **状态管理**: Pinia
- **部署**: EdgeOne Pages

### 后端
- **框架**: Python FastAPI
- **AI模型**: MockingBird (声音克隆) + 备选TTS方案
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **文件存储**: 本地存储 + 云存储
- **部署**: 云服务器 (GPU支持)

### 核心功能
1. **文字转语音 (TTS)**: 将用户输入的文本转换为语音
2. **声音克隆**: 通过用户上传的音频样本训练个性化音色
3. **音色管理**: 保存、管理和选择不同的音色
4. **移动端适配**: 响应式设计，支持PWA功能

## 项目结构

```
├── frontend/          # 前端PWA应用
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── backend/           # 后端API服务
│   ├── app/
│   ├── models/
│   ├── requirements.txt
│   └── main.py
├── ai-service/        # AI语音处理服务
│   ├── mockingbird/
│   ├── tts/
│   └── requirements.txt
├── docs/              # 项目文档
│   ├── api/
│   ├── deployment/
│   └── development/
├── scripts/           # 部署和工具脚本
├── tests/             # 测试文件
├── prd.md            # 产品需求文档
└── README.md         # 项目说明
```

## 开发阶段

### 第一阶段 (MVP)
- [x] 项目需求分析与技术调研
- [/] 项目架构设计与环境搭建
- [ ] AI语音技术集成研究
- [ ] 后端API服务开发
- [ ] 前端PWA应用开发
- [ ] 声音克隆功能实现
- [ ] 前后端集成与测试
- [ ] EdgeOne部署配置

### 第二阶段 (功能完善)
- [ ] 用户体验优化
- [ ] 性能优化和错误处理
- [ ] 音色管理功能完善

### 第三阶段 (进阶功能)
- [ ] 功能扩展与完善
- [ ] 多语种支持
- [ ] 社区功能

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- Git

### 安装依赖

```bash
# 前端依赖
cd frontend
npm install

# 后端依赖
cd ../backend
pip install -r requirements.txt

# AI服务依赖
cd ../ai-service
pip install -r requirements.txt
```

### 开发运行

```bash
# 启动前端开发服务器
cd frontend
npm run dev

# 启动后端API服务
cd backend
python main.py

# 启动AI服务
cd ai-service
python main.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

项目链接: [https://github.com/your-username/teacher-call-me-to-school](https://github.com/your-username/teacher-call-me-to-school)
