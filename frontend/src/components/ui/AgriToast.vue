<template>
  <div
    class="pointer-events-auto flex flex-col rounded-xl shadow-xl border backdrop-blur-md overflow-hidden transition-all duration-300 relative w-full"
    :class="[
      typeClasses[type] || typeClasses.info
    ]"
    role="alert"
  >
    <!-- Card Body -->
    <div class="flex items-start gap-3 p-4">
      <!-- Status Icon -->
      <div class="mt-0.5 shrink-0">
        <span class="material-icons-outlined text-[20px] leading-none" :class="iconColorClasses[type]">
          {{ typeIcons[type] || 'info' }}
        </span>
      </div>
      
      <!-- Toast Message -->
      <div class="flex-1 text-sm font-semibold pr-2 text-gray-800 dark:text-gray-200">
        {{ message }}
      </div>

      <!-- Close Button -->
      <button 
        @click="$emit('close')"
        class="shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors focus-ring rounded-lg p-0.5"
      >
        <span class="material-icons-outlined text-[18px] block">close</span>
      </button>
    </div>

    <!-- Shrinking Progress Bar -->
    <div
      v-if="duration > 0"
      class="h-1 bg-current opacity-20 absolute bottom-0 left-0"
      :style="{ width: `${progress}%`, transition: 'width 100ms linear' }"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info',
    validator: (val) => ['success', 'error', 'warning', 'info'].includes(val)
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const emit = defineEmits(['close'])

const progress = ref(100)
let timer = null
let elapsed = 0
const intervalTime = 100

onMounted(() => {
  if (props.duration > 0) {
    timer = setInterval(() => {
      elapsed += intervalTime
      progress.value = Math.max(0, 100 - (elapsed / props.duration) * 100)
      if (elapsed >= props.duration) {
        clearInterval(timer)
        emit('close')
      }
    }, intervalTime)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// CSS and coloring rules
const typeClasses = {
  success: 'bg-white/95 dark:bg-[#2c2c30]/95 border-primary-200 dark:border-primary-900/40 text-primary-800 dark:text-primary-400',
  error: 'bg-white/95 dark:bg-[#2c2c30]/95 border-red-200 dark:border-red-900/40 text-status-danger dark:text-red-400',
  warning: 'bg-white/95 dark:bg-[#2c2c30]/95 border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-400',
  info: 'bg-white/95 dark:bg-[#2c2c30]/95 border-blue-200 dark:border-blue-900/40 text-blue-800 dark:text-blue-400'
}

const iconColorClasses = {
  success: 'text-primary-500 dark:text-primary-400',
  error: 'text-status-danger dark:text-red-400',
  warning: 'text-amber-500 dark:text-amber-400',
  info: 'text-blue-500 dark:text-blue-400'
}

const typeIcons = {
  success: 'check_circle',
  error: 'error_outline',
  warning: 'warning_amber',
  info: 'info'
}
</script>
