<template>
  <div class="swap-screen">
    <HomeHeader />
    <h2>Update Detector Location</h2>

    <!-- URL label gate: checking / 404 / unreachable replaces the form entirely -->
    <LabelLookupPanel
      v-if="!showForm"
      kind="detector"
      :label="urlLabel"
      :state="lookupState"
      :retrying="isRetrying"
      @retry="retryLookup"
      @manual="enterManually"
    />

    <template v-else>
      <!-- Verified banner for a label that came from the URL -->
      <div v-if="labelLocked && matchedDetector" class="verified-banner">
        <span class="verified-tick" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
               stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </span>
        <div class="verified-text">
          <strong>{{ matchedDetector.label }}</strong>
          <span>{{ verifiedDetail }}</span>
        </div>
        <button type="button" class="verified-change" @click="enterManually">Change</button>
      </div>

      <div class="form-container" :class="{ reveal: labelLocked }">
        <!-- Detector Label -->
        <div class="form-group">
          <label for="detector-label"><span>Detector Label</span></label>
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
            :readonly="labelLocked"
            :disabled="isProcessing"
          />
          <div v-if="!labelLocked" class="field-hint">
            Use the printed asset label, not the serial number.
          </div>
        </div>

        <!-- Destination -->
        <div class="form-group">
          <label for="destination"><span>Select Destination</span></label>
          <select id="destination" v-model="destination" class="form-input"
                  :disabled="isProcessing" @change="onDestinationChange">
            <option value="">-- Select Destination --</option>
            <option value="BURNLEY">Burnley repair/calibration</option>
            <option value="DISTRICT_CACHE">District Cache</option>
            <option value="STATION">Fire Station</option>
          </select>
        </div>

        <!-- District -->
        <div v-if="destination === 'DISTRICT_CACHE' || destination === 'STATION'" class="form-group">
          <label for="district"><span>Select District</span></label>
          <select id="district" v-model="selectedDistrict" class="form-input"
                  :disabled="isProcessing || isLoadingDistricts" @change="onDistrictChange">
            <option value="">-- Select District --</option>
            <option v-for="d in districts" :key="d.value" :value="d.value">{{ d.label }}</option>
          </select>
          <div v-if="isLoadingDistricts" class="loading-inline" aria-live="polite">Loading districts...</div>
        </div>

        <!-- Fire Station -->
        <div v-if="destination === 'STATION'" class="form-group">
          <label for="station"><span>Select Fire Station</span></label>
          <select id="station" v-model="selectedStation" class="form-input"
                  :disabled="isProcessing || isLoadingStations || !selectedDistrict">
            <option value="">-- Select Fire Station --</option>
            <option v-for="s in stations" :key="s.id" :value="s.label">{{ s.label }}</option>
          </select>
          <div v-if="isLoadingStations" class="loading-inline" aria-live="polite">Loading stations...</div>
          <div v-else-if="selectedDistrict && !stations.length" class="loading-inline">
            No fire stations recorded for this district.
          </div>
        </div>

        <!-- Actions -->
        <div class="action-bar">
          <button type="button" class="btn-cancel" @click="handleCancel" :disabled="isProcessing">Cancel</button>
          <button type="button" class="btn-primary" @click="handleSubmit"
                  :disabled="isSubmitDisabled || isProcessing">
            {{ isProcessing ? 'Processing...' : 'Submit' }}
          </button>
        </div>
      </div>
    </template>

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
      <div class="modal-content" role="dialog" aria-modal="true"
           aria-labelledby="idle-title" aria-describedby="idle-desc">
        <h3 id="idle-title">Still there?</h3>
        <p id="idle-desc">
          You've been inactive for a while. You'll be returned to the home page in
          <strong class="idle-count" role="timer" :class="{ 'idle-count--urgent': idleUrgent }">{{ idleSecondsRemaining }}</strong>
          second{{ idleSecondsRemaining === 1 ? '' : 's' }}.
        </p>
        <div class="idle-progress" aria-hidden="true">
          <span class="idle-progress-bar" :class="{ 'idle-progress-bar--urgent': idleUrgent }"
                :style="{ width: idleProgressPercent + '%' }"></span>
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
import LabelLookupPanel from './LabelLookupPanel.vue'
import { useInactivityTimeout } from '@/composables/useInactivityTimeout'
import {
  lookupDetector,
  firstParam,
  DISTRICT_WORDS,
  DETECTOR_STATUS_WORDS
} from '@/utils/labelLookup'

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
  onTimeout: () => { router.replace({ name: 'Home' }).catch(() => {}) }
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

const goHomeNow = () => { router.replace({ name: 'Home' }).catch(() => {}) }

// --- URL label ---
const urlLabel = computed(() => firstParam(props.detector_label || route.params.detector_label))

// idle | checking | found | missing | error
const lookupState = ref('idle')
const isRetrying = ref(false)
const matchedDetector = ref(null)

const showForm = computed(() => lookupState.value === 'idle' || lookupState.value === 'found')
const labelLocked = computed(() => !!urlLabel.value && lookupState.value === 'found')

const verifiedDetail = computed(() => {
  const d = matchedDetector.value
  if (!d) return ''
  const place = d.location_label ? `Currently at ${d.location_label}` : 'Found in the register'
  const district = DISTRICT_WORDS[String(d.location_district || '').trim()]
  return district ? `${place} · ${district}` : place
})

// --- Form state ---
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
const errorTitle = ref('Detector Not Found')
const successMessage = ref('')

const NOT_FOUND_MESSAGE =
  'No record of this detector exists. Check the spelling and if it still fails, email the Hazmat Unit with the label and destination.'
const UNREACHABLE_MESSAGE =
  'Could not reach the database to check this detector. Check your connection and try again.'

const isSubmitDisabled = computed(() => {
  if (lookupState.value === 'checking') return true
  if (!detectorLabel.value.trim()) return true
  if (!destination.value) return true
  if ((destination.value === 'DISTRICT_CACHE' || destination.value === 'STATION') && !selectedDistrict.value) return true
  if (destination.value === 'STATION' && !selectedStation.value) return true
  return false
})

// --- Label verification ---
const resolveDetector = async ({ force = false } = {}) => {
  const label = urlLabel.value

  if (!label) {
    lookupState.value = 'idle'
    matchedDetector.value = null
    detectorLabel.value = ''
    return
  }

  lookupState.value = 'checking'
  detectorLabel.value = label

  const result = await lookupDetector(label, { force })
  if (urlLabel.value !== label) return // URL moved on mid-flight

  if (result.state === 'found') {
    matchedDetector.value = result.record
    detectorLabel.value = result.record.label
    lookupState.value = 'found'
  } else {
    matchedDetector.value = null
    lookupState.value = result.state // missing | error
  }
}

const retryLookup = async () => {
  if (isRetrying.value) return
  isRetrying.value = true
  try {
    await resolveDetector({ force: true })
  } finally {
    isRetrying.value = false
  }
}

const enterManually = () => {
  router.replace({ name: 'DetectorTransfer' }).catch(() => {})
}

// --- Reference data ---
const resetSelections = () => {
  destination.value = ''
  selectedDistrict.value = ''
  selectedStation.value = ''
  stations.value = []
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
  selectedStation.value = ''
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
  if (destination.value === 'STATION') fetchStations()
}

const handleCancel = () => {
  resetSelections()
  if (!labelLocked.value) detectorLabel.value = ''
  showErrorModal.value = false
  showSuccessModal.value = false
}

const findExactLocation = (results, matchFn) => {
  const list = Array.isArray(results) ? results : []
  return list.find(matchFn) || null
}

// --- Submit ---
const handleSubmit = async () => {
  if (isSubmitDisabled.value || isProcessing.value) return
  isProcessing.value = true
  errorMessage.value = ''

  try {
    let detector = null
    const typed = detectorLabel.value.trim()

    if (matchedDetector.value && typed.toUpperCase() === String(matchedDetector.value.label).toUpperCase()) {
      detector = matchedDetector.value
    } else {
      const result = await lookupDetector(typed)
      if (result.state === 'error') {
        errorTitle.value = 'Connection Problem'
        errorMessage.value = UNREACHABLE_MESSAGE
        showErrorModal.value = true
        return
      }
      if (result.state !== 'found') {
        errorTitle.value = 'Detector Not Found'
        errorMessage.value = NOT_FOUND_MESSAGE
        showErrorModal.value = true
        return
      }
      detector = result.record
    }

    let targetLocation = null
    let targetStatus = ''

    if (destination.value === 'BURNLEY') {
      const res = await apiFetch('/locations/?label=Burnley')
      targetLocation = findExactLocation(res, (l) => String(l.label).toUpperCase() === 'BURNLEY')
      targetStatus = 'OF'
    } else if (destination.value === 'DISTRICT_CACHE') {
      const res = await apiFetch(
        `/locations/?location_type=DI&district=${encodeURIComponent(selectedDistrict.value)}`
      )
      targetLocation = findExactLocation(
        res,
        (l) => l.location_type === 'DI' &&
          String(l.district || '').toUpperCase() === selectedDistrict.value.toUpperCase()
      )
      targetStatus = 'IS'
    } else if (destination.value === 'STATION') {
      const res = await apiFetch(
        `/locations/?label=${encodeURIComponent(selectedStation.value)}&location_type=ST`
      )
      targetLocation = findExactLocation(
        res,
        (l) => String(l.label).toUpperCase() === selectedStation.value.toUpperCase() &&
          l.location_type === 'ST'
      )
      targetStatus = 'OP'
    }

    if (!targetLocation?.id) {
      throw new Error('Could not resolve the destination location in the database.')
    }

    await apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify([{
        detector_id: detector.id,
        location_id: targetLocation.id,
        status: targetStatus
      }])
    })

    matchedDetector.value = { ...detector, location_label: targetLocation.label }
    successMessage.value =
      `${detector.label} is now recorded at ${targetLocation.label} and marked as ${DETECTOR_STATUS_WORDS[targetStatus]}.`
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
  successMessage.value = ''
  if (!labelLocked.value) {
    detectorLabel.value = ''
    matchedDetector.value = null
  }
}

// --- Lifecycle ---
onMounted(() => {
  fetchDistricts()
  resolveDetector()
})

watch(urlLabel, () => {
  resetSelections()
  successMessage.value = ''
  errorMessage.value = ''
  showErrorModal.value = false
  showSuccessModal.value = false
  resolveDetector()
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

/* Verified banner */
.verified-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto 14px;
  padding: 12px 14px;
  box-sizing: border-box;
  background: linear-gradient(135deg, #e8f8f2, #f4fbf7);
  border: 1px solid #b7e4d0;
  border-radius: 10px;
}
.verified-tick {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #278257;
  color: #fff;
}
.verified-text { display: grid; gap: 2px; min-width: 0; flex: 1 1 auto; }
.verified-text strong {
  font-size: 0.98rem;
  letter-spacing: 0.05em;
  color: #1e6a46;
  overflow-wrap: break-word;
}
.verified-text span { font-size: 0.82rem; color: #495057; overflow-wrap: break-word; }
.verified-change {
  flex: 0 0 auto;
  min-height: 38px;
  padding: 6px 13px;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: #2f7d5c;
  background: #fff;
  border: 1px solid #b7e4d0;
  border-radius: 7px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.18s ease, border-color 0.18s ease;
}
.verified-change:hover { background: #f1f8f4; border-color: #42b883; }
.verified-change:focus-visible { outline: 2px solid #42b883; outline-offset: 2px; }

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
  font-size: 1rem;
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
.form-input[readonly] {
  background: #eef6f1;
  border-color: #b7e4d0;
  font-weight: 600;
  letter-spacing: 0.05em;
  cursor: default;
}
.field-hint { font-size: 0.8rem; color: #6c757d; margin-top: 6px; }
.loading-inline { font-size: 0.85rem; color: #666; margin-top: 6px; font-style: italic; }

.reveal { animation: fadeUp 0.25s ease-out; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.action-bar { display: flex; gap: 12px; justify-content: flex-end; margin-top: 28px; }
.action-bar .btn-cancel,
.action-bar .btn-primary { flex: 0 1 auto; min-width: 120px; }

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
  scrollbar-color: #42b883 #f1f5f3;
}
.modal-content::-webkit-scrollbar { width: 8px; }
.modal-content::-webkit-scrollbar-track { background: #f1f5f3; border-radius: 8px; }
.modal-content::-webkit-scrollbar-thumb { background: #42b883; border-radius: 8px; }
.modal-content::-webkit-scrollbar-thumb:hover { background: #278257; }
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

@media (max-width: 480px) {
  .swap-screen { padding: 12px 12px calc(24px + env(safe-area-inset-bottom)); }
  .form-container { padding: 18px 14px; border-radius: 10px; }
  .form-group { margin-bottom: 16px; }
  .verified-banner { flex-wrap: wrap; }
  .verified-change { width: 100%; min-height: 44px; }
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
  .reveal { animation: none; }
}
</style>