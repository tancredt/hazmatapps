<template>
  <div class="main-menu-screen">
    <h1>FRV Inventory</h1>
    <p class="subtitle">District: {{ district }} | Location: {{ location_label }}</p>
    <div class="menu-grid">
      <router-link :to="{ name: 'CylindersMenu', params: { district, location_label } }" class="menu-card cylinders">
        <!-- Gas Cylinder SVG Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="card-icon-svg">
          <rect x="9" y="2" width="6" height="4" rx="1" />
          <path d="M12 2v-1" />
          <path d="M9 6h6" />
          <path d="M6 10h12v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V10z" />
          <path d="M6 10c0-2 1.5-4 3-4h6c1.5 0 3 2 3 4" />
        </svg>
        <h2>Cylinders</h2>
        <p>Manage gas cylinders</p>
      </router-link>
      <router-link :to="{ name: 'DetectorsMenu', params: { district, location_label } }" class="menu-card detectors">
        <div class="card-icon">📟</div>
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

<style scoped>
.main-menu-screen {
  padding: 40px 20px; font-family: system-ui, -apple-system, sans-serif;
  max-width: 800px; margin: 0 auto; text-align: center; color: #333;
}
h1 { font-size: 2.5rem; margin-bottom: 8px; color: #2c3e50; }
.subtitle { color: #666; font-size: 1.1rem; margin-bottom: 40px; font-weight: 500; }
.menu-grid { display: flex; gap: 30px; justify-content: center; flex-wrap: wrap; }
.menu-card {
  flex: 1; min-width: 250px; max-width: 350px; background: #ffffff;
  border: 2px solid #dee2e6; border-radius: 16px; padding: 40px 20px;
  text-decoration: none; color: #333; transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.menu-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
.menu-card.cylinders:hover { border-color: #f39c12; background: #fef9e7; }
.menu-card.detectors:hover { border-color: #42b883; background: #f0fdf4; }
.card-icon-svg { 
  width: 64px; height: 64px; margin-bottom: 15px; 
  color: #f39c12; 
}
.menu-card.cylinders:hover .card-icon-svg { color: #d35400; }
.card-icon { font-size: 4rem; margin-bottom: 15px; }
.menu-card h2 { font-size: 1.8rem; margin: 0 0 8px 0; color: #2c3e50; }
.menu-card p { color: #666; font-size: 1rem; margin: 0; }
</style>