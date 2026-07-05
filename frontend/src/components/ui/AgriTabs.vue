<template>
  <div class="border-b border-gray-200 dark:border-gray-800 w-full mb-6">
    <nav class="flex space-x-6 overflow-x-auto -mb-px" aria-label="Tabs">
      <button
        v-for="tab in formattedTabs"
        :key="tab.value"
        @click="selectTab(tab.value)"
        class="group relative py-4 px-1 text-sm font-bold border-b-2 whitespace-nowrap transition-all duration-200 focus-ring cursor-pointer flex items-center gap-2"
        :class="[
          modelValue === tab.value
            ? 'border-primary-600 text-primary-700 dark:border-primary-400 dark:text-primary-400'
            : 'border-transparent text-gray-550 hover:text-gray-900 hover:border-gray-300 dark:text-gray-400 dark:hover:text-white dark:hover:border-gray-700'
        ]"
      >
        <!-- Icon -->
        <span
          v-if="tab.icon"
          class="material-icons-outlined text-[18px] leading-none shrink-0"
          :class="[
            modelValue === tab.value
              ? 'text-primary-600 dark:text-primary-400'
              : 'text-gray-400 group-hover:text-gray-600 dark:text-gray-500 dark:group-hover:text-gray-300'
          ]"
        >
          {{ tab.icon }}
        </span>

        <!-- Label -->
        <span>{{ tab.label }}</span>

        <!-- Indicator underline bubble for a nice glow/micro-interaction -->
        <span
          v-if="modelValue === tab.value"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500 rounded-full dark:bg-primary-400 transition-all duration-300"
        ></span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tabs: {
    type: Array,
    required: true
  },
  modelValue: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const formattedTabs = computed(() => {
  return props.tabs.map(tab => {
    if (typeof tab === 'object' && tab !== null) {
      return {
        label: tab.label || tab.name || String(tab.value),
        value: tab.value,
        icon: tab.icon || ''
      }
    }
    return { label: String(tab), value: tab, icon: '' }
  })
})

const selectTab = (val) => {
  emit('update:modelValue', val)
}
</script>
