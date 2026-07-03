import { ref, onMounted, onUnmounted } from 'vue'

/**
   * Custom hook to track when an element enters the viewport.
   * @param {Object} options Configuration parameters
   * @param {number} [options.threshold=0.1] Ratio of element visibility to trigger intersection
   * @param {string} [options.rootMargin='0px'] Margins around root element
   * @param {boolean} [options.once=true] Whether to stop observing after it intersects once
   */
export function useIntersectionObserver(options = {}) {
  const target = ref(null)
  const isVisible = ref(false)
  let observer = null

  const once = options.once !== false

  onMounted(() => {
    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
          isVisible.value = true
          if (once) {
            observer.disconnect()
          }
        }
      }, {
        threshold: options.threshold || 0.1,
        rootMargin: options.rootMargin || '0px'
      })

      if (target.value) {
        observer.observe(target.value)
      }
    } else {
      // Fallback for older browsers or systems without IntersectionObserver
      isVisible.value = true
    }
  })

  onUnmounted(() => {
    if (observer) {
      observer.disconnect()
    }
  })

  return {
    target,
    isVisible
  }
}
