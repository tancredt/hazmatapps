<template>
  <main class="home-page">
    <section class="home-content">
      <svg class="home-emblem" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id="homeAu" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#FFD34D" />
            <stop offset="0.55" stop-color="#FF7A2F" />
            <stop offset="1" stop-color="#FF3B4E" />
          </linearGradient>
        </defs>
        <path d="M32 6 L54 14 V30 C54 45 44.5 54.5 32 60 C19.5 54.5 10 45 10 30 V14 Z"
          fill="rgba(11,19,34,0.85)" stroke="url(#homeAu)" stroke-width="2.5" stroke-linejoin="round" />
        <line x1="26" y1="31" x2="40" y2="24.5" stroke="rgba(200,215,238,0.6)" stroke-width="1.8" />
        <line x1="26" y1="31" x2="38.5" y2="42" stroke="rgba(200,215,238,0.6)" stroke-width="1.8" />
        <circle cx="40" cy="24.5" r="4.5" fill="#2E9BFF" stroke="rgba(255,255,255,0.35)" stroke-width="1" />
        <circle cx="38.5" cy="42" r="3.8" fill="#FFD34D" stroke="rgba(255,255,255,0.35)" stroke-width="1" />
        <circle cx="26" cy="31" r="6.5" fill="url(#homeAu)" stroke="rgba(255,255,255,0.4)" stroke-width="1" />
      </svg>

      <h1 class="home-title">
        <span class="home-welcome">Welcome to </span>
        <span class="home-name"><span class="frv">FRV</span> Gas Detection Management</span>
      </h1>

      <span class="home-rule" aria-hidden="true"></span>

      <button type="button" class="get-started" @click="getStarted">
        <span>Get Started</span>
        <svg class="btn-arrow" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
          aria-hidden="true" focusable="false">
          <path d="M5 12h14" />
          <path d="m13 6 6 6-6 6" />
        </svg>
      </button>
    </section>
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
  --ink: #060b14;
  --text: #f2f6fc;
  --text-dim: #9fb0c8;
  --gold: #ffb71b;
  --red: #ff3b4e;
  --blue: #2e9bff;

  display: flex;
  height: 100vh;
  height: 100dvh;
  overflow-y: auto;
  overflow-x: hidden;
  background:
    radial-gradient(900px 500px at 50% -10%, rgba(30, 52, 92, 0.5), transparent 65%),
    radial-gradient(700px 420px at 50% 115%, rgba(196, 0, 26, 0.18), transparent 70%),
    linear-gradient(180deg, #0b1526 0%, #060b14 60%, #0a0f1c 100%);
  color: var(--text);
  font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
  scrollbar-width: thin;
  scrollbar-color: #c4001a #0b1322;
}
.home-page::-webkit-scrollbar { width: 8px; }
.home-page::-webkit-scrollbar-track { background: #0b1322; }
.home-page::-webkit-scrollbar-thumb { background: #c4001a; border-radius: 8px; }
.home-page::-webkit-scrollbar-thumb:hover { background: #ff3b4e; }

/* margin:auto centers when there's room, stays scrollable when there isn't */
.home-content {
  margin: auto;
  width: 100%;
  max-width: 640px;
  box-sizing: border-box;
  padding:
    calc(32px + env(safe-area-inset-top))
    calc(20px + env(safe-area-inset-right))
    calc(40px + env(safe-area-inset-bottom))
    calc(20px + env(safe-area-inset-left));
  text-align: center;
}

.home-emblem {
  display: block;
  width: clamp(64px, 14vw, 88px);
  height: auto;
  margin: 0 auto 22px;
  filter: drop-shadow(0 0 18px rgba(255, 122, 47, 0.25));
  animation: fade-up 0.6s ease 0.05s both;
}

.home-title { margin: 0; }
.home-welcome {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 14px;
  animation: fade-up 0.6s ease 0.15s both;
}
.home-welcome::before,
.home-welcome::after {
  content: '';
  height: 1px;
  width: 26px;
  flex: 0 0 auto;
}
.home-welcome::before { background: linear-gradient(90deg, transparent, rgba(255, 183, 27, 0.6)); }
.home-welcome::after { background: linear-gradient(90deg, rgba(255, 183, 27, 0.6), transparent); }
.home-name {
  display: block;
  font-size: clamp(1.7rem, 5.5vw, 2.9rem);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.015em;
  text-wrap: balance;
  animation: fade-up 0.6s ease 0.25s both;
}
.frv {
  background: linear-gradient(100deg, #ffd34d 0%, #ff7a2f 55%, #ff3b4e 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
}

.home-rule {
  display: block;
  width: 72px;
  height: 3px;
  border-radius: 2px;
  margin: 20px auto 28px;
  background: linear-gradient(90deg, var(--gold), var(--red), var(--blue));
  animation: fade-up 0.6s ease 0.35s both;
}

.get-started {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 52px;
  padding: 14px 32px;
  font: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #fff;
  border-radius: 999px;
  border: 1px solid rgba(255, 183, 27, 0.45);
  background: linear-gradient(135deg, #e01230 0%, #c4001a 55%, #8f0013 100%);
  box-shadow: 0 10px 28px -8px rgba(214, 0, 28, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.18s ease, box-shadow 0.25s ease, filter 0.25s ease;
  animation: fade-up 0.6s ease 0.45s both;
}
@media (hover: hover) {
  .get-started:hover {
    transform: translateY(-2px);
    filter: brightness(1.06);
    box-shadow: 0 14px 34px -8px rgba(214, 0, 28, 0.65), 0 0 22px rgba(255, 183, 27, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
  .get-started:hover .btn-arrow { transform: translateX(3px); }
}
.get-started:active { transform: translateY(0) scale(0.97); }
.get-started:focus-visible { outline: 2px solid var(--gold); outline-offset: 4px; }
.btn-arrow { transition: transform 0.2s ease; }

@keyframes fade-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 480px) {
  .home-welcome { letter-spacing: 0.22em; gap: 10px; }
  .home-welcome::before,
  .home-welcome::after { width: 18px; }
  .get-started { width: 100%; max-width: 340px; }
}
@media (max-height: 560px) {
  .home-emblem { width: 56px; margin-bottom: 14px; }
  .home-rule { margin: 14px auto 20px; }
  .home-content { padding-top: calc(20px + env(safe-area-inset-top)); padding-bottom: calc(24px + env(safe-area-inset-bottom)); }
}

@media (prefers-reduced-motion: reduce) {
  .home-page,
  .home-page *,
  .home-page *::before,
  .home-page *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>