import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTreatmentReminders } from '../useTreatmentReminders'

vi.mock('../../services/api', () => ({
  default: {
    schedules: {
      getDueReminders: vi.fn().mockResolvedValue([
        { id: 1, title: 'Gumboro Vaccine', treatment_type: 'Vaccine', dosage: '200ml/1000L', scheduled_date: new Date().toISOString() }
      ])
    }
  }
}))

describe('useTreatmentReminders composable', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('provides expected methods and refs', () => {
    const { dueReminders, notificationPermission, requestPermission, speakReminder } = useTreatmentReminders()
    expect(dueReminders).toBeDefined()
    expect(notificationPermission).toBeDefined()
    expect(typeof requestPermission).toBe('function')
    expect(typeof speakReminder).toBe('function')
  })
})
