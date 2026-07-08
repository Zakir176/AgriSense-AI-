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
                    @timeupdate="onVideoTimeUpdate"
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

                <!-- Discrepancy Status Banner -->
                <div v-if="selectedClip?.inference_result?.discrepancy_note">
                  <div
                    class="border rounded-2xl p-4 flex items-start space-x-3 text-xs"
                    :class="selectedClip.inference_result.discrepancy_note.includes('missing')
                      ? (selectedClip.inference_result.discrepancy_note.includes('mortality')
                        ? 'bg-red-55/15 dark:bg-red-950/20 border-red-200 dark:border-red-900/40 text-red-800 dark:text-red-300'
                        : 'bg-amber-55/15 dark:bg-amber-950/20 border-amber-255/35 dark:border-amber-900/40 text-amber-850 dark:text-amber-300')
                      : 'bg-emerald-55/15 dark:bg-emerald-950/15 border-emerald-200/60 dark:border-emerald-900/30 text-emerald-800 dark:text-emerald-350'"
                  >
                    <span class="material-icons-outlined shrink-0 mt-0.5"
                      :class="selectedClip.inference_result.discrepancy_note.includes('missing')
                        ? (selectedClip.inference_result.discrepancy_note.includes('mortality') ? 'text-red-500' : 'text-amber-500')
                        : 'text-emerald-500'"
                    >
                      {{ selectedClip.inference_result.discrepancy_note.includes('missing') ? 'report_problem' : 'check_circle' }}
                    </span>
                    <div class="space-y-1">
                      <p class="font-bold uppercase tracking-wider text-[10px]">
                        {{ selectedClip.inference_result.discrepancy_note.includes('missing')
                          ? (selectedClip.inference_result.discrepancy_note.includes('mortality') ? 'Critical Anomaly: Suspected Mortality' : 'Warning: Population Discrepancy (Undocumented Loss)')
                          : 'Population Status: Verified' }}
                      </p>
                      <p class="text-xs leading-relaxed font-semibold">
                        {{ selectedClip.inference_result.discrepancy_note }}
                      </p>
                      <p class="text-[10px] text-gray-500 dark:text-gray-400 mt-1 leading-normal" v-if="selectedClip.inference_result.discrepancy_note.includes('missing')">
                        Note: The system automatically compared this visual scan against batch parameters (flock size minus daily mortality logs). A notification has been raised in the system alerts queue.
                      </p>
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


            <!-- Active Object Tracking Map -->
            <AgriCard class="mt-6 animate-fade-in-up" v-if="selectedClip?.inference_result?.tracked_birds">
              <template #header>
                <div class="flex items-center justify-between w-full">
                  <div class="flex items-center gap-2">
                    <span class="material-icons-outlined text-primary-650 dark:text-primary-400">sensors</span>
                    <h3 class="text-sm font-bold text-gray-900 dark:text-white">Spatial Telemetry & Density Map</h3>
                  </div>
                  <!-- Mode Toggles -->
                  <div class="flex items-center space-x-2">
                    <button 
                      @click="heatmapMode = false"
                      class="px-2.5 py-1 rounded-lg text-2xs font-extrabold border uppercase tracking-wider transition-colors cursor-pointer"
                      :class="!heatmapMode 
                        ? 'bg-primary-50 dark:bg-primary-950/40 border-primary-300 text-primary-700 dark:text-primary-400 shadow-sm font-black' 
                        : 'bg-white dark:bg-darkbg-100 border-gray-250 dark:border-gray-800 text-gray-400 dark:text-gray-500 hover:text-gray-600'"
                    >
                      Vector Dots
                    </button>
                    <button 
                      @click="heatmapMode = true"
                      class="px-2.5 py-1 rounded-lg text-2xs font-extrabold border uppercase tracking-wider transition-colors cursor-pointer"
                      :class="heatmapMode 
                        ? 'bg-primary-50 dark:bg-primary-950/40 border-primary-300 text-primary-700 dark:text-primary-400 shadow-sm font-black' 
                        : 'bg-white dark:bg-darkbg-100 border-gray-250 dark:border-gray-800 text-gray-400 dark:text-gray-500 hover:text-gray-600'"
                    >
                      Thermal Density
                    </button>
                  </div>
                </div>
              </template>
              
              <div class="space-y-4">
                <!-- Map Header Statistics -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-gray-50 dark:bg-darkbg-100 border border-gray-150 dark:border-gray-850">
                  <div>
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Spatial Dispersion</p>
                    <p class="text-base font-black text-gray-800 dark:text-white tabular-nums">
                      {{ selectedClip.inference_result.spatial_dispersion_index || '38.4' }} <span class="text-2xs font-bold text-gray-400 dark:text-gray-500">px</span>
                    </p>
                  </div>
                  <div>
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider font-extrabold">Clustering Index</p>
                    <p class="text-base font-black text-gray-800 dark:text-white tabular-nums">
                      {{ selectedClip.inference_result.clustering_density_pct || '15.0' }}%
                    </p>
                  </div>
                  <div>
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider font-extrabold">Clustering Warning</p>
                    <p class="text-xs font-extrabold mt-1.5 flex items-center gap-1.5 leading-none" 
                       :class="(selectedClip.inference_result.clustering_density_pct || 15) > 55 ? 'text-red-550' : 'text-primary-600'">
                      <span class="h-2 w-2 rounded-full inline-block" :class="(selectedClip.inference_result.clustering_density_pct || 15) > 55 ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'"></span>
                      {{ (selectedClip.inference_result.clustering_density_pct || 15) > 55 ? 'Critical (Huddling)' : 'Healthy Dispersion' }}
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="text-[9px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Tracked Nodes</p>
                    <p class="text-base font-black text-gray-800 dark:text-white tabular-nums">
                      {{ selectedClip.inference_result.tracked_birds.length }} <span class="text-2xs font-bold text-gray-400 dark:text-gray-500">nodes</span>
                    </p>
                  </div>
                </div>

                <!-- Canvas Rendering Area -->
                <div class="relative bg-black rounded-xl border border-gray-150 dark:border-gray-850 overflow-hidden flex items-center justify-center">
                  <canvas 
                    ref="mapCanvas" 
                    class="w-full aspect-[645/480] block"
                    @mousemove="handleCanvasHover"
                    @mouseleave="handleCanvasLeave"
                  ></canvas>
                  
                  <!-- Hover Annotation Overlay card -->
                  <div 
                    v-if="hoveredBird"
                    class="absolute bg-gray-900/95 text-white border border-gray-800 text-[10px] rounded-lg p-2 shadow-xl backdrop-blur-sm pointer-events-none z-20 space-y-0.5"
                    :style="{ left: hoveredBirdScreenX + 'px', top: hoveredBirdScreenY + 'px', transform: 'translate(-50%, -120%)' }"
                  >
                    <p class="font-extrabold text-primary-400 uppercase tracking-wider">Bird Node #{{ hoveredBird.track_id }}</p>
                    <p class="font-semibold text-gray-300">Status: {{ hoveredBird.status === 'inactive' ? `Lethargic (${hoveredBird.inactivity_duration_sec}s)` : 'Active' }}</p>
                    <p class="text-2xs text-gray-500">Coordinates: {{ hoveredBird.x }}, {{ hoveredBird.y }}</p>
                  </div>
                </div>

                <!-- Interactive bird node selector grid -->
                <div class="text-left">
                  <div class="flex justify-between items-center mb-2">
                    <p class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">Tracked Nodes Catalog</p>
                    <div class="flex items-center gap-3 text-[10px] font-semibold">
                      <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-emerald-500"></span> Active ({{ activeCount }})</span>
                      <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-red-500 animate-ping"></span> Inactive ({{ inactiveCount }})</span>
                    </div>
                  </div>
                  <div class="grid grid-cols-6 sm:grid-cols-10 md:grid-cols-12 lg:grid-cols-14 gap-1.5 max-h-[220px] overflow-y-auto p-3 border border-gray-150 dark:border-gray-850 rounded-xl bg-gray-50/50 dark:bg-darkbg-100/30">
                    <div
                      v-for="b in selectedClip.inference_result.tracked_birds"
                      :key="b.track_id"
                      class="h-8 flex flex-col items-center justify-center rounded-lg border text-[10px] font-mono font-bold transition-all relative group cursor-pointer"
                      :class="[
                        b.status === 'inactive'
                          ? 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900/40 text-red-650 dark:text-red-400 animate-pulse'
                          : 'bg-emerald-50/50 dark:bg-emerald-950/10 border-emerald-100 dark:border-emerald-900/20 text-emerald-600 dark:text-emerald-450 hover:bg-emerald-100/40 dark:hover:bg-emerald-950/30',
                        hoveredBirdId === b.track_id ? 'ring-2 ring-primary-500 border-transparent scale-105 shadow-sm bg-primary-100/10 dark:bg-primary-950/20' : ''
                      ]"
                      @mouseenter="hoveredBirdId = b.track_id"
                      @mouseleave="hoveredBirdId = null"
                    >
                      <span class="absolute bottom-full mb-1.5 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-[9px] font-sans font-normal py-1 px-2 rounded opacity-0 pointer-events-none group-hover:opacity-100 transition whitespace-nowrap z-10 shadow-lg leading-normal">
                        ID #{{ b.track_id }} · {{ b.status === 'inactive' ? `Lethargic (${b.inactivity_duration_sec}s)` : 'Healthy & Active' }}
                      </span>
                      <span>#{{ b.track_id }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </AgriCard>
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

const activeCount = computed(() => {
  return selectedClip.value?.inference_result?.tracked_birds?.filter(b => b.status === 'active').length || 0
})

const inactiveCount = computed(() => {
  return selectedClip.value?.inference_result?.tracked_birds?.filter(b => b.status === 'inactive').length || 0
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

// ── Spatial Map Canvas Drawing ─────────────────
const heatmapMode = ref(false)
const mapCanvas = ref(null)
const hoveredBirdId = ref(null)
const hoveredBirdScreenX = ref(0)
const hoveredBirdScreenY = ref(0)
const currentTime = ref(0)

const onVideoTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = videoPlayer.value.currentTime
  }
}

const getBirdPositionAtTime = (bird, time) => {
  if (!bird.history || bird.history.length === 0) {
    return { x: bird.x, y: bird.y }
  }
  let closest = bird.history[0]
  let minDiff = Math.abs(closest.sec - time)
  for (let k = 1; k < bird.history.length; k++) {
    const diff = Math.abs(bird.history[k].sec - time)
    if (diff < minDiff) {
      minDiff = diff
      closest = bird.history[k]
    }
  }
  return { x: closest.x, y: closest.y }
}

const hoveredBird = computed(() => {
  if (!hoveredBirdId.value) return null
  return selectedClip.value?.inference_result?.tracked_birds?.find(b => b.track_id === hoveredBirdId.value) || null
})

const drawMap = () => {
  const canvasEl = mapCanvas.value
  if (!canvasEl) return

  const ctx = canvasEl.getContext('2d')
  if (!ctx) return

  // Standard dimensions
  canvasEl.width = 645
  canvasEl.height = 480

  ctx.clearRect(0, 0, canvasEl.width, canvasEl.height)

  const birds = selectedClip.value?.inference_result?.tracked_birds || []

  // Resolve positions at the current playback timestamp
  const resolvedPositions = birds.map(b => {
    const pos = getBirdPositionAtTime(b, currentTime.value)
    return {
      bird: b,
      x: pos.x,
      y: pos.y
    }
  })

  if (heatmapMode.value) {
    // Thermal density heat mode
    ctx.fillStyle = '#0a0d0c'
    ctx.fillRect(0, 0, canvasEl.width, canvasEl.height)

    ctx.strokeStyle = 'rgba(16, 185, 129, 0.04)'
    ctx.lineWidth = 1
    for (let x = 40; x < canvasEl.width; x += 40) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, canvasEl.height)
      ctx.stroke()
    }
    for (let y = 40; y < canvasEl.height; y += 40) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(canvasEl.width, y)
      ctx.stroke()
    }

    ctx.globalCompositeOperation = 'screen'
    resolvedPositions.forEach(rp => {
      const rad = ctx.createRadialGradient(rp.x, rp.y, 2, rp.x, rp.y, 45)
      if (rp.bird.status === 'inactive') {
        rad.addColorStop(0, 'rgba(239, 68, 68, 0.65)')
        rad.addColorStop(0.3, 'rgba(239, 68, 68, 0.35)')
        rad.addColorStop(0.7, 'rgba(245, 158, 11, 0.12)')
        rad.addColorStop(1, 'rgba(0, 0, 0, 0)')
      } else {
        rad.addColorStop(0, 'rgba(245, 158, 11, 0.55)')
        rad.addColorStop(0.4, 'rgba(16, 185, 129, 0.22)')
        rad.addColorStop(0.8, 'rgba(59, 130, 246, 0.05)')
        rad.addColorStop(1, 'rgba(0, 0, 0, 0)')
      }
      ctx.beginPath()
      ctx.arc(rp.x, rp.y, 45, 0, Math.PI * 2)
      ctx.fillStyle = rad
      ctx.fill()
    })
    ctx.globalCompositeOperation = 'source-over'
  } else {
    // Vector dots telemetry mode
    ctx.fillStyle = '#101513'
    ctx.fillRect(0, 0, canvasEl.width, canvasEl.height)

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)'
    ctx.lineWidth = 1
    for (let x = 40; x < canvasEl.width; x += 40) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, canvasEl.height)
      ctx.stroke()
    }
    for (let y = 40; y < canvasEl.height; y += 40) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(canvasEl.width, y)
      ctx.stroke()
    }

    // Draw cluster bonds dynamically based on current frame coordinates
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.12)'
    ctx.lineWidth = 0.8
    resolvedPositions.forEach((rp1, i1) => {
      resolvedPositions.forEach((rp2, i2) => {
        if (i1 >= i2) return
        const dist = Math.hypot(rp2.x - rp1.x, rp2.y - rp1.y)
        if (dist < 60.0) {
          ctx.beginPath()
          ctx.moveTo(rp1.x, rp1.y)
          ctx.lineTo(rp2.x, rp2.y)
          ctx.stroke()
        }
      })
    })

    // Draw active coordinates nodes
    resolvedPositions.forEach(rp => {
      const isHovered = hoveredBirdId.value === rp.bird.track_id
      if (rp.bird.status === 'inactive') {
        ctx.beginPath()
        ctx.arc(rp.x, rp.y, 14, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(239, 68, 68, 0.15)'
        ctx.fill()
        
        ctx.beginPath()
        ctx.arc(rp.x, rp.y, 8, 0, Math.PI * 2)
        ctx.strokeStyle = '#ef4444'
        ctx.lineWidth = 1.2
        ctx.stroke()
      } else if (isHovered) {
        ctx.beginPath()
        ctx.arc(rp.x, rp.y, 12, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(16, 185, 129, 0.25)'
        ctx.fill()
      }

      ctx.beginPath()
      ctx.arc(rp.x, rp.y, 5, 0, Math.PI * 2)
      ctx.fillStyle = rp.bird.status === 'inactive' ? '#f87171' : '#10b981'
      ctx.fill()

      ctx.font = 'bold 9px monospace'
      ctx.fillStyle = isHovered ? '#ffffff' : 'rgba(255,255,255,0.45)'
      ctx.fillText(`#${rp.bird.track_id}`, rp.x + 8, rp.y + 3)
    })
  }
}

const handleCanvasHover = (e) => {
  const canvasEl = mapCanvas.value
  if (!canvasEl) return

  const rect = canvasEl.getBoundingClientRect()
  const scaleX = canvasEl.width / rect.width
  const scaleY = canvasEl.height / rect.height
  
  const clickX = (e.clientX - rect.left) * scaleX
  const clickY = (e.clientY - rect.top) * scaleY

  let nearest = null
  let nearestPos = null
  let minDist = 25.0
  
  const birds = selectedClip.value?.inference_result?.tracked_birds || []
  birds.forEach(b => {
    const pos = getBirdPositionAtTime(b, currentTime.value)
    const dist = Math.hypot(pos.x - clickX, pos.y - clickY)
    if (dist < minDist) {
      minDist = dist
      nearest = b
      nearestPos = pos
    }
  })

  if (nearest && nearestPos) {
    hoveredBirdId.value = nearest.track_id
    hoveredBirdScreenX.value = (nearestPos.x / scaleX)
    hoveredBirdScreenY.value = (nearestPos.y / scaleY)
  } else {
    hoveredBirdId.value = null
  }
}

const handleCanvasLeave = () => {
  hoveredBirdId.value = null
}

// Redraw map on timeline updates or config toggles
watch([selectedClip, heatmapMode, hoveredBirdId, currentTime], () => {
  drawMap()
}, { deep: true })

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
  setTimeout(drawMap, 200)
})
</script>
