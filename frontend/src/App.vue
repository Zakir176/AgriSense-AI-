<template>
  <div class="h-screen bg-[#f4f7f4] text-gray-850 dark:bg-[#0f1412] dark:text-gray-150 flex font-sans transition-colors duration-200">
    <!-- Render raw router-view for blank layout pages (like Login) -->
    <router-view v-if="isBlankLayout" class="flex-1 h-full" />

    <!-- Standard Dashboard App Layout -->
    <div v-else class="flex w-full">
      <!-- Sidebar -->
      <aside class="hidden md:flex md:w-64 flex-col bg-white dark:bg-[#181e1b] border-r border-gray-200 dark:border-gray-800 shrink-0 transition-colors duration-200">
        <!-- Logo -->
        <div class="h-16 flex items-center px-6 border-b border-gray-200 dark:border-gray-800">
          <span class="text-xl font-extrabold tracking-wider text-primary-600 dark:text-primary-400">AGRISENSE AI</span>
        </div>

        <!-- Navigation Links -->
        <nav class="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          <router-link 
            v-for="item in navItems" 
            :key="item.path" 
            :to="item.path"
            class="flex items-center space-x-3 px-4 py-2.5 rounded-xl text-sm font-medium transition group"
            :class="[
              isRouteActive(item.path)
                ? 'bg-primary-50 text-primary-700 border border-primary-200/50 dark:bg-primary-950/60 dark:text-primary-400 dark:border-primary-900/50'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/40 hover:text-gray-900 dark:hover:text-white border border-transparent'
            ]"
          >
            <span class="material-icons-outlined text-lg" :class="isRouteActive(item.path) ? 'text-primary-600 dark:text-primary-400' : 'text-gray-450 dark:text-gray-500 group-hover:text-gray-700 dark:group-hover:text-white'">
              {{ item.icon }}
            </span>
            <span>{{ item.name }}</span>
          </router-link>
        </nav>

        <!-- Sidebar Footer / Logout -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-800">
          <button 
            @click="handleLogout"
            class="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-medium text-red-650 hover:bg-red-50 hover:border-red-200/30 dark:text-red-400 dark:hover:bg-red-950/20 border border-transparent dark:hover:border-red-900/30 transition"
          >
            <span class="material-icons-outlined text-lg">logout</span>
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Top Header Bar -->
        <header class="h-16 bg-white dark:bg-[#181e1b] border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-6 transition-colors duration-200">
          <div class="flex items-center space-x-3 md:hidden">
            <span class="text-xl font-extrabold tracking-wider text-primary-600 dark:text-primary-400">AGRISENSE AI</span>
          </div>
          <div class="hidden md:block text-sm text-gray-500 dark:text-gray-400">
            Site: <span class="text-gray-850 dark:text-gray-200 font-semibold">{{ store.currentFarm ? store.currentFarm.name : 'Loading...' }}</span>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Theme Toggle Button -->
            <button 
              @click="toggleTheme" 
              class="p-2 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition text-gray-500 dark:text-gray-400 focus:outline-none"
              aria-label="Toggle Theme"
            >
              <span class="material-icons-outlined text-lg block">
                {{ isDark ? 'light_mode' : 'dark_mode' }}
              </span>
            </button>

            <!-- User Panel -->
            <div class="flex items-center space-x-3 border-l border-gray-200 dark:border-gray-800 pl-4">
              <div class="flex flex-col text-right">
                <span class="text-sm font-semibold text-gray-800 dark:text-white">Evans Kabwe</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">Operator</span>
              </div>
              <div class="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-850 text-primary-700 dark:text-white flex items-center justify-center text-sm font-bold border border-primary-250 dark:border-primary-700">
                EK
              </div>
            </div>
          </div>
        </header>

        <!-- View Content Area -->
        <main class="flex-grow p-6 overflow-y-auto max-w-7xl w-full mx-auto">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from './services/api'
import { store } from './services/store'

const route = useRoute()
const router = useRouter()

const isBlankLayout = computed(() => route.meta.layout === 'blank')

// Theme management
const isDark = ref(false)

const applyTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

const initApp = async () => {
  if (isBlankLayout.value) return

  const token = localStorage.getItem('agrisense_token')
  if (!token) {
    router.push({ name: 'Login' })
    return
  }

  try {
    // 1. Verify token
    await api.auth.getMe()

    // 2. Fetch farms
    const farms = await api.farms.list()
    if (farms && farms.length > 0) {
      store.currentFarm = farms[0]
      
      // 3. Fetch batches for the farm
      const batches = await api.batches.list(store.currentFarm.id)
      store.batchesList = batches
      
      // 4. Set first active batch as active
      const active = batches.find(b => b.status === 'active')
      if (active) {
        store.activeBatch = active
      } else if (batches.length > 0) {
        // Fallback to first batch if no active one exists
        store.activeBatch = batches[0]
      }
    }
  } catch (error) {
    console.error('Session initialization failed:', error)
    localStorage.removeItem('agrisense_token')
    router.push({ name: 'Login' })
  }
}

// Watch layout state: when user logs in and transitions from blank layout to main dashboard
watch(isBlankLayout, (newBlank) => {
  if (!newBlank) {
    initApp()
  }
})

onMounted(() => {
  // Respect user preference, default to light mode (false) if none exists
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  applyTheme()
  
  initApp()
})

const navItems = [
  { name: 'Dashboard', path: '/', icon: 'dashboard' },
  { name: 'Batches', path: '/batches', icon: 'layers' },
  { name: 'Feed & Water', path: '/readings', icon: 'opacity' },
  { name: 'Flock Growth', path: '/growth', icon: 'show_chart' },
  { name: 'Medications', path: '/medications', icon: 'vaccines' },
  { name: 'AI Visual Monitor', path: '/inference', icon: 'videocam' },
  { name: 'Audio Insights', path: '/audio', icon: 'hearing' },
  { name: 'Analytics', path: '/analytics', icon: 'analytics' }
]

const isRouteActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const handleLogout = () => {
  localStorage.removeItem('agrisense_token')
  store.currentFarm = null
  store.activeBatch = null
  store.batchesList = []
  router.push({ name: 'Login' })
}
</script>

<style>
/* Load Google Fonts and Material Icons */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');
</style>
