<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ $t('meds.title') }}</h1>
        <p class="mt-0.5 text-sm text-gray-550 dark:text-gray-400">
          {{ $t('meds.subtitle') }}
          <span v-if="activeBatchObj" class="font-bold text-gray-700 dark:text-gray-300">Batch #{{ activeBatchObj.id }} · {{ activeBatchObj.breed }}</span>
          <span v-else class="italic text-gray-450">{{ $t('meds.no_active') }}</span>
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Custom AgriSelect dropdown -->
        <div class="w-48">
          <AgriSelect
            v-model="selectedBatchId"
            :options="batchOptions"
            :placeholder="$t('meds.select_batch')"
            @change="onBatchChange"
          />
        </div>
        <AgriButton
          variant="outline"
          size="sm"
          :disabled="entries.length === 0"
          @click="exportCSV"
          title="Download CSV"
        >
          <span class="material-icons-outlined text-sm">download</span>
          <span>Export CSV</span>
        </AgriButton>
        <AgriButton
          variant="primary"
          icon="medical_services"
          :disabled="!selectedBatchId"
          @click="showLogModal = true"
        >{{ $t('meds.log_admin') }}</AgriButton>
      </div>
    </div>


    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">vaccines</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">{{ $t('meds.select_view') }}</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ $t('meds.vaccines_org') }}</p>
    </div>

    <template v-else>
      <!-- ─── Summary Cards ─── -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <AgriStatCard
          :label="$t('meds.total_treatments')"
          :value="entries.length"
          icon="history"
          icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500"
          class="animate-fade-in-up delay-100"
        />
        <AgriStatCard
          :label="$t('calendar.upcoming')"
          :value="upcomingCount"
          icon="event_upcoming"
          icon-color-class="bg-amber-50 dark:bg-amber-950/40 text-amber-500"
          class="animate-fade-in-up delay-150"
        />
        <AgriStatCard
          :label="$t('meds.vaccinations_done')"
          :value="vaccineCount"
          icon="verified"
          icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450"
          class="animate-fade-in-up delay-200"
        />
        <AgriStatCard
          :label="$t('meds.resolution_success')"
          :value="entries.length > 0 ? Math.round((resolvedCount / entries.length) * 100) : 0"
          suffix="%"
          icon="monitoring"
          icon-color-class="bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400"
          class="animate-fade-in-up delay-250"
        />
      </div>

      <!-- ─── Interactive Treatment Calendar ─── -->
      <TreatmentCalendar
        id="treatment-calendar-panel"
        :schedules="schedules"
        :batch-start-date="activeBatchObj?.start_date"
        @open-schedule="openScheduleModal"
        @edit="editSchedule"
        @delete="deleteSchedule"
        @mark-complete="markScheduleComplete"
        class="animate-fade-in-up delay-300"
      />

      <!-- ─── Treatment History Logs ─── -->
      <AgriCard class="animate-fade-in-up delay-300" padding="none">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">history</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('meds.admin_logs') }}</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ entries.length }} {{ $t('meds.entries') }}</span>
          </div>
        </template>

        <AgriTable
          :headers="tableHeaders"
          :items="entries"
          :loading="loading"
          striped
          class="border-none shadow-none rounded-none"
        >
          <template #date="{ item }">
            <span class="text-xs font-semibold text-gray-700 dark:text-gray-300">{{ formatDate(item.date) }}</span>
          </template>

          <template #medicine_type="{ item }">
            <div class="flex items-center gap-2">
              <AgriBadge
                :variant="isVaccine(item.medicine_type) ? 'success' : 'warning'"
              >
                {{ isVaccine(item.medicine_type) ? 'Vaccine' : 'Treatment' }}
              </AgriBadge>
              <span class="font-bold text-gray-900 dark:text-white text-xs">{{ item.medicine_type }}</span>
            </div>
          </template>

          <template #dosage="{ item }">
            <span class="text-xs font-bold text-gray-650 dark:text-gray-450">{{ item.dosage }}</span>
          </template>

          <template #outcome_note="{ item }">
            <div class="text-xs">
              <span v-if="item.outcome_note" class="italic text-gray-700 dark:text-gray-300">"{{ item.outcome_note }}"</span>
              <span v-else class="text-gray-400 dark:text-gray-600 flex items-center gap-1">
                <span class="h-1 w-1 bg-amber-500 rounded-full animate-ping"></span>
                {{ $t('meds.pending_note') }}
              </span>
            </div>
          </template>

          <template #actions="{ item }">
            <div class="flex justify-end gap-2">
              <AgriButton
                variant="outline"
                size="sm"
                icon="edit"
                @click="editMedication(item)"
              >{{ $t('meds.edit') || 'Edit' }}</AgriButton>
              <AgriButton
                variant="ghost"
                size="sm"
                icon="delete"
                class="text-red-500 hover:text-red-650 hover:bg-red-50 dark:hover:bg-red-950/20"
                @click="deleteMedication(item.id)"
              >{{ $t('meds.delete') || 'Delete' }}</AgriButton>
            </div>
          </template>
        </AgriTable>
      </AgriCard>
    </template>

    <!-- ─── Schedule Modal ─── -->
    <ScheduleModal
      :show="showScheduleModal"
      :initial-date="selectedScheduleDate"
      :edit-data="editingScheduleData"
      @close="closeScheduleModal"
      @save="saveSchedule"
    />

    <!-- ─── Log Medication Modal ─── -->
    <AgriModal
      :show="showLogModal"
      :title="editingMedicationId ? $t('meds.edit_log') : $t('meds.log_vaccine')"
      @close="closeModal"
    >
      <form @submit.prevent="submitMedication" class="space-y-4">
        <!-- Date -->
        <AgriInput
          v-model="form.date"
          type="date"
          :label="$t('meds.admin_date')"
          required
          icon="calendar_today"
        />

        <!-- Type -->
        <AgriInput
          v-model="form.medicine_type"
          type="text"
          :label="$t('meds.med_name')"
          required
          placeholder="e.g. Newcastle ND-LaSota Vaccine, Amoxicillin"
          icon="vaccines"
        />

        <!-- Dosage -->
        <AgriInput
          v-model="form.dosage"
          type="text"
          :label="$t('meds.dosage_inst')"
          required
          placeholder="e.g. 10 ml/L in water, 2.5g / kg feed"
          icon="medical_services"
        />

        <!-- Outcome Note -->
        <div>
          <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">{{ $t('meds.outcome_notes') }}</label>
          <textarea
            v-model="form.outcome_note"
            rows="2.5"
            placeholder="e.g. Routine immunization. Flock healthy."
            class="w-full text-sm font-medium transition-all duration-200 px-4 py-2.5 border border-gray-250 dark:border-gray-800 rounded-xl bg-white dark:bg-darkbg-50/50 text-gray-900 dark:text-white placeholder-gray-400 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 dark:focus:border-primary-400 dark:focus:ring-primary-400/10 outline-none"
          ></textarea>
        </div>

        <!-- Form Error -->
        <div v-if="formError" class="text-xs font-semibold text-status-danger bg-red-50 dark:bg-red-950/20 px-3.5 py-2.5 rounded-xl border border-red-200 dark:border-red-900/30">
          {{ formError }}
        </div>

        <div class="flex gap-3 pt-3 border-t border-gray-150 dark:border-gray-800">
          <AgriButton
            type="button"
            variant="outline"
            class="flex-1"
            @click="closeModal"
          >{{ $t('meds.cancel') }}</AgriButton>
          <AgriButton
            type="submit"
            variant="primary"
            class="flex-1"
            :loading="submitting"
          >
            {{ editingMedicationId ? $t('meds.save_changes') : $t('meds.log_treatment') }}
          </AgriButton>
        </div>
      </form>
    </AgriModal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'
import { useToast } from '../composables/useToast'
import { useAnimations } from '../composables/useAnimations'
import { useI18n } from 'vue-i18n'
import { useReminders } from '../composables/useReminders'

// Design System components
import AgriButton from '../components/ui/AgriButton.vue'
import AgriCard from '../components/ui/AgriCard.vue'
import AgriStatCard from '../components/ui/AgriStatCard.vue'
import AgriTable from '../components/ui/AgriTable.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriModal from '../components/ui/AgriModal.vue'
import AgriInput from '../components/ui/AgriInput.vue'
import AgriSelect from '../components/ui/AgriSelect.vue'

// Custom feature components
import TreatmentCalendar from '../components/TreatmentCalendar.vue'
import ScheduleModal from '../components/ScheduleModal.vue'

const toast = useToast()
const { getStaggerDelayClass } = useAnimations()
const { t } = useI18n()
const { scheduleReminder, cancelReminder } = useReminders()

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const entries = ref([])
const schedules = ref([])
const loading = ref(false)

// Medication Log Modal
const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)
const editingMedicationId = ref(null)

// Schedule Modal
const showScheduleModal = ref(false)
const selectedScheduleDate = ref('')
const editingScheduleData = ref(null)

// ── Form helpers ──────────────────────────
const getTodayString = () => {
  const d = new Date()
  return [d.getFullYear(), String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')].join('-')
}

const form = ref({
  date: getTodayString(),
  medicine_type: '',
  dosage: '',
  outcome_note: ''
})

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

const vaccineCount = computed(() => {
  return entries.value.filter(e => isVaccine(e.medicine_type)).length
})

const upcomingCount = computed(() => {
  return schedules.value.filter(s => s.status === 'pending').length
})

const resolvedCount = computed(() => {
  return entries.value.filter(e => e.outcome_note && e.outcome_note.trim().length > 0).length
})

const isVaccine = (typeStr) => {
  if (!typeStr) return false
  const lower = typeStr.toLowerCase()
  return lower.includes('vaccine') || lower.includes('vacc') || lower.includes('vac') || lower.includes('vax')
}

const tableHeaders = computed(() => [
  { text: t('meds.date'), value: 'date', align: 'left' },
  { text: t('meds.type_desc'), value: 'medicine_type', align: 'left' },
  { text: t('meds.dosage'), value: 'dosage', align: 'left' },
  { text: t('meds.outcome_notes'), value: 'outcome_note', align: 'left' },
  { text: t('meds.actions'), value: 'actions', align: 'right' }
])

// ── Data fetching ──────────────────────────
const fetchData = async () => {
  if (!selectedBatchId.value) return
  loading.value = true
  try {
    const [meds, scheds] = await Promise.all([
      api.medications.list(selectedBatchId.value),
      api.schedules.list(selectedBatchId.value)
    ])
    entries.value = meds
    schedules.value = scheds
  } catch (err) {
    console.error('Failed to load medication/schedule data:', err)
  } finally {
    loading.value = false
  }
}

const onBatchChange = () => {
  fetchData()
}

// ── Schedule Logic ───────────────────────
const openScheduleModal = (dateStr) => {
  selectedScheduleDate.value = dateStr || getTodayString()
  editingScheduleData.value = null
  showScheduleModal.value = true
}

const editSchedule = (item) => {
  editingScheduleData.value = { ...item }
  selectedScheduleDate.value = item.scheduled_date
  showScheduleModal.value = true
}

const closeScheduleModal = () => {
  showScheduleModal.value = false
  editingScheduleData.value = null
}

const saveSchedule = async (payload) => {
  submitting.value = true
  try {
    let savedItem
    if (editingScheduleData.value) {
      savedItem = await api.schedules.update(editingScheduleData.value.id, payload)
      toast.success(t('calendar.schedule_updated'))
    } else {
      payload.batch_id = selectedBatchId.value
      savedItem = await api.schedules.create(payload)
      toast.success(t('calendar.schedule_created'))
    }
    
    // Handle reminders
    if (savedItem.remind_at) {
      await scheduleReminder(
        `sched_${savedItem.id}`,
        savedItem.title,
        `Treatment scheduled for batch #${selectedBatchId.value}`,
        savedItem.remind_at
      )
    } else {
      await cancelReminder(`sched_${savedItem.id}`)
    }
    
    await fetchData()
    closeScheduleModal()
  } catch (err) {
    toast.error(err.message || 'Failed to save schedule')
  } finally {
    submitting.value = false
  }
}

const deleteSchedule = async (id) => {
  if (!confirm(t('calendar.confirm_delete'))) return
  try {
    await api.schedules.delete(id)
    await cancelReminder(`sched_${id}`)
    await fetchData()
    toast.success(t('calendar.schedule_deleted'))
  } catch (err) {
    toast.error('Failed to delete schedule')
  }
}

const markScheduleComplete = async (item) => {
  try {
    await api.schedules.complete(item.id)
    await cancelReminder(`sched_${item.id}`)
    await fetchData()
    toast.success(t('calendar.marked_complete'))
  } catch (err) {
    toast.error('Failed to mark complete')
  }
}

// ── Log Modal Actions ───────────────────────
const closeModal = () => {
  showLogModal.value = false
  editingMedicationId.value = null
  formError.value = ''
  formSuccess.value = false
  form.value = {
    date: getTodayString(),
    medicine_type: '',
    dosage: '',
    outcome_note: ''
  }
}

const editMedication = (entry) => {
  editingMedicationId.value = entry.id
  form.value = {
    date: entry.date,
    medicine_type: entry.medicine_type,
    dosage: entry.dosage,
    outcome_note: entry.outcome_note || ''
  }
  formError.value = ''
  formSuccess.value = false
  showLogModal.value = true
}

const deleteMedication = async (id) => {
  if (!confirm('Are you sure you want to delete this medication entry?')) return
  try {
    await api.medications.delete(id)
    await fetchData()
    toast.success('Medication entry deleted successfully')
  } catch (err) {
    alert('Failed to delete medication entry: ' + err.message)
  }
}

const submitMedication = async () => {
  formError.value = ''
  formSuccess.value = false
  submitting.value = true

  try {
    if (editingMedicationId.value) {
      await api.medications.update(editingMedicationId.value, {
        date: form.value.date,
        medicine_type: form.value.medicine_type,
        dosage: form.value.dosage,
        outcome_note: form.value.outcome_note
      })
      toast.success('Medication record updated')
    } else {
      await api.medications.create({
        batch_id: selectedBatchId.value,
        date: form.value.date,
        medicine_type: form.value.medicine_type,
        dosage: form.value.dosage,
        outcome_note: form.value.outcome_note
      })
      toast.success('Medication dosage logged')
    }
    formSuccess.value = true
    await fetchData()
    closeModal()
  } catch (err) {
    formError.value = err.message || 'Failed to save medication entry.'
  } finally {
    submitting.value = false
  }
}

const exportCSV = () => {
  if (entries.value.length === 0) return

  const headers = [
    'Date',
    'Medicine / Vaccine',
    'Treatment Type',
    'Dosage',
    'Administered By',
    'Outcome Note'
  ]

  const sorted = [...entries.value].sort((a, b) => new Date(a.date) - new Date(b.date))

  const rows = sorted.map(e => [
    e.date,
    e.medicine_type ?? '—',
    e.treatment_type ?? '—',
    e.dosage ?? '—',
    e.administered_by ?? '—',
    e.outcome_note ?? ''
  ])

  const csvString = [headers.join(','), ...rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(','))].join('\n')
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `AgriSense_Batch_${selectedBatchId.value}_Medication_Records.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// ── Formatting ──────────────────────────
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const options = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

// ── Lifecycle & Watchers ──────────────────
watch(() => store.activeBatch, (newVal) => {
  if (newVal && !selectedBatchId.value) {
    selectedBatchId.value = newVal.id
    fetchData()
  }
}, { immediate: true })

onMounted(() => {
  if (store.activeBatch) {
    selectedBatchId.value = store.activeBatch.id
    fetchData()
  }
})
</script>
