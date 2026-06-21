import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Batches from '../views/Batches.vue'
import FeedWater from '../views/FeedWater.vue'
import Growth from '../views/Growth.vue'
import Medications from '../views/Medications.vue'
import AIVisualMonitor from '../views/AIVisualMonitor.vue'
import AudioInsight from '../views/AudioInsight.vue'
import Analytics from '../views/Analytics.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, layout: 'blank' }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/batches',
    name: 'Batches',
    component: Batches,
    meta: { requiresAuth: true }
  },
  {
    path: '/readings',
    name: 'FeedWater',
    component: FeedWater,
    meta: { requiresAuth: true }
  },
  {
    path: '/growth',
    name: 'Growth',
    component: Growth,
    meta: { requiresAuth: true }
  },
  {
    path: '/medications',
    name: 'Medications',
    component: Medications,
    meta: { requiresAuth: true }
  },
  {
    path: '/inference',
    name: 'AIVisualMonitor',
    component: AIVisualMonitor,
    meta: { requiresAuth: true }
  },
  {
    path: '/audio',
    name: 'AudioInsight',
    component: AudioInsight,
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from) => {
  const isAuthenticated = !!localStorage.getItem('agrisense_token')
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    // If not authenticated, redirect to Login
    return { name: 'Login' }
  }
})

export default router
