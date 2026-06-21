<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Analytics & Insights</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Cross-batch efficiency analysis, dynamic Feed Conversion Ratio (FCR), and rule-based diagnostic suggestions for
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
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">analytics</span>
      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">Select a batch above to inspect cross-cohort analytics.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Computes biomass efficiency ratios and feed wastage metrics.</p>
    </div>

    <template v-else>

      <!-- ─── Analytics Loading States ─── -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="n in 3" :key="n" class="h-24 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl animate-pulse"></div>
      </div>

      <template v-else>
        <!-- ─── KPI Widgets ─── -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Cumulative FCR -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Cumulative FCR</div>
            <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
              {{ computedFCR !== null ? computedFCR.toFixed(2) : '—' }}
            </div>
            <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1.5 flex items-center gap-1">
              <span class="h-2 w-2 rounded-full" :class="getFCRColor(computedFCR)"></span>
              {{ getFCRLabel(computedFCR) }} (Target 1.5 - 1.7)
            </p>
          </div>

          <!-- Total Biomass Gain -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Total Biomass Gain</div>
            <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
              {{ biomassGainKg !== null ? (biomassGainKg / 1000).toFixed(1) + ' t' : '—' }}
            </div>
            <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1.5">Based on latest weight sample</p>
          </div>

          <!-- Total Feed Used -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Total Feed Consumed</div>
            <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
              {{ (totalFeedKg / 1000).toFixed(1) }} t
            </div>
            <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1.5">Sum of daily logs: {{ totalFeedKg.toLocaleString() }} kg</p>
          </div>

          <!-- Water-to-Feed Ratio -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Water-to-Feed Ratio</div>
            <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
              {{ waterFeedRatio !== null ? waterFeedRatio.toFixed(1) + 'x' : '—' }}
            </div>
            <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1.5">Standard: 1.8x - 2.2x ratio</p>
          </div>
        </div>

        <!-- ─── Recommendations / AI Suggestions ─── -->
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-4">
          <div class="flex items-center gap-1.5 border-b border-gray-100 dark:border-gray-800 pb-3">
            <span class="material-icons-outlined text-primary-600 dark:text-primary-400 font-bold">psychology</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Management Recommendations</h2>
          </div>

          <div v-if="suggestions.length === 0" class="text-xs text-gray-400 dark:text-gray-500 py-3">
            Log feed, water, and growth samples to enable diagnostic recommendations.
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(s, idx) in suggestions"
              :key="idx"
              class="flex items-start gap-3 p-3.5 rounded-xl border text-xs"
              :class="getSuggestionStyles(s.type)"
            >
              <span class="material-icons-outlined text-sm mt-0.5">{{ getSuggestionIcon(s.type) }}</span>
              <div>
                <p class="font-bold uppercase tracking-wider text-[10px] mb-0.5">{{ s.title }}</p>
                <p class="leading-relaxed font-medium">{{ s.message }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── Graphs Section ─── -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Cross-batch FCR comparison -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden p-5 space-y-4">
            <div class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3">
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-gray-500">bar_chart</span>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white">Cohort Performance Comparison (FCR)</h3>
              </div>
            </div>
            <div class="h-64 flex items-center justify-center">
              <canvas ref="fcrCanvas"></canvas>
            </div>
          </div>

          <!-- Growth Rate vs Standard -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden p-5 space-y-4">
            <div class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-3">
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-gray-500">show_chart</span>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white">Daily Growth Rate (g/day)</h3>
              </div>
            </div>
            <div class="h-64 flex items-center justify-center">
              <div v-if="growthData.length === 0" class="text-xs text-gray-400 dark:text-gray-500">
                Log growth records to inspect daily weight velocity.
              </div>
              <canvas v-else ref="growthCanvas"></canvas>
            </div>
          </div>
        </div>
      </template>

    </template>
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
const growthData = ref([])
const loading = ref(false)

let fcrChartInstance = null
let growthChartInstance = null

const fcrCanvas = ref(null)
const growthCanvas = ref(null)

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

const totalFeedKg = computed(() => {
  return readings.value.reduce((sum, r) => sum + (r.feed_kg || 0), 0)
})

const totalWaterLitres = computed(() => {
  return readings.value.reduce((sum, r) => sum + (r.water_litres || 0), 0)
})

const waterFeedRatio = computed(() => {
  if (totalFeedKg.value === 0) return null
  return totalWaterLitres.value / totalFeedKg.value
})

const latestWeightG = computed(() => {
  if (growthData.value.length === 0) return null
  // Sort desc to get latest
  const sorted = [...growthData.value].sort((a, b) => new Date(b.date) - new Date(a.date))
  return sorted[0].avg_weight_g
})

const biomassGainKg = computed(() => {
  if (latestWeightG.value === null || !activeBatchObj.value) return null
  // Hatch weight is ~42g
  const weightGainG = latestWeightG.value - 42
  const gainPerBirdKg = weightGainG / 1000
  return gainPerBirdKg * activeBatchObj.value.bird_count
})

const computedFCR = computed(() => {
  if (biomassGainKg.value === null || biomassGainKg.value <= 0 || totalFeedKg.value === 0) return null
  return totalFeedKg.value / biomassGainKg.value
})

// ── Suggestions System ─────────────────────
const suggestions = computed(() => {
  const items = []
  if (!activeBatchObj.value) return items

  // Check FCR levels
  const fcr = computedFCR.value
  if (fcr !== null) {
    if (fcr > 1.85) {
      items.push({
        type: 'danger',
        title: 'Elevated Feed Conversion Ratio',
        message: `Current FCR of ${fcr.toFixed(2)} indicates flock consumes excessive feed relative to weight gain. Check for feed hopper leakage, draft cooling causing feed energy burn, or high cull rates.`
      })
    } else if (fcr < 1.45) {
      items.push({
        type: 'success',
        title: 'Outstanding Feed Efficiency',
        message: `FCR is sitting at a highly efficient ${fcr.toFixed(2)}. Verify average flock weight sample sizes are representative of full cohort sizing (min 20 birds).`
      })
    }
  }

  // Check Water ratio
  const ratio = waterFeedRatio.value
  if (ratio !== null) {
    if (ratio > 2.5) {
      items.push({
        type: 'warning',
        title: 'High Water-to-Feed Ratio',
        message: `Water ratio is ${ratio.toFixed(1)}x feed. Elevated water intake suggests heat distress cooling cycles or potential water nipple line leaks. Verify house temperatures immediately.`
      })
    } else if (ratio < 1.7) {
      items.push({
        type: 'warning',
        title: 'Low Water-to-Feed Ratio',
        message: `Water ratio is ${ratio.toFixed(1)}x feed. Low water availability severely suppresses growth velocities. Check drinking line pressure gauges and filter blockages.`
      })
    }
  }

  // General recommendations based on age
  if (activeBatchObj.value) {
    const age = activeCohortAge()
    if (age < 7) {
      items.push({
        type: 'info',
        title: 'Brooding Phase Operations',
        message: 'Flock is in critical week 1 brooding. Maintain ambient temperature at 31-33°C, relative humidity at 60%, and ensure feed trays remain easily accessible.'
      })
    } else if (age >= 35) {
      items.push({
        type: 'warning',
        title: 'Harvest Window Approaching',
        message: 'Cohort age is reaching harvest parameters. Closely monitor ventilation and stocking densities. Confirm all medication withdrawal times are strictly observed.'
      })
    }
  }

  return items
})

const activeCohortAge = () => {
  if (!activeBatchObj.value) return 0
  const start = new Date(activeBatchObj.value.start_date)
  const today = new Date()
  const diffTime = today - start
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 ? diffDays : 0
}

// ── Data Fetching ──────────────────────────
const loadAllData = async () => {
  if (!selectedBatchId.value) return
  loading.value = true
  try {
    const [fetchedReadings, fetchedGrowth] = await Promise.all([
      api.readings.list(selectedBatchId.value),
      api.growth.list(selectedBatchId.value)
    ])
    readings.value = fetchedReadings
    growthData.value = fetchedGrowth

    await nextTick()
    renderFcrComparisonChart()
    renderGrowthVelocityChart()
  } catch (err) {
    console.error('Failed to load analytics datasets:', err)
  } finally {
    loading.value = false
  }
}

const onBatchChange = () => {
  loadAllData()
}

// ── Chart Renderers ────────────────────────
const renderFcrComparisonChart = () => {
  if (fcrChartInstance) {
    fcrChartInstance.destroy()
    fcrChartInstance = null
  }

  if (!fcrCanvas.value) return

  // Mock static historical batch FCR data combined with current dynamically computed FCR
  const dataset = [
    { label: 'Batch #2 (Archived)', fcr: 1.62, status: 'Archived' },
    { label: 'Batch #3 (Archived)', fcr: 1.58, status: 'Archived' },
    { label: `Batch #${selectedBatchId.value} (Active)`, fcr: computedFCR.value || 1.68, status: 'Active' }
  ]

  const isDark = document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const textColor = isDark ? '#9ca3af' : '#6b7280'

  fcrChartInstance = new Chart(fcrCanvas.value, {
    type: 'bar',
    data: {
      labels: dataset.map(d => d.label),
      datasets: [
        {
          label: 'FCR Index',
          data: dataset.map(d => d.fcr),
          backgroundColor: dataset.map(d => d.status === 'Active' ? 'rgba(34, 197, 94, 0.7)' : 'rgba(107, 114, 128, 0.4)'),
          borderColor: dataset.map(d => d.status === 'Active' ? '#22c55e' : '#6b7280'),
          borderWidth: 1.5,
          borderRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: textColor, font: { size: 10, family: 'Inter' } }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { size: 10, family: 'Inter' } }
        }
      }
    }
  })
}

const renderGrowthVelocityChart = () => {
  if (growthChartInstance) {
    growthChartInstance.destroy()
    growthChartInstance = null
  }

  if (!growthCanvas.value || growthData.value.length === 0) return

  // Sort samples ascending for time mapping
  const sorted = [...growthData.value].sort((a, b) => new Date(a.date) - new Date(b.date))
  
  // Calculate average daily gains
  const labels = []
  const actualVelocity = []
  const targetVelocity = []

  for (let i = 1; i < sorted.length; i++) {
    const s1 = sorted[i-1]
    const s2 = sorted[i]
    const diffDays = Math.ceil((new Date(s2.date) - new Date(s1.date)) / (1000 * 60 * 60 * 24))
    if (diffDays > 0) {
      labels.push(formatDateShort(s2.date))
      actualVelocity.push((s2.avg_weight_g - s1.avg_weight_g) / diffDays)
      targetVelocity.push(58) // Breed velocity baseline (58g/day)
    }
  }

  const isDark = document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const textColor = isDark ? '#9ca3af' : '#6b7280'

  growthChartInstance = new Chart(growthCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Weight Gain (g/day)',
          data: actualVelocity,
          borderColor: '#10b981',
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          pointRadius: 3
        },
        {
          label: 'Ross 308 Target',
          data: targetVelocity,
          borderColor: '#4b5563',
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: textColor, font: { size: 10, family: 'Inter' } }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { size: 10, family: 'Inter' } }
        }
      }
    }
  })
}

// ── Formatting ──────────────────────────
const formatDateShort = (dateStr) => {
  const options = { month: 'short', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

const getFCRColor = (fcr) => {
  if (fcr === null) return 'bg-gray-400'
  if (fcr >= 1.5 && fcr <= 1.75) return 'bg-emerald-500'
  if (fcr > 1.75 && fcr <= 1.85) return 'bg-amber-500'
  return 'bg-rose-500'
}

const getFCRLabel = (fcr) => {
  if (fcr === null) return 'Not Calculated'
  if (fcr >= 1.5 && fcr <= 1.75) return 'Ideal Efficiency'
  if (fcr > 1.75 && fcr <= 1.85) return 'Moderate Variance'
  return 'Inefficient Conversion'
}

const getSuggestionIcon = (type) => {
  if (type === 'danger') return 'report_problem'
  if (type === 'warning') return 'warning'
  if (type === 'success') return 'check_circle'
  return 'info'
}

const getSuggestionStyles = (type) => {
  if (type === 'danger') return 'border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 text-red-750 dark:text-red-400'
  if (type === 'warning') return 'border-amber-200 dark:border-amber-900/40 bg-amber-50 dark:bg-amber-950/20 text-amber-800 dark:text-amber-400'
  if (type === 'success') return 'border-emerald-250 dark:border-emerald-900/40 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-850 dark:text-emerald-450'
  return 'border-blue-200 dark:border-blue-900/40 bg-blue-50 dark:bg-blue-950/20 text-blue-800 dark:text-blue-400'
}

// ── Lifecycle & Watchers ──────────────────
watch(() => store.activeBatch, (newVal) => {
  if (newVal && !selectedBatchId.value) {
    selectedBatchId.value = newVal.id
    loadAllData()
  }
}, { immediate: true })

onMounted(() => {
  if (store.activeBatch) {
    selectedBatchId.value = store.activeBatch.id
    loadAllData()
  }
})

onUnmounted(() => {
  if (fcrChartInstance) fcrChartInstance.destroy()
  if (growthChartInstance) growthChartInstance.destroy()
})
</script>
