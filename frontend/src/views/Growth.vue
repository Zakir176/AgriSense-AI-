<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Growth Monitoring</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Record cohort weight samples and check development metrics.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Record Sample Weight</h2>
        <div class="text-gray-450 dark:text-gray-500 py-6 text-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Weight Input Form
        </div>
      </div>
      
      <div class="lg:col-span-2 bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Growth Curve Chart</h2>
        <div class="text-gray-450 dark:text-gray-500 h-64 flex items-center justify-center border border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
          Growth Rate chart
        </div>
      </div>
    </div>
  </div>
</template>
