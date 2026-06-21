<template>
  <div class="space-y-6">
    <div>
      <div class="flex items-center space-x-2">
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">AI Visual Monitoring</h1>
        <span class="bg-primary-100 text-primary-700 dark:bg-primary-950 dark:text-primary-400 text-xs font-semibold px-2 py-1 rounded-full border border-primary-200 dark:border-primary-800">Phase 1 Prototype</span>
      </div>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Upload pre-recorded footage of poultry houses to estimate bird counts and identify motion profiles.
      </p>
    </div>

    <!-- Alert Box emphasizing Uploaded footage status -->
    <div class="bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/60 rounded-xl p-4 flex items-start space-x-3 text-blue-700 dark:text-blue-300 text-sm">
      <svg class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div>
        <span class="font-semibold">Notice:</span> Phase 1 executes computer vision inference exclusively on <strong class="underline">uploaded video files</strong>. Live continuous camera integrations are deferred to Phase 2.
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Upload Footage</h2>
        <div class="text-gray-450 dark:text-gray-500 py-12 text-center border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-400 dark:hover:border-gray-700 transition cursor-pointer">
          Drag and drop video, or click to browse
        </div>
      </div>
      
      <div class="lg:col-span-2 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Inference Results</h2>
        <div class="text-gray-450 dark:text-gray-500 h-64 flex items-center justify-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Analyzed results details will appear here after upload
        </div>
      </div>
    </div>
  </div>
</template>
