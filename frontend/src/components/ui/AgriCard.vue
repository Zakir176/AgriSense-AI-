<template>
  <div
    class="rounded-2xl border transition-all duration-300 overflow-hidden bg-white dark:bg-darkbg-50/70 border-gray-200 dark:border-gray-800"
    :class="[
      paddingClasses[padding] || paddingClasses.md,
      {
        'hover:-translate-y-1 hover:shadow-lg': hoverLift,
        'shadow-sm': !hoverLift,
        'glass-panel bg-white/70 dark:bg-darkbg-50/75': glass
      }
    ]"
  >
    <!-- Header Slot -->
    <div
      v-if="$slots.header"
      class="border-b border-gray-150 dark:border-gray-800 px-6 py-4 flex items-center justify-between"
    >
      <slot name="header" />
    </div>

    <!-- Body content (default slot) -->
    <div class="flex-1">
      <slot />
    </div>

    <!-- Footer Slot -->
    <div
      v-if="$slots.footer"
      class="border-t border-gray-150 dark:border-gray-800 px-6 py-4 bg-gray-50/50 dark:bg-darkbg-100/30 flex items-center"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  hoverLift: {
    type: Boolean,
    default: false
  },
  glass: {
    type: Boolean,
    default: false
  },
  padding: {
    type: String,
    default: 'md',
    validator: (val) => ['none', 'sm', 'md', 'lg'].includes(val)
  }
})

const paddingClasses = {
  none: 'p-0',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8'
}
</script>
