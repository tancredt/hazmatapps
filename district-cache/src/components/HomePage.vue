<template>
  <main ref="pageEl" class="home-page" :class="{ 'is-launching': isLaunching }">
    <!-- ===== Ambient layered background ===== -->
    <div class="bg-base" aria-hidden="true"></div>
    <div class="bg-aurora" aria-hidden="true">
      <span class="blob blob-red"></span>
      <span class="blob blob-blue"></span>
      <span class="blob blob-gold"></span>
    </div>
    <div class="bg-grid" aria-hidden="true"></div>
    <div class="bg-particles" aria-hidden="true">
      <span v-for="p in particles" :key="p.id" class="particle" :style="p.style"></span>
    </div>
    <div class="bg-scanline" aria-hidden="true"></div>
    <div class="bg-vignette" aria-hidden="true"></div>

    <!-- ===== Live sensor trace (decorative) ===== -->
    <div class="trace" aria-hidden="true">
      <svg class="trace-svg trace-back" viewBox="0 0 2400 80" preserveAspectRatio="none">
        <path :d="traceBack" fill="none" stroke="rgba(46,155,255,0.35)" stroke-width="1.4" />
      </svg>
      <svg class="trace-svg trace-front" viewBox="0 0 2400 80" preserveAspectRatio="none">
        <defs>
          <linearGradient id="traceFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="rgba(53,224,140,0.22)" />
            <stop offset="1" stop-color="rgba(53,224,140,0)" />
          </linearGradient>
        </defs>
        <path :d="traceFrontArea" fill="url(#traceFill)" stroke="none" />
        <path :d="traceFront" fill="none" stroke="rgba(53,224,140,0.6)" stroke-width="1.6" />
      </svg>
    </div>

    <!-- ===== HUD corner frame ===== -->
    <div class="hud" aria-hidden="true">
      <span class="corner corner-tl"></span>
      <span class="corner corner-tr"></span>
      <span class="corner corner-bl"></span>
      <span class="corner corner-br"></span>
    </div>

    <!-- ===== Content ===== -->
    <div class="frame">
      <section class="stage">
        <div class="emblem-parallax">
          <div class="emblem-wrap">
            <svg class="emblem" viewBox="0 0 160 160" aria-hidden="true" focusable="false">
              <defs>
                <linearGradient id="frvAu" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stop-color="#FFD34D" />
                  <stop offset="0.55" stop-color="#FF7A2F" />
                  <stop offset="1" stop-color="#FF3B4E" />
                </linearGradient>
                <radialGradient id="frvCore" cx="0.5" cy="0.5" r="0.5">
                  <stop offset="0" stop-color="rgba(46,155,255,0.28)" />
                  <stop offset="0.7" stop-color="rgba(46,155,255,0.08)" />
                  <stop offset="1" stop-color="rgba(46,155,255,0)" />
                </radialGradient>
                <linearGradient id="frvSweep" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stop-color="rgba(46,155,255,0)" />
                  <stop offset="1" stop-color="rgba(46,155,255,0.45)" />
                </linearGradient>
              </defs>

              <circle cx="80" cy="80" r="78" fill="none" stroke="rgba(46,155,255,0.12)" stroke-width="1" />
              <circle class="ticks" cx="80" cy="80" r="74" fill="none" stroke="rgba(159,176,200,0.35)"
                stroke-width="2" stroke-dasharray="1.5 7" />
              <circle cx="80" cy="80" r="63" fill="none" stroke="rgba(255,183,27,0.28)" stroke-width="1" />

              <circle class="pulse p1" cx="80" cy="80" r="52" fill="none" stroke="rgba(46,155,255,0.5)" stroke-width="1.5" />
              <circle class="pulse p2" cx="80" cy="80" r="52" fill="none" stroke="rgba(255,77,94,0.45)" stroke-width="1.5" />

              <g class="sweep">
                <path d="M80 80 L80 17 A63 63 0 0 1 112 25.5 Z" fill="url(#frvSweep)" />
                <line x1="80" y1="80" x2="80" y2="17" stroke="rgba(46,155,255,0.7)" stroke-width="1.5" />
              </g>

              <circle cx="80" cy="80" r="42" fill="url(#frvCore)" />

              <path class="shield"
                d="M80 42 L107 51.5 V71 C107 89.5 96.5 101 80 108.5 C63.5 101 53 89.5 53 71 V51.5 Z"
                fill="rgba(9,15,28,0.9)" stroke="url(#frvAu)" stroke-width="2.5" stroke-linejoin="round" />

              <g class="molecule">
                <line x1="73" y1="75" x2="89" y2="67.5" stroke="rgba(200,215,238,0.55)" stroke-width="1.6" />
                <line x1="73" y1="75" x2="87.5" y2="88" stroke="rgba(200,215,238,0.55)" stroke-width="1.6" />
                <circle cx="89" cy="67.5" r="5" fill="#2E9BFF" stroke="rgba(255,255,255,0.35)" stroke-width="1" />
                <circle cx="87.5" cy="88" r="4.2" fill="#FFD34D" stroke="rgba(255,255,255,0.35)" stroke-width="1" />
                <circle cx="73" cy="75" r="7.2" fill="url(#frvAu)" stroke="rgba(255,255,255,0.4)" stroke-width="1" />
              </g>

              <circle class="led" cx="80" cy="121" r="3" fill="#35E08C" />
            </svg>
          </div>
        </div>

        <h1 class="headline">
          <span class="headline-welcome">Welcome to </span>
          <span class="headline-title"><span class="frv">FRV</span> Gas Detection Management</span>
        </h1>

        <span class="headline-rule" aria-hidden="true"></span>

        <div class="cta">
          <span class="cta-ring" aria-hidden="true"></span>
          <button type="button" class="get-started" :disabled="isLaunching" @click="handleGetStarted">
            <span class="btn-label">Get Started</span>
            <svg class="btn-arrow" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
              aria-hidden="true" focusable="false">
              <path d="M5 12h14" />
              <path d="m13 6 6 6-6 6" />
            </svg>
          </button>
        </div>
      </section>
    </div>

    <div class="bg-grain" aria-hidden="true"></div>
    <div class="launch-veil" aria-hidden="true"></div>
  </main>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- State ---
const pageEl = ref(null)
const isLaunching = ref(false)
const particles = ref([])
const traceFront = ref('')
const traceFrontArea = ref('')
const traceBack = ref('')

let launchTimer = null
let rafId = 0
let targetX = 0, targetY = 0, curX = 0, curY = 0
let prefersReduced = false
let motionOK = false
let mediaReduce = null
let mediaFine = null

// --- Helpers ---
const rand = (min, max) => min + Math.random() * (max - min)
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)]

const PARTICLE_COLORS = [
  'rgba(140, 175, 230, 0.65)',
  'rgba(140, 175, 230, 0.65)',
  'rgba(140, 175, 230, 0.65)',
  'rgba(255, 183, 27, 0.6)',
  'rgba(255, 77, 94, 0.55)',
  'rgba(53, 224, 140, 0.5)'
]

// --- Drifting gas molecules ---
function seedParticles() {
  const count = window.innerWidth < 640 ? 14 : 26
  particles.value = Array.from({ length: count }, (_, i) => {
    const size = rand(2, 6)
    const duration = rand(16, 34)
    return {
      id: i,
      style: {
        left: `${rand(0, 100).toFixed(2)}%`,
        width: `${size.toFixed(1)}px`,
        height: `${size.toFixed(1)}px`,
        background: pick(PARTICLE_COLORS),
        filter: size > 4.5 ? 'blur(1px)' : 'none',
        animationDuration: `${duration.toFixed(2)}s`,
        animationDelay: `${(-rand(0, duration)).toFixed(2)}s`,
        '--sway': `${rand(-60, 60).toFixed(0)}px`,
        '--po': rand(0.25, 0.7).toFixed(2)
      }
    }
  })
}

// --- Ambient sensor waveform (seamlessly tiling) ---
function buildSegment(width, baseline, jitter, spikeChance, spikeMin, spikeMax) {
  const pts = [[0, baseline]]
  let x = 0
  while (x < width) {
    x += rand(9, 17)
    if (x >= width - 14) {
      pts.push([width, baseline])
      break
    }
    if (Math.random() < spikeChance) {
      pts.push([x, baseline - rand(2, 5)])
      pts.push([x + 6, rand(spikeMin, spikeMax)])
      pts.push([x + 13, baseline + rand(0, 5)])
      x += 13
    } else {
      pts.push([x, baseline + rand(-jitter, jitter)])
    }
  }
  return pts
}

function toPath(pts, offsetX = 0, startWithMove = true) {
  return pts
    .map(([x, y], i) => `${i === 0 && startWithMove ? 'M' : 'L'}${(x + offsetX).toFixed(1)} ${y.toFixed(1)}`)
    .join(' ')
}

function seedTraces() {
  const W = 1200
  const front = buildSegment(W, 54, 4, 0.07, 12, 30)
  const back = buildSegment(W, 42, 3, 0.05, 20, 34)
  traceFront.value = `${toPath(front)} ${toPath(front, W, false)}`
  traceFrontArea.value = `${traceFront.value} L2400 80 L0 80 Z`
  traceBack.value = `${toPath(back)} ${toPath(back, W, false)}`
}

// --- Damped pointer parallax ---
function applyParallax() {
  curX += (targetX - curX) * 0.08
  curY += (targetY - curY) * 0.08
  const el = pageEl.value
  if (el) {
    el.style.setProperty('--mx', curX.toFixed(4))
    el.style.setProperty('--my', curY.toFixed(4))
  }
  if (Math.abs(targetX - curX) > 0.0005 || Math.abs(targetY - curY) > 0.0005) {
    rafId = requestAnimationFrame(applyParallax)
  } else {
    rafId = 0
  }
}

function onPointerMove(e) {
  if (!motionOK) return
  targetX = e.clientX / window.innerWidth - 0.5
  targetY = e.clientY / window.innerHeight - 0.5
  if (!rafId) rafId = requestAnimationFrame(applyParallax)
}

function onPointerLeave() {
  if (!motionOK) return
  targetX = 0
  targetY = 0
  if (!rafId) rafId = requestAnimationFrame(applyParallax)
}

function syncMotionPrefs() {
  prefersReduced = mediaReduce.matches
  motionOK = !prefersReduced && mediaFine.matches
  if (!prefersReduced && particles.value.length === 0) seedParticles()
}

// --- Primary action ---
function handleGetStarted() {
  if (isLaunching.value) return
  const go = () => {
    router.push({ name: 'DetectorTransfer' }).catch(() => {
      isLaunching.value = false
    })
  }
  if (prefersReduced) {
    go()
    return
  }
  isLaunching.value = true
  launchTimer = setTimeout(go, 280)
}

// --- Lifecycle ---
onMounted(() => {
  mediaReduce = window.matchMedia('(prefers-reduced-motion: reduce)')
  mediaFine = window.matchMedia('(pointer: fine)')
  syncMotionPrefs()
  mediaReduce.addEventListener?.('change', syncMotionPrefs)
  mediaFine.addEventListener?.('change', syncMotionPrefs)

  seedTraces()

  const el = pageEl.value
  el?.addEventListener('pointermove', onPointerMove, { passive: true })
  el?.addEventListener('pointerleave', onPointerLeave, { passive: true })
})

onBeforeUnmount(() => {
  if (launchTimer) clearTimeout(launchTimer)
  if (rafId) cancelAnimationFrame(rafId)
  const el = pageEl.value
  el?.removeEventListener('pointermove', onPointerMove)
  el?.removeEventListener('pointerleave', onPointerLeave)
  mediaReduce?.removeEventListener?.('change', syncMotionPrefs)
  mediaFine?.removeEventListener?.('change', syncMotionPrefs)
})
</script>

<style scoped>
.home-page {
  --ink-900: #060b14;
  --ink-800: #0b1322;
  --ink-700: #101b30;
  --red: #ff3b4e;
  --red-deep: #c4001a;
  --red-dark: #8f0013;
  --gold: #ffb71b;
  --gold-soft: #ffd34d;
  --blue: #2e9bff;
  --green: #35e08c;
  --text: #f2f6fc;
  --text-dim: #9fb0c8;
  --line: rgba(158, 180, 214, 0.14);

  position: relative;
  height: 100vh;
  height: 100dvh;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--ink-900);
  color: var(--text);
  font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
  scrollbar-width: thin;
  scrollbar-color: var(--red-deep) var(--ink-800);
}

/* Scrollbar in the page's own language */
.home-page::-webkit-scrollbar { width: 10px; }
.home-page::-webkit-scrollbar-track { background: var(--ink-800); }
.home-page::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #ff7a2f, var(--red-deep));
  border-radius: 8px;
  border: 2px solid var(--ink-800);
}
.home-page::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, var(--gold-soft), var(--red));
}

/* ===== Background layers ===== */
.bg-base {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(1100px 620px at 50% -12%, rgba(30, 52, 92, 0.55), transparent 68%),
    radial-gradient(900px 480px at 50% 118%, rgba(196, 0, 26, 0.22), transparent 70%),
    linear-gradient(180deg, #0b1526 0%, #060b14 55%, #0a0f1c 100%);
}

.bg-aurora {
  position: fixed;
  inset: 0;
  z-index: 1;
  overflow: hidden;
  pointer-events: none;
  opacity: 0;
  animation: fade 1.6s ease 0.15s forwards;
  transform: translate3d(calc(var(--mx, 0) * 18px), calc(var(--my, 0) * 12px), 0);
}
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  mix-blend-mode: screen;
  will-change: transform;
}
.blob-red {
  width: 58vmax; height: 58vmax;
  top: -22%; left: -14%;
  background: radial-gradient(circle at 35% 35%, rgba(214, 0, 28, 0.5), transparent 65%);
  animation: drift-a 24s ease-in-out infinite alternate;
}
.blob-blue {
  width: 52vmax; height: 52vmax;
  top: 14%; right: -18%;
  background: radial-gradient(circle at 60% 40%, rgba(10, 90, 214, 0.45), transparent 65%);
  animation: drift-b 28s ease-in-out infinite alternate;
}
.blob-gold {
  width: 40vmax; height: 40vmax;
  bottom: -24%; left: 28%;
  background: radial-gradient(circle at 50% 50%, rgba(255, 183, 27, 0.26), transparent 65%);
  animation: drift-c 32s ease-in-out infinite alternate;
}

.bg-grid {
  position: fixed;
  inset: -30px;
  z-index: 2;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(120, 150, 200, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120, 150, 200, 0.07) 1px, transparent 1px);
  background-size: 44px 44px;
  -webkit-mask-image: radial-gradient(ellipse at center, #000 28%, transparent 74%);
  mask-image: radial-gradient(ellipse at center, #000 28%, transparent 74%);
  opacity: 0;
  animation: fade 1.8s ease 0.3s forwards;
  transform: translate3d(calc(var(--mx, 0) * 8px), calc(var(--my, 0) * 6px), 0);
}

.bg-particles {
  position: fixed;
  inset: 0;
  z-index: 3;
  overflow: hidden;
  pointer-events: none;
  transform: translate3d(calc(var(--mx, 0) * 12px), calc(var(--my, 0) * 8px), 0);
}
.particle {
  position: absolute;
  top: 102%;
  border-radius: 50%;
  opacity: 0;
  animation-name: float;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

.bg-scanline {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 2px;
  z-index: 4;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(46, 155, 255, 0.8), transparent);
  box-shadow: 0 0 18px 2px rgba(46, 155, 255, 0.35);
  opacity: 0;
  animation: scan 10s linear 2s infinite;
}

.bg-vignette {
  position: fixed;
  inset: 0;
  z-index: 6;
  pointer-events: none;
  background: radial-gradient(ellipse at center, transparent 52%, rgba(3, 6, 12, 0.78) 100%);
}

.bg-grain {
  position: fixed;
  inset: 0;
  z-index: 30;
  pointer-events: none;
  opacity: 0.05;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/></svg>");
  background-size: 160px 160px;
}

/* ===== Sensor trace footer ===== */
.trace {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: 84px;
  z-index: 7;
  overflow: hidden;
  pointer-events: none;
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 10%, #000 90%, transparent);
  mask-image: linear-gradient(90deg, transparent, #000 10%, #000 90%, transparent);
  opacity: 0;
  animation: fade 1.4s ease 0.9s forwards;
}
.trace-svg {
  position: absolute;
  bottom: 0; left: 0;
  width: 200%;
  height: 100%;
  display: block;
  will-change: transform;
}
.trace-front {
  animation: trace-scroll 22s linear infinite;
  filter: drop-shadow(0 0 5px rgba(53, 224, 140, 0.45));
}
.trace-back {
  animation: trace-scroll 36s linear infinite;
  opacity: 0.7;
}

/* ===== HUD corners ===== */
.hud {
  position: fixed;
  inset: 18px;
  z-index: 8;
  pointer-events: none;
  opacity: 0;
  animation: fade 1.2s ease 1s forwards;
}
.corner {
  position: absolute;
  width: 26px; height: 26px;
  border: 0 solid rgba(255, 183, 27, 0.4);
}
.corner-tl { top: 0; left: 0; border-top-width: 2px; border-left-width: 2px; }
.corner-tr { top: 0; right: 0; border-top-width: 2px; border-right-width: 2px; }
.corner-bl { bottom: 0; left: 0; border-bottom-width: 2px; border-left-width: 2px; }
.corner-br { bottom: 0; right: 0; border-bottom-width: 2px; border-right-width: 2px; }

/* ===== Content ===== */
.frame {
  position: relative;
  z-index: 10;
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 56px 24px 140px;
  box-sizing: border-box;
}
.stage {
  text-align: center;
  max-width: 780px;
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.is-launching .stage {
  opacity: 0.25;
  transform: scale(1.035);
}

/* Emblem */
.emblem-parallax {
  transform: translate3d(calc(var(--mx, 0) * -12px), calc(var(--my, 0) * -8px), 0);
  will-change: transform;
}
.emblem-wrap {
  position: relative;
  width: clamp(132px, 22vh, 196px);
  margin: 0 auto 30px;
  animation: pop 0.9s cubic-bezier(0.22, 1, 0.36, 1) 0.1s both;
}
.emblem-wrap::before {
  content: '';
  position: absolute;
  inset: -20%;
  z-index: -1;
  background: radial-gradient(circle, rgba(214, 0, 28, 0.22), rgba(46, 155, 255, 0.1) 45%, transparent 70%);
  filter: blur(24px);
  animation: breathe 7s ease-in-out infinite;
}
.emblem {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}
.emblem .ticks,
.emblem .sweep,
.emblem .pulse {
  transform-box: view-box;
  transform-origin: 50% 50%;
}
.emblem .ticks { animation: spin 80s linear infinite reverse; }
.emblem .sweep { animation: spin 5.5s linear infinite; opacity: 0.85; }
.emblem .pulse { opacity: 0; animation: pulse 3.2s ease-out infinite; }
.emblem .p2 { animation-delay: 1.6s; }
.emblem .shield { filter: drop-shadow(0 0 14px rgba(255, 122, 47, 0.35)); }
.emblem .molecule {
  transform-box: fill-box;
  transform-origin: center;
  animation: molecule-float 6s ease-in-out infinite alternate;
}
.emblem .led {
  opacity: 0.8;
  filter: drop-shadow(0 0 5px rgba(53, 224, 140, 0.9));
  animation: led 2.4s ease-in-out infinite;
}

/* Headline */
.headline { margin: 0; }
.headline-welcome {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.34em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 16px;
  animation: rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.28s both;
}
.headline-welcome::before,
.headline-welcome::after {
  content: '';
  height: 1px;
  width: 30px;
  flex: 0 0 auto;
}
.headline-welcome::before { background: linear-gradient(90deg, transparent, rgba(255, 183, 27, 0.6)); }
.headline-welcome::after { background: linear-gradient(90deg, rgba(255, 183, 27, 0.6), transparent); }
.headline-title {
  display: block;
  font-size: clamp(2.1rem, 5.2vw, 3.55rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.015em;
  text-wrap: balance;
  color: var(--text);
  animation: rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.42s both;
}
.frv {
  background: linear-gradient(100deg, #ffd34d 0%, #ff7a2f 55%, #ff3b4e 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 16px rgba(255, 122, 47, 0.35));
}
.headline-rule {
  display: block;
  width: 92px;
  height: 3px;
  border-radius: 2px;
  margin: 26px auto 34px;
  background: linear-gradient(90deg, var(--gold), var(--red), var(--blue));
  animation: rule-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.56s both;
}

/* CTA */
.cta {
  position: relative;
  display: inline-block;
  animation: rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.68s both;
}
.cta-ring {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  border: 1.5px solid rgba(255, 59, 78, 0.55);
  opacity: 0;
  pointer-events: none;
  animation: ring 2.8s ease-out 1.4s infinite;
}
.get-started {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 36px;
  font: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #fff;
  border-radius: 999px;
  border: 1px solid rgba(255, 183, 27, 0.45);
  background: linear-gradient(135deg, #e01230 0%, var(--red-deep) 55%, var(--red-dark) 100%);
  box-shadow:
    0 10px 30px -8px rgba(214, 0, 28, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.18s ease, box-shadow 0.25s ease, filter 0.25s ease;
}
.get-started::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(110deg, transparent 32%, rgba(255, 255, 255, 0.35) 47%, transparent 62%);
  transform: translateX(-130%) skewX(-18deg);
  animation: sheen 4.6s ease-in-out 1.4s infinite;
  pointer-events: none;
}
@media (hover: hover) {
  .get-started:hover:not(:disabled) {
    transform: translateY(-2px);
    filter: brightness(1.06);
    box-shadow:
      0 16px 38px -8px rgba(214, 0, 28, 0.65),
      0 0 26px rgba(255, 183, 27, 0.28),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
  .get-started:hover:not(:disabled) .btn-arrow { transform: translateX(4px); }
}
.get-started:active:not(:disabled) { transform: translateY(0) scale(0.97); }
.get-started:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 4px;
}
.get-started:disabled { cursor: default; filter: brightness(1.12); }
.btn-label { position: relative; z-index: 1; }
.btn-arrow {
  position: relative;
  z-index: 1;
  transition: transform 0.2s ease;
}

/* Launch transition */
.launch-veil {
  position: fixed;
  inset: 0;
  z-index: 40;
  pointer-events: none;
  opacity: 0;
  background: radial-gradient(circle at 50% 58%, rgba(214, 0, 28, 0.35), rgba(6, 11, 20, 0.97) 72%);
  transition: opacity 0.26s ease;
}
.is-launching .launch-veil {
  opacity: 1;
  pointer-events: all;
}

/* ===== Keyframes ===== */
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes rise {
  from { opacity: 0; transform: translateY(26px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pop {
  0% { opacity: 0; transform: scale(0.82); }
  60% { opacity: 1; }
  100% { opacity: 1; transform: scale(1); }
}
@keyframes rule-in {
  from { opacity: 0; transform: scaleX(0); }
  to { opacity: 1; transform: scaleX(1); }
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes pulse {
  0% { transform: scale(0.66); opacity: 0.55; }
  70% { opacity: 0.12; }
  100% { transform: scale(1.42); opacity: 0; }
}
@keyframes led {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}
@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.08); opacity: 1; }
}
@keyframes molecule-float {
  from { transform: translateY(-1.5px); }
  to { transform: translateY(1.5px); }
}
@keyframes drift-a {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(6%, 8%) scale(1.15); }
  100% { transform: translate(-4%, -6%) scale(1.05); }
}
@keyframes drift-b {
  0% { transform: translate(0, 0) scale(1.05); }
  50% { transform: translate(-7%, 5%) scale(0.95); }
  100% { transform: translate(4%, -8%) scale(1.12); }
}
@keyframes drift-c {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(5%, -7%) scale(1.18); }
  100% { transform: translate(-6%, 4%) scale(1.02); }
}
@keyframes float {
  0% { transform: translate3d(0, 0, 0); opacity: 0; }
  10% { opacity: var(--po, 0.5); }
  90% { opacity: var(--po, 0.5); }
  100% { transform: translate3d(var(--sway, 20px), -114vh, 0); opacity: 0; }
}
@keyframes scan {
  0% { transform: translateY(-2vh); opacity: 0; }
  8% { opacity: 0.35; }
  92% { opacity: 0.35; }
  100% { transform: translateY(102vh); opacity: 0; }
}
@keyframes sheen {
  0% { transform: translateX(-130%) skewX(-18deg); }
  22% { transform: translateX(130%) skewX(-18deg); }
  100% { transform: translateX(130%) skewX(-18deg); }
}
@keyframes ring {
  0% { transform: scale(1); opacity: 0.7; }
  70% { transform: scale(1.25, 1.6); opacity: 0; }
  100% { transform: scale(1.25, 1.6); opacity: 0; }
}
@keyframes trace-scroll {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}

/* ===== Responsive ===== */
@media (max-width: 640px) {
  .frame { padding: 40px 18px 110px; }
  .hud { inset: 12px; }
  .corner { width: 18px; height: 18px; }
  .headline-welcome { letter-spacing: 0.22em; gap: 10px; }
  .headline-welcome::before,
  .headline-welcome::after { width: 20px; }
  .headline-rule { margin: 22px auto 28px; }
  .trace { height: 56px; }
  .emblem-wrap { margin-bottom: 24px; }
}
@media (max-height: 640px) {
  .frame { padding-top: 32px; padding-bottom: 96px; }
  .emblem-wrap { width: clamp(104px, 18vh, 150px); margin-bottom: 18px; }
  .headline-rule { margin: 18px auto 22px; }
}

/* ===== Reduced motion ===== */
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