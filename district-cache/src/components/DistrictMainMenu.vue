<template>
  <div class="main-menu-screen">
    <h1>District Operations</h1>
    <p class="subtitle">Select a District</p>
    
    <div v-if="isLoading" class="loading">Loading districts...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div class="menu-grid" v-if="!isLoading && !error">
      <router-link 
        v-for="d in districts" 
        :key="d.value" 
        :to="{ name: 'DistrictOperationsMenu', params: { district: d.value } }" 
        class="menu-card"
      >
        <h2>{{ d.label }}</h2>
        <p>Manage district cache & returns</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'

const districts = ref([])
const isLoading = ref(false)
const error = ref(null)

onMounted(async () => {
  isLoading.value = true
  try {
    const data = await apiFetch('/districts/')
    // Filter out the 'ALL' option if it exists in your choices
    districts.value = data.filter(d => d.value !== 'AL') 
  } catch (err) {
    error.value = 'Failed to load districts.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
})
</script>