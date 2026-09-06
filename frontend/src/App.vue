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
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding-top: 50px;
  padding-bottom: 0.25rem;
  overflow: auto;
  max-height: calc(100vh - 50px);
}
</style>
