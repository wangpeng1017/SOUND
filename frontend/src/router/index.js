import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/Home.vue'),
      meta: {
        title: '老师喊我去上学'
      }
    },
    {
      path: '/voices',
      name: 'Voices',
      component: () => import('../views/Voices.vue'),
      meta: {
        title: '我的音色'
      }
    },
    {
      path: '/create',
      name: 'Create',
      component: () => import('../views/Create.vue'),
      meta: {
        title: '创建音色'
      }
    }
  ]
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '老师喊我去上学'
  next()
})

export default router
