<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>Update Detector Location</h2>

    <div class="form-container">
      <!-- Detector Label -->
      <div class="form-group">
        <label for="detector-label">Detector Label (e.g. PGM123)</label>
        <input
          id="detector-label"
          type="text"
          v-model="detectorLabel"
          class="form-input"
          placeholder="Enter detector label..."
          autocomplete="off"
          autocapitalize="characters"
          autocorrect="off"
          spellcheck="false"
          :disabled="isProcessing"
        />
      </div>

      <!-- Destination -->
      <div class="form-group">
        <label for="destination">Select Destination</label>
        <select id="destination" v-model="destination" class="form-input" :disabled="isProcessing" @change="onDestinationChange">
          <option value="">-- Select Destination --</option>
          <option value="BURNLEY">Burnley repair/calibration</option>
          <option value="DISTRICT_CACHE">District Cache</option>
          <option value="STATION">Fire Station</option>
        </select>
      </div>

      <!-- District (Conditional) -->
      <div v-if="destination === 'DISTRICT_CACHE' || destination === 'STATION'" class="form-group">
        <label for="district">Select District</label>
        <select id="district" v-model="selectedDistrict" class="form-input" :disabled="isProcessing || isLoadingDistricts" @change="onDistrictChange">
          <option value="">-- Select District --</option>
          <option v-for="d in districts" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
      </div>

      <!-- Fire Station (Conditional) -->
      <div v-if="destination === 'STATION'" class="form-group">
        <label for="station">Select Fire Station</label>
        <select id="station" v-model="selectedStation" class="form-input" :disabled="isProcessing || isLoadingStations || !selectedDistrict">
          <option value="">-- Select Fire Station --</option>
          <option v-for="s in stations" :key="s.id" :value="s.label">{{ s.label }}</option>
        </select>
        <div v-if="isLoadingStations" class="loading-inline" aria-live="polite">Loading stations...</div>
      </div>

      <!-- Action Buttons -->
      <div class="action-bar">
        <button type="button" class="btn-cancel" @click="handleCancel" :disabled="isProcessing">Cancel</button>
        <button type="button" class="btn-primary" @click="handleSubmit" :disabled="isSubmitDisabled || isProcessing">
          {{ isProcessing ? 'Processing...' : 'Submit' }}
        </button>
      </div>
    </div>

    <!-- Error Modal -->
    <div v-if="showErrorModal" class="modal-overlay" @click.self="showErrorModal = false">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="error-title">
        <h3 id="error-title">Detector Not Found</h3>
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
        <p>Detector location and status have been updated successfully.</p>
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
import { useRouter } from 'vue-router'
import { apiFetch } from '@/utils/api'
import HomeHeader from './HomeHeader.vue'
import { useInactivityTimeout } from '@/composables/useInactivityTimeout'

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

const idleUrgent = computed(() => idleSecondsRemaining.value <= 10)
const idleProgressPercent = computed(() =>
  Math.max(0, Math.min(100, (idleSecondsRemaining.value / idleWarningSeconds) * 100))
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

// --- State ---
const detectorLabel = ref('')
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

// --- Computed ---
const isSubmitDisabled = computed(() => {
  if (!detectorLabel.value.trim()) return true
  if (!destination.value) return true
  if ((destination.value === 'DISTRICT_CACHE' || destination.value === 'STATION') && !selectedDistrict.value) return true
  if (destination.value === 'STATION' && !selectedStation.value) return true
  return false
})

// --- Methods ---
const fetchDistricts = async () => {
  isLoadingDistricts.value = true
  try {
    const data = await apiFetch('/districts/')
    districts.value = data
  } catch (err) {
    console.error('Failed to fetch districts', err)
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
    const data = await apiFetch(`/locations/?location_type=ST&district=${encodeURIComponent(selectedDistrict.value)}`)
    stations.value = data
  } catch (err) {
    console.error('Failed to fetch stations', err)
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
  detectorLabel.value = ''
  destination.value = ''
  selectedDistrict.value = ''
  selectedStation.value = ''
  stations.value = []

  // Close any open modals just in case
  showErrorModal.value = false
  showSuccessModal.value = false
}

// Helper to safely find exact matches since backend uses icontains
const findExactLocation = (results, matchFn) => {
  return results.find(matchFn) || null
}

const handleSubmit = async () => {
  if (isSubmitDisabled.value) return
  isProcessing.value = true
  errorMessage.value = ''

  try {
    // 1. Check if detector exists (case-insensitive exact match)
    const inputLabel = detectorLabel.value.trim()
    const searchResults = await apiFetch(`/detector-labels/?label=${encodeURIComponent(inputLabel)}`)

    // The backend uses icontains, so we filter for exact case-insensitive match on frontend
    const matchedDetector = searchResults.find(d => d.label.toUpperCase() === inputLabel.toUpperCase())

    if (!matchedDetector) {
      errorMessage.value = 'No record of this detector exists. Check the spelling and if it still fails, email the Hazmat Unit with the label and destination.'
      showErrorModal.value = true
      isProcessing.value = false
      return
    }

    // 2. Resolve Target Location ID & Status
    let targetLocationId = null
    let targetStatus = ''

    if (destination.value === 'BURNLEY') {
      const res = await apiFetch(`/locations/?label=Burnley`)
      const loc = findExactLocation(res, l => l.label.toUpperCase() === 'BURNLEY')
      targetLocationId = loc?.id
      targetStatus = 'OF' // OFFLINE
    } else if (destination.value === 'DISTRICT_CACHE') {
      const res = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(selectedDistrict.value)}`)
      const loc = findExactLocation(res, l => l.location_type === 'DI' && l.district?.toUpperCase() === selectedDistrict.value.toUpperCase())
      targetLocationId = loc?.id
      targetStatus = 'IS' // INSTOCK
    } else if (destination.value === 'STATION') {
      const res = await apiFetch(`/locations/?label=${encodeURIComponent(selectedStation.value)}&location_type=ST`)
      const loc = findExactLocation(res, l => l.label.toUpperCase() === selectedStation.value.toUpperCase() && l.location_type === 'ST')
      targetLocationId = loc?.id
      targetStatus = 'OP' // OPERATIONAL
    }

    if (!targetLocationId) {
      throw new Error('Could not resolve the destination location in the database.')
    }

    // 3. Execute Update
    const payload = [{
      detector_id: matchedDetector.id,
      location_id: targetLocationId,
      status: targetStatus
    }]

    await apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    showSuccessModal.value = true
  } catch (err) {
    console.error('Update failed:', err)
    errorMessage.value = err.message || 'An unexpected error occurred. Please try again.'
    showErrorModal.value = true
  } finally {
    isProcessing.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  // Reset form for next use
  handleCancel()
}

// --- Lifecycle ---
onMounted(() => {
  fetchDistricts()
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
  display: block;
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
.loading-inline {
  font-size: 0.85rem;
  color: #666;
  margin-top: 6px;
  font-style: italic;
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
  .modal-overlay { padding: 16px; }
  .modal-content { padding: 20px 16px; }
  .modal-actions { flex-direction: column-reverse; }
  .modal-actions .btn-confirm,
  .modal-actions .btn-cancel { width: 100%; min-width: 0; min-height: 48px; }
}

@media (prefers-reduced-motion: reduce) {
  .idle-progress-bar { transition: none; }
}
</style>