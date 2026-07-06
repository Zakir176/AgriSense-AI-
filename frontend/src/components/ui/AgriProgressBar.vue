<template>
  <div class="w-full flex flex-col gap-1.5 animate-scale-in">
    <!-- Optional Labels -->
    <div v-if="label || showValue" class="flex justify-between items-center text-xs font-bold text-gray-500 dark:text-gray-400 select-none">
      <span v-if="label" class="uppercase tracking-wider">{{ label }}</span>
      <span v-if="showValue" class="font-mono">{{ percentage }}%</span>
    </div>

    <!-- Progress Bar Track -->
    <div
      class="w-full bg-gray-200 dark:bg-darkbg-200 rounded-full overflow-hidden relative"
      :class="heightClass"
    >
      <!-- Progress Bar Indicator -->
      <div
        class="h-full rounded-full transition-all duration-300 ease-out"
        :class="[
          colorClass || 'bg-primary-500 dark:bg-primary-400',
          { 'progress-striped': animated }
        ]"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    required: true
  },
  max: {
    type: Number,
    default: 100
  },
  label: {
    type: String,
    default: ''
  },
  showValue: {
    type: Boolean,
    default: false
  },
  animated: {
    type: Boolean,
    default: false
  },
  colorClass: {
    type: String,
    default: ''
  },
  heightClass: {
    type: String,
    default: 'h-2.5'
  }
})

const percentage = computed(() => {
  if (props.max <= 0) return 0
  return Math.min(100, Math.max(0, Math.round((props.value / props.max) * 100)))
})
</script>

<style scoped>
/* Stripe patterns and animation keyframes for progress bar */
.progress-striped {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
  animation: progress-bar-stripes 1s linear infinite;
}

@keyframes progress-bar-stripes {
  from {
    background-position: 1rem 0;
  }
  to {
    background-position: 0 0;
  }
}
</style>
