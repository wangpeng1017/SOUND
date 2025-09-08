# 🚀 Vercel部署指南

本文档详细说明如何将"老师喊我去上学"AI语音克隆应用部署到Vercel平台。

## 📋 部署概述

### 架构说明
- **前端**: 部署到Vercel (PWA应用)
- **后端API**: 部署到Heroku/Railway (Python FastAPI)
- **AI服务**: 部署到GPU云服务器 (语音处理)

### 部署策略
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Heroku        │    │   GPU Server    │
│   (前端PWA)     │───▶│   (后端API)     │───▶│   (AI服务)      │
│   Vue.js + PWA  │    │   FastAPI       │    │   TTS + 克隆    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Vercel配置

### 1. 项目配置文件

#### vercel.json
```json
{
  "version": 2,
  "name": "teacher-call-me-to-school",
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-backend-api.herokuapp.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

#### .vercelignore
```
backend/
ai-service/
node_modules/
.env.local
```

### 2. 环境变量配置

在Vercel控制台设置以下环境变量：

```bash
# API配置
VITE_API_BASE_URL=https://your-backend-api.herokuapp.com

# 应用配置
VITE_APP_TITLE=老师喊我去上学
VITE_APP_DESCRIPTION=极简AI语音克隆应用

# PWA配置
VITE_PWA_NAME=老师喊我去上学
VITE_PWA_SHORT_NAME=语音克隆
VITE_PWA_THEME_COLOR=#4F46E5
```

## 🚀 部署步骤

### 第1步: 准备GitHub仓库

```bash
# 确保代码已推送到GitHub
git add .
git commit -m "🚀 配置Vercel部署"
git push origin master
```

### 第2步: 连接Vercel

1. 访问 [Vercel控制台](https://vercel.com/dashboard)
2. 点击 "New Project"
3. 选择GitHub仓库: `wangpeng1017/SOUND`
4. 配置项目设置:
   ```
   Framework Preset: Vue.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

### 第3步: 配置环境变量

在Vercel项目设置中添加环境变量：

```bash
VITE_API_BASE_URL=https://your-backend-api.herokuapp.com
VITE_APP_TITLE=老师喊我去上学
VITE_APP_DESCRIPTION=极简AI语音克隆应用
```

### 第4步: 部署验证

1. **自动部署**: 推送代码到GitHub自动触发部署
2. **手动部署**: 在Vercel控制台点击 "Deploy"
3. **预览部署**: 每个PR都会生成预览链接

## 🔍 部署验证

### 自动化检查脚本

```bash
#!/bin/bash
# scripts/verify-vercel-deployment.sh

echo "🔍 验证Vercel部署..."

# 检查部署状态
VERCEL_URL="https://teacher-call-me-to-school.vercel.app"

# 测试主页
echo "📱 测试主页..."
curl -I $VERCEL_URL

# 测试PWA manifest
echo "📋 测试PWA manifest..."
curl -I $VERCEL_URL/manifest.json

# 测试Service Worker
echo "⚙️ 测试Service Worker..."
curl -I $VERCEL_URL/sw.js

echo "✅ 部署验证完成"
```

### 功能测试清单

- [ ] 主页正常加载
- [ ] PWA功能正常 (可安装)
- [ ] 路由跳转正常
- [ ] API请求正常 (如果后端已部署)
- [ ] 静态资源加载正常
- [ ] 移动端适配正常

## 🛠️ 故障排除

### 常见问题

#### 1. 构建失败
```bash
# 检查构建日志
npm run build

# 常见原因:
# - 依赖版本冲突
# - 环境变量缺失
# - 代码语法错误
```

#### 2. 路由404错误
```json
// vercel.json 确保包含SPA重写规则
{
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

#### 3. API请求失败
```javascript
// 检查API基础URL配置
const API_BASE = import.meta.env.VITE_API_BASE_URL
console.log('API Base URL:', API_BASE)
```

#### 4. PWA功能异常
```javascript
// 检查Service Worker注册
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}
```

### 调试工具

1. **Vercel日志**: 查看构建和运行时日志
2. **浏览器开发者工具**: 检查网络请求和控制台错误
3. **Lighthouse**: 测试PWA功能和性能

## 📊 性能优化

### 构建优化

```javascript
// vite.config.js
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia']
        }
      }
    }
  }
})
```

### CDN优化

```json
// vercel.json
{
  "headers": [
    {
      "source": "/(.*\\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2))",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

## 🔄 CI/CD集成

### GitHub Actions

```yaml
# .github/workflows/vercel-deploy.yml
name: Vercel Deploy
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Build
        run: cd frontend && npm run build
      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## 📞 支持

如果遇到部署问题，请：

1. 检查 [Vercel文档](https://vercel.com/docs)
2. 查看项目的GitHub Issues
3. 联系项目维护者

---

**部署成功后，你的应用将在以下地址可用:**
- 🌐 **生产环境**: https://teacher-call-me-to-school.vercel.app
- 🔧 **预览环境**: https://teacher-call-me-to-school-git-branch.vercel.app
