import { ref } from 'vue'
import i18n from '../i18n'

const isSpeaking = ref(false)
const voiceEnabled = ref(localStorage.getItem('agri_voice_enabled') !== 'false')

export function useVoicePrompts() {
  const getIsSupported = () => typeof window !== 'undefined' && 'speechSynthesis' in window

  const toggleVoice = () => {
    voiceEnabled.value = !voiceEnabled.value
    localStorage.setItem('agri_voice_enabled', String(voiceEnabled.value))
    if (!voiceEnabled.value && getIsSupported()) {
      window.speechSynthesis.cancel()
      isSpeaking.value = false
    }
  }

  const speak = (text, langOverride = null) => {
    if (!getIsSupported() || !voiceEnabled.value || !text) return

    try {
      window.speechSynthesis.cancel() // Stop prior speech to avoid queue backing up

      const currentLang = langOverride || (i18n.global.locale?.value || i18n.global.locale || 'en')
      const utterance = new SpeechSynthesisUtterance(text)

      const voices = window.speechSynthesis.getVoices ? window.speechSynthesis.getVoices() : []
      let selectedVoice = null

      if (currentLang === 'ny') {
        // Try finding Chichewa/Nyanja voice, fallback to Swahili, African English, or default
        selectedVoice = voices.find(v => 
          v.lang.startsWith('ny') || 
          v.lang.startsWith('ny-MW') || 
          v.lang.startsWith('sw') || 
          (v.name && v.name.toLowerCase().includes('swahili')) ||
          (v.name && v.name.toLowerCase().includes('chichewa'))
        )
        utterance.lang = selectedVoice ? selectedVoice.lang : 'ny-MW'
        utterance.rate = 0.88 // Slightly slower for clear regional pronunciation
        utterance.pitch = 1.0
      } else {
        selectedVoice = voices.find(v => v.lang.startsWith('en'))
        utterance.lang = selectedVoice ? selectedVoice.lang : 'en-US'
        utterance.rate = 0.95
      }

      if (selectedVoice) {
        utterance.voice = selectedVoice
      }

      utterance.onstart = () => { isSpeaking.value = true }
      utterance.onend = () => { isSpeaking.value = false }
      utterance.onerror = () => { isSpeaking.value = false }

      window.speechSynthesis.speak(utterance)
    } catch (err) {
      console.warn('[useVoicePrompts] Speech synthesis error:', err)
      isSpeaking.value = false
    }
  }

  const stop = () => {
    if (getIsSupported()) {
      window.speechSynthesis.cancel()
      isSpeaking.value = false
    }
  }

  return {
    isSupported: getIsSupported(),
    isSpeaking,
    voiceEnabled,
    toggleVoice,
    speak,
    stop
  }
}
