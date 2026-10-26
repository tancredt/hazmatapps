<template>
  <div class="app-container">
    <Navbar v-if="authStore.isAuthenticated" />
    <main>
      <RouterView />
    </main>
    <AppFooter v-if="authStore.isAuthenticated" />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
import AppFooter from './components/AppFooter.vue'
import { useAuthStore } from './stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.checkAuth()
})
</script>

<style>
/* Lock the viewport to prevent window-level scrolling */
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden; 
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

main {
  flex: 1;
  padding-top: 50px; /* Space for the fixed Navbar */
  overflow-y: auto; /* Allows scrolling inside the main area if content overflows */
  box-sizing: border-box;
}
</style>
