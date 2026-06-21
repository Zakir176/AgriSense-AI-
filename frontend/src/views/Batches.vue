<template>
  <div class="space-y-6">
    <!-- Header Block -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Batches</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Register new cohorts, monitor active flocks, and view historical operations.</p>
      </div>
      <button 
        @click="showCreateModal = true"
        class="bg-primary-600 hover:bg-primary-500 text-white font-semibold px-4 py-2.5 rounded-xl shadow-sm hover:shadow transition flex items-center space-x-2"
        id="btn-register-batch"
      >
        <span class="material-icons-outlined text-lg">add</span>
        <span>Register Batch</span>
      </button>
    </div>

    <!-- Active Batches Grid -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-sm transition-colors duration-200">
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">Active Cohorts</h2>
        <span class="bg-primary-50 text-primary-700 dark:bg-primary-950/40 dark:text-primary-400 text-xs font-semibold px-2.5 py-1 rounded-full border border-primary-100 dark:border-primary-900/40">
          {{ activeBatches.length }} Running
        </span>
      </div>

      <div v-if="isLoading" class="p-12 text-center text-gray-450 dark:text-gray-500">
        <span class="material-icons-outlined text-3xl animate-spin block mb-2">sync</span>
        <span>Retrieving cohorts...</span>
      </div>

      <div v-else-if="activeBatches.length === 0" class="text-center py-16 text-gray-450 dark:text-gray-500">
        <span class="material-icons-outlined text-4xl block mb-2 text-gray-300 dark:text-gray-700">layers</span>
        <p class="text-base font-medium">No active cohorts registered</p>
        <p class="text-sm mt-1">Register a new batch of birds to start logging feed, water, and growth.</p>
      </div>

      <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
        <div v-for="batch in activeBatches" :key="batch.id" class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/10 transition">
          <div class="space-y-2">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-bold text-gray-950 dark:text-white">
                {{ batch.breed }}
              </h3>
              <span class="bg-green-50 text-green-700 dark:bg-green-950/30 dark:text-green-400 text-xs font-medium px-2 py-0.5 rounded border border-green-150 dark:border-green-900/30">
                Active
              </span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm text-gray-500 dark:text-gray-450">
              <div class="flex items-center space-x-1.5">
                <span class="material-icons-outlined text-base">people</span>
                <span>Flock: <strong class="text-gray-850 dark:text-gray-200">{{ batch.bird_count.toLocaleString() }} birds</strong></span>
              </div>
              <div class="flex items-center space-x-1.5">
                <span class="material-icons-outlined text-base">date_range</span>
                <span>Started: <strong class="text-gray-850 dark:text-gray-200">{{ formatDate(batch.start_date) }}</strong></span>
              </div>
              <div class="flex items-center space-x-1.5 col-span-2 sm:col-span-1">
                <span class="material-icons-outlined text-base">cake</span>
                <span>Age: <strong class="text-gray-850 dark:text-gray-200">{{ calculateDays(batch.start_date) }} days</strong></span>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button 
              @click="selectActiveBatch(batch)"
              class="flex-1 md:flex-initial px-4 py-2 border border-gray-200 dark:border-gray-850 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-semibold rounded-xl text-gray-700 dark:text-gray-250 transition"
              :class="{ 'ring-2 ring-primary-500 border-primary-500': store.activeBatch?.id === batch.id }"
            >
              {{ store.activeBatch?.id === batch.id ? 'Active Focus' : 'Focus Batch' }}
            </button>
            <button 
              @click="archiveBatch(batch.id)"
              class="flex-1 md:flex-initial px-4 py-2 border border-transparent hover:border-gray-250 dark:hover:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-semibold rounded-xl text-red-650 dark:text-red-400 transition flex items-center justify-center space-x-1"
            >
              <span class="material-icons-outlined text-sm">archive</span>
              <span>Archive</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Historical / Archived Batches Table -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden shadow-sm transition-colors duration-200">
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">Archived / Historical</h2>
        <span class="bg-gray-100 text-gray-600 dark:bg-gray-800/40 dark:text-gray-400 text-xs font-semibold px-2.5 py-1 rounded-full border border-gray-200 dark:border-gray-800">
          {{ archivedBatches.length }} Total
        </span>
      </div>

      <div v-if="archivedBatches.length === 0" class="text-center py-12 text-gray-450 dark:text-gray-500">
        No archived cohorts. Active cohorts will appear here once closed.
      </div>

      <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
        <div v-for="batch in archivedBatches" :key="batch.id" class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/10 transition">
          <div class="space-y-1">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-bold text-gray-700 dark:text-gray-400 line-through">
                {{ batch.breed }}
              </h3>
              <span class="bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 text-xs font-medium px-2 py-0.5 rounded border border-gray-200 dark:border-gray-800">
                Closed
              </span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm text-gray-500 dark:text-gray-450">
              <div>Flock: {{ batch.bird_count.toLocaleString() }} birds</div>
              <div>Started: {{ formatDate(batch.start_date) }}</div>
              <div class="text-xs text-red-500 hover:text-red-400 cursor-pointer pt-0.5" @click="deleteBatchPermanently(batch.id)">
                Delete Permanently
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Register Batch Dialog Modal (Custom backdrop implementation) -->
    <div 
      v-if="showCreateModal" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 overflow-y-auto"
      @click.self="closeModal"
    >
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 w-full max-w-md rounded-2xl shadow-xl overflow-hidden transform transition-all p-6 space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Register Cohort Batch</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>

        <form @submit.prevent="createBatch" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Breed / Type</label>
            <input 
              v-model="newBatch.breed"
              type="text" 
              required
              placeholder="e.g. Cobb 500 Broilers"
              class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-850 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm transition"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Bird Count</label>
              <input 
                v-model.number="newBatch.bird_count"
                type="number" 
                required
                min="1"
                placeholder="1000"
                class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-850 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm transition"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Start Date</label>
              <input 
                v-model="newBatch.start_date"
                type="date" 
                required
                class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-850 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm transition"
              />
            </div>
          </div>

          <div v-if="errorMsg" class="text-sm text-red-650 dark:text-red-400 bg-red-50 dark:bg-red-950/20 px-3 py-2 rounded-lg border border-red-200 dark:border-red-900/30">
            {{ errorMsg }}
          </div>

          <div class="flex space-x-3 pt-4 border-t border-gray-150 dark:border-gray-800">
            <button 
              type="button" 
              @click="closeModal" 
              class="flex-1 py-2.5 border border-gray-200 dark:border-gray-850 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-bold rounded-xl text-gray-750 dark:text-gray-250 transition"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="isSubmitting"
              class="flex-1 py-2.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow transition"
            >
              {{ isSubmitting ? 'Registering...' : 'Register' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../services/api'
import { store } from '../services/store'

const isLoading = ref(false)
const showCreateModal = ref(false)
const isSubmitting = ref(false)
const errorMsg = ref('')

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
  } catch (error) {
    console.error('Failed to load cohorts:', error)
  } finally {
    isLoading.value = false
  }
}

const selectActiveBatch = (batch) => {
  store.activeBatch = batch
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

const createBatch = async () => {
  if (!store.currentFarm) return
  isSubmitting.value = true
  errorMsg.value = ''
  try {
    const payload = {
      farm_id: store.currentFarm.id,
      breed: newBatch.value.breed,
      bird_count: newBatch.value.bird_count,
      start_date: newBatch.value.start_date,
      status: 'active'
    }
    await api.batches.create(payload)
    await loadBatches()
    
    // Auto-focus the newly created batch
    const active = activeBatches.value
    if (active.length > 0) {
      // Find the one we just made (usually max id)
      const maxIdBatch = active.reduce((prev, curr) => (prev.id > curr.id) ? prev : curr)
      store.activeBatch = maxIdBatch
    }
    
    closeModal()
  } catch (error) {
    errorMsg.value = error.message || 'Registration failed.'
  } finally {
    isSubmitting.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
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
  // Reset hours to get correct day difference
  start.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)
  const diffTime = Math.abs(today - start)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

onMounted(() => {
  loadBatches()
})
</script>
