<template>
  <AgriModal
    :show="show"
    :title="isEdit ? $t('calendar.edit_schedule') : $t('calendar.schedule_treatment')"
    @close="closeModal"
  >
    <form @submit.prevent="submit" class="space-y-4">
      <!-- Quick Templates -->
      <div v-if="!isEdit" class="space-y-1.5">
        <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ $t('calendar.quick_templates') }}</label>
        <div class="flex flex-wrap gap-2">
          <AgriButton
            v-for="tpl in quickTemplates"
            :key="tpl.title"
            type="button"
            variant="ghost"
            size="sm"
            class="bg-gray-50 dark:bg-darkbg-50 hover:bg-gray-100 dark:hover:bg-gray-800"
            @click="applyTemplate(tpl)"
          >
            {{ tpl.label }}
          </AgriButton>
        </div>
      </div>

      <!-- Title & Type -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AgriInput
          v-model="form.title"
          type="text"
          :label="$t('calendar.title_label')"
          required
          placeholder="e.g. Gumboro Dose 2"
          icon="vaccines"
        />
        <div>
          <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">{{ $t('calendar.type_label') }}</label>
          <AgriSelect
            v-model="form.treatment_type"
            :options="typeOptions"
          />
        </div>
      </div>

      <!-- Date & Dosage -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AgriInput
          v-model="form.scheduled_date"
          type="date"
          :label="$t('calendar.date_label')"
          required
          icon="calendar_today"
        />
        <AgriInput
          v-model="form.dosage"
          type="text"
          :label="$t('calendar.dosage_label')"
          placeholder="e.g. 10 ml/L in water"
          icon="medical_services"
        />
      </div>

      <!-- Notes -->
      <div>
        <label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">{{ $t('calendar.notes_label') }}</label>
        <textarea
          v-model="form.notes"
          rows="2"
          placeholder="e.g. Administer early morning"
          class="w-full text-sm font-medium transition-all duration-200 px-4 py-2.5 border border-gray-250 dark:border-gray-800 rounded-xl bg-white dark:bg-darkbg-50/50 text-gray-900 dark:text-white placeholder-gray-400 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 dark:focus:border-primary-400 dark:focus:ring-primary-400/10 outline-none"
        ></textarea>
      </div>

      <!-- Reminder Setup -->
      <div class="p-3 bg-gray-50 dark:bg-darkbg-50 rounded-xl border border-gray-200 dark:border-gray-800">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="material-icons-outlined text-gray-500">notifications_active</span>
            <span class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('calendar.set_reminder') }}</span>
          </div>
          <!-- Simple Toggle -->
          <button 
            type="button"
            class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            role="switch"
            :aria-checked="enableReminder"
            @click="toggleReminder"
          >
            <span class="sr-only">Enable reminder</span>
            <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white dark:bg-darkbg-50"></span>
            <span aria-hidden="true" class="pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out" :class="enableReminder ? 'bg-primary-500' : 'bg-gray-200 dark:bg-gray-700'"></span>
            <span aria-hidden="true" class="pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 dark:border-gray-700 bg-white shadow ring-0 transition-transform duration-200 ease-in-out" :class="enableReminder ? 'translate-x-4' : 'translate-x-0'"></span>
          </button>
        </div>
        
        <div v-if="enableReminder" class="animate-fade-in-up">
          <AgriInput
            v-model="form.remind_at"
            type="datetime-local"
            :label="$t('calendar.remind_me_at')"
            required
          />
          <p v-if="!permissionGranted" class="mt-2 text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
            <span class="material-icons-outlined text-[14px]">warning</span>
            {{ $t('calendar.notification_warning') }}
          </p>
        </div>
      </div>

      <!-- Form Error -->
      <div v-if="formError" class="text-xs font-semibold text-status-danger bg-red-50 dark:bg-red-950/20 px-3.5 py-2.5 rounded-xl border border-red-200 dark:border-red-900/30">
        {{ formError }}
      </div>

      <!-- Footer Actions -->
      <div class="flex gap-3 pt-3 border-t border-gray-150 dark:border-gray-800">
        <AgriButton
          type="button"
          variant="outline"
          class="flex-1"
          @click="closeModal"
        >{{ $t('calendar.cancel') }}</AgriButton>
        <AgriButton
          type="submit"
          variant="primary"
          class="flex-1"
          :loading="submitting"
        >
          {{ isEdit ? $t('calendar.save_changes') : $t('calendar.schedule_btn') }}
        </AgriButton>
      </div>
    </form>
  </AgriModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AgriModal from './ui/AgriModal.vue'
import AgriInput from './ui/AgriInput.vue'
import AgriSelect from './ui/AgriSelect.vue'
import AgriButton from './ui/AgriButton.vue'
import { useReminders } from '../composables/useReminders'

const props = defineProps({
  show: Boolean,
  initialDate: String,
  editData: Object // if present, we are in edit mode
})

const emit = defineEmits(['close', 'save'])
const { t } = useI18n()
const { permissionGranted, requestPermission } = useReminders()

const submitting = ref(false)
const formError = ref('')
const enableReminder = ref(false)

const form = ref({
  title: '',
  treatment_type: 'vaccine',
  scheduled_date: '',
  dosage: '',
  notes: '',
  remind_at: ''
})

const isEdit = computed(() => !!props.editData)

const typeOptions = [
  { label: t('calendar.type_vaccine'), value: 'vaccine' },
  { label: t('calendar.type_medication'), value: 'medication' },
  { label: t('calendar.type_supplement'), value: 'supplement' }
]

const quickTemplates = [
  { label: t('calendar.tpl_gumboro'), title: 'Gumboro Vaccine', type: 'vaccine', dosage: 'Water/Oral' },
  { label: t('calendar.tpl_newcastle'), title: 'Newcastle Vaccine', type: 'vaccine', dosage: 'Ocular/Water' },
  { label: t('calendar.tpl_coccidiosis'), title: 'Coccidiosis Treatment', type: 'medication', dosage: '' },
  { label: t('calendar.tpl_vitamins'), title: 'Vitamin Supplement', type: 'supplement', dosage: 'Water additive' }
]

const toggleReminder = async () => {
  enableReminder.value = !enableReminder.value
  if (enableReminder.value) {
    await requestPermission()
    if (!form.value.remind_at && form.value.scheduled_date) {
      // Default to 8 AM on the scheduled date
      form.value.remind_at = `${form.value.scheduled_date}T08:00`
    }
  } else {
    form.value.remind_at = ''
  }
}

const applyTemplate = (tpl) => {
  form.value.title = tpl.title
  form.value.treatment_type = tpl.type
  form.value.dosage = tpl.dosage
}

const closeModal = () => {
  emit('close')
}

const resetForm = () => {
  formError.value = ''
  enableReminder.value = false
  if (isEdit.value) {
    form.value = { ...props.editData }
    if (form.value.remind_at) {
      enableReminder.value = true
      // Convert to datetime-local format
      form.value.remind_at = new Date(form.value.remind_at).toISOString().slice(0, 16)
    }
  } else {
    form.value = {
      title: '',
      treatment_type: 'vaccine',
      scheduled_date: props.initialDate || new Date().toISOString().split('T')[0],
      dosage: '',
      notes: '',
      remind_at: ''
    }
  }
}

watch(() => props.show, (val) => {
  if (val) resetForm()
})

const submit = () => {
  const payload = { ...form.value }
  if (!enableReminder.value) {
    payload.remind_at = null
  } else if (payload.remind_at) {
    // ensure it's ISO UTC for backend
    payload.remind_at = new Date(payload.remind_at).toISOString()
  }
  
  emit('save', payload)
}
</script>
