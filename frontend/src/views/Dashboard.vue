<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Farm Dashboard</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Real-time indicators and operational summary for
          <span class="font-semibold text-gray-700 dark:text-gray-300">{{ store.currentFarm?.name || 'Prime Nest Poultry' }}</span>
        </p>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl px-3 py-2">
          <span class="relative flex h-1.5 w-1.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
          </span>
          Live
        </div>
        <button
          @click="refreshAll"
          :disabled="loading"
          class="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl px-3 py-2 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition disabled:opacity-50"
        >
          <span class="material-icons-outlined text-[15px]" :class="loading ? 'animate-spin' : ''">refresh</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- ─── KPI Cards ─── -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">

      <!-- Active Batches -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm group hover:shadow-md transition-all duration-200">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Active Batches</span>
          <div class="h-8 w-8 rounded-xl bg-primary-50 dark:bg-primary-950/50 flex items-center justify-center">
            <span class="material-icons-outlined text-primary-600 dark:text-primary-400 text-[17px]">layers</span>
          </div>
        </div>
        <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
          {{ loading ? '—' : activeBatchCount }}
        </div>
        <div class="mt-1 text-xs text-gray-500 dark:text-gray-500">
          {{ store.batchesList.length }} total batch{{ store.batchesList.length !== 1 ? 'es' : '' }} on farm
        </div>
      </div>

      <!-- Total Birds -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm group hover:shadow-md transition-all duration-200">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Birds</span>
          <div class="h-8 w-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 flex items-center justify-center">
            <span class="material-icons-outlined text-emerald-600 dark:text-emerald-400 text-[17px]">egg</span>
          </div>
        </div>
        <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
          {{ loading ? '—' : totalBirds.toLocaleString() }}
        </div>
        <div class="mt-1 text-xs text-gray-500 dark:text-gray-500">
          <span v-if="store.activeBatch">
            Active: <b class="text-gray-700 dark:text-gray-300">{{ store.activeBatch.bird_count?.toLocaleString() }}</b> · {{ store.activeBatch.breed }}
          </span>
          <span v-else>No active batch</span>
        </div>
      </div>

      <!-- Unacknowledged Alerts -->
      <div
        class="bg-white dark:bg-darkbg-50 border rounded-2xl p-5 shadow-sm group hover:shadow-md transition-all duration-200"
        :class="unackAlerts.length > 0
          ? 'border-red-200 dark:border-red-900/40'
          : 'border-gray-200 dark:border-gray-800'"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-bold uppercase tracking-wider"
            :class="unackAlerts.length > 0 ? 'text-red-500 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'">
            Active Alerts
          </span>
          <div class="h-8 w-8 rounded-xl flex items-center justify-center"
            :class="unackAlerts.length > 0 ? 'bg-red-50 dark:bg-red-950/40' : 'bg-gray-50 dark:bg-darkbg-100'">
            <span class="material-icons-outlined text-[17px]"
              :class="unackAlerts.length > 0 ? 'text-red-500 dark:text-red-400' : 'text-gray-400 dark:text-gray-500'">
              notifications_active
            </span>
          </div>
        </div>
        <div class="text-3xl font-black tabular-nums"
          :class="unackAlerts.length > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'">
          {{ loading ? '—' : unackAlerts.length }}
        </div>
        <div class="mt-1 text-xs"
          :class="unackAlerts.length > 0 ? 'text-red-400 dark:text-red-500' : 'text-gray-500 dark:text-gray-500'">
          {{ unackAlerts.length > 0 ? 'Requires attention' : 'All clear — no pending alerts' }}
        </div>
      </div>

      <!-- Active Batch Day -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm group hover:shadow-md transition-all duration-200">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Batch Age</span>
          <div class="h-8 w-8 rounded-xl bg-violet-50 dark:bg-violet-950/40 flex items-center justify-center">
            <span class="material-icons-outlined text-violet-600 dark:text-violet-400 text-[17px]">calendar_today</span>
          </div>
        </div>
        <div class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">
          {{ loading ? '—' : (batchAgeDays !== null ? `Day ${batchAgeDays}` : '—') }}
        </div>
        <div class="mt-1 text-xs text-gray-500 dark:text-gray-500">
          <span v-if="store.activeBatch">
            Started {{ formatDate(store.activeBatch.start_date) }}
          </span>
          <span v-else>No active batch</span>
        </div>
      </div>
    </div>

    <!-- ─── Body grid: Alerts + Batch Info ─── -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-5">

      <!-- Alert Queue (left / wide) -->
      <div class="xl:col-span-2 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">inbox</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Active Alerts Queue</h2>
            <span
              v-if="unackAlerts.length > 0"
              class="inline-flex items-center justify-center h-5 min-w-5 px-1.5 rounded-full text-[10px] font-bold bg-red-500 text-white"
            >{{ unackAlerts.length }}</span>
          </div>
          <button
            v-if="unackAlerts.length > 0"
            @click="acknowledgeAll"
            :disabled="ackLoading"
            class="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-500 transition disabled:opacity-50"
          >
            Acknowledge All
          </button>
        </div>

        <!-- Skeleton while loading -->
        <div v-if="loading" class="p-5 space-y-3">
          <div v-for="n in 3" :key="n" class="h-14 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
        </div>

        <!-- Empty state -->
        <div v-else-if="unackAlerts.length === 0" class="flex flex-col items-center justify-center py-14 text-center px-6">
          <div class="h-12 w-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 flex items-center justify-center mb-3">
            <span class="material-icons-outlined text-emerald-500 dark:text-emerald-400 text-2xl">check_circle</span>
          </div>
          <p class="text-sm font-semibold text-gray-700 dark:text-gray-300">All clear</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">No unacknowledged alerts. Daily metrics within normal limits.</p>
        </div>

        <!-- Alert rows -->
        <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
          <div
            v-for="alert in unackAlerts.slice(0, 8)"
            :key="alert.id"
            class="flex items-start gap-3 px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition"
          >
            <div class="mt-0.5 shrink-0 h-7 w-7 rounded-lg flex items-center justify-center"
              :class="alertIconBg(alert.alert_type)">
              <span class="material-icons-outlined text-[14px]" :class="alertIconColor(alert.alert_type)">
                {{ alertIcon(alert.alert_type) }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 dark:text-gray-200 leading-snug">{{ alert.message }}</p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ formatDateTime(alert.created_at) }} · Batch #{{ alert.batch_id }}</p>
            </div>
            <button
              @click="acknowledgeAlert(alert.id)"
              class="shrink-0 text-xs font-semibold text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400 transition px-2 py-1 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-950/30"
            >
              Ack
            </button>
          </div>
          <div v-if="unackAlerts.length > 8" class="px-5 py-3 text-xs text-gray-400 dark:text-gray-500 text-center">
            +{{ unackAlerts.length - 8 }} more alerts not shown
          </div>
        </div>
      </div>

      <!-- Right column: Batch overview + quick stats -->
      <div class="flex flex-col gap-5">

        <!-- Active Batch Card -->
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
          <div class="flex items-center gap-2 px-5 py-4 border-b border-gray-100 dark:border-gray-800">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">inventory_2</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Active Batch</h2>
          </div>
          <div v-if="loading" class="p-5 space-y-2.5">
            <div v-for="n in 4" :key="n" class="h-5 bg-gray-100 dark:bg-gray-800/50 rounded animate-pulse"></div>
          </div>
          <div v-else-if="!store.activeBatch" class="px-5 py-10 text-center text-sm text-gray-400 dark:text-gray-500">
            No active batch. <router-link to="/batches" class="text-primary-600 dark:text-primary-400 font-semibold">Create one →</router-link>
          </div>
          <div v-else class="px-5 py-4 space-y-3 text-sm">
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400">Batch ID</span>
              <span class="font-semibold text-gray-900 dark:text-white">#{{ store.activeBatch.id }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400">Breed</span>
              <span class="font-semibold text-gray-900 dark:text-white">{{ store.activeBatch.breed || '—' }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400">Bird Count</span>
              <span class="font-semibold text-gray-900 dark:text-white">{{ store.activeBatch.bird_count?.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400">Start Date</span>
              <span class="font-semibold text-gray-900 dark:text-white">{{ formatDate(store.activeBatch.start_date) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-500 dark:text-gray-400">Status</span>
              <span
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wide"
                :class="store.activeBatch.status === 'active'
                  ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'"
              >
                <span class="h-1.5 w-1.5 rounded-full"
                  :class="store.activeBatch.status === 'active' ? 'bg-emerald-500' : 'bg-gray-400'"></span>
                {{ store.activeBatch.status }}
              </span>
            </div>
            <router-link
              to="/batches"
              class="flex items-center justify-center gap-1.5 w-full mt-2 py-2 rounded-xl border border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition"
            >
              View all batches
              <span class="material-icons-outlined text-[14px]">arrow_forward</span>
            </router-link>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm p-4">
          <p class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Quick Actions</p>
          <div class="grid grid-cols-2 gap-2">
            <router-link
              v-for="ql in quickLinks"
              :key="ql.path"
              :to="ql.path"
              class="flex flex-col items-center gap-1.5 p-3 rounded-xl border border-gray-100 dark:border-gray-800 hover:border-primary-200 dark:hover:border-primary-900 hover:bg-primary-50/50 dark:hover:bg-primary-950/20 transition group text-center"
            >
              <span class="material-icons-outlined text-[20px] text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition">{{ ql.icon }}</span>
              <span class="text-[11px] font-semibold text-gray-600 dark:text-gray-400 group-hover:text-primary-700 dark:group-hover:text-primary-300 transition leading-tight">{{ ql.label }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Bottom: Recent Readings + All Batches Status ─── -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-5">

      <!-- Recent Feed/Water Readings -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">opacity</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Recent Feed & Water Logs</h2>
          </div>
          <router-link to="/readings" class="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-500 transition">View all</router-link>
        </div>

        <div v-if="loading" class="p-5 space-y-2.5">
          <div v-for="n in 4" :key="n" class="h-10 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="recentReadings.length === 0" class="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
          <span class="material-icons-outlined text-3xl block mb-2 text-gray-300 dark:text-gray-700">water_drop</span>
          No readings logged yet for this batch.
        </div>

        <div v-else>
          <!-- Header row -->
          <div class="grid grid-cols-4 px-5 py-2 text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
            <span>Date</span>
            <span class="text-right">Feed (kg)</span>
            <span class="text-right">Water (L)</span>
            <span class="text-right">Status</span>
          </div>
          <div class="divide-y divide-gray-100 dark:divide-gray-800">
            <div
              v-for="r in recentReadings.slice(0, 6)"
              :key="r.id ?? r.date"
              class="grid grid-cols-4 px-5 py-3 text-sm items-center hover:bg-gray-50 dark:hover:bg-darkbg-100 transition"
            >
              <span class="text-gray-700 dark:text-gray-300 font-medium text-xs">{{ formatDate(r.date) }}</span>
              <span class="text-right text-gray-900 dark:text-white font-semibold tabular-nums">{{ r.feed_kg?.toFixed(1) }}</span>
              <span class="text-right text-gray-900 dark:text-white font-semibold tabular-nums">{{ r.water_litres?.toFixed(1) }}</span>
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

      <!-- All Batches Status Table -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">layers</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">All Batches</h2>
          </div>
          <router-link to="/batches" class="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-500 transition">Manage</router-link>
        </div>

        <div v-if="loading" class="p-5 space-y-2.5">
          <div v-for="n in 3" :key="n" class="h-12 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="store.batchesList.length === 0" class="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
          <span class="material-icons-outlined text-3xl block mb-2 text-gray-300 dark:text-gray-700">layers</span>
          No batches created yet.
          <router-link to="/batches" class="block mt-2 text-primary-600 dark:text-primary-400 font-semibold">Create first batch →</router-link>
        </div>

        <div v-else>
          <div class="grid grid-cols-4 px-5 py-2 text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
            <span>ID / Breed</span>
            <span class="text-right">Birds</span>
            <span class="text-right">Age</span>
            <span class="text-right">Status</span>
          </div>
          <div class="divide-y divide-gray-100 dark:divide-gray-800">
            <div
              v-for="batch in store.batchesList.slice(0, 7)"
              :key="batch.id"
              class="grid grid-cols-4 px-5 py-3 text-sm items-center hover:bg-gray-50 dark:hover:bg-darkbg-100 transition"
            >
              <div>
                <div class="font-bold text-gray-900 dark:text-white text-xs">#{{ batch.id }}</div>
                <div class="text-gray-400 dark:text-gray-500 text-[11px]">{{ batch.breed || '—' }}</div>
              </div>
              <span class="text-right text-gray-800 dark:text-gray-200 font-semibold tabular-nums text-xs">{{ batch.bird_count?.toLocaleString() }}</span>
              <span class="text-right text-gray-500 dark:text-gray-400 text-xs">Day {{ batchAge(batch.start_date) }}</span>
              <span class="flex justify-end">
                <span
                  class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-bold"
                  :class="batch.status === 'active'
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'
                    : batch.status === 'closed'
                      ? 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-500'
                      : 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400'"
                >
                  {{ batch.status }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'

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
const quickLinks = [
  { label: 'Log Feed & Water', path: '/readings', icon: 'opacity' },
  { label: 'Log Growth', path: '/growth', icon: 'show_chart' },
  { label: 'AI Monitor', path: '/inference', icon: 'videocam' },
  { label: 'Medications', path: '/medications', icon: 'vaccines' },
]

// ── Data fetching ──────────────────────────────
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // Always refresh alerts across all batches (unacknowledged only)
    const alertsData = await api.alerts.list(null, true)
    unackAlerts.value = alertsData

    // If active batch is set, fetch recent readings
    if (store.activeBatch?.id) {
      const readings = await api.readings.list(store.activeBatch.id)
      recentReadings.value = readings
    } else {
      recentReadings.value = []
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

// Re-fetch when active batch changes (e.g. after App.vue initialises store)
watch(() => store.activeBatch, fetchDashboardData)

onMounted(fetchDashboardData)
</script>
