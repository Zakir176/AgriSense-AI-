<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex items-start justify-between animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ $t('dashboard.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          {{ $t('dashboard.subtitle') }}
          <span class="font-semibold text-gray-700 dark:text-gray-300">{{ store.currentFarm?.name || 'Prime Nest Poultry' }}</span>
        </p>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1.5 text-xs font-semibold text-gray-550 dark:text-gray-400 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl px-3.5 py-2 shadow-xs select-none">
          <span class="relative flex h-1.5 w-1.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-450 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
          </span>
          {{ $t('dashboard.live_monitoring') }}
        </div>
        <AgriButton
          variant="outline"
          size="sm"
          icon="refresh"
          :loading="loading"
          @click="refreshAll"
        >{{ $t('dashboard.refresh') }}</AgriButton>
      </div>
    </div>

    <!-- ─── KPI Cards (Staggered Fade-in) ─── -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div class="animate-fade-in-up delay-50">
        <AgriStatCard
          :label="$t('dashboard.active_batches')"
          :value="activeBatchCount"
          icon="layers"
          icon-color-class="bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400"
          :loading="loading"
          :subtext="`${store.batchesList.length} total batch${store.batchesList.length !== 1 ? 'es' : ''} on farm`"
          class="h-full"
        />
      </div>

      <div class="animate-fade-in-up delay-100">
        <AgriStatCard
          :label="$t('dashboard.total_birds')"
          :value="liveCountValue"
          icon="egg"
          icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400"
          :loading="loading"
          :trend="populationTrendText"
          :trend-direction="populationTrendDirection"
          :trend-good="populationTrendGood"
          :subtext="populationSubtext"
          class="h-full"
          :class="{ 'border-red-250 dark:border-red-900/40 animate-pulse-glow': hasPopulationAlert }"
        />
      </div>

      <!-- Active Alerts Card (Pulsing critical warning if counts exist) -->
      <div class="animate-fade-in-up delay-150">
        <AgriStatCard
          :label="$t('dashboard.active_alerts')"
          :value="unackAlerts.length"
          icon="notifications_active"
          :icon-color-class="unackAlerts.length > 0 ? 'bg-red-50 dark:bg-red-950/40 text-red-500 dark:text-red-400' : 'bg-gray-50 dark:bg-darkbg-100 text-gray-400 dark:text-gray-500'"
          :loading="loading"
          :trend="unackAlerts.length > 0 ? $t('dashboard.action_required') : $t('dashboard.all_clear')"
          :trend-direction="unackAlerts.length > 0 ? 'up' : 'neutral'"
          :trend-good="unackAlerts.length === 0"
          :subtext="unackAlerts.length > 0 ? $t('dashboard.exceptions_detected') : $t('dashboard.systems_normal')"
          class="h-full"
          :class="{ 'border-red-250 dark:border-red-900/40 animate-pulse-glow': unackAlerts.length > 0 }"
        />
      </div>

      <div class="animate-fade-in-up delay-200">
        <AgriStatCard
          :label="$t('dashboard.batch_age')"
          :value="batchAgeDays !== null ? batchAgeDays : 0"
          :prefix="$t('dashboard.day') + ' '"
          icon="calendar_today"
          icon-color-class="bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400"
          :loading="loading"
          :subtext="store.activeBatch ? `Started ${formatDate(store.activeBatch.start_date)}` : $t('dashboard.no_active_batch')"
          class="h-full"
        />
      </div>
    </div>

    <!-- ─── Body grid: Alerts + Batch Info ─── -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-5">

      <!-- Alert Queue (left / wide) -->
      <AgriCard id="dashboard-alerts-card" class="xl:col-span-2 animate-fade-in-up delay-250" padding="none" glass>
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">inbox</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('dashboard.active_alerts_queue') }}</h2>
            <AgriBadge
              v-if="unackAlerts.length > 0"
              variant="critical"
              pulse
            >
              {{ unackAlerts.length }} {{ $t('dashboard.unresolved') }}
            </AgriBadge>
          </div>
          <AgriButton
            v-if="unackAlerts.length > 0"
            variant="ghost"
            size="sm"
            :loading="ackLoading"
            @click="acknowledgeAll"
          >{{ $t('dashboard.ack_all') }}</AgriButton>
        </template>

        <!-- Skeleton while loading -->
        <div v-if="loading" class="p-5 space-y-3">
          <AgriSkeleton v-for="n in 3" :key="n" type="card" height="h-14" />
        </div>

        <!-- Empty state -->
        <div v-else-if="unackAlerts.length === 0" class="flex flex-col items-center justify-center py-14 text-center px-6">
          <div class="h-12 w-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 flex items-center justify-center mb-3">
            <span class="material-icons-outlined text-emerald-500 dark:text-emerald-400 text-2xl">check_circle</span>
          </div>
          <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">All clear</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ $t('dashboard.no_alerts_desc') }}</p>
        </div>

        <!-- Alert rows -->
        <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
          <div
            v-for="(alert, index) in unackAlerts.slice(0, 8)"
            :key="alert.id"
            class="flex items-start gap-3 px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition animate-fade-in-up active-press"
            :class="getStaggerDelayClass(index)"
          >
            <div class="mt-0.5 shrink-0 h-7 w-7 rounded-lg flex items-center justify-center"
              :class="[alertIconBg(alert.alert_type), { 'animate-pulse-glow': alert.severity === 'critical' }]">
              <span class="material-icons-outlined text-[14px]" :class="alertIconColor(alert.alert_type)">
                {{ alertIcon(alert.alert_type) }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5">
                <p class="text-sm font-bold text-gray-800 dark:text-gray-200 leading-snug">{{ alert.message }}</p>
                <AgriBadge v-if="alert.severity === 'critical'" variant="critical" size="xs">Critical</AgriBadge>
              </div>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ formatDateTime(alert.created_at) }} · Batch #{{ alert.batch_id }}</p>
            </div>
            <AgriButton
              variant="outline"
              size="sm"
              @click="acknowledgeAlert(alert.id)"
            >{{ $t('dashboard.ack') }}</AgriButton>
          </div>
          <div v-if="unackAlerts.length > 8" class="px-5 py-3.5 text-xs text-gray-450 dark:text-gray-500 text-center font-semibold">
            +{{ unackAlerts.length - 8 }} {{ $t('dashboard.more_alerts') }}
          </div>
        </div>
      </AgriCard>

      <!-- Right column: Batch overview + quick stats -->
      <div class="flex flex-col gap-5">

        <!-- Active Batch Card -->
        <AgriCard class="animate-fade-in-up delay-300" padding="none" glass>
          <template #header>
            <div class="flex items-center gap-2">
              <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">inventory_2</span>
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('dashboard.active_cohort') }}</h2>
            </div>
          </template>
          
          <template v-if="loading">
            <div class="p-5 space-y-3">
              <AgriSkeleton v-for="n in 3" :key="n" type="card" height="h-14" />
            </div>
          </template>
          <div v-else-if="!store.activeBatch" class="px-5 py-10 text-center text-sm text-gray-400 dark:text-gray-500">
            {{ $t('dashboard.no_batch_registered') }} <router-link to="/batches" class="text-primary-600 dark:text-primary-400 font-semibold">{{ $t('dashboard.create_one') }}</router-link>
          </div>
          <div v-else class="px-5 py-4.5 space-y-3.5 text-sm">
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400 font-medium">{{ $t('dashboard.batch_id') }}</span>
              <span class="font-bold text-gray-900 dark:text-white">#{{ store.activeBatch.id }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400 font-medium">{{ $t('dashboard.breed_type') }}</span>
              <span class="font-bold text-gray-900 dark:text-white">{{ store.activeBatch.breed || '—' }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400 font-medium">{{ $t('dashboard.original_flock_size') }}</span>
              <span class="font-bold text-gray-900 dark:text-white">{{ store.activeBatch.bird_count?.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400 font-medium">{{ $t('dashboard.register_date') }}</span>
              <span class="font-bold text-gray-900 dark:text-white">{{ formatDate(store.activeBatch.start_date) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400 font-medium">{{ $t('dashboard.status') }}</span>
              <AgriBadge :variant="store.activeBatch.status === 'active' ? 'active' : 'info'" pulse>
                {{ store.activeBatch.status }}
              </AgriBadge>
            </div>
            <router-link
              to="/batches"
              class="flex items-center justify-center gap-1.5 w-full mt-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-800 text-xs font-bold text-gray-600 dark:text-gray-450 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition duration-150"
            >
              {{ $t('dashboard.manage_cohorts') }}
              <span class="material-icons-outlined text-[14px]">arrow_forward</span>
            </router-link>
          </div>
        </AgriCard>

        <!-- Quick Links -->
        <AgriCard id="dashboard-quick-links" class="animate-fade-in-up delay-350" glass>
          <p class="text-xs font-bold text-gray-550 dark:text-gray-400 uppercase tracking-wider mb-3">{{ $t('dashboard.quick_links') }}</p>
          <div class="grid grid-cols-2 gap-2">
            <router-link
              v-for="ql in quickLinks"
              :key="ql.path"
              :to="ql.path"
              class="flex flex-col items-center gap-2 p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 hover:border-primary-200 dark:hover:border-primary-900 hover:bg-primary-50/40 dark:hover:bg-primary-950/20 active-press transition-all duration-150 group text-center"
            >
              <div class="h-9 w-9 rounded-xl bg-gray-50 dark:bg-darkbg-100 flex items-center justify-center group-hover:bg-primary-50 dark:group-hover:bg-primary-950/50 transition">
                <span class="material-icons-outlined text-[20px] text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition">{{ ql.icon }}</span>
              </div>
              <span class="text-[11px] font-bold text-gray-600 dark:text-gray-400 group-hover:text-primary-700 dark:group-hover:text-primary-300 transition leading-tight">{{ ql.label }}</span>
            </router-link>
          </div>
        </AgriCard>
      </div>
    </div>

    <!-- ─── Bottom: Recent Readings + All Batches Status ─── -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-5">

      <!-- Recent Feed/Water Readings -->
      <AgriCard class="animate-fade-in-up delay-400" padding="none" glass>
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">opacity</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('dashboard.recent_logs') }}</h2>
          </div>
          <router-link to="/readings" class="text-xs font-bold text-primary-600 dark:text-primary-400 hover:text-primary-500 transition">{{ $t('dashboard.view_all') }}</router-link>
        </template>

        <!-- Using AgriTable component -->
        <AgriTable
          :headers="readingsHeaders"
          :items="recentReadings"
          :loading="loading"
          striped
          class="border-none shadow-none rounded-none"
        >
          <!-- Custom renderers -->
          <template #date="{ item }">
            <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ formatDate(item.date) }}</span>
          </template>
          
          <template #feed_kg="{ item }">
            <span class="font-mono text-gray-900 dark:text-white font-bold">{{ item.feed_kg?.toFixed(1) }}</span>
          </template>

          <template #water_litres="{ item }">
            <span class="font-mono text-gray-900 dark:text-white font-bold">{{ item.water_litres?.toFixed(1) }}</span>
          </template>

          <template #status="{ item }">
            <span class="flex justify-end">
              <AgriBadge
                :variant="item.flagged_abnormal ? 'warning' : 'success'"
                :icon="item.flagged_abnormal ? 'warning' : 'check'"
              >
                {{ item.flagged_abnormal ? $t('dashboard.flagged') : $t('dashboard.normal') }}
              </AgriBadge>
            </span>
          </template>
        </AgriTable>
      </AgriCard>

      <!-- All Batches Status Table -->
      <AgriCard class="animate-fade-in-up delay-500" padding="none" glass>
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">layers</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('dashboard.all_cohorts') }}</h2>
          </div>
          <router-link to="/batches" class="text-xs font-bold text-primary-600 dark:text-primary-400 hover:text-primary-500 transition">{{ $t('dashboard.manage') }}</router-link>
        </template>

        <!-- Using AgriTable component -->
        <AgriTable
          :headers="batchesHeaders"
          :items="store.batchesList.slice(0, 7)"
          :loading="loading"
          striped
          class="border-none shadow-none rounded-none"
        >
          <template #breed="{ item }">
            <div>
              <div class="font-bold text-gray-900 dark:text-white text-xs">#{{ item.id }}</div>
              <div class="text-gray-450 dark:text-gray-500 text-[11px] font-medium">{{ item.breed || '—' }}</div>
            </div>
          </template>

          <template #bird_count="{ item }">
            <span class="font-mono font-bold text-gray-900 dark:text-white text-xs">{{ item.bird_count?.toLocaleString() }}</span>
          </template>

          <template #age="{ item }">
            <span class="text-xs text-gray-600 dark:text-gray-400 font-semibold">Day {{ batchAge(item.start_date) }}</span>
          </template>

          <template #status="{ item }">
            <span class="flex justify-end">
              <AgriBadge
                :variant="item.status === 'active' ? 'active' : item.status === 'closed' ? 'info' : 'warning'"
                :pulse="item.status === 'active'"
              >
                {{ item.status }}
              </AgriBadge>
            </span>
          </template>
        </AgriTable>
      </AgriCard>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'
import { useAnimations } from '../composables/useAnimations'
import { useI18n } from 'vue-i18n'

// Import premium design system components
import AgriButton from '../components/ui/AgriButton.vue'
import AgriCard from '../components/ui/AgriCard.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriStatCard from '../components/ui/AgriStatCard.vue'
import AgriTable from '../components/ui/AgriTable.vue'
import AgriSkeleton from '../components/ui/AgriSkeleton.vue'

const { getStaggerDelayClass } = useAnimations()
const { t } = useI18n()

const loading = ref(true)
const ackLoading = ref(false)
const recentReadings = ref([])
const unackAlerts = ref([])

// ── Computed KPIs ──────────────────────────────
const activeBatchCount = computed(() =>
  store.batchesList.filter(b => b.status === 'active').length
)

const totalBirds = computed(() =>
  store.batchesList
    .filter(b => b.status === 'active')
    .reduce((sum, b) => sum + (b.bird_count || 0), 0)
)

const cumulativeMortality = computed(() => {
  return recentReadings.value.reduce((sum, r) => sum + (r.mortality_count || 0), 0)
})

const expectedChickenCount = computed(() => {
  if (!store.activeBatch) return 0
  return Math.max(0, store.activeBatch.bird_count - cumulativeMortality.value)
})

const liveCountValue = computed(() => {
  if (store.latestInferenceResult && store.latestInferenceResult.bird_count_est !== null) {
    return store.latestInferenceResult.bird_count_est
  }
  return expectedChickenCount.value
})

const populationTrendText = computed(() => {
  if (!store.latestInferenceResult) return 'Expected'
  const diff = expectedChickenCount.value - store.latestInferenceResult.bird_count_est
  if (diff > 0) return `${diff} Missing`
  return 'Verified'
})

const populationTrendDirection = computed(() => {
  if (store.latestInferenceResult && store.latestInferenceResult.bird_count_est < expectedChickenCount.value) {
    return 'down'
  }
  return 'neutral'
})

const populationTrendGood = computed(() => {
  if (!store.latestInferenceResult) return true
  return store.latestInferenceResult.bird_count_est >= expectedChickenCount.value
})

const populationSubtext = computed(() => {
  if (!store.activeBatch) return t('dashboard.no_active_batch')
  if (store.latestInferenceResult) {
    return `Expected: ${expectedChickenCount.value} · AI Visual: ${store.latestInferenceResult.bird_count_est}`
  }
  return `Expected: ${expectedChickenCount.value} · No recent scan`
})

const hasPopulationAlert = computed(() => {
  return !!(store.latestInferenceResult && store.latestInferenceResult.bird_count_est < expectedChickenCount.value)
})

const batchAgeDays = computed(() => {
  if (!store.activeBatch?.start_date) return null
  return batchAge(store.activeBatch.start_date)
})

// ── Helpers ──────────────────────────────────
const batchAge = (startDate) => {
  if (!startDate) return 0
  const start = new Date(startDate)
  const today = new Date()
  return Math.max(0, Math.floor((today - start) / (1000 * 60 * 60 * 24)))
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

const formatDateTime = (dtStr) => {
  if (!dtStr) return '—'
  const d = new Date(dtStr)
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) + ' ' +
    d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

// ── Table Configuration ───────────────────────
const readingsHeaders = computed(() => [
  { text: t('dashboard.date'), value: 'date', align: 'left' },
  { text: t('dashboard.feed_kg'), value: 'feed_kg', align: 'right' },
  { text: t('dashboard.water_l'), value: 'water_litres', align: 'right' },
  { text: t('dashboard.status'), value: 'status', align: 'right' }
])

const batchesHeaders = computed(() => [
  { text: t('dashboard.id_breed'), value: 'breed', align: 'left' },
  { text: t('dashboard.birds'), value: 'bird_count', align: 'right' },
  { text: t('dashboard.age'), value: 'age', align: 'right' },
  { text: t('dashboard.status'), value: 'status', align: 'right' }
])

// ── Alert helpers ──────────────────────────────
const alertIcon = (type) => {
  const map = {
    feed_deviation: 'restaurant',
    water_deviation: 'water_drop',
    growth_deviation: 'show_chart',
    mortality: 'warning',
    temperature: 'thermostat',
    manual: 'edit_note',
  }
  return map[type] || 'notifications'
}

const alertIconBg = (type) => {
  const warm = ['mortality', 'temperature', 'manual']
  return warm.includes(type)
    ? 'bg-red-50 dark:bg-red-950/40'
    : 'bg-amber-50 dark:bg-amber-950/40'
}

const alertIconColor = (type) => {
  const warm = ['mortality', 'temperature', 'manual']
  return warm.includes(type)
    ? 'text-red-500 dark:text-red-400'
    : 'text-amber-500 dark:text-amber-400'
}

// ── Quick links ──────────────────────────────
const quickLinks = computed(() => [
  { label: t('dashboard.log_feed_water'), path: '/readings', icon: 'opacity' },
  { label: t('dashboard.log_growth'), path: '/growth', icon: 'show_chart' },
  { label: t('dashboard.ai_monitor'), path: '/inference', icon: 'videocam' },
  { label: t('dashboard.medications'), path: '/medications', icon: 'vaccines' },
])

// ── Data fetching ──────────────────────────────
const fetchDashboardData = async () => {
  loading.value = true
  try {
    const alertsData = await api.alerts.list(null, true)
    unackAlerts.value = alertsData

    if (store.activeBatch?.id) {
      const readings = await api.readings.list(store.activeBatch.id)
      recentReadings.value = readings

      // Load latest visual detection scan
      const clips = await api.inference.list(store.activeBatch.id)
      if (clips && clips.length > 0) {
        store.latestInferenceResult = clips[0].inference_result
      } else {
        store.latestInferenceResult = null
      }
    } else {
      recentReadings.value = []
      store.latestInferenceResult = null
    }
  } catch (err) {
    console.error('Dashboard fetch error:', err)
  } finally {
    loading.value = false
  }
}

const refreshAll = () => fetchDashboardData()

const acknowledgeAlert = async (alertId) => {
  try {
    await api.alerts.acknowledge(alertId)
    unackAlerts.value = unackAlerts.value.filter(a => a.id !== alertId)
  } catch (err) {
    console.error('Ack error:', err)
  }
}

const acknowledgeAll = async () => {
  ackLoading.value = true
  try {
    await Promise.all(unackAlerts.value.map(a => api.alerts.acknowledge(a.id)))
    unackAlerts.value = []
  } catch (err) {
    console.error('Ack all error:', err)
  } finally {
    ackLoading.value = false
  }
}

watch(() => store.activeBatch, (newVal) => {
  if (newVal) {
    fetchDashboardData()
  }
})

onMounted(() => {
  fetchDashboardData()
})
</script>
