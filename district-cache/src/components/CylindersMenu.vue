<template>
  <div class="sub-menu-screen">
    <HomeHeader />
    <h1>Cylinders</h1>
    <p class="subtitle">District: {{ district }} | Location: {{ location_label }}</p>
    <div class="menu-grid">
      <router-link :to="{ name: 'CylinderEmpty', params: { district, location_label } }" class="menu-card">
        <h2>Report Empty</h2>
        <p>Report a cylinder as empty</p>
      </router-link>
      <router-link :to="{ name: 'CylinderSwap', params: { district, location_label } }" class="menu-card">
        <h2>Swap Cylinder</h2>
        <p>Replace an empty cylinder</p>
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

