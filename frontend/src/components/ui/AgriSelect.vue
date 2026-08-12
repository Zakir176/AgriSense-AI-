<template>
  <div ref="selectRef" class="flex flex-col w-full gap-1.5 relative select-none animate-scale-in">
    <!-- Label -->
    <label
      v-if="label"
      class="text-xs font-bold tracking-wide text-gray-500 uppercase dark:text-gray-400"
    >
      {{ label }}
    </label>

    <!-- Trigger Button -->
    <div
      @click="toggleDropdown"
      :class="[
        'flex items-center justify-between text-sm font-medium w-full px-4 py-2.5 rounded-xl border transition-all duration-205 cursor-pointer bg-white dark:bg-darkbg-50/50 text-gray-900 dark:text-white',
        disabled ? 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-darkbg-100' : 'hover:border-gray-300 dark:hover:border-gray-700',
        isOpen ? 'border-primary-500 ring-4 ring-primary-500/10 dark:border-primary-400 dark:ring-primary-400/10' : 'border-gray-250 dark:border-gray-800',
        error ? 'border-status-danger ring-2 ring-status-danger/10' : '',
        success ? 'border-status-success ring-2 ring-status-success/10' : ''
      ]"
    >
      <span v-if="selectedLabel" class="truncate">{{ selectedLabel }}</span>
      <span v-else class="text-gray-400 dark:text-gray-600 truncate">{{ placeholder }}</span>

      <!-- Animated Chevron -->
      <span
        class="shrink-0 material-icons-outlined text-gray-450 dark:text-gray-500 text-[18px] transition-transform duration-200"
        :class="{ 'rotate-180': isOpen }"
      >
        expand_more
      </span>
    </div>

    <!-- Dropdown Options Overlay -->
    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="absolute left-0 right-0 z-50 mt-14.5 bg-white dark:bg-[#2c2c30] border border-gray-200 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden focus:outline-none flex flex-col max-h-60"
      >
        <!-- Search bar inside dropdown -->
        <div v-if="searchable" class="p-2 border-b border-gray-100 dark:border-gray-800 shrink-0">
          <div class="relative flex items-center">
            <span class="absolute left-2.5 material-icons-outlined text-[15px] text-gray-400 pointer-events-none">search</span>
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              class="w-full text-xs font-semibold pl-9 pr-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-850 dark:bg-darkbg-100 text-gray-800 dark:text-white outline-none focus:border-primary-500 dark:focus:border-primary-400"
              @click.stop
            />
          </div>
        </div>

        <!-- Scrollable Options List -->
        <ul class="overflow-y-auto py-1 divide-y divide-gray-50 dark:divide-gray-800/40">
          <li
            v-if="filteredOptions.length === 0"
            class="px-4 py-3 text-xs text-center text-gray-400 dark:text-gray-500"
          >
            No matches found
          </li>
          <li
            v-for="opt in filteredOptions"
            :key="opt.value"
            @click="selectOption(opt.value)"
            class="px-4 py-2.5 text-sm font-medium transition cursor-pointer flex items-center justify-between text-gray-750 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-primary-950/40 hover:text-primary-700 dark:hover:text-primary-400"
            :class="{ 'bg-primary-50/50 text-primary-700 dark:bg-primary-950/20 dark:text-primary-400': opt.value === modelValue }"
          >
            <span class="truncate">{{ opt.label }}</span>
            <span
              v-if="opt.value === modelValue"
              class="material-icons-outlined text-primary-600 dark:text-primary-400 text-[16px]"
            >
              check
            </span>
          </li>
        </ul>
      </div>
    </Transition>

    <!-- Error description -->
    <Transition name="fade">
      <p
        v-if="error"
        class="text-xs font-semibold text-status-danger mt-0.5"
      >
        {{ error }}
      </p>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  searchable: {
    type: Boolean,
    default: false
  },
  disabled: {
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
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectRef = ref(null)
const searchInput = ref(null)
const isOpen = ref(false)
const searchQuery = ref('')

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

// Map array items to uniform objects
const formattedOptions = computed(() => {
  return props.options.map(opt => {
    if (typeof opt === 'object' && opt !== null) {
      // support object layout
      return {
        label: opt.label !== undefined ? opt.label : opt.name || String(opt.value),
        value: opt.value !== undefined ? opt.value : opt.id || opt
      }
    }
    return { label: String(opt), value: opt }
  })
})

// Filter option values dynamically
const filteredOptions = computed(() => {
  if (!searchQuery.value) return formattedOptions.value
  const query = searchQuery.value.toLowerCase()
  return formattedOptions.value.filter(opt =>
    opt.label.toLowerCase().includes(query)
  )
})

// Active chosen element text
const selectedLabel = computed(() => {
  const selected = formattedOptions.value.find(opt => opt.value === props.modelValue)
  return selected ? selected.label : ''
})

const selectOption = (val) => {
  emit('update:modelValue', val)
  emit('change', val)
  isOpen.value = false
}

// Click outside closing logic
const handleClickOutside = (event) => {
  if (selectRef.value && !selectRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

// Focus on search input when opening
watch(isOpen, (newVal) => {
  if (newVal) {
    searchQuery.value = ''
    if (props.searchable) {
      nextTick(() => {
        searchInput.value?.focus()
      })
    }
  }
})

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.18s ease, transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

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
