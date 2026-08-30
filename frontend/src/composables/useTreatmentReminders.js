import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api'

export function useTreatmentReminders() {
  const notifiedIds = ref(new Set())
  const dueReminders = ref([])
  const notificationPermission = ref(typeof Notification !== 'undefined' ? Notification.permission : 'default')
  let pollInterval = null

  const requestPermission = async () => {
    if (!('Notification' in window)) return
    if (Notification.permission === 'default') {
      const result = await Notification.requestPermission()
      notificationPermission.value = result
    }
  }

  const fireNotification = (treatment) => {
    if (!('Notification' in window)) return
    if (Notification.permission !== 'granted') return
    if (notifiedIds.value.has(treatment.id)) return

    const isOverdue = new Date(treatment.scheduled_date) < new Date()
    const title = isOverdue
      ? `⚠️ Overdue Treatment: ${treatment.title}`
      : `💊 Treatment Due Today: ${treatment.title}`

    const body = [
      `Type: ${treatment.treatment_type}`,
      treatment.dosage ? `Dosage: ${treatment.dosage}` : null,
      isOverdue ? `Was due: ${new Date(treatment.scheduled_date).toLocaleDateString()}` : 'Due: Today'
    ].filter(Boolean).join('\n')

    const notification = new Notification(title, {
      body,
      icon: '/favicon.ico',
      tag: `treatment-${treatment.id}`,
      requireInteraction: true
    })

    notification.onclick = () => {
      window.focus()
      notification.close()
    }

    notifiedIds.value.add(treatment.id)
  }

  const checkReminders = async () => {
    try {
      const data = await api.schedules.getDueReminders()
      const reminders = Array.isArray(data) ? data : []
      dueReminders.value = reminders
      reminders.forEach(fireNotification)
    } catch (err) {
      // Silent fail — don't disrupt the app if this endpoint is unavailable
      console.warn('[TreatmentReminders] Could not fetch due reminders:', err)
    }
  }

  onMounted(async () => {
    await requestPermission()
    await checkReminders()
    // Poll every 5 minutes
    pollInterval = setInterval(checkReminders, 5 * 60 * 1000)
  })

  onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
  })

  return {
    dueReminders,
    notificationPermission,
    requestPermission
  }
}
