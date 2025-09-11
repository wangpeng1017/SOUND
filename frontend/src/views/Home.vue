<template>
  <div class="container">
    <!-- 错误提示 -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="clearError" class="error-close">×</button>
    </div>

    <!-- 主要功能卡片 -->
    <div class="card">
      <h2 class="card-title">✨ 输入文字，生成语音</h2>
      
      <!-- 文本输入 -->
      <div class="input-group">
        <label class="label">要说的话</label>
        <textarea 
          v-model="inputText"
          class="input textarea"
          placeholder="输入你想让老师/妈妈说的话..."
          :disabled="isGenerating"
          maxlength="200"
        ></textarea>
        <div class="text-counter">{{ inputText.length }}/200</div>
      </div>

      <!-- 音色选择 -->
      <div class="input-group">
        <label class="label">选择音色</label>
        <div class="voice-selector">
          <button
            v-for="voice in combinedVoices"
            :key="voice.id"
            @click="selectVoice(voice)"
            class="voice-btn"
            :class="{ active: selectedVoice?.id === voice.id }"
            :disabled="isGenerating"
          >
            {{ voice.name }}
          </button>
        </div>
        <div v-if="combinedVoices.length === 0" class="no-voices">
          <span class="text-gray-500">暂无可用音色</span>
          <router-link to="/create" class="link">去创建 →</router-link>
        </div>
      </div>

      <!-- 生成按钮 -->
      <button
        @click="handleGenerate"
        class="btn btn-primary generate-btn"
        :disabled="!canGenerate"
      >
        <span v-if="!isGenerating">🎤 生成语音</span>
        <span v-else class="flex items-center gap-2">
          <div class="loading-spinner"></div>
          生成中... {{ currentTask?.progress || 0 }}%
        </span>
      </button>
    </div>

    <!-- 结果展示 -->
    <div v-if="currentTask" class="card result-card">
      <h3 class="result-title">🎵 生成结果</h3>
      
      <div class="result-info">
        <div class="result-text">"{{ currentTask.text }}"</div>
        <div class="result-voice">音色：{{ currentTask.voice?.name }}</div>
      </div>

      <!-- 音频播放器 -->
      <div v-if="isTaskCompleted && currentTask.audio_url" class="audio-player">
        <audio 
          ref="audioPlayer"
          :src="getAudioUrl(currentTask.audio_url)"
          controls
          class="audio-controls"
        ></audio>
        
        <div class="audio-actions">
          <button @click="playAudio" class="btn btn-secondary">
            🔊 播放
          </button>
          <button @click="downloadAudio" class="btn btn-secondary">
            📥 下载
          </button>
        </div>
      </div>

      <!-- 处理状态 -->
      <div v-else-if="isGenerating" class="processing-status">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: (currentTask?.progress || 0) + '%' }"
          ></div>
        </div>
        <div class="status-text">正在生成语音，请稍候...</div>
      </div>
    </div>

    <!-- 快捷短语 -->
    <div class="card">
      <h3 class="card-title">💡 快捷短语</h3>
      <div class="quick-phrases">
        <button
          v-for="phrase in quickPhrases"
          :key="phrase"
          @click="inputText = phrase"
          class="phrase-btn"
          :disabled="isGenerating"
        >
          {{ phrase }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '../stores/app.js'
import apiService from '../services/api.js'
import browserTTS from '../services/browserTTS.js'

// 使用store
const store = useAppStore()

// 响应式数据
const inputText = ref('')
const audioPlayer = ref(null)
const useBrowserTTS = ref(true) // 默认使用浏览器TTS
const isPlaying = ref(false)

// 快捷短语
const quickPhrases = [
  '该起床了，要迟到了！',
  '快去写作业！',
  '记得吃饭哦',
  '早点睡觉',
  '好好学习，天天向上',
  '注意安全'
]

// 计算属性
const canGenerate = computed(() => {
  return inputText.value.trim() && 
         store.selectedVoice && 
         !store.isGenerating
})

// 从store解构需要的状态和方法
const {
  availableVoices,
  selectedVoice,
  currentTask,
  isGenerating,
  error,
  isTaskCompleted
} = store

const {
  clearError,
  selectVoice,
  generateSpeech
} = store

// 组合音色（store + 后备直连 API），避免后端瞬时内存导致的列表为空
const fallbackVoices = ref([])
const combinedVoices = computed(() => {
  const map = new Map()
  ;[...availableVoices.value, ...fallbackVoices.value].forEach(v => {
    if (v && v.id && !map.has(v.id) && (v.status === 'ready')) {
      map.set(v.id, { id: v.id, name: v.name, status: v.status })
    }
  })
  return Array.from(map.values())
})

// 方法
const handleGenerate = async () => {
  if (!canGenerate.value) return
  
  // 如果启用浏览器TTS，直接在前端合成
  if (useBrowserTTS.value && browserTTS.isSupported) {
    try {
      clearError()
      isPlaying.value = true
      
      // 使用选中的音色ID（如果是浏览器音色）
      const voiceId = selectedVoice.value?.id
      
      // 调用浏览器TTS
      await browserTTS.textToSpeech(inputText.value, voiceId)
      
      isPlaying.value = false
    } catch (error) {
      console.error('浏览器TTS失败:', error)
      isPlaying.value = false
      // 回退到服务器TTS
      await generateSpeech(inputText.value)
    }
  } else {
    // 使用服务器端TTS
    await generateSpeech(inputText.value)
  }
}

const getAudioUrl = (audioUrl) => {
  if (audioUrl.startsWith('http')) {
    return audioUrl
  }
  return apiService.getAudioUrl(audioUrl.replace('/api/audio/', ''))
}

const playAudio = () => {
  if (audioPlayer.value) {
    audioPlayer.value.play()
  }
}

const downloadAudio = () => {
  if (currentTask.value?.audio_url) {
    const link = document.createElement('a')
    link.href = getAudioUrl(currentTask.value.audio_url)
    link.download = `语音_${Date.now()}.mp3`
    link.click()
  }
}

// 生命周期
onMounted(async () => {
  store.initApp()
  // 后备直连获取音色清单
  try {
    const res = await fetch('/api/voices')
    const data = await res.json()
    if (data?.success && Array.isArray(data.data)) {
      fallbackVoices.value = data.data
      // 若当前未选择音色，默认选择第一个
      if (!selectedVoice.value && fallbackVoices.value.length > 0) {
        selectVoice(fallbackVoices.value[0])
      }
    }
  } catch (_) {}
})
</script>

<style scoped>
.error-banner {
  background: var(--error);
  color: white;
  padding: var(--space-3);
  border-radius: var(--radius);
  margin-bottom: var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--space-4);
  text-align: center;
}

.input-group {
  margin-bottom: var(--space-4);
}

.text-counter {
  text-align: right;
  font-size: 12px;
  color: var(--gray-500);
  margin-top: var(--space-1);
}

.voice-selector {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.voice-btn {
  padding: var(--space-2) var(--space-4);
  border: 2px solid var(--gray-200);
  border-radius: var(--radius);
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.voice-btn:hover {
  border-color: var(--primary);
}

.voice-btn.active {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

.voice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-voices {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  background: var(--gray-50);
  border-radius: var(--radius);
}

.link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.generate-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
}

.result-card {
  background: var(--gray-50);
  border: 2px solid var(--success);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: var(--space-3);
  color: var(--success);
}

.result-info {
  margin-bottom: var(--space-4);
}

.result-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: var(--space-2);
  padding: var(--space-3);
  background: white;
  border-radius: var(--radius);
}

.result-voice {
  font-size: 14px;
  color: var(--gray-600);
}

.audio-player {
  text-align: center;
}

.audio-controls {
  width: 100%;
  margin-bottom: var(--space-3);
}

.audio-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: center;
}

.processing-status {
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s ease;
}

.status-text {
  font-size: 14px;
  color: var(--gray-600);
}

.quick-phrases {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.phrase-btn {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--gray-300);
  border-radius: var(--radius);
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.phrase-btn:hover {
  background: var(--gray-50);
  border-color: var(--primary);
}

.phrase-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
