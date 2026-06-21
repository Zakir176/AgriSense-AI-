<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Feed & Water Logs</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Record daily consumption and monitor rolling deviations for
          <span v-if="store.activeBatch" class="font-semibold text-gray-700 dark:text-gray-300">Batch #{{ store.activeBatch.id }} · {{ store.activeBatch.breed }}</span>
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
          Log Reading
        </button>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">opacity</span>
      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">Select a batch above to view feed and water logs.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Readings are tracked per-batch. Choose an active cohort to start.</p>
    </div>

    <template v-else>

      <!-- ─── Summary KPIs ─── -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Total Readings</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ readings.length }}</div>
        </div>
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Latest Feed</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
            {{ readings.length > 0 ? readings[0].feed_kg?.toFixed(1) + ' kg' : '—' }}
          </div>
        </div>
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Latest Water</div>
          <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
            {{ readings.length > 0 ? readings[0].water_litres?.toFixed(1) + ' L' : '—' }}
          </div>
        </div>
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-sm">
          <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Flagged</div>
          <div class="text-2xl font-black tabular-nums" :class="flaggedCount > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-gray-900 dark:text-white'">
            {{ flaggedCount }}
          </div>
        </div>
      </div>

      <!-- ─── Chart ─── -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">show_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Consumption Trends</h2>
          </div>
          <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-primary-500"></span> <span class="text-gray-400">Feed</span></span>
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-blue-500"></span> <span class="text-gray-400">Water</span></span>
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-sm bg-primary-300/40 border border-primary-300"></span> <span class="text-gray-400">7d Avg</span></span>
          </div>
        </div>

        <div v-if="chartLoading" class="h-72 flex items-center justify-center">
          <span class="material-icons-outlined text-2xl text-gray-300 dark:text-gray-700 animate-spin">sync</span>
        </div>
        <div v-else-if="summaryData.length < 2" class="h-72 flex flex-col items-center justify-center text-sm text-gray-400 dark:text-gray-500">
          <span class="material-icons-outlined text-3xl mb-2 text-gray-300 dark:text-gray-700">timeline</span>
          Need at least 2 readings to chart trends.
        </div>
        <div v-else class="p-4">
          <canvas ref="chartCanvas" class="w-full" style="height: 280px;"></canvas>
        </div>
      </div>

      <!-- ─── Readings Table ─── -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">table_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">All Readings</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ readings.length }} entries</span>
          </div>
        </div>

        <div v-if="tableLoading" class="p-5 space-y-2.5">
          <div v-for="n in 5" :key="n" class="h-10 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="readings.length === 0" class="py-14 text-center">
          <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-2">water_drop</span>
          <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">No readings logged yet</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Click "Log Reading" to record today's feed and water consumption.</p>
        </div>

        <div v-else>
          <!-- Table header -->
          <div class="grid grid-cols-5 px-5 py-2 text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
            <span>Date</span>
            <span class="text-right">Feed (kg)</span>
            <span class="text-right">Water (L)</span>
            <span class="text-right">Feed Δ%</span>
            <span class="text-right">Status</span>
          </div>
          <div class="divide-y divide-gray-100 dark:divide-gray-800 max-h-[440px] overflow-y-auto">
            <div
              v-for="(r, idx) in enrichedReadings"
              :key="r.id ?? idx"
              class="grid grid-cols-5 px-5 py-3 text-sm items-center hover:bg-gray-50 dark:hover:bg-darkbg-100 transition"
            >
              <span class="text-gray-700 dark:text-gray-300 font-medium text-xs">{{ formatDate(r.date) }}</span>
              <span class="text-right text-gray-900 dark:text-white font-semibold tabular-nums">{{ r.feed_kg?.toFixed(1) }}</span>
              <span class="text-right text-gray-900 dark:text-white font-semibold tabular-nums">{{ r.water_litres?.toFixed(1) }}</span>
              <span class="text-right tabular-nums text-xs font-semibold"
                :class="getDeviationClass(r._feedDevPct)">
                {{ r._feedDevPct !== null ? (r._feedDevPct >= 0 ? '+' : '') + r._feedDevPct.toFixed(1) + '%' : '—' }}
              </span>
              <span class="flex justify-end">
                <span
                  class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-bold"
                  :class="r.flagged_abnormal
                    ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400'
                    : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'"
                >
                  <span class="material-icons-outlined text-[10px]">{{ r.flagged_abnormal ? 'warning' : 'check' }}</span>
                  {{ r.flagged_abnormal ? 'Flagged' : 'Normal' }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ Log Reading Modal ═══ -->
    <div
      v-if="showLogModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto"
      @click.self="closeModal"
    >
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 w-full max-w-md rounded-2xl shadow-xl p-6 space-y-5">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Log Daily Reading</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>

        <form @submit.prevent="submitReading" class="space-y-4">
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
            <!-- Feed -->
            <div>
              <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Feed (kg)</label>
              <input
                v-model.number="form.feed_kg"
                type="number"
                step="0.1"
                min="0"
                required
                placeholder="e.g. 125.0"
                class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
              />
            </div>
            <!-- Water -->
            <div>
              <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Water (L)</label>
              <input
                v-model.number="form.water_litres"
                type="number"
                step="0.1"
                min="0"
                required
                placeholder="e.g. 210.0"
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
            Reading logged successfully!
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
              {{ submitting ? 'Saving…' : 'Save Reading' }}
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
const readings = ref([])
const summaryData = ref([])
const tableLoading = ref(false)
const chartLoading = ref(false)
const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)

let chartInstance = null
const chartCanvas = ref(null)

// ── Form ──────────────────────────────────
const getTodayString = () => {
  const d = new Date()
  return [d.getFullYear(), String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')].join('-')
}

const form = ref({
  date: getTodayString(),
  feed_kg: null,
  water_litres: null,
})

// ── Computed ──────────────────────────────
const flaggedCount = computed(() => readings.value.filter(r => r.flagged_abnormal).length)

// Enrich readings with deviation % from summary data
const enrichedReadings = computed(() => {
  const summaryMap = {}
  summaryData.value.forEach(s => { summaryMap[s.date] = s })

  return readings.value.map(r => {
    const summary = summaryMap[r.date]
    return {
      ...r,
      _feedDevPct: summary ? summary.feed_deviation_pct : null,
      _waterDevPct: summary ? summary.water_deviation_pct : null,
    }
  })
})

// ── Data fetching ──────────────────────────
const fetchReadings = async () => {
  if (!selectedBatchId.value) return
  tableLoading.value = true
  try {
    readings.value = await api.readings.list(selectedBatchId.value)
  } catch (err) {
    console.error('Failed to load readings:', err)
  } finally {
    tableLoading.value = false
  }
}

const fetchSummary = async () => {
  if (!selectedBatchId.value) return
  chartLoading.value = true
  try {
    summaryData.value = await api.readings.getSummary(selectedBatchId.value)
  } catch (err) {
    console.error('Failed to load summary:', err)
  } finally {
    chartLoading.value = false
  }
}

const loadAll = async () => {
  await Promise.all([fetchReadings(), fetchSummary()])
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

  if (!chartCanvas.value || summaryData.value.length < 2) return

  const data = summaryData.value
  const labels = data.map(d => formatDateShort(d.date))

  const isDark = document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const textColor = isDark ? '#9ca3af' : '#6b7280'

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Feed (kg)',
          data: data.map(d => d.feed_kg),
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.08)',
          borderWidth: 2,
          tension: 0.35,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: '#22c55e',
        },
        {
          label: 'Water (L)',
          data: data.map(d => d.water_litres),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.06)',
          borderWidth: 2,
          tension: 0.35,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: '#3b82f6',
        },
        {
          label: 'Feed 7d Avg',
          data: data.map(d => d.feed_rolling_avg_7d),
          borderColor: 'rgba(34, 197, 94, 0.4)',
          borderWidth: 1.5,
          borderDash: [6, 3],
          tension: 0.4,
          fill: false,
          pointRadius: 0,
        },
        {
          label: 'Water 7d Avg',
          data: data.map(d => d.water_rolling_avg_7d),
          borderColor: 'rgba(59, 130, 246, 0.35)',
          borderWidth: 1.5,
          borderDash: [6, 3],
          tension: 0.4,
          fill: false,
          pointRadius: 0,
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: isDark ? '#1e2722' : '#fff',
          titleColor: isDark ? '#fff' : '#111',
          bodyColor: isDark ? '#d1d5db' : '#374151',
          borderColor: isDark ? '#374151' : '#e5e7eb',
          borderWidth: 1,
          cornerRadius: 10,
          padding: 10,
          titleFont: { weight: 'bold', size: 12 },
          bodyFont: { size: 11 },
          callbacks: {
            label: (ctx) => {
              const unit = ctx.datasetIndex <= 1
                ? (ctx.datasetIndex === 0 ? ' kg' : ' L')
                : (ctx.datasetIndex === 2 ? ' kg (avg)' : ' L (avg)')
              return `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}${unit}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { size: 10 } },
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { size: 10 } },
          beginAtZero: false,
        }
      }
    }
  })
}

// ── Form submission ──────────────────────────
const submitReading = async () => {
  formError.value = ''
  formSuccess.value = false
  submitting.value = true

  try {
    await api.readings.create({
      batch_id: selectedBatchId.value,
      date: form.value.date,
      feed_kg: form.value.feed_kg,
      water_litres: form.value.water_litres,
    })
    formSuccess.value = true

    // Refresh data
    await loadAll()

    // Auto-close after brief success flash
    setTimeout(() => {
      closeModal()
    }, 1200)
  } catch (err) {
    formError.value = err.message || 'Failed to save reading.'
  } finally {
    submitting.value = false
  }
}

const closeModal = () => {
  showLogModal.value = false
  formError.value = ''
  formSuccess.value = false
  form.value = {
    date: getTodayString(),
    feed_kg: null,
    water_litres: null,
  }
}

// ── Helpers ──────────────────────────────────
const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

const formatDateShort = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
}

const getDeviationClass = (pct) => {
  if (pct === null) return 'text-gray-400 dark:text-gray-600'
  if (Math.abs(pct) > 20) return 'text-red-500 dark:text-red-400'
  if (Math.abs(pct) > 10) return 'text-amber-500 dark:text-amber-400'
  return 'text-gray-500 dark:text-gray-400'
}

// ── Lifecycle ──────────────────────────────
watch(() => store.activeBatch, (newBatch) => {
  if (newBatch?.id && !selectedBatchId.value) {
    selectedBatchId.value = newBatch.id
    loadAll()
  }
}, { immediate: true })

onMounted(() => {
  if (store.activeBatch?.id) {
    selectedBatchId.value = store.activeBatch.id
    loadAll()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>
