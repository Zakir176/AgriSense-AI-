<template>
  <AgriModal
    :show="show"
    :title="$t('inventory.modal_title')"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('inventory.adjustment_type') }}</label>
        <AgriSelect
          v-model="form.adjustment_type"
          :options="typeOptions"
          :placeholder="$t('inventory.select_reason')"
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <AgriInput
          v-model.number="form.quantity"
          type="number"
          :label="$t('inventory.quantity')"
          required
          min="1"
          placeholder="e.g. 15"
          icon="people"
        />
        <AgriInput
          v-model="form.date"
          type="date"
          :label="$t('inventory.event_date')"
          required
          icon="calendar_today"
        />
      </div>

      <!-- Sale-specific financial fields -->
      <div v-if="form.adjustment_type === 'sale'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <AgriInput
          v-model.number="form.unit_price_zmw"
          type="number"
          :label="$t('inventory.price_per_bird')"
          min="0"
          step="0.01"
          placeholder="e.g. 85.00"
          icon="payments"
        />
        <AgriInput
          v-model="form.buyer_name"
          type="text"
          :label="$t('inventory.buyer_name')"
          placeholder="e.g. Shoprite Lusaka"
          icon="person"
        />
      </div>

      <!-- Computed sale total preview -->
      <div
        v-if="form.adjustment_type === 'sale' && form.unit_price_zmw && form.quantity"
        class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 px-3.5 py-2.5 rounded-xl border border-emerald-200 dark:border-emerald-900/30"
      >
        💰 {{ $t('inventory.sale_total') }}: ZMW {{ (form.quantity * form.unit_price_zmw).toFixed(2) }}
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">{{ $t('inventory.notes_label') }}</label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="w-full text-xs rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-darkbg-100 p-3 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-primary-500 focus:outline-none transition"
          :placeholder="$t('inventory.notes_placeholder')"
        ></textarea>
      </div>

      <div v-if="errorMsg" class="text-xs font-semibold text-status-danger bg-red-50 dark:bg-red-950/20 px-3.5 py-2.5 rounded-xl border border-red-200 dark:border-red-900/30">
        {{ errorMsg }}
      </div>

      <div class="flex space-x-3 pt-4 border-t border-gray-150 dark:border-gray-800">
        <AgriButton
          type="button"
          variant="outline"
          class="flex-1"
          @click="$emit('close')"
        >{{ $t('common.cancel') }}</AgriButton>
        <AgriButton
          type="submit"
          variant="primary"
          class="flex-1"
          :loading="isSubmitting"
        >{{ $t('inventory.submit_adjustment') }}</AgriButton>
      </div>
    </form>
  </AgriModal>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AgriModal from './ui/AgriModal.vue'
import AgriInput from './ui/AgriInput.vue'
import AgriButton from './ui/AgriButton.vue'
import AgriSelect from './ui/AgriSelect.vue'

const { t } = useI18n()

const props = defineProps({
  show: { type: Boolean, default: false },
  batchId: { type: Number, default: null }
})

const emit = defineEmits(['close', 'success'])

const isSubmitting = ref(false)
const errorMsg = ref('')

const typeOptions = computed(() => [
  { value: 'sale', label: t('inventory.type_sale') },
  { value: 'cull', label: t('inventory.type_cull') },
  { value: 'mortality', label: t('inventory.type_mortality') },
  { value: 'addition', label: t('inventory.type_addition') },
  { value: 'correction', label: t('inventory.type_correction') }
])

const form = reactive({
  adjustment_type: 'sale',
  quantity: 1,
  date: new Date().toISOString().split('T')[0],
  notes: '',
  unit_price_zmw: null,
  buyer_name: ''
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    form.adjustment_type = 'sale'
    form.quantity = 1
    form.date = new Date().toISOString().split('T')[0]
    form.notes = ''
    form.unit_price_zmw = null
    form.buyer_name = ''
    errorMsg.value = ''
  }
})

async function handleSubmit() {
  if (!form.quantity || form.quantity <= 0) {
    errorMsg.value = 'Quantity must be greater than 0'
    return
  }

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    const delta = ['mortality', 'sale', 'cull'].includes(form.adjustment_type) ? -form.quantity : form.quantity
    const payload = {
      adjustment_type: form.adjustment_type,
      quantity_delta: delta,
      date: form.date,
      notes: form.notes
    }
    // Attach financial fields for sales
    if (form.adjustment_type === 'sale') {
      if (form.unit_price_zmw) payload.unit_price_zmw = form.unit_price_zmw
      if (form.buyer_name) payload.buyer_name = form.buyer_name
    }
    emit('success', payload)
  } catch (err) {
    errorMsg.value = err.message || 'Failed to submit adjustment'
  } finally {
    isSubmitting.value = false
  }
}
</script>
