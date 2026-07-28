<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ $t('audio.title') }}</h1>
          <AgriBadge variant="warning" icon="science">{{ $t('audio.research_preview') }}</AgriBadge>
        </div>
        <p class="mt-0.5 text-sm text-gray-550 dark:text-gray-400">
          {{ $t('audio.subtitle') }}
        </p>
      </div>
    </div>

    <!-- Live Recording / Microphone Status Panel -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in-up delay-75">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-red-50 dark:bg-red-950/40 text-red-650 dark:text-red-400 flex items-center justify-center">
          <span class="material-icons-outlined animate-pulse text-[20px]">settings_voice</span>
        </div>
        <div>
          <h2 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
            Mic Cluster #1 (House A-Central)
            <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-50 dark:bg-red-950/40 border border-red-100 dark:border-red-900/35">
              <span class="relative flex h-1.5 w-1.5 shrink-0">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-650"></span>
              </span>
              <span class="text-[9px] font-bold text-red-600 dark:text-red-400 uppercase tracking-wider">{{ $t('audio.live_recording') }}</span>
            </div>
          </h2>
          <p class="text-xs text-gray-500 mt-0.5">{{ $t('audio.capturing') }}</p>
        </div>
      </div>
      <!-- Quick distress overview status -->
      <div class="flex items-center gap-2">
        <span class="text-xs font-semibold text-gray-500">{{ $t('audio.distress_status') }}</span>
        <AgriBadge
          :variant="selectedSample?.id === 'live_mic' ? (liveSeverity === 'Normal' ? 'success' : (liveSeverity === 'Warning' ? 'warning' : 'critical')) : 'success'"
          :icon="selectedSample?.id === 'live_mic' ? (liveSeverity === 'Normal' ? 'check' : (liveSeverity === 'Warning' ? 'warning' : 'error')) : 'check'"
          :pulse="selectedSample?.id === 'live_mic' && liveSeverity !== 'Normal'"
        >
          {{ selectedSample?.id === 'live_mic' ? liveSeverity : $t('audio.normal') }}
        </AgriBadge>
      </div>
    </div>

    <!-- Alert Box emphasizing Illustrative/Research preview status -->
    <div class="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 rounded-xl p-4 flex items-start space-x-3 text-amber-850 dark:text-amber-300 text-xs font-semibold animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-amber-600 dark:text-amber-400 shrink-0 mt-0.5">science</span>
      <div>
        <span class="font-bold">{{ $t('audio.research_stage') }}</span> {{ $t('audio.research_desc') }}
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- ─── Left Pane: Soundboard & Settings ─── -->
      <div class="lg:col-span-1 space-y-4 animate-fade-in-up delay-150">
        <AgriCard id="audio-library-card">
          <template #header>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('audio.acoustic_library') }}</h2>
            <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">4 Profiles</span>
          </template>

          <div class="space-y-3">
            <div
              v-for="s in samples"
              :key="s.id"
              @click="selectSample(s)"
              class="w-full text-left p-4.5 rounded-xl border transition cursor-pointer flex items-center justify-between group active-press"
              :class="selectedSample?.id === s.id
                ? 'border-primary-500 bg-primary-50/20 dark:bg-primary-950/10'
                : 'border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700'"
            >
              <div class="space-y-1 pr-2 truncate">
                <p class="text-xs font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition truncate">{{ s.title }}</p>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 font-mono">{{ s.frequencyRange }}</p>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <AgriBadge
                  :variant="s.severity === 'Normal' ? 'success' : (s.severity === 'Warning' ? 'warning' : 'critical')"
                  :pulse="s.severity === 'Critical'"
                  size="xs"
                >
                  {{ s.severity }}
                </AgriBadge>
                <div class="h-8 w-8 rounded-full bg-gray-50 group-hover:bg-primary-500/15 dark:bg-darkbg-100 flex items-center justify-center transition">
                  <span class="material-icons-outlined text-sm text-gray-600 dark:text-gray-450 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition leading-none">
                    {{ isPlaying && selectedSample?.id === s.id ? 'pause' : 'play_arrow' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </AgriCard>

        <!-- ML Classifier Settings -->
        <AgriCard>
          <template #header>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">{{ $t('audio.ml_settings') }}</h2>
            <span class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">{{ $t('audio.adjust') }}</span>
          </template>

          <div class="space-y-6">
            <!-- Cough Threshold -->
            <div class="space-y-2">
              <div class="flex justify-between items-end">
                <label class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('audio.cough_sensitivity') }}</label>
                <span class="text-xs font-mono font-bold" :class="audioConfig.cough_threshold_pct < 50 ? 'text-status-danger' : 'text-gray-500'">{{ Math.round(audioConfig.cough_threshold_pct) }}%</span>
              </div>
              <input type="range" min="10" max="100" v-model.number="audioConfig.cough_threshold_pct" @change="saveConfig" class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-primary-600">
              <p class="text-[10px] text-gray-450 dark:text-gray-500">{{ $t('audio.cough_desc') }}</p>
            </div>

            <!-- Chirp Threshold -->
            <div class="space-y-2">
              <div class="flex justify-between items-end">
                <label class="text-xs font-bold text-gray-700 dark:text-gray-300">{{ $t('audio.chirp_sensitivity') }}</label>
                <span class="text-xs font-mono font-bold" :class="audioConfig.chirp_threshold_pct < 50 ? 'text-status-danger' : 'text-gray-500'">{{ Math.round(audioConfig.chirp_threshold_pct) }}%</span>
              </div>
              <input type="range" min="10" max="100" v-model.number="audioConfig.chirp_threshold_pct" @change="saveConfig" class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-primary-600">
              <p class="text-[10px] text-gray-450 dark:text-gray-500">{{ $t('audio.chirp_desc') }}</p>
            </div>
            
            <div v-if="offlineMode" class="text-[10px] flex items-center gap-1.5 text-amber-600 dark:text-amber-400 mt-2">
              <span class="material-icons-outlined text-[14px]">wifi_off</span>
              {{ $t('audio.offline_sync') }}
            </div>
          </div>
        </AgriCard>
      </div>

      <!-- ─── Right Pane: Oscilloscope & Spectral Details ─── -->
      <div class="lg:col-span-2 space-y-6 animate-fade-in-up delay-200">

        <div v-if="!selectedSample" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center flex flex-col items-center justify-center h-full min-h-[400px]">
          <span class="material-icons-outlined text-5xl text-gray-300 dark:text-gray-700 mb-3 animate-pulse">settings_voice</span>
          <h3 class="font-bold text-gray-700 dark:text-gray-300 text-sm">{{ $t('audio.select_sample') }}</h3>
          <p class="text-xs text-gray-450 dark:text-gray-500 mt-1 max-w-xs mx-auto">
            {{ $t('audio.select_desc') }}
          </p>
        </div>

        <template v-else>
          <!-- Dynamic Spectrogram/Waveform Player -->
          <AgriCard>
            <template #header>
              <div>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white">{{ selectedSample.title }} Analysis</h3>
                <p class="text-[10px] text-gray-450 dark:text-gray-500">{{ $t('audio.spectral_sig') }} {{ selectedSample.frequencyRange }}</p>
              </div>
              <AgriButton
                variant="primary"
                size="sm"
                :icon="isPlaying ? 'pause' : 'volume_up'"
                @click="togglePlayback"
              >
                {{ isPlaying ? $t('audio.mute_sample') : $t('audio.listen_synthesized') }}
              </AgriButton>
            </template>

            <!-- Waveform Canvas -->
            <div class="bg-gray-950 rounded-2xl h-44 overflow-hidden border border-gray-900 flex items-center justify-center relative shadow-inner">
              <canvas ref="waveCanvas" class="w-full h-full"></canvas>
              <!-- Bouncing decibel meter -->
              <div class="absolute bottom-3 right-4 bg-black/60 text-white text-[9px] font-bold tracking-widest px-2.5 py-1 rounded uppercase flex items-center gap-1 select-none">
                <span class="h-1.5 w-1.5 rounded-full bg-primary-400" :class="isPlaying ? 'animate-ping' : ''"></span>
                {{ isPlaying ? 'Dynamic Oscillator' : 'Idle Spectrum' }}
              </div>
            </div>

            <!-- Analytics Dashboard -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
              <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850 rounded-xl p-4 space-y-1">
                <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{{ $t('audio.distress_prob') }}</p>
                <div class="text-2xl font-black tabular-nums" :class="getSeverityTextClass(selectedSample.severity)">
                  {{ selectedSample.distressProb }}%
                </div>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">{{ $t('audio.calc_weight') }}</p>
              </div>

              <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850 rounded-xl p-4 space-y-1">
                <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{{ $t('audio.dominant_peak') }}</p>
                <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
                  {{ selectedSample.dominantPeak }}
                </div>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">{{ $t('audio.exc_threshold') }}</p>
              </div>

              <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850 rounded-xl p-4 space-y-1">
                <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{{ $t('audio.flock_cohesion') }}</p>
                <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
                  {{ selectedSample.cohesion }}%
                </div>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">{{ $t('audio.spatial_metrics') }}</p>
              </div>
            </div>
          </AgriCard>

          <!-- Recommendations & Clinical Notes -->
          <div
            class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-4 animate-scale-in"
            :class="selectedSample.severity === 'Critical' ? 'border-red-250 dark:border-red-950 bg-red-50/5' : ''"
          >
            <h4 class="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
              :class="selectedSample.severity === 'Critical' ? 'text-status-danger' : 'text-primary-650 dark:text-primary-400'">
              <span class="material-icons-outlined text-[16px] font-semibold">health_and_safety</span>
              {{ $t('audio.clinical_diag') }}
            </h4>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
              <div class="space-y-2">
                <h5 class="font-bold text-gray-900 dark:text-white text-xs">{{ $t('audio.voc_details') }}</h5>
                <p class="text-xs text-gray-600 dark:text-gray-450 leading-relaxed font-semibold">
                  {{ selectedSample.description }}
                </p>
              </div>
              <div class="space-y-2">
                <h5 class="font-bold text-gray-900 dark:text-white text-xs">{{ $t('audio.management') }}</h5>
                <ul class="text-xs text-gray-650 dark:text-gray-400 space-y-2 list-disc pl-4 font-semibold">
                  <li v-for="(inst, i) in selectedSample.instructions" :key="i">{{ inst }}</li>
                </ul>
              </div>
            </div>
          </div>
        </template>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, nextTick, computed, onMounted, watch } from 'vue'
import { api } from '../services/api'
import { store } from '../services/store'
import { useToast } from '../composables/useToast'

// Design System components
import AgriCard from '../components/ui/AgriCard.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriButton from '../components/ui/AgriButton.vue'

const toast = useToast()

const offlineMode = ref(false)

// Live Microphone Analyzer state
const liveSeverity = ref('Normal')
const liveDistressProb = ref(0)
const livePeak = ref('—')
const liveCohesion = ref(100)
const liveDescription = ref('Analyzing live audio stream from your computer microphone. Data is being sent to the telemetry backend.')
const isLiveMicConnected = ref(false)

const audioConfig = ref({
  cough_threshold_pct: 80.0,
  chirp_threshold_pct: 65.0
})

const loadConfig = async () => {
  if (!store.currentFarm?.id) return
  try {
    const config = await api.audio.getConfig(store.currentFarm.id)
    if (config) {
      audioConfig.value.cough_threshold_pct = config.cough_threshold_pct
      audioConfig.value.chirp_threshold_pct = config.chirp_threshold_pct
      offlineMode.value = !!config.offline
    }
  } catch (err) {
    console.error('Failed to load audio config:', err)
  }
}

const saveConfig = async () => {
  if (!store.currentFarm?.id) return
  try {
    const res = await api.audio.updateConfig(store.currentFarm.id, {
      cough_threshold_pct: audioConfig.value.cough_threshold_pct,
      chirp_threshold_pct: audioConfig.value.chirp_threshold_pct
    })
    if (res?.offline) {
      offlineMode.value = true
    } else {
      offlineMode.value = false
    }
  } catch (err) {
    console.error('Failed to save audio config:', err)
  }
}

onMounted(() => {
  loadConfig()
})

// ── Synthesized Sound Profiles ────────────────
const samples = computed(() => {
  return [
    {
      id: 'healthy',
      title: 'Baseline Healthy Clucking (Normal)',
      frequencyRange: '200 Hz - 850 Hz',
      severity: 'Normal',
      distressProb: 1.2,
      dominantPeak: '420 Hz',
      cohesion: 96,
      waveType: 'sine',
      baseFreq: 261.63, // C4
      description: 'Steady, repetitive low-amplitude chuckles. Birds exhibit uniform spacing, normal posture, and healthy feeding behavior. Signals high flock comfort and well-being.',
      instructions: [
        'No immediate operations needed.',
        'Maintain standard automated feeding schedules.',
        'Verify water pressure gauges are within baseline ranges.'
      ]
    },
    {
      id: 'thermal',
      title: 'High-Pitch Chirping (Thermal Distress)',
      frequencyRange: '3000 Hz - 5500 Hz',
      severity: 76.8 >= audioConfig.value.chirp_threshold_pct ? 'Warning' : 'Normal',
      distressProb: 76.8,
      dominantPeak: '3600 Hz',
      cohesion: 71,
      waveType: 'sine',
      baseFreq: 880.00, // A5
      description: 'Sharp, loud, rapid high-frequency chirps. Typical indicator of temperature lagging (cold/draft stress causing birds to huddle) or heat spikes (causing panting and dispersal).',
      instructions: [
        'Perform house inspection immediately.',
        'Check heating line / heat pads if age is under 14 days.',
        'Verify air circulation fans and pad cooling statuses.',
        'Confirm thermal probes are calibrated correctly.'
      ]
    },
    {
      id: 'feeding',
      title: 'Rhythmic Excitement (Feeding Alert)',
      frequencyRange: '800 Hz - 1800 Hz',
      severity: 'Normal',
      distressProb: 14.5,
      dominantPeak: '1200 Hz',
      cohesion: 88,
      waveType: 'triangle',
      baseFreq: 329.63, // E4
      description: 'Highly active rhythmic call bursts coinciding with hopper distribution motor cycles. Normal soundscape of flock eating and moving towards feed lanes.',
      instructions: [
        'Monitor hopper distribution timers.',
        'Check that feed line level gauges register normal levels.',
        'No distress interventions required.'
      ]
    },
    {
      id: 'respiratory',
      title: 'Raspy Gasping (Pathology Risk)',
      frequencyRange: '1500 Hz - 3200 Hz',
      severity: 92.4 >= audioConfig.value.cough_threshold_pct ? 'Critical' : 'Warning',
      distressProb: 92.4,
      dominantPeak: '2400 Hz',
      cohesion: 48,
      waveType: 'sawtooth',
      baseFreq: 110.00, // A2
      description: 'Raspy, congested cough noises combined with whistling gasps. Strongly suggests respiratory congestion, ventilation failure, high ammonia density, or viral pathogens.',
      instructions: [
        'Immediate physical evaluation recommended.',
        'Inspect mechanical extraction fans & side air dampers.',
        'Check ammonia (NH3) gas sensor levels — target < 20 ppm.',
        'Alert attending veterinary staff for flock swab evaluation.'
      ]
    },
    {
      id: 'live_mic',
      title: 'Live Local Microphone (Active Scan)',
      frequencyRange: '20 Hz - 20,000 Hz',
      severity: liveSeverity.value,
      distressProb: liveDistressProb.value,
      dominantPeak: livePeak.value,
      cohesion: liveCohesion.value,
      description: liveDescription.value,
      instructions: [
        'Make sounds (clap, click, speak) to observe real-time frequency waveforms.',
        'Adjust Cough/Chirp sensitivity filters in ML Settings panel.',
        'High decibel triggers will raise system respiratory alerts.'
      ]
    }
  ]
})

// ── State ──────────────────────────────────
const selectedSample = ref(null)
const isPlaying = ref(false)
const waveCanvas = ref(null)

let audioCtx = null
let oscillator = null
let gainNode = null
let canvasCtx = null
let animationFrameId = null

// Live Mic Streams
let micStream = null
let micAnalyser = null
let micSource = null
let micDataArray = null
let mediaRecorder = null
let recordIntervalId = null

const connectMicrophone = async () => {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    initAudio()
    if (audioCtx.state === 'suspended') {
      await audioCtx.resume()
    }
    
    micAnalyser = audioCtx.createAnalyser()
    micAnalyser.fftSize = 256
    
    micSource = audioCtx.createMediaStreamSource(micStream)
    micSource.connect(micAnalyser)
    
    const bufferLength = micAnalyser.frequencyBinCount
    micDataArray = new Uint8Array(bufferLength)

    // Setup Telemetry MediaRecorder
    try {
      mediaRecorder = new MediaRecorder(micStream, { mimeType: 'audio/webm' })
      mediaRecorder.ondataavailable = async (e) => {
        if (e.data.size > 0 && store.currentFarm?.id) {
          try {
            const result = await api.audio.classify(store.currentFarm.id, e.data)
            if (result) {
              liveDistressProb.value = result.distressProb
              liveSeverity.value = result.severity
              livePeak.value = result.dominantPeak
              liveCohesion.value = result.cohesion
              liveDescription.value = result.description
            }
          } catch (err) {
            console.error("Telemetry upload failed:", err)
          }
        }
      }
      mediaRecorder.start()
      
      // Capture slices every 3 seconds
      recordIntervalId = setInterval(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.stop()
          mediaRecorder.start()
        }
      }, 3000)
    } catch (mrErr) {
      console.warn("MediaRecorder setup failed (browser may not support it):", mrErr)
    }
    
    isLiveMicConnected.value = true
    isPlaying.value = true
    
    nextTick(() => {
      startAnimation()
    })
  } catch (err) {
    console.error('Mic access denied:', err)
    alert('Microphone access denied: ' + err.message)
    selectedSample.value = null
  }
}

const disconnectMicrophone = () => {
  if (recordIntervalId) {
    clearInterval(recordIntervalId)
    recordIntervalId = null
  }
  if (mediaRecorder) {
    if (mediaRecorder.state !== 'inactive') mediaRecorder.stop()
    mediaRecorder = null
  }
  if (micStream) {
    micStream.getTracks().forEach(track => track.stop())
    micStream = null
  }
  if (micSource) {
    micSource.disconnect()
    micSource = null
  }
  if (micAnalyser) {
    micAnalyser.disconnect()
    micAnalyser = null
  }
  isLiveMicConnected.value = false
  isPlaying.value = false
}

// ── Sound Selection ────────────────────────
const selectSample = (sample) => {
  const previousWasMic = selectedSample.value?.id === 'live_mic'
  stopSound()
  if (previousWasMic) {
    disconnectMicrophone()
  }
  selectedSample.value = sample
  
  if (sample.id === 'live_mic') {
    connectMicrophone()
  } else {
    nextTick(() => {
      startAnimation()
    })
  }
}

// ── Web Audio API Sound Generation ──────────
const initAudio = () => {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)()
  }
}

const playSound = () => {
  if (!selectedSample.value) return
  if (selectedSample.value.id === 'live_mic') {
    connectMicrophone()
    return
  }
  initAudio()

  oscillator = audioCtx.createOscillator()
  gainNode = audioCtx.createGain()

  oscillator.type = selectedSample.value.waveType
  oscillator.frequency.setValueAtTime(selectedSample.value.baseFreq, audioCtx.currentTime)

  const modulationSpeed = selectedSample.value.id === 'thermal' ? 25 : (selectedSample.value.id === 'healthy' ? 8 : 12)
  const modulationDepth = selectedSample.value.id === 'thermal' ? 200 : (selectedSample.value.id === 'healthy' ? 30 : 70)
  
  const now = audioCtx.currentTime
  for (let i = 0; i < 60; i++) {
    const t = now + i * 0.1
    const freqMod = Math.sin(i * (modulationSpeed / 10)) * modulationDepth
    oscillator.frequency.setValueAtTime(selectedSample.value.baseFreq + freqMod, t)
  }

  gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime)
  
  oscillator.connect(gainNode)
  gainNode.connect(audioCtx.destination)
  oscillator.start()
  isPlaying.value = true
}

const stopSound = () => {
  if (selectedSample.value?.id === 'live_mic') {
    disconnectMicrophone()
    return
  }
  if (oscillator) {
    try {
      oscillator.stop()
      oscillator.disconnect()
    } catch (_) {}
    oscillator = null
  }
  if (gainNode) {
    gainNode.disconnect()
    gainNode = null
  }
  isPlaying.value = false
}

const togglePlayback = () => {
  if (isPlaying.value) {
    stopSound()
  } else {
    playSound()
  }
}

// ── Oscilloscope Canvas Animation ──────────
const startAnimation = () => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }

  if (!waveCanvas.value) return
  const canvas = waveCanvas.value
  canvasCtx = canvas.getContext('2d')

  canvas.width = canvas.parentElement.clientWidth
  canvas.height = canvas.parentElement.clientHeight

  let phase = 0

  const draw = () => {
    if (!canvasCtx || !selectedSample.value) return

    const width = canvas.width
    const height = canvas.height

    canvasCtx.fillStyle = '#141416'
    canvasCtx.fillRect(0, 0, width, height)

    canvasCtx.strokeStyle = 'rgba(255, 255, 255, 0.03)'
    canvasCtx.lineWidth = 1
    for (let i = 1; i < 8; i++) {
      const x = (width / 8) * i
      canvasCtx.beginPath()
      canvasCtx.moveTo(x, 0)
      canvasCtx.lineTo(x, height)
      canvasCtx.stroke()
    }
    for (let i = 1; i < 4; i++) {
      const y = (height / 4) * i
      canvasCtx.beginPath()
      canvasCtx.moveTo(0, y)
      canvasCtx.lineTo(width, y)
      canvasCtx.stroke()
    }

    if (selectedSample.value.id === 'live_mic' && micAnalyser) {
      micAnalyser.getByteTimeDomainData(micDataArray)
      const bufferLength = micAnalyser.frequencyBinCount
      
      // Calculate RMS just for oscilloscope display purposes if needed, 
      // but bypass assigning to live severity (now handled by backend)
      let sumOfSquares = 0
      for (let i = 0; i < bufferLength; i++) {
        const v = (micDataArray[i] - 128) / 128.0
        sumOfSquares += v * v
      }
      // We don't overwrite liveDistressProb.value or liveSeverity.value anymore
      // because they are asynchronously updated by the backend Telemetry payload.

      // Draw active mic waveform
      canvasCtx.beginPath()
      canvasCtx.lineWidth = 2
      canvasCtx.strokeStyle = liveSeverity.value === 'Normal'
        ? '#2d6a4f'
        : (liveSeverity.value === 'Warning' ? '#f4a261' : '#e76f51')
      
      const sliceWidth = width / bufferLength
      let x = 0
      for (let i = 0; i < bufferLength; i++) {
        const v = micDataArray[i] / 128.0
        const y = v * (height / 2)
        
        if (i === 0) {
          canvasCtx.moveTo(x, y)
        } else {
          canvasCtx.lineTo(x, y)
        }
        x += sliceWidth
      }
      canvasCtx.stroke()
    } else {
      // Draw reference synthesized waves or idle waves (original loop)
      canvasCtx.beginPath()
      canvasCtx.lineWidth = 2
      canvasCtx.strokeStyle = selectedSample.value.severity === 'Normal'
        ? '#2d6a4f'
        : (selectedSample.value.severity === 'Warning' ? '#f4a261' : '#e76f51')

      const amp = isPlaying.value ? 45 : 8
      const freq = selectedSample.value.id === 'thermal' ? 0.08 : (selectedSample.value.id === 'healthy' ? 0.02 : 0.04)

      for (let x = 0; x < width; x++) {
        let y = height / 2
        if (isPlaying.value) {
          if (selectedSample.value.id === 'healthy') {
            y += Math.sin(x * freq + phase) * amp * (0.8 + 0.2 * Math.sin(phase * 0.5))
          } else if (selectedSample.value.id === 'thermal') {
            y += Math.sin(x * freq + phase) * amp * (Math.sin(x * 0.005 + phase * 0.2) > 0.4 ? 1 : 0.1)
          } else if (selectedSample.value.id === 'feeding') {
            y += Math.sin(x * freq + phase) * amp * Math.cos(x * 0.01 + phase * 0.05)
          } else {
            const noise = (Math.random() - 0.5) * 12
            const sawtooth = ((x * freq + phase) % 2) - 1
            y += (sawtooth * amp) + noise
          }
        } else {
          y += (Math.random() - 0.5) * 2 + Math.sin(x * 0.01 + phase) * 2
        }

        if (x === 0) {
          canvasCtx.moveTo(x, y)
        } else {
          canvasCtx.lineTo(x, y)
        }
      }
      canvasCtx.stroke()
    }

    phase += isPlaying.value ? 0.25 : 0.03
    animationFrameId = requestAnimationFrame(draw)
  }

  draw()
}

// ── Formatting ──────────────────────────
const getSeverityTextClass = (sev) => {
  if (sev === 'Normal') return 'text-primary-600 dark:text-primary-400'
  if (sev === 'Warning') return 'text-status-warning'
  return 'text-status-danger'
}

const getStaggerDelayClass = (idx) => {
  const delays = [50, 100, 150, 200]
  return `delay-${delays[idx] || 200}`
}

onUnmounted(() => {
  stopSound()
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})
</script>
