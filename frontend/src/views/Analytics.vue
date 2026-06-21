<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Analytics & Insights</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Cross-batch analysis, efficiency trends, and dynamic management suggestions.</p>
    </div>

    <!-- Recommendations Card -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Rule-Based Recommendations</h2>
      <div class="text-gray-450 dark:text-gray-500 py-6 text-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
        Suggestions based on metrics (e.g. Feed-Conversion-Ratio performance alerts)
      </div>
    </div>

    <!-- Chart Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Feed Efficiency Analysis</h3>
        <div class="text-gray-450 dark:text-gray-500 h-64 flex items-center justify-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Feed Conversion Chart
        </div>
      </div>
      <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Growth Deviation</h3>
        <div class="text-gray-450 dark:text-gray-500 h-64 flex items-center justify-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Growth Rate Dev Chart
        </div>
      </div>
    </div>
  </div>
</template>
