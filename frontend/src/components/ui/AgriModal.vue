<template>
  <Teleport to="body">
    <!-- Overlay backdrop -->
    <Transition name="modal-fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 dark:bg-black/80 backdrop-blur-sm pointer-events-auto"
        @click="onBackdropClick"
        aria-modal="true"
        role="dialog"
      >
        <!-- Modal content card -->
        <Transition name="modal-scale">
          <div
            v-if="show"
            class="w-full max-w-lg bg-white dark:bg-[#1b1b1e] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden"
            @click.stop
          >
            <!-- Header slot -->
            <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between shrink-0">
              <slot name="header">
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">
                  {{ title }}
                </h3>
              </slot>
              
              <!-- Close cross button -->
              <button
                @click="$emit('close')"
                class="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors focus-ring"
                aria-label="Close modal"
              >
                <span class="material-icons-outlined text-[20px] block">close</span>
              </button>
            </div>

            <!-- Body slot -->
            <div class="px-6 py-5 overflow-y-auto flex-1 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
              <slot />
            </div>

            <!-- Footer slot -->
            <div
              v-if="$slots.footer"
              class="px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-darkbg-50/30 flex items-center justify-end gap-3 shrink-0"
            >
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  closeOnEsc: {
    type: Boolean,
    default: true
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const onBackdropClick = () => {
  if (props.closeOnBackdrop) {
    emit('close')
  }
}

const handleEsc = (e) => {
  if (props.show && props.closeOnEsc && e.key === 'Escape') {
    emit('close')
  }
}

// Prevent body scroll when modal is active
watch(() => props.show, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  window.addEventListener('keydown', handleEsc)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEsc)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Backdrop fade animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.22s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Modal scaling slide-up animation */
.modal-scale-enter-active,
.modal-scale-leave-active {
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.modal-scale-enter-from,
.modal-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(12px);
}
</style>
