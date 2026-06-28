<template>
  <div class="min-h-screen bg-gray-50 dark:bg-darkbg-100 text-gray-850 dark:text-gray-150 font-sans transition-colors duration-200 relative overflow-x-hidden">
    <!-- Header Spacing -->
    <div class="absolute inset-0 bg-[radial-gradient(#d1e8ce_1.2px,transparent_1.2px)] dark:bg-[radial-gradient(#1a2219_1.2px,transparent_1.2px)] [background-size:28px_28px] opacity-35 pointer-events-none z-0"></div>

    <!-- Header Navigation -->
    <header class="relative z-10 max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
      <div class="flex items-center space-x-2.5">
        <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-600/25">
          <span class="material-icons-outlined text-white text-[18px]">agriculture</span>
        </div>
        <div>
          <div class="text-[17px] font-black tracking-wide text-gray-900 dark:text-white uppercase leading-none">AgriSense <span class="text-primary-600 dark:text-primary-400">AI</span></div>
          <div class="text-[10px] text-gray-400 dark:text-gray-500 font-bold tracking-wider uppercase leading-none mt-0.5">Operator Platform</div>
        </div>
      </div>

      <nav class="hidden md:flex items-center space-x-8 text-sm font-semibold text-gray-550 dark:text-gray-400">
        <a href="#features" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">Key Features</a>
        <a href="#demo" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">Live Simulation</a>
        <a href="#about" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">Our Impact</a>
      </nav>

      <div class="flex items-center space-x-4">
        <!-- Floating Theme Toggle -->
        <button
          @click="toggleTheme"
          class="p-2 rounded-xl border border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-darkbg-50/80 hover:bg-gray-100 dark:hover:bg-gray-800/60 transition text-gray-500 dark:text-gray-400"
          aria-label="Toggle Theme"
        >
          <span class="material-icons-outlined text-lg block">{{ isDark ? 'light_mode' : 'dark_mode' }}</span>
        </button>

        <AgriButton
          variant="primary"
          size="sm"
          icon="login"
          @click="navigateToLogin"
        >
          Operator Portal
        </AgriButton>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="relative z-10 max-w-7xl mx-auto px-6 pt-10 pb-20 md:py-24 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
      <!-- Hero Copy -->
      <div class="lg:col-span-6 space-y-6 text-left animate-fade-in-up">
        <!-- Badge -->
        <div class="inline-flex items-center space-x-2 bg-primary-100/50 dark:bg-primary-950/40 px-4 py-2 rounded-full border border-primary-200/50 dark:border-primary-900/30 w-fit">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
          </span>
          <span class="text-[10px] font-bold uppercase tracking-wider text-primary-700 dark:text-primary-400">PWA Offline Enabled</span>
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-gray-900 dark:text-white">
          Precision Poultry <br class="hidden sm:inline"/>
          <span class="bg-gradient-to-r from-primary-600 via-primary-500 to-emerald-500 dark:from-primary-400 dark:to-emerald-400 bg-clip-text text-transparent">Driven by Local AI</span>
        </h1>

        <p class="text-base text-gray-550 dark:text-gray-450 leading-relaxed max-w-xl">
          Empowering smallholder poultry farmers across Africa with offline-first farm telemetry, YOLOv8 video flock counting, and respiratory distress audio classification. Built to operate reliably in low-connectivity rural environments.
        </p>

        <!-- Actions -->
        <div class="flex flex-wrap gap-4 pt-2">
          <AgriButton
            variant="primary"
            size="lg"
            icon="arrow_forward"
            @click="navigateToLogin"
          >
            Launch Farm Portal
          </AgriButton>
          <AgriButton
            variant="outline"
            size="lg"
            icon="play_circle_outline"
            @click="scrollToDemo"
          >
            Explore Live Demo
          </AgriButton>
        </div>

        <!-- Mini Stats -->
        <div class="grid grid-cols-3 gap-6 pt-8 border-t border-gray-250/60 dark:border-gray-800/80 max-w-lg">
          <div>
            <p class="text-2xl font-black text-primary-600 dark:text-primary-400">98.4%</p>
            <p class="text-[10px] uppercase font-bold text-gray-400 dark:text-gray-500 tracking-wider mt-0.5">YOLO Count Accuracy</p>
          </div>
          <div>
            <p class="text-2xl font-black text-primary-600 dark:text-primary-400">100%</p>
            <p class="text-[10px] uppercase font-bold text-gray-400 dark:text-gray-500 tracking-wider mt-0.5">Offline Write Uptime</p>
          </div>
          <div>
            <p class="text-2xl font-black text-primary-600 dark:text-primary-400">&lt;2.2s</p>
            <p class="text-[10px] uppercase font-bold text-gray-400 dark:text-gray-500 tracking-wider mt-0.5">Anomaly Audio Alerts</p>
          </div>
        </div>
      </div>

      <!-- Hero Visuals (Mock Dashboard Frame) -->
      <div class="lg:col-span-6 relative flex justify-center items-center animate-fade-in-up delay-150">
        <!-- Soft decorative background glow -->
        <div class="absolute w-[450px] h-[450px] bg-primary-200/20 dark:bg-primary-950/15 rounded-full blur-[90px] -z-10"></div>

        <!-- Main Mock Card -->
        <div class="w-full max-w-lg bg-white/80 dark:bg-darkbg-50/80 backdrop-blur-md border border-gray-200 dark:border-gray-800 rounded-3xl p-4 shadow-2xl relative">
          <!-- Banner -->
          <div class="flex items-center justify-between pb-3 border-b border-gray-150 dark:border-gray-800">
            <div class="flex items-center space-x-2">
              <span class="h-3 w-3 rounded-full bg-red-400"></span>
              <span class="h-3 w-3 rounded-full bg-amber-400"></span>
              <span class="h-3 w-3 rounded-full bg-green-400"></span>
            </div>
            <span class="text-[10px] font-bold text-gray-450 dark:text-gray-500 uppercase tracking-widest">Coop Visual Feed</span>
          </div>

          <!-- Hero Image -->
          <div class="mt-3 rounded-2xl overflow-hidden aspect-video bg-[#0f1412] relative border border-gray-150 dark:border-gray-800">
            <img
              src="../assets/landing_hero_farm.png"
              alt="Smart Poultry Shed Visual"
              class="w-full h-full object-cover opacity-85"
            />
            <!-- Visual YOLO Detection Overlays -->
            <div class="absolute top-4 left-4 bg-primary-500/90 text-white font-bold text-[10px] px-2.5 py-1 rounded-lg backdrop-blur-sm border border-primary-600 shadow-lg flex items-center gap-1.5 animate-pulse">
              <span class="material-icons-outlined text-xs">videocam</span>
              <span>YOLOv8: Active Count</span>
            </div>
            <div class="absolute bottom-3 right-3 bg-black/60 text-white font-mono text-[9px] px-2 py-1 rounded backdrop-blur-sm">
              Shed 01 · Cam 02 · 1080p
            </div>
          </div>

          <!-- Floating Stats Widgets inside Hero Visual -->
          <div class="absolute -bottom-6 -left-6 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 shadow-xl rounded-2xl p-4 flex items-center space-x-3 max-w-[200px] animate-bounce-slow">
            <div class="h-10 w-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450 flex items-center justify-center">
              <span class="material-icons-outlined text-xl">thermostat</span>
            </div>
            <div>
              <p class="text-[10px] text-gray-450 uppercase font-bold tracking-wider">Temp Gauge</p>
              <p class="text-base font-black text-gray-900 dark:text-white mt-0.5">24.5 °C</p>
            </div>
          </div>

          <div class="absolute -top-6 -right-6 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 shadow-xl rounded-2xl p-4 flex items-center space-x-3 max-w-[210px] animate-bounce-slow delay-200">
            <div class="h-10 w-10 rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-500 flex items-center justify-center">
              <span class="material-icons-outlined text-xl">groups</span>
            </div>
            <div>
              <p class="text-[10px] text-gray-450 uppercase font-bold tracking-wider">Bird Density</p>
              <p class="text-base font-black text-gray-900 dark:text-white mt-0.5">1,248 birds</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Key Capabilities Section -->
    <section id="features" class="relative z-10 bg-white dark:bg-[#121715] border-y border-gray-200 dark:border-gray-850/60 py-20 transition-colors duration-200">
      <div class="max-w-7xl mx-auto px-6">
        <!-- Subheading -->
        <div class="text-center space-y-3 max-w-xl mx-auto mb-16">
          <h2 class="text-xs uppercase font-bold text-primary-600 dark:text-primary-400 tracking-widest">Technological Core</h2>
          <h3 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight leading-tight">Engineered for Sub-Saharan Resilience</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
            Our platform merges state-of-the-art vision models and low-connectivity system designs to serve the unique operational environments of African smallholders.
          </p>
        </div>

        <!-- Grids -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Card 1 -->
          <div class="bg-gray-50 dark:bg-darkbg-50/50 border border-gray-200 dark:border-gray-800 p-6 rounded-2xl hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
            <div class="space-y-4">
              <div class="h-12 w-12 rounded-2xl bg-primary-100 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400 flex items-center justify-center transition-colors group-hover:bg-primary-500 group-hover:text-white">
                <span class="material-icons-outlined text-2xl">wifi_off</span>
              </div>
              <h4 class="text-lg font-bold text-gray-950 dark:text-white leading-snug">Local-First & Offline Sync</h4>
              <p class="text-xs text-gray-550 dark:text-gray-400 leading-relaxed">
                Powered by IndexedDB caching. Records feed quantities, water consumption, weight samples, and vaccination logs completely offline. Saves modifications to a sync queue and pushes data automatically once network recovery occurs.
              </p>
            </div>
            <div class="pt-6 text-xs font-bold text-primary-600 dark:text-primary-400 flex items-center gap-1">
              <span>Read cache architecture</span>
              <span class="material-icons-outlined text-sm">chevron_right</span>
            </div>
          </div>

          <!-- Card 2 -->
          <div class="bg-gray-50 dark:bg-darkbg-50/50 border border-gray-200 dark:border-gray-800 p-6 rounded-2xl hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
            <div class="space-y-4">
              <div class="h-12 w-12 rounded-2xl bg-primary-100 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400 flex items-center justify-center transition-colors group-hover:bg-primary-500 group-hover:text-white">
                <span class="material-icons-outlined text-2xl">videocam</span>
              </div>
              <h4 class="text-lg font-bold text-gray-950 dark:text-white leading-snug">YOLOv8 AI Vision Feed</h4>
              <p class="text-xs text-gray-550 dark:text-gray-400 leading-relaxed">
                Processes video frames using lightweight YOLOv8 models. Measures bird counts, spatial distribution densities, and alerts operations if flocks show low mobility or cluster patterns indicating cold temperature stress.
              </p>
            </div>
            <div class="pt-6 text-xs font-bold text-primary-600 dark:text-primary-400 flex items-center gap-1">
              <span>Explore object maps</span>
              <span class="material-icons-outlined text-sm">chevron_right</span>
            </div>
          </div>

          <!-- Card 3 -->
          <div class="bg-gray-50 dark:bg-darkbg-50/50 border border-gray-200 dark:border-gray-800 p-6 rounded-2xl hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
            <div class="space-y-4">
              <div class="h-12 w-12 rounded-2xl bg-primary-100 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400 flex items-center justify-center transition-colors group-hover:bg-primary-500 group-hover:text-white">
                <span class="material-icons-outlined text-2xl">hearing</span>
              </div>
              <h4 class="text-lg font-bold text-gray-950 dark:text-white leading-snug">Bioacoustic Health Classifier</h4>
              <p class="text-xs text-gray-550 dark:text-gray-400 leading-relaxed">
                Monitors acoustic feeds inside broiler pens. Machine learning models extract sound distress ratios to flag high frequencies of coughing/chirping which indicate early respiratory warnings or predator presence.
              </p>
            </div>
            <div class="pt-6 text-xs font-bold text-primary-600 dark:text-primary-400 flex items-center gap-1">
              <span>View audio spectral rules</span>
              <span class="material-icons-outlined text-sm">chevron_right</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Interactive Simulation Section -->
    <section id="demo" class="relative z-10 py-20 max-w-7xl mx-auto px-6">
      <div class="bg-gray-50 dark:bg-darkbg-50 border border-gray-200 dark:border-gray-850/60 rounded-3xl p-8 md:p-12 shadow-sm grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <!-- Left explanation -->
        <div class="lg:col-span-5 space-y-6 text-left">
          <h2 class="text-xs uppercase font-bold text-primary-600 dark:text-primary-400 tracking-widest">Interactive Sandbox</h2>
          <h3 class="text-3xl font-black text-gray-900 dark:text-white tracking-tight leading-tight">Simulate Farm Scenarios</h3>
          <p class="text-sm text-gray-555 dark:text-gray-450 leading-relaxed">
            Choose a preset scenario below to watch how our reactive rule engines automatically process readings and generate immediate actions for operators:
          </p>

          <!-- Buttons -->
          <div class="flex flex-col space-y-3 pt-2">
            <button
              v-for="preset in presets"
              :key="preset.id"
              @click="selectPreset(preset)"
              class="w-full text-left p-4 rounded-xl border transition-all duration-200 focus:outline-none flex justify-between items-center"
              :class="[
                selectedPreset.id === preset.id
                  ? 'bg-primary-50 dark:bg-primary-950/40 border-primary-500 text-primary-800 dark:text-primary-400 font-bold shadow-sm'
                  : 'bg-white dark:bg-[#141a18] border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-350 hover:bg-gray-50 dark:hover:bg-gray-800/40'
              ]"
            >
              <div class="flex items-center space-x-3">
                <span class="material-icons-outlined text-lg" :class="selectedPreset.id === preset.id ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400'">{{ preset.icon }}</span>
                <span class="text-xs">{{ preset.name }}</span>
              </div>
              <span class="material-icons-outlined text-sm font-bold" :class="selectedPreset.id === preset.id ? 'text-primary-500' : 'text-gray-300'">radio_button_checked</span>
            </button>
          </div>
        </div>

        <!-- Right Visual Showcase -->
        <div class="lg:col-span-7 bg-white dark:bg-[#111816] rounded-2xl border border-gray-150 dark:border-gray-800 p-6 space-y-6 shadow-lg">
          <div class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800/80 pb-4">
            <div class="flex items-center space-x-2">
              <span class="material-icons-outlined text-primary-500 text-base">analytics</span>
              <span class="text-[11px] font-bold text-gray-450 dark:text-gray-500 uppercase tracking-widest">Smart Rule Simulator Output</span>
            </div>
            <AgriBadge :variant="selectedPreset.badgeType" :pulse="selectedPreset.badgeType === 'danger' || selectedPreset.badgeType === 'warning'">
              {{ selectedPreset.status }}
            </AgriBadge>
          </div>

          <!-- Gauges Grid -->
          <div class="grid grid-cols-3 gap-4">
            <div class="p-3.5 bg-gray-50 dark:bg-darkbg-50/50 rounded-xl border border-gray-150 dark:border-gray-800 flex flex-col justify-between">
              <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">🌡 Temperature</span>
              <p class="text-lg font-black text-gray-900 dark:text-white mt-1.5 transition-all duration-300">{{ selectedPreset.temp }}°C</p>
            </div>
            <div class="p-3.5 bg-gray-50 dark:bg-darkbg-50/50 rounded-xl border border-gray-150 dark:border-gray-800 flex flex-col justify-between">
              <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">💧 Humidity</span>
              <p class="text-lg font-black text-gray-900 dark:text-white mt-1.5 transition-all duration-300">{{ selectedPreset.humidity }}%</p>
            </div>
            <div class="p-3.5 bg-gray-50 dark:bg-darkbg-50/50 rounded-xl border border-gray-150 dark:border-gray-800 flex flex-col justify-between">
              <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">🍽 Feed Left</span>
              <p class="text-lg font-black text-gray-900 dark:text-white mt-1.5 transition-all duration-300">{{ selectedPreset.feed }} kg</p>
            </div>
          </div>

          <!-- AI Logic Assessment -->
          <div class="p-4 bg-gray-50 dark:bg-darkbg-50/60 border border-gray-150 dark:border-gray-800 rounded-xl space-y-2 text-left">
            <span class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest block">System Diagnostics</span>
            <p class="text-xs font-semibold text-gray-850 dark:text-gray-250 leading-relaxed">{{ selectedPreset.desc }}</p>
          </div>

          <!-- Action recommendation -->
          <div class="p-4 rounded-xl border flex gap-3 text-left items-start transition-all duration-200"
               :class="[
                 selectedPreset.badgeType === 'danger'
                   ? 'bg-red-50/40 dark:bg-red-950/20 border-red-200 dark:border-red-900/30 text-red-800 dark:text-red-400'
                   : selectedPreset.badgeType === 'warning'
                     ? 'bg-amber-50/40 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/30 text-amber-800 dark:text-amber-400'
                     : 'bg-emerald-50/45 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/30 text-emerald-800 dark:text-emerald-400'
               ]">
            <span class="material-icons-outlined text-lg mt-0.5">
              {{ selectedPreset.badgeType === 'danger' ? 'report_problem' : selectedPreset.badgeType === 'warning' ? 'warning' : 'task_alt' }}
            </span>
            <div>
              <p class="text-[10px] uppercase font-bold tracking-wider">Recommended Action</p>
              <p class="text-xs font-bold mt-0.5 leading-snug">{{ selectedPreset.action }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonial Section -->
    <section id="about" class="relative z-10 py-16 bg-white dark:bg-[#121715] border-t border-gray-200 dark:border-gray-850/60 transition-colors duration-200">
      <div class="max-w-4xl mx-auto px-6 text-center space-y-6">
        <span class="material-icons-outlined text-4xl text-primary-500 dark:text-primary-400">format_quote</span>
        <blockquote class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white tracking-tight leading-relaxed">
          "Before AgriSense AI, we had to check the shed manually every hour, and a disease outbreak could go unnoticed for days. Now, even when our mobile network drops out, we can log our daily numbers offline. The YOLOv8 camera detects count changes instantly, saving us hundreds of birds and reducing feed waste by 18%."
        </blockquote>
        <div class="space-y-1">
          <p class="font-extrabold text-gray-950 dark:text-white text-base">Evans Kabwe</p>
          <p class="text-xs font-semibold text-gray-450 dark:text-gray-500">Chief Operator · Prime Nest Poultry Sheds, Zambia</p>
        </div>
      </div>
    </section>

    <!-- Footer Gateway CTA -->
    <footer class="relative z-10 bg-gray-900 text-gray-300 py-16 transition-colors duration-200 border-t border-gray-800">
      <div class="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-12 gap-12">
        <div class="md:col-span-6 space-y-4 text-left">
          <div class="flex items-center space-x-2.5">
            <div class="h-9 w-9 rounded-xl bg-primary-600 flex items-center justify-center">
              <span class="material-icons-outlined text-white text-[18px]">agriculture</span>
            </div>
            <span class="text-[17px] font-black tracking-wide text-white uppercase">AGRISENSE AI</span>
          </div>
          <p class="text-xs text-gray-450 leading-relaxed max-w-sm">
            Providing next-generation agricultural technology solutions for Sub-Saharan poultry farms. Fully functional offline-first interfaces designed for tablets.
          </p>
        </div>

        <div class="md:col-span-6 space-y-6 text-left md:text-right flex flex-col justify-between items-start md:items-end">
          <div class="space-y-2">
            <h4 class="text-lg font-bold text-white tracking-tight">Ready to optimize your poultry operations?</h4>
            <p class="text-xs text-gray-450">Launch the operator portal today and start monitoring telemetry trends.</p>
          </div>

          <div class="pt-4 flex flex-wrap gap-4">
            <AgriButton
              variant="outline"
              size="md"
              class="border-gray-700 text-gray-350 hover:bg-gray-800 hover:text-white"
              @click="navigateToLogin"
            >
              Sign In
            </AgriButton>
            <AgriButton
              variant="primary"
              size="md"
              icon="rocket_launch"
              @click="navigateToLogin"
            >
              Get Started
            </AgriButton>
          </div>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-6 mt-16 pt-6 border-t border-gray-800 text-center md:text-left flex flex-col md:flex-row justify-between text-[11px] text-gray-500">
        <span>© 2026 AgriSense AI. All rights reserved.</span>
        <span class="mt-2 md:mt-0">v1.0.0 · Sub-Saharan AgriTech Framework</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AgriButton from '../components/ui/AgriButton.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'

const router = useRouter()

const isDark = ref(false)

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

const navigateToLogin = () => {
  router.push({ name: 'Login' })
}

const scrollToDemo = () => {
  const el = document.getElementById('demo')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

// Sandbox presets simulation data
const presets = [
  {
    id: 'normal',
    name: 'Normal Telemetry Run',
    icon: 'task_alt',
    temp: '24.2',
    humidity: '62',
    feed: '1,250',
    status: 'Optimal Conditions',
    badgeType: 'success',
    desc: 'Coop parameters are in bounds. Temperature and relative humidity meet breed criteria for Cobb 500 broilers. Feed silos show healthy capacity levels.',
    action: 'No manual correction needed. Sensor polling active.'
  },
  {
    id: 'heatwave',
    name: 'Critical Heat Alert',
    icon: 'thermostat',
    temp: '34.8',
    humidity: '78',
    feed: '1,230',
    status: 'Heat Stress Danger',
    badgeType: 'danger',
    desc: 'Temperature registers 34.8°C, which is 6.8°C above target. High relative humidity prevents self-cooling. High clustering hazard warning from YOLO spatial maps.',
    action: 'Activate supplementary tunnel fans. Inspect water spray mist nozzles immediately.'
  },
  {
    id: 'feed_empty',
    name: 'Empty Silo Warning',
    icon: 'restaurant',
    temp: '24.1',
    humidity: '60',
    feed: '85',
    status: 'Silo Level Critical',
    badgeType: 'warning',
    desc: 'Feed reservoir registers below the 100 kg threshold. Automated auger feeders will experience empty runs within 3 hours. Bird counts remain normal.',
    action: 'Dispatch replacement feed bags. Verify batch feed logs in Operator Portal.'
  }
]

const selectedPreset = ref(presets[0])

const selectPreset = (preset) => {
  selectedPreset.value = preset
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  isDark.value = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme()
})
</script>

<style scoped>
.animate-bounce-slow {
  animation: bounce-slow 3s infinite ease-in-out;
}
@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
</style>
