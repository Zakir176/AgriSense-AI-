<template>
  <div class="space-y-6">
    <div>
      <div class="flex items-center space-x-2">
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Audio Insights</h1>
        <span class="bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400 text-xs font-semibold px-2 py-1 rounded-full border border-amber-200 dark:border-amber-900">Research Preview</span>
      </div>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Flock recording repository illustrating baseline bird behavior distress patterns.
      </p>
    </div>

    <!-- Alert Box emphasizing Illustrative/Research preview status -->
    <div class="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/60 rounded-xl p-4 flex items-start space-x-3 text-amber-800 dark:text-amber-300 text-sm">
      <svg class="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <span class="font-semibold">Research Stage Feature:</span> This module functions solely as an illustrative library of pre-tagged sound bytes. Real-time audio distress detection is a future capability currently under active research.
      </div>
    </div>

    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Acoustic Samples Library</h2>
      <div class="text-center py-12 text-gray-450 dark:text-gray-500 border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
        Audio clips library placeholder
      </div>
    </div>
  </div>
</template>
