<template>
  <div class="bg-white dark:bg-[#1b1b1e] border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden animate-fade-in-up delay-250">
    
    <!-- ── Header Controls ── -->
    <div class="p-4 sm:p-6 border-b border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="flex items-center rounded-lg bg-gray-100 dark:bg-gray-800/50 p-1">
          <button @click="prevMonth" class="p-1.5 rounded hover:bg-white dark:hover:bg-gray-700 text-gray-500 transition-colors">
            <span class="material-icons-outlined text-[18px] block">chevron_left</span>
          </button>
          <span class="px-3 font-bold text-gray-800 dark:text-gray-200 min-w-[120px] text-center">
            {{ currentMonthName }} {{ currentYear }}
          </span>
          <button @click="nextMonth" class="p-1.5 rounded hover:bg-white dark:hover:bg-gray-700 text-gray-500 transition-colors">
            <span class="material-icons-outlined text-[18px] block">chevron_right</span>
          </button>
        </div>
        <AgriButton variant="ghost" size="sm" @click="goToToday">{{ $t('calendar.today') }}</AgriButton>
      </div>

      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Legend -->
        <div class="hidden md:flex items-center gap-3 mr-2 text-xs font-semibold text-gray-500 dark:text-gray-400">
          <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-500"></span>{{ $t('calendar.type_vaccine') }}</div>
          <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-blue-500"></span>{{ $t('calendar.type_medication') }}</div>
          <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-amber-500"></span>{{ $t('calendar.type_supplement') }}</div>
        </div>
        
        <AgriButton
          variant="primary"
          icon="event"
          @click="$emit('open-schedule')"
        >{{ $t('calendar.schedule_treatment') }}</AgriButton>
      </div>
    </div>

    <!-- ── Calendar Grid ── -->
    <div class="overflow-x-auto">
      <div class="min-w-[600px] w-full border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-darkbg-50/30 grid grid-cols-7">
        <div 
          v-for="day in weekDays" 
          :key="day"
          class="py-2.5 text-center text-[11px] font-bold text-gray-400 uppercase tracking-wider"
        >
          {{ day }}
        </div>
      </div>

      <div class="min-w-[600px] w-full grid grid-cols-7 border-l border-gray-100 dark:border-gray-800">
        <div 
          v-for="(cell, idx) in calendarCells" 
          :key="idx"
          @click="onCellClick(cell)"
          class="min-h-[100px] border-r border-b border-gray-100 dark:border-gray-800 p-2 transition-colors cursor-pointer group relative"
          :class="[
            cell.isCurrentMonth ? 'bg-white dark:bg-[#1b1b1e] hover:bg-gray-50 dark:hover:bg-gray-800/40' : 'bg-gray-50/50 dark:bg-darkbg-50/30 text-gray-400 dark:text-gray-600',
            cell.isToday ? 'ring-inset ring-2 ring-primary-500/50' : '',
            cell.isOverdue ? 'ring-inset ring-2 ring-red-500/30 bg-red-50/30 dark:bg-red-900/10' : ''
          ]"
        >
          <!-- Date & Age -->
          <div class="flex justify-between items-start">
            <span class="text-sm font-semibold" :class="cell.isCurrentMonth ? 'text-gray-900 dark:text-gray-200' : ''">
              {{ cell.date.getDate() }}
            </span>
            <span v-if="cell.flockAge !== null && cell.flockAge >= 0" class="text-[10px] font-bold text-gray-400 dark:text-gray-500">
              D{{ cell.flockAge }}
            </span>
          </div>

          <!-- Indicators -->
          <div class="mt-2 flex flex-wrap gap-1">
            <div 
              v-for="item in cell.items" 
              :key="item.id"
              class="w-2.5 h-2.5 rounded-full"
              :class="getTypeColor(item.treatment_type)"
              :title="item.title"
            ></div>
          </div>
          
          <!-- Overdue Badge (Small) -->
          <div v-if="cell.isOverdue" class="absolute bottom-2 right-2 flex">
             <span class="relative flex h-2.5 w-2.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Inline Day Detail Popover (Below Grid) ── -->
    <div v-if="selectedCell" class="bg-gray-50 dark:bg-darkbg-50 border-t border-gray-200 dark:border-gray-800 p-4 sm:p-6 animate-fade-in-up relative">
      <button @click="selectedCell = null" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
        <span class="material-icons-outlined text-[20px]">close</span>
      </button>
      
      <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">
        {{ formatDate(selectedCell.date) }} 
        <span v-if="selectedCell.flockAge !== null && selectedCell.flockAge >= 0" class="text-gray-500 font-normal">
          · Day {{ selectedCell.flockAge }}
        </span>
      </h3>
      
      <div v-if="selectedCell.items.length === 0" class="text-sm text-gray-500 italic">
        {{ $t('calendar.no_treatments') }}
      </div>
      
      <div v-else class="space-y-3">
        <div 
          v-for="item in selectedCell.items" 
          :key="item.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-white dark:bg-[#1b1b1e] border border-gray-200 dark:border-gray-800 rounded-xl"
        >
          <div class="flex items-start gap-3">
            <div class="mt-1 flex-shrink-0 w-3 h-3 rounded-full" :class="getTypeColor(item.treatment_type)"></div>
            <div>
              <p class="text-sm font-bold text-gray-900 dark:text-white">{{ item.title }}</p>
              <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2 mt-0.5">
                <span class="uppercase tracking-wider font-semibold">{{ item.treatment_type }}</span>
                <span v-if="item.dosage">• {{ item.dosage }}</span>
              </div>
              <p v-if="item.notes" class="text-xs italic text-gray-450 mt-1">{{ item.notes }}</p>
            </div>
          </div>
          
          <div class="flex items-center gap-2 sm:ml-auto">
            <!-- Status Badge -->
            <AgriBadge 
              :variant="item.status === 'completed' ? 'success' : item.status === 'skipped' ? 'warning' : item.scheduled_date < todayStr ? 'critical' : 'info'"
              :pulse="item.status === 'pending' && item.scheduled_date < todayStr"
            >
              {{ item.status === 'completed' ? $t('calendar.status_completed') : item.status === 'skipped' ? $t('calendar.status_skipped') : item.scheduled_date < todayStr ? $t('calendar.status_overdue') : $t('calendar.status_pending') }}
            </AgriBadge>

            <!-- Actions -->
            <template v-if="item.status === 'pending'">
              <AgriButton variant="outline" size="sm" icon="check" @click="$emit('mark-complete', item)">
                {{ $t('calendar.mark_complete') }}
              </AgriButton>
              <AgriButton variant="ghost" size="sm" icon="edit" @click="$emit('edit', item)" />
              <AgriButton variant="ghost" size="sm" icon="delete" class="text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20" @click="$emit('delete', item.id)" />
            </template>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AgriButton from './ui/AgriButton.vue'
import AgriBadge from './ui/AgriBadge.vue'

const props = defineProps({
  schedules: { type: Array, default: () => [] },
  batchStartDate: { type: String, default: null }
})

const emit = defineEmits(['open-schedule', 'edit', 'delete', 'mark-complete'])

const currentDate = ref(new Date())
const selectedCell = ref(null)

const todayStr = new Date().toISOString().split('T')[0]

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const currentMonthName = computed(() => monthNames[currentDate.value.getMonth()])
const currentYear = computed(() => currentDate.value.getFullYear())

// Generate grid cells
const calendarCells = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  
  // 0 = Sun, 1 = Mon ... adjust to make Mon = 0
  let startOffset = firstDayOfMonth.getDay() - 1
  if (startOffset === -1) startOffset = 6 // Sunday
  
  const cells = []
  
  // Previous month days
  for (let i = 0; i < startOffset; i++) {
    const d = new Date(year, month, -startOffset + i + 1)
    cells.push(createCellData(d, false))
  }
  
  // Current month days
  for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
    const d = new Date(year, month, i)
    cells.push(createCellData(d, true))
  }
  
  // Next month days to complete grid (42 cells total for 6 rows)
  const remaining = 42 - cells.length
  for (let i = 1; i <= remaining; i++) {
    const d = new Date(year, month + 1, i)
    cells.push(createCellData(d, false))
  }
  
  return cells
})

const createCellData = (date, isCurrentMonth) => {
  // Normalize date to local YYYY-MM-DD
  const offset = date.getTimezoneOffset() * 60000
  const dateStr = new Date(date.getTime() - offset).toISOString().split('T')[0]
  
  const isToday = dateStr === todayStr
  
  // Find items for this day
  const items = props.schedules.filter(s => s.scheduled_date === dateStr)
  
  const isOverdue = items.some(i => i.status === 'pending' && i.scheduled_date < todayStr)
  
  // Calculate flock age
  let flockAge = null
  if (props.batchStartDate) {
    const start = new Date(props.batchStartDate)
    start.setHours(0,0,0,0)
    const current = new Date(date)
    current.setHours(0,0,0,0)
    const diffTime = current - start
    if (diffTime >= 0) {
      flockAge = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }
  }

  return { date, dateStr, isCurrentMonth, isToday, items, isOverdue, flockAge }
}

const getTypeColor = (type) => {
  switch(type.toLowerCase()) {
    case 'vaccine': return 'bg-emerald-500'
    case 'medication': return 'bg-blue-500'
    case 'supplement': return 'bg-amber-500'
    default: return 'bg-gray-500'
  }
}

const onCellClick = (cell) => {
  if (cell.items.length > 0) {
    selectedCell.value = cell
  } else {
    // Open schedule modal for that date
    selectedCell.value = null
    emit('open-schedule', cell.dateStr)
  }
}

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  selectedCell.value = null
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  selectedCell.value = null
}

const goToToday = () => {
  currentDate.value = new Date()
  selectedCell.value = null
}

const formatDate = (date) => {
  return date.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
}
</script>
