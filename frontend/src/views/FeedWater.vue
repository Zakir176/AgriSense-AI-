<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Feed & Water Logs</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Record daily consumption and monitor rolling deviations.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Input Form Card -->
      <div class="lg:col-span-1 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Log Daily Metrics</h2>
        <div class="text-gray-450 dark:text-gray-500 py-6 text-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Daily Log Form
        </div>
      </div>
      
      <!-- Chart Card -->
      <div class="lg:col-span-2 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Flock Consumption Trends</h2>
        <div class="text-gray-450 dark:text-gray-500 h-64 flex items-center justify-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Timeseries Chart
        </div>
      </div>
    </div>
  </div>
</template>
