<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Farm Dashboard</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Real-time indicators and operational summary for Prime Nest Poultry Farm.</p>
    </div>
    
    <!-- Summary Cards Grid -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-white dark:bg-darkbg-50 overflow-hidden border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm transition-colors duration-250">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Active Batches</div>
        <div class="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">0</div>
      </div>
      <div class="bg-white dark:bg-darkbg-50 overflow-hidden border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm transition-colors duration-250">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Total Birds</div>
        <div class="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">0</div>
      </div>
      <div class="bg-white dark:bg-darkbg-50 overflow-hidden border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm transition-colors duration-250">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Recent Alerts</div>
        <div class="mt-2 text-3xl font-semibold text-red-600 dark:text-red-400">0</div>
      </div>
      <div class="bg-white dark:bg-darkbg-50 overflow-hidden border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm transition-colors duration-250">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Growth Rate Performance</div>
        <div class="mt-2 text-3xl font-semibold text-primary-600 dark:text-primary-400">--</div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl p-6 shadow-sm transition-colors duration-250">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Active Alerts Queue</h2>
      <div class="text-center py-12 text-gray-450 dark:text-gray-500 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-lg">
        No active alerts. Daily metrics within normal limits.
      </div>
    </div>
  </div>
</template>
