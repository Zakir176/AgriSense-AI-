<template>
  <div class="h-screen bg-[#f4f7f4] text-gray-850 dark:bg-[#0f1412] dark:text-gray-150 flex font-sans transition-colors duration-200">
    <Toast />
    <TourGuide />
    <SyncDrawer />
    <!-- Render raw router-view for blank layout pages (like Login) -->
    <router-view v-if="isBlankLayout" class="flex-1 h-full" />

    <!-- Standard Dashboard App Layout -->
    <div v-else class="flex w-full">
      <!-- Sidebar Backdrop (Mobile only) -->
      <div 
        v-if="isSidebarOpen" 
        @click="isSidebarOpen = false" 
        class="fixed inset-0 bg-black/45 backdrop-blur-xs z-30 md:hidden transition-all duration-200"
      ></div>

      <!-- Sidebar -->
      <aside 
        class="fixed inset-y-0 left-0 z-40 flex flex-col bg-white dark:bg-[#181e1b] border-r border-gray-200 dark:border-gray-800 overflow-hidden shrink-0 transition-all duration-300 w-64 md:static md:inset-auto md:z-auto"
        :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-0'"
      >
        <!-- Logo -->
        <div class="h-16 flex items-center justify-between px-6 border-b border-gray-200 dark:border-gray-800">
          <span class="text-xl font-extrabold tracking-wider text-primary-600 dark:text-primary-400">AGRISENSE AI</span>
          <!-- Mobile Close Button -->
          <button 
            @click="isSidebarOpen = false"
            class="md:hidden p-1.5 rounded-lg border border-gray-150 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-850 transition text-gray-500 dark:text-gray-400 focus:outline-none cursor-pointer"
            aria-label="Close Sidebar"
          >
            <span class="material-icons-outlined text-lg block">close</span>
          </button>
        </div>

        <!-- Navigation Links -->
        <nav class="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          <router-link 
            v-for="item in navItems" 
            :key="item.path" 
            :to="item.path"
            :id="item.key === 'feed_water' ? 'nav-feed-water' : (item.key === 'ai_monitor' ? 'nav-ai-monitor' : 'nav-' + item.key)"
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
            <span>{{ $t('nav.' + item.key) }}</span>
          </router-link>
        </nav>

        <!-- Sidebar Footer / Logout -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-800 space-y-2">
          <button 
            @click="startTourGuide"
            class="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-primary-50 hover:bg-primary-100 dark:bg-primary-950/20 dark:hover:bg-primary-950/40 border border-primary-200/30 dark:border-primary-900/30 rounded-xl text-sm font-bold text-primary-750 dark:text-primary-400 transition cursor-pointer"
          >
            <span class="material-icons-outlined text-base">help_outline</span>
            <span>{{ $t('tour.restart') }}</span>
          </button>
          <button 
            @click="handleLogout"
            class="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-medium text-red-650 hover:bg-red-50 hover:border-red-200/30 dark:text-red-400 dark:hover:bg-red-950/20 border border-transparent dark:hover:border-red-900/30 transition cursor-pointer"
          >
            <span class="material-icons-outlined text-lg">logout</span>
            <span>{{ $t('app.sign_out') }}</span>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- Top Header Bar -->
        <header class="h-16 bg-white dark:bg-[#181e1b] border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 md:px-6 transition-colors duration-200">
          <div class="flex items-center space-x-3 md:hidden">
            <!-- Mobile Menu Toggle -->
            <button 
              @click="isSidebarOpen = !isSidebarOpen"
              class="p-2 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition text-gray-500 dark:text-gray-400 focus:outline-none cursor-pointer"
              :aria-label="isSidebarOpen ? 'Collapse Sidebar' : 'Expand Sidebar'"
            >
              <span class="material-icons-outlined text-lg block">{{ isSidebarOpen ? 'menu_open' : 'menu' }}</span>
            </button>
            <!-- Mobile-only logo (desktop has logo in sidebar) -->
            <span class="md:hidden text-xl font-extrabold tracking-wider text-primary-600 dark:text-primary-400">AGRISENSE AI</span>
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
              {{ $t('app.site') }} <span class="text-gray-850 dark:text-gray-200 font-semibold">{{ store.currentFarm ? store.currentFarm.name : $t('app.loading') }}</span>
            </div>
          </div>
          
          <div id="header-actions" class="flex items-center space-x-4">
            <!-- Offline Indicator -->
            <div v-if="isOffline" class="flex items-center space-x-1.5 px-2 sm:px-3 py-1.5 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-lg text-amber-700 dark:text-amber-400 text-xs font-bold">
              <span class="material-icons-outlined text-sm">wifi_off</span>
              <span class="hidden sm:inline">{{ $t('app.offline_mode') }}</span>
            </div>
            <div v-if="isSyncing" class="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg text-blue-700 dark:text-blue-400 text-xs font-bold">
              <span class="material-icons-outlined text-sm animate-spin">sync</span>
              <span>{{ $t('app.syncing') }}</span>
            </div>
            <!-- Manual Sync Trigger Button (opens Sync Drawer) -->
            <button 
              v-if="syncQueueLength > 0"
              @click="toggleDrawer" 
              class="flex items-center space-x-1.5 px-2 md:px-3 py-1.5 bg-primary-50 dark:bg-primary-950/40 border border-primary-200 dark:border-primary-900 rounded-lg text-primary-750 dark:text-primary-400 text-xs font-black animate-pulse hover:bg-primary-100 dark:hover:bg-primary-900/50 transition focus:outline-none cursor-pointer"
              aria-label="Pending Sync Queue"
            >
              <span class="material-icons-outlined text-sm animate-spin" v-if="isSyncing">sync</span>
              <span class="material-icons-outlined text-sm" v-else>cloud_upload</span>
              <span class="hidden sm:inline">{{ $t('app.pending_sync') }} ({{ syncQueueLength }})</span>
              <span class="sm:hidden">{{ syncQueueLength }}</span>
            </button>
            <!-- Notifications Bell -->
            <div class="relative" data-dropdown="notifications">
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
                  <span class="font-bold text-sm text-gray-800 dark:text-white">{{ $t('app.notifications') }}</span>
                  <span class="text-xs bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-2 py-0.5 rounded-full font-bold">{{ unreadAlertsCount }} {{ $t('app.new') }}</span>
                </div>
                <div class="max-h-64 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
                  <div v-if="alerts.length === 0" class="p-4 text-center text-xs text-gray-500">
                    {{ $t('app.no_alerts') }}
                  </div>
                  <div v-for="alert in alerts" :key="alert.id" class="p-3 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition flex gap-3 items-start cursor-pointer" @click="acknowledgeAlert(alert.id)">
                    <span class="material-icons-outlined text-[16px] mt-0.5" :class="alert.severity === 'critical' ? 'text-red-500' : 'text-amber-500'">
                      {{ alert.severity === 'critical' ? 'error' : 'warning' }}
                    </span>
                    <div class="flex-1">
                      <p class="text-xs font-semibold text-gray-800 dark:text-gray-200">{{ alert.message }}</p>
                      <p class="text-[10px] text-gray-500 mt-1">{{ $t('app.dismiss') }}</p>
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

            <!-- Language Switcher -->
            <div class="relative" data-dropdown="language">
              <button 
                @click="showLanguageDropdown = !showLanguageDropdown"
                class="flex items-center justify-center p-2 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition text-gray-500 dark:text-gray-400 focus:outline-none"
                aria-label="Switch Language"
              >
                <span class="material-icons-outlined text-lg">language</span>
                <span class="text-xs font-bold ml-1 uppercase">{{ $i18n.locale }}</span>
              </button>
              <div v-if="showLanguageDropdown" class="absolute right-0 mt-2 w-32 bg-white dark:bg-darkbg-50 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800 overflow-hidden z-50">
                <button @click="changeLanguage('en')" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-darkbg-100 transition text-gray-800 dark:text-gray-200" :class="{ 'font-bold text-primary-600': $i18n.locale === 'en' }">English</button>
                <button @click="changeLanguage('ny')" class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-darkbg-100 transition text-gray-800 dark:text-gray-200" :class="{ 'font-bold text-primary-600': $i18n.locale === 'ny' }">Nyanja</button>
              </div>
            </div>

            <!-- User Panel -->
            <div id="site-header-role" class="flex items-center space-x-3 border-l border-gray-200 dark:border-gray-800 pl-3 md:pl-4">
              <div class="hidden sm:flex flex-col text-right">
                <span class="text-sm font-semibold text-gray-800 dark:text-white">
                  {{ store.currentUser ? store.currentUser.full_name || store.currentUser.username : $t('app.guest') }}
                </span>
                <span class="text-[10px] uppercase font-bold tracking-wider text-primary-650 dark:text-primary-400">
                  {{ store.currentFarm && store.currentFarm.role ? store.currentFarm.role : $t('app.guest') }}
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
import Toast from './components/Toast.vue'
import TourGuide from './components/TourGuide.vue'
import SyncDrawer from './components/SyncDrawer.vue'
import { useSyncManager } from './composables/useSyncManager'
import { useReminders } from './composables/useReminders'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const route = useRoute()
const router = useRouter()

const showLanguageDropdown = ref(false)

const changeLanguage = (lang) => {
  locale.value = lang
  localStorage.setItem('language', lang)
  showLanguageDropdown.value = false
}

const isBlankLayout = computed(() => route.meta.layout === 'blank')

// Responsive Mobile Sidebar Management
// Open by default on desktop, closed on mobile — resolved in onMounted
const isSidebarOpen = ref(true)

watch(() => route.path, () => {
  // Only auto-close on mobile navigation
  if (window.innerWidth < 768) {
    isSidebarOpen.value = false
  }
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
    
    // Check if there is a saved focused batch ID in localStorage
    const savedFocusedId = localStorage.getItem('agrisense_focused_batch_id')
    let active = null
    if (savedFocusedId) {
      active = batches.find(b => b.id === parseInt(savedFocusedId) && b.status === 'active')
    }
    
    if (!active) {
      active = batches.find(b => b.status === 'active')
    }
    
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
      
      // 4. Restore focused batch selection if stored, otherwise default to first active batch
      const savedFocusedId = localStorage.getItem('agrisense_focused_batch_id')
      let active = null
      if (savedFocusedId) {
        active = batches.find(b => b.id === parseInt(savedFocusedId) && b.status === 'active')
      }
      
      if (!active) {
        active = batches.find(b => b.status === 'active')
      }
      
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

const handleClickOutside = (e) => {
  // Close language dropdown if clicking outside its container
  if (showLanguageDropdown.value && !e.target.closest('[data-dropdown="language"]')) {
    showLanguageDropdown.value = false
  }
  // Close notifications dropdown if clicking outside its container
  if (showNotifications.value && !e.target.closest('[data-dropdown="notifications"]')) {
    showNotifications.value = false
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

// Background Sync Management (delegated to useSyncManager composable)
const {
  isOffline,
  isSyncing,
  queueLength: syncQueueLength,
  toggleDrawer,
  syncAll,
  initialize: initSyncManager,
  destroy: destroySyncManager
} = useSyncManager()

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

onMounted(async () => {
  // Respect user preference, default to light mode (false) if none exists
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  applyTheme()

  // Close sidebar by default on mobile screens
  if (window.innerWidth < 768) {
    isSidebarOpen.value = false
  }

  await router.isReady()
  initApp()
  
  setTimeout(() => {
    const token = localStorage.getItem('agrisense_token')
    const onboarded = localStorage.getItem('agrisense_onboarded')
    if (token && !onboarded && !isBlankLayout.value) {
      startTourGuide()
    }
  }, 1000)
  
  // Periodically check for alerts
  alertsInterval = setInterval(() => {
    fetchAlerts()
  }, 30000)

  // Initialize sync manager (handles queue polling, online/offline listeners)
  initSyncManager()
  
  // Initialize reminders
  const { checkPendingReminders } = useReminders()
  checkPendingReminders()
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', handleClickOutside)
  
  // Auto-sync if we came online while the page was closed/reloading
  if (navigator.onLine) {
    syncAll()
  }
})

onUnmounted(() => {
  clearInterval(alertsInterval)
  destroySyncManager()
  document.removeEventListener('click', handleClickOutside)
})

const navItems = [
  { key: 'dashboard', path: '/dashboard', icon: 'dashboard' },
  { key: 'batches', path: '/batches', icon: 'layers' },
  { key: 'feed_water', path: '/readings', icon: 'opacity' },
  { key: 'flock_growth', path: '/growth', icon: 'show_chart' },
  { key: 'medications', path: '/medications', icon: 'vaccines' },
  { key: 'ai_monitor', path: '/inference', icon: 'videocam' },
  { key: 'audio', path: '/audio', icon: 'hearing' },
  { key: 'analytics', path: '/analytics', icon: 'analytics' },
  { key: 'settings', path: '/farm-settings', icon: 'settings' }
]

const isRouteActive = (path) => {
  if (path === '/dashboard') {
    return route.path === '/dashboard'
  }
  return route.path.startsWith(path)
}

const startTourGuide = () => {
  store.tour.active = true
  store.tour.currentStep = 0
  router.push('/dashboard')
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
