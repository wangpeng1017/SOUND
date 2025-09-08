import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiService from '../services/api.js'

export const useAppStore = defineStore('app', () => {
  // ==================== 状态 ====================
  
  // 音色列表
  const voices = ref([])
  const voicesLoading = ref(false)
  
  // 当前选中的音色
  const selectedVoice = ref(null)
  
  // TTS相关状态
  const currentTask = ref(null)
  const isGenerating = ref(false)
  
  // 全局加载状态
  const globalLoading = ref(false)
  
  // 错误信息
  const error = ref(null)

  // ==================== 计算属性 ====================
  
  // 可用的音色列表
  const availableVoices = computed(() => {
    return voices.value.filter(voice => voice.status === 'ready')
  })
  
  // 是否有可用音色
  const hasVoices = computed(() => {
    return availableVoices.value.length > 0
  })
  
  // 当前任务是否完成
  const isTaskCompleted = computed(() => {
    return currentTask.value?.status === 'completed'
  })

  // ==================== 方法 ====================
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  // 设置错误
  const setError = (message) => {
    error.value = message
    console.error('应用错误:', message)
  }
  
  // 加载音色列表
  const loadVoices = async () => {
    try {
      voicesLoading.value = true
      clearError()
      
      const response = await apiService.getVoices()
      
      if (response.success) {
        voices.value = response.data
        
        // 如果没有选中音色，默认选择第一个
        if (!selectedVoice.value && voices.value.length > 0) {
          selectedVoice.value = voices.value[0]
        }
      }
    } catch (err) {
      setError('加载音色列表失败: ' + err.message)
    } finally {
      voicesLoading.value = false
    }
  }
  
  // 选择音色
  const selectVoice = (voice) => {
    selectedVoice.value = voice
  }
  
  // 文字转语音
  const generateSpeech = async (text) => {
    if (!text.trim()) {
      setError('请输入要转换的文字')
      return null
    }
    
    if (!selectedVoice.value) {
      setError('请选择一个音色')
      return null
    }
    
    try {
      isGenerating.value = true
      clearError()
      
      // 发起TTS请求
      const response = await apiService.textToSpeech(text, selectedVoice.value.id)
      
      if (response.success) {
        currentTask.value = {
          id: response.data.task_id,
          text: text,
          voice: selectedVoice.value,
          status: 'processing',
          progress: 0,
          audio_url: null
        }
        
        // 开始轮询任务状态
        pollTaskStatus(response.data.task_id)
        
        return response.data.task_id
      }
    } catch (err) {
      setError('生成语音失败: ' + err.message)
      isGenerating.value = false
      return null
    }
  }
  
  // 轮询任务状态
  const pollTaskStatus = async (taskId) => {
    const maxAttempts = 30 // 最多轮询30次
    let attempts = 0
    
    const poll = async () => {
      try {
        attempts++
        
        const response = await apiService.getTTSStatus(taskId)
        
        if (response.success) {
          const taskData = response.data
          
          // 更新当前任务状态
          if (currentTask.value && currentTask.value.id === taskId) {
            currentTask.value = {
              ...currentTask.value,
              status: taskData.status,
              progress: taskData.progress,
              audio_url: taskData.audio_url
            }
          }
          
          // 如果任务完成或失败，停止轮询
          if (taskData.status === 'completed' || taskData.status === 'failed') {
            isGenerating.value = false
            
            if (taskData.status === 'failed') {
              setError('语音生成失败')
            }
            
            return
          }
          
          // 如果任务还在进行中且未超过最大尝试次数，继续轮询
          if (attempts < maxAttempts) {
            setTimeout(poll, 1000) // 1秒后再次轮询
          } else {
            isGenerating.value = false
            setError('语音生成超时')
          }
        }
      } catch (err) {
        isGenerating.value = false
        setError('获取任务状态失败: ' + err.message)
      }
    }
    
    // 开始轮询
    poll()
  }
  
  // 上传音频样本
  const uploadVoiceSample = async (audioFile, voiceName) => {
    try {
      globalLoading.value = true
      clearError()
      
      const response = await apiService.uploadVoiceSample(audioFile, voiceName)
      
      if (response.success) {
        // 重新加载音色列表
        await loadVoices()
        return response.data
      }
    } catch (err) {
      setError('上传音频失败: ' + err.message)
      return null
    } finally {
      globalLoading.value = false
    }
  }
  
  // 清除当前任务
  const clearCurrentTask = () => {
    currentTask.value = null
    isGenerating.value = false
  }
  
  // 初始化应用
  const initApp = async () => {
    await loadVoices()
  }

  // ==================== 返回 ====================
  
  return {
    // 状态
    voices,
    voicesLoading,
    selectedVoice,
    currentTask,
    isGenerating,
    globalLoading,
    error,
    
    // 计算属性
    availableVoices,
    hasVoices,
    isTaskCompleted,
    
    // 方法
    clearError,
    setError,
    loadVoices,
    selectVoice,
    generateSpeech,
    uploadVoiceSample,
    clearCurrentTask,
    initApp
  }
})
