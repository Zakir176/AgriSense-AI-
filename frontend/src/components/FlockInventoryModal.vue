<template>
  <AgriModal
    :show="show"
    title="Log Flock Inventory Adjustment"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Adjustment Type</label>
        <AgriSelect
          v-model="form.adjustment_type"
          :options="typeOptions"
          placeholder="Select reason..."
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <AgriInput
          v-model.number="form.quantity"
          type="number"
          label="Quantity (Head Count)"
          required
          min="1"
          placeholder="e.g. 15"
          icon="people"
        />
        <AgriInput
          v-model="form.date"
          type="date"
          label="Event Date"
          required
          icon="calendar_today"
        />
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">Notes / Reason Details</label>
        <textarea
          v-model="form.notes"
          rows="3"
          class="w-full text-xs rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-darkbg-100 p-3 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-primary-500 focus:outline-none transition"
          placeholder="e.g. Sold 20 birds to local restaurant, or Culled due to leg abnormality"
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
        >Cancel</AgriButton>
        <AgriButton
          type="submit"
          variant="primary"
          class="flex-1"
          :loading="isSubmitting"
        >Submit Adjustment</AgriButton>
      </div>
    </form>
  </AgriModal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import AgriModal from './ui/AgriModal.vue'
import AgriInput from './ui/AgriInput.vue'
import AgriButton from './ui/AgriButton.vue'
import AgriSelect from './ui/AgriSelect.vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  batchId: { type: Number, default: null }
})

const emit = defineEmits(['close', 'success'])

const isSubmitting = ref(false)
const errorMsg = ref('')

const typeOptions = [
  { value: 'sale', label: 'Sale (Market Harvest / Sold)' },
  { value: 'cull', label: 'Cull (Selective Removal)' },
  { value: 'mortality', label: 'Mortality (Unrecorded Death)' },
  { value: 'addition', label: 'Addition (Flock Restock)' },
  { value: 'correction', label: 'Correction (Inventory Count Adjustment)' }
]

const form = reactive({
  adjustment_type: 'sale',
  quantity: 1,
  date: new Date().toISOString().split('T')[0],
  notes: ''
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    form.adjustment_type = 'sale'
    form.quantity = 1
    form.date = new Date().toISOString().split('T')[0]
    form.notes = ''
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
    emit('success', {
      adjustment_type: form.adjustment_type,
      quantity_delta: delta,
      date: form.date,
      notes: form.notes
    })
  } catch (err) {
    errorMsg.value = err.message || 'Failed to submit adjustment'
  } finally {
    isSubmitting.value = false
  }
}
</script>
