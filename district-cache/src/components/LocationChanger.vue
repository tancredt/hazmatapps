<template>
  <div class="app-container">
    <LoginScreen v-if="!auth.isAuthenticated" />
    <SwapScreen 
      v-else 
      :district="district" 
      :location_label="location_label" 
    />
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router' // 👈 Added useRoute
import { useAuthStore } from '../stores/auth'
import LoginScreen from '../components/LoginScreen.vue'
import SwapScreen from '../components/SwapScreen.vue'

const props = defineProps({
  district: String,
  location_label: String
})

const route = useRoute()
const auth = useAuthStore()

// 👇 Fallback to route params if props haven't bound yet
const district = computed(() => props.district || route.params.district)
const location_label = computed(() => props.location_label || route.params.location_label)

onMounted(() => {
  auth.checkAuth()
})
</script>