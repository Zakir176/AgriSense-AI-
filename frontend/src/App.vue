<template>
  <div class="h-screen bg-[#f4f7f4] text-gray-850 dark:bg-[#0f1412] dark:text-gray-150 flex font-sans transition-colors duration-200">
    <Toast />
    <!-- Render raw router-view for blank layout pages (like Login) -->
    <router-view v-if="isBlankLayout" class="flex-1 h-full" />

    <!-- Standard Dashboard App Layout -->
    <div v-else class="flex w-full">
      <!-- Mobile Backdrop -->
      <div 
        v-if="isMobileMenuOpen" 
        class="fixed inset-0 z-40 bg-black/50 md:hidden backdrop-blur-sm" 
        @click="isMobileMenuOpen = false"
      ></div>

      <!-- Sidebar -->
      <aside 
        class="fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 md:relative md:translate-x-0 w-64 flex flex-col bg-white dark:bg-[#181e1b] border-r border-gray-200 dark:border-gray-800 shrink-0"
        :class="isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
      >
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
        <header class="h-16 bg-white dark:bg-[#181e1b] border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 md:px-6 transition-colors duration-200">
          <div class="flex items-center space-x-3 md:hidden">
            <button 
              @click="isMobileMenuOpen = true"
              class="p-2 -ml-2 rounded-xl text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition focus:outline-none"
            >
              <span class="material-icons-outlined">menu</span>
            </button>
            <span class="text-lg font-extrabold tracking-wider text-primary-600 dark:text-primary-400">AGRISENSE AI</span>
          </div>
          <div class="hidden md:block text-sm text-gray-500 dark:text-gray-400">
            <label for="farm-selector" class="sr-only">Switch Farm</label>
            <div class="relative inline-block text-left" v-if="store.farmsList && store.farmsList.length > 1">
              <select
                id="farm-selector"
                :value="store.currentFarm ? store.currentFarm.id : ''"
                @change="e => {
                  const selectedId = parseInt(e.target.value)
                  const farm = store.farmsList.find(f => f.id === selectedId)
                  if (farm) handleFarmChange(farm)
                }"
                class="bg-gray-50 dark:bg-[#202723] text-gray-800 dark:text-white border border-gray-200 dark:border-gray-850 rounded-xl px-3 py-1.5 text-sm font-semibold focus:outline-none hover:bg-gray-150 dark:hover:bg-[#28312b] transition duration-150 cursor-pointer"
              >
                <option v-for="farm in store.farmsList" :key="farm.id" :value="farm.id">
                  🌱 {{ farm.name }}
                </option>
              </select>
            </div>
            <div v-else>
              Site: <span class="text-gray-850 dark:text-gray-200 font-semibold">{{ store.currentFarm ? store.currentFarm.name : 'Loading...' }}</span>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- Offline Indicator -->
            <div v-if="isOffline" class="flex items-center space-x-1.5 px-3 py-1.5 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-700 dark:text-amber-400 text-xs font-bold">
              <span class="material-icons-outlined text-sm">wifi_off</span>
              <span>Offline Mode</span>
            </div>
            <div v-if="isSyncing" class="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg text-blue-700 dark:text-blue-400 text-xs font-bold">
              <span class="material-icons-outlined text-sm animate-spin">sync</span>
              <span>Syncing...</span>
            </div>
            <!-- Manual Sync Trigger Button -->
            <button 
              v-if="syncQueueLength > 0"
              @click="syncOfflineData" 
              class="flex items-center space-x-1.5 px-2 md:px-3 py-1.5 bg-primary-50 dark:bg-primary-950/40 border border-primary-200 dark:border-primary-900 rounded-lg text-primary-750 dark:text-primary-400 text-xs font-black animate-pulse hover:bg-primary-100 dark:hover:bg-primary-900/50 transition focus:outline-none cursor-pointer"
              :disabled="isSyncing"
              aria-label="Pending Sync Queue"
            >
              <span class="material-icons-outlined text-sm animate-spin" v-if="isSyncing">sync</span>
              <span class="material-icons-outlined text-sm" v-else>cloud_upload</span>
              <span class="hidden sm:inline">Pending Sync ({{ syncQueueLength }})</span>
              <span class="sm:hidden">{{ syncQueueLength }}</span>
            </button>
            <!-- Notifications Bell -->
            <div class="relative">
              <button 
                @click="toggleNotifications"
                class="p-2 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition text-gray-500 dark:text-gray-400 focus:outline-none relative"
                aria-label="Notifications"
              >
                <span class="material-icons-outlined text-lg block">notifications</span>
                <span v-if="unreadAlertsCount > 0" class="absolute top-1.5 right-1.5 flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
                </span>
              </button>
              
              <!-- Dropdown -->
              <div v-if="showNotifications" class="absolute right-0 mt-2 w-80 bg-white dark:bg-darkbg-50 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800 overflow-hidden z-50">
                <div class="p-3 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50 dark:bg-darkbg-100">
                  <span class="font-bold text-sm text-gray-800 dark:text-white">Notifications</span>
                  <span class="text-xs bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-2 py-0.5 rounded-full font-bold">{{ unreadAlertsCount }} New</span>
                </div>
                <div class="max-h-64 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
                  <div v-if="alerts.length === 0" class="p-4 text-center text-xs text-gray-500">
                    No new alerts.
                  </div>
                  <div v-for="alert in alerts" :key="alert.id" class="p-3 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition flex gap-3 items-start cursor-pointer" @click="acknowledgeAlert(alert.id)">
                    <span class="material-icons-outlined text-[16px] mt-0.5" :class="alert.severity === 'critical' ? 'text-red-500' : 'text-amber-500'">
                      {{ alert.severity === 'critical' ? 'error' : 'warning' }}
                    </span>
                    <div class="flex-1">
                      <p class="text-xs font-semibold text-gray-800 dark:text-gray-200">{{ alert.message }}</p>
                      <p class="text-[10px] text-gray-500 mt-1">Click to dismiss</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

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
            <div class="flex items-center space-x-3 border-l border-gray-200 dark:border-gray-800 pl-3 md:pl-4">
              <div class="hidden sm:flex flex-col text-right">
                <span class="text-sm font-semibold text-gray-800 dark:text-white">
                  {{ store.currentUser ? store.currentUser.full_name || store.currentUser.username : 'Guest' }}
                </span>
                <span class="text-[10px] uppercase font-bold tracking-wider text-primary-650 dark:text-primary-400">
                  {{ store.currentFarm && store.currentFarm.role ? store.currentFarm.role : 'Guest' }}
                </span>
              </div>
              <div class="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-850 text-primary-700 dark:text-white flex items-center justify-center text-sm font-bold border border-primary-250 dark:border-primary-700 shrink-0">
                {{ store.currentUser ? (store.currentUser.full_name || store.currentUser.username).split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : '?' }}
              </div>
            </div>
          </div>
        </header>

        <!-- View Content Area -->
        <main class="flex-grow p-4 md:p-6 overflow-y-auto max-w-7xl w-full mx-auto relative">
          <router-view v-slot="{ Component }">
            <transition name="fade-slide" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from './services/api'
import { store } from './services/store'
import { getSyncQueue, removeFromSyncQueue } from './services/db'
import Toast from './components/Toast.vue'

const route = useRoute()
const router = useRouter()

const isBlankLayout = computed(() => route.meta.layout === 'blank')

// Mobile state
const isMobileMenuOpen = ref(false)

// Close mobile menu on route change
watch(() => route.path, () => {
  isMobileMenuOpen.value = false
})

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

const handleFarmChange = async (farm) => {
  store.currentFarm = farm
  try {
    const batches = await api.batches.list(farm.id)
    store.batchesList = batches
    const active = batches.find(b => b.status === 'active')
    if (active) {
      store.activeBatch = active
    } else if (batches.length > 0) {
      store.activeBatch = batches[0]
    } else {
      store.activeBatch = null
    }
  } catch (error) {
    console.error('Failed to load batches for farm:', error)
  }
}

const initApp = async () => {
  if (isBlankLayout.value) return

  const token = localStorage.getItem('agrisense_token')
  if (!token) {
    router.push({ name: 'Login' })
    return
  }

  try {
    // 1. Verify token & get user details
    const user = await api.auth.getMe()
    store.currentUser = user

    // 2. Fetch farms
    const farms = await api.farms.list()
    store.farmsList = farms
    
    if (farms && farms.length > 0) {
      // If current farm is not set or not in current list, pick first one
      if (!store.currentFarm || !farms.some(f => f.id === store.currentFarm.id)) {
        store.currentFarm = farms[0]
      }
      
      // 3. Fetch batches for the farm
      const batches = await api.batches.list(store.currentFarm.id)
      store.batchesList = batches
      
      // 4. Set first active batch as active
      const active = batches.find(b => b.status === 'active')
      if (active) {
        store.activeBatch = active
      } else if (batches.length > 0) {
        store.activeBatch = batches[0]
      } else {
        store.activeBatch = null
      }
    } else {
      store.currentFarm = null
      store.activeBatch = null
      store.batchesList = []
    }
  } catch (error) {
    console.error('Session initialization failed:', error)
    localStorage.removeItem('agrisense_token')
    router.push({ name: 'Login' })
  }
}

// Notifications Management
const alerts = ref([])
const showNotifications = ref(false)
const unreadAlertsCount = computed(() => alerts.value.length)
let alertsInterval = null

const fetchAlerts = async () => {
  if (isBlankLayout.value) return
  try {
    const unacknowledged = await api.alerts.list(null, true)
    alerts.value = unacknowledged
  } catch (error) {
    console.error('Failed to load alerts:', error)
  }
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    fetchAlerts()
  }
}

const acknowledgeAlert = async (id) => {
  try {
    await api.alerts.update(id, { acknowledged: true })
    alerts.value = alerts.value.filter(a => a.id !== id)
  } catch (error) {
    console.error('Failed to acknowledge alert:', error)
  }
}

// Background Sync Management
const isOffline = ref(!navigator.onLine)
const isSyncing = ref(false)
const syncQueueLength = ref(0)

const updateQueueLength = async () => {
  try {
    const queue = await getSyncQueue()
    syncQueueLength.value = queue.length
  } catch (error) {
    console.error('Failed to get sync queue length:', error)
  }
}

const handleOnline = async () => {
  isOffline.value = false
  await syncOfflineData()
}

const handleOffline = () => {
  isOffline.value = true
}

const syncOfflineData = async () => {
  if (isSyncing.value) return
  isSyncing.value = true
  await updateQueueLength()
  
  try {
    const queue = await getSyncQueue()
    if (queue.length > 0) {
      console.log(`[Sync] Found ${queue.length} items to sync`)
      for (const item of queue) {
        try {
          const apiBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'
          await fetch(`${apiBase}${item.url}`, {
            method: item.method,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('agrisense_token')}`
            },
            body: item.payload ? JSON.stringify(item.payload) : undefined
          })
          await removeFromSyncQueue(item.id)
          await updateQueueLength()
          console.log(`[Sync] Successfully synced request ${item.id}`)
        } catch (err) {
          console.error(`[Sync] Failed to sync request ${item.id}:`, err)
          // Stop syncing on first error to preserve order
          break
        }
      }
      
      // Refresh the app state by calling initApp to fetch fresh data
      await initApp()
    }
  } finally {
    isSyncing.value = false
    await updateQueueLength()
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

// Watch layout state: when user logs in and transitions from blank layout to main dashboard
watch(isBlankLayout, (newBlank) => {
  if (!newBlank) {
    initApp()
  } else {
    clearInterval(alertsInterval)
  }
})

let syncQueueInterval = null

onMounted(async () => {
  // Respect user preference, default to light mode (false) if none exists
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  applyTheme()
  
  await router.isReady()
  initApp()
  
  // Periodically check for alerts and sync queue size
  alertsInterval = setInterval(() => {
    fetchAlerts()
  }, 30000)

  await updateQueueLength()
  syncQueueInterval = setInterval(updateQueueLength, 3000)

  // Register online/offline listeners
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  
  // Check if we came online while the page was closed/reloading
  if (navigator.onLine) {
    syncOfflineData()
  }
})

onUnmounted(() => {
  clearInterval(alertsInterval)
  clearInterval(syncQueueInterval)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
  { name: 'Batches', path: '/batches', icon: 'layers' },
  { name: 'Feed & Water', path: '/readings', icon: 'opacity' },
  { name: 'Flock Growth', path: '/growth', icon: 'show_chart' },
  { name: 'Medications', path: '/medications', icon: 'vaccines' },
  { name: 'AI Visual Monitor', path: '/inference', icon: 'videocam' },
  { name: 'Audio Insights', path: '/audio', icon: 'hearing' },
  { name: 'Analytics', path: '/analytics', icon: 'analytics' },
  { name: 'Farm Settings', path: '/farm-settings', icon: 'settings' }
]

const isRouteActive = (path) => {
  if (path === '/dashboard') {
    return route.path === '/dashboard'
  }
  return route.path.startsWith(path)
}

const handleLogout = () => {
  localStorage.removeItem('agrisense_token')
  store.currentUser = null
  store.currentFarm = null
  store.activeBatch = null
  store.batchesList = []
  store.farmsList = []
  router.push({ name: 'Login' })
}
</script>

<style>
/* Load Google Fonts and Material Icons */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');

/* Page Transitions (Fade + Slide) */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 200ms cubic-bezier(0.4, 0, 0.2, 1), transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Mobile viewport override (150ms) */
@media (max-width: 768px) {
  .fade-slide-enter-active,
  .fade-slide-leave-active {
    transition-duration: 150ms;
  }
}

/* Respect user preferences for reduced motion */
@media (prefers-reduced-motion: reduce) {
  .fade-slide-enter-active,
  .fade-slide-leave-active {
    transition: opacity 150ms ease !important;
    transform: none !important;
    will-change: auto;
  }
  .fade-slide-enter-from,
  .fade-slide-leave-to {
    opacity: 0 !important;
    transform: none !important;
  }
}
</style>
