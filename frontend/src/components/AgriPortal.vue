<template>
  <div 
    class="relative w-full overflow-hidden rounded-3xl p-8 shadow-2xl border text-center min-h-[360px] flex flex-col justify-between items-center group transition-colors duration-200"
    :class="[
      isDark 
        ? 'bg-gradient-to-br from-gray-900 via-[#0b100d] to-black border-emerald-950/40 text-white' 
        : 'bg-gradient-to-br from-emerald-50/45 via-white to-emerald-50/20 border-emerald-200/50 text-gray-850'
    ]"
  >
    <!-- Starfield/Grid background overlay -->
    <div 
      class="absolute inset-0 [background-size:20px_20px] pointer-events-none -z-10 transition-opacity"
      :class="[
        isDark 
          ? 'bg-[radial-gradient(#162a1f_1px,transparent_1px)] opacity-40' 
          : 'bg-[radial-gradient(#d1e7dd_1.2px,transparent_1.2px)] opacity-60'
      ]"
    ></div>
    
    <div class="relative z-10 space-y-2 max-w-md">
      <div 
        class="inline-flex items-center space-x-2 border px-3 py-1 rounded-full transition-colors"
        :class="[
          isDark 
            ? 'bg-emerald-950/60 border-emerald-500/30 text-emerald-450' 
            : 'bg-emerald-50 border-emerald-200/60 text-primary-700'
        ]"
      >
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-450 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-550"></span>
        </span>
        <span class="text-[9px] font-black uppercase tracking-wider">Quantum Data Pipeline</span>
      </div>
      <h3 class="text-xl sm:text-2xl font-black tracking-tight leading-none mt-2" :class="isDark ? 'text-white' : 'text-gray-900'">
        The AgriSense Sync Portal
      </h3>
      <p class="text-xs max-w-sm mx-auto leading-relaxed" :class="isDark ? 'text-emerald-500/80' : 'text-primary-700/80'">
        Interactive synchronization gateway. Move your cursor near the anomaly core to influence the gravity well of telemetry packet streams.
      </p>
    </div>

    <!-- Canvas Container -->
    <div class="relative w-full flex-1 flex items-center justify-center min-h-[220px]" ref="container">
      <canvas ref="canvas" class="w-full h-full max-h-[300px] max-w-[450px] pointer-events-none"></canvas>
      
      <!-- Interactive Core trigger button -->
      <button 
        @click="$emit('portal-click')"
        class="absolute z-20 group/btn h-20 w-20 rounded-full flex flex-col items-center justify-center transition-all duration-300 transform hover:scale-105 active:scale-95 text-center"
        :class="[
          isDark 
            ? 'bg-black/60 hover:bg-emerald-950/50 border-emerald-500/40 hover:border-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_35px_rgba(52,211,153,0.5)]' 
            : 'bg-white/85 hover:bg-emerald-50/50 border-emerald-300 hover:border-emerald-500 shadow-[0_0_15px_rgba(45,106,79,0.1)] hover:shadow-[0_0_25px_rgba(45,106,79,0.25)]'
        ]"
      >
        <span class="material-icons-outlined text-2xl animate-pulse" :class="isDark ? 'text-emerald-450' : 'text-primary-650'">vpn_key</span>
        <span class="text-[8px] font-bold uppercase tracking-widest mt-1" :class="isDark ? 'text-emerald-500' : 'text-primary-750'">Connect</span>
      </button>
    </div>

    <!-- Bottom Gateway Telemetry Stats -->
    <div 
      class="relative z-10 grid grid-cols-2 gap-8 text-left w-full border-t pt-4 px-4 rounded-2xl p-3 max-w-md transition-colors"
      :class="[
        isDark 
          ? 'border-emerald-950/60 bg-black/30' 
          : 'border-emerald-100 bg-emerald-50/20'
      ]"
    >
      <div>
        <p class="text-[8px] uppercase tracking-wider font-extrabold" :class="isDark ? 'text-emerald-600/80' : 'text-primary-650'">Packet Sync Stream</p>
        <p class="text-xs font-mono font-bold" :class="isDark ? 'text-white' : 'text-gray-900'">1,248 packets/sec</p>
      </div>
      <div class="text-right">
        <p class="text-[8px] uppercase tracking-wider font-extrabold" :class="isDark ? 'text-emerald-600/80' : 'text-primary-650'">Gateway Status</p>
        <p class="text-xs font-mono font-bold mt-0.5 flex items-center justify-end gap-1" :class="isDark ? 'text-emerald-455' : 'text-primary-650'">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
          <span>Online - Ready</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  isDark: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['portal-click'])

const canvas = ref(null)
const container = ref(null)

let animationFrameId = null
let particles = []
const maxParticles = 160

// Mouse status relative to canvas center
let targetMouseX = 0
let targetMouseY = 0
let currentMouseX = 0
let currentMouseY = 0

// Particle class definition
class PacketParticle {
  constructor(canvasWidth, canvasHeight) {
    this.reset(canvasWidth, canvasHeight)
    // Randomize initial age so they don't start at the same location
    this.r = Math.random() * Math.max(canvasWidth, canvasHeight) * 0.6 + 15
    this.theta = Math.random() * Math.PI * 2
  }

  reset(canvasWidth, canvasHeight) {
    this.theta = 0
    this.r = Math.random() * Math.max(canvasWidth, canvasHeight) * 0.6 + 15
    this.speed = Math.random() * 0.02 + 0.005
    
    // Closer to center = smaller and faster
    this.size = Math.random() * 1.8 + 0.6
    
    // Choose theme-tailored green/teal colors based on isDark prop
    let colors = []
    if (props.isDark) {
      colors = [
        'rgba(52, 211, 153, ', // Bright mint green
        'rgba(34, 211, 238, ', // Neon Cyan
        'rgba(74, 222, 128, ', // Neon green
        'rgba(16, 185, 129, '  // Emerald
      ]
    } else {
      colors = [
        'rgba(45, 106, 79, ',  // Deep forest green
        'rgba(64, 145, 108, ', // Rich green
        'rgba(2, 128, 144, ',  // Ocean blue-green
        'rgba(33, 158, 188, '  // Tech blue
      ]
    }
    this.baseColor = colors[Math.floor(Math.random() * colors.length)]
    
    // 3D Tilt perspective noise offset
    this.zOffset = (Math.random() - 0.5) * 15
  }

  update(canvasWidth, canvasHeight, gravityX, gravityY) {
    const distToCenter = this.r
    const angularSpeed = this.speed * (80 / Math.max(10, distToCenter)) + 0.002
    
    this.theta += angularSpeed
    
    // Spiraling inwards slowly
    this.r -= 0.35 + (80 / Math.max(15, distToCenter)) * 0.1
    
    if (this.r <= 6) {
      this.reset(canvasWidth, canvasHeight)
      this.r = Math.random() * 80 + 100
    }
  }

  draw(ctx, cx, cy) {
    const tiltFactor = 0.45
    
    const localX = this.r * Math.cos(this.theta)
    const localY = this.r * Math.sin(this.theta) * tiltFactor + this.zOffset
    
    const depthZ = this.r * Math.sin(this.theta) * (1 - tiltFactor)
    const scale = 250 / (250 + depthZ)
    
    const x = cx + localX * scale
    const y = cy + localY * scale

    const alpha = Math.min(1.0, (this.r / 20) * scale * 0.9)
    
    ctx.beginPath()
    ctx.arc(x, y, this.size * scale, 0, Math.PI * 2)
    ctx.fillStyle = `${this.baseColor}${alpha})`
    ctx.fill()
    
    if (this.size > 1.8 && depthZ < 0) {
      ctx.beginPath()
      ctx.arc(x, y, this.size * scale * 2.5, 0, Math.PI * 2)
      ctx.fillStyle = `${this.baseColor}${alpha * 0.2})`
      ctx.fill()
    }
  }
}

const render = () => {
  const canvasEl = canvas.value
  if (!canvasEl) return

  const ctx = canvasEl.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvasEl.width, canvasEl.height)

  const cx = canvasEl.width / 2
  const cy = canvasEl.height / 2

  currentMouseX += (targetMouseX - currentMouseX) * 0.08
  currentMouseY += (targetMouseY - currentMouseY) * 0.08

  const coreX = cx + currentMouseX
  const coreY = cy + currentMouseY
  
  // Radial gradient core
  const gradient = ctx.createRadialGradient(coreX, coreY, 2, coreX, coreY, 65)
  if (props.isDark) {
    gradient.addColorStop(0, 'rgba(52, 211, 153, 0.95)')
    gradient.addColorStop(0.2, 'rgba(16, 185, 129, 0.6)')
    gradient.addColorStop(0.5, 'rgba(6, 182, 212, 0.25)')
    gradient.addColorStop(1, 'rgba(5, 150, 105, 0)')
  } else {
    gradient.addColorStop(0, 'rgba(45, 106, 79, 0.75)')
    gradient.addColorStop(0.3, 'rgba(82, 183, 136, 0.45)')
    gradient.addColorStop(0.6, 'rgba(33, 158, 188, 0.18)')
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
  }

  ctx.beginPath()
  ctx.arc(coreX, coreY, 65, 0, Math.PI * 2)
  ctx.fillStyle = gradient
  ctx.fill()

  // Draw core ring border
  ctx.beginPath()
  ctx.ellipse(coreX, coreY, 15, 7, 0, 0, Math.PI * 2)
  ctx.strokeStyle = props.isDark ? 'rgba(52, 211, 153, 0.4)' : 'rgba(45, 106, 79, 0.45)'
  ctx.lineWidth = 1
  ctx.stroke()

  // Draw particles
  particles.forEach(p => {
    p.update(canvasEl.width, canvasEl.height, currentMouseX, currentMouseY)
    p.draw(ctx, coreX, coreY)
  })

  // Draw orbit lanes
  ctx.save()
  ctx.strokeStyle = props.isDark ? 'rgba(16, 185, 129, 0.08)' : 'rgba(45, 106, 79, 0.08)'
  ctx.lineWidth = 0.8
  const orbits = [45, 90, 140, 200]
  orbits.forEach(radius => {
    ctx.beginPath()
    ctx.ellipse(coreX, coreY, radius, radius * 0.45, 0, 0, Math.PI * 2)
    ctx.stroke()
  })
  ctx.restore()

  animationFrameId = requestAnimationFrame(render)
}

const resizeCanvas = () => {
  const canvasEl = canvas.value
  if (!canvasEl) return

  const rect = canvasEl.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1

  canvasEl.width = rect.width * dpr
  canvasEl.height = rect.height * dpr

  const ctx = canvasEl.getContext('2d')
  if (ctx) {
    ctx.scale(dpr, dpr)
  }
}

const onMouseMove = (e) => {
  const containerEl = container.value
  if (!containerEl) return

  const rect = containerEl.getBoundingClientRect()
  const mouseX = e.clientX - rect.left - rect.width / 2
  const mouseY = e.clientY - rect.top - rect.height / 2

  const maxDisplacement = 40
  const dist = Math.sqrt(mouseX*mouseX + mouseY*mouseY)
  
  if (dist > maxDisplacement) {
    targetMouseX = (mouseX / dist) * maxDisplacement
    targetMouseY = (mouseY / dist) * maxDisplacement
  } else {
    targetMouseX = mouseX
    targetMouseY = mouseY
  }
}

const onMouseLeave = () => {
  targetMouseX = 0
  targetMouseY = 0
}

watch(() => props.isDark, () => {
  // Update particle colors instantly when theme changes
  const canvasEl = canvas.value
  if (canvasEl) {
    particles.forEach(p => p.reset(canvasEl.width, canvasEl.height))
  }
})

onMounted(() => {
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)

  const el = container.value
  if (el) {
    window.addEventListener('mousemove', onMouseMove)
    el.addEventListener('mouseleave', onMouseLeave)
  }

  // Populate particles
  const canvasEl = canvas.value
  if (canvasEl) {
    for (let i = 0; i < maxParticles; i++) {
      particles.push(new PacketParticle(canvasEl.width, canvasEl.height))
    }
  }

  render()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', resizeCanvas)
  window.removeEventListener('mousemove', onMouseMove)
})
</script>

<style scoped>
canvas {
  display: block;
}
</style>
