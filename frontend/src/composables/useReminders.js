import { ref } from 'vue'
import { useToast } from './useToast'
import { addReminder, getReminders, removeReminder } from '../services/db'

export function useReminders() {
  const toast = useToast()
  const permissionGranted = ref(Notification.permission === 'granted')
  
  const activeTimers = new Map() // track setTimeout IDs

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

  const triggerNotification = (title, body) => {
    if (permissionGranted.value) {
      new Notification(title, {
        body,
        icon: '/pwa-192x192.png' // using PWA icon
      })
    } else {
      // Fallback to in-app toast
      toast.info(`${title}: ${body}`)
    }
  }

  const scheduleReminder = async (id, title, body, remindAt) => {
    const remindTime = new Date(remindAt).getTime()
    const now = Date.now()
    
    // Store in IndexedDB to persist
    await addReminder({ id, title, body, remindAt })

    if (remindTime <= now) {
      // Past due, trigger immediately (if missed while offline/closed)
      triggerNotification(title, body)
      await removeReminder(id)
      return
    }

    // Schedule within current session
    const delay = remindTime - now
    
    // Max setTimeout is ~24.8 days
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

  // Called once on app mount to re-hydrate missed or upcoming reminders
  const checkPendingReminders = async () => {
    const pending = await getReminders()
    for (const reminder of pending) {
      scheduleReminder(reminder.id, reminder.title, reminder.body, reminder.remindAt)
    }
  }

  return {
    permissionGranted,
    requestPermission,
    scheduleReminder,
    cancelReminder,
    checkPendingReminders
  }
}
