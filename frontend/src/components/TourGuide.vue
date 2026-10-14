<template>
  <div
    v-if="store.tour.active"
    class="fixed inset-0 z-[99990] overflow-hidden pointer-events-none"
    role="presentation"
  >
    <!-- Input blocker: stops clicks, wheel and touch scrolling so the spotlight can't drift off its target -->
    <div
      class="fixed inset-0 bg-transparent pointer-events-auto touch-none"
      @click.stop
      @wheel.prevent
      @touchmove.prevent
    ></div>

    <!-- Spotlight cutout (collapses to a full-screen dim when a step has no target) -->
    <div class="tour-spot" :style="spotStyle" aria-hidden="true"></div>

    <!-- Tour card -->
    <div
      ref="cardRef"
      :style="cardStyle"
      class="tour-card pointer-events-auto flex flex-col bg-white/95 dark:bg-[#1a201c]/95 backdrop-blur-md border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl overflow-hidden"
      role="dialog"
      aria-modal="true"
      aria-live="polite"
      :aria-label="$t('tour.aria_label')"
    >
      <!-- Progress bar -->
      <div class="h-1 w-full bg-gray-100 dark:bg-gray-800 shrink-0">
        <div
          class="h-full bg-gradient-to-r from-primary-500 to-emerald-400 transition-all duration-300 ease-out"
          :style="{ width: progressPct + '%' }"
        ></div>
      </div>

      <div :key="store.tour.currentStep" class="tour-content flex-1 min-h-0 overflow-y-auto p-4 sm:p-5">
        <!-- Meta row -->
        <div class="flex items-center justify-between gap-3 mb-3">
          <span class="text-[10px] font-black text-primary-650 dark:text-primary-400 uppercase tracking-widest">
            {{ $t('tour.step_of', { current: store.tour.currentStep + 1, total: store.tour.steps.length }) }}
          </span>
          <button
            v-if="!isLastStep"
            @click="skipTour"
            class="min-h-[32px] px-2 -mr-2 text-[11px] text-gray-400 hover:text-gray-700 dark:hover:text-white transition uppercase font-bold cursor-pointer rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
          >
            {{ $t('tour.skip') }}
          </button>
        </div>

        <!-- Title + icon -->
        <div class="flex items-start gap-3" :class="isCentered ? 'flex-col items-center text-center' : ''">
          <div
            class="shrink-0 flex items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-emerald-500 text-white shadow-md shadow-primary-500/20"
            :class="isCentered ? 'h-14 w-14' : 'h-9 w-9'"
          >
            <span class="material-icons-outlined" :class="isCentered ? 'text-3xl' : 'text-lg'">{{ stepIcon }}</span>
          </div>
          <div class="min-w-0">
            <h3
              class="font-black text-gray-900 dark:text-white leading-tight"
              :class="isCentered ? 'text-lg' : 'text-sm sm:text-[15px]'"
            >
              {{ $t(`tour.steps.${currentStepObj.id}.title`) }}
            </h3>
            <p class="mt-1.5 text-xs sm:text-[13px] text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
              {{ $t(`tour.steps.${currentStepObj.id}.content`) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between gap-3 px-4 sm:px-5 py-3 border-t border-gray-100 dark:border-gray-800 shrink-0">
        <button
          v-if="store.tour.currentStep > 0"
          @click="prevStep"
          class="flex items-center gap-1 min-h-[40px] px-3 rounded-xl border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-white/5 text-xs font-bold text-gray-700 dark:text-gray-300 transition cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        >
          <span class="material-icons-outlined text-sm">chevron_left</span>
          {{ $t('tour.prev') }}
        </button>
        <div v-else></div>

        <button
          ref="nextBtnRef"
          @click="nextStep"
          class="flex items-center gap-1 min-h-[40px] px-5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-black transition cursor-pointer shadow-md shadow-primary-500/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary-500 dark:focus-visible:ring-offset-[#1a201c]"
        >
          <span>{{ isLastStep ? $t('tour.finish') : (store.tour.currentStep === 0 ? $t('tour.start') : $t('tour.next')) }}</span>
          <span class="material-icons-outlined text-sm">{{ isLastStep ? 'done' : 'chevron_right' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { store, TOUR_STORAGE_KEY } from '../services/store'
import { useToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { t } = useI18n()

// Layout constants
const MARGIN = 12            // min gap between card and viewport edge
const GAP = 14               // gap between spotlight and card
const SPOT_PAD = 8           // spotlight padding around the target
const MOBILE_BP = 640        // card becomes a top/bottom sheet below this
const SIDEBAR_BP = 768       // matches App.vue md breakpoint (sidebar is off-canvas below)

const STEP_ICONS = {
  welcome: 'agriculture',
  role: 'badge',
  toolbar: 'tune',
  sidebar: 'menu_open',
  alerts: 'notifications_active',
  quicklinks: 'bolt',
  batches: 'layers',
  feed: 'opacity',
  growth: 'show_chart',
  meds: 'vaccines',
  ai: 'videocam',
  audio: 'hearing',
  analytics: 'analytics',
  financial: 'payments',
  settings: 'settings',
  done: 'check_circle'
}

const cardRef = ref(null)
const nextBtnRef = ref(null)
const spot = ref(null)             // { top, left, width, height } of the visible target, or null
const cardPos = ref({ top: 0, left: 0, width: 340, sheet: false })
const isCentered = ref(true)

let runId = 0                      // invalidates stale async locate() runs
let targetEl = null
let measureRaf = 0
let settleTimers = []

const currentStepObj = computed(() => store.tour.steps[store.tour.currentStep])
const isLastStep = computed(() => store.tour.currentStep === store.tour.steps.length - 1)
const progressPct = computed(() => ((store.tour.currentStep + 1) / store.tour.steps.length) * 100)
const stepIcon = computed(() => STEP_ICONS[currentStepObj.value?.id] || 'help_outline')


// ── Styles ────────────────────────────────────────────────
const spotStyle = computed(() => {
  const s = spot.value
  if (!s) {
    // No target: zero-size box at screen centre whose shadow dims everything
    return {
      position: 'fixed',
      top: '50%',
      left: '50%',
      width: '0px',
      height: '0px',
      borderRadius: '16px',
      boxShadow: '0 0 0 9999px rgba(10, 15, 12, 0.72)',
      zIndex: 99998,
      pointerEvents: 'none'
    }
  }
  return {
    position: 'fixed',
    top: `${s.top - SPOT_PAD}px`,
    left: `${s.left - SPOT_PAD}px`,
    width: `${s.width + SPOT_PAD * 2}px`,
    height: `${s.height + SPOT_PAD * 2}px`,
    borderRadius: '16px',
    boxShadow: '0 0 0 9999px rgba(10, 15, 12, 0.72), 0 0 0 2px rgba(16, 185, 129, 0.9), 0 0 24px 4px rgba(16, 185, 129, 0.45)',
    zIndex: 99998,
    pointerEvents: 'none'
  }
})

const cardStyle = computed(() => {
  const p = cardPos.value
  if (p.sheet) {
    // Mobile: full-width sheet pinned to top or bottom
    const base = {
      position: 'fixed',
      left: `${MARGIN}px`,
      right: `${MARGIN}px`,
      maxHeight: '55vh',
      zIndex: 99999
    }
    return p.anchor === 'top'
      ? { ...base, top: `calc(${MARGIN}px + env(safe-area-inset-top, 0px))` }
      : { ...base, bottom: `calc(${MARGIN}px + env(safe-area-inset-bottom, 0px))` }
  }
  return {
    position: 'fixed',
    top: `${p.top}px`,
    left: `${p.left}px`,
    width: `${p.width}px`,
    maxHeight: `calc(100vh - ${MARGIN * 2}px)`,
    zIndex: 99999
  }
})

// ── Positioning ───────────────────────────────────────────
const positionCard = () => {
  const vw = window.innerWidth
  const vh = window.innerHeight
  const s = spot.value
  const card = cardRef.value
  const height = card ? card.offsetHeight : 220

  // Mobile: bottom sheet, or top sheet if the target lives in the lower half
  if (vw < MOBILE_BP) {
    if (!s) {
      // Centered card on small screens: keep it a sheet at the bottom for thumb reach
      cardPos.value = { sheet: true, anchor: 'bottom' }
    } else {
      const centerY = s.top + s.height / 2
      cardPos.value = { sheet: true, anchor: centerY > vh / 2 ? 'top' : 'bottom' }
    }
    isCentered.value = !s
    return
  }

  const width = Math.min(vw >= 1024 ? 380 : 340, vw - MARGIN * 2)

  if (!s) {
    cardPos.value = {
      sheet: false,
      width,
      top: Math.max(MARGIN, (vh - height) / 2),
      left: Math.max(MARGIN, (vw - width) / 2)
    }
    isCentered.value = true
    return
  }
  isCentered.value = false

  const r = {
    top: s.top - SPOT_PAD,
    left: s.left - SPOT_PAD,
    right: s.left + s.width + SPOT_PAD,
    bottom: s.top + s.height + SPOT_PAD
  }
  const cx = (r.left + r.right) / 2
  const cy = (r.top + r.bottom) / 2
  const clampX = (x) => Math.max(MARGIN, Math.min(vw - width - MARGIN, x))
  const clampY = (y) => Math.max(MARGIN, Math.min(vh - height - MARGIN, y))

  const candidates = {
    bottom: { fits: r.bottom + GAP + height <= vh - MARGIN, top: r.bottom + GAP, left: clampX(cx - width / 2) },
    top:    { fits: r.top - GAP - height >= MARGIN,         top: r.top - GAP - height, left: clampX(cx - width / 2) },
    right:  { fits: r.right + GAP + width <= vw - MARGIN,   top: clampY(cy - height / 2), left: r.right + GAP },
    left:   { fits: r.left - GAP - width >= MARGIN,         top: clampY(cy - height / 2), left: r.left - GAP - width }
  }
  const opposite = { top: 'bottom', bottom: 'top', left: 'right', right: 'left' }
  const preferred = currentStepObj.value.placement || 'bottom'
  const order = [preferred, opposite[preferred], 'bottom', 'top', 'right', 'left']
  const pick = order.find((k) => candidates[k].fits)

  if (pick) {
    cardPos.value = { sheet: false, width, top: candidates[pick].top, left: candidates[pick].left }
  } else {
    // Target is huge: float the card over its lower edge so it is always reachable
    cardPos.value = { sheet: false, width, top: clampY(vh - height - MARGIN), left: clampX(cx - width / 2) }
  }
}

const schedulePosition = async () => {
  await nextTick()
  requestAnimationFrame(positionCard)
}

// ── Target resolution & measuring ────────────────────────
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const waitForElement = (selector, timeout = 3000) =>
  new Promise((resolve) => {
    const existing = document.querySelector(selector)
    if (existing) return resolve(existing)
    const start = Date.now()
    const timer = setInterval(() => {
      const found = document.querySelector(selector)
      if (found || Date.now() - start > timeout) {
        clearInterval(timer)
        resolve(found || null)
      }
    }, 50)
  })

const resolveTarget = (step, el) => {
  if (!el) return null
  return step.closest ? (el.closest(step.closest) || el) : el
}

const measure = () => {
  cancelAnimationFrame(measureRaf)
  measureRaf = requestAnimationFrame(() => {
    if (!store.tour.active) return
    const step = currentStepObj.value
    if (!step || !step.targetSelector) return

    // Re-resolve if Vue re-rendered the node (v-if, route transition, etc.)
    if (!targetEl || !targetEl.isConnected) {
      targetEl = resolveTarget(step, document.querySelector(step.targetSelector))
    }
    if (!targetEl) {
      spot.value = null
      positionCard()
      return
    }

    const b = targetEl.getBoundingClientRect()
    const vw = window.innerWidth
    const vh = window.innerHeight
    // Clip to the viewport so huge targets still produce a sensible spotlight
    const top = Math.max(b.top, SPOT_PAD)
    const left = Math.max(b.left, SPOT_PAD)
    const bottom = Math.min(b.bottom, vh - SPOT_PAD)
    const right = Math.min(b.right, vw - SPOT_PAD)
    if (right - left < 4 || bottom - top < 4) {
      spot.value = null
    } else {
      spot.value = { top, left, width: right - left, height: bottom - top }
    }
    positionCard()
  })
}

const clearSettleTimers = () => {
  settleTimers.forEach(clearTimeout)
  settleTimers = []
}

const locate = async () => {
  const id = ++runId
  clearSettleTimers()
  if (!store.tour.active) return

  const step = currentStepObj.value
  if (!step) return

  // Mobile drawer: open for sidebar steps, close otherwise (App.vue reacts to this flag)
  const wasOpen = store.tour.sidebarOpen
  const wantOpen = !!step.needsSidebar
  store.tour.sidebarOpen = wantOpen
  const drawerMoving = window.innerWidth < SIDEBAR_BP && wasOpen !== wantOpen

  // Navigate if needed
  if (route.path !== step.route) {
    try { await router.push(step.route) } catch { /* duplicate/aborted nav is fine */ }
    await nextTick()
    await sleep(350)            // let page transition + data render settle
  } else if (drawerMoving) {
    await sleep(320)            // drawer slide animation
  }
  if (id !== runId) return

  targetEl = null
  if (!step.targetSelector) {
    spot.value = null
    isCentered.value = true
    schedulePosition()
    focusNext()
    return
  }

  const found = await waitForElement(step.targetSelector)
  if (id !== runId) return

  targetEl = resolveTarget(step, found)
  if (!targetEl) {
    // Never skip or lock up: fall back to a centered card
    console.warn(`[Tour] Target not found, showing centered card: ${step.targetSelector}`)
    spot.value = null
    isCentered.value = true
    schedulePosition()
    focusNext()
    return
  }

  // Bring into view instantly (smooth scrolling makes the spotlight chase the target)
  targetEl.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'auto' })
  measure()
  focusNext()

  // Re-measure as entrance animations / layout shifts / drawer transitions settle
  settleTimers = [250, 600, 1100].map((ms) => setTimeout(() => { if (id === runId) measure() }, ms))
}

const focusNext = async () => {
  await nextTick()
  nextBtnRef.value?.focus({ preventScroll: true })
}

// ── Navigation ───────────────────────────────────────────
const nextStep = () => {
  if (isLastStep.value) endTour(true)
  else store.tour.currentStep++
}

const prevStep = () => {
  if (store.tour.currentStep > 0) store.tour.currentStep--
}

const skipTour = () => endTour(false)

const endTour = (completed) => {
  runId++
  clearSettleTimers()
  store.tour.active = false
  store.tour.currentStep = 0
  store.tour.sidebarOpen = false
  spot.value = null
  targetEl = null
  localStorage.setItem(TOUR_STORAGE_KEY, 'true')
  if (completed) toast.success(t('tour.completed'))
}

const onKeydown = (e) => {
  if (!store.tour.active) return
  if (e.key === 'Escape') { e.preventDefault(); skipTour() }
  else if (e.key === 'ArrowRight') { e.preventDefault(); nextStep() }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); prevStep() }
}

// ── Watchers & lifecycle ─────────────────────────────────
watch(() => store.tour.active, (active) => {
  if (active) {
    spot.value = null
    isCentered.value = true
    schedulePosition()
    locate()
  } else {
    spot.value = null
    targetEl = null
  }
})

watch(() => store.tour.currentStep, () => {
  if (store.tour.active) locate()
})

// Language switches change text length, so reflow the card
watch(() => t('tour.next'), () => { if (store.tour.active) schedulePosition() })

onMounted(() => {
  window.addEventListener('resize', measure)
  window.addEventListener('orientationchange', measure)
  window.addEventListener('scroll', measure, true)
  window.addEventListener('keydown', onKeydown)
  if (store.tour.active) locate()
})

onUnmounted(() => {
  window.removeEventListener('resize', measure)
  window.removeEventListener('orientationchange', measure)
  window.removeEventListener('scroll', measure, true)
  window.removeEventListener('keydown', onKeydown)
  cancelAnimationFrame(measureRaf)
  clearSettleTimers()
})
</script>

<style scoped>
.tour-spot {
  transition:
    top 280ms cubic-bezier(0.4, 0, 0.2, 1),
    left 280ms cubic-bezier(0.4, 0, 0.2, 1),
    width 280ms cubic-bezier(0.4, 0, 0.2, 1),
    height 280ms cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 280ms ease;
}

.tour-card {
  transition:
    top 280ms cubic-bezier(0.4, 0, 0.2, 1),
    left 280ms cubic-bezier(0.4, 0, 0.2, 1);
  animation: tour-pop 260ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

.tour-content {
  animation: tour-fade 240ms ease-out;
}

@keyframes tour-pop {
  from { opacity: 0; transform: translateY(8px) scale(0.98); }
  to   { opacity: 1; transform: none; }
}

@keyframes tour-fade {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .tour-spot,
  .tour-card {
    transition: none;
    animation: none;
  }
  .tour-content {
    animation: none;
  }
}
</style>
