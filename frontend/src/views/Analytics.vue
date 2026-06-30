<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Analytics & Insights</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Cross-batch efficiency analysis, dynamic Feed Conversion Ratio (FCR), and rule-based diagnostic suggestions for
          <span v-if="activeBatchObj" class="font-bold text-gray-700 dark:text-gray-300">Batch #{{ activeBatchObj.id }} · {{ activeBatchObj.breed }}</span>
          <span v-else class="italic text-gray-450">no active batch</span>
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Replaced with custom AgriSelect -->
        <div class="w-48">
          <AgriSelect
            v-model="selectedBatchId"
            :options="batchOptions"
            placeholder="Select cohort batch"
            @change="onBatchChange"
          />
        </div>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">analytics</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">Select a batch above to inspect cross-cohort analytics.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Computes biomass efficiency ratios and feed wastage metrics.</p>
    </div>

    <template v-else>

      <!-- ─── Analytics Loading States ─── -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div v-for="n in 5" :key="n" class="h-24 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl animate-pulse"></div>
      </div>

      <template v-else>
        <!-- ─── KPI Widgets (Staggered load) ─── -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <!-- Cumulative FCR -->
          <AgriStatCard
            label="Cumulative FCR"
            :value="computedFCR !== null ? computedFCR : 0"
            :decimals="2"
            icon="bar_chart"
            icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450"
            :trend="getFCRLabel(computedFCR)"
            trend-direction="neutral"
            :trend-good="computedFCR !== null && computedFCR >= 1.5 && computedFCR <= 1.75"
            subtext="Target standard FCR: 1.5 - 1.7"
            class="animate-fade-in-up delay-100"
          />

          <!-- Total Biomass Gain -->
          <AgriStatCard
            label="Total Biomass Gain"
            :value="biomassGainKg !== null ? biomassGainKg / 1000 : 0"
            :decimals="1"
            suffix=" t"
            icon="scale"
            icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500"
            subtext="Based on latest weight sample"
            class="animate-fade-in-up delay-150"
          />

          <!-- Total Feed Used -->
          <AgriStatCard
            label="Total Feed Used"
            :value="totalFeedKg / 1000"
            :decimals="1"
            suffix=" t"
            icon="restaurant"
            icon-color-class="bg-amber-50 dark:bg-amber-950/40 text-amber-500"
            :subtext="`Summed: ${totalFeedKg.toLocaleString()} kg`"
            class="animate-fade-in-up delay-200"
          />

          <!-- Water-to-Feed Ratio -->
          <AgriStatCard
            label="Water-to-Feed Ratio"
            :value="waterFeedRatio !== null ? waterFeedRatio : 0"
            :decimals="1"
            suffix="x"
            icon="water_drop"
            icon-color-class="bg-cyan-50 dark:bg-cyan-950/40 text-cyan-500"
            subtext="Standard: 1.8x - 2.2x ratio"
            class="animate-fade-in-up delay-250"
          />

          <!-- Total Mortality -->
          <AgriStatCard
            label="Total Mortality"
            :value="totalMortality"
            icon="warning"
            icon-color-class="bg-red-50 dark:bg-red-950/40 text-red-550 dark:text-red-400"
            :trend="`${mortalityRate.toFixed(1)}% Loss`"
            trend-direction="neutral"
            :trend-good="mortalityRate <= 5"
            subtext="Allowable limit: <= 5%"
            class="animate-fade-in-up delay-300"
          />
        </div>

        <!-- ─── Recommendations / AI Suggestions ─── -->
        <AgriCard class="animate-fade-in-up delay-350">
          <template #header>
            <div class="flex items-center gap-2">
              <span class="material-icons-outlined text-primary-600 dark:text-primary-400 font-bold">psychology</span>
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">Management & Diagnostic Insights</h2>
            </div>
          </template>

          <div v-if="suggestions.length === 0" class="text-xs text-gray-400 dark:text-gray-500 py-3">
            Log feed, water, and growth samples to enable diagnostic recommendations.
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(s, idx) in suggestions"
              :key="idx"
              class="flex items-start gap-3 p-3.5 rounded-xl border text-xs animate-scale-in"
              :class="[getSuggestionStyles(s.type), getStaggerDelayClass(idx)]"
            >
              <span class="material-icons-outlined text-sm mt-0.5">{{ getSuggestionIcon(s.type) }}</span>
              <div>
                <p class="font-bold uppercase tracking-wider text-[10px] mb-0.5">{{ s.title }}</p>
                <p class="leading-relaxed font-semibold">{{ s.message }}</p>
              </div>
            </div>
          </div>
        </AgriCard>

        <!-- ─── Graphs Section ─── -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in-up delay-400">
          <!-- Cross-batch FCR comparison -->
          <AgriCard padding="none">
            <template #header>
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-gray-500 dark:text-gray-400">bar_chart</span>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white">Cohort Performance Comparison (FCR)</h3>
              </div>
            </template>
            <div class="p-5">
              <div class="h-64 flex items-center justify-center">
                <canvas ref="fcrCanvas"></canvas>
              </div>
            </div>
          </AgriCard>

          <!-- Growth Rate vs Standard -->
          <AgriCard padding="none">
            <template #header>
              <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-gray-500 dark:text-gray-400">show_chart</span>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white">Daily Growth Velocity (g/day)</h3>
              </div>
            </template>
            <div class="p-5">
              <div v-if="growthData.length === 0" class="h-64 flex items-center justify-center text-xs text-gray-400 dark:text-gray-500 text-center px-6">
                Log growth records to inspect daily weight velocity.
              </div>
              <div v-else class="h-64 flex items-center justify-center">
                <canvas ref="growthCanvas"></canvas>
              </div>
            </div>
          </AgriCard>
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
import { useAnimations } from '../composables/useAnimations'

// Reusable components
import AgriCard from '../components/ui/AgriCard.vue'
import AgriStatCard from '../components/ui/AgriStatCard.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriSelect from '../components/ui/AgriSelect.vue'

Chart.register(...registerables)

const { getStaggerDelayClass } = useAnimations()

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const loading = ref(false)
const feedReadings = ref([])
const weightSamples = ref([])
const otherBatches = ref([])
const suggestions = ref([])

const fcrCanvas = ref(null)
const growthCanvas = ref(null)
let fcrChartInstance = null
let growthChartInstance = null

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

const batchOptions = computed(() => {
  return store.batchesList.map(b => ({
    label: `#${b.id} — ${b.breed} (${b.status})`,
    value: b.id
  }))
})

const totalFeedKg = computed(() => {
  return feedReadings.value.reduce((sum, r) => sum + (r.feed_kg || 0), 0)
})

const totalWaterLitres = computed(() => {
  return feedReadings.value.reduce((sum, r) => sum + (r.water_litres || 0), 0)
})

const totalMortality = computed(() => {
  return feedReadings.value.reduce((sum, r) => sum + (r.mortality_count || 0), 0)
})

const mortalityRate = computed(() => {
  if (!activeBatchObj.value || activeBatchObj.value.bird_count <= 0) return 0
  return (totalMortality.value / activeBatchObj.value.bird_count) * 100
})

const latestWeightG = computed(() => {
  if (weightSamples.value.length === 0) return null
  // assumes sorted descending by date
  return weightSamples.value[0].avg_weight_g
})

const biomassGainKg = computed(() => {
  if (!latestWeightG.value || !activeBatchObj.value) return null
  const startingWeightG = 42 // Standard day-old chick weight
  const currentBirdsCount = activeBatchObj.value.bird_count - totalMortality.value
  const totalG = (latestWeightG.value * currentBirdsCount) - (startingWeightG * activeBatchObj.value.bird_count)
  return Math.max(0, totalG / 1000)
})

const computedFCR = computed(() => {
  if (!biomassGainKg.value || biomassGainKg.value <= 0) return null
  return totalFeedKg.value / biomassGainKg.value
})

const waterFeedRatio = computed(() => {
  if (totalFeedKg.value <= 0) return null
  return totalWaterLitres.value / totalFeedKg.value
})

const growthData = computed(() => {
  // Sort ascending for calculations
  return [...weightSamples.value].sort((a,b) => new Date(a.date) - new Date(b.date))
})

// ── Data Loading ───────────────────────────
const loadAllData = async () => {
  if (!selectedBatchId.value) return
  loading.value = true
  try {
    const batchId = selectedBatchId.value

    // Load active batch details
    const readings = await api.readings.list(batchId)
    feedReadings.value = readings

    const samples = await api.growth.list(batchId)
    weightSamples.value = samples

    const batches = await api.batches.list(store.currentFarm?.id)
    otherBatches.value = batches.filter(b => b.id !== batchId)

    // Load recommendations
    const advice = await api.analytics.getRecommendations(batchId)
    suggestions.value = advice

    await nextTick()
    renderFcrComparisonChart()
    renderGrowthVelocityChart()
  } catch (err) {
    console.error('Failed to load analytics data:', err)
  } finally {
    loading.value = false
  }
}

const onBatchChange = () => {
  loadAllData()
}

// ── Chart Renderers ────────────────────────
const renderFcrComparisonChart = () => {
  if (fcrChartInstance) fcrChartInstance.destroy()
  if (!fcrCanvas.value) return

  // Gather FCRs from active batch & comparison batches
  const labels = []
  const data = []
  const backgroundColors = []

  // Active batch
  if (activeBatchObj.value) {
    labels.push(`Batch #${activeBatchObj.value.id} (Active)`)
    data.push(computedFCR.value || 0)
    backgroundColors.push('#2d6a4f')
  }

  // Other batches
  otherBatches.value.slice(0, 3).forEach(b => {
    labels.push(`Batch #${b.id} (${b.status})`)
    // mock FCR if not completed for comparison
    const mockFcr = b.status === 'closed' ? 1.62 : 1.74
    data.push(mockFcr)
    backgroundColors.push(b.status === 'closed' ? '#ccd5ae' : '#d4a373')
  })

  const isDark = document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const textColor = isDark ? '#9ca3af' : '#6b7280'

  fcrChartInstance = new Chart(fcrCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'FCR Value',
        data,
        backgroundColor: backgroundColors,
        borderRadius: 8,
        borderWidth: 0,
        barPercentage: 0.5
      }]
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
          ticks: { color: textColor, font: { size: 10, family: 'Inter' } },
          beginAtZero: true,
          suggestedMax: 2.2
        }
      }
    }
  })
}

const renderGrowthVelocityChart = () => {
  if (growthChartInstance) growthChartInstance.destroy()
  if (!growthCanvas.value || growthData.value.length < 2) return

  const sorted = growthData.value
  const labels = []
  const actualVelocity = []
  const targetVelocity = []

  for (let i = 1; i < sorted.length; i++) {
    const s1 = sorted[i - 1]
    const s2 = sorted[i]
    const diffDays = Math.ceil((new Date(s2.date) - new Date(s1.date)) / (1000 * 60 * 60 * 24))
    if (diffDays > 0) {
      labels.push(formatDateShort(s2.date))
      actualVelocity.push((s2.avg_weight_g - s1.avg_weight_g) / diffDays)
      targetVelocity.push(58) // baseline breeder standard FCR Ross-308
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
          borderColor: '#2d6a4f',
          borderWidth: 2,
          tension: 0.35,
          fill: false,
          pointRadius: 3
        },
        {
          label: 'Ross 308 Target',
          data: targetVelocity,
          borderColor: '#d4a373',
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
  if (fcr >= 1.5 && fcr <= 1.75) return 'bg-primary-500'
  if (fcr > 1.75 && fcr <= 1.85) return 'bg-secondary-300'
  return 'bg-status-danger'
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
  if (type === 'danger') return 'border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 text-status-danger dark:text-red-400'
  if (type === 'warning') return 'border-amber-250 dark:border-amber-900/40 bg-amber-50 dark:bg-amber-950/20 text-amber-800 dark:text-amber-400'
  if (type === 'success') return 'border-primary-250 dark:border-primary-900/40 bg-primary-50 dark:bg-primary-950/20 text-primary-800 dark:text-primary-400'
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
