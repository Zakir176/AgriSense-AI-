<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="relative inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 active:scale-95 focus-ring select-none cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100"
    :class="[
      variantClasses[variant] || variantClasses.primary,
      sizeClasses[size] || sizeClasses.md,
      { 'pr-10': loading && iconPosition === 'right', 'pl-10': loading && iconPosition === 'left' }
    ]"
    v-bind="$attrs"
  >
    <!-- Loading Spinner -->
    <span
      v-if="loading"
      class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center"
    >
      <span class="animate-spin h-5 w-5 border-2 border-current border-t-transparent rounded-full"></span>
    </span>

    <!-- Content Wrapper (Hidden during loading if needed, or faded) -->
    <span :class="['flex items-center gap-2 transition-opacity', { 'opacity-0': loading }]">
      <!-- Icon Left -->
      <span 
        v-if="icon && iconPosition === 'left'" 
        class="material-icons-outlined text-[1.15em] leading-none shrink-0"
      >
        {{ icon }}
      </span>

      <slot />

      <!-- Icon Right -->
      <span 
        v-if="icon && iconPosition === 'right'" 
        class="material-icons-outlined text-[1.15em] leading-none shrink-0"
      >
        {{ icon }}
      </span>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (val) => ['primary', 'secondary', 'outline', 'ghost', 'destructive'].includes(val)
  },
  size: {
    type: String,
    default: 'md',
    validator: (val) => ['sm', 'md', 'lg'].includes(val)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'button'
  },
  icon: {
    type: String,
    default: ''
  },
  iconPosition: {
    type: String,
    default: 'left'
  }
})

// Variant-specific styling rules using our nature-inspired palette
const variantClasses = {
  primary: 'bg-primary-600 hover:bg-primary-500 text-white shadow-sm hover:shadow-md border border-primary-700/10 hover:border-primary-600/10',
  secondary: 'bg-secondary-100 hover:bg-secondary-200 text-secondary-700 shadow-sm border border-secondary-200/50 dark:bg-secondary-700/20 dark:hover:bg-secondary-700/30 dark:text-secondary-200 dark:border-secondary-600/20',
  outline: 'bg-transparent border border-gray-250 hover:bg-gray-50 text-gray-700 dark:border-gray-800 dark:hover:bg-darkbg-50/50 dark:text-gray-300',
  ghost: 'bg-transparent hover:bg-gray-100 text-gray-650 hover:text-gray-900 dark:hover:bg-darkbg-50/50 dark:text-gray-400 dark:hover:text-white',
  destructive: 'bg-status-danger text-white shadow-sm hover:bg-red-500 hover:shadow-md'
}

// Size-specific sizes
const sizeClasses = {
  sm: 'px-4 py-2 text-xs gap-1.5 rounded-lg whitespace-nowrap shrink-0',
  md: 'px-5 py-2.5 text-sm gap-2 rounded-xl whitespace-nowrap shrink-0',
  lg: 'px-7 py-3 text-base gap-2.5 rounded-2xl whitespace-nowrap shrink-0'
}
</script>
