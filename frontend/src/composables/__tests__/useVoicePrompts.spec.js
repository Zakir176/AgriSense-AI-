import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useVoicePrompts } from '../useVoicePrompts'

describe('useVoicePrompts composable', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('initializes with default voiceEnabled state', () => {
    const { voiceEnabled, isSupported } = useVoicePrompts()
    expect(typeof isSupported).toBe('boolean')
    expect(voiceEnabled.value).toBe(true)
  })

  it('toggles voice setting correctly and persists in localStorage', () => {
    const { voiceEnabled, toggleVoice } = useVoicePrompts()
    expect(voiceEnabled.value).toBe(true)
    
    toggleVoice()
    expect(voiceEnabled.value).toBe(false)
    expect(localStorage.getItem('agri_voice_enabled')).toBe('false')

    toggleVoice()
    expect(voiceEnabled.value).toBe(true)
    expect(localStorage.getItem('agri_voice_enabled')).toBe('true')
  })

  it('handles speak without crashing when window.speechSynthesis is mocked', () => {
    const cancelMock = vi.fn()
    const speakMock = vi.fn()

    window.speechSynthesis = {
      cancel: cancelMock,
      speak: speakMock,
      getVoices: () => [{ lang: 'ny-MW', name: 'Chichewa Voice' }, { lang: 'en-US', name: 'English Voice' }]
    }
    window.SpeechSynthesisUtterance = vi.fn().mockImplementation((text) => ({
      text,
      lang: '',
      rate: 1,
      pitch: 1
    }))

    const { speak } = useVoicePrompts()
    speak('Mankhwala achedwa', 'ny')

    expect(cancelMock).toHaveBeenCalled()
    expect(speakMock).toHaveBeenCalled()
  })
})
