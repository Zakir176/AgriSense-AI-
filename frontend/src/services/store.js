import { reactive } from 'vue'

export const store = reactive({
  currentUser: null,
  currentFarm: null,
  activeBatch: null,
  batchesList: [],
  alertsList: [],
  farmsList: [],
  latestInferenceResult: null,
  
  // Tour Guide Onboarding State
  tour: {
    active: false,
    currentStep: 0,
    steps: [
      {
        targetSelector: '#site-header-role',
        route: '/dashboard',
        titleKey: 'tour.step1_title',
        contentKey: 'tour.step1_content',
        placement: 'bottom'
      },
      {
        targetSelector: '#header-actions',
        route: '/dashboard',
        titleKey: 'tour.step2_title',
        contentKey: 'tour.step2_content',
        placement: 'bottom'
      },
      {
        targetSelector: '#dashboard-alerts-card',
        route: '/dashboard',
        titleKey: 'tour.step3_title',
        contentKey: 'tour.step3_content',
        placement: 'top'
      },
      {
        targetSelector: '#dashboard-quick-links',
        route: '/dashboard',
        titleKey: 'tour.step4_title',
        contentKey: 'tour.step4_content',
        placement: 'top'
      },
      {
        targetSelector: '#nav-feed-water',
        route: '/dashboard',
        titleKey: 'tour.step5_title',
        contentKey: 'tour.step5_content',
        placement: 'right'
      },
      {
        targetSelector: '#readings-table-card',
        route: '/readings',
        titleKey: 'tour.step6_title',
        contentKey: 'tour.step6_content',
        placement: 'top'
      },
      {
        targetSelector: '#nav-flock_health',
        route: '/readings',
        titleKey: 'tour.step7_title',
        contentKey: 'tour.step7_content',
        placement: 'right'
      },
      {
        targetSelector: '#treatment-calendar-panel',
        route: '/medications',
        titleKey: 'tour.step8_title',
        contentKey: 'tour.step8_content',
        placement: 'top'
      },
      {
        targetSelector: '#nav-ai-monitor',
        route: '/medications',
        titleKey: 'tour.step9_title',
        contentKey: 'tour.step9_content',
        placement: 'right'
      },
      {
        targetSelector: '#ai-live-feed-card',
        route: '/inference',
        titleKey: 'tour.step10_title',
        contentKey: 'tour.step10_content',
        placement: 'top'
      },
      {
        targetSelector: '#nav-audio',
        route: '/inference',
        titleKey: 'tour.step11_title',
        contentKey: 'tour.step11_content',
        placement: 'right'
      },
      {
        targetSelector: '#audio-library-card',
        route: '/audio',
        titleKey: 'tour.step12_title',
        contentKey: 'tour.step12_content',
        placement: 'top'
      }
    ]
  }
})
