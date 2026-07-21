import { ref, computed, watch } from 'vue'
import { getSyncQueue, removeFromSyncQueue } from '../services/db'

// ---- Singleton State (shared across all consumers) ----
const queueItems = ref([])
const isSyncing = ref(false)
const isOffline = ref(!navigator.onLine)
const isDrawerOpen = ref(false)
const syncProgress = ref({ current: 0, total: 0 })
const lastSyncResult = ref(null) // { success: boolean, timestamp: number }

let pollInterval = null
let isInitialized = false

// ---- Category Mapping ----
const CATEGORY_MAP = {
  '/readings': { key: 'readings', icon: 'opacity' },
  '/growth': { key: 'growth', icon: 'show_chart' },
  '/medications': { key: 'medications', icon: 'vaccines' },
  '/batches': { key: 'batches', icon: 'layers' },
  '/farms': { key: 'farms', icon: 'agriculture' },
  '/alerts': { key: 'alerts', icon: 'notification_important' }
}

function resolveCategory(url) {
  for (const [prefix, meta] of Object.entries(CATEGORY_MAP)) {
    if (url.startsWith(prefix)) return meta
  }
  return { key: 'other', icon: 'pending_actions' }
}

// ---- Composable ----
export function useSyncManager() {

  // -- Queue Refresh --
  const refreshQueue = async () => {
    try {
      const items = await getSyncQueue()
      queueItems.value = items
    } catch (e) {
      console.error('[SyncManager] Failed to refresh queue:', e)
    }
  }

  // -- Grouped Items --
  const groupedByType = computed(() => {
    const groups = {}
    for (const item of queueItems.value) {
      const cat = resolveCategory(item.url)
      if (!groups[cat.key]) {
        groups[cat.key] = { key: cat.key, icon: cat.icon, items: [] }
      }
      groups[cat.key].items.push(item)
    }
    // Sort groups alphabetically by key for consistent ordering
    return Object.values(groups).sort((a, b) => a.key.localeCompare(b.key))
  })

  const queueLength = computed(() => queueItems.value.length)

  // -- Drawer Controls --
  const openDrawer = () => { isDrawerOpen.value = true }
  const closeDrawer = () => { isDrawerOpen.value = false }
  const toggleDrawer = () => { isDrawerOpen.value = !isDrawerOpen.value }

  // -- Sync All --
  const syncAll = async () => {
    if (isSyncing.value || !navigator.onLine) return false

    isSyncing.value = true
    await refreshQueue()
    const queue = [...queueItems.value]
    syncProgress.value = { current: 0, total: queue.length }

    if (queue.length === 0) {
      isSyncing.value = false
      return true
    }

    let allSuccess = true
    const apiBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

    const BATCH_SIZE = 5
    for (let i = 0; i < queue.length; i += BATCH_SIZE) {
      const batch = queue.slice(i, i + BATCH_SIZE)
      
      const results = await Promise.allSettled(batch.map(async (item) => {
        const response = await fetch(`${apiBase}${item.url}`, {
          method: item.method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('agrisense_token')}`
          },
          body: item.payload ? JSON.stringify(item.payload) : undefined
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        await removeFromSyncQueue(item.id)
        syncProgress.value.current++
        return item.id
      }))

      const hasErrors = results.some(r => r.status === 'rejected')
      if (hasErrors) {
        results.forEach((r, idx) => {
          if (r.status === 'rejected') {
            console.error(`[SyncManager] Failed to sync item ${batch[idx].id}:`, r.reason)
          } else {
            console.log(`[SyncManager] Synced item ${batch[idx].id}`)
          }
        })
        allSuccess = false
        // Stop on first batch error to preserve rough ordering
        break
      } else {
        batch.forEach(item => console.log(`[SyncManager] Synced item ${item.id}`))
      }
      await refreshQueue()
    }

    lastSyncResult.value = {
      success: allSuccess,
      timestamp: Date.now()
    }

    isSyncing.value = false
    syncProgress.value = { current: 0, total: 0 }
    await refreshQueue()
    return allSuccess
  }

  // -- Sync Single Item --
  const syncOne = async (id) => {
    if (isSyncing.value || !navigator.onLine) return false

    const item = queueItems.value.find(i => i.id === id)
    if (!item) return false

    isSyncing.value = true
    syncProgress.value = { current: 0, total: 1 }
    const apiBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

    try {
      const response = await fetch(`${apiBase}${item.url}`, {
        method: item.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('agrisense_token')}`
        },
        body: item.payload ? JSON.stringify(item.payload) : undefined
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      await removeFromSyncQueue(item.id)
      syncProgress.value.current = 1
      lastSyncResult.value = { success: true, timestamp: Date.now() }
    } catch (err) {
      console.error(`[SyncManager] Failed to sync item ${id}:`, err)
      lastSyncResult.value = { success: false, timestamp: Date.now() }
    }

    isSyncing.value = false
    syncProgress.value = { current: 0, total: 0 }
    await refreshQueue()
  }

  // -- Remove Single Item --
  const removeOne = async (id) => {
    try {
      await removeFromSyncQueue(id)
      await refreshQueue()
    } catch (e) {
      console.error('[SyncManager] Failed to remove item:', e)
    }
  }

  // -- Remove All Items --
  const removeAll = async () => {
    try {
      for (const item of queueItems.value) {
        await removeFromSyncQueue(item.id)
      }
      await refreshQueue()
    } catch (e) {
      console.error('[SyncManager] Failed to clear queue:', e)
    }
  }

  // -- Online / Offline Handlers --
  const handleOnline = () => {
    isOffline.value = false
  }

  const handleOffline = () => {
    isOffline.value = true
  }

  // -- Initialize (called once from App.vue) --
  const initialize = () => {
    if (isInitialized) return

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    refreshQueue()
    pollInterval = setInterval(refreshQueue, 3000)
    isInitialized = true
  }

  // -- Cleanup --
  const destroy = () => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
    isInitialized = false
  }

  return {
    // State
    queueItems,
    queueLength,
    isSyncing,
    isOffline,
    isDrawerOpen,
    syncProgress,
    lastSyncResult,
    groupedByType,

    // Actions
    openDrawer,
    closeDrawer,
    toggleDrawer,
    refreshQueue,
    syncAll,
    syncOne,
    removeOne,
    removeAll,
    initialize,
    destroy
  }
}
