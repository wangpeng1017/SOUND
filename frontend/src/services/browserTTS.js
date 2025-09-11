// 浏览器原生 Web Speech API TTS 服务
// 完全免费，无需后端，立即可用

class BrowserTTSService {
  constructor() {
    this.synthesis = window.speechSynthesis
    this.currentUtterance = null
    this.voices = []
    this.isSupported = this.checkSupport()
    
    // 初始化时加载语音
    if (this.isSupported) {
      this.loadVoices()
      // 某些浏览器需要监听语音变化事件
      this.synthesis.onvoiceschanged = () => this.loadVoices()
    }
  }

  // 检查浏览器是否支持
  checkSupport() {
    return 'speechSynthesis' in window
  }

  // 加载可用的语音列表
  loadVoices() {
    const allVoices = this.synthesis.getVoices()
    
    // 优先筛选中文语音
    this.voices = allVoices.filter(voice => 
      voice.lang.includes('zh') || 
      voice.lang.includes('cmn') ||
      voice.lang.includes('CN')
    )
    
    // 如果没有中文语音，使用所有语音
    if (this.voices.length === 0) {
      this.voices = allVoices
    }
    
    return this.voices
  }

  // 获取语音列表（格式化为应用需要的格式）
  getVoices() {
    return this.voices.map(voice => ({
      id: voice.voiceURI,
      name: voice.name,
      lang: voice.lang,
      local: voice.localService
    }))
  }

  // 文字转语音
  async textToSpeech(text, voiceId = null) {
    if (!this.isSupported) {
      throw new Error('您的浏览器不支持语音合成功能')
    }

    // 停止之前的语音
    this.stop()

    return new Promise((resolve, reject) => {
      try {
        // 创建语音实例
        const utterance = new SpeechSynthesisUtterance(text)
        
        // 设置语音参数
        utterance.lang = 'zh-CN'
        utterance.rate = 1.0    // 语速 0.1-10
        utterance.pitch = 1.0   // 音调 0-2
        utterance.volume = 1.0  // 音量 0-1
        
        // 如果指定了语音ID，设置对应的语音
        if (voiceId) {
          const selectedVoice = this.voices.find(v => v.voiceURI === voiceId)
          if (selectedVoice) {
            utterance.voice = selectedVoice
          }
        }
        
        // 事件监听
        utterance.onstart = () => {
          console.log('开始播放语音')
        }
        
        utterance.onend = () => {
          console.log('语音播放完成')
          resolve({
            success: true,
            message: '语音播放完成'
          })
        }
        
        utterance.onerror = (event) => {
          console.error('语音合成错误:', event)
          reject(new Error('语音合成失败: ' + event.error))
        }
        
        // 保存引用
        this.currentUtterance = utterance
        
        // 开始语音合成
        this.synthesis.speak(utterance)
        
      } catch (error) {
        reject(error)
      }
    })
  }

  // 暂停播放
  pause() {
    if (this.synthesis.speaking) {
      this.synthesis.pause()
    }
  }

  // 恢复播放
  resume() {
    if (this.synthesis.paused) {
      this.synthesis.resume()
    }
  }

  // 停止播放
  stop() {
    this.synthesis.cancel()
  }

  // 检查是否正在播放
  isSpeaking() {
    return this.synthesis.speaking
  }

  // 检查是否暂停
  isPaused() {
    return this.synthesis.paused
  }
}

// 创建单例
const browserTTS = new BrowserTTSService()

export default browserTTS
