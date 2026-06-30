<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">AI Visual Monitoring</h1>
          <AgriBadge variant="info" icon="psychology">YOLOv8 CV Engine</AgriBadge>
        </div>
        <p class="mt-0.5 text-sm text-gray-550 dark:text-gray-400">
          Upload poultry house footage to analyze density distribution, estimate counts, and profile movement anomalies.
        </p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Replaced with custom AgriSelect -->
        <div class="w-48">
          <AgriSelect
            v-model="selectedBatchId"
            :options="batchOptions"
            placeholder="Select cohort batch"
            @change="onBatchChange"
          />
        </div>
      </div>
    </div>

    <!-- Alert Box emphasizing Uploaded footage status -->
    <div class="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/40 rounded-xl p-4 flex items-start space-x-3 text-blue-700 dark:text-blue-300 text-xs font-semibold animate-fade-in-up delay-75">
      <span class="material-icons-outlined text-blue-600 dark:text-blue-400 shrink-0 mt-0.5">info</span>
      <div>
        <span class="font-bold">Prototype Telemetry:</span> This computer vision module processes pre-recorded footage uploads. Real-time RTSP streams are scheduled for farm integration in Phase 2.
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center animate-fade-in-up delay-100">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">photo_camera</span>
      <p class="text-sm font-bold text-gray-600 dark:text-gray-400">Select a batch above to start AI footage profiling.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Footage logs and neural network inferences are archived per batch.</p>
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- ─── Left Pane: Upload & History ─── -->
        <div class="space-y-6 lg:col-span-1 animate-fade-in-up delay-100">
          <!-- Upload Box -->
          <AgriCard>
            <h2 class="text-sm font-bold text-gray-900 dark:text-white mb-4">Analyze New Footage</h2>

            <div
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
              class="border-2 border-dashed rounded-2xl p-6 text-center transition cursor-pointer flex flex-col items-center justify-center space-y-2 group"
              :class="isDragging
                ? 'border-primary-500 bg-primary-50/10'
                : 'border-gray-200 dark:border-gray-800 hover:border-primary-500/50 hover:bg-gray-50/50 dark:hover:bg-darkbg-100/50'"
            >
              <input
                type="file"
                ref="fileInput"
                class="hidden"
                accept="video/*"
                @change="handleFileSelect"
              />
              <span class="material-icons-outlined text-3xl text-gray-400 group-hover:text-primary-500 transition">cloud_upload</span>
              <p class="text-xs font-bold text-gray-700 dark:text-gray-300">Drag & drop video file</p>
              <p class="text-[10px] text-gray-400 dark:text-gray-500">or click to browse local files (MP4, WebM)</p>
            </div>

            <!-- Upload progress / processing overlay -->
            <div v-if="processing" class="mt-4 bg-primary-50/30 dark:bg-primary-950/10 border border-primary-100 dark:border-primary-900/40 rounded-xl p-4 space-y-3">
              <div class="flex items-center gap-3">
                <span class="material-icons-outlined text-lg text-primary-650 dark:text-primary-400 animate-spin">sync</span>
                <div class="text-xs">
                  <p class="font-bold text-gray-800 dark:text-gray-200">Executing AI CV Inference</p>
                  <p class="text-gray-500 dark:text-gray-400 text-[10px]">Processing frames with YOLOv8 neural net…</p>
                </div>
              </div>
              <!-- Animated Progress Bar -->
              <AgriProgressBar
                :value="uploadProgress"
                :max="100"
                animated
                show-value
                color-class="bg-primary-500"
                height-class="h-1.5"
              />
            </div>

            <!-- Upload Error -->
            <div v-if="error" class="mt-4 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 rounded-xl p-3.5 text-xs text-status-danger font-semibold">
              {{ error }}
            </div>
          </AgriCard>

          <!-- History Catalog -->
          <AgriCard padding="none">
            <template #header>
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">Footage History</h2>
            </template>

            <div v-if="listLoading" class="p-4 space-y-2.5">
              <div v-for="n in 3" :key="n" class="h-12 bg-gray-100 dark:bg-gray-850 rounded-xl animate-pulse"></div>
            </div>

            <div v-else-if="clips.length === 0" class="py-12 text-center text-xs text-gray-400 dark:text-gray-500 px-6">
              <span class="material-icons-outlined text-2xl mb-1 text-gray-300 dark:text-gray-700 block">movie</span>
              No clips uploaded yet.
            </div>

            <div v-else class="divide-y divide-gray-100 dark:divide-gray-850 max-h-[300px] overflow-y-auto">
              <button
                v-for="c in clips"
                :key="c.id"
                @click="selectClip(c)"
                class="w-full text-left px-5 py-3 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition flex items-center justify-between text-xs"
                :class="selectedClip?.id === c.id ? 'bg-primary-50/20 dark:bg-primary-950/10 border-r-2 border-primary-500' : ''"
              >
                <div class="space-y-0.5 pr-2 truncate">
                  <p class="font-bold text-gray-900 dark:text-white truncate">{{ getFileName(c.file_url) }}</p>
                  <p class="text-[10px] text-gray-400 dark:text-gray-500">{{ formatDateTime(c.uploaded_at) }}</p>
                </div>
                <div class="text-right shrink-0">
                  <p class="font-bold text-gray-700 dark:text-gray-300">{{ c.inference_result?.bird_count_est }} birds</p>
                  <p class="text-[9px] text-gray-450 dark:text-gray-500">Score: {{ c.inference_result?.movement_score }}</p>
                </div>
              </button>
            </div>
          </AgriCard>
        </div>

        <!-- ─── Right Pane: Visual Player & CV Analytics ─── -->
        <div class="lg:col-span-2 space-y-6 animate-fade-in-up delay-200">

          <div v-if="!selectedClip" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center flex flex-col items-center justify-center h-full min-h-[400px]">
            <span class="material-icons-outlined text-5xl text-gray-300 dark:text-gray-700 mb-3 animate-pulse">analytics</span>
            <h3 class="font-bold text-gray-700 dark:text-gray-300 text-sm">Awaiting footage selection</h3>
            <p class="text-xs text-gray-450 dark:text-gray-500 mt-1 max-w-xs mx-auto">
              Upload a new poultry video clip or select a historic record from the sidebar to inspect AI predictions.
            </p>
          </div>

          <template v-else>
            <!-- Player and Overlays -->
            <AgriCard padding="none">
              <template #header>
                <div class="flex items-center gap-2">
                  <span class="material-icons-outlined text-primary-650 dark:text-primary-400">play_circle_outline</span>
                  <h3 class="text-sm font-bold text-gray-900 dark:text-white">{{ getFileName(selectedClip.file_url) }}</h3>
                </div>
                <span class="text-[10px] text-gray-400 dark:text-gray-500 font-bold uppercase tracking-wider">{{ formatDateTime(selectedClip.uploaded_at) }}</span>
              </template>

              <div class="p-5 space-y-4">
                <!-- HTML5 Video Player -->
                <div class="relative bg-black rounded-xl overflow-hidden aspect-video max-h-[380px] w-full border border-gray-150 dark:border-gray-850 flex items-center justify-center shadow-inner">
                  <video
                    ref="videoPlayer"
                    :src="getVideoUrl(selectedClip.file_url)"
                    controls
                    class="w-full h-full object-contain"
                  ></video>
                  <!-- Bounding box overlay mock -->
                  <div class="absolute inset-0 pointer-events-none opacity-30 mix-blend-screen bg-green-500/5 flex items-center justify-center border border-emerald-500/20">
                    <div class="absolute top-4 left-4 bg-emerald-600 text-white text-[9px] font-bold px-2 py-0.5 rounded-lg shadow-sm flex items-center gap-1 uppercase tracking-wider">
                      <span class="h-1.5 w-1.5 rounded-full bg-red-500 animate-ping"></span>
                      YOLOv8 Active
                    </div>
                  </div>
                </div>

                <!-- AI Inference Metrics -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  <!-- Count Estimate (Animated Number Countup) -->
                  <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850 rounded-xl p-4 space-y-1">
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Estimated Bird Count</p>
                    <div class="flex items-baseline gap-1.5">
                      <span class="text-3xl font-black text-gray-900 dark:text-white tabular-nums">{{ animatedBirdCount }}</span>
                      <span class="text-[10px] text-gray-450 dark:text-gray-500 font-semibold">in-frame density</span>
                    </div>
                    <p class="text-[10px] text-gray-500 dark:text-gray-450 mt-1">Normal cluster profile detected</p>
                  </div>

                  <!-- Activity level score (Circular SVG Gauge) -->
                  <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850 rounded-xl p-4 flex items-center justify-between gap-2">
                    <div class="space-y-1.5">
                      <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Activity Index</p>
                      <div class="flex items-baseline gap-0.5">
                        <span class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ selectedClip.inference_result?.movement_score }}</span>
                        <span class="text-[10px] text-gray-400 dark:text-gray-500 font-semibold">/ 10</span>
                      </div>
                      <div class="pt-0.5">
                        <AgriBadge
                          :variant="selectedClip.inference_result?.movement_score < 2 ? 'critical' : selectedClip.inference_result?.movement_score > 7 ? 'warning' : 'success'"
                          size="xs"
                        >
                          {{ getActivityLabel(selectedClip.inference_result?.movement_score) }}
                        </AgriBadge>
                      </div>
                    </div>
                    <!-- Circular Gauge -->
                    <div class="relative flex items-center justify-center shrink-0">
                      <svg class="w-14 h-14 transform -rotate-90">
                        <circle cx="28" cy="28" r="24" class="stroke-gray-250 dark:stroke-gray-800" stroke-width="4.5" fill="transparent" />
                        <circle
                          cx="28" cy="28" r="24"
                          class="transition-all duration-1000 ease-out"
                          :class="selectedClip.inference_result?.movement_score < 2 ? 'stroke-status-danger' : selectedClip.inference_result?.movement_score > 7 ? 'stroke-status-warning' : 'stroke-primary-500'"
                          stroke-width="4.5"
                          fill="transparent"
                          :stroke-dasharray="2 * Math.PI * 24"
                          :stroke-dashoffset="2 * Math.PI * 24 * (1 - (selectedClip.inference_result?.movement_score || 0) / 10)"
                        />
                      </svg>
                      <span class="absolute text-2xs font-extrabold text-gray-700 dark:text-gray-300">{{ (selectedClip.inference_result?.movement_score * 10).toFixed(0) }}%</span>
                    </div>
                  </div>

                  <!-- Low Activity windows -->
                  <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850 rounded-xl p-4 space-y-1 flex flex-col justify-between">
                    <div>
                      <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Anomalous Activity</p>
                      <div class="text-xs font-bold text-gray-900 dark:text-white mt-1.5 flex items-center gap-1.5">
                        <span class="material-icons-outlined text-[16px] leading-none" :class="selectedClip.inference_result?.low_activity_windows?.length > 0 ? 'text-status-warning' : 'text-primary-500'">
                          {{ selectedClip.inference_result?.low_activity_windows?.length > 0 ? 'warning' : 'check_circle' }}
                        </span>
                        {{ selectedClip.inference_result?.low_activity_windows?.length > 0 ? 'Lethargy Flagged' : 'No Anomaly' }}
                      </div>
                    </div>
                    <p class="text-[10px] text-gray-450 dark:text-gray-500 leading-normal">
                      {{ selectedClip.inference_result?.low_activity_windows?.length > 0
                        ? 'Detected slow movement segments.'
                        : 'Uniform cohort movement observed.' }}
                    </p>
                  </div>
                </div>
              </div>
            </AgriCard>

            <!-- Anomalies details timeline -->
            <div v-if="selectedClip.inference_result?.low_activity_windows?.length > 0" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-3 animate-fade-in-up">
              <h4 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5 select-none">
                <span class="material-icons-outlined text-[16px] text-status-warning">warning</span>
                Flagged Anomaly Details
              </h4>
              <div class="space-y-4 pl-2">
                <div
                  v-for="(w, idx) in selectedClip.inference_result.low_activity_windows"
                  :key="idx"
                  class="border-l-2 border-amber-400 pl-4 py-1.5 space-y-1 relative animate-scale-in"
                  :class="getStaggerDelayClass(idx)"
                >
                  <!-- Bullet dot -->
                  <div class="absolute -left-1.5 top-3 h-2.5 w-2.5 rounded-full bg-amber-400 animate-pulse-glow"></div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/45 border border-amber-100 dark:border-amber-900/30 px-2 py-0.5 rounded-md tabular-nums">
                      {{ w.start_sec }}s - {{ w.end_sec }}s
                    </span>
                    <span class="text-xs text-amber-800 dark:text-amber-300 font-bold">Lethargic Cluster Velocity</span>
                  </div>
                  <p class="text-xs text-gray-650 dark:text-gray-350">
                    Reason: {{ w.reason }}
                  </p>
                </div>
              </div>
            </div>
          </template>

        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'
import { useAnimations } from '../composables/useAnimations'
import { useToast } from '../composables/useToast'

// Design System components
import AgriCard from '../components/ui/AgriCard.vue'
import AgriBadge from '../components/ui/AgriBadge.vue'
import AgriProgressBar from '../components/ui/AgriProgressBar.vue'
import AgriButton from '../components/ui/AgriButton.vue'
import AgriSelect from '../components/ui/AgriSelect.vue'

const toast = useToast()
const { animateNumber, getStaggerDelayClass } = useAnimations()

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const clips = ref([])
const selectedClip = ref(null)
const listLoading = ref(false)
const processing = ref(false)
const error = ref('')
const isDragging = ref(false)
const uploadProgress = ref(0)
const animatedBirdCount = ref(0)

const videoPlayer = ref(null)
let progressInterval = null

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

const batchOptions = computed(() => {
  return store.batchesList.map(b => ({
    label: `#${b.id} — ${b.breed} (${b.status})`,
    value: b.id
  }))
})

// Watch selected clip and animate the bird count estimate
watch(selectedClip, (newClip) => {
  if (newClip?.inference_result?.bird_count_est) {
    animateNumber(animatedBirdCount, 0, newClip.inference_result.bird_count_est, 650)
  } else {
    animatedBirdCount.value = 0
  }
}, { immediate: true })

// ── Data fetching ──────────────────────────
const fetchClips = async () => {
  if (!selectedBatchId.value) return
  listLoading.value = true
  try {
    clips.value = await api.inference.list(selectedBatchId.value)
    if (clips.value.length > 0 && !selectedClip.value) {
      selectedClip.value = clips.value[0]
    }
  } catch (err) {
    console.error('Failed to load video clips:', err)
  } finally {
    listLoading.value = false
  }
}

const onBatchChange = () => {
  selectedClip.value = null
  fetchClips()
}

const selectClip = (clip) => {
  selectedClip.value = clip
  if (videoPlayer.value) {
    videoPlayer.value.load()
  }
}

// ── Progress Simulation & Upload ──────────
const startProgress = () => {
  uploadProgress.value = 0
  progressInterval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += Math.floor(Math.random() * 8) + 2
    }
  }, 180)
}

const endProgress = () => {
  if (progressInterval) clearInterval(progressInterval)
  uploadProgress.value = 100
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    uploadFile(files[0])
  }
}

const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    uploadFile(files[0])
  }
}

const uploadFile = async (file) => {
  if (!selectedBatchId.value) return
  error.value = ''
  processing.value = true
  startProgress()

  try {
    const result = await api.inference.uploadVideo(selectedBatchId.value, file)
    endProgress()
    setTimeout(() => {
      clips.value.unshift(result)
      selectedClip.value = result
      toast.success('Footage uploaded and processed by YOLOv8')
      processing.value = false
    }, 400)
  } catch (err) {
    if (progressInterval) clearInterval(progressInterval)
    error.value = err.message || 'CV inference failed on this video.'
    processing.value = false
  }
}

// ── Formatting & Display helpers ───────────
const getFileName = (pathStr) => {
  if (!pathStr) return ''
  return pathStr.split(/[\\/]/).pop()
}

const getVideoUrl = (pathStr) => {
  if (!pathStr) return ''
  const filename = getFileName(pathStr)
  return `http://127.0.0.1:8000/uploads/${filename}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const options = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

const getActivityLabel = (score) => {
  if (score === null || score === undefined) return 'Unknown'
  if (score < 2) return 'Lethargic'
  if (score > 7) return 'Hyperactive'
  return 'Active'
}

// ── Lifecycle & Watchers ──────────────────
watch(() => store.activeBatch, (newVal) => {
  if (newVal && !selectedBatchId.value) {
    selectedBatchId.value = newVal.id
    fetchClips()
  }
}, { immediate: true })

onMounted(() => {
  if (store.activeBatch) {
    selectedBatchId.value = store.activeBatch.id
    fetchClips()
  }
})
</script>
