<template>
  <div class="container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">➕ 创建音色</h1>
      <p class="page-subtitle">上传音频样本，训练专属音色</p>
    </div>

    <!-- 创建表单 -->
    <div class="card">
      <!-- 步骤指示器 -->
      <div class="steps">
        <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
          <div class="step-number">1</div>
          <div class="step-label">音色信息</div>
        </div>
        <div class="step-line"></div>
        <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
          <div class="step-number">2</div>
          <div class="step-label">上传音频</div>
        </div>
        <div class="step-line"></div>
        <div class="step" :class="{ active: currentStep >= 3 }">
          <div class="step-number">3</div>
          <div class="step-label">完成创建</div>
        </div>
      </div>

      <!-- 步骤1: 音色信息 -->
      <div v-if="currentStep === 1" class="step-content">
        <h3 class="step-title">🏷️ 音色信息</h3>
        
        <div class="input-group">
          <label class="label">音色名称</label>
          <input
            v-model="voiceName"
            type="text"
            class="input"
            placeholder="例如：李老师、妈妈、爸爸"
            maxlength="20"
          />
          <div class="input-hint">给你的音色起个名字，方便识别</div>
        </div>

        <div class="step-actions">
          <button
            @click="nextStep"
            class="btn btn-primary"
            :disabled="!voiceName.trim()"
          >
            下一步 →
          </button>
        </div>
      </div>

      <!-- 步骤2: 上传音频 -->
      <div v-if="currentStep === 2" class="step-content">
        <h3 class="step-title">🎤 上传音频样本</h3>
        
        <!-- 录音区域 -->
        <div class="upload-area">
          <!-- 文件上传 -->
          <div class="upload-section">
            <input
              ref="fileInput"
              type="file"
              accept="audio/*"
              @change="handleFileSelect"
              class="file-input"
            />
            
            <div 
              @click="$refs.fileInput.click()"
              class="upload-zone"
              :class="{ 'has-file': selectedFile }"
            >
              <div v-if="!selectedFile" class="upload-placeholder">
                <div class="upload-icon">📁</div>
                <div class="upload-text">点击选择音频文件</div>
                <div class="upload-hint">支持 MP3、WAV、M4A 格式</div>
              </div>
              
              <div v-else class="file-info">
                <div class="file-icon">🎵</div>
                <div class="file-name">{{ selectedFile.name }}</div>
                <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
              </div>
            </div>
          </div>

          <!-- 录音提示 -->
          <div class="recording-tips">
            <h4 class="tips-title">📝 录音建议</h4>
            <ul class="tips-list">
              <li>录音时长建议 5-15 秒</li>
              <li>环境安静，声音清晰</li>
              <li>语速正常，发音标准</li>
              <li>可以说一段完整的话</li>
            </ul>
          </div>
        </div>

        <div class="step-actions">
          <button @click="prevStep" class="btn btn-secondary">
            ← 上一步
          </button>
          <button
            @click="nextStep"
            class="btn btn-primary"
            :disabled="!selectedFile"
          >
            下一步 →
          </button>
        </div>
      </div>

      <!-- 步骤3: 确认创建 -->
      <div v-if="currentStep === 3" class="step-content">
        <h3 class="step-title">✅ 确认创建</h3>
        
        <div class="creation-summary">
          <div class="summary-item">
            <span class="summary-label">音色名称：</span>
            <span class="summary-value">{{ voiceName }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">音频文件：</span>
            <span class="summary-value">{{ selectedFile?.name }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">文件大小：</span>
            <span class="summary-value">{{ formatFileSize(selectedFile?.size) }}</span>
          </div>
        </div>

        <div class="creation-note">
          <p>🔄 音色训练需要几分钟时间，请耐心等待</p>
        </div>

        <div class="step-actions">
          <button @click="prevStep" class="btn btn-secondary">
            ← 上一步
          </button>
          <button
            @click="createVoice"
            class="btn btn-primary"
            :disabled="isCreating"
          >
            <span v-if="!isCreating">🚀 开始创建</span>
            <span v-else class="flex items-center gap-2">
              <div class="loading-spinner"></div>
              创建中...
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- 创建成功 -->
    <div v-if="creationResult" class="card success-card">
      <div class="success-content">
        <div class="success-icon">🎉</div>
        <h3 class="success-title">创建成功！</h3>
        <p class="success-message">
          音色 "{{ creationResult.name }}" 已开始训练
        </p>
        
        <div class="success-actions">
          <router-link to="/voices" class="btn btn-primary">
            查看我的音色
          </router-link>
          <button @click="resetForm" class="btn btn-secondary">
            再创建一个
          </button>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="card error-card">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3 class="error-title">创建失败</h3>
        <p class="error-message">{{ error }}</p>
        
        <div class="error-actions">
          <button @click="clearError" class="btn btn-primary">
            重试
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/app.js'

// 使用store
const store = useAppStore()

// 响应式数据
const currentStep = ref(1)
const voiceName = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)
const isCreating = ref(false)
const creationResult = ref(null)

// 从store解构
const { error, clearError } = store
const { uploadVoiceSample } = store

// 方法
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 验证文件类型
    if (!file.type.startsWith('audio/')) {
      alert('请选择音频文件')
      return
    }
    
    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('文件过大，请选择小于10MB的音频文件')
      return
    }
    
    selectedFile.value = file
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const createVoice = async () => {
  if (!selectedFile.value || !voiceName.value.trim()) {
    return
  }
  
  try {
    isCreating.value = true
    
    const result = await uploadVoiceSample(selectedFile.value, voiceName.value.trim())
    
    if (result) {
      creationResult.value = result
      currentStep.value = 4 // 显示成功状态
    }
  } catch (err) {
    console.error('创建音色失败:', err)
  } finally {
    isCreating.value = false
  }
}

const resetForm = () => {
  currentStep.value = 1
  voiceName.value = ''
  selectedFile.value = null
  creationResult.value = null
  isCreating.value = false
  clearError()
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.page-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: var(--space-2);
}

.page-subtitle {
  color: var(--gray-600);
}

.steps {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-6);
  padding: 0 var(--space-4);
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--gray-200);
  color: var(--gray-500);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.2s ease;
}

.step.active .step-number {
  background: var(--primary);
  color: white;
}

.step.completed .step-number {
  background: var(--success);
  color: white;
}

.step-label {
  font-size: 12px;
  color: var(--gray-600);
  text-align: center;
}

.step.active .step-label {
  color: var(--primary);
  font-weight: 500;
}

.step-line {
  flex: 1;
  height: 2px;
  background: var(--gray-200);
  margin: 0 var(--space-2);
}

.step-content {
  margin-bottom: var(--space-6);
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--space-4);
  text-align: center;
}

.input-group {
  margin-bottom: var(--space-4);
}

.input-hint {
  font-size: 14px;
  color: var(--gray-500);
  margin-top: var(--space-1);
}

.upload-area {
  margin-bottom: var(--space-4);
}

.file-input {
  display: none;
}

.upload-zone {
  border: 2px dashed var(--gray-300);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: var(--space-4);
}

.upload-zone:hover {
  border-color: var(--primary);
  background: var(--gray-50);
}

.upload-zone.has-file {
  border-color: var(--success);
  background: var(--success);
  color: white;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.upload-icon {
  font-size: 32px;
}

.upload-text {
  font-weight: 500;
}

.upload-hint {
  font-size: 14px;
  color: var(--gray-500);
}

.file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.file-icon {
  font-size: 32px;
}

.file-name {
  font-weight: 500;
}

.file-size {
  font-size: 14px;
  opacity: 0.8;
}

.recording-tips {
  background: var(--gray-50);
  border-radius: var(--radius);
  padding: var(--space-4);
}

.tips-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: var(--space-3);
}

.tips-list {
  list-style: none;
  padding: 0;
}

.tips-list li {
  padding: var(--space-1) 0;
  font-size: 14px;
  color: var(--gray-600);
}

.tips-list li:before {
  content: "• ";
  color: var(--primary);
  font-weight: bold;
  margin-right: var(--space-2);
}

.creation-summary {
  background: var(--gray-50);
  border-radius: var(--radius);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--gray-200);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  color: var(--gray-600);
}

.summary-value {
  font-weight: 500;
}

.creation-note {
  text-align: center;
  padding: var(--space-3);
  background: var(--primary);
  color: white;
  border-radius: var(--radius);
  margin-bottom: var(--space-4);
}

.step-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
}

.success-card {
  background: var(--success);
  color: white;
  text-align: center;
}

.success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.success-icon {
  font-size: 48px;
}

.success-title {
  font-size: 20px;
  font-weight: 600;
}

.success-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.error-card {
  background: var(--error);
  color: white;
  text-align: center;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.error-icon {
  font-size: 48px;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
}

.error-actions {
  margin-top: var(--space-4);
}

/* 移动端优化 */
@media (max-width: 480px) {
  .steps {
    padding: 0;
  }
  
  .step-number {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  
  .step-label {
    font-size: 11px;
  }
  
  .step-actions {
    flex-direction: column;
  }
  
  .success-actions {
    flex-direction: column;
  }
}
</style>
