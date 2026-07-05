import { ref } from 'vue'

export function useAnimations() {
  /**
   * Generates a CSS delay class based on item index for staggered animations.
   * @param {number} index
   * @returns {string}
   */
  const getStaggerDelayClass = (index) => {
    const delays = [50, 100, 150, 200, 250, 300, 400, 500]
    const matchedDelay = delays[index] || delays[delays.length - 1]
    return `delay-${matchedDelay}`
  }

  /**
   * Animates a reactive reference variable from startValue to endValue.
   * @param {import('vue').Ref<number>} reactiveRef
   * @param {number} startVal
   * @param {number} endVal
   * @param {number} duration
   * @param {number} decimals
   */
  const animateNumber = (reactiveRef, startVal, endVal, duration = 650, decimals = 0) => {
    let startTime = null

    const step = (timestamp) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      const currentVal = progress * (endVal - startVal) + startVal
      
      reactiveRef.value = parseFloat(currentVal.toFixed(decimals))

      if (progress < 1) {
        window.requestAnimationFrame(step)
      } else {
        reactiveRef.value = endVal
      }
    }

    window.requestAnimationFrame(step)
  }

  return {
    getStaggerDelayClass,
    animateNumber
  }
}
