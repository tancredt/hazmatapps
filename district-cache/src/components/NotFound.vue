<template>
  <main class="not-found-screen">
    <div class="not-found-content">
      <p class="nf-code">Error 404</p>

      <h1 class="nf-title" ref="titleRef" tabindex="-1">{{ heading }}</h1>
      <p class="nf-message">{{ message }}</p>

      <div class="nf-path">
        <span class="nf-path-label">Requested</span>
        <code>{{ attemptedPath }}</code>
      </div>

      <p v-if="missing" class="nf-hint">
        Check the spelling and try again. If it still fails, email the Hazmat Unit
        with the label and destination.
      </p>

      <nav class="nf-actions" aria-label="Recovery options">
        <router-link :to="{ name: 'Home' }" class="nf-btn nf-btn--primary">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
               stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
               aria-hidden="true" focusable="false">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
          Back to home
        </router-link>

        <router-link v-if="missing" :to="{ name: missing.retryRoute }" class="nf-btn nf-btn--ghost">
          Enter a {{ missing.kind }} label manually
        </router-link>
      </nav>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const titleRef = ref(null)

const safeDecode = (value) => {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

const attemptedPath = computed(() => route.fullPath)

// Works out whether this 404 came from an unknown detector/cylinder label.
const missing = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  const section = segments[0]
  const label = safeDecode(segments[1] || '').trim()
  if (!label) return null

  if (section === 'detector-transfer') {
    return { kind: 'detector', label, retryRoute: 'DetectorTransfer' }
  }
  if (section === 'cylinder-transfer') {
    return { kind: 'cylinder', label, retryRoute: 'CylinderTransfer' }
  }
  return null
})

const heading = computed(() => {
  if (missing.value?.kind === 'detector') return 'Detector not found'
  if (missing.value?.kind === 'cylinder') return 'Cylinder not found'
  return 'Page not found'
})

const message = computed(() => {
  if (missing.value) {
    return `No ${missing.value.kind} labelled “${missing.value.label}” exists in the database.`
  }
  return "The page you're looking for doesn't exist or may have been moved."
})

onMounted(async () => {
  await nextTick()
  titleRef.value?.focus()
})
</script>

<style scoped>
.not-found-screen {
  --green: #278257;
  --green-tint: #e8f8f2;
  --green-line: #b7e4d0;
  --accent: #42b883;
  --ink: #212529;
  --ink-2: #495057;
  --muted: #6c757d;
  --line: #dee2e6;
  --banner-h: 58px;

  display: flex;
  min-height: calc(100vh - var(--banner-h));
  min-height: calc(100dvh - var(--banner-h));
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  background: #ffffff;
  color: var(--ink);
  font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
  scrollbar-width: thin;
  scrollbar-color: #ced4da #f8f9fa;
}
.not-found-screen::-webkit-scrollbar { width: 8px; }
.not-found-screen::-webkit-scrollbar-track { background: #f8f9fa; }
.not-found-screen::-webkit-scrollbar-thumb { background: #ced4da; border-radius: 8px; }
.not-found-screen::-webkit-scrollbar-thumb:hover { background: var(--accent); }

.not-found-content {
  margin: auto;
  width: 100%;
  max-width: 520px;
  box-sizing: border-box;
  padding:
    calc(32px + env(safe-area-inset-top))
    calc(20px + env(safe-area-inset-right))
    calc(32px + env(safe-area-inset-bottom))
    calc(20px + env(safe-area-inset-left));
  text-align: center;
}

.nf-code {
  display: inline-block;
  margin: 0 0 16px;
  padding: 6px 18px;
  border-radius: 999px;
  background: var(--green-tint);
  border: 1px solid var(--green-line);
  color: #1e6a46;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.nf-title {
  margin: 0 0 12px;
  font-size: clamp(1.5rem, 5vw, 2.1rem);
  font-weight: 700;
  line-height: 1.3;
  color: var(--ink);
  text-wrap: balance;
}
.nf-title:focus { outline: none; }

.nf-message {
  margin: 0 0 20px;
  font-size: 1rem;
  line-height: 1.6;
  color: var(--ink-2);
  overflow-wrap: break-word;
}

.nf-path {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0 0 16px;
  padding: 12px 14px;
  background: #f8f9fa;
  border: 1px solid var(--line);
  border-radius: 10px;
  text-align: left;
}
.nf-path-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
.nf-path code {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
  font-size: 0.85rem;
  color: var(--ink-2);
  word-break: break-all;
}

.nf-hint {
  margin: 0 0 24px;
  font-size: 0.85rem;
  line-height: 1.55;
  color: var(--muted);
}

.nf-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.nf-btn {
  flex: 1 1 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 48px;
  min-width: 180px;
  padding: 12px 20px;
  box-sizing: border-box;
  font: inherit;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
}
.nf-btn:active { transform: scale(0.985); }
.nf-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.nf-btn--primary { background: var(--accent); border: 1px solid var(--accent); color: #fff; }
.nf-btn--primary:hover { background: #369e6f; border-color: #369e6f; }

.nf-btn--ghost { background: #fff; border: 1px solid #ced4da; color: var(--ink-2); }
.nf-btn--ghost:hover { background: #f1f3f5; border-color: var(--accent); color: #2f7d5c; }

@media (max-width: 480px) {
  .not-found-screen { --banner-h: 54px; }
  .not-found-content {
    padding-left: calc(16px + env(safe-area-inset-left));
    padding-right: calc(16px + env(safe-area-inset-right));
  }
  .nf-actions { flex-direction: column; }
  .nf-btn { width: 100%; min-width: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .nf-btn { transition: none; }
  .nf-btn:active { transform: none; }
}
</style>