<template>
  <div class="sub-menu-screen">
    <HomeHeader />
    <h1>Detectors</h1>
    <p class="subtitle">District: {{ district }} | Location: {{ location_label }}</p>
    <div class="menu-grid">
      <router-link :to="{ name: 'DetectorFault', params: { district, location_label } }" class="menu-card">
        <div class="card-icon">🐛</div>
        <h2>Report Fault/Missing</h2>
        <p>Log a detector issue</p>
      </router-link>
      <router-link :to="{ name: 'LocationChanger', params: { district, location_label } }" class="menu-card">
        <div class="card-icon">🔄</div>
        <h2>Swap Detector</h2>
        <p>Replace a faulty detector</p>
      </router-link>
      <router-link :to="{ name: 'Return', params: { district, location_label } }" class="menu-card">
        <div class="card-icon">📦</div>
        <h2>Return Detector</h2>
        <p>Return detectors to Burnley</p>
      </router-link>
      <router-link :to="{ name: 'Restock', params: { district, location_label } }" class="menu-card">
        <div class="card-icon">🏗️</div>
        <h2>Restock District Cache</h2>
        <p>Add detectors to cache</p>
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

<style scoped>
.sub-menu-screen { padding: 40px 20px; font-family: system-ui, -apple-system, sans-serif; max-width: 1000px; margin: 0 auto; text-align: center; color: #333; }
h1 { font-size: 2.2rem; margin-bottom: 8px; color: #2c3e50; margin-top: 20px; }
.subtitle { color: #666; font-size: 1.1rem; margin-bottom: 40px; font-weight: 500; }
.menu-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 24px; }
.menu-card {
  background: #ffffff; border: 2px solid #dee2e6; border-radius: 16px;
  padding: 30px 20px; text-decoration: none; color: #333;
  transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.menu-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-color: #42b883; background: #f0fdf4; }
.card-icon { font-size: 3rem; margin-bottom: 15px; }
.menu-card h2 { font-size: 1.4rem; margin: 0 0 8px 0; color: #2c3e50; }
.menu-card p { color: #666; font-size: 0.9rem; margin: 0; }
</style>