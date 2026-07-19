<template>
  <div
    class="glass-panel border-white/20 dark:border-darkbg-50/20 rounded-2xl p-5 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-200 flex flex-col justify-between"
  >
    <!-- Skeleton Loading -->
    <div v-if="loading" class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="h-4 w-24 bg-gray-150 dark:bg-gray-800 rounded-md animate-shimmer"></div>
        <div class="h-8 w-8 bg-gray-150 dark:bg-gray-800 rounded-xl animate-shimmer"></div>
      </div>
      <div class="h-8 w-16 bg-gray-150 dark:bg-gray-800 rounded-md animate-shimmer"></div>
      <div class="h-3 w-32 bg-gray-150 dark:bg-gray-800 rounded-md animate-shimmer"></div>
    </div>

    <!-- Normal State -->
    <div v-else class="space-y-2">
      <!-- Title & Icon -->
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider select-none">
          {{ label }}
        </span>
        <div
          v-if="icon"
          class="h-8 w-8 rounded-xl flex items-center justify-center transition-all duration-300"
          :class="iconColorClass || 'bg-primary-50 dark:bg-primary-950/40 text-primary-600 dark:text-primary-400'"
        >
          <span class="material-icons-outlined text-[17px] leading-none">{{ icon }}</span>
        </div>
      </div>

      <!-- Stat Value (Count up animation) -->
      <div class="flex flex-wrap items-baseline gap-2">
        <span class="text-3xl font-black text-gray-900 dark:text-white tracking-tight tabular-nums">
          {{ prefix }}{{ formattedValue }}{{ suffix }}
        </span>
        <!-- Trend Indicator -->
        <span
          v-if="trend"
          class="inline-flex items-center gap-0.5 text-xs font-bold px-1.5 py-0.5 rounded-md"
          :class="[
            trendGood === true
              ? 'bg-primary-50 text-primary-700 dark:bg-primary-950/50 dark:text-primary-400'
              : trendGood === false
                ? 'bg-red-50 text-status-danger dark:bg-red-950/30 dark:text-red-400'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
          ]"
        >
          <span class="material-icons-outlined text-[12px] leading-none">
            {{ trendDirection === 'up' ? 'trending_up' : trendDirection === 'down' ? 'trending_down' : 'trending_flat' }}
          </span>
          {{ trend }}
        </span>
      </div>

      <!-- Bottom Subtext -->
      <div v-if="subtext" class="text-xs text-gray-500 dark:text-gray-450 truncate">
        {{ subtext }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: Number,
    required: true
  },
  decimals: {
    type: Number,
    default: 0
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  trend: {
    type: [String, Number],
    default: ''
  },
  trendDirection: {
    type: String,
    default: 'neutral', // 'up' | 'down' | 'neutral'
    validator: (val) => ['up', 'down', 'neutral'].includes(val)
  },
  trendGood: {
    type: Boolean,
    default: null // true: green, false: red, null: neutral gray
  },
  icon: {
    type: String,
    default: ''
  },
  iconColorClass: {
    type: String,
    default: ''
  },
  subtext: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const displayValue = ref(0)

// Helper to handle counting interpolation
const animateValue = (start, end, duration = 650) => {
  let startTime = null
  
  const step = (timestamp) => {
    if (!startTime) startTime = timestamp
    const progress = Math.min((timestamp - startTime) / duration, 1)
    const currentVal = progress * (end - start) + start
    displayValue.value = parseFloat(currentVal.toFixed(props.decimals))
    
    if (progress < 1) {
      window.requestAnimationFrame(step)
    } else {
      displayValue.value = end
    }
  }
  
  window.requestAnimationFrame(step)
}

watch(() => props.value, (newVal, oldVal) => {
  animateValue(oldVal || 0, newVal)
})

onMounted(() => {
  animateValue(0, props.value)
})

const formattedValue = computed(() => {
  return displayValue.value.toLocaleString(undefined, {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals
  })
})
</script>
