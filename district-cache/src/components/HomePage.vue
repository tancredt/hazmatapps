<template>
  <main class="home-page">
    <div class="home-content">
      <h1 class="home-title">Welcome to FRV Gas Detection Management</h1>
      <button type="button" class="get-started" @click="getStarted">Get Started</button>
    </div>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const getStarted = () => {
  router.push({ name: 'DetectorTransfer' })
}
</script>

<style scoped>
.home-page {
  display: flex;
  height: 100vh;
  height: 100dvh;
  overflow-y: auto;
  overflow-x: hidden;
  background: #ffffff;
  color: #212529;
  font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
  scrollbar-width: thin;
  scrollbar-color: #ced4da #f8f9fa;
}
.home-page::-webkit-scrollbar { width: 8px; }
.home-page::-webkit-scrollbar-track { background: #f8f9fa; }
.home-page::-webkit-scrollbar-thumb { background: #ced4da; border-radius: 8px; }
.home-page::-webkit-scrollbar-thumb:hover { background: #42b883; }

/* margin:auto centers when there's room, stays scrollable on short screens */
.home-content {
  margin: auto;
  width: 100%;
  max-width: 640px;
  box-sizing: border-box;
  padding:
    calc(32px + env(safe-area-inset-top))
    calc(20px + env(safe-area-inset-right))
    calc(32px + env(safe-area-inset-bottom))
    calc(20px + env(safe-area-inset-left));
  text-align: center;
}

.home-title {
  margin: 0 0 28px;
  font-size: clamp(1.5rem, 5vw, 2.25rem);
  font-weight: 700;
  line-height: 1.3;
  color: #212529;
  text-wrap: balance;
}

.get-started {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 28px;
  font: inherit;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: #278257;
  border: 1px solid #278257;
  border-radius: 8px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}
.get-started:hover { background: #1e6a46; border-color: #1e6a46; }
.get-started:active { background: #185a3b; border-color: #185a3b; }
.get-started:focus-visible { outline: 2px solid #42b883; outline-offset: 2px; }

@media (max-width: 480px) {
  .home-content {
    padding-left: calc(16px + env(safe-area-inset-left));
    padding-right: calc(16px + env(safe-area-inset-right));
  }
  .home-title { margin-bottom: 24px; }
  .get-started { width: 100%; max-width: 320px; }
}
</style>