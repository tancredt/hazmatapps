<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 5 minutes in milliseconds
const TIMEOUT_DURATION = 5 * 60 * 1000 
let inactivityTimer = null

// Events that indicate the user is actively using the app
const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']

// Function to handle the timeout
const handleTimeout = async () => {
  console.log('Session timed out due to inactivity.')
  if (inactivityTimer) clearTimeout(inactivityTimer)
  
  // Log the user out via the API and redirect to the login screen
  await authStore.logout()
  router.push('/') 
}

// Function to reset the timer on user activity
const resetTimer = () => {
  if (inactivityTimer) {
    clearTimeout(inactivityTimer)
  }
  
  // Only set the timer if the user is actually logged in
  if (authStore.isAuthenticated) {
    inactivityTimer = setTimeout(handleTimeout, TIMEOUT_DURATION)
  }
}

// Watch for authentication state changes to start/stop the timer
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    resetTimer() // User logged in, start the timer
  } else {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer) // User logged out, stop the timer
      inactivityTimer = null
    }
  }
})

onMounted(() => {
  // Add event listeners for user activity
  activityEvents.forEach(event => {
    window.addEventListener(event, resetTimer, { passive: true })
  })
  
  // If already authenticated on mount (e.g., page refresh), start the timer
  if (authStore.isAuthenticated) {
    resetTimer()
  }
})

onUnmounted(() => {
  // Clean up event listeners and timer when the app is destroyed
  activityEvents.forEach(event => {
    window.removeEventListener(event, resetTimer)
  })
  if (inactivityTimer) {
    clearTimeout(inactivityTimer)
  }
})
</script>

<template>
  <!-- This is the placeholder where Vue Router will render your matched components -->
  <router-view />
</template>

<style>
/* Ensure the app takes up the full viewport height for mobile layouts */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>