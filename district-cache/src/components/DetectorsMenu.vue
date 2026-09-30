<template>
  <div class="sub-menu-screen">
    <HomeHeader />
    <h1>Detectors</h1>
    <p class="subtitle">District: {{ district }} | Location: {{ location_label }}</p>
    
    <div class="menu-grid">
      <router-link :to="{ name: 'DetectorFault', params: { district, location_label } }" class="menu-card">
        <h2>Report Fault/Missing</h2>
        <p>Log a detector issue</p>
      </router-link>
      
      <router-link :to="{ name: 'LocationChanger', params: { district, location_label } }" class="menu-card">
        <h2>Swap Detector</h2>
        <p>Replace a faulty detector</p>
        <span class="district-use">(District Use)</span>
      </router-link>

      <!-- NEW DISTRICT STATUS BUTTON -->
      <router-link :to="{ name: 'DistrictStatus', params: { district, location_label } }" class="menu-card">
        <h2>District Status</h2>
        <p>View cache slots & movements</p>
        <span class="district-use">(District Use)</span>
      </router-link>

      <router-link :to="{ name: 'Return', params: { district, location_label } }" class="menu-card">
        <h2>Return Detector</h2>
        <p>Return detectors to Burnley</p>
        <span class="district-use">(District Use)</span>
      </router-link>
      
      <router-link :to="{ name: 'Restock', params: { district, location_label } }" class="menu-card">
        <h2>Restock District Cache</h2>
        <p>Add detectors to cache</p>
        <span class="district-use">(District Use)</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({
  district: String,
  location_label: String
})

const route = useRoute()
const district = computed(() => props.district || route.params.district)
const location_label = computed(() => props.location_label || route.params.location_label)
</script>

