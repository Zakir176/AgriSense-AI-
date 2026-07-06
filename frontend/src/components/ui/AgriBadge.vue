<template>
  <span
    class="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-full border tracking-wide uppercase select-none transition-all duration-200"
    :class="[
      variantClasses[variant] || variantClasses.info,
      { 'animate-pulse-glow': pulse && variant === 'warning', 'animate-pulse-critical': pulse && variant === 'critical' }
    ]"
  >
    <!-- Dot with outer pulsing effect if pulse is enabled -->
    <span v-if="pulse" class="relative flex h-1.5 w-1.5 shrink-0">
      <span
        class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
        :class="dotColorClasses[variant] || 'bg-blue-400'"
      ></span>
      <span
        class="relative inline-flex rounded-full h-1.5 w-1.5"
        :class="dotColorClasses[variant] || 'bg-blue-500'"
      ></span>
    </span>

    <!-- Optional Badge Icon -->
    <span
      v-if="icon"
      class="material-icons-outlined text-[13px] leading-none shrink-0"
    >
      {{ icon }}
    </span>

    <slot />
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'info',
    validator: (val) => ['active', 'success', 'warning', 'critical', 'info'].includes(val)
  },
  pulse: {
    type: Boolean,
    default: false
  },
  icon: {
    type: String,
    default: ''
  }
})

// Curated colors for agricultural context
const variantClasses = {
  active: 'bg-emerald-50 text-emerald-700 border-emerald-200/50 dark:bg-emerald-950/30 dark:text-emerald-450 dark:border-emerald-900/30',
  success: 'bg-primary-50 text-primary-700 border-primary-200/50 dark:bg-primary-950/30 dark:text-primary-450 dark:border-primary-900/30',
  warning: 'bg-amber-50 text-amber-700 border-amber-200/50 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-900/30',
  critical: 'bg-red-50 text-status-danger border-red-200/50 dark:bg-red-950/30 dark:text-red-400 dark:border-red-900/30',
  info: 'bg-accent-50 text-accent-600 border-accent-100 dark:bg-accent-950/30 dark:text-accent-500 dark:border-accent-900/30'
}

const dotColorClasses = {
  active: 'bg-emerald-500',
  success: 'bg-primary-500',
  warning: 'bg-amber-500',
  critical: 'bg-red-500',
  info: 'bg-accent-500'
}
</script>
