import { ref } from 'vue'
import { useToast } from './useToast'
import { addReminder, getReminders, removeReminder } from '../services/db'
import api from '../services/api'
import i18n from '../i18n'
import { useVoicePrompts } from './useVoicePrompts'

export function useReminders() {
  const toast = useToast()
  const permissionGranted = ref(typeof Notification !== 'undefined' && Notification.permission === 'granted')
  const { speak, voiceEnabled } = useVoicePrompts()
  
  const activeTimers = new Map() // track setTimeout IDs

  const t = (key, params) => {
    try {
      if (i18n.global.t) {
        return i18n.global.t(key, params)
      }
    } catch (e) {
      // fallback
    }
    return key
  }

  const requestPermission = async () => {
    if (!('Notification' in window)) return false
    if (Notification.permission === 'granted') {
      permissionGranted.value = true
      return true
    }
    const permission = await Notification.requestPermission()
    permissionGranted.value = permission === 'granted'
    return permissionGranted.value
  }

  const triggerNotification = (title, body, speakText = null) => {
    if (permissionGranted.value && 'Notification' in window) {
      new Notification(title, {
        body,
        icon: '/favicon.ico'
      })
    } else {
      // Fallback to in-app toast
      toast.info(`${title}: ${body}`)
    }

    if (voiceEnabled.value && (speakText || body || title)) {
      speak(speakText || `${title}. ${body}`)
    }
  }

  const scheduleReminder = async (id, title, body, remindAt) => {
    const remindTime = new Date(remindAt).getTime()
    const now = Date.now()
    
    // Store in IndexedDB to persist
    await addReminder({ id, title, body, remindAt })

    if (remindTime <= now) {
      // Past due, trigger immediately
      triggerNotification(title, body)
      await removeReminder(id)
      return
    }

    const delay = remindTime - now
    if (delay > 2147483647) return

    const timerId = setTimeout(async () => {
      triggerNotification(title, body)
      await removeReminder(id)
      activeTimers.delete(id)
    }, delay)

    activeTimers.set(id, timerId)
  }

  const cancelReminder = async (id) => {
    await removeReminder(id)
    if (activeTimers.has(id)) {
      clearTimeout(activeTimers.get(id))
      activeTimers.delete(id)
    }
  }

  const checkPendingReminders = async () => {
    const pending = await getReminders()
    for (const reminder of pending) {
      scheduleReminder(reminder.id, reminder.title, reminder.body, reminder.remindAt)
    }
  }

  const notifiedServerIds = new Set()

  const checkDueFromServer = async () => {
    try {
      const data = await api.schedules.getDueReminders()
      const reminders = Array.isArray(data) ? data : []

      for (const treatment of reminders) {
        if (notifiedServerIds.has(treatment.id)) continue

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

        const speechKey = isOverdue ? 'reminders.speech_overdue' : 'reminders.speech_due_today'
        let speakText = t(speechKey, {
          title: treatment.title,
          type: treatment.treatment_type || '',
          dosage: treatment.dosage || ''
        })

        if (speakText.startsWith('reminders.')) {
          speakText = isOverdue
            ? `Attention. Overdue treatment for ${treatment.title}.`
            : `Reminder. Treatment due today: ${treatment.title}.`
        }

        triggerNotification(title, body, speakText)
        notifiedServerIds.add(treatment.id)
      }

      return reminders
    } catch (err) {
      console.warn('[Reminders] Could not fetch due reminders from server:', err)
      return []
    }
  }

  return {
    permissionGranted,
    requestPermission,
    scheduleReminder,
    cancelReminder,
    checkPendingReminders,
    checkDueFromServer
  }
}
