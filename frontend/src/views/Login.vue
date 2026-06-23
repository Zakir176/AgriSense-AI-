<template>
  <div class="h-full flex bg-gray-50 dark:bg-darkbg-100 transition-colors duration-300 relative overflow-hidden">

    <!-- Floating Theme Toggle -->
    <button
      @click="toggleTheme"
      class="absolute top-5 right-5 p-2.5 rounded-xl bg-white/80 dark:bg-darkbg-50/80 backdrop-blur-md border border-gray-200 dark:border-gray-800 shadow-md text-gray-500 dark:text-gray-400 hover:scale-110 active:scale-95 transition-all duration-200 focus:outline-none z-30"
      aria-label="Toggle Theme"
    >
      <span class="material-icons-outlined text-[18px] block leading-none">
        {{ isDark ? 'light_mode' : 'dark_mode' }}
      </span>
    </button>

    <!-- ═══════════════════════════════════════════
         LEFT PANE — Immersive farm visual
    ════════════════════════════════════════════ -->
    <div class="hidden md:flex md:w-[55%] relative bg-[#0a0f0d] overflow-hidden flex-col h-full">
      <!-- Background Image -->
      <img
        src="../assets/login_bg_farm.png"
        alt="AgriSense AI Smart Farm"
        class="absolute inset-0 w-full h-full object-cover opacity-70"
      />
      <!-- Layered gradients for depth -->
      <div class="absolute inset-0 bg-gradient-to-br from-[#071209]/95 via-primary-950/70 to-transparent"></div>
      <div class="absolute inset-0 bg-gradient-to-t from-[#040a06]/80 via-transparent to-transparent"></div>

      <!-- Subtle dot grid -->
      <div class="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.055)_1px,transparent_1px)] [background-size:28px_28px]"></div>

      <!-- Main overlay content — vertically centered -->
      <div class="relative z-10 flex flex-col justify-center flex-1 px-14 py-16 text-white">

        <!-- Badge -->
        <div class="inline-flex items-center space-x-2 bg-white/8 backdrop-blur-md px-4 py-2 rounded-full border border-white/12 w-fit mb-8">
          <span class="material-icons-outlined text-primary-400 text-[15px]">psychology</span>
          <span class="text-[11px] font-bold uppercase tracking-widest text-gray-300">Next-Gen AgriTech Platform</span>
        </div>

        <!-- Hero copy -->
        <h1 class="text-5xl font-black tracking-tight leading-[1.15] mb-5">
          Precision Poultry<br/>
          <span class="bg-gradient-to-r from-primary-300 via-green-300 to-emerald-300 bg-clip-text text-transparent inline-block">Driven by AI</span>
        </h1>
        <p class="text-gray-400 text-[15px] leading-relaxed max-w-sm mb-10">
          Real-time telemetry, YOLOv8 flock counting, bioacoustic health scoring, and predictive alerts — all in one platform.
        </p>

        <!-- Feature cards -->
        <div class="grid grid-cols-2 gap-3 mb-10">
          <div class="group bg-white/5 hover:bg-white/9 backdrop-blur-sm border border-white/8 hover:border-white/18 rounded-2xl p-4 transition-all duration-300 cursor-default">
            <div class="flex items-center space-x-2 mb-2">
              <span class="material-icons-outlined text-primary-400 text-[18px]">videocam</span>
              <div class="font-bold text-[13px]">YOLOv8 Telemetry</div>
            </div>
            <div class="text-[11px] text-gray-500 leading-relaxed">Real-time flock visual counts & movement analysis</div>
          </div>
          <div class="group bg-white/5 hover:bg-white/9 backdrop-blur-sm border border-white/8 hover:border-white/18 rounded-2xl p-4 transition-all duration-300 cursor-default">
            <div class="flex items-center space-x-2 mb-2">
              <span class="material-icons-outlined text-primary-400 text-[18px]">hearing</span>
              <div class="font-bold text-[13px]">Bioacoustic Insights</div>
            </div>
            <div class="text-[11px] text-gray-500 leading-relaxed">Early respiratory stress & audio anomaly detection</div>
          </div>
          <div class="group bg-white/5 hover:bg-white/9 backdrop-blur-sm border border-white/8 hover:border-white/18 rounded-2xl p-4 transition-all duration-300 cursor-default">
            <div class="flex items-center space-x-2 mb-2">
              <span class="material-icons-outlined text-primary-400 text-[18px]">show_chart</span>
              <div class="font-bold text-[13px]">Growth Analytics</div>
            </div>
            <div class="text-[11px] text-gray-500 leading-relaxed">FCR tracking, weight benchmarks & batch comparisons</div>
          </div>
          <div class="group bg-white/5 hover:bg-white/9 backdrop-blur-sm border border-white/8 hover:border-white/18 rounded-2xl p-4 transition-all duration-300 cursor-default">
            <div class="flex items-center space-x-2 mb-2">
              <span class="material-icons-outlined text-primary-400 text-[18px]">notifications_active</span>
              <div class="font-bold text-[13px]">Smart Alerts</div>
            </div>
            <div class="text-[11px] text-gray-500 leading-relaxed">Rule-based & AI-driven health & environment alerts</div>
          </div>
        </div>

        <!-- Live stats ticker -->
        <div class="flex items-center space-x-6 bg-white/5 border border-white/8 rounded-2xl px-5 py-3 backdrop-blur-sm">
          <div class="flex items-center space-x-1.5">
            <span class="relative flex h-1.5 w-1.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
            </span>
            <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Live</span>
          </div>
          <div class="flex items-center space-x-5 text-[11px] text-gray-300 font-mono">
            <span>🐔 Flock: <b class="text-white">{{ stats.birdCount }}</b></span>
            <span>📊 FCR: <b class="text-white">{{ stats.fcr }}</b></span>
            <span>🌡 Shed: <b class="text-white">{{ stats.temp }}°C</b></span>
            <span>💧 RH: <b class="text-white">{{ stats.rh }}%</b></span>
          </div>
        </div>
      </div>

      <!-- Bottom footer -->
      <div class="relative z-10 px-14 py-5 flex justify-between text-[11px] text-gray-600 border-t border-white/5">
        <span>© 2026 AgriSense AI</span>
        <span>v1.0.0 · Prime Nest Poultry</span>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════
         RIGHT PANE — Login form
    ════════════════════════════════════════════ -->
    <div class="w-full md:w-[45%] flex items-center justify-center h-full p-8 sm:p-12 relative">

      <!-- Soft background accents -->
      <div class="absolute inset-0 bg-[radial-gradient(#d1e8ce_1px,transparent_1px)] dark:bg-[radial-gradient(#1a2219_1px,transparent_1px)] [background-size:22px_22px] opacity-30 pointer-events-none"></div>
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div class="w-[420px] h-[420px] bg-primary-200/25 dark:bg-primary-950/20 rounded-full blur-[110px]"></div>
      </div>

      <!-- Card entry animation -->
      <Transition
        appear
        
        enter-active-class="transition-all duration-700 ease-out"
        enter-from-class="opacity-0 translate-y-8 scale-[0.97]"
        enter-to-class="opacity-100 translate-y-0 scale-100"
      >
        <div class="max-w-sm w-full bg-white/95 dark:bg-darkbg-50/95 backdrop-blur-2xl border border-gray-100 dark:border-gray-800/60 rounded-3xl shadow-2xl shadow-gray-200/40 dark:shadow-black/30 relative overflow-hidden">

          <!-- Gradient accent bar -->
          <div class="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-primary-500 via-primary-400 to-emerald-400 rounded-t-3xl"></div>

          <div class="px-8 pt-10 pb-8">

            <!-- Logo -->
            <div class="flex items-center space-x-2.5 mb-8">
              <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-600/25">
                <span class="material-icons-outlined text-white text-[18px]">agriculture</span>
              </div>
              <div>
                <div class="text-[17px] font-black tracking-wide text-gray-900 dark:text-white uppercase leading-none">AgriSense <span class="text-primary-600 dark:text-primary-400">AI</span></div>
                <div class="text-[10px] text-gray-400 dark:text-gray-500 font-medium tracking-wider uppercase leading-none mt-0.5">Intelligent Farm Management</div>
              </div>
            </div>

            <!-- Heading -->
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white leading-tight">{{ isRegistering ? 'Create account' : 'Welcome back' }}</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ isRegistering ? 'Register a new operator account' : 'Sign in to your operator dashboard' }}</p>

            <!-- Error alert -->
            <Transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-200 ease-in"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <div
                v-if="errorMessage"
                class="mt-5 bg-red-50 dark:bg-red-950/25 border border-red-200 dark:border-red-900/40 text-red-700 dark:text-red-400 text-sm px-4 py-3 rounded-2xl flex items-start space-x-2.5"
              >
                <span class="material-icons-outlined text-[18px] shrink-0 mt-0.5">error_outline</span>
                <span>{{ errorMessage }}</span>
              </div>
            </Transition>

            <!-- Forgot-password tip -->
            <Transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-200"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <div
                v-if="showForgotTip && !isRegistering"
                class="mt-5 bg-primary-50 dark:bg-primary-950/20 border border-primary-200/70 dark:border-primary-900/40 text-primary-800 dark:text-primary-300 text-xs px-4 py-3 rounded-2xl flex items-start space-x-2.5"
              >
                <span class="material-icons-outlined text-[18px] shrink-0 text-primary-500 dark:text-primary-400">tips_and_updates</span>
                <div>
                  <div class="font-semibold mb-0.5">Demo Account</div>
                  <div>Use <code class="bg-primary-100 dark:bg-primary-900/40 px-1.5 py-0.5 rounded font-mono text-[11px] font-bold">operator</code> / <code class="bg-primary-100 dark:bg-primary-900/40 px-1.5 py-0.5 rounded font-mono text-[11px] font-bold">prime_nest_2026</code></div>
                </div>
              </div>
            </Transition>

            <!-- Success alert (registration) -->
            <Transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-200 ease-in"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <div
                v-if="successMessage"
                class="mt-5 bg-emerald-50 dark:bg-emerald-950/25 border border-emerald-200 dark:border-emerald-900/40 text-emerald-700 dark:text-emerald-400 text-sm px-4 py-3 rounded-2xl flex items-start space-x-2.5"
              >
                <span class="material-icons-outlined text-[18px] shrink-0 mt-0.5">check_circle</span>
                <span>{{ successMessage }}</span>
              </div>
            </Transition>

            <form @submit.prevent="isRegistering ? handleRegister() : handleLogin()" class="mt-7 space-y-4">

              <!-- Full Name (register only) -->
              <div v-if="isRegistering" class="space-y-1.5">
                <label for="fullName" class="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">Full Name</label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 dark:text-gray-500">
                    <span class="material-icons-outlined text-[18px]">badge</span>
                  </span>
                  <input
                    v-model="fullName"
                    id="fullName"
                    name="fullName"
                    type="text"
                    autocomplete="name"
                    class="block w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700/80 placeholder-gray-350 dark:placeholder-gray-600 text-gray-900 dark:text-white rounded-xl bg-gray-50 dark:bg-[#111816] focus:outline-none focus:ring-2 focus:ring-primary-500/25 focus:border-primary-500 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-200 text-sm"
                    placeholder="Enter your full name"
                  />
                </div>
              </div>

              <!-- Username -->
              <div class="space-y-1.5">
                <label for="username" class="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">Username</label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 dark:text-gray-500">
                    <span class="material-icons-outlined text-[18px]">person_outline</span>
                  </span>
                  <input
                    v-model="username"
                    id="username"
                    name="username"
                    type="text"
                    required
                    autocomplete="username"
                    class="block w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700/80 placeholder-gray-350 dark:placeholder-gray-600 text-gray-900 dark:text-white rounded-xl bg-gray-50 dark:bg-[#111816] focus:outline-none focus:ring-2 focus:ring-primary-500/25 focus:border-primary-500 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-200 text-sm"
                    placeholder="Choose a username"
                  />
                </div>
              </div>

              <!-- Password -->
              <div class="space-y-1.5">
                <label for="password" class="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">Password</label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 dark:text-gray-500">
                    <span class="material-icons-outlined text-[18px]">lock_outline</span>
                  </span>
                  <input
                    v-model="password"
                    id="password"
                    name="password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    autocomplete="current-password"
                    class="block w-full pl-10 pr-11 py-3 border border-gray-200 dark:border-gray-700/80 placeholder-gray-350 dark:placeholder-gray-600 text-gray-900 dark:text-white rounded-xl bg-gray-50 dark:bg-[#111816] focus:outline-none focus:ring-2 focus:ring-primary-500/25 focus:border-primary-500 hover:border-gray-300 dark:hover:border-gray-600 transition-all duration-200 text-sm"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors focus:outline-none"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  >
                    <span class="material-icons-outlined text-[18px]">{{ showPassword ? 'visibility_off' : 'visibility' }}</span>
                  </button>
                </div>
              </div>

              <!-- Remember + Forgot (login only) -->
              <div v-if="!isRegistering" class="flex items-center justify-between pt-1">
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="rememberMe"
                    class="w-4 h-4 text-primary-600 border-gray-300 dark:border-gray-700 rounded focus:ring-primary-500/30 transition cursor-pointer"
                  />
                  <span class="text-sm text-gray-600 dark:text-gray-400 select-none">Remember device</span>
                </label>
                <button
                  type="button"
                  @click="triggerForgotTip"
                  class="text-sm font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 transition-colors focus:outline-none"
                >
                  Forgot password?
                </button>
              </div>

              <!-- Submit button -->
              <button
                type="submit"
                :disabled="isLoading || loginSuccess"
                class="mt-2 w-full flex justify-center items-center gap-2.5 py-3.5 px-4 border border-transparent text-sm font-bold rounded-xl text-white transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:cursor-not-allowed"
                :class="loginSuccess
                  ? 'bg-emerald-500 shadow-lg shadow-emerald-500/20 scale-[0.99]'
                  : 'bg-primary-600 hover:bg-primary-500 active:scale-[0.99] shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 disabled:opacity-60'"
              >
                <template v-if="loginSuccess">
                  <span class="material-icons-outlined text-[18px] animate-bounce">check_circle</span>
                  <span>Redirecting…</span>
                </template>
                <template v-else-if="isLoading">
                  <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  <span>{{ isRegistering ? 'Creating account…' : 'Authenticating…' }}</span>
                </template>
                <template v-else>
                  <span>{{ isRegistering ? 'Create Account' : 'Sign In' }}</span>
                  <span class="material-icons-outlined text-[17px]">{{ isRegistering ? 'person_add' : 'arrow_forward' }}</span>
                </template>
              </button>
            </form>

            <!-- Toggle + Demo credentials -->
            <div class="mt-7 pt-5 border-t border-gray-100 dark:border-gray-800/60 text-center space-y-4">
              <!-- Mode toggle -->
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ isRegistering ? 'Already have an account?' : "Don't have an account?" }}
                <button
                  type="button"
                  @click="toggleMode"
                  class="font-bold text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 transition-colors focus:outline-none ml-1"
                >
                  {{ isRegistering ? 'Sign in' : 'Sign up' }}
                </button>
              </p>

              <!-- Demo credentials (login mode only) -->
              <div v-if="!isRegistering">
                <p class="text-[11px] text-gray-400 dark:text-gray-500 mb-2 uppercase tracking-wider font-semibold">Demo Account</p>
                <div class="inline-flex items-center gap-2 bg-gray-50 dark:bg-[#111816] border border-gray-200/80 dark:border-gray-800/60 px-3.5 py-2 rounded-xl font-mono text-[11px] text-gray-600 dark:text-gray-400">
                  <span><b class="text-gray-800 dark:text-gray-200">operator</b></span>
                  <span class="text-gray-300 dark:text-gray-700">/</span>
                  <span><b class="text-gray-800 dark:text-gray-200">prime_nest_2026</b></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'

const router = useRouter()

// Form state
const username = ref('')
const password = ref('')
const fullName = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)
const loginSuccess = ref(false)
const showForgotTip = ref(false)
const isRegistering = ref(false)

// Theme
const isDark = ref(false)

// Live stats ticker
const stats = ref({ birdCount: '1,842', fcr: '1.74', temp: '24.2', rh: '61' })
let statsInterval = null

const tickStats = () => {
  // Simulate small live fluctuations
  const jitter = (val, range, decimals = 0) => {
    const n = parseFloat(val.toString().replace(',', '')) + (Math.random() - 0.5) * range
    return decimals > 0 ? n.toFixed(decimals) : Math.round(n).toLocaleString()
  }
  stats.value = {
    birdCount: jitter(stats.value.birdCount, 6),
    fcr: jitter(stats.value.fcr, 0.04, 2),
    temp: jitter(stats.value.temp, 0.3, 1),
    rh: jitter(stats.value.rh, 1.5, 1),
  }
}

// Theme management
const applyTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
}

// Forgot password tip
const triggerForgotTip = () => {
  showForgotTip.value = true
  setTimeout(() => { showForgotTip.value = false }, 7000)
}

// Mode toggle
const toggleMode = () => {
  isRegistering.value = !isRegistering.value
  errorMessage.value = ''
  successMessage.value = ''
  loginSuccess.value = false
}

// Login handler
const handleLogin = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true
  try {
    await api.auth.login(username.value, password.value)
    loginSuccess.value = true
    setTimeout(() => router.push({ name: 'Dashboard' }), 800)
  } catch (error) {
    if (error.message && error.message.toLowerCase().includes('fetch')) {
      errorMessage.value = 'Cannot reach the server. Please ensure the backend is running on port 8000.'
    } else {
      errorMessage.value = error.message || 'Login failed. Please check your credentials.'
    }
  } finally {
    isLoading.value = false
  }
}

// Register handler
const handleRegister = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true
  try {
    await api.auth.register(username.value, password.value, fullName.value)
    loginSuccess.value = true
    successMessage.value = 'Account created successfully!'
    setTimeout(() => router.push({ name: 'Dashboard' }), 800)
  } catch (error) {
    if (error.message && error.message.toLowerCase().includes('fetch')) {
      errorMessage.value = 'Cannot reach the server. Please ensure the backend is running on port 8000.'
    } else {
      errorMessage.value = error.message || 'Registration failed. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  isDark.value = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme()
  statsInterval = setInterval(tickStats, 3000)
})

onUnmounted(() => {
  clearInterval(statsInterval)
})
</script>
