import { reactive } from 'vue'

// Bump the suffix whenever the tour changes enough to re-show it to everyone.
export const TOUR_STORAGE_KEY = 'agrisense_onboarded_v2'

export const store = reactive({
  currentUser: null,
  currentFarm: null,
  activeBatch: null,
  batchesList: [],
  alertsList: [],
  farmsList: [],
  latestInferenceResult: null,
  
  // Tour Guide Onboarding State
  //
  // Step fields:
  //   id              - used for i18n keys: tour.steps.<id>.title / .content
  //   route           - page the step lives on (tour navigates automatically)
  //   targetSelector  - element to spotlight; omit for a centered card
  //   closest         - optional: spotlight the nearest ancestor matching this selector
  //   placement       - preferred tooltip side on wide screens (auto-flips if no room)
  //   needsSidebar    - open the off-canvas sidebar on mobile for this step
  tour: {
    active: false,
    currentStep: 0,
    sidebarOpen: false,
    steps: [
      { id: 'welcome',   route: '/dashboard' },
      { id: 'role',      route: '/dashboard',     targetSelector: '#site-header-role', placement: 'bottom' },
      { id: 'toolbar',   route: '/dashboard',     targetSelector: '#header-actions',   placement: 'bottom' },
      { id: 'sidebar',   route: '/dashboard',     targetSelector: '#app-sidebar-nav',  placement: 'right', needsSidebar: true },
      { id: 'alerts',    route: '/dashboard',     targetSelector: '#dashboard-alerts-card', placement: 'top' },
      { id: 'quicklinks',route: '/dashboard',     targetSelector: '#dashboard-quick-links', placement: 'top' },
      { id: 'batches',   route: '/batches',       targetSelector: 'main h1', closest: '.animate-fade-in-up', placement: 'bottom' },
      { id: 'feed',      route: '/readings',      targetSelector: '#readings-table-card', placement: 'top' },
      { id: 'growth',    route: '/growth',        targetSelector: 'main h1', closest: '.animate-fade-in-up', placement: 'bottom' },
      { id: 'meds',      route: '/medications',   targetSelector: '#treatment-calendar-panel', placement: 'top' },
      { id: 'ai',        route: '/inference',     targetSelector: '#ai-live-feed-card', placement: 'top' },
      { id: 'audio',     route: '/audio',         targetSelector: '#audio-library-card', placement: 'top' },
      { id: 'analytics', route: '/analytics',     targetSelector: 'main h1', closest: '.animate-fade-in-up', placement: 'bottom' },
      { id: 'financial', route: '/financial',     targetSelector: 'main h1', closest: '.animate-fade-in-up', placement: 'bottom' },
      { id: 'settings',  route: '/farm-settings', targetSelector: 'main h1', closest: '.animate-fade-in-up', placement: 'bottom' },
      { id: 'done',      route: '/dashboard' }
    ]
  }
})
