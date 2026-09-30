<template>
  <div class="main-menu-screen">
    <h1>FRV Inventory</h1>
    <p class="subtitle">District: {{ district }} | Location: {{ location_label }}</p>
    <div class="menu-grid">
      <router-link :to="{ name: 'CylindersMenu', params: { district, location_label } }" class="menu-card cylinders">
        <h2>Cylinders</h2>
        <p>Manage gas cylinders</p>
      </router-link>
      <router-link :to="{ name: 'DetectorsMenu', params: { district, location_label } }" class="menu-card detectors">
        <h2>Detectors</h2>
        <p>Manage gas detectors</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  district: String,
  location_label: String
})

const route = useRoute()
const district = computed(() => props.district || route.params.district)
const location_label = computed(() => props.location_label || route.params.location_label)
</script>

