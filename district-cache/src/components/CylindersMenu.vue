<template>
  <div class="sub-menu-screen">
    <HomeHeader />
    <h1>Cylinders</h1>
    <p class="subtitle">District: {{ district }} | Location: {{ location_label }}</p>
    <div class="menu-grid">
      <router-link :to="{ name: 'CylinderEmpty', params: { district, location_label } }" class="menu-card">
        <div class="card-icon">⚠️</div>
        <h2>Report Empty</h2>
        <p>Report a cylinder as empty</p>
      </router-link>
      <router-link to="#" class="menu-card disabled" @click.prevent>
        <div class="card-icon">🔄</div>
        <h2>Swap Cylinder</h2>
        <p>Coming soon</p>
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
.sub-menu-screen { padding: 40px 20px; font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 0 auto; text-align: center; color: #333; }
h1 { font-size: 2.2rem; margin-bottom: 8px; color: #2c3e50; margin-top: 20px; }
.subtitle { color: #666; font-size: 1.1rem; margin-bottom: 40px; font-weight: 500; }
.menu-grid { display: flex; gap: 30px; justify-content: center; flex-wrap: wrap; }
.menu-card {
  flex: 1; min-width: 250px; max-width: 350px; background: #ffffff;
  border: 2px solid #dee2e6; border-radius: 16px; padding: 30px 20px;
  text-decoration: none; color: #333; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.menu-card:hover:not(.disabled) { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-color: #f39c12; background: #fef9e7; }
.menu-card.disabled { opacity: 0.5; cursor: not-allowed; background: #f8f9fa; }
.card-icon { font-size: 3rem; margin-bottom: 15px; }
.menu-card h2 { font-size: 1.5rem; margin: 0 0 8px 0; color: #2c3e50; }
.menu-card p { color: #666; font-size: 0.95rem; margin: 0; }
</style>