<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Audio Insights</h1>
          <span class="bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-900">Research Preview</span>
        </div>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Acoustic library analyzing bird behavior distress signals and vocalization frequencies.
        </p>
      </div>
    </div>

    <!-- Alert Box emphasizing Illustrative/Research preview status -->
    <div class="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 rounded-xl p-4 flex items-start space-x-3 text-amber-850 dark:text-amber-300 text-sm">
      <span class="material-icons-outlined text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5">science</span>
      <div>
        <span class="font-semibold">Research Stage Feature:</span> This module illustrates acoustic distress indicators. Real-time, continuous microphone cluster integration is slated for Phase 2.
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- ─── Left Pane: Soundboard ─── -->
      <div class="lg:col-span-1 space-y-4">
        <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Acoustic Samples Library</h2>
            <span class="text-[10px] font-bold text-gray-400 uppercase">4 Profiles</span>
          </div>

          <div class="space-y-3">
            <div
              v-for="s in samples"
              :key="s.id"
              @click="selectSample(s)"
              class="w-full text-left p-4 rounded-xl border transition cursor-pointer flex items-center justify-between group"
              :class="selectedSample?.id === s.id
                ? 'border-primary-500 bg-primary-50/10 dark:bg-primary-950/5'
                : 'border-gray-200 dark:border-gray-850 hover:border-gray-300 dark:hover:border-gray-700'"
            >
              <div class="space-y-1">
                <p class="text-xs font-bold text-gray-950 dark:text-white group-hover:text-primary-500 transition">{{ s.title }}</p>
                <p class="text-[10px] text-gray-500 dark:text-gray-400">{{ s.frequencyRange }}</p>
              </div>
              <div class="flex items-center gap-2">
                <span
                  class="text-[9px] font-extrabold px-1.5 py-0.5 rounded"
                  :class="s.severity === 'Normal' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30' : (s.severity === 'Warning' ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/30' : 'bg-red-50 text-red-700 dark:bg-red-950/30')"
                >
                  {{ s.severity }}
                </span>
                <button class="h-8 w-8 rounded-full bg-gray-50 group-hover:bg-primary-500/20 dark:bg-gray-850 flex items-center justify-center transition">
                  <span class="material-icons-outlined text-sm text-gray-650 dark:text-gray-400 group-hover:text-primary-500 transition">
                    {{ isPlaying && selectedSample?.id === s.id ? 'pause' : 'play_arrow' }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── Right Pane: Oscilloscope & Spectral Details ─── -->
      <div class="lg:col-span-2 space-y-6">

        <div v-if="!selectedSample" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center flex flex-col items-center justify-center h-full min-h-[400px]">
          <span class="material-icons-outlined text-5xl text-gray-300 dark:text-gray-700 mb-3 animate-pulse">settings_voice</span>
          <h3 class="font-bold text-gray-700 dark:text-gray-300 text-sm">Select an acoustic sample</h3>
          <p class="text-xs text-gray-450 dark:text-gray-500 mt-1 max-w-xs mx-auto">
            Choose a profile from the library to play synthesized soundscapes, inspect the frequency spectrum, and view clinical recommendations.
          </p>
        </div>

        <template v-else>
          <!-- Dynamic Spectrogram/Waveform Player -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm p-5 space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-sm font-bold text-gray-900 dark:text-white">{{ selectedSample.title }} Analysis</h3>
                <p class="text-[10px] text-gray-400 dark:text-gray-500">Spectral signature: {{ selectedSample.frequencyRange }}</p>
              </div>
              <button
                @click="togglePlayback"
                class="bg-primary-600 hover:bg-primary-500 text-white font-bold px-4 py-2 rounded-xl shadow-sm flex items-center gap-1.5 text-xs transition"
              >
                <span class="material-icons-outlined text-sm">{{ isPlaying ? 'pause' : 'volume_up' }}</span>
                {{ isPlaying ? 'Mute Sample' : 'Listen Synthesized' }}
              </button>
            </div>

            <!-- Waveform Canvas -->
            <div class="bg-gray-950 rounded-2xl h-44 overflow-hidden border border-gray-900 flex items-center justify-center relative shadow-inner">
              <canvas ref="waveCanvas" class="w-full h-full"></canvas>
              <!-- Bouncing decibel meter -->
              <div class="absolute bottom-3 right-4 bg-black/60 text-white text-[9px] font-bold tracking-widest px-2 py-0.5 rounded uppercase flex items-center gap-1">
                <span class="h-1.5 w-1.5 rounded-full bg-primary-400" :class="isPlaying ? 'animate-ping' : ''"></span>
                {{ isPlaying ? 'Dynamic Oscillator' : 'Idle Spectrum' }}
              </div>
            </div>

            <!-- Analytics Dashboard -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-100 dark:border-gray-850 rounded-xl p-4 space-y-1">
                <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Distress Probability</p>
                <div class="text-2xl font-black tabular-nums" :class="getSeverityTextClass(selectedSample.severity)">
                  {{ selectedSample.distressProb }}%
                </div>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Calculated via frequency weighting</p>
              </div>

              <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-100 dark:border-gray-850 rounded-xl p-4 space-y-1">
                <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Dominant Peak</p>
                <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
                  {{ selectedSample.dominantPeak }}
                </div>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Excitation threshold limit</p>
              </div>

              <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-100 dark:border-gray-850 rounded-xl p-4 space-y-1">
                <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Flock Cohesion</p>
                <div class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">
                  {{ selectedSample.cohesion }}%
                </div>
                <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Spatial correlation metrics</p>
              </div>
            </div>
          </div>

          <!-- Recommendations & Clinical Notes -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-4">
            <h4 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
              <span class="material-icons-outlined text-[16px] text-primary-600 dark:text-primary-400 font-semibold">health_and_safety</span>
              Clinical Diagnostics & Action Plan
            </h4>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
              <div class="space-y-2">
                <h5 class="font-bold text-gray-900 dark:text-white text-xs">Vocalization Details</h5>
                <p class="text-xs text-gray-600 dark:text-gray-450 leading-relaxed">
                  {{ selectedSample.description }}
                </p>
              </div>
              <div class="space-y-2">
                <h5 class="font-bold text-gray-900 dark:text-white text-xs">Management Instructions</h5>
                <ul class="text-xs text-gray-650 dark:text-gray-400 space-y-1.5 list-disc pl-4">
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
import { ref, onUnmounted, nextTick } from 'vue'

// ── Synthesized Sound Profiles ────────────────
const samples = [
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
    severity: 'Warning',
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
    severity: 'Critical',
    distressProb: 92.4,
    dominantPeak: '2400 Hz',
    cohesion: 48,
    waveType: 'sawtooth',
    baseFreq: 110.00, // A2 (low raspy rumble)
    description: 'Raspy, congested cough noises combined with whistling gasps. Strongly suggests respiratory congestion, ventilation failure, high ammonia density, or viral pathogens.',
    instructions: [
      'Immediate physical evaluation recommended.',
      'Inspect mechanical extraction fans & side air dampers.',
      'Check ammonia (NH3) gas sensor levels — target < 20 ppm.',
      'Alert attending veterinary staff for flock swab evaluation.'
    ]
  }
]

// ── State ──────────────────────────────────
const selectedSample = ref(null)
const isPlaying = ref(false)
const waveCanvas = ref(null)

let audioCtx = null
let oscillator = null
let gainNode = null
let canvasCtx = null
let animationFrameId = null

// ── Sound Selection ────────────────────────
const selectSample = (sample) => {
  stopSound()
  selectedSample.value = sample
  nextTick(() => {
    startAnimation()
  })
}

// ── Web Audio API Sound Generation ──────────
const initAudio = () => {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)()
  }
}

const playSound = () => {
  if (!selectedSample.value) return
  initAudio()

  oscillator = audioCtx.createOscillator()
  gainNode = audioCtx.createGain()

  oscillator.type = selectedSample.value.waveType
  // Set frequency based on profile
  oscillator.frequency.setValueAtTime(selectedSample.value.baseFreq, audioCtx.currentTime)

  // Modulate frequency to simulate natural bird call fluctuations
  const modulationSpeed = selectedSample.value.id === 'thermal' ? 25 : (selectedSample.value.id === 'healthy' ? 8 : 12)
  const modulationDepth = selectedSample.value.id === 'thermal' ? 200 : (selectedSample.value.id === 'healthy' ? 30 : 70)
  
  const now = audioCtx.currentTime
  for (let i = 0; i < 60; i++) {
    const t = now + i * 0.1
    // Generate organic chirping sounds
    const freqMod = Math.sin(i * (modulationSpeed / 10)) * modulationDepth
    oscillator.frequency.setValueAtTime(selectedSample.value.baseFreq + freqMod, t)
  }

  // Set gain/volume low to prevent user hearing loud beeps
  gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime)
  
  // Connect and start
  oscillator.connect(gainNode)
  gainNode.connect(audioCtx.destination)
  oscillator.start()
  isPlaying.value = true
}

const stopSound = () => {
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

  // Set canvas size
  canvas.width = canvas.parentElement.clientWidth
  canvas.height = canvas.parentElement.clientHeight

  let phase = 0

  const draw = () => {
    if (!canvasCtx || !selectedSample.value) return

    const width = canvas.width
    const height = canvas.height

    // Background fill
    canvasCtx.fillStyle = '#090d10'
    canvasCtx.fillRect(0, 0, width, height)

    // Grid lines
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

    // Oscilloscope wave trace
    canvasCtx.beginPath()
    canvasCtx.lineWidth = 2
    canvasCtx.strokeStyle = selectedSample.value.severity === 'Normal'
      ? '#10b981'
      : (selectedSample.value.severity === 'Warning' ? '#f59e0b' : '#ef4444')

    // Control parameters based on selected sound profile
    const amp = isPlaying.value ? 45 : 8
    const freq = selectedSample.value.id === 'thermal' ? 0.08 : (selectedSample.value.id === 'healthy' ? 0.02 : 0.04)

    for (let x = 0; x < width; x++) {
      let y = height / 2
      if (isPlaying.value) {
        if (selectedSample.value.id === 'healthy') {
          // Normal: Smooth sine waves
          y += Math.sin(x * freq + phase) * amp * (0.8 + 0.2 * Math.sin(phase * 0.5))
        } else if (selectedSample.value.id === 'thermal') {
          // Thermal: High-pitch rapid chirp pulses
          y += Math.sin(x * freq + phase) * amp * (Math.sin(x * 0.005 + phase * 0.2) > 0.4 ? 1 : 0.1)
        } else if (selectedSample.value.id === 'feeding') {
          // Feeding: Rhythmic envelope bursts
          y += Math.sin(x * freq + phase) * amp * Math.cos(x * 0.01 + phase * 0.05)
        } else {
          // Respiratory: Raspy sawtooth noise bursts
          const noise = (Math.random() - 0.5) * 12
          const sawtooth = ((x * freq + phase) % 2) - 1
          y += (sawtooth * amp) + noise
        }
      } else {
        // Idle: flat gentle thermal noise
        y += (Math.random() - 0.5) * 2 + Math.sin(x * 0.01 + phase) * 2
      }

      if (x === 0) {
        canvasCtx.moveTo(x, y)
      } else {
        canvasCtx.lineTo(x, y)
      }
    }

    canvasCtx.stroke()

    // Shift wave phase
    phase += isPlaying.value ? 0.25 : 0.03
    animationFrameId = requestAnimationFrame(draw)
  }

  draw()
}

// ── Formatting ──────────────────────────
const getSeverityTextClass = (sev) => {
  if (sev === 'Normal') return 'text-emerald-500'
  if (sev === 'Warning') return 'text-amber-500'
  return 'text-red-500'
}

onUnmounted(() => {
  stopSound()
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})
</script>
