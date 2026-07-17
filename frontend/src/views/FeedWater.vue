<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ $t('feed.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          {{ $t('feed.subtitle') }}
          <span v-if="store.activeBatch" class="font-bold text-gray-700 dark:text-gray-300">Batch #{{ store.activeBatch.id }} · {{ store.activeBatch.breed }}</span>
          <span v-else class="italic text-gray-450">{{ $t('feed.no_active') }}</span>
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Replaced with custom AgriSelect -->
        <div class="w-48">
          <AgriSelect
            v-model="selectedBatchId"
            :options="batchOptions"
            :placeholder="$t('feed.select_batch')"
            @change="onBatchChange"
          />
        </div>
        <AgriButton
          variant="primary"
          icon="add"
          :disabled="!selectedBatchId"
          @click="showLogModal = true"
        >{{ $t('feed.log_reading') }}</AgriButton>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">opacity</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">{{ $t('feed.select_view') }}</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ $t('feed.tracked_desc') }}</p>
    </div>

    <template v-else>

      <!-- ─── Summary KPIs (Staggered load) ─── -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="animate-fade-in-up delay-100">
          <AgriStatCard
            :label="$t('feed.total_readings')"
            :value="readings.length"
            icon="bar_chart"
            icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500"
            :loading="tableLoading"
            class="h-full"
          />
        </div>
        <div class="animate-fade-in-up delay-150">
          <AgriStatCard
            :label="$t('feed.latest_feed')"
            :value="readings.length > 0 ? readings[0].feed_kg : 0"
            :decimals="1"
            suffix=" kg"
            icon="restaurant"
            icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450"
            :loading="tableLoading"
            class="h-full"
          />
        </div>
        <div class="animate-fade-in-up delay-200">
          <AgriStatCard
            :label="$t('feed.latest_water')"
            :value="readings.length > 0 ? readings[0].water_litres : 0"
            :decimals="1"
            suffix=" L"
            icon="water_drop"
            icon-color-class="bg-cyan-50 dark:bg-cyan-950/40 text-cyan-500"
            :loading="tableLoading"
            class="h-full"
          />
        </div>
        <div class="animate-fade-in-up delay-250">
          <AgriStatCard
            :label="$t('feed.flagged_readings')"
            :value="flaggedCount"
            icon="warning"
            :icon-color-class="flaggedCount > 0 ? 'bg-red-50 dark:bg-red-950/40 text-red-500' : 'bg-gray-50 dark:bg-darkbg-100 text-gray-400'"
            :trend="flaggedCount > 0 ? $t('feed.review_anomalies') : $t('feed.optimal')"
            :trend-direction="flaggedCount > 0 ? 'up' : 'neutral'"
            :trend-good="flaggedCount === 0"
            :loading="tableLoading"
            class="h-full"
            :class="{ 'border-red-250 dark:border-red-900/40 animate-pulse-glow': flaggedCount > 0 }"
          />
        </div>
      </div>

      <!-- ─── Chart Panel ─── -->
      <AgriCard class="animate-fade-in-up delay-300" padding="none">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">show_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('feed.consumption_trends') }}</h2>
          </div>
          <div class="flex items-center gap-3 text-[10px] font-bold uppercase tracking-wider">
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-primary-500"></span> <span class="text-gray-400">{{ $t('feed.feed') }}</span></span>
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-blue-500"></span> <span class="text-gray-400">{{ $t('feed.water') }}</span></span>
            <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-sm bg-primary-300/40 border border-primary-300"></span> <span class="text-gray-400">{{ $t('feed.avg_7d') }}</span></span>
          </div>
        </template>

        <div v-if="chartLoading" class="h-72 flex items-center justify-center">
          <span class="material-icons-outlined text-2xl text-primary-500 animate-spin">sync</span>
        </div>
        <div v-else-if="summaryData.length < 2" class="h-72 flex flex-col items-center justify-center text-sm text-gray-400 dark:text-gray-500 p-6 text-center">
          <span class="material-icons-outlined text-3xl mb-2 text-gray-300 dark:text-gray-700">timeline</span>
          <p class="font-bold text-gray-700 dark:text-gray-300">{{ $t('feed.insufficient_data') }}</p>
          <p class="text-xs mt-1">{{ $t('feed.need_at_least_2') }}</p>
        </div>
        <div v-else class="p-4">
          <canvas ref="chartCanvas" class="w-full" style="height: 280px;"></canvas>
        </div>
      </AgriCard>

      <!-- ─── Readings Table ─── -->
      <AgriCard class="animate-fade-in-up delay-350" padding="none">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">table_chart</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('feed.all_readings') }}</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ readings.length }} {{ $t('feed.entries') }}</span>
          </div>
          <div v-if="readings.length > 0" class="flex items-center gap-2">
            <button
              @click="exportCSV"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-50 dark:hover:bg-darkbg-100 rounded-lg border border-gray-250 dark:border-gray-800 transition-all shadow-sm shrink-0"
              title="Download CSV"
            >
              <span class="material-icons-outlined text-sm">download</span>
              <span>{{ $t('feed.export_csv') }}</span>
            </button>
            <button
              @click="printLedger"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-50 dark:hover:bg-darkbg-100 rounded-lg border border-gray-250 dark:border-gray-800 transition-all shadow-sm shrink-0"
              title="Print PDF Report"
            >
              <span class="material-icons-outlined text-sm">print</span>
              <span>{{ $t('feed.print_ledger') }}</span>
            </button>
          </div>
        </template>

        <AgriTable
          :headers="tableHeaders"
          :items="enrichedReadings"
          :loading="tableLoading"
          striped
          class="border-none shadow-none rounded-none"
        >
          <template #date="{ item }">
            <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ formatDate(item.date) }}</span>
          </template>

          <template #feed_kg="{ item }">
            <span class="font-mono font-bold text-gray-900 dark:text-white">{{ item.feed_kg?.toFixed(1) }}</span>
          </template>

          <template #water_litres="{ item }">
            <span class="font-mono font-bold text-gray-900 dark:text-white">{{ item.water_litres?.toFixed(1) }}</span>
          </template>

          <template #mortality_count="{ item }">
            <span class="font-mono font-bold text-status-danger">{{ item.mortality_count || '0' }}</span>
          </template>

          <template #_feedDevPct="{ item }">
            <span class="font-mono text-xs font-bold" :class="getDeviationClass(item._feedDevPct)">
              {{ item._feedDevPct !== null ? (item._feedDevPct >= 0 ? '+' : '') + item._feedDevPct.toFixed(1) + '%' : '—' }}
            </span>
          </template>

          <template #status="{ item }">
            <div class="flex justify-center">
              <AgriBadge
                :variant="item.flagged_abnormal ? 'warning' : 'success'"
                :icon="item.flagged_abnormal ? 'warning' : 'check'"
                :pulse="item.flagged_abnormal"
              >
                {{ item.flagged_abnormal ? 'Flagged' : 'Normal' }}
              </AgriBadge>
            </div>
          </template>

          <template #actions="{ item }">
            <div class="flex justify-end gap-3">
              <button @click="editReading(item)" class="text-gray-400 hover:text-primary-500 transition-colors" title="Edit">
                <span class="material-icons-outlined text-[16px] block">edit</span>
              </button>
              <button @click="deleteReading(item.id)" class="text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                <span class="material-icons-outlined text-[16px] block">delete_outline</span>
              </button>
            </div>
          </template>
        </AgriTable>
      </AgriCard>
    </template>

    <!-- ─── Log Reading Modal (AgriModal) ─── -->
    <AgriModal
      :show="showLogModal"
      :title="editingReadingId ? $t('feed.edit_log') : $t('feed.log_daily')"
      @close="closeModal"
    >
      <form @submit.prevent="submitReading" class="space-y-4">
        <!-- Date input -->
        <AgriInput
          v-model="form.date"
          type="date"
          :label="$t('feed.reading_date')"
          required
          icon="calendar_today"
        />

        <div class="grid grid-cols-3 gap-4">
          <!-- Feed Input -->
          <AgriInput
            v-model.number="form.feed_kg"
            type="number"
            step="0.1"
            min="0"
            label="Feed (kg)"
            required
            placeholder="e.g. 125"
            icon="restaurant"
          />
          <!-- Water Input -->
          <AgriInput
            v-model.number="form.water_litres"
            type="number"
            step="0.1"
            min="0"
            label="Water (L)"
            required
            placeholder="e.g. 210"
            icon="water_drop"
          />
          <!-- Mortality Input -->
          <AgriInput
            v-model.number="form.mortality_count"
            type="number"
            min="0"
            :label="$t('feed.mortality')"
            required
            placeholder="0"
            icon="warning"
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
          >{{ $t('feed.cancel') }}</AgriButton>
          <AgriButton
            type="submit"
            variant="primary"
            class="flex-1"
            :loading="submitting"
          >
            {{ editingReadingId ? $t('feed.save_changes') : $t('feed.save_reading') }}
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
const readings = ref([])
const summaryData = ref([])
const tableLoading = ref(false)
const chartLoading = ref(false)
const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)
const editingReadingId = ref(null)

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
  mortality_count: 0
})

// ── Computed ──────────────────────────────
const flaggedCount = computed(() => readings.value.filter(r => r.flagged_abnormal).length)

const batchOptions = computed(() => {
  return store.batchesList.map(b => ({
    label: `#${b.id} — ${b.breed} (${b.status})`,
    value: b.id
  }))
})

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

const tableHeaders = computed(() => [
  { text: t('feed.date'), value: 'date', align: 'left' },
  { text: t('feed.feed_kg'), value: 'feed_kg', align: 'right' },
  { text: t('feed.water_l'), value: 'water_litres', align: 'right' },
  { text: t('feed.mortality'), value: 'mortality_count', align: 'right' },
  { text: t('feed.feed_delta'), value: '_feedDevPct', align: 'right' },
  { text: t('feed.status'), value: 'status', align: 'center' },
  { text: t('feed.actions'), value: 'actions', align: 'right' }
])

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
          borderColor: '#2d6a4f',
          backgroundColor: 'rgba(45, 106, 79, 0.08)',
          borderWidth: 2,
          tension: 0.35,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: '#2d6a4f',
        },
        {
          label: 'Water (L)',
          data: data.map(d => d.water_litres),
          borderColor: '#219ebc',
          backgroundColor: 'rgba(33, 158, 188, 0.06)',
          borderWidth: 2,
          tension: 0.35,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: '#219ebc',
        },
        {
          label: 'Feed 7d Avg',
          data: data.map(d => d.feed_rolling_avg_7d),
          borderColor: 'rgba(45, 106, 79, 0.4)',
          borderWidth: 1.5,
          borderDash: [6, 3],
          tension: 0.4,
          fill: false,
          pointRadius: 0,
        },
        {
          label: 'Water 7d Avg',
          data: data.map(d => d.water_rolling_avg_7d),
          borderColor: 'rgba(33, 158, 188, 0.35)',
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
const editReading = (r) => {
  editingReadingId.value = r.id
  form.value = {
    date: r.date,
    feed_kg: r.feed_kg,
    water_litres: r.water_litres,
    mortality_count: r.mortality_count || 0
  }
  formError.value = ''
  formSuccess.value = false
  showLogModal.value = true
}

const deleteReading = async (id) => {
  if (!confirm('Are you sure you want to delete this reading?')) return
  try {
    await api.readings.delete(id)
    await loadAll()
    toast.success('Reading deleted successfully')
  } catch (err) {
    alert('Failed to delete reading: ' + err.message)
  }
}

const submitReading = async () => {
  formError.value = ''
  formSuccess.value = false
  submitting.value = true

  try {
    const payload = {
      date: form.value.date,
      feed_kg: Number(form.value.feed_kg),
      water_litres: Number(form.value.water_litres),
      mortality_count: form.value.mortality_count === '' || form.value.mortality_count === null ? 0 : Number(form.value.mortality_count)
    }

    if (editingReadingId.value) {
      await api.readings.update(editingReadingId.value, payload)
      toast.success('Daily reading updated')
    } else {
      await api.readings.create({
        batch_id: selectedBatchId.value,
        ...payload
      })
      toast.success('Daily reading logged')
    }
    formSuccess.value = true

    await loadAll()
    closeModal()
  } catch (err) {
    formError.value = err.message || 'Failed to save reading.'
  } finally {
    submitting.value = false
  }
}

const closeModal = () => {
  showLogModal.value = false
  editingReadingId.value = null
  formError.value = ''
  formSuccess.value = false
  form.value = {
    date: getTodayString(),
    feed_kg: null,
    water_litres: null,
    mortality_count: 0
  }
}

// ── Helpers ──────────────────────────────────
const getCohortAgeAtDate = (readingDateStr) => {
  if (!store.activeBatch?.start_date) return '—'
  const start = new Date(store.activeBatch.start_date)
  const readingDate = new Date(readingDateStr)
  start.setHours(0,0,0,0)
  readingDate.setHours(0,0,0,0)
  const diffTime = readingDate - start
  const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return days >= 0 ? days : 0
}

const exportCSV = () => {
  if (summaryData.value.length === 0) return
  
  const headers = [
    'Date',
    'Cohort Age (Days)',
    'Feed Consumed (kg)',
    'Water Consumed (Liters)',
    'Daily Mortality (Birds)',
    'Cumulative Mortality (Birds)',
    'Feed Conversion Ratio (FCR)',
    '7d Feed Avg (kg)',
    '7d Water Avg (Liters)',
    'Feed Deviation (%)',
    'Water Deviation (%)'
  ]

  const rows = summaryData.value.map(row => {
    const age = getCohortAgeAtDate(row.date)
    const fcrVal = row.feed_conversion_ratio ? row.feed_conversion_ratio.toFixed(2) : '—'
    const feedDev = row.feed_deviation_pct !== null ? `${row.feed_deviation_pct > 0 ? '+' : ''}${row.feed_deviation_pct}` : '—'
    const waterDev = row.water_deviation_pct !== null ? `${row.water_deviation_pct > 0 ? '+' : ''}${row.water_deviation_pct}` : '—'
    
    return [
      row.date,
      age,
      row.feed_kg.toFixed(1),
      row.water_litres.toFixed(1),
      row.mortality_count || 0,
      row.cumulative_mortality || 0,
      fcrVal,
      row.feed_rolling_avg_7d.toFixed(1),
      row.water_rolling_avg_7d.toFixed(1),
      feedDev,
      waterDev
    ]
  })

  const csvString = [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `AgriSense_Batch_${selectedBatchId.value}_Telemetry_Report.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const printLedger = () => {
  if (summaryData.value.length === 0) return
  
  const printWindow = window.open('', '_blank')
  
  let tableRowsHtml = ''
  summaryData.value.forEach(row => {
    const age = getCohortAgeAtDate(row.date)
    const fcrVal = row.feed_conversion_ratio ? row.feed_conversion_ratio.toFixed(2) : '—'
    const statusText = row.flagged_abnormal ? 'FLAGGED' : 'NORMAL'
    const statusColor = row.flagged_abnormal ? 'color: #dc2626; font-weight: bold;' : 'color: #16a34a;'
    
    tableRowsHtml += `
      <tr style="border-bottom: 1px solid #e5e7eb;">
        <td style="padding: 10px 8px; text-align: left;">${formatDate(row.date)}</td>
        <td style="padding: 10px 8px; text-align: center;">${age}</td>
        <td style="padding: 10px 8px; text-align: right;">${row.feed_kg.toFixed(1)}</td>
        <td style="padding: 10px 8px; text-align: right;">${row.water_litres.toFixed(1)}</td>
        <td style="padding: 10px 8px; text-align: center;">${row.mortality_count || 0}</td>
        <td style="padding: 10px 8px; text-align: center;">${row.cumulative_mortality || 0}</td>
        <td style="padding: 10px 8px; text-align: center; font-weight: bold;">${fcrVal}</td>
        <td style="padding: 10px 8px; text-align: center; ${statusColor}">${statusText}</td>
      </tr>
    `
  })

  const batchInfo = store.activeBatch 
    ? `Batch #${store.activeBatch.id} - ${store.activeBatch.breed} (${store.activeBatch.bird_count} birds)` 
    : 'All Batches'
  const dateRange = summaryData.value.length > 0 
    ? `From ${formatDate(summaryData.value[0].date)} to ${formatDate(summaryData.value[summaryData.value.length - 1].date)}` 
    : ''

  printWindow.document.write(`
    \x3chtml\x3e
      \x3chead\x3e
        \x3ctitle\x3eAgriSense AI - Telemetry Ledger Report\x3c/title\x3e
        \x3cstyle\x3e
          body { font-family: 'Inter', system-ui, -apple-system, sans-serif; color: #111827; padding: 25px; line-height: 1.5; background-color: #fff; }
          .header { border-bottom: 2px solid #10b981; padding-bottom: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
          .logo-area { display: flex; flex-direction: column; }
          .logo { font-size: 26px; font-weight: 800; color: #059669; letter-spacing: -0.025em; }
          .logo span { color: #10b981; }
          .subtitle { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; margin-top: 2px; }
          .meta-area { font-size: 13px; color: #374151; text-align: right; line-height: 1.6; }
          table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }
          th { background-color: #f9fafb; padding: 10px 8px; font-weight: 700; border-bottom: 2px solid #e5e7eb; color: #4b5563; }
          td { border-bottom: 1px solid #e5e7eb; color: #1f2937; }
          .footer { margin-top: 40px; border-top: 1px solid #e5e7eb; padding-top: 15px; font-size: 11px; color: #9ca3af; text-align: center; }
          @media print {
            body { padding: 0; }
            button { display: none; }
          }
        \x3c/style\x3e
      \x3c/head\x3e
      \x3cbody\x3e
        <div class="header">
          <div class="logo-area">
            <div class="logo">AgriSense <span>AI</span></div>
            <div class="subtitle">Poultry Ledger Report</div>
          </div>
          <div class="meta-area">
            <strong>Cohort:</strong> \${batchInfo}<br>
            <strong>Date Range:</strong> \${dateRange}<br>
            <strong>Report Date:</strong> \${new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th style="text-align: left;">Date</th>
              <th style="text-align: center;">Age (Days)</th>
              <th style="text-align: right;">Feed (kg)</th>
              <th style="text-align: right;">Water (L)</th>
              <th style="text-align: center;">Mortality (Birds)</th>
              <th style="text-align: center;">Cumulative</th>
              <th style="text-align: center;">FCR</th>
              <th style="text-align: center;">Status</th>
            </tr>
          </thead>
          <tbody>
            \${tableRowsHtml}
          </tbody>
        </table>
        <div class="footer">
          Generated automatically by AgriSense AI Precision Poultry System &copy; 2026. All rights reserved.
        </div>
        \x3cscript\x3e
          window.onload = function() {
            setTimeout(function() {
              window.print();
              window.close();
            }, 300);
          }
        \x3c/script\x3e
      \x3c/body\x3e
    \x3c/html\x3e
  `)
  printWindow.document.close()
}

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
  if (Math.abs(pct) > 20) return 'text-status-danger'
  if (Math.abs(pct) > 10) return 'text-status-warning'
  return 'text-gray-500 dark:text-gray-400'
}

// Staggered delay helper
const getStaggerDelayClass = (idx) => {
  const delays = [50, 100, 150, 200, 250, 300]
  return `delay-${delays[idx] || 300}`
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
