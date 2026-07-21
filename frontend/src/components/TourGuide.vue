<template>
  <div v-if="store.tour.active" class="fixed inset-0 z-[99990] overflow-hidden pointer-events-none">
    <!-- Click-blocking layer under the tour to prevent misclicks during tutorial -->
    <div class="fixed inset-0 bg-transparent pointer-events-auto" @click.stop></div>

    <!-- Backdrop overlay with a dynamic cutout highlighted shape -->
    <div :style="overlayStyle"></div>

    <!-- Tooltip dialog box -->
    <div 
      v-if="targetBounds"
      :style="tooltipStyle"
      class="bg-white dark:bg-[#1a201c] border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-2xl pointer-events-auto flex flex-col justify-between min-h-[160px]"
    >
      <!-- Title & Progress -->
      <div class="space-y-1.5">
        <div class="flex justify-between items-center">
          <span class="text-[10px] font-black text-primary-650 dark:text-primary-400 uppercase tracking-widest">
            Step {{ store.tour.currentStep + 1 }} of {{ store.tour.steps.length }}
          </span>
          <button 
            @click="skipTour" 
            class="text-[10px] text-gray-400 hover:text-gray-600 dark:hover:text-white transition uppercase font-bold cursor-pointer"
          >
            {{ $t('tour.skip') }}
          </button>
        </div>
        <h3 class="text-sm font-black text-gray-900 dark:text-white leading-tight">
          {{ $t(currentStepObj.titleKey) }}
        </h3>
        <p class="text-xs text-gray-550 dark:text-gray-400 leading-relaxed font-semibold">
          {{ $t(currentStepObj.contentKey) }}
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-between pt-4 mt-2 border-t border-gray-100 dark:border-gray-800">
        <button 
          v-if="store.tour.currentStep > 0"
          @click="prevStep"
          class="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-gray-200 dark:border-gray-850 hover:bg-gray-50 dark:hover:bg-darkbg-100 text-xs font-bold text-gray-650 dark:text-gray-450 transition cursor-pointer"
        >
          <span class="material-icons-outlined text-sm">chevron_left</span>
          {{ $t('tour.prev') }}
        </button>
        <div v-else></div> <!-- Spacer -->

        <button 
          @click="nextStep"
          class="flex items-center gap-1 px-4 py-1.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-black transition cursor-pointer shadow-md shadow-primary-500/10"
        >
          <span>{{ isLastStep ? $t('tour.finish') : $t('tour.next') }}</span>
          <span class="material-icons-outlined text-sm" v-if="!isLastStep">chevron_right</span>
          <span class="material-icons-outlined text-sm" v-else>done</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { store } from '../services/store'
import { useToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const targetBounds = ref(null)
const resizeObserver = ref(null)

const currentStepObj = computed(() => {
  return store.tour.steps[store.tour.currentStep]
})

const isLastStep = computed(() => {
  return store.tour.currentStep === store.tour.steps.length - 1
})

const overlayStyle = computed(() => {
  if (!targetBounds.value) return { display: 'none' }
  const pad = 6
  return {
    position: 'fixed',
    top: `${targetBounds.value.top - pad}px`,
    left: `${targetBounds.value.left - pad}px`,
    width: `${targetBounds.value.width + pad * 2}px`,
    height: `${targetBounds.value.height + pad * 2}px`,
    borderRadius: '16px',
    boxShadow: '0 0 0 9999px rgba(10, 15, 12, 0.70), 0 0 16px 2px rgba(16, 185, 129, 0.8)',
    zIndex: '99998',
    pointerEvents: 'none',
    transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)'
  }
})

const tooltipStyle = computed(() => {
  if (!targetBounds.value) return { display: 'none' }
  const pad = 12
  const bounds = targetBounds.value
  const width = 310
  const height = 180

  let top = 0
  let left = 0

  const placement = currentStepObj.value.placement || 'bottom'

  if (placement === 'bottom') {
    top = bounds.bottom + pad
    left = bounds.left + (bounds.width - width) / 2
  } else if (placement === 'top') {
    top = bounds.top - height - pad
    left = bounds.left + (bounds.width - width) / 2
  } else if (placement === 'left') {
    top = bounds.top + (bounds.height - height) / 2
    left = bounds.left - width - pad
  } else if (placement === 'right') {
    top = bounds.top + (bounds.height - height) / 2
    left = bounds.right + pad
  }

  // Viewport bounds protection
  top = Math.max(12, Math.min(window.innerHeight - height - 12, top))
  left = Math.max(12, Math.min(window.innerWidth - width - 12, left))

  return {
    position: 'fixed',
    top: `${top}px`,
    left: `${left}px`,
    width: `${width}px`,
    zIndex: '99999',
    transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)'
  }
})

const waitForElement = (selector, timeout = 2500) => {
  return new Promise((resolve) => {
    const el = document.querySelector(selector)
    if (el) return resolve(el)

    const startTime = Date.now()
    const timer = setInterval(() => {
      const found = document.querySelector(selector)
      if (found || Date.now() - startTime > timeout) {
        clearInterval(timer)
        resolve(found || null)
      }
    }, 50)
  })
}

const recalculateBounds = async () => {
  if (!store.tour.active) {
    targetBounds.value = null
    return
  }

  const step = currentStepObj.value
  if (!step) return

  // If routes don't match, trigger redirect first
  if (route.path !== step.route) {
    router.push(step.route)
    // Wait for route changes to complete layout transitions
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 350))
  }

  const el = await waitForElement(step.targetSelector)
  if (el) {
    targetBounds.value = el.getBoundingClientRect()
    // Scroll element into view smoothly if not fully visible
    el.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  } else {
    console.warn(`[Tour] Target element not found in DOM: ${step.targetSelector}`)
    targetBounds.value = null
    // Auto-advance if element is missing to prevent lock-ups
    nextStep()
  }
}

const nextStep = async () => {
  if (isLastStep.value) {
    endTour(true)
  } else {
    store.tour.currentStep++
  }
}

const prevStep = () => {
  if (store.tour.currentStep > 0) {
    store.tour.currentStep--
  }
}

const skipTour = () => {
  endTour(false)
}

const endTour = (completed) => {
  store.tour.active = false
  store.tour.currentStep = 0
  targetBounds.value = null
  localStorage.setItem('agrisense_onboarded', 'true')
  if (completed) {
    toast.success('Onboarding Farm Tour completed successfully!')
  }
}

// Watchers
watch(() => store.tour.active, (isActive) => {
  if (isActive) {
    recalculateBounds()
  } else {
    targetBounds.value = null
  }
})

watch(() => store.tour.currentStep, () => {
  recalculateBounds()
})

watch(() => route.path, () => {
  // Recalculate if route changed by navigation during tour
  if (store.tour.active) {
    setTimeout(recalculateBounds, 100)
  }
})

// Lifecycle listeners
onMounted(() => {
  window.addEventListener('resize', recalculateBounds)
  window.addEventListener('scroll', recalculateBounds, true)
  if (store.tour.active) {
    recalculateBounds()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', recalculateBounds)
  window.removeEventListener('scroll', recalculateBounds, true)
})
</script>
