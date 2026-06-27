<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Medications & Vaccines</h1>
        <p class="mt-0.5 text-sm text-gray-550 dark:text-gray-400">
          Track treatments, vaccination cycles, and monitor outcome notes for
          <span v-if="activeBatchObj" class="font-bold text-gray-700 dark:text-gray-300">Batch #{{ activeBatchObj.id }} · {{ activeBatchObj.breed }}</span>
          <span v-else class="italic text-gray-450">no active batch</span>
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Custom AgriSelect dropdown -->
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
          icon="medical_services"
          :disabled="!selectedBatchId"
          @click="showLogModal = true"
        >
          Log Administration
        </AgriButton>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">vaccines</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">Select a batch above to view medication schedules.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Vaccinations and clinical remedies are organized by production batch.</p>
    </div>

    <template v-else>
      <!-- ─── Summary Cards (Staggered load) ─── -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AgriStatCard
          label="Total Treatments"
          :value="entries.length"
          icon="medical_services"
          icon-color-class="bg-blue-50 dark:bg-blue-950/40 text-blue-500"
          class="animate-fade-in-up delay-100"
        />
        <AgriStatCard
          label="Vaccinations Done"
          :value="vaccineCount"
          icon="verified"
          icon-color-class="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450"
          class="animate-fade-in-up delay-150"
        />
        <AgriStatCard
          label="Resolution Success Rate"
          :value="entries.length > 0 ? Math.round((resolvedCount / entries.length) * 100) : 0"
          suffix="%"
          icon="monitoring"
          icon-color-class="bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400"
          class="animate-fade-in-up delay-200"
        />
      </div>

      <!-- ─── Vaccine Schedule Timeline ─── -->
      <AgriCard class="animate-fade-in-up delay-250">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">schedule</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Broiler Vaccination Roadmap</h2>
          </div>
          <span class="text-xs text-gray-450 dark:text-gray-500 font-semibold">Standard Broiler Program (Ross/Cobb)</span>
        </template>

        <!-- Horizontal Timeline -->
        <div class="relative py-6 flex flex-col md:flex-row justify-between items-center md:items-start gap-8 md:gap-4 w-full">
          <!-- Connective line -->
          <div class="hidden md:block absolute top-[43px] left-[5%] right-[5%] h-0.5 bg-gray-200 dark:bg-gray-800 z-0"></div>

          <!-- Timeline Steps -->
          <div
            v-for="(item, idx) in vaccineSchedule"
            :key="idx"
            class="relative flex flex-col items-center text-center z-10 w-full md:w-1/5 animate-scale-in"
            :class="getStaggerDelayClass(idx)"
          >
            <!-- Step marker bubble -->
            <div
              class="h-10 w-10 rounded-full flex items-center justify-center border-2 transition-all duration-300"
              :class="[
                item.status === 'completed'
                  ? 'bg-primary-500 border-primary-600 text-white dark:bg-primary-600'
                  : item.status === 'overdue'
                    ? 'bg-red-50 border-status-danger text-status-danger dark:bg-red-950/40 animate-pulse-critical'
                    : 'bg-white dark:bg-darkbg-50 border-gray-300 dark:border-gray-800 text-gray-400'
              ]"
            >
              <span class="material-icons-outlined text-[18px] leading-none">
                {{ item.status === 'completed' ? 'check' : item.status === 'overdue' ? 'warning' : 'hourglass_empty' }}
              </span>
            </div>

            <!-- Labels -->
            <div class="mt-3.5 space-y-0.5">
              <p class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase">Day {{ item.day }}</p>
              <p class="text-sm font-extrabold text-gray-850 dark:text-gray-200">{{ item.name }}</p>
              <p class="text-[11px] text-gray-550 dark:text-gray-550">{{ item.type }}</p>
              <div class="pt-1.5 flex justify-center">
                <AgriBadge
                  :variant="item.status === 'completed' ? 'success' : item.status === 'overdue' ? 'critical' : 'info'"
                  :pulse="item.status === 'overdue'"
                  size="xs"
                >
                  {{ item.status }}
                </AgriBadge>
              </div>
            </div>
          </div>
        </div>
      </AgriCard>

      <!-- ─── Treatment History Logs ─── -->
      <AgriCard class="animate-fade-in-up delay-300" padding="none">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">history</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Administration logs</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ entries.length }} entries</span>
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
                Pending outcome note…
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
              />
              <AgriButton
                variant="ghost"
                size="sm"
                icon="delete"
                class="text-red-500 hover:text-red-650 hover:bg-red-50 dark:hover:bg-red-950/20"
                @click="deleteMedication(item.id)"
              />
            </div>
          </template>
        </AgriTable>
      </AgriCard>
    </template>

    <!-- ─── Log Medication Modal (AgriModal) ─── -->
    <AgriModal
      :show="showLogModal"
      :title="editingMedicationId ? 'Edit Medical Log' : 'Log Vaccine & Medication'"
      @close="closeModal"
    >
      <form @submit.prevent="submitMedication" class="space-y-4">
        <!-- Date -->
        <AgriInput
          v-model="form.date"
          type="date"
          label="Administration Date"
          required
          icon="calendar_today"
        />

        <!-- Type -->
        <AgriInput
          v-model="form.medicine_type"
          type="text"
          label="Medicine / Treatment Name"
          required
          placeholder="e.g. Newcastle ND-LaSota Vaccine, Amoxicillin"
          icon="vaccines"
        />

        <!-- Dosage -->
        <AgriInput
          v-model="form.dosage"
          type="text"
          label="Dosage Instruction"
          required
          placeholder="e.g. 10 ml/L in water, 2.5g / kg feed"
          icon="medical_services"
        />

        <!-- Outcome Note -->
        <div>
          <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Outcome Notes</label>
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
          >
            Cancel
          </AgriButton>
          <AgriButton
            type="submit"
            variant="primary"
            class="flex-1"
            :loading="submitting"
          >
            {{ editingMedicationId ? 'Save Changes' : 'Log Treatment' }}
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

// Design System components
import AgriButton from '../components/ui/AgriButton.vue'
import AgriCard from '../components/ui/AgriCard.vue'
import AgriStatCard from '../components/ui/AgriStatCard.vue'
import AgriTable from '../components/ui/AgriTable.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriModal from '../components/ui/AgriModal.vue'
import AgriInput from '../components/ui/AgriInput.vue'
import AgriSelect from '../components/ui/AgriSelect.vue'

const toast = useToast()
const { getStaggerDelayClass } = useAnimations()

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const entries = ref([])
const loading = ref(false)
const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)
const editingMedicationId = ref(null)

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

const resolvedCount = computed(() => {
  return entries.value.filter(e => e.outcome_note && e.outcome_note.trim().length > 0).length
})

const activeCohortAge = computed(() => {
  if (!activeBatchObj.value?.start_date) return 0
  const start = new Date(activeBatchObj.value.start_date)
  const today = new Date()
  start.setHours(0,0,0,0)
  today.setHours(0,0,0,0)
  return Math.ceil(Math.abs(today - start) / (1000 * 60 * 60 * 24))
})

const vaccineSchedule = computed(() => {
  if (!activeBatchObj.value) return []
  const age = activeCohortAge.value
  
  const schedule = [
    { day: 1, name: "Marek's Vaccine", type: 'Hatchery' },
    { day: 7, name: 'Gumboro (Dose 1)', type: 'Water/Oral' },
    { day: 14, name: 'Newcastle (Dose 1)', type: 'Ocular/Water' },
    { day: 21, name: 'Gumboro (Dose 2)', type: 'Water/Oral' },
    { day: 28, name: 'Newcastle (Dose 2)', type: 'Water/Oral' }
  ]

  return schedule.map(item => {
    const isLogged = entries.value.some(e => {
      if (!isVaccine(e.medicine_type)) return false
      const nameLower = e.medicine_type.toLowerCase()
      const itemLower = item.name.toLowerCase().split(' ')[0]
      return nameLower.includes(itemLower)
    })

    let status = 'pending'
    if (isLogged) {
      status = 'completed'
    } else if (age >= item.day) {
      status = 'overdue'
    }

    return {
      ...item,
      status
    }
  })
})

const isVaccine = (typeStr) => {
  if (!typeStr) return false
  const lower = typeStr.toLowerCase()
  return lower.includes('vaccine') || lower.includes('vacc') || lower.includes('vac') || lower.includes('vax')
}

const tableHeaders = [
  { text: 'Date', value: 'date', align: 'left' },
  { text: 'Type / Description', value: 'medicine_type', align: 'left' },
  { text: 'Dosage', value: 'dosage', align: 'left' },
  { text: 'Outcome Notes', value: 'outcome_note', align: 'left' },
  { text: 'Actions', value: 'actions', align: 'right' }
]

// ── Data fetching ──────────────────────────
const fetchEntries = async () => {
  if (!selectedBatchId.value) return
  loading.value = true
  try {
    entries.value = await api.medications.list(selectedBatchId.value)
  } catch (err) {
    console.error('Failed to load medication history:', err)
  } finally {
    loading.value = false
  }
}

const onBatchChange = () => {
  fetchEntries()
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
    await fetchEntries()
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
    await fetchEntries()
    closeModal()
  } catch (err) {
    formError.value = err.message || 'Failed to save medication entry.'
  } finally {
    submitting.value = false
  }
}

// ── Formatting ──────────────────────────
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const options = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

const formatDateShort = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

// ── Lifecycle & Watchers ──────────────────
watch(() => store.activeBatch, (newVal) => {
  if (newVal && !selectedBatchId.value) {
    selectedBatchId.value = newVal.id
    fetchEntries()
  }
}, { immediate: true })

onMounted(() => {
  if (store.activeBatch) {
    selectedBatchId.value = store.activeBatch.id
    fetchEntries()
  }
})
</script>
