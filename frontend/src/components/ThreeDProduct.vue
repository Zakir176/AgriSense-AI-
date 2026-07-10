<template>
  <div class="relative w-full aspect-square md:aspect-[4/3] flex flex-col justify-between bg-gradient-to-b from-gray-50/50 to-white/50 dark:from-darkbg-50/20 dark:to-darkbg-100/10 border border-gray-250/50 dark:border-gray-800/40 rounded-3xl p-6 shadow-xl overflow-hidden select-none group">
    <!-- Grid overlay background for tech design -->
    <div class="absolute inset-0 bg-[linear-gradient(to_right,#e5e7eb_1px,transparent_1px),linear-gradient(to_bottom,#e5e7eb_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#1b201d_1px,transparent_1px),linear-gradient(to_bottom,#1b201d_1px,transparent_1px)] [background-size:24px_24px] opacity-[0.15] -z-10"></div>
    
    <!-- Top info bar -->
    <div class="relative z-10 flex items-center justify-between">
      <div>
        <div class="flex items-center space-x-2">
          <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-[10px] font-black uppercase tracking-wider text-gray-450 dark:text-gray-500">AgriSense Edge Node</span>
        </div>
        <h4 class="text-sm font-extrabold text-gray-900 dark:text-white mt-1">Model: SH-300 v4</h4>
      </div>
      <div class="flex space-x-2">
        <button 
          @click="toggleAutoRotate"
          class="p-1.5 rounded-lg border border-gray-200 dark:border-gray-805 bg-white/90 dark:bg-darkbg-50/90 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition"
          title="Toggle Auto Rotate"
        >
          <span class="material-icons-outlined text-sm block">{{ autoRotate ? 'pause' : 'play_arrow' }}</span>
        </button>
        <button 
          @click="resetView"
          class="p-1.5 rounded-lg border border-gray-200 dark:border-gray-805 bg-white/90 dark:bg-darkbg-50/90 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition"
          title="Reset View"
        >
          <span class="material-icons-outlined text-sm block">refresh</span>
        </button>
      </div>
    </div>

    <!-- Main Canvas Viewport -->
    <div class="relative flex-1 flex items-center justify-center cursor-grab active:cursor-grabbing w-full min-h-[220px]" ref="container">
      <canvas ref="canvas" class="w-full h-full max-h-[380px] max-w-[500px]"></canvas>

      <!-- Floating Holographic HTML Labels -->
      <div 
        v-for="(label, idx) in projectedLabels" 
        :key="idx"
        class="absolute pointer-events-none transition-all duration-75 select-none"
        :style="{
          left: label.x + 'px',
          top: label.y + 'px',
          opacity: label.visible ? 1 : 0,
          transform: 'translate(-50%, -100%)'
        }"
      >
        <div class="bg-white/90 dark:bg-darkbg-50/90 backdrop-blur-md border border-primary-500/25 dark:border-primary-400/20 px-2.5 py-1.5 rounded-xl shadow-lg flex flex-col items-start min-w-[120px] max-w-[160px] translate-y-[-16px]">
          <span class="text-[8px] font-black uppercase tracking-wider text-primary-600 dark:text-primary-400">{{ label.category }}</span>
          <span class="text-[10px] font-extrabold text-gray-850 dark:text-gray-100 mt-0.5 leading-none">{{ label.title }}</span>
          <!-- Dynamic Telemetry reading if present -->
          <span v-if="label.dynamicVal" class="text-[9px] font-mono text-emerald-600 dark:text-emerald-450 mt-1 font-bold">{{ label.dynamicVal }}</span>
          
          <!-- Connector point line -->
          <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-[16px] w-[1px] h-[16px] bg-gradient-to-b from-primary-500/30 to-transparent"></div>
          <div class="absolute bottom-[-16px] left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-primary-500 border border-white dark:border-darkbg-50"></div>
        </div>
      </div>
    </div>

    <!-- Bottom Status Stats Bar -->
    <div class="relative z-10 grid grid-cols-3 gap-2.5 pt-3 border-t border-gray-200/60 dark:border-gray-800/80 bg-white/40 dark:bg-[#121614]/40 backdrop-blur-xs rounded-2xl p-3">
      <div class="text-left">
        <p class="text-[8px] uppercase tracking-wider font-bold text-gray-400 dark:text-gray-500">Power Input</p>
        <p class="text-[11px] font-black text-gray-850 dark:text-gray-250 mt-0.5 flex items-center gap-1">
          <span class="material-icons-outlined text-xs text-amber-500">wb_sunny</span>
          <span>10.8 W (Solar)</span>
        </p>
      </div>
      <div class="text-left">
        <p class="text-[8px] uppercase tracking-wider font-bold text-gray-400 dark:text-gray-500">Battery Level</p>
        <p class="text-[11px] font-black text-gray-850 dark:text-gray-250 mt-0.5 flex items-center gap-1">
          <span class="material-icons-outlined text-xs text-emerald-500">battery_charging_full</span>
          <span>94.2%</span>
        </p>
      </div>
      <div class="text-left">
        <p class="text-[8px] uppercase tracking-wider font-bold text-gray-400 dark:text-gray-500">Sensor Signal</p>
        <p class="text-[11px] font-black text-emerald-600 dark:text-emerald-450 mt-0.5 flex items-center gap-1">
          <span class="material-icons-outlined text-xs">rss_feed</span>
          <span>-68 dBm (LoRa)</span>
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

const canvas = ref(null)
const container = ref(null)
const autoRotate = ref(true)

// Rotation angles in radians
const angleX = ref(-0.4) // Pitch
const angleY = ref(0.6)  // Yaw

// Interaction variables
let isDragging = false
let previousMouseX = 0
let previousMouseY = 0
let velocityX = 0
let velocityY = 0
let animationFrameId = null

const toggleAutoRotate = () => {
  autoRotate.value = !autoRotate.value
}

const resetView = () => {
  angleX.value = -0.4
  angleY.value = 0.6
  velocityX = 0
  velocityY = 0
}

// 3D Model Coordinate System & Projection
// local origin (0,0,0) is centered inside the hub box.
// Chassis: a box (cube).
const chassisWidth = 70
const chassisHeight = 45
const chassisDepth = 70

const chassisVertices = [
  { x: -chassisWidth/2, y: -chassisHeight/2, z: -chassisDepth/2 },
  { x:  chassisWidth/2, y: -chassisHeight/2, z: -chassisDepth/2 },
  { x:  chassisWidth/2, y:  chassisHeight/2, z: -chassisDepth/2 },
  { x: -chassisWidth/2, y:  chassisHeight/2, z: -chassisDepth/2 },
  { x: -chassisWidth/2, y: -chassisHeight/2, z:  chassisDepth/2 },
  { x:  chassisWidth/2, y: -chassisHeight/2, z:  chassisDepth/2 },
  { x:  chassisWidth/2, y:  chassisHeight/2, z:  chassisDepth/2 },
  { x: -chassisWidth/2, y:  chassisHeight/2, z:  chassisDepth/2 },
]

// Index of vertices forming each of the 6 faces of the chassis
const chassisFaces = [
  { indices: [0, 1, 2, 3], normal: { x: 0, y: 0, z: -1 }, name: 'back' },
  { indices: [1, 5, 6, 2], normal: { x: 1, y: 0, z: 0 }, name: 'right' },
  { indices: [4, 0, 3, 7], normal: { x: -1, y: 0, z: 0 }, name: 'left' },
  { indices: [4, 5, 6, 7], normal: { x: 0, y: 0, z: 1 }, name: 'front' },
  { indices: [4, 5, 1, 0], normal: { x: 0, y: -1, z: 0 }, name: 'top' },
  { indices: [3, 2, 6, 7], normal: { x: 0, y: 1, z: 0 }, name: 'bottom' }
]

// Solar Panel: thin panel on top, tilted.
const panelWidth = 76
const panelHeight = 4
const panelDepth = 48
const panelYOffset = -chassisHeight/2 - 12
const panelTilt = 0.35 // rotation around X axis for panel

const localPanelVertices = [
  { x: -panelWidth/2, y: -panelHeight/2, z: -panelDepth/2 },
  { x:  panelWidth/2, y: -panelHeight/2, z: -panelDepth/2 },
  { x:  panelWidth/2, y:  panelHeight/2, z: -panelDepth/2 },
  { x: -panelWidth/2, y:  panelHeight/2, z: -panelDepth/2 },
  { x: -panelWidth/2, y: -panelHeight/2, z:  panelDepth/2 },
  { x:  panelWidth/2, y: -panelHeight/2, z:  panelDepth/2 },
  { x:  panelWidth/2, y:  panelHeight/2, z:  panelDepth/2 },
  { x: -panelWidth/2, y:  panelHeight/2, z:  panelDepth/2 },
]

// Tilt vertices and offset them to place panel on top
const solarPanelVertices = localPanelVertices.map(v => {
  // Rotate around X axis
  const cosT = Math.cos(panelTilt)
  const sinT = Math.sin(panelTilt)
  const ry = v.y * cosT - v.z * sinT
  const rz = v.y * sinT + v.z * cosT
  return {
    x: v.x,
    y: ry + panelYOffset,
    z: rz - 6 // offset slightly back
  }
})

const solarFaces = [
  { indices: [0, 1, 2, 3], normal: { x: 0, y: -Math.sin(panelTilt), z: -Math.cos(panelTilt) } },
  { indices: [1, 5, 6, 2], normal: { x: 1, y: 0, z: 0 } },
  { indices: [4, 0, 3, 7], normal: { x: -1, y: 0, z: 0 } },
  { indices: [4, 5, 6, 7], normal: { x: 0, y: Math.sin(panelTilt), z: Math.cos(panelTilt) } },
  { indices: [4, 5, 1, 0], normal: { x: 0, y: -1, z: 0 } },
  { indices: [3, 2, 6, 7], normal: { x: 0, y: 1, z: 0 } }
]

// Antenna: a cylinder/line from center top to top
const antennaBase = { x: -20, y: -chassisHeight/2, z: -15 }
const antennaTip = { x: -20, y: -105, z: -15 }

// LED positions on the front face (Z = chassisDepth/2 + 0.5)
const leds = [
  { x: -20, y: 10, z: chassisDepth/2 + 1, color: 'power', hz: 0 },   // Solid green
  { x: 0, y: 10, z: chassisDepth/2 + 1, color: 'sync', hz: 1.5 },     // Blinking Blue
  { x: 20, y: 10, z: chassisDepth/2 + 1, color: 'alert', hz: 0.5 }   // Slow Blinking Amber
]

// Signal ripples animation state
const signalRipples = ref([
  { radius: 0, opacity: 1 },
  { radius: 25, opacity: 0.6 },
  { radius: 50, opacity: 0.2 }
])

// Projected HTML labels overlay
const projectedLabels = ref([
  {
    localPos: { x: -20, y: -105, z: -15 }, // Antenna tip
    category: 'RF Node',
    title: 'Dual-Band LoRa Antenna',
    dynamicVal: '915 MHz · Active',
    x: 0, y: 0, visible: false
  },
  {
    localPos: { x: 25, y: -10, z: chassisDepth/2 }, // Front right
    category: 'Edge Compute',
    title: 'Local YOLOv8 Co-processor',
    dynamicVal: 'Coop Counting Enabled',
    x: 0, y: 0, visible: false
  },
  {
    localPos: { x: 0, y: chassisHeight/2, z: 0 }, // Bottom center
    category: 'Energy',
    title: 'Silo Load Cells Input',
    dynamicVal: '0.00 kg - 10,000.00 kg',
    x: 0, y: 0, visible: false
  }
])

// 3D Projection functions
const rotateX = (v, phi) => {
  const cosP = Math.cos(phi)
  const sinP = Math.sin(phi)
  return {
    x: v.x,
    y: v.y * cosP - v.z * sinP,
    z: v.y * sinP + v.z * cosP
  }
}

const rotateY = (v, theta) => {
  const cosT = Math.cos(theta)
  const sinT = Math.sin(theta)
  return {
    x: v.x * cosT + v.z * sinT,
    y: v.y,
    z: -v.x * sinT + v.z * cosT
  }
}

const project = (v, cx, cy, d) => {
  const scale = d / (d + v.z)
  return {
    x: cx + v.x * scale,
    y: cy + v.y * scale,
    z: v.z,
    scale
  }
}

// Lighting calculation (flat shading)
const computeLighting = (normal, rotatedNormal, isDarkTheme) => {
  // Light source from top-left-front in camera space
  const lightDir = { x: -0.4, y: -0.7, z: -0.6 }
  // Normalize light dir
  const length = Math.sqrt(lightDir.x*lightDir.x + lightDir.y*lightDir.y + lightDir.z*lightDir.z)
  const lNorm = { x: lightDir.x/length, y: lightDir.y/length, z: lightDir.z/length }

  // Dot product
  const dot = -(rotatedNormal.x * lNorm.x + rotatedNormal.y * lNorm.y + rotatedNormal.z * lNorm.z)
  const intensity = Math.max(0.15, Math.min(1.0, dot))

  // Base colors
  if (isDarkTheme) {
    // Shading for dark mode (metallic dark charcoal chassis)
    const baseR = 30, baseG = 38, baseB = 34
    const r = Math.round(baseR + intensity * 60)
    const g = Math.round(baseG + intensity * 85) // higher green response
    const b = Math.round(baseB + intensity * 65)
    return `rgb(${r}, ${g}, ${b})`
  } else {
    // Shading for light mode (cool white/light grey plastic chassis)
    const baseR = 210, baseG = 220, baseB = 215
    const r = Math.round(baseR + intensity * 40)
    const g = Math.round(baseG + intensity * 35)
    const b = Math.round(baseB + intensity * 38)
    return `rgb(${r}, ${g}, ${b})`
  }
}

// Main Render Loop
const render = () => {
  const canvasEl = canvas.value
  if (!canvasEl) return

  const ctx = canvasEl.getContext('2d')
  if (!ctx) return

  const isDarkTheme = props.isDark

  // Clear background
  ctx.clearRect(0, 0, canvasEl.width, canvasEl.height)

  const cx = canvasEl.width / 2
  const cy = canvasEl.height / 2 + 15
  const d = 320 // Camera distance

  // Update automatic rotation if enabled
  if (autoRotate.value && !isDragging) {
    angleY.value += 0.007
  }

  // Handle momentum
  if (!isDragging) {
    angleX.value += velocityX
    angleY.value += velocityY
    velocityX *= 0.92
    velocityY *= 0.92
    
    // Clamp Pitch (X Rotation) to prevent flipping upside down
    angleX.value = Math.max(-0.9, Math.min(0.2, angleX.value))
  }

  // 1. Rotate and project chassis vertices
  const rotChassisVertices = chassisVertices.map(v => {
    let rv = rotateY(v, angleY.value)
    rv = rotateX(rv, angleX.value)
    return rv
  })

  const projChassisVertices = rotChassisVertices.map(v => project(v, cx, cy, d))

  // Rotate chassis normal vectors for backface culling & flat shading
  const rotatedChassisNormals = chassisFaces.map(f => {
    let rn = rotateY(f.normal, angleY.value)
    rn = rotateX(rn, angleX.value)
    return rn
  })

  // 2. Rotate and project Solar Panel vertices
  const rotSolarVertices = solarPanelVertices.map(v => {
    let rv = rotateY(v, angleY.value)
    rv = rotateX(rv, angleX.value)
    return rv
  })
  const projSolarVertices = rotSolarVertices.map(v => project(v, cx, cy, d))

  const rotatedSolarNormals = solarFaces.map(f => {
    let rn = rotateY(f.normal, angleY.value)
    rn = rotateX(rn, angleX.value)
    return rn
  })

  // 3. Assemble all polygons to draw (for Painter's Depth Sorting)
  const drawList = []

  // Add chassis faces to draw list
  chassisFaces.forEach((face, idx) => {
    const rotNormal = rotatedChassisNormals[idx]
    
    // Backface culling: face normal towards camera has positive Z component in this system.
    // If Z > 0, normal faces towards screen.
    if (rotNormal.z > -0.15) {
      // Calculate average Z for depth sorting
      let avgZ = 0
      face.indices.forEach(vIdx => {
        avgZ += rotChassisVertices[vIdx].z
      })
      avgZ /= 4

      // Setup colors
      const faceColor = computeLighting(face.normal, rotNormal, isDarkTheme)
      const strokeColor = isDarkTheme ? 'rgba(52, 211, 153, 0.25)' : 'rgba(45, 106, 79, 0.25)'

      drawList.push({
        type: 'polygon',
        depth: avgZ,
        points: face.indices.map(vIdx => projChassisVertices[vIdx]),
        fill: faceColor,
        stroke: strokeColor,
        lineWidth: 1.5,
        name: `chassis-${face.name}`
      })
    }
  })

  // Add solar panel faces to draw list
  solarFaces.forEach((face, idx) => {
    const rotNormal = rotatedSolarNormals[idx]
    if (rotNormal.z > -0.2) {
      let avgZ = 0
      face.indices.forEach(vIdx => {
        avgZ += rotSolarVertices[vIdx].z
      })
      avgZ /= 4

      // Solar Panel coloring (metallic bluish grid)
      let panelColor = ''
      const dot = -(rotNormal.x * -0.4 + rotNormal.y * -0.7 + rotNormal.z * -0.6)
      const intensity = Math.max(0.1, Math.min(1.0, dot))
      if (isDarkTheme) {
        panelColor = `rgb(${Math.round(15 + intensity * 25)}, ${Math.round(25 + intensity * 45)}, ${Math.round(45 + intensity * 75)})`
      } else {
        panelColor = `rgb(${Math.round(40 + intensity * 20)}, ${Math.round(55 + intensity * 25)}, ${Math.round(90 + intensity * 35)})`
      }

      const strokeColor = isDarkTheme ? '#4ade80' : '#2d6a4f'

      drawList.push({
        type: 'polygon',
        depth: avgZ,
        points: face.indices.map(vIdx => projSolarVertices[vIdx]),
        fill: panelColor,
        stroke: strokeColor,
        lineWidth: 1,
        name: 'solar-face',
        // Flag to draw solar panel cell grids
        isSolar: true,
        indices: face.indices,
        projPoints: face.indices.map(vIdx => projSolarVertices[vIdx])
      })
    }
  })

  // 4. Rotate and project Antenna
  let rotAntBase = rotateY(antennaBase, angleY.value)
  rotAntBase = rotateX(rotAntBase, angleX.value)
  const projAntBase = project(rotAntBase, cx, cy, d)

  let rotAntTip = rotateY(antennaTip, angleY.value)
  rotAntTip = rotateX(rotAntTip, angleX.value)
  const projAntTip = project(rotAntTip, cx, cy, d)

  // Add antenna line to draw list
  const antennaAvgZ = (rotAntBase.z + rotAntTip.z) / 2
  drawList.push({
    type: 'line',
    depth: antennaAvgZ,
    from: projAntBase,
    to: projAntTip,
    color: isDarkTheme ? '#10b981' : '#1b4f3b',
    lineWidth: 3.5
  })

  // Add a metallic silver cap at the top of the antenna
  drawList.push({
    type: 'circle',
    depth: rotAntTip.z - 2,
    pos: projAntTip,
    radius: 4.5,
    fill: isDarkTheme ? '#f3f4f6' : '#4b5563',
    stroke: isDarkTheme ? '#10b981' : '#1b4f3b',
    lineWidth: 1
  })

  // 5. Blinking LEDs on Front Panel
  leds.forEach(led => {
    let rotLed = rotateY(led, angleY.value)
    rotLed = rotateX(rotLed, angleX.value)
    
    const frontNormal = rotatedChassisNormals[3]
    if (frontNormal.z > 0.05) {
      const projLed = project(rotLed, cx, cy, d)
      
      const timeMs = Date.now()
      let glow = true
      if (led.hz > 0) {
        const period = 1000 / led.hz
        glow = (timeMs % period) < (period / 2)
      }

      let ledColor = ''
      let ledGlowColor = ''
      if (led.color === 'power') {
        ledColor = '#10b981'
        ledGlowColor = 'rgba(16, 185, 129, 0.45)'
      } else if (led.color === 'sync') {
        ledColor = '#3b82f6'
        ledGlowColor = 'rgba(59, 130, 246, 0.45)'
      } else if (led.color === 'alert') {
        ledColor = '#f59e0b'
        ledGlowColor = 'rgba(245, 158, 11, 0.45)'
      }

      drawList.push({
        type: 'led',
        depth: rotLed.z - 1,
        pos: projLed,
        radius: 3,
        glow,
        color: ledColor,
        glowColor: ledGlowColor
      })
    }
  })

  // 6. Draw LoRa wave signal ripples from Antenna Tip
  const timeSec = Date.now() / 1000
  signalRipples.value.forEach((ripple, idx) => {
    ripple.radius = ((timeSec * 35 + idx * 25) % 75)
    ripple.opacity = Math.max(0, 1 - (ripple.radius / 75))

    const circlePoints = []
    const numPoints = 16
    for (let i = 0; i < numPoints; i++) {
      const theta = (i / numPoints) * Math.PI * 2
      const cxLocal = antennaTip.x + Math.cos(theta) * ripple.radius
      const czLocal = antennaTip.z + Math.sin(theta) * ripple.radius
      const cyLocal = antennaTip.y
      
      let rotP = rotateY({ x: cxLocal, y: cyLocal, z: czLocal }, angleY.value)
      rotP = rotateX(rotP, angleX.value)
      circlePoints.push(project(rotP, cx, cy, d))
    }

    drawList.push({
      type: 'ring',
      depth: rotAntTip.z + 10,
      points: circlePoints,
      color: isDarkTheme ? `rgba(52, 211, 153, ${ripple.opacity * 0.35})` : `rgba(40, 145, 108, ${ripple.opacity * 0.3})`,
      lineWidth: 1.5
    })
  })

  // 7. Sort all draw items by depth
  drawList.sort((a, b) => b.depth - a.depth)

  // 8. Execute Drawing Instructions
  drawList.forEach(item => {
    if (item.type === 'polygon') {
      ctx.beginPath()
      ctx.moveTo(item.points[0].x, item.points[0].y)
      for (let i = 1; i < item.points.length; i++) {
        ctx.lineTo(item.points[i].x, item.points[i].y)
      }
      ctx.closePath()
      ctx.fillStyle = item.fill
      ctx.fill()
      ctx.strokeStyle = item.stroke
      ctx.lineWidth = item.lineWidth
      ctx.stroke()

      if (item.isSolar) {
        ctx.save()
        ctx.beginPath()
        ctx.moveTo(item.points[0].x, item.points[0].y)
        for (let i = 1; i < item.points.length; i++) {
          ctx.lineTo(item.points[i].x, item.points[i].y)
        }
        ctx.closePath()
        ctx.clip()

        ctx.strokeStyle = isDarkTheme ? 'rgba(52, 211, 153, 0.4)' : 'rgba(255, 255, 255, 0.4)'
        ctx.lineWidth = 0.8
        const steps = 4
        for (let i = 1; i < steps; i++) {
          const t = i / steps
          const pLeftX = item.points[0].x * (1 - t) + item.points[3].x * t
          const pLeftY = item.points[0].y * (1 - t) + item.points[3].y * t
          const pRightX = item.points[1].x * (1 - t) + item.points[2].x * t
          const pRightY = item.points[1].y * (1 - t) + item.points[2].y * t

          ctx.beginPath()
          ctx.moveTo(pLeftX, pLeftY)
          ctx.lineTo(pRightX, pRightY)
          ctx.stroke()

          const pTopX = item.points[0].x * (1 - t) + item.points[1].x * t
          const pTopY = item.points[0].y * (1 - t) + item.points[1].y * t
          const pBotX = item.points[3].x * (1 - t) + item.points[2].x * t
          const pBotY = item.points[3].y * (1 - t) + item.points[2].y * t

          ctx.beginPath()
          ctx.moveTo(pTopX, pTopY)
          ctx.lineTo(pBotX, pBotY)
          ctx.stroke()
        }
        ctx.restore()
      }
    } else if (item.type === 'line') {
      ctx.beginPath()
      ctx.moveTo(item.from.x, item.from.y)
      ctx.lineTo(item.to.x, item.to.y)
      ctx.strokeStyle = item.color
      ctx.lineWidth = item.lineWidth
      ctx.lineCap = 'round'
      ctx.stroke()
    } else if (item.type === 'circle') {
      ctx.beginPath()
      ctx.arc(item.pos.x, item.pos.y, item.radius, 0, Math.PI * 2)
      ctx.fillStyle = item.fill
      ctx.fill()
      ctx.strokeStyle = item.stroke
      ctx.lineWidth = item.lineWidth
      ctx.stroke()
    } else if (item.type === 'led') {
      ctx.beginPath()
      ctx.arc(item.pos.x, item.pos.y, item.radius, 0, Math.PI * 2)
      ctx.fillStyle = item.glow ? item.color : '#4b5563'
      ctx.fill()
      
      if (item.glow) {
        ctx.beginPath()
        ctx.arc(item.pos.x, item.pos.y, item.radius + 3, 0, Math.PI * 2)
        ctx.fillStyle = item.glowColor
        ctx.fill()
      }
    } else if (item.type === 'ring') {
      ctx.beginPath()
      ctx.moveTo(item.points[0].x, item.points[0].y)
      for (let i = 1; i < item.points.length; i++) {
        ctx.lineTo(item.points[i].x, item.points[i].y)
      }
      ctx.closePath()
      ctx.strokeStyle = item.color
      ctx.lineWidth = item.lineWidth
      ctx.stroke()
    }
  })

  updateHTMLOverlay(cx, cy, d)

  animationFrameId = requestAnimationFrame(render)
}

const updateHTMLOverlay = (cx, cy, d) => {
  const canvasEl = canvas.value
  const containerEl = container.value
  if (!canvasEl || !containerEl) return

  const rect = canvasEl.getBoundingClientRect()
  const contRect = containerEl.getBoundingClientRect()

  const scaleX = rect.width / canvasEl.width
  const scaleY = rect.height / canvasEl.height

  projectedLabels.value.forEach(label => {
    let rv = rotateY(label.localPos, angleY.value)
    rv = rotateX(rv, angleX.value)

    const proj = project(rv, canvasEl.width / 2, canvasEl.height / 2 + 15, d)

    const domX = rect.left - contRect.left + proj.x * scaleX
    const domY = rect.top - contRect.top + proj.y * scaleY

    label.x = domX
    label.y = domY
    label.visible = rv.z < 60
  })
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

const onMouseDown = (e) => {
  isDragging = true
  previousMouseX = e.clientX
  previousMouseY = e.clientY
  velocityX = 0
  velocityY = 0
}

const onMouseMove = (e) => {
  if (!isDragging) return
  
  const deltaX = e.clientX - previousMouseX
  const deltaY = e.clientY - previousMouseY

  const rotSpeed = 0.006
  angleY.value += deltaX * rotSpeed
  angleX.value += deltaY * rotSpeed
  angleX.value = Math.max(-0.9, Math.min(0.2, angleX.value))

  velocityY = deltaX * rotSpeed * 0.4
  velocityX = deltaY * rotSpeed * 0.4

  previousMouseX = e.clientX
  previousMouseY = e.clientY
}

const onMouseUp = () => {
  isDragging = false
}

const onTouchStart = (e) => {
  if (e.touches.length !== 1) return
  isDragging = true
  previousMouseX = e.touches[0].clientX
  previousMouseY = e.touches[0].clientY
  velocityX = 0
  velocityY = 0
}

const onTouchMove = (e) => {
  if (!isDragging || e.touches.length !== 1) return
  
  const deltaX = e.touches[0].clientX - previousMouseX
  const deltaY = e.touches[0].clientY - previousMouseY

  const rotSpeed = 0.008
  angleY.value += deltaX * rotSpeed
  angleX.value += deltaY * rotSpeed
  angleX.value = Math.max(-0.9, Math.min(0.2, angleX.value))

  velocityY = deltaX * rotSpeed * 0.4
  velocityX = deltaY * rotSpeed * 0.4

  previousMouseX = e.touches[0].clientX
  previousMouseY = e.touches[0].clientY
}

onMounted(() => {
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)

  const el = container.value
  if (el) {
    el.addEventListener('mousedown', onMouseDown)
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)
    
    el.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchmove', onTouchMove, { passive: true })
    window.addEventListener('touchend', onMouseUp)
  }

  render()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrameId)
  window.removeEventListener('resize', resizeCanvas)

  const el = container.value
  if (el) {
    el.removeEventListener('mousedown', onMouseDown)
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('mouseup', onMouseUp)
    
    el.removeEventListener('touchstart', onTouchStart)
    window.removeEventListener('touchmove', onTouchMove)
    window.removeEventListener('touchend', onMouseUp)
  }
})
</script>

<style scoped>
canvas {
  display: block;
}
</style>
