<template>
  <div class="space-y-6">
    <!-- Header Block -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ $t('batches.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">{{ $t('batches.subtitle') }}</p>
      </div>
      <AgriButton 
        id="btn-register-batch"
        variant="primary"
        icon="add"
        @click="showCreateModal = true"
      >{{ $t('batches.register_batch') }}</AgriButton>
    </div>

    <!-- Active Batches Grid -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-sm transition-colors duration-200 animate-fade-in-up delay-100">
      <div class="px-6 py-4 border-b border-gray-150 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('batches.active_cohorts') }}</h2>
        <AgriBadge variant="active" pulse>
          {{ activeBatches.length }} {{ $t('batches.running') }}
        </AgriBadge>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="p-12 text-center text-gray-450 dark:text-gray-500">
        <span class="material-icons-outlined text-3xl animate-spin block mb-2 text-primary-500">sync</span>
        <span class="font-semibold text-sm">{{ $t('batches.retrieving') }}</span>
      </div>

      <!-- Empty State -->
      <div v-else-if="activeBatches.length === 0" class="text-center py-16 text-gray-450 dark:text-gray-500 px-6">
        <span class="material-icons-outlined text-4xl block mb-2 text-gray-300 dark:text-gray-700">layers</span>
        <p class="text-base font-bold text-gray-700 dark:text-gray-300">{{ $t('batches.no_active') }}</p>
        <p class="text-xs mt-1">{{ $t('batches.register_new_desc') }}</p>
      </div>

      <!-- Batch Cards List -->
      <div v-else class="divide-y divide-gray-150 dark:divide-gray-800/80">
        <div 
          v-for="(batch, index) in activeBatches" 
          :key="batch.id" 
          class="hover:bg-gray-50/50 dark:hover:bg-darkbg-100/10 transition duration-150 flex flex-col animate-fade-in-up"
          :class="getStaggerDelayClass(index)"
        >
          <!-- Primary Summary Row -->
          <div class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div class="space-y-2 flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <h3 class="text-base font-bold text-gray-950 dark:text-white truncate">
                  {{ batch.breed }}
                </h3>
                <AgriBadge variant="active" pulse>{{ $t('batches.active') }}</AgriBadge>
                <AgriBadge v-if="store.activeBatch?.id === batch.id" variant="success" icon="center_focus_strong">
                  Focus
                </AgriBadge>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm text-gray-500 dark:text-gray-450">
                <div class="flex items-center space-x-1.5 font-medium">
                  <span class="material-icons-outlined text-base text-gray-400">people</span>
                  <span>{{ $t('batches.flock') }} <strong class="text-gray-800 dark:text-gray-250 font-bold">{{ batch.bird_count.toLocaleString() }} {{ $t('batches.birds') }}</strong></span>
                </div>
                <div class="flex items-center space-x-1.5 font-medium">
                  <span class="material-icons-outlined text-base text-gray-400">date_range</span>
                  <span>{{ $t('batches.started') }} <strong class="text-gray-800 dark:text-gray-250 font-bold">{{ formatDate(batch.start_date) }}</strong></span>
                </div>
                <div class="flex items-center space-x-1.5 font-medium col-span-2 sm:col-span-1">
                  <span class="material-icons-outlined text-base text-gray-400">cake</span>
                  <span>{{ $t('batches.age') }} <strong class="text-gray-800 dark:text-gray-250 font-bold">{{ calculateDays(batch.start_date) }} {{ $t('batches.days') }}</strong></span>
                </div>
              </div>
            </div>

            <!-- Actions Row -->
            <div class="flex flex-wrap items-center gap-2 mt-4 md:mt-0">
              <!-- Expand Detail Button -->
              <AgriButton
                variant="outline"
                size="sm"
                :icon="expandedBatchId === batch.id ? 'expand_less' : 'expand_more'"
                @click="toggleExpand(batch.id)"
              >{{ $t('batches.details') }}</AgriButton>
              <AgriButton 
                variant="outline"
                size="sm"
                icon="edit"
                @click="openEditModal(batch)"
              >{{ $t('batches.edit') }}</AgriButton>
              <AgriButton 
                :variant="store.activeBatch?.id === batch.id ? 'primary' : 'outline'"
                size="sm"
                icon="center_focus_strong"
                @click="selectActiveBatch(batch)"
              >
                {{ store.activeBatch?.id === batch.id ? $t('batches.active_focus') : $t('batches.focus') }}
              </AgriButton>
              <AgriButton 
                variant="ghost"
                size="sm"
                icon="archive"
                class="text-red-500 hover:text-red-650 hover:bg-red-50 dark:hover:bg-red-950/20"
                @click="archiveBatch(batch.id)"
              >{{ $t('batches.archive') }}</AgriButton>
            </div>
          </div>

          <!-- Collapsible Details Area -->
          <Transition name="slide-height">
            <div 
              v-show="expandedBatchId === batch.id" 
              class="border-t border-gray-150 dark:border-gray-800/80 bg-gray-50/50 dark:bg-darkbg-100/30 px-6 py-4 overflow-hidden transition-all duration-200"
            >
              <div class="flex items-center justify-between mb-3">
                <p class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Flock Inventory & Audit Ledger</p>
                <AgriButton
                  variant="outline"
                  size="sm"
                  icon="edit_note"
                  @click="openInventoryModal(batch)"
                >Adjust Inventory</AgriButton>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs font-semibold text-gray-600 dark:text-gray-450">
                <div class="bg-white dark:bg-darkbg-50 p-3 rounded-xl border border-gray-200/60 dark:border-gray-800">
                  <p class="text-gray-400 dark:text-gray-500 uppercase text-[10px] tracking-wide mb-1">Live Flock Count</p>
                  <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                    {{ inventorySummaries[batch.id]?.current_live_count ?? batch.bird_count }} head
                  </p>
                </div>
                <div class="bg-white dark:bg-darkbg-50 p-3 rounded-xl border border-gray-200/60 dark:border-gray-800">
                  <p class="text-gray-400 dark:text-gray-500 uppercase text-[10px] tracking-wide mb-1">Total Mortality</p>
                  <p class="text-sm font-bold text-red-500">
                    {{ inventorySummaries[batch.id]?.total_mortality ?? 0 }} birds
                  </p>
                </div>
                <div class="bg-white dark:bg-darkbg-50 p-3 rounded-xl border border-gray-200/60 dark:border-gray-800">
                  <p class="text-gray-400 dark:text-gray-500 uppercase text-[10px] tracking-wide mb-1">Total Sales / Harvested</p>
                  <p class="text-sm font-bold text-blue-500">
                    {{ inventorySummaries[batch.id]?.total_sales ?? 0 }} birds
                  </p>
                </div>
                <div class="bg-white dark:bg-darkbg-50 p-3 rounded-xl border border-gray-200/60 dark:border-gray-800">
                  <p class="text-gray-400 dark:text-gray-500 uppercase text-[10px] tracking-wide mb-1">Culls / Corrections</p>
                  <p class="text-sm font-bold text-gray-800 dark:text-gray-200">
                    {{ (inventorySummaries[batch.id]?.total_culls || 0) + (inventorySummaries[batch.id]?.total_corrections || 0) }} birds
                  </p>
                </div>
              </div>

              <!-- Inventory Ledger History Stream -->
              <div v-if="inventorySummaries[batch.id]?.history?.length" class="mt-3 pt-3 border-t border-gray-200/60 dark:border-gray-800">
                <p class="text-[11px] font-bold text-gray-500 dark:text-gray-400 mb-2">Recent Inventory Adjustments</p>
                <div class="space-y-1.5 max-h-40 overflow-y-auto">
                  <div
                    v-for="adj in inventorySummaries[batch.id].history.slice(0, 5)"
                    :key="adj.id"
                    class="flex items-center justify-between text-[11px] bg-white dark:bg-darkbg-50 p-2 rounded-lg border border-gray-150 dark:border-gray-800"
                  >
                    <div class="flex items-center gap-2">
                      <span class="px-1.5 py-0.5 rounded font-bold uppercase text-[9px]"
                        :class="adj.quantity_delta < 0 ? 'bg-red-50 text-red-600 dark:bg-red-950/40 dark:text-red-400' : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400'">
                        {{ adj.adjustment_type }}
                      </span>
                      <span class="text-gray-700 dark:text-gray-300 font-medium">{{ adj.notes || 'No description' }}</span>
                    </div>
                    <div class="flex items-center gap-3">
                      <span class="font-mono font-bold" :class="adj.quantity_delta < 0 ? 'text-red-500' : 'text-emerald-500'">
                        {{ adj.quantity_delta > 0 ? '+' : '' }}{{ adj.quantity_delta }}
                      </span>
                      <span class="text-gray-400 text-[10px]">{{ adj.date }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Historical / Archived Batches Table -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-sm transition-colors duration-200 animate-fade-in-up delay-200">
      <div class="px-6 py-4 border-b border-gray-150 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('batches.archived_historical') }}</h2>
        <AgriBadge variant="info">
          {{ archivedBatches.length }} {{ $t('batches.total') }}
        </AgriBadge>
      </div>

      <div v-if="archivedBatches.length === 0" class="text-center py-12 text-gray-450 dark:text-gray-500 font-semibold text-xs px-6">
        {{ $t('batches.no_archived') }}
      </div>

      <div v-else class="divide-y divide-gray-150 dark:divide-gray-800">
        <div v-for="batch in archivedBatches" :key="batch.id" class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-gray-50/50 dark:hover:bg-darkbg-100/15 transition animate-fade-in-up">
          <div class="space-y-1">
            <div class="flex items-center space-x-3">
              <h3 class="text-base font-bold text-gray-500 dark:text-gray-400 line-through">
                {{ batch.breed }}
              </h3>
              <AgriBadge variant="info">{{ $t('batches.closed') }}</AgriBadge>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm text-gray-500 dark:text-gray-450">
              <div>{{ $t('batches.flock') }} <strong class="text-gray-700 dark:text-gray-300">{{ batch.bird_count.toLocaleString() }} {{ $t('batches.birds') }}</strong></div>
              <div>{{ $t('batches.started') }} <strong class="text-gray-700 dark:text-gray-300">{{ formatDate(batch.start_date) }}</strong></div>
              <div 
                class="text-xs text-status-danger hover:text-red-500 hover:underline cursor-pointer pt-0.5 font-bold flex items-center gap-1" 
                @click="deleteBatchPermanently(batch.id)"
              >
                <span class="material-icons-outlined text-xs">delete</span>
                <span>{{ $t('batches.delete_perm') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Register Batch Dialog Modal (Integrated AgriModal) -->
    <AgriModal
      :show="showCreateModal"
      :title="editingBatchId ? $t('batches.edit_cohort') : $t('batches.register_cohort')"
      @close="closeModal"
    >
      <form @submit.prevent="submitBatch" class="space-y-4">
        <AgriInput
          v-model="newBatch.breed"
          :label="$t('batches.breed_type')"
          required
          :placeholder="$t('batches.breed_placeholder')"
          icon="layers"
        />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AgriInput
            v-model.number="newBatch.bird_count"
            type="number"
            :label="$t('batches.initial_bird_count')"
            required
            min="1"
            :placeholder="$t('batches.initial_count_placeholder')"
            icon="people"
          />
          <AgriInput
            v-model="newBatch.start_date"
            type="date"
            :label="$t('batches.start_date')"
            required
            icon="calendar_today"
          />
        </div>

        <div v-if="errorMsg" class="text-xs font-semibold text-status-danger bg-red-50 dark:bg-red-950/20 px-3.5 py-2.5 rounded-xl border border-red-200 dark:border-red-900/30">
          {{ errorMsg }}
        </div>

        <div class="flex space-x-3 pt-4 border-t border-gray-150 dark:border-gray-800">
          <AgriButton 
            type="button" 
            variant="outline"
            class="flex-1"
            @click="closeModal" 
          >{{ $t('batches.cancel') }}</AgriButton>
          <AgriButton 
            type="submit" 
            variant="primary"
            class="flex-1"
            :loading="isSubmitting"
          >
            {{ editingBatchId ? $t('batches.save_changes') : $t('batches.register') }}
          </AgriButton>
        </div>
      </form>
    </AgriModal>

    <!-- Flock Inventory Adjustment Modal -->
    <FlockInventoryModal
      :show="showInventoryModal"
      :batch-id="selectedInventoryBatch?.id"
      @close="showInventoryModal = false"
      @success="handleInventorySubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../services/api'
import { store } from '../services/store'
import { useAnimations } from '../composables/useAnimations'
import { useToast } from '../composables/useToast'

// Reusable Components
import AgriButton from '../components/ui/AgriButton.vue'
import AgriInput from '../components/ui/AgriInput.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriModal from '../components/ui/AgriModal.vue'
import FlockInventoryModal from '../components/FlockInventoryModal.vue'

const { getStaggerDelayClass } = useAnimations()
const toast = useToast()

const isLoading = ref(false)
const showCreateModal = ref(false)
const showInventoryModal = ref(false)
const selectedInventoryBatch = ref(null)
const inventorySummaries = ref({})
const isSubmitting = ref(false)
const errorMsg = ref('')
const editingBatchId = ref(null)
const expandedBatchId = ref(null)

const toggleExpand = async (id) => {
  if (expandedBatchId.value === id) {
    expandedBatchId.value = null
  } else {
    expandedBatchId.value = id
    await fetchInventorySummary(id)
  }
}

const fetchInventorySummary = async (batchId) => {
  try {
    const summary = await api.inventory.getSummary(batchId)
    inventorySummaries.value[batchId] = summary
  } catch (err) {
    console.error('Failed to fetch inventory summary:', err)
  }
}

const openInventoryModal = (batch) => {
  selectedInventoryBatch.value = batch
  showInventoryModal.value = true
}

const handleInventorySubmit = async (payload) => {
  if (!selectedInventoryBatch.value) return
  try {
    await api.inventory.create(selectedInventoryBatch.value.id, payload)
    toast.success('Inventory adjustment logged successfully')
    showInventoryModal.value = false
    await fetchInventorySummary(selectedInventoryBatch.value.id)
  } catch (err) {
    toast.error(err.message || 'Failed to record inventory adjustment')
  }
}

// Initialize form variables
const getTodayString = () => {
  const d = new Date()
  const month = '' + (d.getMonth() + 1)
  const day = '' + d.getDate()
  const year = d.getFullYear()
  return [year, month.padStart(2, '0'), day.padStart(2, '0')].join('-')
}

const newBatch = ref({
  breed: '',
  bird_count: null,
  start_date: getTodayString()
})

const activeBatches = computed(() => {
  return store.batchesList.filter(b => b.status === 'active')
})

const archivedBatches = computed(() => {
  return store.batchesList.filter(b => b.status === 'archived')
})

const loadBatches = async () => {
  if (!store.currentFarm) return
  isLoading.value = true
  try {
    const list = await api.batches.list(store.currentFarm.id)
    store.batchesList = list
    // Pre-fetch summaries for active batches
    for (const b of list) {
      if (b.status === 'active') {
        fetchInventorySummary(b.id)
      }
    }
  } catch (error) {
    console.error('Failed to load cohorts:', error)
  } finally {
    isLoading.value = false
  }
}

const selectActiveBatch = (batch) => {
  store.activeBatch = batch
  localStorage.setItem('agrisense_focused_batch_id', batch.id)
  toast.success(`Globally focused on ${batch.breed} (Batch #${batch.id})`)
}

const archiveBatch = async (batchId) => {
  if (!confirm('Are you sure you want to archive this cohort? This closes daily entries.')) return
  try {
    await api.batches.update(batchId, { status: 'archived' })
    await loadBatches()
    
    // Update active focus if we archived it
    if (store.activeBatch?.id === batchId) {
      const remainingActive = activeBatches.value
      store.activeBatch = remainingActive.length > 0 ? remainingActive[0] : null
    }
  } catch (error) {
    alert('Failed to archive: ' + error.message)
  }
}

const deleteBatchPermanently = async (batchId) => {
  if (!confirm('WARNING: This permanently deletes this cohort and all its logs. Continue?')) return
  try {
    await api.batches.delete(batchId)
    await loadBatches()
    if (store.activeBatch?.id === batchId) {
      store.activeBatch = null
    }
  } catch (error) {
    alert('Deletion failed: ' + error.message)
  }
}

const openEditModal = (batch) => {
  editingBatchId.value = batch.id
  newBatch.value = {
    breed: batch.breed,
    bird_count: batch.bird_count,
    start_date: batch.start_date
  }
  errorMsg.value = ''
  showCreateModal.value = true
}

const submitBatch = async () => {
  if (!store.currentFarm) return
  isSubmitting.value = true
  errorMsg.value = ''
  try {
    if (editingBatchId.value) {
      const payload = {
        breed: newBatch.value.breed,
        bird_count: newBatch.value.bird_count,
        start_date: newBatch.value.start_date
      }
      await api.batches.update(editingBatchId.value, payload)
    } else {
      const payload = {
        farm_id: store.currentFarm.id,
        breed: newBatch.value.breed,
        bird_count: newBatch.value.bird_count,
        start_date: newBatch.value.start_date,
        status: 'active'
      }
      await api.batches.create(payload)
    }
    
    await loadBatches()
    
    // Auto-focus the newly created batch if creating
    if (!editingBatchId.value) {
      const active = activeBatches.value
      if (active.length > 0) {
        const maxIdBatch = active.reduce((prev, curr) => (prev.id > curr.id) ? prev : curr)
        store.activeBatch = maxIdBatch
      }
    } else {
      // update active focus if we edited the active one
      if (store.activeBatch?.id === editingBatchId.value) {
        store.activeBatch = activeBatches.value.find(b => b.id === editingBatchId.value)
      }
    }
    
    closeModal()
  } catch (error) {
    errorMsg.value = error.message || 'Operation failed.'
  } finally {
    isSubmitting.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingBatchId.value = null
  newBatch.value = {
    breed: '',
    bird_count: null,
    start_date: getTodayString()
  }
  errorMsg.value = ''
}

// Utility formatting
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

const calculateDays = (startDateStr) => {
  if (!startDateStr) return 0
  const start = new Date(startDateStr)
  const today = new Date()
  start.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)
  const diffTime = today - start
  return diffTime >= 0 ? Math.ceil(diffTime / (1000 * 60 * 60 * 24)) : 0
}

onMounted(() => {
  loadBatches()
})
</script>

<style scoped>
/* Collapsible transition styling */
.slide-height-enter-active,
.slide-height-leave-active {
  transition: max-height 0.22s ease-in-out, opacity 0.2s ease-in-out, padding 0.22s ease-in-out;
  max-height: 400px;
}
.slide-height-enter-from,
.slide-height-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
</style>
