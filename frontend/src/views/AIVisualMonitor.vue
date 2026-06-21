<template>
  <div class="space-y-6">

    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">AI Visual Monitoring</h1>
          <span class="bg-primary-100 text-primary-700 dark:bg-primary-950 dark:text-primary-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-primary-200 dark:border-primary-800">YOLOv8 CV Engine</span>
        </div>
        <p class="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
          Upload poultry house footage to analyze density distribution, estimate counts, and profile movement anomalies.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <!-- Batch selector -->
        <select
          v-model="selectedBatchId"
          @change="onBatchChange"
          class="text-sm bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl px-3 py-2 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
        >
          <option :value="null" disabled>Select batch…</option>
          <option v-for="b in store.batchesList" :key="b.id" :value="b.id">
            #{{ b.id }} — {{ b.breed }} ({{ b.status }})
          </option>
        </select>
      </div>
    </div>

    <!-- Alert Box emphasizing Uploaded footage status -->
    <div class="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/40 rounded-xl p-4 flex items-start space-x-3 text-blue-700 dark:text-blue-300 text-sm">
      <span class="material-icons-outlined text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5">info</span>
      <div>
        <span class="font-semibold">Prototype Mode:</span> This CV module analyzes pre-recorded video clips. Live camera stream bindings are scheduled for Phase 2 implementation.
      </div>
    </div>

    <!-- ─── No batch selected state ─── -->
    <div v-if="!selectedBatchId" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center">
      <span class="material-icons-outlined text-4xl text-gray-300 dark:text-gray-700 block mb-3">photo_camera</span>
      <p class="text-sm font-semibold text-gray-600 dark:text-gray-400">Select a batch above to start AI footage profiling.</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Footage logs and neural network inferences are archived per batch.</p>
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- ─── Left Pane: Upload & History ─── -->
        <div class="space-y-6 lg:col-span-1">
          <!-- Upload Box -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-4">
            <h2 class="text-sm font-bold text-gray-900 dark:text-white">Analyze New Footage</h2>

            <div
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
              class="border-2 border-dashed rounded-2xl p-6 text-center transition cursor-pointer flex flex-col items-center justify-center space-y-2 group"
              :class="isDragging
                ? 'border-primary-500 bg-primary-50/10'
                : 'border-gray-200 dark:border-gray-850 hover:border-primary-500/50 hover:bg-gray-50/50 dark:hover:bg-darkbg-100/50'"
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
            <div v-if="processing" class="bg-primary-50/30 dark:bg-primary-950/10 border border-primary-100 dark:border-primary-900/40 rounded-xl p-4 flex items-center gap-3">
              <span class="material-icons-outlined text-lg text-primary-600 dark:text-primary-400 animate-spin">sync</span>
              <div class="text-xs">
                <p class="font-bold text-gray-800 dark:text-gray-200">Executing AI CV Inference</p>
                <p class="text-gray-500 dark:text-gray-400 text-[10px]">Processing frames with YOLOv8 neural net…</p>
              </div>
            </div>

            <!-- Upload Error -->
            <div v-if="error" class="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 rounded-xl p-3 text-xs text-red-600 dark:text-red-400">
              {{ error }}
            </div>
          </div>

          <!-- History Catalog -->
          <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden">
            <div class="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">Footage History</h2>
            </div>

            <div v-if="listLoading" class="p-4 space-y-2">
              <div v-for="n in 3" :key="n" class="h-12 bg-gray-100 dark:bg-gray-800/50 rounded-xl animate-pulse"></div>
            </div>

            <div v-else-if="clips.length === 0" class="py-12 text-center text-xs text-gray-400 dark:text-gray-500">
              <span class="material-icons-outlined text-2xl mb-1 text-gray-300 dark:text-gray-700 block">movie</span>
              No clips uploaded yet.
            </div>

            <div v-else class="divide-y divide-gray-100 dark:divide-gray-800 max-h-[300px] overflow-y-auto">
              <button
                v-for="c in clips"
                :key="c.id"
                @click="selectClip(c)"
                class="w-full text-left px-5 py-3 hover:bg-gray-50 dark:hover:bg-darkbg-100 transition flex items-center justify-between text-xs"
                :class="selectedClip?.id === c.id ? 'bg-primary-50/20 dark:bg-primary-950/10 border-r-2 border-primary-500' : ''"
              >
                <div class="space-y-0.5">
                  <p class="font-bold text-gray-900 dark:text-white">{{ getFileName(c.file_url) }}</p>
                  <p class="text-[10px] text-gray-400 dark:text-gray-500">{{ formatDateTime(c.uploaded_at) }}</p>
                </div>
                <div class="text-right">
                  <p class="font-bold text-gray-700 dark:text-gray-300">{{ c.inference_result?.bird_count_est }} birds</p>
                  <p class="text-[9px] text-gray-450 dark:text-gray-500">Score: {{ c.inference_result?.movement_score }}</p>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- ─── Right Pane: Visual Player & CV Analytics ─── -->
        <div class="lg:col-span-2 space-y-6">

          <div v-if="!selectedClip" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-16 text-center flex flex-col items-center justify-center h-full min-h-[400px]">
            <span class="material-icons-outlined text-5xl text-gray-300 dark:text-gray-700 mb-3 animate-pulse">analytics</span>
            <h3 class="font-bold text-gray-700 dark:text-gray-300 text-sm">Awaiting footage selection</h3>
            <p class="text-xs text-gray-450 dark:text-gray-500 mt-1 max-w-xs mx-auto">
              Upload a new poultry video clip or select a historic record from the sidebar to inspect AI predictions.
            </p>
          </div>

          <template v-else>
            <!-- Player and Overlays -->
            <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm overflow-hidden p-4 space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="material-icons-outlined text-primary-600 dark:text-primary-400">play_circle_outline</span>
                  <h3 class="text-sm font-bold text-gray-900 dark:text-white">{{ getFileName(selectedClip.file_url) }}</h3>
                </div>
                <span class="text-[10px] text-gray-400 dark:text-gray-500 font-bold uppercase tracking-wider">{{ formatDateTime(selectedClip.uploaded_at) }}</span>
              </div>

              <!-- HTML5 Video Player -->
              <div class="relative bg-black rounded-xl overflow-hidden aspect-video max-h-[380px] w-full border border-gray-150 dark:border-gray-850 flex items-center justify-center shadow-inner">
                <video
                  ref="videoPlayer"
                  :src="getVideoUrl(selectedClip.file_url)"
                  controls
                  class="w-full h-full object-contain"
                ></video>
                <!-- Neural Net bounding box mockup overlay -->
                <div class="absolute inset-0 pointer-events-none opacity-30 mix-blend-screen bg-green-500/5 flex items-center justify-center border-2 border-emerald-500/20">
                  <div class="absolute top-4 left-4 bg-emerald-600 text-white text-[9px] font-bold px-2 py-0.5 rounded shadow flex items-center gap-1 uppercase tracking-wider">
                    <span class="h-1.5 w-1.5 rounded-full bg-red-500 animate-ping"></span>
                    YOLOv8 Active
                  </div>
                </div>
              </div>

              <!-- AI Inference Metrics -->
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                <!-- Count Estimate -->
                <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-100 dark:border-gray-850 rounded-xl p-4 space-y-1">
                  <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Estimated Bird Count</p>
                  <div class="flex items-baseline gap-1.5">
                    <span class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ selectedClip.inference_result?.bird_count_est }}</span>
                    <span class="text-[10px] text-gray-400 dark:text-gray-500 font-semibold">in frame density</span>
                  </div>
                  <p class="text-[10px] text-gray-450 dark:text-gray-500 mt-1">Normal cluster profile detected</p>
                </div>

                <!-- Activity level score -->
                <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-100 dark:border-gray-850 rounded-xl p-4 space-y-2">
                  <div class="flex justify-between items-center">
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Activity Index</p>
                    <span
                      class="text-[9px] font-extrabold px-1.5 py-0.5 rounded-md uppercase"
                      :class="getActivityClass(selectedClip.inference_result?.movement_score)"
                    >
                      {{ getActivityLabel(selectedClip.inference_result?.movement_score) }}
                    </span>
                  </div>
                  <div class="flex items-baseline gap-1">
                    <span class="text-2xl font-black text-gray-900 dark:text-white tabular-nums">{{ selectedClip.inference_result?.movement_score }}</span>
                    <span class="text-[10px] text-gray-400 dark:text-gray-500 font-semibold">/ 10</span>
                  </div>
                  <!-- Progress gauge -->
                  <div class="w-full bg-gray-200 dark:bg-gray-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-500"
                      :class="getActivityColor(selectedClip.inference_result?.movement_score)"
                      :style="{ width: `${selectedClip.inference_result?.movement_score * 10}%` }"
                    ></div>
                  </div>
                </div>

                <!-- Low Activity windows -->
                <div class="bg-gray-50 dark:bg-darkbg-100 border border-gray-100 dark:border-gray-850 rounded-xl p-4 space-y-1 flex flex-col justify-between">
                  <div>
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Anomalous Activity</p>
                    <div class="text-xs font-bold text-gray-900 dark:text-white mt-1 flex items-center gap-1.5">
                      <span class="material-icons-outlined text-[15px]" :class="selectedClip.inference_result?.low_activity_windows?.length > 0 ? 'text-amber-500' : 'text-emerald-500'">
                        {{ selectedClip.inference_result?.low_activity_windows?.length > 0 ? 'warning' : 'check_circle' }}
                      </span>
                      {{ selectedClip.inference_result?.low_activity_windows?.length > 0 ? 'Lethargy Flagged' : 'No Anomaly' }}
                    </div>
                  </div>
                  <p class="text-[10px] text-gray-450 dark:text-gray-500">
                    {{ selectedClip.inference_result?.low_activity_windows?.length > 0
                      ? 'Detected low movement windows in clip.'
                      : 'Uniform cohort movement observed.' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Anomalies details timeline -->
            <div v-if="selectedClip.inference_result?.low_activity_windows?.length > 0" class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm space-y-3">
              <h4 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
                <span class="material-icons-outlined text-[16px] text-amber-500">warning</span>
                Flagged Anomaly Details
              </h4>
              <div class="space-y-3 pl-2">
                <div
                  v-for="(w, idx) in selectedClip.inference_result.low_activity_windows"
                  :key="idx"
                  class="border-l-2 border-amber-400 pl-4 py-1 space-y-1 relative"
                >
                  <!-- Bullet dot -->
                  <div class="absolute -left-1.5 top-2.5 h-2.5 w-2.5 rounded-full bg-amber-400"></div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-gray-900 dark:text-white bg-amber-50 dark:bg-amber-950/40 border border-amber-100 dark:border-amber-900/30 px-2 py-0.5 rounded-md tabular-nums">
                      {{ w.start_sec }}s - {{ w.end_sec }}s
                    </span>
                    <span class="text-xs text-amber-700 dark:text-amber-400 font-semibold">Slow Movement Window</span>
                  </div>
                  <p class="text-xs text-gray-600 dark:text-gray-350">
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

// ── State ──────────────────────────────────
const selectedBatchId = ref(null)
const clips = ref([])
const selectedClip = ref(null)
const listLoading = ref(false)
const processing = ref(false)
const error = ref('')
const isDragging = ref(false)

const videoPlayer = ref(null)

// ── Computed ──────────────────────────────
const activeBatchObj = computed(() => {
  return store.batchesList.find(b => b.id === selectedBatchId.value)
})

// ── Data fetching ──────────────────────────
const fetchClips = async () => {
  if (!selectedBatchId.value) return
  listLoading.value = true
  try {
    clips.value = await api.inference.list(selectedBatchId.value)
    // Auto-select first clip if none is selected
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
  // Trigger reloading video if playing
  if (videoPlayer.value) {
    videoPlayer.value.load()
  }
}

// ── File Handlers ──────────────────────────
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

  try {
    const result = await api.inference.uploadVideo(selectedBatchId.value, file)
    // Add result to start of the array
    clips.value.unshift(result)
    // Select the new clip
    selectedClip.value = result
  } catch (err) {
    error.value = err.message || 'Catastrophic error: failed to run CV inference on this file format.'
  } finally {
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
  return `http://localhost:8000/uploads/${filename}`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const options = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  return new Date(dateStr).toLocaleDateString(undefined, options)
}

const getActivityClass = (score) => {
  if (score === null || score === undefined) return 'bg-gray-100 text-gray-700'
  if (score < 2) return 'bg-rose-50 text-rose-700 dark:bg-rose-950/30 dark:text-rose-400 border border-rose-100 dark:border-rose-900/30'
  if (score > 7) return 'bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400 border border-amber-100 dark:border-amber-900/30'
  return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/30'
}

const getActivityLabel = (score) => {
  if (score === null || score === undefined) return 'Unknown'
  if (score < 2) return 'Lethargic'
  if (score > 7) return 'Hyperactive'
  return 'Active'
}

const getActivityColor = (score) => {
  if (score === null || score === undefined) return 'bg-gray-400'
  if (score < 2) return 'bg-rose-500'
  if (score > 7) return 'bg-amber-500'
  return 'bg-emerald-500'
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
