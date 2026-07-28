import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

// Register PWA Service Worker
import { registerSW } from 'virtual:pwa-register'
registerSW({ immediate: true })

createApp(App).use(router).use(i18n).mount('#app')
