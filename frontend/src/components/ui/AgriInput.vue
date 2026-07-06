<template>
  <div class="flex flex-col w-full gap-1.5 animate-scale-in">
    <!-- Input Label -->
    <label
      v-if="label"
      :for="inputId"
      class="text-xs font-bold tracking-wide text-gray-500 uppercase dark:text-gray-400 select-none"
    >
      {{ label }}
      <span v-if="required" class="text-status-danger font-black">*</span>
    </label>

    <!-- Input Box Wrapper -->
    <div class="relative flex items-center w-full">
      <!-- Left Icon -->
      <span
        v-if="icon"
        class="absolute left-3.5 material-icons-outlined text-gray-450 dark:text-gray-500 pointer-events-none select-none text-[18px]"
      >
        {{ icon }}
      </span>

      <!-- Input Element -->
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        @input="$emit('update:modelValue', $event.target.value)"
        class="w-full text-sm font-medium transition-all duration-205 rounded-xl border outline-none bg-white dark:bg-darkbg-50/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-650 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-100 dark:disabled:bg-darkbg-100"
        :class="[
          icon ? 'pl-10.5' : 'pl-4',
          error ? 'pr-10.5' : 'pr-4',
          // Border and focus status
          error
            ? 'border-status-danger ring-2 ring-status-danger/10 focus:ring-status-danger/25'
            : success
              ? 'border-status-success ring-2 ring-status-success/10 focus:ring-status-success/25'
              : 'border-gray-250 dark:border-gray-800 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 dark:focus:border-primary-400 dark:focus:ring-primary-400/10'
        ]"
        v-bind="$attrs"
      />

      <!-- Right Indicator Icons (e.g., error alert, success checkmark) -->
      <span
        v-if="error"
        class="absolute right-3.5 material-icons-outlined text-status-danger text-[18px] pointer-events-none select-none animate-pulse"
      >
        error_outline
      </span>
      <span
        v-else-if="success"
        class="absolute right-3.5 material-icons-outlined text-status-success text-[18px] pointer-events-none select-none"
      >
        check_circle_outline
      </span>
    </div>

    <!-- Error/Helper Message -->
    <Transition name="fade">
      <p
        v-if="error"
        class="text-xs font-semibold text-status-danger flex items-center gap-1 mt-0.5"
      >
        <span>{{ error }}</span>
      </p>
    </Transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  success: {
    type: Boolean,
    default: false
  },
  icon: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue'])

const inputId = computed(() => props.id || `agri-input-${Math.random().toString(36).substring(2, 9)}`)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
