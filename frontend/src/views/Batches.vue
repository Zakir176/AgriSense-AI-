<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Batches</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Register new cohorts, view flock history, and close active batches.</p>
      </div>
      <button class="bg-primary-600 hover:bg-primary-500 text-white font-medium px-4 py-2.5 rounded-xl transition">
        Register Batch
      </button>
    </div>

    <!-- Active Batches Table Placeholder -->
    <div class="bg-white dark:bg-darkbg-50 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden shadow-sm transition-colors duration-250">
      <div class="p-6 border-b border-gray-200 dark:border-gray-800">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Active Cohorts</h2>
      </div>
      <div class="text-center py-12 text-gray-450 dark:text-gray-500">
        No active cohorts registered. Click "Register Batch" to get started.
      </div>
    </div>
  </div>
</template>
