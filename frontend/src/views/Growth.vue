<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Growth Monitoring</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Monitor weight gains, standard deviations, and daily growth rates for
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
        <AgriButton
          variant="primary"
          icon="add"
          :disabled="!selectedBatchId"
          @click="showLogModal = true"
        >
          Record Weight
        </AgriButton>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">scale</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">Select a batch above to view growth analytics.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Growth curves and target deviations are calculated per cohort.</p>
    </div>

    <template v-else>

      <!-- ─── Summary KPIs (Staggered load) ─── -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <AgriStatCard
          label="Average Weight"
          :value="latestSample ? latestSample.avg_weight_g : 0"
          suffix=" g"
          icon="balance"
          icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450"
          :loading="tableLoading"
          :trend="latestSample ? `${latestSample.deviation >= 0 ? '+' : ''}${latestSample.deviation.toFixed(1)}%` : '—'"
          :trend-direction="latestSample && latestSample.deviation >= 0 ? 'up' : 'down'"
          :trend-good="latestSample ? latestSample.deviation >= 0 : null"
          :subtext="latestSample ? 'vs breed weight target' : 'No weight samples recorded'"
          class="animate-fade-in-up delay-100"
        />

        <AgriStatCard
          label="Daily Growth Rate"
          :value="latestSample && latestSample.growthRate > 0 ? latestSample.growthRate : 0"
          :decimals="1"
          suffix=" g/d"
          icon="trending_up"
          icon-color-class="bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400"
          :loading="tableLoading"
          subtext="Target: 50-70 g / cohort day"
          class="animate-fade-in-up delay-150"
        />

        <AgriStatCard
          label="Last Sample Size"
          :value="latestSample ? latestSample.sample_size : 0"
          suffix=" birds"
          icon="groups"
          icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500"
          :loading="tableLoading"
          subtext="Recommended sample is >= 20"
          class="animate-fade-in-up delay-200"
        />

        <AgriStatCard
          label="Cohort Age"
          :value="activeCohortAge"
          suffix=" days"
          icon="calendar_today"
          icon-color-class="bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400"
          :loading="tableLoading"
          :subtext="`Start: ${formatDateShort(activeBatchObj.start_date)}`"
          class="animate-fade-in-up delay-250"
        />
      </div>

      <!-- ─── Chart ─── -->
      <AgriCard class="animate-fade-in-up delay-300" padding="none">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">stacked_line_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Growth Curve Comparison</h2>
          </div>
          <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-primary-500"></span> <span class="text-gray-400">Actual (g)</span></span>
            <span class="flex items-center gap-1"><span class="h-0.5 w-3 bg-gray-400 dark:bg-gray-600 border-t border-dashed"></span> <span class="text-gray-400">Breed Target (Ross 308)</span></span>
          </div>
        </template>

        <div v-if="chartLoading" class="h-72 flex items-center justify-center">
          <span class="material-icons-outlined text-2xl text-primary-500 animate-spin">sync</span>
        </div>
        <div v-else-if="samples.length === 0" class="h-72 flex flex-col items-center justify-center text-sm text-gray-400 dark:text-gray-500 p-6 text-center">
          <span class="material-icons-outlined text-3xl mb-2 text-gray-300 dark:text-gray-700">query_stats</span>
          <p class="font-bold text-gray-700 dark:text-gray-300">No telemetry charts available</p>
          <p class="text-xs mt-1">Record weight samples to view the FCR growth curve comparison.</p>
        </div>
        <div v-else class="p-4">
          <canvas ref="chartCanvas" class="w-full" style="height: 280px;"></canvas>
        </div>
      </AgriCard>

      <!-- ─── Weight Logs Table ─── -->
      <AgriCard class="animate-fade-in-up delay-350" padding="none">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">table_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Growth Logs</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ samples.length }} samples</span>
          </div>
        </template>

        <AgriTable
          :headers="tableHeaders"
          :items="enrichedSamples"
          :loading="tableLoading"
          striped
          class="border-none shadow-none rounded-none"
        >
          <template #date="{ item }">
            <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ formatDate(item.date) }}</span>
          </template>

          <template #age="{ item }">
            <span class="font-mono font-bold text-gray-800 dark:text-gray-200">Day {{ item.age }}</span>
          </template>

          <template #sample_size="{ item }">
            <span class="text-gray-650 dark:text-gray-450">{{ item.sample_size }} birds</span>
          </template>

          <template #avg_weight_g="{ item }">
            <span class="font-mono font-bold text-gray-900 dark:text-white">{{ item.avg_weight_g }} g</span>
          </template>

          <template #growthRate="{ item }">
            <span class="font-mono font-bold text-primary-600 dark:text-primary-400">
              {{ item.growthRate > 0 ? item.growthRate.toFixed(1) + ' g/d' : '—' }}
            </span>
          </template>

          <template #deviation="{ item }">
            <span class="font-mono text-xs font-bold" :class="getDeviationClass(item.deviation)">
              {{ item.deviation !== null && item.deviation !== undefined ? (item.deviation >= 0 ? '+' : '') + item.deviation.toFixed(1) + '%' : '—' }}
            </span>
          </template>

          <template #actions="{ item }">
            <div class="flex justify-end gap-3">
              <button @click="editSample(item)" class="text-gray-400 hover:text-primary-500 transition-colors" title="Edit">
                <span class="material-icons-outlined text-[16px] block">edit</span>
              </button>
              <button @click="deleteSample(item.id)" class="text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                <span class="material-icons-outlined text-[16px] block">delete_outline</span>
              </button>
            </div>
          </template>
        </AgriTable>
      </AgriCard>
    </template>

    <!-- ─── Record Weight Modal (AgriModal) ─── -->
    <AgriModal
      :show="showLogModal"
      :title="editingSampleId ? 'Edit Weight Record' : 'Record Cohort Weight'"
      @close="closeModal"
    >
      <form @submit.prevent="submitSample" class="space-y-4">
        <AgriInput
          v-model="form.date"
          type="date"
          label="Weighing Date"
          required
          icon="calendar_today"
        />

        <div class="grid grid-cols-2 gap-4">
          <AgriInput
            v-model.number="form.avg_weight_g"
            type="number"
            min="1"
            label="Average Weight (grams)"
            required
            placeholder="e.g. 350"
            icon="balance"
          />
          <AgriInput
            v-model.number="form.sample_size"
            type="number"
            min="1"
            label="Sample Size (Birds)"
            required
            placeholder="20"
            icon="people"
          />
        </div>

        <!-- Form Messages -->
        <div v-if="formError" class="text-xs font-semibold text-status-danger bg-red-50 dark:bg-red-950/20 px-3.5 py-2.5 rounded-xl border border-red-200 dark:border-red-900/30">
          {{ formError }}
        </div>

        <div class="flex gap-3 pt-3 border-t border-gray-150 dark:border-gray-800">
          <AgriButton
            type="button"
            variant="outline"
            class="flex-1"
            @click="closeModal"
          >
            Cancel
          </AgriButton>
          <AgriButton
            type="submit"
            variant="primary"
            class="flex-1"
            :loading="submitting"
          >
            {{ editingSampleId ? 'Save Changes' : 'Save Record' }}
          </AgriButton>
        </div>
      </form>
    </AgriModal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'
import { Chart, registerables } from 'chart.js'
import { useToast } from '../composables/useToast'

// Design System components
import AgriButton from '../components/ui/AgriButton.vue'
import AgriCard from '../components/ui/AgriCard.vue'
import AgriStatCard from '../components/ui/AgriStatCard.vue'
import AgriTable from '../components/ui/AgriTable.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriModal from '../components/ui/AgriModal.vue'
import AgriInput from '../components/ui/AgriInput.vue'
import AgriSelect from '../components/ui/AgriSelect.vue'

Chart.register(...registerables)

const toast = useToast()

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const samples = ref([])
const tableLoading = ref(false)
const chartLoading = ref(false)
const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)
const editingSampleId = ref(null)

let chartInstance = null
const chartCanvas = ref(null)

// ── Form ──────────────────────────────────
const getTodayString = () => {
  const d = new Date()
  return [d.getFullYear(), String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')].join('-')
}

const form = ref({
  date: getTodayString(),
  avg_weight_g: null,
  sample_size: 20
})

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

const calculateAge = (dateStr) => {
  if (!activeBatchObj.value?.start_date) return 0
  const start = new Date(activeBatchObj.value.start_date)
  const current = new Date(dateStr)
  start.setHours(0,0,0,0)
  current.setHours(0,0,0,0)
  const diffTime = current - start
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays >= 0 ? diffDays : 0
}

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

const latestSample = computed(() => {
  if (samples.value.length === 0) return null
  // samples are already sorted by date desc
  return enrichedSamples.value[0]
})

const activeCohortAge = computed(() => {
  if (!activeBatchObj.value?.start_date) return 0
  const start = new Date(activeBatchObj.value.start_date)
  const today = new Date()
  start.setHours(0,0,0,0)
  today.setHours(0,0,0,0)
  return Math.ceil(Math.abs(today - start) / (1000 * 60 * 60 * 24))
})

// Calculate daily growth rates between consecutive samples
const enrichedSamples = computed(() => {
  // Sort ascending to calculate rate, then reverse back to desc
  const sorted = [...samples.value].sort((a,b) => new Date(a.date) - new Date(b.date))
  
  const enriched = sorted.map((s, idx) => {
    let rate = 0
    if (idx > 0) {
      const prev = sorted[idx - 1]
      const weightDiff = s.avg_weight_g - prev.avg_weight_g
      const dateDiff = Math.ceil(Math.abs(new Date(s.date) - new Date(prev.date)) / (1000 * 60 * 60 * 24))
      if (dateDiff > 0) {
        rate = weightDiff / dateDiff
      }
    }
    const age = calculateAge(s.date)
    const targetWeight = getBreedStandardWeight(age)
    const deviation = targetWeight > 0 ? ((s.avg_weight_g - targetWeight) / targetWeight) * 100 : 0
    return {
      ...s,
      age,
      target_weight_g: targetWeight,
      deviation,
      growthRate: rate
    }
  })

  return enriched.reverse()
})

const tableHeaders = [
  { text: 'Date', value: 'date', align: 'left' },
  { text: 'Age (Days)', value: 'age', align: 'right' },
  { text: 'Sample Size', value: 'sample_size', align: 'right' },
  { text: 'Avg Weight (g)', value: 'avg_weight_g', align: 'right' },
  { text: 'Growth Rate', value: 'growthRate', align: 'right' },
  { text: 'Deviation', value: 'deviation', align: 'right' },
  { text: 'Actions', value: 'actions', align: 'right' }
]

// ── Data fetching ──────────────────────────
const fetchSamples = async () => {
  if (!selectedBatchId.value) return
  tableLoading.value = true
  try {
    samples.value = await api.growth.list(selectedBatchId.value)
  } catch (err) {
    console.error('Failed to load growth logs:', err)
  } finally {
    tableLoading.value = false
  }
}

const loadAll = async () => {
  chartLoading.value = true
  await fetchSamples()
  chartLoading.value = false
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

  if (!chartCanvas.value || samples.value.length === 0) return

  // Sort samples ascending for chart
  const sorted = [...enrichedSamples.value].reverse()
  const labels = sorted.map(s => `Day ${s.age}`)

  const isDark = document.documentElement.classList.contains('dark')
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const textColor = isDark ? '#9ca3af' : '#6b7280'

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Actual (g)',
          data: sorted.map(s => s.avg_weight_g),
          borderColor: '#2d6a4f',
          backgroundColor: 'rgba(45, 106, 79, 0.08)',
          borderWidth: 2.5,
          tension: 0.3,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: '#2d6a4f',
        },
        {
          label: 'Breed Target (Ross 308)',
          data: sorted.map(s => s.target_weight_g),
          borderColor: '#d4a373',
          borderWidth: 1.5,
          borderDash: [6, 3],
          tension: 0.3,
          fill: false,
          pointRadius: 0,
        }
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
          backgroundColor: isDark ? '#2c2c30' : '#fff',
          titleColor: isDark ? '#fff' : '#111',
          bodyColor: isDark ? '#d1d5db' : '#374151',
          borderColor: isDark ? '#374151' : '#e5e7eb',
          borderWidth: 1,
          cornerRadius: 10,
          padding: 10,
          titleFont: { weight: 'bold', size: 12 },
          bodyFont: { size: 11 },
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(0)} g`
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { size: 10 } }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { size: 10 } },
          beginAtZero: false
        }
      }
    }
  })
}

// ── Form submission ──────────────────────────
const closeModal = () => {
  showLogModal.value = false
  editingSampleId.value = null
  formError.value = ''
  formSuccess.value = false
  form.value = {
    date: getTodayString(),
    avg_weight_g: null,
    sample_size: 20
  }
}

const editSample = (s) => {
  editingSampleId.value = s.id
  form.value = {
    date: s.date,
    avg_weight_g: s.avg_weight_g,
    sample_size: s.sample_size
  }
  formError.value = ''
  formSuccess.value = false
  showLogModal.value = true
}

const deleteSample = async (id) => {
  if (!confirm('Are you sure you want to delete this sample?')) return
  try {
    await api.growth.delete(id)
    await loadAll()
    toast.success('Weight sample deleted successfully')
  } catch (err) {
    alert('Failed to delete sample: ' + err.message)
  }
}

const submitSample = async () => {
  formError.value = ''
  formSuccess.value = false
  submitting.value = true

  try {
    if (editingSampleId.value) {
      await api.growth.update(editingSampleId.value, {
        date: form.value.date,
        avg_weight_g: form.value.avg_weight_g,
        sample_size: form.value.sample_size
      })
      toast.success('Growth sample record updated')
    } else {
      await api.growth.create({
        batch_id: selectedBatchId.value,
        date: form.value.date,
        avg_weight_g: form.value.avg_weight_g,
        sample_size: form.value.sample_size
      })
      toast.success('Average cohort weight recorded')
    }
    formSuccess.value = true
    await loadAll()
    closeModal()
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
  if (dev >= 5) return 'text-emerald-600 dark:text-emerald-450 font-bold'
  if (dev <= -5) return 'text-status-danger font-bold animate-pulse'
  return 'text-gray-650 dark:text-gray-400'
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
