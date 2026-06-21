<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Growth Monitoring</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Monitor weight gains, standard deviations, and daily growth rates for
          <span v-if="activeBatchObj" class="font-semibold text-gray-700 dark:text-gray-300">Batch #{{ activeBatchObj.id }} · {{ activeBatchObj.breed }}</span>
          <span v-else class="italic">no active batch</span>
        </p>
      </div>
      <div class="flex items-center gap-2">
        <!-- Batch selector -->
        <select
          v-model="selectedBatchId"
          @change="onBatchChange"
          class="text-sm bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl px-3 py-2 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
        >
          <option :value="null" disabled>Select batch…</option>
          <option v-for="b in store.batchesList" :key="b.id" :value="b.id">
            #{{ b.id }} — {{ b.breed }} ({{ b.status }})
          </option>
        </select>
        <button
          @click="showLogModal = true"
          :disabled="!selectedBatchId"
          class="bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-4 py-2 rounded-xl shadow-sm hover:shadow transition flex items-center gap-1.5 text-sm"
        >
          <span class="material-icons-outlined text-[17px]">add</span>
          Record Weight
        </button>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">scale</span>
      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">Select a batch above to view growth analytics.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Growth curves and target deviations are calculated per cohort.</p>
    </div>

    <template v-else>

      <!-- ─── Summary KPIs ─── -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Average Weight</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
            {{ latestSample ? latestSample.avg_weight_g.toFixed(0) + ' g' : '—' }}
          </div>
          <div class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">
            <span v-if="latestSample" :class="getDeviationClass(latestSample.deviation)">
              {{ latestSample.deviation >= 0 ? '+' : '' }}{{ latestSample.deviation.toFixed(1) }}% vs breed target
            </span>
            <span v-else>No samples recorded</span>
          </div>
        </div>

        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Daily Growth Rate</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
            {{ latestSample && latestSample.growthRate > 0 ? latestSample.growthRate.toFixed(1) + ' g/d' : '—' }}
          </div>
          <div class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Target is 50-70 g/day</div>
        </div>

        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Last Sample Size</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
            {{ latestSample ? latestSample.sample_size + ' birds' : '—' }}
          </div>
          <div class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Recommended size >= 20</div>
        </div>

        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Cohort Age</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
            {{ activeCohortAge }} days
          </div>
          <div class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Start date: {{ formatDateShort(activeBatchObj.start_date) }}</div>
        </div>
      </div>

      <!-- ─── Chart ─── -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">stacked_line_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Growth Curve Comparison</h2>
          </div>
          <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-primary-500"></span> <span class="text-gray-400">Actual (g)</span></span>
            <span class="flex items-center gap-1"><span class="h-0.5 w-3 bg-gray-400 dark:bg-gray-600 border-t border-dashed"></span> <span class="text-gray-400">Breed Target (Ross 308)</span></span>
          </div>
        </div>

        <div v-if="chartLoading" class="h-72 flex items-center justify-center">
          <span class="material-icons-outlined text-2xl text-gray-300 dark:text-gray-700 animate-spin">sync</span>
        </div>
        <div v-else-if="samples.length === 0" class="h-72 flex flex-col items-center justify-center text-sm text-gray-400 dark:text-gray-500">
          <span class="material-icons-outlined text-3xl mb-2 text-gray-300 dark:text-gray-700">query_stats</span>
          Record weight samples to view the growth curve.
        </div>
        <div v-else class="p-4">
          <canvas ref="chartCanvas" class="w-full" style="height: 280px;"></canvas>
        </div>
      </div>

      <!-- ─── Weight Logs Table ─── -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">table_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Growth Logs</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ samples.length }} samples</span>
          </div>
        </div>

        <div v-if="tableLoading" class="p-5 space-y-2.5">
          <div v-for="n in 3" :key="n" class="h-10 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="samples.length === 0" class="py-14 text-center">
          <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-2">balance</span>
          <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">No weight records yet</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Click "Record Weight" to input the first average batch sample.</p>
        </div>

        <div v-else>
          <!-- Table header -->
          <div class="grid grid-cols-6 px-5 py-2 text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
            <span>Date</span>
            <span class="text-right">Age (Days)</span>
            <span class="text-right">Sample Size</span>
            <span class="text-right">Avg Weight (g)</span>
            <span class="text-right">Growth Rate</span>
            <span class="text-right">Deviation</span>
          </div>
          <div class="divide-y divide-gray-100 dark:divide-gray-800 max-h-[440px] overflow-y-auto">
            <div
              v-for="(s, idx) in enrichedSamples"
              :key="s.id ?? idx"
              class="grid grid-cols-6 px-5 py-3 text-sm items-center hover:bg-gray-50 dark:hover:bg-darkbg-100 transition"
            >
              <span class="text-gray-700 dark:text-gray-300 font-medium text-xs">{{ formatDate(s.date) }}</span>
              <span class="text-right text-gray-900 dark:text-white tabular-nums font-semibold">{{ s.age }}</span>
              <span class="text-right text-gray-600 dark:text-gray-400 tabular-nums">{{ s.sample_size }} birds</span>
              <span class="text-right text-gray-900 dark:text-white font-bold tabular-nums">{{ s.avg_weight_g.toFixed(0) }}g</span>
              <span class="text-right text-gray-900 dark:text-white tabular-nums font-semibold">
                {{ s.growthRate > 0 ? s.growthRate.toFixed(1) + ' g/d' : '—' }}
              </span>
              <span class="text-right tabular-nums text-xs font-semibold" :class="getDeviationClass(s.deviation)">
                {{ s.deviation >= 0 ? '+' : '' }}{{ s.deviation.toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ Record Weight Modal ═══ -->
    <div
      v-if="showLogModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto"
      @click.self="closeModal"
    >
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 w-full max-w-md rounded-2xl shadow-xl p-6 space-y-5">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Record Sample Weight</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>

        <form @submit.prevent="submitSample" class="space-y-4">
          <!-- Date -->
          <div>
            <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Date</label>
            <input
              v-model="form.date"
              type="date"
              required
              class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <!-- Avg Weight -->
            <div>
              <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Avg Weight (g)</label>
              <input
                v-model.number="form.avg_weight_g"
                type="number"
                step="1"
                min="0"
                required
                placeholder="e.g. 450"
                class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
              />
            </div>
            <!-- Sample Size -->
            <div>
              <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Sample Size</label>
              <input
                v-model.number="form.sample_size"
                type="number"
                step="1"
                min="1"
                required
                placeholder="e.g. 20"
                class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
              />
            </div>
          </div>

          <!-- Error -->
          <div v-if="formError" class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/20 px-3 py-2 rounded-xl border border-red-200 dark:border-red-900/30">
            {{ formError }}
          </div>

          <!-- Success -->
          <div v-if="formSuccess" class="text-sm text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 px-3 py-2 rounded-xl border border-emerald-200 dark:border-emerald-900/30 flex items-center gap-2">
            <span class="material-icons-outlined text-[16px]">check_circle</span>
            Weight record logged successfully!
          </div>

          <div class="flex gap-3 pt-3 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              @click="closeModal"
              class="flex-1 py-2.5 border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-bold rounded-xl text-gray-700 dark:text-gray-300 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="flex-1 py-2.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow transition flex items-center justify-center gap-2"
            >
              <span v-if="submitting" class="material-icons-outlined text-[16px] animate-spin">sync</span>
              {{ submitting ? 'Saving…' : 'Save Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const samples = ref([])
const summaryData = ref([])
const tableLoading = ref(false)
const chartLoading = ref(false)
const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)

let chartInstance = null
const chartCanvas = ref(null)

// ── Breed Standard Ross 308 Target Curve ──
const breedStandards = [
  { day: 0, weight: 42 },
  { day: 7, weight: 189 },
  { day: 14, weight: 498 },
  { day: 21, weight: 991 },
  { day: 28, weight: 1612 },
  { day: 35, weight: 2337 },
  { day: 42, weight: 3054 }
]

const getBreedStandardWeight = (ageDays) => {
  if (ageDays <= 0) return 42
  if (ageDays >= 42) return 3054
  for (let i = 0; i < breedStandards.length - 1; i++) {
    const p1 = breedStandards[i]
    const p2 = breedStandards[i + 1]
    if (ageDays >= p1.day && ageDays <= p2.day) {
      const ratio = (ageDays - p1.day) / (p2.day - p1.day)
      return p1.weight + ratio * (p2.weight - p1.weight)
    }
  }
  return 42
}

// ── Form helpers ──────────────────────────
const getTodayString = () => {
  const d = new Date()
  return [d.getFullYear(), String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')].join('-')
}

const form = ref({
  date: getTodayString(),
  avg_weight_g: null,
  sample_size: 20
})

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

const activeCohortAge = computed(() => {
  if (!activeBatchObj.value) return 0
  const start = new Date(activeBatchObj.value.start_date)
  const today = new Date()
  const diffTime = today - start
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 ? diffDays : 0
})

const calculateAge = (dateStr) => {
  if (!activeBatchObj.value) return 0
  const start = new Date(activeBatchObj.value.start_date)
  const current = new Date(dateStr)
  const diffTime = current - start
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 ? diffDays : 0
}

const enrichedSamples = computed(() => {
  return samples.value.map(s => {
    const age = calculateAge(s.date)
    const std = getBreedStandardWeight(age)
    const deviation = std > 0 ? ((s.avg_weight_g - std) / std) * 100 : 0
    const summary = summaryData.value.find(sm => sm.date === s.date)
    const growthRate = summary ? summary.growth_rate_g_per_day : 0
    return {
      ...s,
      age,
      stdWeight: std,
      deviation,
      growthRate
    }
  })
})

const latestSample = computed(() => {
  if (enrichedSamples.value.length === 0) return null
  // The samples list from API is sorted by date desc, so the first is the latest
  return enrichedSamples.value[0]
})

// ── Data fetching ──────────────────────────
const fetchSamples = async () => {
  if (!selectedBatchId.value) return
  tableLoading.value = true
  try {
    samples.value = await api.growth.list(selectedBatchId.value)
  } catch (err) {
    console.error('Failed to load growth samples:', err)
  } finally {
    tableLoading.value = false
  }
}

const fetchSummary = async () => {
  if (!selectedBatchId.value) return
  chartLoading.value = true
  try {
    summaryData.value = await api.growth.getSummary(selectedBatchId.value)
  } catch (err) {
    console.error('Failed to load growth summary:', err)
  } finally {
    chartLoading.value = false
  }
}

const loadAll = async () => {
  await Promise.all([fetchSamples(), fetchSummary()])
  await nextTick()
  renderChart()
}

const onBatchChange = () => {
  loadAll()
}

// ── Chart rendering ──────────────────────────
const renderChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  if (!chartCanvas.value || summaryData.value.length === 0) return

  // Sort ascending by date for chart plotting
  const data = [...summaryData.value].sort((a, b) => new Date(a.date) - new Date(b.date))
  const labels = data.map(d => formatDateShort(d.date))

  // Find standard curves corresponding to age
  const targetData = data.map(d => {
    const age = calculateAge(d.date)
    return getBreedStandardWeight(age)
  })

  const isDark = document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const textColor = isDark ? '#9ca3af' : '#6b7280'

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Actual weight (g)',
          data: data.map(d => d.avg_weight_g),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.08)',
          borderWidth: 2.5,
          tension: 0.25,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#10b981',
        },
        {
          label: 'Ross 308 Target (g)',
          data: targetData,
          borderColor: '#6b7280',
          borderWidth: 1.5,
          borderDash: [5, 5],
          tension: 0.1,
          fill: false,
          pointRadius: 0,
          pointHoverRadius: 0,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          padding: 10,
          cornerRadius: 8,
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: textColor,
            font: {
              size: 10,
              family: 'Inter'
            }
          }
        },
        y: {
          grid: {
            color: gridColor
          },
          ticks: {
            color: textColor,
            font: {
              size: 10,
              family: 'Inter'
            }
          }
        }
      }
    }
  })
}

// ── Modals & Actions ──────────────────────────
const closeModal = () => {
  showLogModal.value = false
  formError.value = ''
  formSuccess.value = false
  form.value = {
    date: getTodayString(),
    avg_weight_g: null,
    sample_size: 20
  }
}

const submitSample = async () => {
  formError.value = ''
  formSuccess.value = false
  submitting.value = true

  try {
    await api.growth.create({
      batch_id: selectedBatchId.value,
      date: form.value.date,
      avg_weight_g: form.value.avg_weight_g,
      sample_size: form.value.sample_size
    })
    formSuccess.value = true
    setTimeout(() => {
      closeModal()
      loadAll()
    }, 1000)
  } catch (err) {
    formError.value = err.message || 'Failed to save weight sample.'
  } finally {
    submitting.value = false
  }
}

// ── Formatting ──────────────────────────
const formatDate = (dateStr) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

const formatDateShort = (dateStr) => {
  const options = { month: 'short', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

const getDeviationClass = (dev) => {
  if (dev === null || dev === undefined) return 'text-gray-400'
  if (dev >= 5) return 'text-emerald-600 dark:text-emerald-400 font-bold'
  if (dev <= -5) return 'text-rose-600 dark:text-rose-400 font-bold'
  return 'text-gray-600 dark:text-gray-400'
}

// ── Lifecycle & Watchers ──────────────────
watch(() => store.activeBatch, (newVal) => {
  if (newVal && !selectedBatchId.value) {
    selectedBatchId.value = newVal.id
    loadAll()
  }
}, { immediate: true })

onMounted(() => {
  if (store.activeBatch) {
    selectedBatchId.value = store.activeBatch.id
    loadAll()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>
