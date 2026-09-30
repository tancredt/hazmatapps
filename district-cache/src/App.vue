<template>
  <div id="app">
    <!-- GLOBAL FRV BANNER (Forced to show everywhere) -->
    <header class="frv-banner">
      Fire Rescue Victoria
    </header>
    
    <!-- ALL ROUTED PAGES LOAD HERE -->
    <router-view />
  </div>
</template>

<script setup>
// No conditional logic needed. It will always render.
</script>

<style>
/* Global styles (no 'scoped' attribute so it applies to the whole app) */
.frv-banner {
  background-color: #003366; /* FRV Deep Navy Blue */
  color: #ffffff;
  text-align: center;
  padding: 14px 0;
  font-size: 1.25rem;
  font-weight: 700;
  font-family: system-ui, -apple-system, sans-serif;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  
  /* Sticky positioning ensures it stays at the top when scrolling */
  position: sticky; 
  top: 0; 
  z-index: 9999; /* Extremely high to ensure it sits above all other elements */
  width: 100%;
}

/* Reset default browser margins to prevent white gaps */
body, html {
  margin: 0;
  padding: 0;
}
</style>