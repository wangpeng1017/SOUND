<template>
  <div class="container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">🎵 我的音色</h1>
      <p class="page-subtitle">管理你的专属音色</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="voicesLoading" class="loading-card">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <!-- 音色列表 -->
    <div v-else-if="voices.length > 0" class="voices-grid">
      <div
        v-for="voice in voices"
        :key="voice.id"
        class="voice-card"
        :class="{ 
          active: selectedVoice?.id === voice.id,
          disabled: voice.status !== 'ready'
        }"
        @click="handleSelectVoice(voice)"
      >
        <!-- 音色状态指示器 -->
        <div class="voice-status">
          <span 
            class="status-dot"
            :class="{
              'status-ready': voice.status === 'ready',
              'status-training': voice.status === 'training',
              'status-failed': voice.status === 'failed'
            }"
          ></span>
        </div>

        <!-- 音色信息 -->
        <div class="voice-info">
          <h3 class="voice-name">{{ voice.name }}</h3>
          <p class="voice-status-text">
            <span v-if="voice.status === 'ready'">✅ 可用</span>
            <span v-else-if="voice.status === 'training'">⏳ 训练中</span>
            <span v-else-if="voice.status === 'failed'">❌ 失败</span>
            <span v-else>⚪ 未知状态</span>
          </p>
        </div>

        <!-- 选中指示器 -->
        <div v-if="selectedVoice?.id === voice.id" class="selected-indicator">
          ✓
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">🎤</div>
      <h3 class="empty-title">还没有音色</h3>
      <p class="empty-subtitle">创建你的第一个专属音色</p>
      <router-link to="/create" class="btn btn-primary">
        ➕ 创建音色
      </router-link>
    </div>

    <!-- 当前选中音色信息 -->
    <div v-if="selectedVoice" class="card selected-voice-info">
      <h3 class="info-title">当前选中</h3>
      <div class="selected-voice-details">
        <div class="voice-avatar">
          {{ selectedVoice.name.charAt(0) }}
        </div>
        <div class="voice-meta">
          <h4 class="voice-name">{{ selectedVoice.name }}</h4>
          <p class="voice-id">ID: {{ selectedVoice.id }}</p>
        </div>
      </div>
      
      <div class="voice-actions">
        <router-link to="/" class="btn btn-primary">
          🎤 去生成语音
        </router-link>
      </div>
    </div>

    <!-- 快速创建按钮 -->
    <div class="floating-action">
      <router-link to="/create" class="fab">
        ➕
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '../stores/app.js'

// 使用store
const store = useAppStore()

// 从store解构状态和方法
const {
  voices,
  voicesLoading,
  selectedVoice
} = store

const {
  selectVoice,
  loadVoices
} = store

// 方法
const handleSelectVoice = (voice) => {
  if (voice.status === 'ready') {
    selectVoice(voice)
  }
}

// 生命周期
onMounted(() => {
  loadVoices()
})
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
  color: var(--gray-800);
}

.page-subtitle {
  color: var(--gray-600);
  font-size: 16px;
}

.loading-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-8);
  text-align: center;
  color: var(--gray-600);
}

.voices-grid {
  display: grid;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.voice-card {
  background: white;
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.voice-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow);
}

.voice-card.active {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

.voice-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.voice-card.disabled:hover {
  border-color: var(--gray-200);
  box-shadow: none;
}

.voice-status {
  flex-shrink: 0;
}

.status-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-ready {
  background: var(--success);
}

.status-training {
  background: var(--warning);
  animation: pulse 2s infinite;
}

.status-failed {
  background: var(--error);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.voice-info {
  flex: 1;
}

.voice-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.voice-status-text {
  font-size: 14px;
  opacity: 0.8;
}

.selected-indicator {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  width: 24px;
  height: 24px;
  background: white;
  color: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: var(--space-2);
  color: var(--gray-700);
}

.empty-subtitle {
  color: var(--gray-500);
  margin-bottom: var(--space-6);
}

.selected-voice-info {
  background: var(--gray-50);
  border: 2px solid var(--primary);
}

.info-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: var(--space-4);
  color: var(--primary);
}

.selected-voice-details {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.voice-avatar {
  width: 48px;
  height: 48px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.voice-meta {
  flex: 1;
}

.voice-meta .voice-name {
  font-size: 18px;
  margin-bottom: var(--space-1);
}

.voice-id {
  font-size: 12px;
  color: var(--gray-500);
  font-family: monospace;
}

.voice-actions {
  text-align: center;
}

.floating-action {
  position: fixed;
  bottom: 80px; /* 避免与底部导航重叠 */
  right: var(--space-4);
  z-index: 50;
}

.fab {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  text-decoration: none;
  font-size: 24px;
  box-shadow: var(--shadow-lg);
  transition: all 0.2s ease;
}

.fab:hover {
  background: var(--primary-dark);
  transform: scale(1.1);
}

/* 移动端优化 */
@media (max-width: 480px) {
  .page-title {
    font-size: 20px;
  }
  
  .voice-card {
    padding: var(--space-3);
  }
  
  .floating-action {
    bottom: 70px;
    right: var(--space-3);
  }
  
  .fab {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
}
</style>
