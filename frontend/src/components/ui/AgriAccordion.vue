<template>
  <div class="border border-gray-200 dark:border-gray-850 rounded-xl overflow-hidden bg-white dark:bg-darkbg-50/50 transition-colors duration-200">
    <!-- Trigger Header -->
    <div
      @click="toggle"
      class="flex items-center justify-between px-5 py-4.5 cursor-pointer hover:bg-gray-50/50 dark:hover:bg-darkbg-50/80 transition-colors select-none"
    >
      <div class="flex items-center gap-3">
        <span v-if="icon" class="material-icons-outlined text-gray-500 dark:text-gray-400 text-[18px] shrink-0">
          {{ icon }}
        </span>
        <slot name="title">
          <span class="font-bold text-sm text-gray-900 dark:text-white">{{ title }}</span>
        </slot>
      </div>

      <!-- Rotating Chevron -->
      <span
        class="material-icons-outlined text-gray-450 dark:text-gray-500 text-[18px] transition-transform duration-200 shrink-0"
        :class="{ 'rotate-180': open }"
      >
        expand_more
      </span>
    </div>

    <!-- Collapsible Body Content -->
    <Transition
      name="accordion"
      @before-enter="beforeEnter"
      @enter="enter"
      @after-enter="afterEnter"
      @before-leave="beforeLeave"
      @leave="leave"
      @after-leave="afterLeave"
    >
      <div v-show="open" class="overflow-hidden">
        <div class="border-t border-gray-150 dark:border-gray-850 px-5 py-4 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
          <slot />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  modelValue: {
    type: Boolean,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'toggle'])

const internalOpen = ref(false)

const open = computed(() => {
  return props.modelValue !== null ? props.modelValue : internalOpen.value
})

const toggle = () => {
  const nextVal = !open.value
  if (props.modelValue !== null) {
    emit('update:modelValue', nextVal)
  } else {
    internalOpen.value = nextVal
  }
  emit('toggle', nextVal)
}

import { computed } from 'vue'

// Custom height-based javascript hooks for the transition of slide-down and slide-up
const beforeEnter = (el) => {
  el.style.height = '0'
}

const enter = (el) => {
  el.style.height = el.scrollHeight + 'px'
  el.style.transition = 'height 0.22s cubic-bezier(0.16, 1, 0.3, 1)'
}

const afterEnter = (el) => {
  el.style.height = 'auto'
}

const beforeLeave = (el) => {
  el.style.height = el.scrollHeight + 'px'
}

const leave = (el) => {
  // force layout repaint
  el.offsetHeight // eslint-disable-line no-unused-expressions
  el.style.height = '0'
  el.style.transition = 'height 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
}

const afterLeave = (el) => {
  el.style.height = ''
}
</script>

<style scoped>
/* Scoped fallback animation rules if needed, JS hooks are preferred for scrollHeight */
</style>
