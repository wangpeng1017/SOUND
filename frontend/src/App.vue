<template>
  <div id="app">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container">
        <h1 class="logo">🎤 老师喊我去上学</h1>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 底部导航 -->
    <nav class="bottom-nav">
      <router-link to="/" class="nav-item" :class="{ active: $route.name === 'Home' }">
        <span class="nav-icon">🏠</span>
        <span class="nav-text">首页</span>
      </router-link>
      
      <router-link to="/voices" class="nav-item" :class="{ active: $route.name === 'Voices' }">
        <span class="nav-icon">🎵</span>
        <span class="nav-text">音色</span>
      </router-link>
      
      <router-link to="/create" class="nav-item" :class="{ active: $route.name === 'Create' }">
        <span class="nav-icon">➕</span>
        <span class="nav-text">创建</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
// 极简的App组件，无需复杂逻辑
</script>

<style scoped>
.header {
  background: white;
  border-bottom: 1px solid var(--gray-200);
  padding: var(--space-4) 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  text-align: center;
}

.main {
  min-height: calc(100vh - 140px); /* 减去header和bottom-nav的高度 */
  padding-bottom: var(--space-4);
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid var(--gray-200);
  display: flex;
  padding: var(--space-2) 0;
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2);
  text-decoration: none;
  color: var(--gray-500);
  transition: color 0.2s ease;
  min-height: 60px;
  justify-content: center;
}

.nav-item:hover,
.nav-item.active {
  color: var(--primary);
}

.nav-icon {
  font-size: 20px;
}

.nav-text {
  font-size: 12px;
  font-weight: 500;
}

/* 移动端优化 */
@media (max-width: 480px) {
  .logo {
    font-size: 18px;
  }
  
  .nav-icon {
    font-size: 18px;
  }
  
  .nav-text {
    font-size: 11px;
  }
}
</style>
