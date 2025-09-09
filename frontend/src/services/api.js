// 极简API服务模块

// API基础URL配置 - 支持多环境
const getApiBaseUrl = () => {
  // 生产环境
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_BASE_URL || 'https://your-backend-api.herokuapp.com'
  }
  // 开发环境
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

const API_BASE = getApiBaseUrl()

class ApiService {
  constructor() {
    this.baseURL = API_BASE
  }

  // 通用请求方法
  async request(url, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    try {
      const response = await fetch(`${this.baseURL}${url}`, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: '请求失败' }))
        throw new Error(error.detail || error.message || '请求失败')
      }

      return await response.json()
    } catch (error) {
      console.error('API请求错误:', error)
      throw error
    }
  }

  // GET请求
  async get(url) {
    return this.request(url, { method: 'GET' })
  }

  // POST请求
  async post(url, data) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // 文件上传
  async upload(url, formData) {
    return this.request(url, {
      method: 'POST',
      headers: {}, // 让浏览器自动设置Content-Type
      body: formData
    })
  }

  // ==================== 具体API方法 ====================

  // 获取音色列表
  async getVoices() {
    return this.get('/api/voices')
  }

  // 文字转语音
  async textToSpeech(text, voiceId = 'default') {
    return this.post('/api/tts', { text, voice_id: voiceId })
  }

  // 获取TTS任务状态
  async getTTSStatus(taskId) {
    return this.get(`/api/tts/status/${taskId}`)
  }

  // 上传音频样本
  async uploadVoiceSample(audioFile, voiceName, userId = 'user_1') {
    const formData = new FormData()
    formData.append('audio_file', audioFile)
    formData.append('name', voiceName)
    formData.append('user_id', userId)
    formData.append('description', `用户上传的音色：${voiceName}`)

    return this.upload('/api/voices', formData)
  }

  // 获取音频文件URL
  getAudioUrl(filename) {
    return `${this.baseURL}/api/audio/${filename}`
  }

  // 健康检查
  async healthCheck() {
    return this.get('/health')
  }
}

// 创建单例实例
const apiService = new ApiService()

export default apiService

// 导出具体方法供组件使用
export const {
  getVoices,
  textToSpeech,
  getTTSStatus,
  uploadVoiceSample,
  getAudioUrl,
  healthCheck
} = apiService
