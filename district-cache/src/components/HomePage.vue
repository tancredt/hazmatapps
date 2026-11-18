<template>
  <main class="home-page">
    <!-- Ambient depth layers -->
    <div class="ambient" aria-hidden="true">
      <span class="orb orb--teal"></span>
      <span class="orb orb--amber"></span>
      <span class="orb orb--navy"></span>
      <span class="mesh"></span>
      <span class="grain"></span>
    </div>

    <div class="home-content">
      <p class="eyebrow reveal" style="--d: 0ms">
        <span class="eyebrow-dot"></span>
        Fire Rescue Victoria · Technical Services
      </p>

      <h1 class="home-title reveal" style="--d: 70ms">
        What are you <span class="title-accent">moving</span>?
      </h1>

      <p class="home-sub reveal" style="--d: 140ms">
        Record a location change for a single piece of equipment. Choose the type to
        begin — the destination, status and movement log are written together.
      </p>

      <div class="choice-grid">
        <!-- ============ DETECTORS ============ -->
        <router-link
          :to="{ name: 'DetectorTransfer' }"
          class="choice choice--detector reveal"
          :class="{ 'is-keyed': flash === 'detectors' }"
          style="--d: 210ms"
          aria-label="Transfer a detector"
          @pointermove="trackGlow"
          @pointerleave="clearGlow"
        >
          <span class="choice-wash" aria-hidden="true"></span>
          <span class="choice-spot" aria-hidden="true"></span>

          <span class="choice-top">
            <span class="choice-icon">
              <svg viewBox="0 0 64 64" width="38" height="38" fill="none" aria-hidden="true" focusable="false">
                <rect x="17" y="7" width="30" height="50" rx="7" stroke="currentColor" stroke-width="2.6"/>
                <path d="M27 7V4.5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2V7" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>
                <rect x="22" y="13" width="20" height="14" rx="3" fill="currentColor" opacity=".14"/>
                <rect x="22" y="13" width="20" height="14" rx="3" stroke="currentColor" stroke-width="2"/>
                <path class="readout" d="M25.5 23.5h4l2-5 2.5 7 2-4h3" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="26" cy="34" r="2.4" fill="currentColor"/>
                <circle cx="32" cy="34" r="2.4" fill="currentColor" opacity=".55"/>
                <circle cx="38" cy="34" r="2.4" fill="currentColor" opacity=".55"/>
                <rect x="23" y="41" width="18" height="11" rx="3" stroke="currentColor" stroke-width="2"/>
                <path d="M27 44.5v4M32 44.5v4M37 44.5v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" opacity=".7"/>
                <path d="M47 20h4a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-4" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".55"/>
              </svg>
            </span>
            <span class="choice-key" aria-hidden="true"><kbd>1</kbd></span>
          </span>

          <span class="choice-text">
            <span class="choice-title">Detectors</span>
            <span class="choice-desc">
              Multigas detectors, PIDs, survey meters and laptops — sent to a fire
              station, a district cache, or Burnley for repair and calibration.
            </span>
          </span>

          <span class="choice-tags">
            <span class="tag">Fire station</span>
            <span class="tag">District cache</span>
            <span class="tag tag--warn">Burnley</span>
          </span>

          <span class="choice-cta">
            Transfer a detector
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
              <path d="M5 12h13"/><path d="m12 5 7 7-7 7"/>
            </svg>
          </span>
        </router-link>

        <!-- ============ CYLINDERS ============ -->
        <router-link
          :to="{ name: 'CylinderTransfer' }"
          class="choice choice--cylinder reveal"
          :class="{ 'is-keyed': flash === 'cylinders' }"
          style="--d: 290ms"
          aria-label="Transfer a cylinder"
          @pointermove="trackGlow"
          @pointerleave="clearGlow"
        >
          <span class="choice-wash" aria-hidden="true"></span>
          <span class="choice-spot" aria-hidden="true"></span>

          <span class="choice-top">
            <span class="choice-icon">
              <svg viewBox="0 0 64 64" width="38" height="38" fill="none" aria-hidden="true" focusable="false">
                <circle cx="32" cy="7" r="4.2" stroke="currentColor" stroke-width="2.4"/>
                <path d="M32 11.2v4.3" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>
                <path d="M26.5 15.5h11" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>
                <path d="M20 27c0-6.4 5.4-11.5 12-11.5S44 20.6 44 27v25a5 5 0 0 1-5 5H25a5 5 0 0 1-5-5z" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/>
                <path d="M20 33h24v11H20z" fill="currentColor" opacity=".14"/>
                <path class="band" d="M20 33h24M20 44h24" stroke="currentColor" stroke-width="2"/>
                <path d="M25 37.5h9M25 40.5h5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" opacity=".75"/>
                <path d="M25.5 24.5c1.4-2.6 3.6-4 6.5-4.2" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity=".45"/>
                <path d="M24 51h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity=".35"/>
              </svg>
            </span>
            <span class="choice-key" aria-hidden="true"><kbd>2</kbd></span>
          </span>

          <span class="choice-text">
            <span class="choice-title">Cylinders</span>
            <span class="choice-desc">
              Calibration and bump-test gas — placed on a fire station appliance or
              returned to a district cache as stock.
            </span>
          </span>

          <span class="choice-tags">
            <span class="tag">Fire station</span>
            <span class="tag">District cache</span>
          </span>

          <span class="choice-cta">
            Transfer a cylinder
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
              <path d="M5 12h13"/><path d="m12 5 7 7-7 7"/>
            </svg>
          </span>
        </router-link>
      </div>

      <div class="home-foot reveal" style="--d: 370ms">
        <p class="foot-note">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
            <path d="M12 2 4 5.5v6c0 5 3.4 9.2 8 10.5 4.6-1.3 8-5.5 8-10.5v-6z"/>
            <path d="m9 12 2 2 4-4"/>
          </svg>
          Every move is timestamped and written to the equipment location log.
        </p>
        <p class="foot-keys">
          Shortcut <kbd>1</kbd> detectors <span class="dot-sep">·</span> <kbd>2</kbd> cylinders
        </p>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const flash = ref('')
let flashTimer = null

const go = (name) => {
  router.push({ name }).catch(() => {})
}

const press = (which, name) => {
  flash.value = which
  clearTimeout(flashTimer)
  flashTimer = setTimeout(() => { flash.value = '' }, 200)
  go(name)
}

const onKeydown = (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey || event.repeat) return
  const el = event.target
  if (el && (el.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName))) return

  if (event.key === '1') {
    event.preventDefault()
    press('detectors', 'DetectorTransfer')
  } else if (event.key === '2') {
    event.preventDefault()
    press('cylinders', 'CylinderTransfer')
  }
}

// Pointer-tracked highlight on each card
const trackGlow = (event) => {
  const card = event.currentTarget
  const rect = card.getBoundingClientRect()
  card.style.setProperty('--mx', `${((event.clientX - rect.left) / rect.width) * 100}%`)
  card.style.setProperty('--my', `${((event.clientY - rect.top) / rect.height) * 100}%`)
}

const clearGlow = (event) => {
  event.currentTarget.style.removeProperty('--mx')
  event.currentTarget.style.removeProperty('--my')
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  clearTimeout(flashTimer)
})
</script>

<style scoped>
.home-page {
  /* --- Palette: FRV navy field, detector teal/green, cylinder amber/ember --- */
  --navy: #003366;
  --navy-deep: #001f3f;
  --navy-tint: #e6edf5;

  --teal: #0f766e;
  --green: #42b883;
  --green-deep: #278257;
  --green-tint: #e8f8f2;

  --amber: #f59e0b;
  --amber-deep: #b45309;
  --ember: #ea580c;
  --amber-tint: #fdf1de;

  --red: #e11d48;
  --blue: #2563eb;

  --ink: #0d1f33;
  --ink-2: #33506e;
  --muted: #64748b;
  --bg: #f4f7fb;
  --surface: #ffffff;
  --surface-2: #f8fafc;
  --line: #dce5ef;

  --ease: cubic-bezier(.16, 1, .3, 1);
  --banner-h: 58px;

  position: relative;
  display: flex;
  min-height: calc(100vh - var(--banner-h));
  min-height: calc(100dvh - var(--banner-h));
  overflow: hidden;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* ============ AMBIENT LAYERS ============ */
.ambient { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: .55;
  will-change: transform;
}
.orb--teal {
  width: 46vmax; height: 46vmax; top: -18vmax; left: -12vmax;
  background: radial-gradient(circle at 40% 40%, rgba(66, 184, 131, .55), rgba(15, 118, 110, .22) 55%, transparent 72%);
  animation: driftA 26s var(--ease) infinite alternate;
}
.orb--amber {
  width: 40vmax; height: 40vmax; bottom: -16vmax; right: -10vmax;
  background: radial-gradient(circle at 55% 45%, rgba(245, 158, 11, .45), rgba(234, 88, 12, .18) 55%, transparent 72%);
  animation: driftB 31s var(--ease) infinite alternate;
}
.orb--navy {
  width: 34vmax; height: 34vmax; top: 30%; right: 22%;
  background: radial-gradient(circle at 50% 50%, rgba(37, 99, 235, .22), rgba(0, 51, 102, .14) 58%, transparent 74%);
  animation: driftC 37s var(--ease) infinite alternate;
}
@keyframes driftA { to { transform: translate3d(6%, 5%, 0) scale(1.1); } }
@keyframes driftB { to { transform: translate3d(-7%, -4%, 0) scale(1.08); } }
@keyframes driftC { to { transform: translate3d(-5%, 7%, 0) scale(1.14); } }

.mesh {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(to right, rgba(0, 51, 102, .055) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 51, 102, .055) 1px, transparent 1px);
  background-size: 62px 62px;
  -webkit-mask-image: radial-gradient(ellipse 78% 68% at 50% 42%, #000 30%, transparent 78%);
  mask-image: radial-gradient(ellipse 78% 68% at 50% 42%, #000 30%, transparent 78%);
}

.grain {
  position: absolute; inset: 0; opacity: .35; mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.16'/%3E%3C/svg%3E");
}

/* ============ CONTENT ============ */
.home-content {
  position: relative;
  margin: auto;
  width: 100%;
  max-width: 940px;
  box-sizing: border-box;
  padding:
    calc(40px + env(safe-area-inset-top))
    calc(24px + env(safe-area-inset-right))
    calc(40px + env(safe-area-inset-bottom))
    calc(24px + env(safe-area-inset-left));
  text-align: center;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  margin: 0 0 18px;
  padding: 6px 14px 6px 11px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: 0 1px 2px rgba(13, 31, 51, .05);
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: .13em;
  text-transform: uppercase;
  color: var(--navy);
}
.eyebrow-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--red);
  box-shadow: 0 0 0 3px rgba(225, 29, 72, .16);
  animation: beacon 2.6s ease-in-out infinite;
}
@keyframes beacon {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 3px rgba(225, 29, 72, .16); }
  50% { opacity: .55; box-shadow: 0 0 0 6px rgba(225, 29, 72, .05); }
}

.home-title {
  margin: 0 0 14px;
  font-size: clamp(2.1rem, 6.4vw, 3.4rem);
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: -.025em;
  color: var(--navy-deep);
  text-wrap: balance;
}
.title-accent {
  background: linear-gradient(100deg, var(--teal) 0%, var(--green-deep) 42%, var(--amber-deep) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: var(--green-deep);
}

.home-sub {
  margin: 0 auto 34px;
  max-width: 56ch;
  font-size: clamp(.95rem, 2.4vw, 1.06rem);
  line-height: 1.6;
  color: var(--ink-2);
  text-wrap: pretty;
}

/* ============ CHOICE CARDS ============ */
.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  text-align: left;
}

.choice {
  --accent: var(--green-deep);
  --accent-2: var(--teal);
  --accent-tint: var(--green-tint);
  --mx: 50%;
  --my: 0%;

  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 26px 24px 22px;
  min-height: 316px;
  box-sizing: border-box;
  overflow: hidden;
  isolation: isolate;

  background: var(--surface);
  border: 1.5px solid var(--line);
  border-radius: 18px;
  text-decoration: none;
  color: var(--ink);
  box-shadow: 0 1px 2px rgba(13, 31, 51, .05), 0 10px 26px -18px rgba(13, 31, 51, .35);
  transition: transform .32s var(--ease), border-color .28s ease, box-shadow .32s var(--ease);
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
.choice--cylinder {
  --accent: var(--amber-deep);
  --accent-2: var(--ember);
  --accent-tint: var(--amber-tint);
}

.choice-wash {
  position: absolute; inset: 0; z-index: -2;
  background: linear-gradient(155deg, var(--accent-tint) 0%, rgba(255, 255, 255, 0) 58%);
  opacity: .7;
  transition: opacity .32s ease;
}
.choice-spot {
  position: absolute; inset: 0; z-index: -1;
  background: radial-gradient(340px circle at var(--mx) var(--my), color-mix(in srgb, var(--accent) 16%, transparent), transparent 62%);
  opacity: 0;
  transition: opacity .3s ease;
}
.choice::after {
  content: '';
  position: absolute; left: 0; right: 0; top: 0; height: 3px;
  background: linear-gradient(90deg, var(--accent-2), var(--accent), var(--accent-2));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform .42s var(--ease);
}

.choice:hover,
.choice:focus-visible,
.choice.is-keyed {
  transform: translateY(-6px);
  border-color: color-mix(in srgb, var(--accent) 52%, var(--line));
  box-shadow: 0 2px 4px rgba(13, 31, 51, .06), 0 26px 46px -26px color-mix(in srgb, var(--accent) 60%, transparent);
}
.choice:hover .choice-wash,
.choice:focus-visible .choice-wash { opacity: 1; }
.choice:hover .choice-spot,
.choice:focus-visible .choice-spot { opacity: 1; }
.choice:hover::after,
.choice:focus-visible::after,
.choice.is-keyed::after { transform: scaleX(1); }
.choice:active,
.choice.is-keyed { transform: translateY(-2px) scale(.994); }
.choice:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }

.choice-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.choice-icon {
  display: grid;
  place-items: center;
  width: 66px; height: 66px;
  flex: 0 0 auto;
  border-radius: 16px;
  color: var(--accent);
  background: linear-gradient(150deg, var(--accent-tint), #ffffff);
  border: 1.5px solid color-mix(in srgb, var(--accent) 26%, transparent);
  box-shadow: inset 0 -8px 18px -14px color-mix(in srgb, var(--accent) 90%, transparent);
  transition: transform .42s var(--ease), box-shadow .32s ease;
}
.choice:hover .choice-icon,
.choice:focus-visible .choice-icon {
  transform: translateY(-2px) rotate(-4deg) scale(1.05);
  box-shadow: inset 0 -8px 18px -12px color-mix(in srgb, var(--accent) 90%, transparent),
              0 12px 22px -14px color-mix(in srgb, var(--accent) 85%, transparent);
}
.readout { animation: trace 3.4s ease-in-out infinite; }
@keyframes trace { 0%, 100% { opacity: .45; } 45% { opacity: 1; } }
.choice--cylinder .band { transition: opacity .3s ease; opacity: .8; }
.choice--cylinder:hover .band { opacity: 1; }

.choice-key kbd {
  display: grid;
  place-items: center;
  min-width: 26px; height: 26px;
  padding: 0 7px;
  font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
  font-size: .76rem;
  font-weight: 700;
  color: var(--muted);
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-bottom-width: 2px;
  border-radius: 7px;
  transition: color .24s ease, border-color .24s ease, background .24s ease;
}
.choice:hover .choice-key kbd,
.choice:focus-visible .choice-key kbd,
.choice.is-keyed .choice-key kbd {
  color: var(--accent);
  background: var(--accent-tint);
  border-color: color-mix(in srgb, var(--accent) 40%, transparent);
}

.choice-text { display: block; }
.choice-title {
  display: block;
  margin-bottom: 8px;
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -.015em;
  color: var(--navy-deep);
}
.choice-desc {
  display: block;
  font-size: .92rem;
  line-height: 1.58;
  color: var(--ink-2);
}

.choice-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: auto;
  padding-top: 4px;
}
.tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .045em;
  text-transform: uppercase;
  color: var(--accent);
  background: var(--accent-tint);
  border: 1px solid color-mix(in srgb, var(--accent) 24%, transparent);
}
.tag--warn {
  color: var(--red);
  background: #fdeef2;
  border-color: rgba(225, 29, 72, .22);
}

.choice-cta {
  display: flex;
  align-items: center;
  gap: 9px;
  padding-top: 15px;
  border-top: 1px dashed var(--line);
  font-size: .95rem;
  font-weight: 700;
  color: var(--accent);
}
.choice-cta svg { transition: transform .34s var(--ease); }
.choice:hover .choice-cta svg,
.choice:focus-visible .choice-cta svg { transform: translateX(6px); }

/* ============ FOOTER ============ */
.home-foot {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px 22px;
  margin-top: 30px;
  font-size: .82rem;
  color: var(--muted);
}
.foot-note {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}
.foot-note svg { color: var(--green-deep); flex: 0 0 auto; }
.foot-keys { display: inline-flex; align-items: center; gap: 7px; margin: 0; }
.foot-keys kbd {
  display: inline-grid;
  place-items: center;
  min-width: 22px; height: 22px;
  padding: 0 6px;
  font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
  font-size: .72rem;
  font-weight: 700;
  color: var(--navy);
  background: var(--surface);
  border: 1px solid var(--line);
  border-bottom-width: 2px;
  border-radius: 6px;
}
.dot-sep { color: var(--line); }

/* ============ ENTRANCE ============ */
.reveal {
  animation: rise .62s var(--ease) both;
  animation-delay: var(--d, 0ms);
}
@keyframes rise {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: none; }
}

/* ============ RESPONSIVE ============ */
@media (max-width: 860px) {
  .choice-grid { grid-template-columns: 1fr; gap: 16px; }
  .choice { min-height: 0; padding: 22px 20px 18px; }
  .choice-title { font-size: 1.45rem; }
}

@media (max-width: 480px) {
  .home-page { --banner-h: 54px; }
  .home-content {
    padding:
      calc(26px + env(safe-area-inset-top))
      calc(16px + env(safe-area-inset-right))
      calc(30px + env(safe-area-inset-bottom))
      calc(16px + env(safe-area-inset-left));
  }
  .eyebrow { font-size: .64rem; letter-spacing: .1em; margin-bottom: 14px; }
  .home-sub { margin-bottom: 24px; }
  .choice-icon { width: 56px; height: 56px; border-radius: 14px; }
  .choice-icon svg { width: 32px; height: 32px; }
  .choice-desc { font-size: .88rem; }
  .home-foot { margin-top: 22px; flex-direction: column; gap: 10px; }
}

@media (hover: none) {
  .choice-key, .foot-keys { display: none; }
  .choice-spot { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .orb, .eyebrow-dot, .readout { animation: none !important; }
  .reveal { animation: none !important; }
  .choice, .choice-icon, .choice-cta svg, .choice::after { transition-duration: .01ms !important; }
  .choice:hover, .choice:focus-visible { transform: none; }
}
</style>

<style>
/* Page scrollbar in the app's own palette */
html {
  scrollbar-width: thin;
  scrollbar-color: #b9c7d8 #eef2f7;
}
body::-webkit-scrollbar { width: 12px; height: 12px; }
body::-webkit-scrollbar-track { background: #eef2f7; }
body::-webkit-scrollbar-thumb {
  background: #b9c7d8;
  border: 3px solid #eef2f7;
  border-radius: 999px;
}
body::-webkit-scrollbar-thumb:hover { background: #42b883; }
body::-webkit-scrollbar-corner { background: transparent; }
</style>