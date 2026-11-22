<template>
  <section
    class="lookup-panel"
    :class="`lookup-panel--${state}`"
    :aria-busy="state === 'checking' ? 'true' : 'false'"
  >
    <div class="hazard-strip" aria-hidden="true"></div>

    <div class="panel-body">
      <!-- ============ CHECKING ============ -->
      <template v-if="state === 'checking'">
        <div class="check-head">
          <span class="spinner" aria-hidden="true"></span>
          <div class="check-text">
            <h3 class="panel-title">Checking this {{ kindWord }}…</h3>
            <p class="panel-sub">
              Looking up <strong>{{ displayLabel }}</strong> in the equipment register.
            </p>
          </div>
        </div>

        <div class="skeleton" aria-hidden="true">
          <span class="sk-line sk-line--wide"></span>
          <span class="sk-line"></span>
          <span class="sk-line sk-line--short"></span>
        </div>

        <p class="sr-only" role="status">
          Checking {{ kindWord }} label {{ displayLabel }} against the database.
        </p>
      </template>

      <!-- ============ 404 / UNREACHABLE ============ -->
      <template v-else>
        <header class="panel-head">
          <div class="code-block" aria-hidden="true">
            <span class="code-num">{{ isMissing ? '404' : 'ERR' }}</span>
            <span class="code-cap">{{ isMissing ? 'No record' : 'No link' }}</span>
          </div>

          <div class="head-text">
            <p class="eyebrow">
              {{ isMissing ? 'Label not in the register' : 'Register unreachable' }}
            </p>
            <h3 class="panel-title" ref="titleRef" tabindex="-1">{{ title }}</h3>
            <p class="panel-sub">{{ summary }}</p>
          </div>
        </header>

        <div class="label-echo">
          <div class="echo-text">
            <span class="echo-cap">{{ kindWord }} label</span>
            <span class="echo-value" ref="labelRef">{{ displayLabel }}</span>
          </div>
          <button
            type="button"
            class="copy-btn"
            @click="copyLabel"
            :aria-label="`Copy label ${displayLabel}`"
          >
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 aria-hidden="true" focusable="false">
              <template v-if="copyState === 'done'">
                <polyline points="20 6 9 17 4 12" />
              </template>
              <template v-else>
                <rect x="9" y="9" width="11" height="11" rx="2" />
                <path d="M5 15V5a2 2 0 0 1 2-2h10" />
              </template>
            </svg>
            <span>{{ copyLabel_text }}</span>
          </button>
        </div>

        <div class="guidance">
          <h4 class="guidance-title">{{ isMissing ? 'What to do next' : 'Before you retry' }}</h4>
          <ol class="steps">
            <li class="step" v-for="(step, i) in steps" :key="i">
              <span class="step-num" aria-hidden="true">{{ i + 1 }}</span>
              <span class="step-text">{{ step }}</span>
            </li>
          </ol>
        </div>

        <div class="panel-actions">
          <button type="button" class="p-btn p-btn--primary" @click="emit('manual')">
            <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 aria-hidden="true" focusable="false">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" />
            </svg>
            Enter label manually
          </button>

          <button
            type="button"
            class="p-btn p-btn--ghost"
            :disabled="retrying"
            @click="emit('retry')"
          >
            <svg class="refresh" :class="{ 'is-spinning': retrying }"
                 viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                 aria-hidden="true" focusable="false">
              <path d="M21 12a9 9 0 1 1-3.2-6.9" />
              <polyline points="21 3 21 9 15 9" />
            </svg>
            {{ retrying ? 'Checking…' : 'Try again' }}
          </button>

          <router-link :to="{ name: 'Home' }" class="p-btn p-btn--home">
            <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor"
                 stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                 aria-hidden="true" focusable="false">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            Back to home
          </router-link>
        </div>

        <p class="assurance">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
               aria-hidden="true" focusable="false">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          Nothing has been changed in the database.
        </p>
      </template>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  kind: { type: String, default: 'detector' },
  label: { type: String, default: '' },
  state: { type: String, default: 'missing' }, // checking | missing | error
  retrying: { type: Boolean, default: false }
})

const emit = defineEmits(['retry', 'manual'])

const titleRef = ref(null)
const labelRef = ref(null)
const copyState = ref('idle')
let copyTimer = null

const kindWord = computed(() => (props.kind === 'cylinder' ? 'cylinder' : 'detector'))
const isMissing = computed(() => props.state === 'missing')
const displayLabel = computed(() => props.label || '—')

const title = computed(() =>
  isMissing.value
    ? `${kindWord.value.charAt(0).toUpperCase()}${kindWord.value.slice(1)} not found`
    : 'Can’t reach the register'
)

const summary = computed(() =>
  isMissing.value
    ? `There is no record of this ${kindWord.value}, so its location can’t be updated.`
    : `We couldn’t check this label. The ${kindWord.value} may well exist — the check just didn’t complete.`
)

const steps = computed(() => {
  if (!isMissing.value) {
    return [
      'Check you still have network coverage — the register lives on the internal network.',
      'Wait a few seconds, then try the check again.',
      'If it keeps failing, contact the Hazmat Unit and quote the label below.'
    ]
  }
  if (props.kind === 'cylinder') {
    return [
      'Cylinder labels look like CYL00123 — the number on its own works too.',
      'Re-scan the QR code, or type the label in by hand.',
      'Still missing? Email the Hazmat Unit with the label and the destination you need.'
    ]
  }
  return [
    'Use the printed asset label, not the serial number.',
    'Re-scan the QR code, or type the label in by hand.',
    'Still missing? Email the Hazmat Unit with the label and the destination you need.'
  ]
})

const copyLabel_text = computed(() => {
  if (copyState.value === 'done') return 'Copied'
  if (copyState.value === 'fail') return 'Select & copy'
  return 'Copy'
})

const flashCopy = (state) => {
  copyState.value = state
  if (copyTimer) clearTimeout(copyTimer)
  copyTimer = setTimeout(() => { copyState.value = 'idle' }, 2200)
}

const selectLabel = () => {
  const el = labelRef.value
  if (!el || !window.getSelection) return
  const range = document.createRange()
  range.selectNodeContents(el)
  const sel = window.getSelection()
  sel.removeAllRanges()
  sel.addRange(range)
}

const copyLabel = async () => {
  const text = displayLabel.value
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      flashCopy('done')
      return
    }
    throw new Error('clipboard unavailable')
  } catch {
    const area = document.createElement('textarea')
    area.value = text
    area.setAttribute('readonly', '')
    area.style.position = 'fixed'
    area.style.opacity = '0'
    document.body.appendChild(area)
    area.select()
    let ok = false
    try { ok = document.execCommand('copy') } catch { ok = false }
    document.body.removeChild(area)
    if (ok) flashCopy('done')
    else { selectLabel(); flashCopy('fail') }
  }
}

const focusTitle = async () => {
  if (props.state === 'checking') return
  await nextTick()
  titleRef.value?.focus()
}

watch(() => props.state, focusTitle)
onMounted(focusTitle)
onUnmounted(() => { if (copyTimer) clearTimeout(copyTimer) })
</script>

<style>
/* App-wide scrollbar, drawn in the register's own palette. */
html {
  scrollbar-width: thin;
  scrollbar-color: #42b883 #f1f5f3;
}
html::-webkit-scrollbar { width: 10px; height: 10px; }
html::-webkit-scrollbar-track { background: #f1f5f3; }
html::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #42b883, #278257);
  border: 2px solid #f1f5f3;
  border-radius: 8px;
}
html::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #369e6f, #1e6a46);
}
</style>

<style scoped>
.lookup-panel {
  --navy: #003366;
  --navy-deep: #00274d;
  --green: #278257;
  --green-bright: #42b883;
  --ink: #212529;
  --ink-2: #495057;
  --muted: #6c757d;
  --line: #dee2e6;

  --tone: #c0392b;
  --tone-tint: #fdecea;
  --tone-line: #f2c9c4;
  --stripe-a: #c0392b;
  --stripe-b: #f7dcd8;

  max-width: 600px;
  margin: 0 auto;
  background: #ffffff;
  border: 1px solid var(--tone-line);
  border-radius: 14px;
  overflow: hidden;
  box-sizing: border-box;
  text-align: left;
  box-shadow:
    0 1px 2px rgba(0, 51, 102, 0.06),
    0 22px 44px -28px rgba(0, 51, 102, 0.45);
  animation: panel-in 0.34s cubic-bezier(0.2, 0.8, 0.25, 1) both;
}

.lookup-panel--error {
  --tone: #a35c00;
  --tone-tint: #fdf3e3;
  --tone-line: #f0dcb8;
  --stripe-a: #b26a00;
  --stripe-b: #f7e6c9;
}

.lookup-panel--checking {
  --tone: #278257;
  --tone-tint: #e8f8f2;
  --tone-line: #b7e4d0;
  --stripe-a: #42b883;
  --stripe-b: #dcf3e8;
}

.hazard-strip {
  height: 8px;
  background: repeating-linear-gradient(
    135deg,
    var(--stripe-a) 0 10px,
    var(--stripe-b) 10px 20px
  );
}
.lookup-panel--checking .hazard-strip {
  background-size: 28px 28px;
  animation: stripe-slide 0.9s linear infinite;
}

.panel-body { padding: 22px 22px 20px; }

/* ---------- Checking ---------- */
.check-head { display: flex; align-items: flex-start; gap: 14px; }
.check-text { min-width: 0; }
.spinner {
  flex: 0 0 auto;
  width: 26px;
  height: 26px;
  margin-top: 2px;
  border-radius: 50%;
  border: 3px solid var(--tone-line);
  border-top-color: var(--green-bright);
  animation: spin 0.75s linear infinite;
}
.skeleton { display: grid; gap: 10px; margin-top: 20px; }
.sk-line {
  height: 12px;
  width: 70%;
  border-radius: 6px;
  background: linear-gradient(90deg, #eef2f0 25%, #f8faf9 50%, #eef2f0 75%);
  background-size: 240% 100%;
  animation: shimmer 1.3s ease-in-out infinite;
}
.sk-line--wide { width: 100%; height: 40px; }
.sk-line--short { width: 45%; }

/* ---------- Head ---------- */
.panel-head {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  animation: rise 0.36s cubic-bezier(0.2, 0.8, 0.25, 1) both;
  animation-delay: 0.04s;
}

.code-block {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  gap: 3px;
  width: 100px;
  padding: 14px 8px;
  border-radius: 12px;
  border: 1px solid var(--tone-line);
  background:
    radial-gradient(120% 120% at 28% 18%, #ffffff 0%, var(--tone-tint) 62%, var(--tone-tint) 100%);
  box-shadow: inset 0 1px 0 #ffffff, 0 10px 20px -16px rgba(192, 57, 43, 0.6);
}
.code-num {
  font-size: clamp(1.9rem, 7vw, 2.4rem);
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0.01em;
  color: var(--tone);
  font-variant-numeric: tabular-nums;
}
.code-cap {
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--tone);
  opacity: 0.85;
}

.head-text { min-width: 0; }
.eyebrow {
  margin: 0 0 6px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--tone);
}
.panel-title {
  margin: 0 0 8px;
  font-size: clamp(1.2rem, 4.6vw, 1.5rem);
  font-weight: 700;
  line-height: 1.25;
  color: var(--ink);
  text-wrap: balance;
}
.panel-title:focus { outline: none; }
.panel-sub {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.55;
  color: var(--ink-2);
  overflow-wrap: break-word;
}

/* ---------- Label echo ---------- */
.label-echo {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin: 20px 0 0;
  padding: 14px 16px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--navy-deep) 0%, var(--navy) 58%, #0a4a80 100%);
  box-shadow: 0 12px 26px -18px rgba(0, 51, 102, 0.85);
  animation: rise 0.36s cubic-bezier(0.2, 0.8, 0.25, 1) both;
  animation-delay: 0.1s;
}
.label-echo::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.055) 0 1px,
    transparent 1px 9px
  );
}
.echo-text { position: relative; z-index: 1; display: grid; gap: 5px; min-width: 0; }
.echo-cap {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #93bfe0;
}
.echo-value {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
  font-size: clamp(1.05rem, 4.6vw, 1.32rem);
  font-weight: 700;
  letter-spacing: 0.13em;
  color: #ffffff;
  word-break: break-all;
}
.copy-btn {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 40px;
  padding: 8px 13px;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: #eaf4ff;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.18s ease, border-color 0.18s ease;
}
.copy-btn:hover { background: rgba(255, 255, 255, 0.22); border-color: rgba(255, 255, 255, 0.5); }
.copy-btn:focus-visible { outline: 2px solid #9fe8c6; outline-offset: 2px; }

/* ---------- Guidance ---------- */
.guidance {
  margin-top: 20px;
  animation: rise 0.36s cubic-bezier(0.2, 0.8, 0.25, 1) both;
  animation-delay: 0.16s;
}
.guidance-title {
  margin: 0 0 10px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
}
.steps {
  list-style: none;
  margin: 0;
  padding: 16px 18px;
  background: #f8f9fa;
  border: 1px solid var(--line);
  border-radius: 12px;
}
.step { position: relative; display: flex; align-items: flex-start; gap: 12px; padding: 7px 0; }
.step:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 13px;
  top: 34px;
  bottom: -7px;
  width: 2px;
  background: var(--tone-line);
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
  background: var(--tone-tint);
  border: 1px solid var(--tone-line);
  color: var(--tone);
  font-size: 0.82rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.step-text {
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--ink-2);
  padding-top: 3px;
}

/* ---------- Actions ---------- */
.panel-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 20px;
  animation: rise 0.36s cubic-bezier(0.2, 0.8, 0.25, 1) both;
  animation-delay: 0.22s;
}
.p-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 48px;
  padding: 12px 16px;
  box-sizing: border-box;
  font: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 9px;
  text-decoration: none;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, transform 0.1s ease;
}
.p-btn:active:not(:disabled) { transform: scale(0.985); }
.p-btn:focus-visible { outline: 2px solid var(--green-bright); outline-offset: 2px; }
.p-btn:disabled { cursor: not-allowed; opacity: 0.75; }

.p-btn--primary { background: var(--green-bright); border: 1px solid var(--green-bright); color: #fff; }
.p-btn--primary:hover { background: #369e6f; border-color: #369e6f; }

.p-btn--ghost { background: #fff; border: 1px solid #ced4da; color: var(--ink-2); }
.p-btn--ghost:hover:not(:disabled) { background: #f1f3f5; border-color: var(--green-bright); color: #2f7d5c; }

.p-btn--home {
  grid-column: 1 / -1;
  background: #fff;
  border: 1px solid var(--navy);
  color: var(--navy);
}
.p-btn--home:hover { background: var(--navy); color: #fff; }

.refresh.is-spinning { animation: spin 0.8s linear infinite; }

.assurance {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 14px 0 0;
  font-size: 0.78rem;
  color: var(--muted);
}

.sr-only {
  position: absolute;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

@keyframes panel-in {
  from { opacity: 0; transform: translateY(10px) scale(0.99); }
  to { opacity: 1; transform: none; }
}
@keyframes rise {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: none; }
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes stripe-slide { to { background-position: 28px 0; } }
@keyframes shimmer {
  0% { background-position: 120% 0; }
  100% { background-position: -120% 0; }
}

@media (max-width: 560px) {
  .panel-body { padding: 18px 15px 16px; }
  .panel-head { flex-direction: column; gap: 12px; }
  .code-block { width: 100%; grid-auto-flow: column; gap: 10px; padding: 10px 14px; }
  .code-num { font-size: 1.7rem; }
  .label-echo { flex-direction: column; align-items: stretch; }
  .copy-btn { justify-content: center; min-height: 44px; }
  .panel-actions { grid-template-columns: 1fr; }
  .steps { padding: 14px 14px; }
}

@media (prefers-reduced-motion: reduce) {
  .lookup-panel, .panel-head, .label-echo, .guidance, .panel-actions { animation: none; }
  .hazard-strip, .sk-line { animation: none; }
  .spinner, .refresh.is-spinning { animation-duration: 2.4s; }
  .p-btn:active:not(:disabled) { transform: none; }
}
</style>