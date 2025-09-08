# 🤝 贡献指南

感谢你对"老师喊我去上学"项目的关注！我们欢迎所有形式的贡献，无论是代码、文档、设计还是想法。

## 📋 贡献方式

### 🐛 报告问题
- 在 [Issues](https://github.com/wangpeng1017/SOUND/issues) 中报告bug
- 使用问题模板，提供详细信息
- 包含复现步骤、环境信息和期望结果

### 💡 功能建议
- 在 [Issues](https://github.com/wangpeng1017/SOUND/issues) 中提出新功能
- 描述功能的使用场景和价值
- 讨论实现方案的可行性

### 📝 改进文档
- 修复文档中的错误或不清楚的地方
- 添加使用示例和最佳实践
- 翻译文档到其他语言

### 🔧 代码贡献
- 修复bug和改进性能
- 实现新功能
- 优化代码结构和设计

## 🚀 开发流程

### 1. 准备开发环境

```bash
# Fork 并克隆项目
git clone https://github.com/YOUR_USERNAME/SOUND.git
cd SOUND

# 安装依赖
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
cd ../ai-service && pip install -r requirements.txt

# 启动开发服务
python scripts/check_services.py
```

### 2. 创建功能分支

```bash
# 从master创建新分支
git checkout -b feature/your-feature-name

# 或修复bug
git checkout -b fix/bug-description
```

### 3. 开发和测试

```bash
# 进行开发...

# 运行测试
cd frontend && npm test
cd backend && pytest
cd ai-service && python -m pytest

# 检查代码质量
cd frontend && npm run lint
cd backend && flake8 .
```

### 4. 提交代码

```bash
# 添加更改
git add .

# 提交（遵循提交规范）
git commit -m "✨ feat: add voice quality assessment"

# 推送到你的fork
git push origin feature/your-feature-name
```

### 5. 创建Pull Request

- 在GitHub上创建Pull Request
- 填写PR模板，描述更改内容
- 等待代码审查和反馈

## 📝 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交类型

| 类型 | Emoji | 描述 |
|------|-------|------|
| `feat` | ✨ | 新功能 |
| `fix` | 🐛 | 修复bug |
| `docs` | 📚 | 文档更新 |
| `style` | 🎨 | 代码格式（不影响功能） |
| `refactor` | ♻️ | 重构代码 |
| `perf` | ⚡ | 性能优化 |
| `test` | ✅ | 测试相关 |
| `chore` | 🔧 | 构建/工具相关 |

### 提交格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 示例

```bash
✨ feat(tts): add edge-tts engine support
🐛 fix(audio): resolve upload validation issue
📚 docs(readme): update installation guide
🎨 style(frontend): improve button hover effects
♻️ refactor(backend): optimize API response structure
```

## 🧪 测试指南

### 前端测试
```bash
cd frontend
npm run test        # 单元测试
npm run test:e2e    # E2E测试
npm run lint        # 代码检查
```

### 后端测试
```bash
cd backend
pytest              # 运行所有测试
pytest -v           # 详细输出
flake8 .            # 代码风格检查
```

### AI服务测试
```bash
cd ai-service
python -m pytest    # 单元测试
python test_imports.py  # 导入测试
```

## 📋 代码规范

### Python代码规范
- 遵循 [PEP 8](https://pep8.org/) 风格指南
- 使用 `black` 进行代码格式化
- 使用 `flake8` 进行代码检查
- 添加类型提示（Type Hints）

### JavaScript代码规范
- 遵循 [ESLint](https://eslint.org/) 配置
- 使用 [Prettier](https://prettier.io/) 格式化
- 使用 Vue 3 Composition API
- 组件命名使用 PascalCase

### 文档规范
- 使用 Markdown 格式
- 添加适当的emoji增强可读性
- 包含代码示例和使用说明
- 保持文档与代码同步更新

## 🔍 代码审查

### 审查要点
- ✅ 功能是否正确实现
- ✅ 代码是否遵循项目规范
- ✅ 是否有适当的测试覆盖
- ✅ 文档是否更新
- ✅ 性能是否有影响

### 审查流程
1. 自动化测试通过
2. 至少一个维护者审查
3. 解决所有反馈意见
4. 合并到主分支

## 🎯 开发优先级

### 高优先级
- 🐛 Bug修复
- 🔒 安全问题
- 📱 用户体验改进

### 中优先级
- ✨ 新功能开发
- ⚡ 性能优化
- 📚 文档完善

### 低优先级
- 🎨 UI美化
- 🔧 工具改进
- 📊 代码重构

## 💬 交流渠道

- 📧 **邮件**: wangpeng1017@example.com
- 🐛 **问题**: [GitHub Issues](https://github.com/wangpeng1017/SOUND/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/wangpeng1017/SOUND/discussions)

## 🙏 致谢

感谢所有为项目做出贡献的开发者！你们的努力让这个项目变得更好。

### 贡献者列表
- [@wangpeng1017](https://github.com/wangpeng1017) - 项目创建者和维护者

---

再次感谢你的贡献！让我们一起打造更好的AI语音克隆应用！ 🎤✨
