<template>
  <div class="container">
    <!-- 主功能卡片 -->
    <div class="card">
      <h2 class="card-title">✨ 输入文字，生成语音</h2>
      
      <!-- 文本输入 -->
      <div class="input-group">
        <label class="label">要说的话</label>
        <textarea 
          v-model="inputText"
          class="input textarea"
          placeholder="输入你想让老师/妈妈说的话..."
          maxlength="200"
        ></textarea>
        <div class="text-counter">{{ inputText.length }}/200</div>
      </div>

      <!-- 音色选择 -->
      <div class="input-group">
        <label class="label">选择音色</label>
        <div v-if="loading" class="loading-text">加载中...</div>
        <div v-else-if="voices.length === 0" class="no-voices">
          <span>暂无可用音色</span>
          <router-link to="/create" class="link">去创建 →</router-link>
        </div>
        <div v-else class="voice-selector">
          <button
            v-for="voice in voices"
            :key="voice.id"
            @click="selectedVoiceId = voice.id"
            class="voice-btn"
            :class="{ active: selectedVoiceId === voice.id }"
          >
            {{ voice.name }}
          </button>
        </div>
      </div>

      <!-- 生成按钮 -->
      <button
        @click="handleGenerate"
        class="btn btn-primary generate-btn"
        :disabled="!canGenerate || generating"
      >
        <span v-if="!generating">🎤 生成语音</span>
        <span v-else>生成中...</span>
      </button>
    </div>

    <!-- 结果展示 -->
    <div v-if="audioUrl" class="card result-card">
      <h3 class="result-title">🎵 生成结果</h3>
      <audio :src="audioUrl" controls class="audio-controls"></audio>
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
        >
          {{ phrase }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 最简单的响应式数据
const inputText = ref('')
const selectedVoiceId = ref('')
const loading = ref(false)
const generating = ref(false)
const audioUrl = ref('')
const voices = ref([])

// 是否可以生成
const canGenerate = computed(() => {
  return inputText.value.trim() && selectedVoiceId.value
})

// 快捷短语
const quickPhrases = [
  '该起床了，要迟到了！',
  '快去写作业！',
  '记得吃饭哦',
  '早点睡觉',
  '好好学习，天天向上',
  '注意安全'
]

// 加载音色列表
const loadVoices = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/voices')
    const data = await res.json()
    if (data?.data) {
      voices.value = data.data.filter(v => v.status === 'ready')
      // 默认选中第一个
      if (voices.value.length > 0 && !selectedVoiceId.value) {
        selectedVoiceId.value = voices.value[0].id
      }
    }
  } catch (e) {
    console.error('加载音色失败:', e)
  } finally {
    loading.value = false
  }
}

// 生成语音
const handleGenerate = async () => {
  if (!canGenerate.value || generating.value) return
  
  generating.value = true
  audioUrl.value = ''
  
  try {
    const response = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: inputText.value,
        voice_id: selectedVoiceId.value
      })
    })
    
    const data = await response.json()
    if (data.audio_url) {
      audioUrl.value = data.audio_url
    } else {
      throw new Error(data.error || '生成失败')
    }
  } catch (e) {
    console.error('生成语音失败:', e)
    alert('生成语音失败，请重试')
  } finally {
    generating.value = false
  }
}

// 页面加载时获取音色列表
onMounted(() => {
  loadVoices()
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

.loading-text {
  padding: var(--space-3);
  text-align: center;
  color: var(--gray-600);
  font-size: 14px;
}

.loading-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-3);
  margin-bottom: var(--space-4);
  background: var(--gray-50);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
}
</style>
