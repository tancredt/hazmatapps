<template>
  <main class="home-page">
    <div class="home-content">
      <h1 class="home-title">Welcome to FRV Gas Detection Management</h1>

      <p class="home-intro">Record an equipment move in four steps:</p>

      <ol class="steps">
        <li class="step">
          <span class="step-num" aria-hidden="true">1</span>
          <span class="step-text">Input Label</span>
        </li>
        <li class="step">
          <span class="step-num" aria-hidden="true">2</span>
          <span class="step-text">Select Destination</span>
        </li>
        <li class="step">
          <span class="step-num" aria-hidden="true">3</span>
          <span class="step-text">
            Choose Specific Location
            <span class="step-note">(if required)</span>
          </span>
        </li>
        <li class="step">
          <span class="step-num" aria-hidden="true">4</span>
          <span class="step-text">Submit</span>
        </li>
      </ol>

      <nav class="choice-bar" aria-label="Choose equipment type">
        <router-link :to="{ name: 'DetectorTransfer' }" class="choice-btn choice-btn--detector">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
            <rect x="7" y="3" width="10" height="18" rx="2.5" />
            <rect x="9.5" y="6" width="5" height="4" rx="1" />
            <path d="M10 14h4M10 17h2.5" />
          </svg>
          Detectors
        </router-link>

        <router-link :to="{ name: 'CylinderTransfer' }" class="choice-btn choice-btn--cylinder">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
            <path d="M10.5 2.5h3M12 2.5v3" />
            <path d="M8 9a4 4 0 0 1 8 0v10.5a1.5 1.5 0 0 1-1.5 1.5h-5A1.5 1.5 0 0 1 8 19.5z" />
            <path d="M8 12.5h8M8 16h8" />
          </svg>
          Cylinders
        </router-link>
      </nav>
    </div>
  </main>
</template>

<script setup>
// Both destinations are plain router links — no script logic required.
</script>

<style scoped>
.home-page {
  --navy: #003366;
  --navy-dark: #00274d;
  --green: #278257;
  --green-dark: #1e6a46;
  --green-tint: #e8f8f2;
  --green-line: #b7e4d0;
  --ink: #212529;
  --ink-2: #495057;
  --muted: #6c757d;
  --line: #dee2e6;
  --banner-h: 58px;

  display: flex;
  height: calc(100vh - var(--banner-h));
  height: calc(100dvh - var(--banner-h));
  overflow-y: auto;
  overflow-x: hidden;
  background: #ffffff;
  color: var(--ink);
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
  max-width: 520px;
  box-sizing: border-box;
  padding:
    calc(32px + env(safe-area-inset-top))
    calc(20px + env(safe-area-inset-right))
    calc(32px + env(safe-area-inset-bottom))
    calc(20px + env(safe-area-inset-left));
  text-align: center;
}

.home-title {
  margin: 0 0 12px;
  font-size: clamp(1.5rem, 5vw, 2.1rem);
  font-weight: 700;
  line-height: 1.3;
  color: var(--ink);
  text-wrap: balance;
}

.home-intro {
  margin: 0 0 20px;
  font-size: 0.95rem;
  color: var(--muted);
}

/* ---------- Steps ---------- */
.steps {
  list-style: none;
  margin: 0 auto 28px;
  padding: 20px 22px;
  max-width: 380px;
  box-sizing: border-box;
  background: #f8f9fa;
  border: 1px solid var(--line);
  border-radius: 12px;
  text-align: left;
}
.step {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 0;
}
/* connector between the numbered badges */
.step:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 13px;
  top: 34px;
  bottom: -7px;
  width: 2px;
  background: var(--green-line);
}
.step-num {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--green-tint);
  border: 1px solid var(--green-line);
  color: var(--green);
  font-size: 0.85rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.step-text {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink-2);
  line-height: 1.4;
}
.step-note {
  font-weight: 400;
  font-style: italic;
  color: var(--muted);
  white-space: nowrap;
}

/* ---------- Buttons ---------- */
.choice-bar {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.choice-btn {
  flex: 1 1 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 52px;
  padding: 12px 20px;
  box-sizing: border-box;
  font: inherit;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
}
.choice-btn:active { transform: scale(0.985); }
.choice-btn:focus-visible { outline: 2px solid #42b883; outline-offset: 2px; }

.choice-btn--detector { background: var(--green); border: 1px solid var(--green); }
.choice-btn--detector:hover { background: var(--green-dark); border-color: var(--green-dark); }

.choice-btn--cylinder { background: var(--navy); border: 1px solid var(--navy); }
.choice-btn--cylinder:hover { background: var(--navy-dark); border-color: var(--navy-dark); }

@media (max-width: 480px) {
  .home-page { --banner-h: 54px; }
  .home-content {
    padding-left: calc(16px + env(safe-area-inset-left));
    padding-right: calc(16px + env(safe-area-inset-right));
  }
  .steps { padding: 16px 18px; margin-bottom: 24px; }
  .choice-bar { flex-direction: column; }
  .choice-btn { width: 100%; min-height: 50px; }
}

@media (prefers-reduced-motion: reduce) {
  .choice-btn { transition: none; }
  .choice-btn:active { transform: none; }
}
</style>