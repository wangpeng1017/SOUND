# 🎤 老师喊我去上学 - AI语音克隆应用

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/wangpeng1017/SOUND?style=social)
![GitHub forks](https://img.shields.io/github/forks/wangpeng1017/SOUND?style=social)
![GitHub issues](https://img.shields.io/github/issues/wangpeng1017/SOUND)
![GitHub license](https://img.shields.io/github/license/wangpeng1017/SOUND)

**一款极简设计的AI语音克隆PWA应用**

[🚀 在线演示](http://localhost:3000) | [📖 文档](./docs/) | [🐛 报告问题](https://github.com/wangpeng1017/SOUND/issues)

</div>

## ✨ 项目简介

"老师喊我去上学"是一款轻量级的移动端PWA应用，专注于AI语音克隆技术。用户只需3步即可将文字转换成特定人物（如老师、爸爸、妈妈）的个性化语音。

### 🎯 核心特性

- 🎤 **智能TTS引擎** - 支持多种语音合成引擎，自动选择最佳方案
- 🎵 **声音克隆** - 上传5-15秒音频即可训练专属音色
- 📱 **PWA应用** - 可安装到手机主屏幕，原生应用体验
- 🎨 **极简设计** - 遵循极简主义，3步完成核心功能
- ⚡ **实时处理** - 异步任务处理，实时状态反馈
- 🔊 **高质量音频** - 智能音频处理和质量评估

## 🏗️ 技术架构

### 🎨 前端层 (PWA)
```
Vue.js 3 + Composition API
├── 🎨 极简UI设计 (原生CSS + CSS变量)
├── 📱 PWA支持 (可安装、离线使用)
├── 🔄 状态管理 (Pinia)
├── 🌐 路由管理 (Vue Router)
└── ⚡ 构建工具 (Vite)
```

### 🔧 后端层 (API网关)
```
Python FastAPI
├── 🌐 RESTful API设计
├── 🔄 异步任务处理
├── 🔗 AI服务代理
├── 📊 任务状态管理
└── 💾 数据缓存
```

### 🤖 AI服务层 (语音处理)
```
多引擎TTS + 声音克隆
├── 🎤 TTS引擎 (Edge-TTS/SAPI/Say/Espeak)
├── 🔊 音频处理 (验证/预处理/特征提取)
├── 🧠 声音克隆 (训练框架/模型管理)
└── 📈 质量评估 (自动评分)
```

### 🚀 部署架构
```
三层微服务架构
├── 前端: EdgeOne Pages (CDN加速)
├── 后端: 云服务器 (API网关)
└── AI服务: GPU服务器 (AI计算)
```

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

## 🚀 快速开始

### 📋 环境要求
- **Node.js** 18+
- **Python** 3.8+
- **Git** 最新版本
- **可选**: FFmpeg (音频处理)

### 📦 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/wangpeng1017/SOUND.git
cd SOUND

# 2. 安装前端依赖
cd frontend && npm install

# 3. 安装后端依赖
cd ../backend && pip install -r requirements.txt

# 4. 安装AI服务依赖
cd ../ai-service && pip install -r requirements.txt
```

### 🎯 启动服务

```bash
# 方式1: 分别启动 (推荐开发)
# 终端1: 启动AI服务 (端口8001)
cd ai-service && python main_v2.py

# 终端2: 启动后端API (端口8000)
cd backend && python main.py

# 终端3: 启动前端应用 (端口3000)
cd frontend && npm run dev

# 方式2: 快速检查服务状态
python scripts/check_services.py
```

### 🌐 访问应用

- **前端应用**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **AI服务**: http://localhost:8001/docs

## 📱 功能演示

### 🎤 文字转语音 (3步完成)
1. **输入文字** - 支持中文，最多200字符
2. **选择音色** - 系统自动检测可用TTS引擎
3. **生成语音** - 实时进度显示，支持播放下载

### 🎵 声音克隆
1. **上传音频** - 支持MP3/WAV/M4A格式，5-15秒最佳
2. **智能处理** - 自动音频验证和质量评估
3. **模型训练** - 异步训练，实时状态跟踪
4. **音色管理** - 创建、使用、删除自定义音色

### 📊 支持的TTS引擎
- ✅ **Edge TTS** - 高质量中文语音 (推荐)
- ✅ **Windows SAPI** - Windows系统内置
- ✅ **macOS Say** - macOS系统内置
- ✅ **Linux Espeak** - 开源轻量级引擎

## 📖 文档

- 📋 [API接口文档](./docs/api/api-specification.md)
- 🛠️ [开发指南](./docs/development/development-guide.md)
- 🚀 [部署指南](./docs/deployment/deployment-guide.md)
- 🎯 [功能演示](./docs/feature-demo-v2.md)
- 🔧 [技术架构](./docs/development/tech-stack.md)

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题
- 使用 [Issues](https://github.com/wangpeng1017/SOUND/issues) 报告bug
- 提供详细的复现步骤和环境信息

### 💡 功能建议
- 在 [Issues](https://github.com/wangpeng1017/SOUND/issues) 中提出新功能建议
- 描述功能的使用场景和预期效果

### 🔧 代码贡献
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '✨ Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 📝 提交规范
```
✨ feat: 新功能
🐛 fix: 修复bug
📚 docs: 文档更新
🎨 style: 代码格式
♻️ refactor: 重构
⚡ perf: 性能优化
✅ test: 测试相关
🔧 chore: 构建/工具
```

## ⭐ Star History

如果这个项目对你有帮助，请给我们一个 ⭐ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=wangpeng1017/SOUND&type=Date)](https://star-history.com/#wangpeng1017/SOUND&Date)

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看文件了解详情。

## 📞 联系方式

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/wangpeng1017/SOUND/issues)
- 💬 **功能讨论**: [GitHub Discussions](https://github.com/wangpeng1017/SOUND/discussions)
- 📧 **邮件联系**: wangpeng1017@example.com

---

<div align="center">

**[⬆ 回到顶部](#-老师喊我去上学---ai语音克隆应用)**

Made with ❤️ by [wangpeng1017](https://github.com/wangpeng1017)

</div>
