<template>
  <div class="audio-recorder">
    <!-- 录音控制区域 -->
    <div class="recorder-controls">
      <!-- 录音状态显示 -->
      <div class="recorder-status">
        <div class="status-indicator" :class="recordingState">
          <div v-if="recordingState === 'idle'" class="status-icon">🎤</div>
          <div v-else-if="recordingState === 'recording'" class="status-icon recording">🔴</div>
          <div v-else-if="recordingState === 'paused'" class="status-icon">⏸️</div>
          <div v-else-if="recordingState === 'stopped'" class="status-icon">⏹️</div>
        </div>
        
        <div class="status-info">
          <div class="status-text">{{ statusText }}</div>
          <div class="status-time">{{ formatTime(recordingTime) }}</div>
        </div>
      </div>

      <!-- 音量指示器 -->
      <div v-if="recordingState === 'recording'" class="volume-indicator">
        <div class="volume-bar">
          <div 
            class="volume-level" 
            :style="{ width: `${volumeLevel}%` }"
          ></div>
        </div>
        <div class="volume-text">音量: {{ Math.round(volumeLevel) }}%</div>
      </div>

      <!-- 录音按钮组 -->
      <div class="recorder-buttons">
        <button
          v-if="recordingState === 'idle'"
          @click="startRecording"
          class="btn btn-primary recorder-btn"
          :disabled="!microphonePermission"
        >
          <span class="btn-icon">🎤</span>
          开始录音
        </button>

        <button
          v-if="recordingState === 'recording'"
          @click="pauseRecording"
          class="btn btn-warning recorder-btn"
        >
          <span class="btn-icon">⏸️</span>
          暂停
        </button>

        <button
          v-if="recordingState === 'paused'"
          @click="resumeRecording"
          class="btn btn-primary recorder-btn"
        >
          <span class="btn-icon">▶️</span>
          继续
        </button>

        <button
          v-if="recordingState === 'recording' || recordingState === 'paused'"
          @click="stopRecording"
          class="btn btn-success recorder-btn"
        >
          <span class="btn-icon">⏹️</span>
          完成录音
        </button>

        <button
          v-if="recordingState === 'stopped' && audioBlob"
          @click="resetRecording"
          class="btn btn-secondary recorder-btn"
        >
          <span class="btn-icon">🔄</span>
          重新录制
        </button>
      </div>
    </div>

    <!-- 录音预览区域 -->
    <div v-if="recordingState === 'stopped' && audioBlob" class="recording-preview">
      <div class="preview-header">
        <h4 class="preview-title">🎵 录音预览</h4>
        <div class="preview-info">
          <span class="preview-duration">时长: {{ formatTime(recordingDuration) }}</span>
          <span class="preview-size">大小: {{ formatFileSize(audioBlob.size) }}</span>
        </div>
      </div>

      <!-- 音频播放器 -->
      <div class="audio-player">
        <audio
          ref="audioPlayer"
          :src="audioUrl"
          controls
          class="audio-controls"
        ></audio>
      </div>

      <!-- 录音质量评估 -->
      <div class="quality-assessment">
        <div class="quality-item" :class="qualityCheck.duration.status">
          <span class="quality-icon">⏱️</span>
          <span class="quality-text">{{ qualityCheck.duration.text }}</span>
        </div>
        <div class="quality-item" :class="qualityCheck.size.status">
          <span class="quality-icon">📦</span>
          <span class="quality-text">{{ qualityCheck.size.text }}</span>
        </div>
      </div>
    </div>

    <!-- 权限请求提示 -->
    <div v-if="!microphonePermission && showPermissionHint" class="permission-hint">
      <div class="hint-icon">🔒</div>
      <div class="hint-text">
        <p>需要麦克风权限才能录音</p>
        <p class="hint-sub">请点击浏览器地址栏的麦克风图标允许访问</p>
      </div>
      <button @click="requestMicrophonePermission" class="btn btn-primary">
        申请权限
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <div class="error-icon">❌</div>
      <div class="error-text">{{ error }}</div>
      <button @click="clearError" class="btn btn-secondary btn-sm">
        关闭
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

// Props
const props = defineProps({
  maxDuration: {
    type: Number,
    default: 15 // 最大录音时长（秒）
  },
  minDuration: {
    type: Number,
    default: 5 // 最小录音时长（秒）
  },
  format: {
    type: String,
    default: 'audio/webm;codecs=opus' // 录音格式
  }
})

// Emits
const emit = defineEmits(['recording-complete', 'recording-start', 'recording-stop'])

// 响应式数据
const recordingState = ref('idle') // idle, recording, paused, stopped
const microphonePermission = ref(false)
const showPermissionHint = ref(false)
const recordingTime = ref(0)
const recordingDuration = ref(0)
const volumeLevel = ref(0)
const audioBlob = ref(null)
const audioUrl = ref('')
const error = ref('')

// 录音相关
const mediaRecorder = ref(null)
const audioStream = ref(null)
const audioContext = ref(null)
const analyser = ref(null)
const recordingTimer = ref(null)
const volumeTimer = ref(null)
const audioChunks = ref([])

// 引用
const audioPlayer = ref(null)

// 计算属性
const statusText = computed(() => {
  switch (recordingState.value) {
    case 'idle':
      return microphonePermission.value ? '准备录音' : '需要麦克风权限'
    case 'recording':
      return '正在录音...'
    case 'paused':
      return '录音已暂停'
    case 'stopped':
      return '录音完成'
    default:
      return ''
  }
})

const qualityCheck = computed(() => {
  const duration = recordingDuration.value
  const size = audioBlob.value?.size || 0
  
  return {
    duration: {
      status: duration >= props.minDuration && duration <= props.maxDuration ? 'good' : 'warning',
      text: duration >= props.minDuration && duration <= props.maxDuration 
        ? `时长合适 (${props.minDuration}-${props.maxDuration}秒)` 
        : `建议时长 ${props.minDuration}-${props.maxDuration}秒`
    },
    size: {
      status: size > 0 && size < 5 * 1024 * 1024 ? 'good' : 'warning',
      text: size > 0 && size < 5 * 1024 * 1024 ? '文件大小合适' : '文件过大'
    }
  }
})

// 方法
const requestMicrophonePermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    microphonePermission.value = true
    showPermissionHint.value = false
    
    // 立即停止流，只是为了获取权限
    stream.getTracks().forEach(track => track.stop())
  } catch (err) {
    console.error('麦克风权限被拒绝:', err)
    error.value = '无法获取麦克风权限，请检查浏览器设置'
    showPermissionHint.value = true
  }
}

const startRecording = async () => {
  try {
    // 获取音频流
    audioStream.value = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })

    // 创建MediaRecorder
    const options = { mimeType: props.format }
    if (!MediaRecorder.isTypeSupported(props.format)) {
      options.mimeType = 'audio/webm'
    }
    
    mediaRecorder.value = new MediaRecorder(audioStream.value, options)
    audioChunks.value = []

    // 设置事件监听
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    mediaRecorder.value.onstop = () => {
      const blob = new Blob(audioChunks.value, { type: props.format })
      audioBlob.value = blob
      audioUrl.value = URL.createObjectURL(blob)
      recordingDuration.value = recordingTime.value
      
      emit('recording-complete', {
        blob,
        url: audioUrl.value,
        duration: recordingDuration.value,
        size: blob.size
      })
    }

    // 设置音量分析
    setupVolumeAnalysis()

    // 开始录音
    mediaRecorder.value.start(100) // 每100ms收集一次数据
    recordingState.value = 'recording'
    recordingTime.value = 0
    
    // 启动计时器
    startTimers()
    
    emit('recording-start')
    
  } catch (err) {
    console.error('开始录音失败:', err)
    error.value = '录音失败，请检查麦克风权限和设备'
  }
}

const pauseRecording = () => {
  if (mediaRecorder.value && recordingState.value === 'recording') {
    mediaRecorder.value.pause()
    recordingState.value = 'paused'
    stopTimers()
  }
}

const resumeRecording = () => {
  if (mediaRecorder.value && recordingState.value === 'paused') {
    mediaRecorder.value.resume()
    recordingState.value = 'recording'
    startTimers()
  }
}

const stopRecording = () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop()
    recordingState.value = 'stopped'
    stopTimers()
    
    // 停止音频流
    if (audioStream.value) {
      audioStream.value.getTracks().forEach(track => track.stop())
    }
    
    emit('recording-stop')
  }
}

const resetRecording = () => {
  recordingState.value = 'idle'
  recordingTime.value = 0
  recordingDuration.value = 0
  volumeLevel.value = 0
  audioBlob.value = null
  
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
    audioUrl.value = ''
  }
  
  audioChunks.value = []
  clearError()
}

const setupVolumeAnalysis = () => {
  try {
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
    analyser.value = audioContext.value.createAnalyser()
    
    const source = audioContext.value.createMediaStreamSource(audioStream.value)
    source.connect(analyser.value)
    
    analyser.value.fftSize = 256
  } catch (err) {
    console.error('音量分析设置失败:', err)
  }
}

const updateVolumeLevel = () => {
  if (analyser.value) {
    const bufferLength = analyser.value.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    analyser.value.getByteFrequencyData(dataArray)
    
    const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength
    volumeLevel.value = (average / 255) * 100
  }
}

const startTimers = () => {
  // 录音时间计时器
  recordingTimer.value = setInterval(() => {
    recordingTime.value++
    
    // 检查最大时长
    if (recordingTime.value >= props.maxDuration) {
      stopRecording()
    }
  }, 1000)
  
  // 音量检测计时器
  volumeTimer.value = setInterval(updateVolumeLevel, 100)
}

const stopTimers = () => {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
  
  if (volumeTimer.value) {
    clearInterval(volumeTimer.value)
    volumeTimer.value = null
  }
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const clearError = () => {
  error.value = ''
}

// 生命周期
onMounted(async () => {
  // 检查浏览器支持
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    error.value = '您的浏览器不支持录音功能'
    return
  }
  
  // 检查权限状态
  try {
    const permission = await navigator.permissions.query({ name: 'microphone' })
    microphonePermission.value = permission.state === 'granted'
    showPermissionHint.value = permission.state === 'denied'
    
    permission.onchange = () => {
      microphonePermission.value = permission.state === 'granted'
      showPermissionHint.value = permission.state === 'denied'
    }
  } catch (err) {
    // 某些浏览器不支持permissions API
    showPermissionHint.value = true
  }
})

onUnmounted(() => {
  stopTimers()
  
  if (audioStream.value) {
    audioStream.value.getTracks().forEach(track => track.stop())
  }
  
  if (audioContext.value) {
    audioContext.value.close()
  }
  
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
})

// 监听录音状态变化
watch(recordingState, (newState) => {
  if (newState === 'stopped' && audioBlob.value) {
    // 录音完成，可以在这里进行额外处理
  }
})
</script>

<style scoped>
.audio-recorder {
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  background: white;
}

.recorder-controls {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  align-items: center;
}

.recorder-status {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--gray-100);
  transition: all 0.3s ease;
}

.status-indicator.recording {
  background: var(--error);
  animation: pulse 1.5s infinite;
}

.status-icon {
  font-size: 24px;
}

.status-icon.recording {
  color: white;
}

.status-info {
  text-align: center;
}

.status-text {
  font-weight: 500;
  margin-bottom: var(--space-1);
}

.status-time {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary);
  font-family: 'Courier New', monospace;
}

.volume-indicator {
  width: 100%;
  max-width: 300px;
}

.volume-bar {
  width: 100%;
  height: 8px;
  background: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--space-1);
}

.volume-level {
  height: 100%;
  background: linear-gradient(90deg, var(--success), var(--warning), var(--error));
  transition: width 0.1s ease;
}

.volume-text {
  text-align: center;
  font-size: 12px;
  color: var(--gray-600);
}

.recorder-buttons {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  justify-content: center;
}

.recorder-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  min-width: 120px;
  justify-content: center;
}

.btn-icon {
  font-size: 16px;
}

.recording-preview {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--gray-200);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.preview-info {
  display: flex;
  gap: var(--space-3);
  font-size: 14px;
  color: var(--gray-600);
}

.audio-player {
  margin-bottom: var(--space-3);
}

.audio-controls {
  width: 100%;
  height: 40px;
}

.quality-assessment {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius);
  font-size: 14px;
}

.quality-item.good {
  background: var(--success);
  color: white;
}

.quality-item.warning {
  background: var(--warning);
  color: white;
}

.quality-icon {
  font-size: 16px;
}

.permission-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--warning);
  color: white;
  border-radius: var(--radius);
  text-align: center;
}

.hint-icon {
  font-size: 32px;
}

.hint-text p {
  margin: 0;
}

.hint-sub {
  font-size: 14px;
  opacity: 0.9;
  margin-top: var(--space-1);
}

.error-message {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--error);
  color: white;
  border-radius: var(--radius);
  margin-top: var(--space-3);
}

.error-icon {
  font-size: 20px;
}

.error-text {
  flex: 1;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 移动端优化 */
@media (max-width: 480px) {
  .recorder-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .recorder-btn {
    width: 100%;
  }
  
  .preview-header {
    flex-direction: column;
    gap: var(--space-2);
    align-items: flex-start;
  }
  
  .quality-assessment {
    flex-direction: column;
  }
  
  .quality-item {
    justify-content: center;
  }
}
</style>
