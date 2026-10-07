<template>
  <div class="sub-menu-screen">
    <h1>District: {{ district }}</h1>
    <p class="subtitle">Select an operation</p>
    <div class="menu-grid">
      <router-link :to="{ name: 'DistrictStatus', params: { district } }" class="menu-card">
        <h2>District Status</h2>
        <p>View cache slots & movements</p>
      </router-link>
      <router-link :to="{ name: 'Return', params: { district } }" class="menu-card">
        <h2>Return Detector</h2>
        <p>Return detectors to Burnley</p>
      </router-link>
      <router-link :to="{ name: 'Restock', params: { district } }" class="menu-card">
        <h2>Restock District Cache</h2>
        <p>Add detectors to cache</p>
      </router-link>
    </div>
    <div class="action-bar" style="margin-top: 40px;">
      <router-link :to="{ name: 'DistrictMainMenu' }" class="btn-cancel" style="text-decoration: none; display: inline-block; padding: 12px 32px;">
        Back to District Selection
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({ district: String })
const route = useRoute()
const district = computed(() => props.district || route.params.district)
</script>