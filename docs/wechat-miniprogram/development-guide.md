# 🎤 微信小程序开发指南

## 📋 项目概述

将"老师喊我去上学"AI语音克隆应用转换为微信小程序，需要考虑技术架构、开发环境、API适配、功能实现等多个方面。

## 1. 技术要求和限制

### 🚫 主要限制

#### 技术限制
- **不支持Vue.js框架** - 需要使用原生小程序语法或uni-app
- **不支持PWA功能** - Service Worker、Web App Manifest等
- **不支持Web Audio API** - 需要使用小程序录音API
- **不支持MediaRecorder** - 需要使用wx.getRecorderManager()
- **网络请求限制** - 只能请求配置的合法域名
- **文件系统限制** - 无法直接访问本地文件系统

#### 功能限制
- **录音时长限制** - 最长60分钟
- **文件大小限制** - 单个文件最大100MB
- **并发请求限制** - 最多10个并发请求
- **本地存储限制** - 最大10MB
- **包大小限制** - 主包2MB，分包20MB

#### 权限限制
- **录音权限** - 需要用户授权
- **网络访问** - 需要配置服务器域名
- **用户信息** - 需要用户主动授权

### ✅ 技术优势

- **原生性能** - 接近原生应用体验
- **微信生态** - 无需下载安装，即用即走
- **用户身份** - 可获取微信用户信息
- **分享功能** - 支持分享到微信好友/群
- **支付功能** - 集成微信支付

## 2. 开发环境搭建

### 📱 必需工具

```bash
# 1. 微信开发者工具
下载地址: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

# 2. Node.js环境 (如使用uni-app)
node --version  # 建议v16+

# 3. 小程序开发框架选择
选项1: 原生小程序开发
选项2: uni-app (推荐)
选项3: Taro
```

### 🔧 开发环境配置

#### 方案1：原生小程序开发
```bash
# 1. 创建小程序项目
# 在微信开发者工具中创建新项目

# 2. 项目结构
miniprogram/
├── pages/           # 页面文件
├── components/      # 组件文件
├── utils/          # 工具函数
├── app.js          # 小程序逻辑
├── app.json        # 小程序配置
└── app.wxss        # 全局样式
```

#### 方案2：uni-app开发 (推荐)
```bash
# 1. 安装HBuilderX或使用CLI
npm install -g @vue/cli
vue create -p dcloudio/uni-preset-vue my-miniprogram

# 2. 项目结构
src/
├── pages/          # 页面
├── components/     # 组件
├── static/         # 静态资源
├── store/          # 状态管理
├── utils/          # 工具函数
├── App.vue         # 应用入口
├── main.js         # 入口文件
└── manifest.json   # 应用配置
```

## 3. 代码适配需求

### 🔄 Vue.js到小程序的转换

#### 页面结构转换
```javascript
// Vue.js (原)
<template>
  <div class="container">
    <h1>{{ title }}</h1>
    <button @click="handleClick">点击</button>
  </div>
</template>

// 小程序 (新)
<view class="container">
  <text class="title">{{ title }}</text>
  <button bindtap="handleClick">点击</button>
</view>
```

#### 生命周期转换
```javascript
// Vue.js (原)
export default {
  mounted() {
    this.init()
  },
  methods: {
    init() {}
  }
}

// 小程序 (新)
Page({
  onLoad() {
    this.init()
  },
  init() {}
})
```

#### 状态管理转换
```javascript
// Pinia (原)
import { useAppStore } from '@/stores/app'
const store = useAppStore()

// 小程序 (新) - 使用全局数据或mobx-miniprogram
const app = getApp()
app.globalData.xxx
```

### 📱 组件适配

#### 录音组件适配
```javascript
// Web Audio API (原)
const mediaRecorder = new MediaRecorder(stream)

// 小程序录音API (新)
const recorderManager = wx.getRecorderManager()
recorderManager.start({
  duration: 15000,
  sampleRate: 16000,
  numberOfChannels: 1,
  encodeBitRate: 48000,
  format: 'mp3'
})
```

#### 文件上传适配
```javascript
// Web FormData (原)
const formData = new FormData()
formData.append('file', file)

// 小程序上传 (新)
wx.uploadFile({
  url: 'https://api.example.com/upload',
  filePath: tempFilePath,
  name: 'file',
  success: (res) => {}
})
```

## 4. API和后端修改

### 🔧 后端API适配

#### 微信登录集成
```python
# 新增微信登录接口
@app.post("/api/wechat/login")
async def wechat_login(code: str):
    """微信小程序登录"""
    # 1. 通过code获取openid
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": WECHAT_APPID,
                "secret": WECHAT_SECRET,
                "js_code": code,
                "grant_type": "authorization_code"
            }
        )
    
    data = response.json()
    openid = data.get("openid")
    
    # 2. 查找或创建用户
    user = await get_or_create_user_by_openid(openid)
    
    # 3. 生成JWT token
    token = create_jwt_token(user.id)
    
    return {"token": token, "user": user}
```

#### 文件上传适配
```python
# 适配小程序文件上传
@app.post("/api/upload/audio")
async def upload_audio_miniprogram(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    voice_name: str = Form(...)
):
    """小程序音频上传"""
    # 验证文件格式 (小程序支持的格式)
    allowed_formats = ['mp3', 'aac', 'm4a', 'wav']
    
    # 上传到Vercel Blob
    result = await storage.upload_file(file, folder="miniprogram/voices")
    
    return {"success": True, "data": result}
```

### 🌐 域名配置

需要在微信公众平台配置以下域名：

```
request合法域名:
- https://your-api-domain.com
- https://your-ai-service.herokuapp.com

uploadFile合法域名:
- https://your-api-domain.com

downloadFile合法域名:
- https://blob.vercel-storage.com
```

## 5. 录音功能实现

### 🎤 小程序录音实现

```javascript
// 录音管理器
const recorderManager = wx.getRecorderManager()

// 录音组件
Component({
  data: {
    isRecording: false,
    recordTime: 0,
    tempFilePath: ''
  },
  
  methods: {
    // 开始录音
    startRecord() {
      // 检查录音权限
      wx.getSetting({
        success: (res) => {
          if (!res.authSetting['scope.record']) {
            // 请求录音权限
            wx.authorize({
              scope: 'scope.record',
              success: () => {
                this.doStartRecord()
              },
              fail: () => {
                wx.showModal({
                  title: '需要录音权限',
                  content: '请在设置中开启录音权限',
                  success: (res) => {
                    if (res.confirm) {
                      wx.openSetting()
                    }
                  }
                })
              }
            })
          } else {
            this.doStartRecord()
          }
        }
      })
    },
    
    // 执行录音
    doStartRecord() {
      recorderManager.start({
        duration: 15000,        // 最长15秒
        sampleRate: 16000,      // 采样率
        numberOfChannels: 1,    // 单声道
        encodeBitRate: 48000,   // 编码码率
        format: 'mp3'          // 格式
      })
      
      this.setData({ isRecording: true })
      this.startTimer()
    },
    
    // 停止录音
    stopRecord() {
      recorderManager.stop()
      this.setData({ isRecording: false })
      this.stopTimer()
    },
    
    // 计时器
    startTimer() {
      this.timer = setInterval(() => {
        this.setData({
          recordTime: this.data.recordTime + 1
        })
      }, 1000)
    },
    
    stopTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    }
  },
  
  ready() {
    // 监听录音结束
    recorderManager.onStop((res) => {
      this.setData({
        tempFilePath: res.tempFilePath
      })
      
      // 触发录音完成事件
      this.triggerEvent('recordComplete', {
        tempFilePath: res.tempFilePath,
        duration: res.duration,
        fileSize: res.fileSize
      })
    })
    
    // 监听录音错误
    recorderManager.onError((res) => {
      wx.showToast({
        title: '录音失败',
        icon: 'error'
      })
    })
  }
})
```

### 🎵 音频播放实现

```javascript
// 音频播放管理
const audioContext = wx.createAudioContext('audioPlayer')

// 播放组件
Component({
  properties: {
    audioUrl: String
  },
  
  methods: {
    playAudio() {
      if (this.properties.audioUrl) {
        audioContext.setSrc(this.properties.audioUrl)
        audioContext.play()
      }
    },
    
    pauseAudio() {
      audioContext.pause()
    },
    
    stopAudio() {
      audioContext.stop()
    }
  }
})
```

## 6. 部署和审核流程

### 📋 部署准备

#### 1. 小程序信息配置
```json
// app.json
{
  "pages": [
    "pages/index/index",
    "pages/create/create",
    "pages/voices/voices"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#4F46E5",
    "navigationBarTitleText": "老师喊我去上学",
    "navigationBarTextStyle": "white"
  },
  "permission": {
    "scope.record": {
      "desc": "需要录音权限来录制音频样本"
    }
  },
  "requiredBackgroundModes": ["audio"]
}
```

#### 2. 隐私政策配置
```json
// sitemap.json
{
  "desc": "关于本小程序的索引情况，可在小程序管理后台查看",
  "rules": [{
    "action": "allow",
    "page": "*"
  }]
}
```

### 🔍 审核要点

#### 必须满足的要求
1. **功能完整性** - 所有功能正常运行
2. **用户协议** - 明确的用户协议和隐私政策
3. **内容合规** - 不涉及违规内容
4. **权限说明** - 清楚说明权限用途
5. **错误处理** - 完善的错误提示

#### 可能的审核问题
1. **录音权限** - 需要明确说明录音用途
2. **AI功能** - 需要说明AI技术的使用
3. **用户生成内容** - 需要内容审核机制
4. **数据安全** - 需要说明数据处理方式

### 📝 审核材料准备

```
1. 小程序基本信息
   - 名称：老师喊我去上学
   - 类别：工具 > 语音工具
   - 标签：AI、语音、教育

2. 功能介绍
   - 核心功能：AI语音克隆
   - 使用场景：教育、娱乐
   - 目标用户：学生、家长、教师

3. 隐私政策
   - 数据收集说明
   - 数据使用说明
   - 数据保护措施

4. 用户协议
   - 服务条款
   - 使用规范
   - 免责声明
```

## 7. 微信特色功能

### 🎯 推荐集成的功能

#### 1. 微信登录
```javascript
// 微信登录
wx.login({
  success: (res) => {
    if (res.code) {
      // 发送code到后端
      this.loginWithCode(res.code)
    }
  }
})
```

#### 2. 分享功能
```javascript
// 分享到好友
onShareAppMessage() {
  return {
    title: '我创建了一个专属音色',
    path: '/pages/index/index',
    imageUrl: '/static/share-image.png'
  }
}

// 分享到朋友圈
onShareTimeline() {
  return {
    title: '老师喊我去上学 - AI语音克隆',
    imageUrl: '/static/timeline-image.png'
  }
}
```

#### 3. 用户信息获取
```javascript
// 获取用户信息
wx.getUserProfile({
  desc: '用于完善用户资料',
  success: (res) => {
    this.setData({
      userInfo: res.userInfo
    })
  }
})
```

### ⚠️ 需要避免的功能

1. **外部链接跳转** - 不能跳转到外部网页
2. **下载功能** - 不能提供APK等下载
3. **虚拟支付** - 不能使用非微信支付
4. **诱导分享** - 不能强制用户分享
5. **获取敏感信息** - 不能获取用户隐私数据

## 8. 开发时间估算

### 📅 开发周期规划

```
第1周：环境搭建和基础框架
- 开发环境配置
- 项目结构搭建
- 基础组件开发

第2周：核心功能开发
- 录音功能实现
- 音频上传功能
- 用户系统集成

第3周：AI功能集成
- 后端API适配
- 语音合成功能
- 音色管理功能

第4周：UI优化和测试
- 界面优化
- 功能测试
- 性能优化

第5周：审核准备和发布
- 审核材料准备
- 提交审核
- 问题修复
```

### 💰 成本估算

```
开发成本：
- 开发人员：1-2人 × 5周
- 设计师：0.5人 × 2周
- 测试人员：0.5人 × 1周

运营成本：
- 小程序认证费：300元/年
- 服务器费用：根据使用量
- 第三方服务费用：根据调用量
```

## 🎯 总结建议

### 优先级建议
1. **高优先级**：核心录音和TTS功能
2. **中优先级**：用户系统和音色管理
3. **低优先级**：分享和社交功能

### 技术选型建议
- **推荐使用uni-app**：可以同时支持小程序和H5
- **后端保持FastAPI**：性能好，易于维护
- **数据库使用PostgreSQL**：已有Vercel集成

### 风险控制
1. **提前准备审核材料**：避免审核延期
2. **功能分期上线**：先上线核心功能
3. **备用方案准备**：准备降级方案

通过以上详细的开发指南，你可以顺利地将Web应用转换为微信小程序，并充分利用微信生态的优势！

## 附录：uni-app项目结构示例

```
teacher-call-miniprogram/
├── src/
│   ├── pages/
│   │   ├── index/
│   │   │   ├── index.vue          # 首页
│   │   │   └── index.scss
│   │   ├── create/
│   │   │   ├── create.vue         # 创建音色页
│   │   │   └── create.scss
│   │   └── voices/
│   │       ├── voices.vue         # 音色列表页
│   │       └── voices.scss
│   ├── components/
│   │   ├── AudioRecorder/
│   │   │   └── AudioRecorder.vue  # 录音组件
│   │   ├── VoiceCard/
│   │   │   └── VoiceCard.vue      # 音色卡片组件
│   │   └── LoadingSpinner/
│   │       └── LoadingSpinner.vue # 加载组件
│   ├── store/
│   │   ├── index.js               # Vuex store
│   │   └── modules/
│   │       ├── user.js            # 用户模块
│   │       └── voice.js           # 音色模块
│   ├── utils/
│   │   ├── request.js             # 网络请求封装
│   │   ├── auth.js                # 微信登录
│   │   └── storage.js             # 本地存储
│   ├── static/
│   │   ├── images/                # 图片资源
│   │   └── icons/                 # 图标资源
│   ├── App.vue                    # 应用入口
│   ├── main.js                    # 入口文件
│   ├── manifest.json              # 应用配置
│   └── pages.json                 # 页面配置
├── package.json
└── README.md
```
