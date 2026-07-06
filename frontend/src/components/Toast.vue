<template>
  <div class="fixed top-5 right-5 z-[100] flex flex-col gap-3 pointer-events-none w-full max-w-sm px-4 md:px-0">
    <TransitionGroup 
      name="toast" 
      tag="div" 
      class="flex flex-col gap-3"
    >
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-lg border backdrop-blur-md transition-all duration-300"
        :class="{
          'bg-white/95 dark:bg-darkbg-50/95 border-emerald-200 dark:border-emerald-900/40 text-emerald-800 dark:text-emerald-300': toast.type === 'success',
          'bg-white/95 dark:bg-darkbg-50/95 border-red-200 dark:border-red-900/40 text-red-800 dark:text-red-300': toast.type === 'error',
          'bg-white/95 dark:bg-darkbg-50/95 border-amber-200 dark:border-amber-900/40 text-amber-800 dark:text-amber-300': toast.type === 'warning',
          'bg-white/95 dark:bg-darkbg-50/95 border-blue-200 dark:border-blue-900/40 text-blue-800 dark:text-blue-300': toast.type === 'info',
        }"
      >
        <div class="mt-0.5 shrink-0">
          <span v-if="toast.type === 'success'" class="material-icons-outlined text-[20px] text-emerald-500">check_circle</span>
          <span v-else-if="toast.type === 'error'" class="material-icons-outlined text-[20px] text-red-500">error_outline</span>
          <span v-else-if="toast.type === 'warning'" class="material-icons-outlined text-[20px] text-amber-500">warning_amber</span>
          <span v-else class="material-icons-outlined text-[20px] text-blue-500">info</span>
        </div>
        
        <div class="flex-1 text-sm font-medium pr-2">
          {{ toast.message }}
        </div>

        <button 
          @click="removeToast(toast.id)"
          class="shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
        >
          <span class="material-icons-outlined text-[18px]">close</span>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts, removeToast } = useToast()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}
.toast-leave-active {
  position: absolute;
  width: 100%;
}
</style>
