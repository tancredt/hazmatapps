import { ref, onMounted, onBeforeUnmount } from 'vue'

const ACTIVITY_EVENTS = ['pointerdown', 'pointermove', 'keydown', 'wheel', 'touchstart', 'scroll', 'input']

/**
 * Redirects after a period of user inactivity, with an optional warning phase.
 * Any pointer, key, touch, wheel, scroll or input activity resets the clock.
 * Uses wall-clock timestamps so throttled background tabs / device sleep are
 * handled correctly, and cleans up all listeners and timers on unmount.
 */
export function useInactivityTimeout(options = {}) {
  const {
    timeoutMs = 5 * 60 * 1000,
    warningMs = 30 * 1000,
    onTimeout,
    events = ACTIVITY_EVENTS
  } = options

  const warningDuration = Math.max(0, Math.min(warningMs, timeoutMs))
  const warningSeconds = Math.ceil(warningDuration / 1000)

  const isWarningVisible = ref(false)
  const secondsRemaining = ref(warningSeconds)

  let lastActivityAt = Date.now()
  let lastHandledAt = 0
  let idleTimer = null
  let countdownTimer = null
  let redirectTimer = null
  let listening = false
  let stopped = false

  function clearTimers() {
    if (idleTimer) { clearTimeout(idleTimer); idleTimer = null }
    if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null }
    if (redirectTimer) { clearTimeout(redirectTimer); redirectTimer = null }
  }

  function remainingMs() {
    return timeoutMs - (Date.now() - lastActivityAt)
  }

  function stop() {
    if (stopped) return
    stopped = true
    clearTimers()
    if (listening) {
      events.forEach(evt => window.removeEventListener(evt, handleActivity, true))
      document.removeEventListener('visibilitychange', handleVisibility)
      listening = false
    }
  }

  function fireTimeout() {
    if (stopped) return
    stop()
    isWarningVisible.value = false
    if (typeof onTimeout === 'function') onTimeout()
  }

  function tick() {
    const remaining = remainingMs()
    secondsRemaining.value = Math.max(0, Math.ceil(remaining / 1000))
    if (remaining <= 0) fireTimeout()
  }

  function scheduleIdleCheck(delay) {
    idleTimer = setTimeout(beginWarning, Math.max(delay, 250))
  }

  function beginWarning() {
    if (stopped) return
    const remaining = remainingMs()
    // Timer fired early (throttled tab) — reschedule against the wall clock.
    if (remaining > warningDuration) {
      scheduleIdleCheck(remaining - warningDuration)
      return
    }
    if (remaining <= 0) {
      fireTimeout()
      return
    }
    isWarningVisible.value = true
    tick()
    if (!countdownTimer) countdownTimer = setInterval(tick, 1000)
    redirectTimer = setTimeout(fireTimeout, remaining)
  }

  function reset() {
    if (stopped) return
    lastActivityAt = Date.now()
    isWarningVisible.value = false
    secondsRemaining.value = warningSeconds
    clearTimers()
    scheduleIdleCheck(timeoutMs - warningDuration)
  }

  function handleActivity() {
    if (stopped) return
    const now = Date.now()
    if (now - lastHandledAt < 1000) return // throttle high-frequency events
    lastHandledAt = now
    reset()
  }

  function handleVisibility() {
    if (stopped || document.visibilityState !== 'visible') return
    const remaining = remainingMs()
    clearTimers()
    if (remaining <= 0) {
      fireTimeout()
      return
    }
    if (remaining <= warningDuration) {
      beginWarning()
      return
    }
    isWarningVisible.value = false
    secondsRemaining.value = warningSeconds
    scheduleIdleCheck(remaining - warningDuration)
  }

  onMounted(() => {
    if (stopped) return
    lastActivityAt = Date.now()
    events.forEach(evt => window.addEventListener(evt, handleActivity, { capture: true, passive: true }))
    document.addEventListener('visibilitychange', handleVisibility)
    listening = true
    scheduleIdleCheck(timeoutMs - warningDuration)
  })

  onBeforeUnmount(stop)

  return { isWarningVisible, secondsRemaining, warningSeconds, stay: reset, stop }
}
