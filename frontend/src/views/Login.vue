<template>
  <div class="min-h-screen flex items-center justify-center bg-[#f4f7f4] dark:bg-darkbg-100 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-250">
    <div class="max-w-md w-full space-y-8 bg-white dark:bg-darkbg-50 p-8 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-xl transition-colors duration-250">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          AgriSense AI
        </h2>
        <p class="mt-2 text-center text-sm text-gray-500 dark:text-gray-400">
          Sign in to access your farm dashboard
        </p>
      </div>
      <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Username</label>
            <input id="username" name="username" type="text" required class="appearance-none rounded-none relative block w-full px-3 py-2.5 border border-gray-250 dark:border-gray-800 placeholder-gray-400 dark:placeholder-gray-500 text-gray-800 dark:text-white rounded-t-xl bg-gray-50 dark:bg-darkbg-100 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" placeholder="Username" />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input id="password" name="password" type="password" required class="appearance-none rounded-none relative block w-full px-3 py-2.5 border border-gray-250 dark:border-gray-800 placeholder-gray-400 dark:placeholder-gray-500 text-gray-800 dark:text-white rounded-b-xl bg-gray-50 dark:bg-darkbg-100 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm" placeholder="Password" />
          </div>
        </div>

        <div>
          <button type="submit" class="group relative w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-medium rounded-xl text-white bg-primary-600 hover:bg-primary-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition">
            Sign In
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogin = () => {
  localStorage.setItem('agrisense_token', 'mock_token')
  router.push({ name: 'Dashboard' })
}
</script>
