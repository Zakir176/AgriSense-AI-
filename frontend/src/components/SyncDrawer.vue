<template>
  <!-- Backdrop Overlay -->
  <Teleport to="body">
    <Transition name="drawer-backdrop">
      <div
        v-if="isDrawerOpen"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[60] cursor-pointer"
        @click="closeDrawer"
      ></div>
    </Transition>

    <!-- Drawer Panel -->
    <Transition name="drawer-slide">
      <aside
        v-if="isDrawerOpen"
        id="sync-drawer"
        class="fixed inset-y-0 right-0 z-[70] flex flex-col w-full sm:w-96 overflow-hidden"
      >
        <!-- Glowing Left Edge -->
        <div class="absolute left-0 inset-y-0 w-[2px] bg-gradient-to-b from-primary-400 via-accent-500 to-primary-400 opacity-70 z-10"></div>

        <!-- Glassmorphic Body -->
        <div class="flex flex-col h-full bg-white/85 dark:bg-[#181e1b]/92 backdrop-blur-xl border-l border-gray-200/60 dark:border-gray-800/60 shadow-2xl">

          <!-- ===== HEADER ===== -->
          <div class="relative px-6 py-5 border-b border-gray-200 dark:border-gray-800">
            <!-- Pulsing glow behind header when items pending -->
            <div
              v-if="queueLength > 0 && !isSyncing"
              class="absolute inset-0 bg-gradient-to-r from-primary-500/5 via-primary-400/8 to-accent-500/5 dark:from-primary-500/10 dark:via-primary-400/12 dark:to-accent-500/8 animate-pulse rounded-none pointer-events-none"
            ></div>

            <div class="relative flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950/50 border border-primary-200/50 dark:border-primary-800/50">
                  <span class="material-icons-outlined text-xl text-primary-600 dark:text-primary-400" :class="{ 'animate-spin': isSyncing }">sync</span>
                </div>
                <div>
                  <h2 class="text-base font-extrabold text-gray-900 dark:text-white tracking-tight">{{ $t('sync.title') }}</h2>
                  <div class="flex items-center space-x-1.5 mt-0.5">
                    <!-- Connection Status Dot -->
                    <span class="relative flex h-2 w-2">
                      <span
                        class="absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping"
                        :class="isOffline ? 'bg-amber-400' : 'bg-emerald-400'"
                      ></span>
                      <span
                        class="relative inline-flex h-2 w-2 rounded-full"
                        :class="isOffline ? 'bg-amber-500' : 'bg-emerald-500'"
                      ></span>
                    </span>
                    <span class="text-[11px] font-bold" :class="isOffline ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'">
                      {{ isOffline ? $t('sync.no_connection') : $t('sync.connected') }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Close Button -->
              <button
                @click="closeDrawer"
                class="p-2 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition text-gray-500 dark:text-gray-400 focus:outline-none cursor-pointer"
                :aria-label="$t('sync.close') || 'Close'"
              >
                <span class="material-icons-outlined text-lg block">close</span>
              </button>
            </div>
          </div>

          <!-- ===== STATUS BAR ===== -->
          <div class="px-6 py-3 bg-gray-50/70 dark:bg-[#1a211d]/60 border-b border-gray-150 dark:border-gray-800 space-y-2">
            <!-- Pending Count -->
            <div class="flex items-center justify-between">
              <span class="text-sm font-bold text-gray-800 dark:text-gray-200">
                <span class="inline-flex items-center justify-center min-w-[1.5rem] h-6 px-1.5 rounded-lg text-xs font-black mr-1.5 transition-all duration-300"
                  :class="queueLength > 0
                    ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300 sync-count-bounce'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'"
                >{{ queueLength }}</span>
                {{ queueLength === 1 ? $t('sync.pending_item') : $t('sync.pending_items') }}
              </span>
            </div>

            <!-- Last Sync Result -->
            <div class="text-[11px] font-medium" :class="!lastSyncResult ? 'text-gray-400 dark:text-gray-600' : (lastSyncResult.success ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400')">
              <span v-if="!lastSyncResult">{{ $t('sync.never_synced') }}</span>
              <span v-else-if="lastSyncResult.success">
                {{ $t('sync.last_synced', { time: relativeTime(lastSyncResult.timestamp) }) }} ✓
              </span>
              <span v-else>
                {{ $t('sync.last_sync_failed', { time: relativeTime(lastSyncResult.timestamp) }) }} ✗
              </span>
            </div>

            <!-- Progress Bar (visible during sync) -->
            <div v-if="isSyncing && syncProgress.total > 0" class="pt-1">
              <AgriProgressBar
                :value="syncProgress.current"
                :max="syncProgress.total"
                :animated="true"
                :showValue="false"
                heightClass="h-1.5"
                colorClass="bg-gradient-to-r from-primary-500 to-accent-500"
              />
              <p class="text-[10px] font-bold text-primary-600 dark:text-primary-400 mt-1">
                {{ $t('sync.syncing_progress', { current: syncProgress.current, total: syncProgress.total }) }}
              </p>
            </div>
          </div>

          <!-- ===== QUEUE LIST ===== -->
          <div class="flex-1 overflow-y-auto">
            <!-- Empty State -->
            <div v-if="queueLength === 0" class="flex flex-col items-center justify-center h-full px-6 py-12 text-center">
              <div class="w-16 h-16 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200/50 dark:border-emerald-800/30 flex items-center justify-center mb-4">
                <span class="material-icons-outlined text-3xl text-emerald-500 dark:text-emerald-400">cloud_done</span>
              </div>
              <p class="text-sm font-bold text-gray-800 dark:text-gray-200">{{ $t('sync.no_pending') }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ $t('sync.no_pending_desc') }}</p>
            </div>

            <!-- Grouped Queue Items -->
            <div v-else class="divide-y divide-gray-100 dark:divide-gray-800/60">
              <TransitionGroup name="sync-group" tag="div">
                <div v-for="group in groupedByType" :key="group.key" class="py-1">
                  <!-- Group Header -->
                  <div class="flex items-center space-x-2 px-6 py-2.5 bg-gray-50/50 dark:bg-[#1a211d]/40 sticky top-0 z-[1]">
                    <span class="material-icons-outlined text-sm text-gray-400 dark:text-gray-500">{{ group.icon }}</span>
                    <span class="text-[11px] font-extrabold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                      {{ $t('sync.category_' + group.key) }}
                    </span>
                    <span class="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded-md text-[10px] font-black bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                      {{ group.items.length }}
                    </span>
                  </div>

                  <!-- Individual Items -->
                  <TransitionGroup name="sync-item" tag="div">
                    <div
                      v-for="item in group.items"
                      :key="item.id"
                      class="flex items-start space-x-3 px-6 py-3 hover:bg-gray-50/80 dark:hover:bg-gray-800/20 transition-colors duration-150 group"
                    >
                      <!-- Method Badge -->
                      <span
                        class="shrink-0 inline-flex items-center justify-center h-6 px-1.5 rounded-md text-[10px] font-black uppercase mt-0.5"
                        :class="methodBadgeClass(item.method)"
                      >{{ item.method }}</span>

                      <!-- Item Details -->
                      <div class="flex-1 min-w-0">
                        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 truncate">
                          {{ item.url }}
                        </p>
                        <p v-if="item.payload" class="text-[11px] text-gray-500 dark:text-gray-500 truncate mt-0.5 font-mono">
                          {{ payloadPreview(item.payload) }}
                        </p>
                        <p class="text-[10px] text-gray-400 dark:text-gray-600 mt-1 font-medium">
                          {{ $t('sync.item_queued', { time: relativeTime(item.timestamp) }) }}
                        </p>
                      </div>

                      <!-- Remove Button -->
                      <button
                        @click="handleRemoveItem(item.id)"
                        class="shrink-0 p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 opacity-0 group-hover:opacity-100 transition-all duration-200 focus:outline-none cursor-pointer"
                        :title="$t('sync.remove_item')"
                      >
                        <span class="material-icons-outlined text-sm">delete_outline</span>
                      </button>
                    </div>
                  </TransitionGroup>
                </div>
              </TransitionGroup>
            </div>
          </div>

          <!-- ===== FOOTER ACTIONS ===== -->
          <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-[#181e1b]/70 space-y-2.5">
            <!-- Force Sync Button -->
            <AgriButton
              variant="primary"
              size="md"
              icon="cloud_upload"
              :loading="isSyncing"
              :disabled="isOffline || queueLength === 0"
              class="w-full"
              @click="handleForceSync"
            >
              <span v-if="isSyncing">{{ $t('sync.syncing_progress', { current: syncProgress.current, total: syncProgress.total }) }}</span>
              <span v-else>{{ $t('sync.force_sync') }}</span>
            </AgriButton>

            <!-- Clear All -->
            <button
              v-if="queueLength > 0 && !isSyncing"
              @click="showClearConfirm = true"
              class="w-full flex items-center justify-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/20 border border-transparent hover:border-red-200/30 dark:hover:border-red-900/30 transition cursor-pointer"
            >
              <span class="material-icons-outlined text-sm">delete_sweep</span>
              <span>{{ $t('sync.clear_all') }}</span>
            </button>
          </div>
        </div>
      </aside>
    </Transition>

    <!-- Clear All Confirmation Modal -->
    <Transition name="fade">
      <div v-if="showClearConfirm" class="fixed inset-0 z-[80] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showClearConfirm = false"></div>
        <div class="relative bg-white dark:bg-[#1e2522] rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 max-w-sm w-full p-6 space-y-4">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200/50 dark:border-red-800/30 flex items-center justify-center">
              <span class="material-icons-outlined text-xl text-red-500">warning</span>
            </div>
            <div>
              <h3 class="text-sm font-extrabold text-gray-900 dark:text-white">{{ $t('sync.clear_all') }}</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ $t('sync.clear_all_confirm') }}</p>
            </div>
          </div>
          <div class="flex space-x-3">
            <AgriButton variant="outline" size="sm" class="flex-1" @click="showClearConfirm = false">
              {{ $t('sync.clear_all_no') }}
            </AgriButton>
            <AgriButton variant="destructive" size="sm" class="flex-1" @click="handleClearAll">
              {{ $t('sync.clear_all_yes') }}
            </AgriButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useSyncManager } from '../composables/useSyncManager'
import { useToast } from '../composables/useToast'
import AgriButton from './ui/AgriButton.vue'
import AgriProgressBar from './ui/AgriProgressBar.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const toast = useToast()

const {
  queueItems,
  queueLength,
  isSyncing,
  isOffline,
  isDrawerOpen,
  syncProgress,
  lastSyncResult,
  groupedByType,
  closeDrawer,
  syncAll,
  removeOne,
  removeAll,
  refreshQueue
} = useSyncManager()

const showClearConfirm = ref(false)

// ---- Actions ----
const handleForceSync = async () => {
  const success = await syncAll()
  if (success) {
    toast.success(t('sync.sync_success') || 'All data synced successfully!')
  } else {
    toast.error(t('sync.sync_error') || 'Some items failed to sync. Will retry.')
  }
}

const handleClearAll = async () => {
  await removeAll()
  showClearConfirm.value = false
  toast.info(t('sync.cleared') || 'Pending queue cleared.')
}

const handleRemoveItem = async (id) => {
  await removeOne(id)
}

// ---- Helpers ----
const methodBadgeClass = (method) => {
  switch (method) {
    case 'POST': return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'
    case 'PUT': return 'bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400'
    case 'DELETE': return 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400'
    default: return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  }
}

const payloadPreview = (payload) => {
  if (!payload || typeof payload !== 'object') return ''
  const entries = Object.entries(payload).slice(0, 3)
  return entries.map(([k, v]) => `${k}: ${v}`).join(', ')
}

const relativeTime = (timestamp) => {
  if (!timestamp) return ''
  const diff = Date.now() - timestamp
  const seconds = Math.floor(diff / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

// -- Removed: lastSyncClass is now computed inline in template --
</script>

<style scoped>
/* Drawer slide animation */
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(100%);
}

/* Backdrop fade */
.drawer-backdrop-enter-active,
.drawer-backdrop-leave-active {
  transition: opacity 250ms ease;
}
.drawer-backdrop-enter-from,
.drawer-backdrop-leave-to {
  opacity: 0;
}

/* Generic fade for confirmation modal */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Group-level animations */
.sync-group-enter-active,
.sync-group-leave-active {
  transition: all 300ms ease;
}
.sync-group-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.sync-group-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Item-level animations */
.sync-item-enter-active {
  transition: all 250ms ease-out;
}
.sync-item-leave-active {
  transition: all 200ms ease-in;
}
.sync-item-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
.sync-item-leave-to {
  opacity: 0;
  transform: scale(0.95);
  max-height: 0;
}

/* Bounce animation for the count badge */
@keyframes syncCountBounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}
.sync-count-bounce {
  animation: syncCountBounce 600ms ease-in-out;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .drawer-slide-enter-active,
  .drawer-slide-leave-active,
  .drawer-backdrop-enter-active,
  .drawer-backdrop-leave-active,
  .sync-group-enter-active,
  .sync-group-leave-active,
  .sync-item-enter-active,
  .sync-item-leave-active {
    transition-duration: 0ms !important;
  }
  .sync-count-bounce {
    animation: none;
  }
}
</style>
