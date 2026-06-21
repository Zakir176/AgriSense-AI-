<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Medications & Vaccines</h1>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Track treatments, vaccination cycles, and monitor outcome notes for
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
        <button
          @click="showLogModal = true"
          :disabled="!selectedBatchId"
          class="bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-4 py-2 rounded-xl shadow-sm hover:shadow transition flex items-center gap-1.5 text-sm"
        >
          <span class="material-icons-outlined text-[17px]">medical_services</span>
          Log Administration
        </button>
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">vaccines</span>
      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">Select a batch above to view medication schedules.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Vaccinations and clinical remedies are organized by production batch.</p>
    </div>

    <template v-else>
      <!-- ─── Summary Cards ─── -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-xl">
            <span class="material-icons-outlined">medical_services</span>
          </div>
          <div>
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">Total Treatments</div>
            <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ entries.length }}</div>
          </div>
        </div>

        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded-xl">
            <span class="material-icons-outlined">verified</span>
          </div>
          <div>
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">Vaccinations</div>
            <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ vaccineCount }}</div>
          </div>
        </div>

        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm flex items-center gap-4">
          <div class="p-3 bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 rounded-xl">
            <span class="material-icons-outlined">monitoring</span>
          </div>
          <div>
            <div class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">Treatment Success</div>
            <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
              {{ entries.length > 0 ? Math.round((resolvedCount / entries.length) * 100) + '%' : '—' }}
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Treatment History Table ─── -->
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-[18px] text-gray-500 dark:text-gray-400">history</span>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Medication & Vaccine Log</h2>
            <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">{{ entries.length }} entries</span>
          </div>
        </div>

        <div v-if="loading" class="p-5 space-y-2.5">
          <div v-for="n in 3" :key="n" class="h-12 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
        </div>

        <div v-else-if="entries.length === 0" class="py-14 text-center">
          <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-2">medication</span>
          <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">No medical records registered yet</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Click "Log Administration" to add vaccines or medical treatments.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50 dark:bg-darkbg-100 text-[10px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <tr>
                <th class="px-6 py-3 font-bold">Date</th>
                <th class="px-6 py-3 font-bold">Type / Description</th>
                <th class="px-6 py-3 font-bold">Dosage</th>
                <th class="px-6 py-3 font-bold">Outcome Notes</th>
                <th class="px-6 py-3 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
              <tr
                v-for="e in entries"
                :key="e.id"
                class="hover:bg-gray-50 dark:hover:bg-darkbg-100 transition items-center"
              >
                <td class="px-6 py-4 text-xs text-gray-700 dark:text-gray-300 font-medium whitespace-nowrap">{{ formatDate(e.date) }}</td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                      :class="isVaccine(e.medicine_type)
                        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400'
                        : 'bg-purple-50 text-purple-700 dark:bg-purple-950/30 dark:text-purple-400'"
                    >
                      {{ isVaccine(e.medicine_type) ? 'Vaccine' : 'Treatment' }}
                    </span>
                    <span class="font-bold text-gray-900 dark:text-white">{{ e.medicine_type }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 font-semibold text-gray-650 dark:text-gray-400 tabular-nums">{{ e.dosage }}</td>
                <td class="px-6 py-4 max-w-xs">
                  <div class="text-xs text-gray-700 dark:text-gray-350">
                    <span v-if="e.outcome_note" class="italic">"{{ e.outcome_note }}"</span>
                    <span v-else class="text-gray-400 dark:text-gray-600">Pending outcome note…</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-right">
                  <button
                    @click="openEditModal(e)"
                    class="text-xs bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-750 dark:text-gray-300 font-bold px-3 py-1.5 rounded-lg transition inline-flex items-center gap-1"
                  >
                    <span class="material-icons-outlined text-[13px]">edit</span>
                    Update Note
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- ═══ Log Medication Modal ═══ -->
    <div
      v-if="showLogModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto"
      @click.self="closeModal"
    >
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 w-full max-w-md rounded-2xl shadow-xl p-6 space-y-5">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Log Medication / Vaccine</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>

        <form @submit.prevent="submitMedication" class="space-y-4">
          <!-- Date -->
          <div>
            <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Administration Date</label>
            <input
              v-model="form.date"
              type="date"
              required
              class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            />
          </div>

          <!-- Type -->
          <div>
            <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Medicine / Treatment Name</label>
            <input
              v-model="form.medicine_type"
              type="text"
              required
              placeholder="e.g. Newcastle ND-LaSota Vaccine, Amoxicillin"
              class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            />
          </div>

          <!-- Dosage -->
          <div>
            <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Dosage</label>
            <input
              v-model="form.dosage"
              type="text"
              required
              placeholder="e.g. 10 ml/L of drinking water, 2.5g / kg feed"
              class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            />
          </div>

          <!-- Outcome Note (Optional) -->
          <div>
            <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Initial Outcome Notes (Optional)</label>
            <textarea
              v-model="form.outcome_note"
              rows="2"
              placeholder="e.g. Scheduled vaccination. Expected recovery 24h."
              class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            ></textarea>
          </div>

          <!-- Error -->
          <div v-if="formError" class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/20 px-3 py-2 rounded-xl border border-red-200 dark:border-red-900/30">
            {{ formError }}
          </div>

          <!-- Success -->
          <div v-if="formSuccess" class="text-sm text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 px-3 py-2 rounded-xl border border-emerald-200 dark:border-emerald-900/30 flex items-center gap-2">
            <span class="material-icons-outlined text-[16px]">check_circle</span>
            Treatment logged successfully!
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
              {{ submitting ? 'Saving…' : 'Log Treatment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ═══ Update Outcome Note Modal ═══ -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 overflow-y-auto"
      @click.self="closeEditModal"
    >
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 w-full max-w-md rounded-2xl shadow-xl p-6 space-y-5">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Update Outcome Note</h3>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition">
            <span class="material-icons-outlined">close</span>
          </button>
        </div>

        <div class="bg-gray-50 dark:bg-darkbg-100 p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 text-xs space-y-1">
          <div><span class="font-bold text-gray-500 dark:text-gray-400">Treatment:</span> <span class="font-semibold text-gray-800 dark:text-gray-200">{{ editingEntry?.medicine_type }}</span></div>
          <div><span class="font-bold text-gray-500 dark:text-gray-400">Dosage:</span> <span class="font-semibold text-gray-800 dark:text-gray-200">{{ editingEntry?.dosage }}</span></div>
          <div><span class="font-bold text-gray-500 dark:text-gray-400">Administered:</span> <span class="font-semibold text-gray-800 dark:text-gray-200">{{ formatDate(editingEntry?.date) }}</span></div>
        </div>

        <form @submit.prevent="submitUpdate" class="space-y-4">
          <!-- Outcome Note -->
          <div>
            <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Outcome Notes</label>
            <textarea
              v-model="editForm.outcome_note"
              rows="3"
              required
              placeholder="e.g. Vaccination complete. 100% of cohort reached with no anomalies."
              class="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-800 rounded-xl bg-gray-50 dark:bg-darkbg-100 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
            ></textarea>
          </div>

          <!-- Error -->
          <div v-if="editError" class="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/20 px-3 py-2 rounded-xl border border-red-200 dark:border-red-900/30">
            {{ editError }}
          </div>

          <!-- Success -->
          <div v-if="editSuccess" class="text-sm text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 px-3 py-2 rounded-xl border border-emerald-200 dark:border-emerald-900/30 flex items-center gap-2">
            <span class="material-icons-outlined text-[16px]">check_circle</span>
            Outcome note updated successfully!
          </div>

          <div class="flex gap-3 pt-3 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              @click="closeEditModal"
              class="flex-1 py-2.5 border border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-bold rounded-xl text-gray-700 dark:text-gray-300 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="updating"
              class="flex-1 py-2.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow transition flex items-center justify-center gap-2"
            >
              <span v-if="updating" class="material-icons-outlined text-[16px] animate-spin">sync</span>
              {{ updating ? 'Updating…' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const entries = ref([])
const loading = ref(false)

const showLogModal = ref(false)
const submitting = ref(false)
const formError = ref('')
const formSuccess = ref(false)

const showEditModal = ref(false)
const editingEntry = ref(null)
const updating = ref(false)
const editError = ref('')
const editSuccess = ref(false)

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

const editForm = ref({
  outcome_note: ''
})

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

const vaccineCount = computed(() => {
  return entries.value.filter(e => isVaccine(e.medicine_type)).length
})

const resolvedCount = computed(() => {
  // Resolved = has outcome note indicating successful result / resolution
  return entries.value.filter(e => e.outcome_note && e.outcome_note.trim().length > 0).length
})

const isVaccine = (typeStr) => {
  if (!typeStr) return false
  const lower = typeStr.toLowerCase()
  return lower.includes('vaccine') || lower.includes('vacc') || lower.includes('vac') || lower.includes('vax')
}

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
  formError.value = ''
  formSuccess.value = false
  form.value = {
    date: getTodayString(),
    medicine_type: '',
    dosage: '',
    outcome_note: ''
  }
}

const submitMedication = async () => {
  formError.value = ''
  formSuccess.value = false
  submitting.value = true

  try {
    await api.medications.create({
      batch_id: selectedBatchId.value,
      date: form.value.date,
      medicine_type: form.value.medicine_type,
      dosage: form.value.dosage,
      outcome_note: form.value.outcome_note
    })
    formSuccess.value = true
    setTimeout(() => {
      closeModal()
      fetchEntries()
    }, 1000)
  } catch (err) {
    formError.value = err.message || 'Failed to save medication entry.'
  } finally {
    submitting.value = false
  }
}

// ── Edit Modal Actions ──────────────────────
const openEditModal = (entry) => {
  editingEntry.value = entry
  editForm.value.outcome_note = entry.outcome_note || ''
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingEntry.value = null
  editError.value = ''
  editSuccess.value = false
  editForm.value.outcome_note = ''
}

const submitUpdate = async () => {
  if (!editingEntry.value) return
  editError.value = ''
  editSuccess.value = false
  updating.value = true

  try {
    await api.medications.update(editingEntry.value.id, {
      outcome_note: editForm.value.outcome_note
    })
    editSuccess.value = true
    setTimeout(() => {
      closeEditModal()
      fetchEntries()
    }, 1000)
  } catch (err) {
    editError.value = err.message || 'Failed to update outcome note.'
  } finally {
    updating.value = false
  }
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
