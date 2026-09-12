<template>
  <div class="swap-screen">
    <h2>FRV - District Cache Restock</h2>
    <h3>{{ district }}</h3>

    <div class="model-selector">
      <label>Detector Model:</label>
      <select v-model="restock.selectedModelId" @change="handleModelChange">
        <option v-for="model in restock.models" :key="model.id" :value="model.id">
          {{ model.label }}
        </option>
      </select>
    </div>

    <div v-if="restock.isLoading" class="loading">Loading equipment...</div>
    <div v-if="restock.error" class="error">{{ restock.error }}</div>

    <div v-if="!restock.isLoading && !restock.error">
      <!-- ================= DISTRICT CACHE SECTION ================= -->
      <div class="location-section">
        <h3>District Cache: {{ district }}</h3>
        <p class="section-subtitle">
          {{ restock.cacheDetectors.length }} cached + {{ restock.transitDetectors.length }} in transit / {{ restock.slotCount }} slots
          ({{ restock.availableSlots }} available)
        </p>

        <!-- Slot Rectangles for Cache -->
        <div class="slots-grid">
          <div
            v-for="i in restock.slotCount"
            :key="'cache-slot-' + i"
            class="slot-rectangle"
            :class="{
              empty: !allDistrictDetectors[i-1],
              transit: allDistrictDetectors[i-1]?.isTransit
            }"
          >
            <template v-if="allDistrictDetectors[i-1]">
              <span class="slot-label">{{ allDistrictDetectors[i-1].label }}</span>
              <span v-if="allDistrictDetectors[i-1].isTransit" class="transit-badge">In Transit</span>
            </template>
            <template v-else>
              Empty
            </template>
          </div>
        </div>

        <!-- Overflow Area -->
        <div v-if="overflowDetectors.length > 0" class="overflow-area">
          <h4>Overflow Detectors ({{ overflowDetectors.length }})</h4>
          <div class="overflow-list">
            <div
              v-for="det in overflowDetectors"
              :key="'ov-' + det.id"
              class="overflow-item"
              :class="{ 'transit-item': det.isTransit }"
            >
              {{ det.label }}
              <span v-if="det.isTransit" class="transit-badge-small">In Transit</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= BURNLEY SELECTION SECTION ================= -->
      <div class="location-section" style="margin-top: 20px;">
        <h3>Available at Burnley</h3>
        <p class="section-subtitle">Select detectors to add to the cache ({{ restock.selectedCount }} selected)</p>
        <div v-if="restock.burnleyDetectors.length > 0" class="overflow-list" style="margin-top: 15px;">
          <div
            v-for="det in restock.burnleyDetectors"
            :key="'burnley-' + det.id"
            class="overflow-item"
            :class="{ selected: restock.selectedBurnleyIds.includes(det.id) }"
            @click="restock.toggleBurnleySelection(det.id)"
          >
            {{ det.label }}
          </div>
        </div>
        <p v-else class="empty-text">No available detectors at Burnley.</p>
      </div>

      <!-- ACTION BUTTON -->
      <div class="action-bar">
        <button
          class="btn-primary"
          @click="attemptAddToCache"
          :disabled="isProcessing || restock.isLoading || !!restock.error || restock.selectedCount === 0"
        >
          {{ isProcessing ? 'Adding...' : `Add to Cache (${restock.selectedCount})` }}
        </button>
      </div>
    </div>

    <!-- ================= WARNING MODAL (TOO MANY) ================= -->
    <div v-if="showWarningModal" class="modal-overlay">
      <div class="modal-content warning-modal">
        <div class="warning-icon">⚠️</div>
        <h3>Cache Capacity Exceeded</h3>
        <p>
          You have selected {{ restock.selectedCount }} detector(s), but adding them would bring the total
          to {{ restock.totalDetectors + restock.selectedCount }} which exceeds the {{ restock.slotCount }} available slots.
          <br><br>
          Currently: {{ restock.cacheDetectors.length }} cached + {{ restock.transitDetectors.length }} in transit = {{ restock.totalDetectors }} detectors.
          <br>
          Available slots remaining: {{ restock.availableSlots }}.
        </p>
        <div class="modal-actions">
          <button class="btn-danger" @click="showWarningModal = false">OK</button>
        </div>
      </div>
    </div>

    <!-- ================= CONFIRMATION MODAL ================= -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal-content">
        <h3>Confirm Restock</h3>
        <p>You have selected {{ restock.selectedCount }} detector(s) to transfer to the {{ district }} district cache.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirmModal = false" :disabled="isProcessing">Cancel</button>
          <button class="btn-confirm" @click="executeRestock" :disabled="isProcessing">
            {{ isProcessing ? 'Transferring...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ================= SUCCESS MODAL ================= -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Success</h3>
        <p>{{ restock.selectedCount }} detector(s) have been transferred to the district cache.</p>
        <div class="modal-actions">
          <button class="btn-confirm" @click="closeSuccessModal">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRestockStore } from '../stores/restock'

const props = defineProps({ district: String })
const restock = useRestockStore()

const isProcessing = ref(false)
const showWarningModal = ref(false)
const showConfirmModal = ref(false)
const showSuccessModal = ref(false)

// Combine cache + transit detectors, marking transit ones
const allDistrictDetectors = computed(() => {
  const cached = restock.cacheDetectors.map(d => ({ ...d, isTransit: false }))
  const transit = restock.transitDetectors.map(d => ({ ...d, isTransit: true }))
  return [...cached, ...transit]
})

const overflowDetectors = computed(() => allDistrictDetectors.value.slice(restock.slotCount))
const slottedDetectors = computed(() => allDistrictDetectors.value.slice(0, restock.slotCount))

const handleModelChange = () => {
  restock.clearSelection()
  restock.fetchCacheAndTransit()
  restock.fetchBurnleyDetectors()
}

const attemptAddToCache = () => {
  if (restock.selectedCount === 0) return

  // Check if adding selected detectors would exceed slot count
  if (!restock.hasSpace) {
    showWarningModal.value = true
    return
  }

  showConfirmModal.value = true
}

const executeRestock = async () => {
  isProcessing.value = true
  try {
    await restock.addToCache()
    showConfirmModal.value = false
    showSuccessModal.value = true
  } catch (err) {
    console.error('Failed to add to cache:', err)
    alert('Failed to add detectors. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  restock.clearSelection()
  restock.fetchCacheAndTransit()
  restock.fetchBurnleyDetectors()
}

onMounted(async () => {
  await restock.fetchModels()
  await restock.resolveDistrictAndDI(props.district)
  await restock.fetchSlotCount()
  await restock.fetchCacheAndTransit()
  await restock.fetchBurnleyDetectors()
})
</script>

<style scoped>
.swap-screen { padding: 20px; font-family: system-ui, -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; color: #333; }
.model-selector { margin-bottom: 20px; }
.model-selector select { padding: 8px 12px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc; }
.location-section { flex: 1; min-width: 320px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
.section-subtitle { color: #666; margin-top: -5px; margin-bottom: 15px; font-size: 0.95rem; }
.empty-text { color: #adb5bd; font-style: italic; text-align: center; padding: 20px 0; }

.slots-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 15px; }
.slot-rectangle {
  width: 110px; height: 80px; border: 2px solid #adb5bd; border-radius: 6px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  font-size: 0.9rem; font-weight: 600; background: #ffffff; color: #333;
  padding: 5px; box-sizing: border-box; word-break: break-word;
}
.slot-rectangle.empty {
  color: #adb5bd; font-style: italic; font-weight: 400; background: #f8f9fa; border-style: dashed;
}
.slot-rectangle.transit {
  border-color: #f39c12; background: #fef9e7;
}
.slot-label { font-weight: 600; }
.transit-badge {
  font-size: 0.65rem; font-weight: 500; color: #e67e22; background: #fdebd0;
  padding: 2px 6px; border-radius: 8px; margin-top: 3px;
}

.overflow-area { margin-top: 25px; padding-top: 15px; border-top: 1px dashed #ced4da; }
.overflow-area h4 { margin: 0 0 12px 0; color: #d35400; font-size: 1rem; font-weight: 600; }
.overflow-list { display: flex; flex-wrap: wrap; gap: 10px; }
.overflow-item {
  padding: 8px 14px; background: #fff3cd; border: 1px solid #ffeeba; border-radius: 20px;
  cursor: pointer; font-size: 0.9rem; font-weight: 500; color: #333; transition: all 0.2s;
  -webkit-tap-highlight-color: transparent; user-select: none;
}
.overflow-item:hover { background: #ffe69c; transform: translateY(-1px); }
.overflow-item.selected { background: #e8f8f2; color: #333; border-color: #42b883; border-width: 2px; }
.overflow-item.transit-item { background: #fef9e7; border-color: #f39c12; }
.transit-badge-small {
  font-size: 0.65rem; color: #e67e22; font-weight: 600; margin-left: 4px;
}

.action-bar { margin-top: 30px; text-align: center; }
.btn-primary {
  padding: 12px 32px; background: #42b883; color: white; border: none; border-radius: 6px;
  font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #38a373; }
.btn-primary:disabled { background: #ccc; cursor: not-allowed; }

.loading, .error { text-align: center; padding: 20px; font-size: 1.1rem; }
.error { color: #e74c3c; background: #fdecea; border-radius: 6px; }

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  padding: 20px; animation: fadeIn 0.2s ease-out;
}
.modal-content {
  background: white; padding: 24px; border-radius: 12px; width: 100%; max-width: 420px;
  text-align: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2); animation: slideUp 0.2s ease-out;
}
.modal-content h3 { margin: 0 0 12px 0; color: #333; font-size: 1.25rem; }
.modal-content p { color: #666; margin-bottom: 20px; font-size: 1rem; line-height: 1.5; }
.modal-actions { display: flex; gap: 12px; }
.btn-cancel, .btn-confirm {
  flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 1rem;
  font-weight: 600; cursor: pointer; transition: opacity 0.2s;
}
.btn-cancel { background: #e9ecef; color: #495057; }
.btn-confirm { background: #42b883; color: white; }
.btn-cancel:disabled, .btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

/* Warning modal styles */
.warning-modal { border: 2px solid #e74c3c; }
.warning-icon { font-size: 4rem; margin-bottom: 10px; }
.warning-modal h3 { color: #e74c3c; }
.btn-danger {
  flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 1rem;
  font-weight: 600; cursor: pointer; background: #e74c3c; color: white;
}
.btn-danger:hover { background: #c0392b; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>