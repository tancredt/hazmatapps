<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>Update Detector Location</h2>

    <div class="form-container">
      <!-- Detector Label -->
      <div class="form-group">
        <label for="detector-label">
          <span>{{ isLocked ? 'Detector Label' : 'Detector Label (e.g. PGM123)' }}</span>
          <span v-if="isLocked" class="locked-tag" title="This label comes from the page address">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
              <rect x="3" y="11" width="18" height="11" rx="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            From link
          </span>
        </label>

        <input
          id="detector-label"
          type="text"
          v-model="detectorLabel"
          class="form-input"
          :class="{ 'locked-input': isLocked }"
          :readonly="isLocked"
          :aria-readonly="isLocked ? 'true' : 'false'"
          :aria-describedby="isLocked ? 'detector-label-help' : null"
          :placeholder="isLocked ? '' : 'Enter detector label...'"
          autocomplete="off"
          autocapitalize="characters"
          autocorrect="off"
          spellcheck="false"
          :disabled="isProcessing"
        />

        <template v-if="isLocked">
          <div id="detector-label-help" class="label-help">
            Locked to the label in the page address.
            <router-link :to="{ name: 'DetectorTransfer' }" class="inline-link">Use a different detector</router-link>
          </div>

          <div v-if="isResolvingDetector" class="loading-inline" aria-live="polite">
            Checking this detector…
          </div>

          <div v-else-if="matchedDetector" class="detector-meta" aria-live="polite">
            <span class="meta-dot" aria-hidden="true"></span>
            <span class="meta-text">
              Currently at <strong>{{ matchedDetector.location_label || 'Unknown location' }}</strong>
            </span>
            <span v-if="currentDistrictLabel" class="meta-district">{{ currentDistrictLabel }}</span>
          </div>

          <div v-else class="detector-alert" role="alert">
            <p>{{ detectorError }}</p>
            <div class="alert-actions">
              <button type="button" class="btn-inline" @click="resolveDetector()">Try again</button>
              <router-link :to="{ name: 'DetectorTransfer' }" class="btn-inline">Enter label manually</router-link>
            </div>
          </div>
        </template>
      </div>

      <div v-if="showDestinations" :class="{ reveal: isLocked }">
        <!-- Destination -->
        <div class="form-group">
          <label for="destination"><span>Select Destination</span></label>
          <select id="destination" v-model="destination" class="form-input" :disabled="isProcessing" @change="onDestinationChange">
            <option value="">-- Select Destination --</option>
            <option value="BURNLEY">Burnley repair/calibration</option>
            <option value="DISTRICT_CACHE">District Cache</option>
            <option value="STATION">Fire Station</option>
          </select>
        </div>

        <!-- District (Conditional) -->
        <div v-if="destination === 'DISTRICT_CACHE' || destination === 'STATION'" class="form-group">
          <label for="district"><span>Select District</span></label>
          <select id="district" v-model="selectedDistrict" class="form-input" :disabled="isProcessing || isLoadingDistricts" @change="onDistrictChange">
            <option value="">-- Select District --</option>
            <option v-for="d in districts" :key="d.value" :value="d.value">{{ d.label }}</option>
          </select>
          <div v-if="isLoadingDistricts" class="loading-inline" aria-live="polite">Loading districts...</div>
        </div>

        <!-- Fire Station (Conditional) -->
        <div v-if="destination === 'STATION'" class="form-group">
          <label for="station"><span>Select Fire Station</span></label>
          <select id="station" v-model="selectedStation" class="form-input" :disabled="isProcessing || isLoadingStations || !selectedDistrict">
            <option value="">-- Select Fire Station --</option>
            <option v-for="s in stations" :key="s.id" :value="s.label">{{ s.label }}</option>
          </select>
          <div v-if="isLoadingStations" class="loading-inline" aria-live="polite">Loading stations...</div>
          <div v-else-if="selectedDistrict && !stations.length" class="loading-inline">
            No fire stations recorded for this district.
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-bar">
          <button type="button" class="btn-cancel" @click="handleCancel" :disabled="isProcessing">Cancel</button>
          <button type="button" class="btn-primary" @click="handleSubmit" :disabled="isSubmitDisabled || isProcessing">
            {{ isProcessing ? 'Processing...' : 'Submit' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Error Modal -->
    <div v-if="showErrorModal" class="modal-overlay" @click.self="showErrorModal = false">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="error-title">
        <h3 id="error-title">{{ errorTitle }}</h3>
        <p>{{ errorMessage }}</p>
        <div class="modal-actions">
          <button type="button" class="btn-confirm" @click="showErrorModal = false">OK</button>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="success-title">
        <h3 id="success-title">Success</h3>
        <p>{{ successMessage || 'Detector location and status have been updated successfully.' }}</p>
        <div class="modal-actions">
          <button type="button" class="btn-confirm" @click="closeSuccessModal">OK</button>
        </div>
      </div>
    </div>

    <!-- Inactivity Warning Modal -->
    <div v-if="showIdleWarning" class="modal-overlay modal-overlay--idle">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="idle-title" aria-describedby="idle-desc">
        <h3 id="idle-title">Still there?</h3>
        <p id="idle-desc">
          You've been inactive for a while. You'll be returned to the home page in
          <strong class="idle-count" role="timer" :class="{ 'idle-count--urgent': idleUrgent }">{{ idleSecondsRemaining }}</strong>
          second{{ idleSecondsRemaining === 1 ? '' : 's' }}.
        </p>
        <div class="idle-progress" aria-hidden="true">
          <span
            class="idle-progress-bar"
            :class="{ 'idle-progress-bar--urgent': idleUrgent }"
            :style="{ width: idleProgressPercent + '%' }"
          ></span>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="goHomeNow">Return home now</button>
          <button type="button" ref="stayButtonRef" class="btn-confirm" @click="stayOnPage">Stay on this page</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'
import { useInactivityTimeout } from '@/composables/useInactivityTimeout'

// Optional prop so the route can pass `props: true`; falls back to the URL param.
const props = defineProps({
  detector_label: { type: String, default: '' }
})

const route = useRoute()
const router = useRouter()

// --- Inactivity timeout (5 minutes, 30-second warning) ---
const IDLE_TIMEOUT_MS = 5 * 60 * 1000
const IDLE_WARNING_MS = 30 * 1000

const {
  isWarningVisible: showIdleWarning,
  secondsRemaining: idleSecondsRemaining,
  warningSeconds: idleWarningSeconds,
  stay: stayOnPage
} = useInactivityTimeout({
  timeoutMs: IDLE_TIMEOUT_MS,
  warningMs: IDLE_WARNING_MS,
  onTimeout: () => {
    router.replace({ name: 'Home' }).catch(() => {})
  }
})

const idleTotalSeconds = Number(idleWarningSeconds) || 30
const idleUrgent = computed(() => idleSecondsRemaining.value <= 10)
const idleProgressPercent = computed(() =>
  Math.max(0, Math.min(100, (idleSecondsRemaining.value / idleTotalSeconds) * 100))
)

const stayButtonRef = ref(null)
watch(showIdleWarning, async (visible) => {
  if (visible) {
    await nextTick()
    stayButtonRef.value?.focus()
  }
})

const goHomeNow = () => {
  router.replace({ name: 'Home' }).catch(() => {})
}

// --- Locked-label mode ---
const urlLabel = computed(() => {
  const raw = props.detector_label || route.params.detector_label || ''
  return String(Array.isArray(raw) ? raw[0] : raw).trim()
})
const isLocked = computed(() => urlLabel.value.length > 0)

// --- State ---
const detectorLabel = ref('')
const matchedDetector = ref(null)
const isResolvingDetector = ref(false)
const detectorError = ref('')

const destination = ref('')
const selectedDistrict = ref('')
const selectedStation = ref('')

const districts = ref([])
const stations = ref([])

const isLoadingDistricts = ref(false)
const isLoadingStations = ref(false)
const isProcessing = ref(false)

const showErrorModal = ref(false)
const showSuccessModal = ref(false)
const errorMessage = ref('')
const errorTitle = ref('Detector Not Found')
const successMessage = ref('')

const NOT_FOUND_MESSAGE =
  'No record of this detector exists. Check the spelling and if it still fails, email the Hazmat Unit with the label and destination.'

const STATUS_WORDS = {
  OF: 'Offline Repair',
  IS: 'In Stock',
  OP: 'Operational'
}

// --- Computed ---
const showDestinations = computed(() => !isLocked.value || !!matchedDetector.value)

const currentDistrictLabel = computed(() => {
  const raw = matchedDetector.value?.location_district
  if (!raw) return ''
  const hit = districts.value.find(
    d => String(d.value).toUpperCase() === String(raw).toUpperCase()
  )
  return hit?.label || raw
})

const isSubmitDisabled = computed(() => {
  if (isResolvingDetector.value) return true
  if (!detectorLabel.value.trim()) return true
  if (isLocked.value && !matchedDetector.value) return true
  if (!destination.value) return true
  if ((destination.value === 'DISTRICT_CACHE' || destination.value === 'STATION') && !selectedDistrict.value) return true
  if (destination.value === 'STATION' && !selectedStation.value) return true
  return false
})

// --- Methods ---
const resetSelections = () => {
  destination.value = ''
  selectedDistrict.value = ''
  selectedStation.value = ''
  stations.value = []
}

// Backend uses icontains, so confirm an exact case-insensitive match here.
const findDetector = async (label) => {
  const results = await apiFetch(`/detector-labels/?label=${encodeURIComponent(label)}`)
  const list = Array.isArray(results) ? results : []
  return list.find(d => String(d.label).toUpperCase() === label.toUpperCase()) || null
}

const resolveDetector = async ({ silent = false } = {}) => {
  const label = urlLabel.value
  detectorLabel.value = label
  detectorError.value = ''

  if (!label) {
    matchedDetector.value = null
    isResolvingDetector.value = false
    return null
  }

  if (!silent) {
    matchedDetector.value = null
    isResolvingDetector.value = true
  }

  try {
    const match = await findDetector(label)
    matchedDetector.value = match
    if (match) {
      detectorLabel.value = match.label
    } else {
      detectorError.value = NOT_FOUND_MESSAGE
    }
    return match
  } catch (err) {
    console.error('Failed to look up detector', err)
    if (!silent) matchedDetector.value = null
    detectorError.value =
      'Could not reach the database to check this detector. Check your connection and try again.'
    return null
  } finally {
    isResolvingDetector.value = false
  }
}

const fetchDistricts = async () => {
  isLoadingDistricts.value = true
  try {
    const data = await apiFetch('/districts/')
    districts.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('Failed to fetch districts', err)
    districts.value = []
  } finally {
    isLoadingDistricts.value = false
  }
}

const fetchStations = async () => {
  if (!selectedDistrict.value) {
    stations.value = []
    return
  }
  isLoadingStations.value = true
  selectedStation.value = '' // Reset station when district changes
  try {
    const data = await apiFetch(
      `/locations/?location_type=ST&district=${encodeURIComponent(selectedDistrict.value)}`
    )
    stations.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('Failed to fetch stations', err)
    stations.value = []
  } finally {
    isLoadingStations.value = false
  }
}

const onDestinationChange = () => {
  selectedDistrict.value = ''
  selectedStation.value = ''
  stations.value = []
}

const onDistrictChange = () => {
  selectedStation.value = ''
  if (destination.value === 'STATION') {
    fetchStations()
  }
}

const handleCancel = () => {
  resetSelections()
  if (!isLocked.value) detectorLabel.value = ''
  showErrorModal.value = false
  showSuccessModal.value = false
}

// Helper to safely find exact matches since backend uses icontains
const findExactLocation = (results, matchFn) => {
  const list = Array.isArray(results) ? results : []
  return list.find(matchFn) || null
}

const handleSubmit = async () => {
  if (isSubmitDisabled.value || isProcessing.value) return
  isProcessing.value = true
  errorMessage.value = ''

  try {
    // 1. Resolve the detector (already verified when the label came from the URL)
    let detector = null
    if (isLocked.value && matchedDetector.value) {
      detector = matchedDetector.value
    } else {
      detector = await findDetector(detectorLabel.value.trim())
      if (!detector) {
        errorTitle.value = 'Detector Not Found'
        errorMessage.value = NOT_FOUND_MESSAGE
        showErrorModal.value = true
        return
      }
    }

    // 2. Resolve Target Location ID & Status
    let targetLocation = null
    let targetStatus = ''

    if (destination.value === 'BURNLEY') {
      const res = await apiFetch(`/locations/?label=Burnley`)
      targetLocation = findExactLocation(res, l => l.label.toUpperCase() === 'BURNLEY')
      targetStatus = 'OF' // OFFLINE
    } else if (destination.value === 'DISTRICT_CACHE') {
      const res = await apiFetch(
        `/locations/?location_type=DI&district=${encodeURIComponent(selectedDistrict.value)}`
      )
      targetLocation = findExactLocation(
        res,
        l => l.location_type === 'DI' &&
             String(l.district || '').toUpperCase() === selectedDistrict.value.toUpperCase()
      )
      targetStatus = 'IS' // INSTOCK
    } else if (destination.value === 'STATION') {
      const res = await apiFetch(
        `/locations/?label=${encodeURIComponent(selectedStation.value)}&location_type=ST`
      )
      targetLocation = findExactLocation(
        res,
        l => l.label.toUpperCase() === selectedStation.value.toUpperCase() && l.location_type === 'ST'
      )
      targetStatus = 'OP' // OPERATIONAL
    }

    if (!targetLocation?.id) {
      throw new Error('Could not resolve the destination location in the database.')
    }

    // 3. Execute Update
    const payload = [{
      detector_id: detector.id,
      location_id: targetLocation.id,
      status: targetStatus
    }]

    await apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    successMessage.value =
      `${detector.label} is now recorded at ${targetLocation.label} and marked as ${STATUS_WORDS[targetStatus]}.`
    showSuccessModal.value = true
  } catch (err) {
    console.error('Update failed:', err)
    errorTitle.value = 'Update Failed'
    errorMessage.value = err?.message || 'An unexpected error occurred. Please try again.'
    showErrorModal.value = true
  } finally {
    isProcessing.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  resetSelections()
  if (isLocked.value) {
    // Keep the URL label, refresh the "currently at" readout
    resolveDetector({ silent: true })
  } else {
    detectorLabel.value = ''
    matchedDetector.value = null
  }
}

// --- Lifecycle ---
onMounted(() => {
  fetchDistricts()
  if (isLocked.value) resolveDetector()
})

// The same component instance is reused when only the URL label changes
watch(urlLabel, (label) => {
  resetSelections()
  successMessage.value = ''
  errorMessage.value = ''
  showErrorModal.value = false
  showSuccessModal.value = false

  if (label) {
    resolveDetector()
  } else {
    detectorLabel.value = ''
    matchedDetector.value = null
    detectorError.value = ''
    isResolvingDetector.value = false
  }
})
</script>

<style scoped>
.swap-screen {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 16px calc(32px + env(safe-area-inset-bottom));
  box-sizing: border-box;
}
.swap-screen h2 {
  text-align: center;
  font-size: clamp(1.3rem, 4.5vw, 1.7rem);
  color: #212529;
  margin: 12px 0 20px;
}

.form-container {
  max-width: 600px;
  margin: 0 auto;
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #dee2e6;
  text-align: left;
  box-sizing: border-box;
}
.form-group { margin-bottom: 20px; }
.form-group label {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 0.95rem;
}
.form-input {
  width: 100%;
  min-height: 46px;
  padding: 10px 12px;
  font-size: 1rem; /* 16px prevents iOS focus zoom */
  font-family: inherit;
  color: #212529;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.18);
}
.form-input:disabled { background: #e9ecef; cursor: not-allowed; }

/* Locked label field */
.locked-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 20px;
  background: #e8f8f2;
  border: 1px solid #b7e4d0;
  color: #2f7d5c;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.locked-input {
  background: #e9ecef;
  border-color: #ced4da;
  border-style: dashed;
  color: #343a40;
  font-weight: 700;
  letter-spacing: 0.06em;
  cursor: default;
}
.locked-input:focus {
  border-color: #adb5bd;
  box-shadow: none;
}
.locked-input:focus-visible {
  outline: 2px solid #42b883;
  outline-offset: 2px;
}
.label-help {
  margin-top: 6px;
  font-size: 0.8rem;
  color: #6c757d;
  line-height: 1.5;
}
.inline-link {
  color: #2f7d5c;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.inline-link:hover { color: #42b883; }
.inline-link:focus-visible { outline: 2px solid #42b883; outline-offset: 2px; border-radius: 3px; }

.detector-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #e8f8f2;
  border: 1px solid #b7e4d0;
  font-size: 0.88rem;
  color: #2f5d4a;
}
.meta-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #42b883;
  flex: 0 0 auto;
}
.meta-text strong { color: #212529; }
.meta-district {
  padding: 2px 8px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid #b7e4d0;
  font-size: 0.75rem;
  font-weight: 600;
  color: #2f7d5c;
}

.detector-alert {
  margin-top: 10px;
  padding: 12px 14px;
  border-radius: 8px;
  background: #fdecea;
  border: 1px solid #f5c6cb;
}
.detector-alert p {
  margin: 0;
  color: #a3271b;
  font-size: 0.88rem;
  line-height: 1.5;
  overflow-wrap: break-word;
}
.alert-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.btn-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 6px 14px;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  color: #495057;
  background: #fff;
  border: 1px solid #ced4da;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  box-sizing: border-box;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.btn-inline:hover { background: #f1f3f5; border-color: #42b883; color: #2f7d5c; }
.btn-inline:focus-visible { outline: 2px solid #42b883; outline-offset: 2px; }

.loading-inline {
  font-size: 0.85rem;
  color: #666;
  margin-top: 6px;
  font-style: italic;
}

.reveal { animation: fadeUp 0.25s ease-out; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.action-bar {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 28px;
}
.action-bar .btn-cancel,
.action-bar .btn-primary { flex: 0 1 auto; min-width: 120px; }

/* Buttons */
.btn-primary, .btn-confirm, .btn-cancel {
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  min-height: 46px;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.2s, border-color 0.2s, transform 0.1s;
}
.btn-primary, .btn-confirm { background: #42b883; color: #fff; border: 1px solid #42b883; }
.btn-primary:hover:not(:disabled), .btn-confirm:hover { background: #369e6f; border-color: #369e6f; }
.btn-primary:active:not(:disabled), .btn-confirm:active { transform: scale(0.98); }
.btn-primary:disabled { background: #9fd4bc; border-color: #9fd4bc; cursor: not-allowed; }
.btn-cancel { background: #fff; color: #495057; border: 1px solid #ced4da; }
.btn-cancel:hover:not(:disabled) { background: #f1f3f5; border-color: #adb5bd; }
.btn-cancel:active:not(:disabled) { transform: scale(0.98); }
.btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary:focus-visible, .btn-confirm:focus-visible, .btn-cancel:focus-visible {
  outline: 2px solid #42b883;
  outline-offset: 2px;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(33, 37, 41, 0.55);
  box-sizing: border-box;
}
.modal-content {
  width: 100%;
  max-width: 420px;
  max-height: calc(100vh - 40px);
  max-height: calc(100dvh - 40px);
  overflow-y: auto;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  text-align: left;
  box-sizing: border-box;
  scrollbar-width: thin;
  scrollbar-color: #ced4da #f1f3f5;
}
.modal-content::-webkit-scrollbar { width: 8px; }
.modal-content::-webkit-scrollbar-track { background: #f1f3f5; border-radius: 8px; }
.modal-content::-webkit-scrollbar-thumb { background: #ced4da; border-radius: 8px; }
.modal-content::-webkit-scrollbar-thumb:hover { background: #42b883; }
.modal-content h3 { margin: 0 0 10px; font-size: 1.2rem; color: #212529; }
.modal-content p { margin: 0 0 20px; color: #495057; line-height: 1.55; overflow-wrap: break-word; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; flex-wrap: wrap; }
.modal-actions .btn-confirm { min-width: 110px; }

/* Inactivity warning */
.modal-overlay--idle { z-index: 1100; }
.idle-count { font-variant-numeric: tabular-nums; color: #212529; }
.idle-count--urgent { color: #c0392b; }
.idle-progress {
  height: 6px;
  margin: 0 0 20px;
  border-radius: 4px;
  background: #e9ecef;
  overflow: hidden;
}
.idle-progress-bar {
  display: block;
  height: 100%;
  border-radius: 4px;
  background: #42b883;
  transition: width 1s linear, background-color 0.3s ease;
}
.idle-progress-bar--urgent { background: #e05252; }

/* Mobile */
@media (max-width: 480px) {
  .swap-screen { padding: 12px 12px calc(24px + env(safe-area-inset-bottom)); }
  .form-container { padding: 18px 14px; border-radius: 10px; }
  .form-group { margin-bottom: 16px; }
  .action-bar { flex-direction: column-reverse; gap: 10px; }
  .action-bar .btn-cancel,
  .action-bar .btn-primary { width: 100%; min-width: 0; min-height: 48px; }
  .alert-actions { flex-direction: column; }
  .btn-inline { width: 100%; min-height: 44px; }
  .modal-overlay { padding: 16px; }
  .modal-content { padding: 20px 16px; }
  .modal-actions { flex-direction: column-reverse; }
  .modal-actions .btn-confirm,
  .modal-actions .btn-cancel { width: 100%; min-width: 0; min-height: 48px; }
}

@media (prefers-reduced-motion: reduce) {
  .idle-progress-bar { transition: none; }
  .reveal { animation: none; }
}
</style>