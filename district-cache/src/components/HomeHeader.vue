<template>
  <div class="home-header-wrapper">
    <router-link :to="{ name: 'Home' }" class="home-btn" aria-label="Go to the home page">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
        <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
      </svg>
      <span>Home</span>
    </router-link>
  </div>
</template>

<script setup>
// Props retained for backward compatibility with existing call sites
// (e.g. <HomeHeader :district="..." :location_label="..." />).
// The Home button now always returns to the landing page.
defineProps({ district: String, location_label: String })
</script>

<style scoped>
.home-header-wrapper { margin-bottom: 10px; }
.home-btn {
  display: inline-flex; align-items: center; gap: 8px;
  min-height: 44px; padding: 8px 16px; box-sizing: border-box;
  background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px;
  color: #495057; text-decoration: none; font-size: 0.9rem; font-weight: 500;
  touch-action: manipulation; -webkit-tap-highlight-color: transparent;
  transition: all 0.2s;
}
.home-btn:hover {
  background: #e9ecef; color: #42b883; border-color: #42b883; transform: translateX(-2px);
}
.home-btn:focus-visible { outline: 2px solid #42b883; outline-offset: 2px; }
</style>