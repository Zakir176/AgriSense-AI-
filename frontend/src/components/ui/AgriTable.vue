<template>
  <div class="w-full overflow-x-auto rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-darkbg-50/50 shadow-sm animate-scale-in">
    <table class="w-full text-left border-collapse text-sm">
      <!-- Table Header -->
      <thead>
        <tr class="border-b border-gray-150 dark:border-gray-800 bg-gray-50/50 dark:bg-darkbg-100/20 text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
          <th
            v-for="header in headers"
            :key="header.value"
            class="px-6 py-4.5 transition-colors select-none whitespace-nowrap"
            :class="[
              header.align === 'right' ? 'text-right' : header.align === 'center' ? 'text-center' : 'text-left',
              { 'cursor-pointer hover:bg-gray-100/55 dark:hover:bg-darkbg-50/80': header.sortable }
            ]"
            @click="header.sortable && handleSort(header.value)"
          >
            <div class="inline-flex items-center gap-1.5 justify-start" :class="{ 'flex-row-reverse w-full': header.align === 'right' }">
              <span>{{ header.text }}</span>
              <span v-if="header.sortable" class="material-icons-outlined text-[14px] text-gray-400">
                {{ sortBy === header.value ? (sortDesc ? 'arrow_downward' : 'arrow_upward') : 'import_export' }}
              </span>
            </div>
          </th>
        </tr>
      </thead>

      <!-- Table Body -->
      <tbody class="divide-y divide-gray-150 dark:divide-gray-850">
        <!-- Loading State (Skeleton Rows) -->
        <template v-if="loading">
          <tr v-for="rowIndex in 3" :key="rowIndex" class="transition-colors">
            <td v-for="header in headers" :key="header.value" class="px-6 py-4.5">
              <AgriSkeleton type="text" :class="header.align === 'right' ? 'ml-auto w-12' : 'w-24'" />
            </td>
          </tr>
        </template>

        <!-- Empty State -->
        <tr v-else-if="items.length === 0">
          <td :colspan="headers.length" class="px-6 py-12 text-center text-gray-400 dark:text-gray-500">
            <span class="material-icons-outlined text-4xl block mb-2 opacity-50">inbox</span>
            <p class="font-medium text-xs">No records available</p>
          </td>
        </tr>

        <!-- Standard Items Rows -->
        <tr
          v-else
          v-for="(item, itemIndex) in items"
          :key="item.id || itemIndex"
          class="hover:bg-gray-50/50 dark:hover:bg-darkbg-100/20 transition-all duration-150"
          :class="{ 'bg-gray-50/30 dark:bg-darkbg-50/10': striped && itemIndex % 2 === 1 }"
        >
          <td
            v-for="header in headers"
            :key="header.value"
            class="px-6 py-4 text-gray-755 dark:text-gray-300 font-semibold whitespace-nowrap"
            :class="[
              header.align === 'right' ? 'text-right' : header.align === 'center' ? 'text-center' : 'text-left'
            ]"
          >
            <!-- Dynamic Slot for custom rendering, fallback to raw value -->
            <slot :name="header.value" :item="item" :index="itemIndex">
              {{ item[header.value] !== undefined && item[header.value] !== null ? item[header.value] : '—' }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  headers: {
    type: Array,
    required: true
  },
  items: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  striped: {
    type: Boolean,
    default: false
  },
  sortBy: {
    type: String,
    default: ''
  },
  sortDesc: {
    type: Boolean,
    default: false
  }
})

import AgriSkeleton from './AgriSkeleton.vue'

const emit = defineEmits(['sort'])

const handleSort = (field) => {
  let isDesc = false
  if (props.sortBy === field) {
    isDesc = !props.sortDesc
  }
  emit('sort', { field, isDesc })
}
</script>
