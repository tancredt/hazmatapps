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
        <span class="district-use">(Station Use)</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import HomeHeader from './HomeHeader.vue'

const props = defineProps({ district: String, location_label: String })
const route = useRoute()
const district = computed(() => props.district || route.params.district)
const location_label = computed(() => props.location_label || route.params.location_label)
</script>