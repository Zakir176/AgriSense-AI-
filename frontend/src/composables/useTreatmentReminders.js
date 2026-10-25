import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api'
import i18n from '../i18n'
import { useVoicePrompts } from './useVoicePrompts'

export function useTreatmentReminders() {
  const notifiedIds = ref(new Set())
  const dueReminders = ref([])
  const notificationPermission = ref(typeof Notification !== 'undefined' ? Notification.permission : 'default')
  let pollInterval = null

  const { speak, voiceEnabled } = useVoicePrompts()

  const t = (key, params) => {
    try {
      if (i18n.global.t) {
        return i18n.global.t(key, params)
      }
    } catch (e) {
      // fallback if i18n context is not yet mounted
    }
    return key
  }

  const requestPermission = async () => {
    if (!('Notification' in window)) return
    if (Notification.permission === 'default') {
      const result = await Notification.requestPermission()
      notificationPermission.value = result
    }
  }

  const speakReminder = (treatment) => {
    const isOverdue = new Date(treatment.scheduled_date) < new Date()
    const speechKey = isOverdue ? 'reminders.speech_overdue' : 'reminders.speech_due_today'
    
    let speechText = t(speechKey, {
      title: treatment.title,
      type: treatment.treatment_type || '',
      dosage: treatment.dosage || ''
    })

    // Fallback text if key returns translation key literal
    if (speechText.startsWith('reminders.')) {
      speechText = isOverdue
        ? `Attention. Overdue treatment for ${treatment.title}. Type: ${treatment.treatment_type}.`
        : `Reminder. Treatment due today: ${treatment.title}. Dosage: ${treatment.dosage || 'as prescribed'}.`
    }

    speak(speechText)
  }

  const fireNotification = (treatment) => {
    if (notifiedIds.value.has(treatment.id)) return

    const isOverdue = new Date(treatment.scheduled_date) < new Date()
    const titleKey = isOverdue ? 'reminders.overdue_title' : 'reminders.due_today_title'
    let title = t(titleKey, { title: treatment.title })
    if (title.startsWith('reminders.')) {
      title = isOverdue ? `⚠️ Overdue Treatment: ${treatment.title}` : `💊 Treatment Due Today: ${treatment.title}`
    }

    const typeStr = t('reminders.type', { type: treatment.treatment_type }) || `Type: ${treatment.treatment_type}`
    const dosageStr = treatment.dosage ? (t('reminders.dosage', { dosage: treatment.dosage }) || `Dosage: ${treatment.dosage}`) : null
    const dateStr = isOverdue
      ? (t('reminders.was_due', { date: new Date(treatment.scheduled_date).toLocaleDateString() }) || `Was due: ${new Date(treatment.scheduled_date).toLocaleDateString()}`)
      : (t('reminders.due_today') || 'Due: Today')

    const body = [typeStr, dosageStr, dateStr].filter(Boolean).join('\n')

    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(title, {
        body,
        icon: '/favicon.ico',
        tag: `treatment-${treatment.id}`,
        requireInteraction: true
      })

      notification.onclick = () => {
        window.focus()
        notification.close()
        speakReminder(treatment)
      }
    }

    // Spoken Audio Announcement
    if (voiceEnabled.value) {
      speakReminder(treatment)
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
      // Silent fail — don't disrupt app if server is unreachable offline
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
    requestPermission,
    speakReminder
  }
}
