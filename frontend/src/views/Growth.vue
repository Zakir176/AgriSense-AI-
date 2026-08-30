<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ $t('growth.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          {{ $t('growth.subtitle') }}
          <span v-if="activeBatchObj" class="font-bold text-gray-700 dark:text-gray-300">Batch #{{ activeBatchObj.id }} · {{ activeBatchObj.breed }}</span>
          <span v-else class="italic text-gray-450">{{ $t('growth.no_active') }}</span>
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Replaced with custom AgriSelect -->
        <div class="w-48">
          <AgriSelect
            v-model="selectedBatchId"
            :options="batchOptions"
            :placeholder="$t('growth.select_batch')"
            @change="onBatchChange"
          />
        </div>
        <AgriButton
          variant="outline"
          size="sm"
          :disabled="samples.length === 0"
          @click="exportCSV"
          title="Download CSV"
        >
          <span class="material-icons-outlined text-sm">download</span>
          <span>Export CSV</span>
        </AgriButton>
        <AgriButton
          variant="primary"
          icon="add"
          :disabled="!selectedBatchId"
          @click="showLogModal = true"
        >{{ $t('growth.record_weight') }}</AgriButton>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">scale</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">{{ $t('growth.select_view') }}</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ $t('growth.calculated_desc') }}</p>
    </div>

    <template v-else>

      <!-- ─── Summary KPIs (Staggered load) ─── -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <AgriStatCard
          :label="$t('growth.avg_weight')"
          :value="latestSample ? latestSample.avg_weight_g : 0"
          suffix=" g"
          icon="balance"
          icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450"
          :loading="tableLoading"
          :trend="latestSample ? `${latestSample.deviation >= 0 ? '+' : ''}${latestSample.deviation.toFixed(1)}%` : '—'"
          :trend-direction="latestSample && latestSample.deviation >= 0 ? 'up' : 'down'"
          :trend-good="latestSample ? latestSample.deviation >= 0 : null"
          :subtext="latestSample ? $t('growth.vs_target') : $t('growth.no_samples')"
          class="animate-fade-in-up delay-100"
        />

        <AgriStatCard
          :label="$t('growth.daily_growth')"
          :value="latestSample && latestSample.growthRate > 0 ? latestSample.growthRate : 0"
          :decimals="1"
          suffix=" g/d"
          icon="trending_up"
          icon-color-class="bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400"
          :loading="tableLoading"
          :subtext="$t('growth.target_growth')"
          class="animate-fade-in-up delay-150"
        />

        <AgriStatCard
          :label="$t('growth.last_sample_size')"
          :value="latestSample ? latestSample.sample_size : 0"
          suffix=" birds"
          icon="groups"
          icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500"
          :loading="tableLoading"
          :subtext="$t('growth.recommended_sample')"
          class="animate-fade-in-up delay-200"
        />

        <AgriStatCard
          :label="$t('growth.cohort_age')"
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
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('growth.curve_comparison') }}</h2>
          </div>
          <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-primary-500"></span> <span class="text-gray-400">{{ $t('growth.actual') }}</span></span>
            <span class="flex items-center gap-1"><span class="h-0.5 w-3 bg-gray-400 dark:bg-gray-600 border-t border-dashed"></span> <span class="text-gray-400">{{ $t('growth.breed_target') }}</span></span>
          </div>
        </template>

        <div v-if="chartLoading" class="h-72 flex items-center justify-center">
          <span class="material-icons-outlined text-2xl text-primary-500 animate-spin">sync</span>
        </div>
        <div v-else-if="samples.length === 0" class="h-72 flex flex-col items-center justify-center text-sm text-gray-400 dark:text-gray-500 p-6 text-center">
          <span class="material-icons-outlined text-3xl mb-2 text-gray-300 dark:text-gray-700">query_stats</span>
          <p class="font-bold text-gray-700 dark:text-gray-300">{{ $t('growth.no_charts') }}</p>
          <p class="text-xs mt-1">{{ $t('growth.record_to_view') }}</p>
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
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('growth.logs') }}</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ samples.length }} {{ $t('growth.samples') }}</span>
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
      :title="editingSampleId ? $t('growth.edit_record') : $t('growth.record_cohort_weight')"
      @close="closeModal"
    >
      <form @submit.prevent="submitSample" class="space-y-4">
        <AgriInput
          v-model="form.date"
          type="date"
          :label="$t('growth.weighing_date')"
          required
          icon="calendar_today"
        />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AgriInput
            v-model.number="form.avg_weight_g"
            type="number"
            min="1"
            :label="$t('growth.avg_weight_grams')"
            required
            placeholder="e.g. 350"
            icon="balance"
          />
          <AgriInput
            v-model.number="form.sample_size"
            type="number"
            min="1"
            :label="$t('growth.sample_size_birds')"
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
          >{{ $t('growth.cancel') }}</AgriButton>
          <AgriButton
            type="submit"
            variant="primary"
            class="flex-1"
            :loading="submitting"
          >
            {{ editingSampleId ? $t('growth.save_changes') : $t('growth.save_record') }}
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
import { useI18n } from 'vue-i18n'

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
const { t } = useI18n()

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
  const diffTime = today - start
  return diffTime >= 0 ? Math.ceil(diffTime / (1000 * 60 * 60 * 24)) : 0
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

const tableHeaders = computed(() => [
  { text: t('growth.date'), value: 'date', align: 'left' },
  { text: t('growth.age_days'), value: 'age', align: 'right' },
  { text: t('growth.sample_size'), value: 'sample_size', align: 'right' },
  { text: t('growth.avg_weight_g'), value: 'avg_weight_g', align: 'right' },
  { text: t('growth.growth_rate'), value: 'growthRate', align: 'right' },
  { text: t('growth.deviation'), value: 'deviation', align: 'right' },
  { text: t('growth.actions'), value: 'actions', align: 'right' }
])

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
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.04)',
          borderWidth: 2.5,
          tension: 0.3,
          fill: true,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: (ctx) => {
            const idx = ctx.dataIndex;
            const s = sorted[idx];
            if (!s) return '#10b981';
            const dev = s.deviation;
            if (Math.abs(dev) > 10) return '#ef4444'; // Critical
            if (Math.abs(dev) > 5) return '#f59e0b';   // Warning
            return '#10b981'; // Optimal
          },
          pointBorderColor: (ctx) => {
            const idx = ctx.dataIndex;
            const s = sorted[idx];
            if (!s) return '#047857';
            const dev = s.deviation;
            if (Math.abs(dev) > 10) return '#b91c1c';
            if (Math.abs(dev) > 5) return '#d97706';
            return '#047857';
          },
          pointBorderWidth: 2,
        },
        {
          label: 'Breed Target Upper (+5%)',
          data: sorted.map(s => s.target_weight_g * 1.05),
          borderColor: 'transparent',
          backgroundColor: 'transparent',
          pointRadius: 0,
          fill: false,
          tension: 0.3
        },
        {
          label: 'Breed Target Lower (-5%)',
          data: sorted.map(s => s.target_weight_g * 0.95),
          borderColor: 'transparent',
          backgroundColor: isDark ? 'rgba(16, 185, 129, 0.05)' : 'rgba(46, 117, 89, 0.05)',
          pointRadius: 0,
          fill: '-1', // Fills down to Upper Target (dataset 1)
          tension: 0.3
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
          filter: (tooltipItem) => {
            // Only show labels for Actual (0) and Breed Target (3)
            return tooltipItem.datasetIndex === 0 || tooltipItem.datasetIndex === 3;
          },
          callbacks: {
            title: (tooltipItems) => {
              const idx = tooltipItems[0].dataIndex;
              const s = sorted[idx];
              return `Cohort Age: Day ${s.age} (${s.date})`;
            },
            label: (ctx) => {
              const idx = ctx.dataIndex;
              const s = sorted[idx];
              if (!s) return '';
              
              if (ctx.datasetIndex === 0) {
                const devText = s.deviation >= 0 ? `+${s.deviation.toFixed(1)}%` : `${s.deviation.toFixed(1)}%`;
                let status = 'Optimal Growth';
                if (Math.abs(s.deviation) > 10) {
                  status = s.deviation > 0 ? 'Critical Overweight 🚨' : 'Critical Underweight 🚨';
                } else if (Math.abs(s.deviation) > 5) {
                  status = s.deviation > 0 ? 'Overweight Warning ⚠️' : 'Underweight Warning ⚠️';
                }
                return [
                  `Actual Weight: ${s.avg_weight_g} g`,
                  `Breed Target: ${s.target_weight_g.toFixed(0)} g`,
                  `Deviation: ${devText} (${status})`
                ];
              } else if (ctx.datasetIndex === 3) {
                return `Standard Target: ${ctx.parsed.y.toFixed(0)} g`;
              }
              return `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(0)} g`;
            }
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

const exportCSV = () => {
  if (samples.value.length === 0) return

  const headers = [
    'Date',
    'Avg Weight (g)',
    'Sample Size',
    'Daily Gain (g)',
    'Notes'
  ]

  const sorted = [...samples.value].sort((a, b) => new Date(a.date) - new Date(b.date))

  const rows = sorted.map((s, i) => {
    const prev = i > 0 ? sorted[i - 1] : null
    const dailyGain = prev && s.avg_weight_g && prev.avg_weight_g
      ? (s.avg_weight_g - prev.avg_weight_g).toFixed(1)
      : '—'
    return [
      s.date,
      s.avg_weight_g?.toFixed(1) ?? '—',
      s.sample_size ?? '—',
      dailyGain,
      s.notes ?? ''
    ]
  })

  const csvString = [headers.join(','), ...rows.map(r => r.map(v => `"${v}"`).join(','))].join('\n')
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `AgriSense_Batch_${selectedBatchId.value}_Growth_Report.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
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
  if (Math.abs(dev) > 10) return 'text-status-danger font-bold animate-pulse'
  if (Math.abs(dev) > 5) return 'text-amber-600 dark:text-amber-400 font-bold'
  return 'text-emerald-600 dark:text-emerald-450 font-bold'
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
