import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import ny from './locales/ny.json'

// Load language from localStorage, or fallback to 'en'
const savedLanguage = localStorage.getItem('language') || 'en'

const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: savedLanguage,
  fallbackLocale: 'en',
  messages: {
    en,
    ny
  }
})

export default i18n
