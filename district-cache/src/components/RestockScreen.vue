<template>
  <div class="restock-wrapper">
    <header class="app-header">
      <h1>FRV - District Cache Restock</h1>
      <p>{{ district }}</p>
    </header>

    <!-- Model Selector -->
    <div class="selector-bar">
      <select v-model="restock.selectedModelId" @change="reloadData" class="select-input" disabled>
        <option v-for="model in restock.models" :key="model.id" :value="model.id">
          {{ model.label }}
        </option>
      </select>
    </div>

    <div v-if="restock.isLoading" class="state-message">Loading equipment...</div>
    <div v-else-if="restock.error" class="state-message error">{{ restock.error }}</div>
    <div v-else-if="!restock.diLocation" class="state-message error">Could not find district cache.</div>

    <div v-else class="content-area">
      <section class="card">
        <div class="card-header cache-header">
          <h2>District Cache: {{ restock.district }}</h2>
          <span class="badge">{{ restock.cacheDetectors.length }} cached + {{ restock.transitDetectors.length }} in transit / {{ restock.slotCount }} slots</span>
        </div>
        <div class="card-body">
          <!-- Slot Grid -->
          <div class="slots-grid">
            <div 
              v-for="(slot, index) in slots" 
              :key="'slot-' + index"
              class="slot-box"
              :class="{ 
                'slot-occupied': slot.detector && !slot.isTransit, 
                'slot-transit': slot.detector && slot.isTransit,
                'slot-empty': !slot.detector 
              }"
            >
              <span v-if="slot.detector" class="slot-label">
                {{ slot.label }}
                <span v-if="slot.isTransit" class="transit-mark">(in-transit)</span>
              </span>
              <span v-else class="slot-label slot-empty-label">Empty</span>
            </div>
          </div>

          <!-- Overflow -->
          <div v-if="overflowDetectors.length > 0" class="overflow-section">
            <p class="overflow-title">Overflow Detectors</p>
            <div 
              v-for="det in overflowDetectors" 
              :key="det.id"
              class="list-item"
            >
              <span>{{ det.label }} <span class="transit-mark">(in-transit)</span></span>
            </div>
          </div>
        </div>
      </section>

      <div class="action-bar">
        <button @click="handleAddDetector" class="btn-primary btn-large">
          Add Detector
        </button>
      </div>
    </div>

    <!-- Full Cache Error Dialog -->
    <div v-if="showFullError" class="modal-overlay" @click.self="showFullError = false">
      <div class="modal-content">
        <h3>Cache Full</h3>
        <p>The detector cache for district {{ district }} is full.</p>
        <button @click="showFullError = false" class="btn-primary" style="margin-top: 12px; width: 100%;">OK</button>
      </div>
    </div>

    <!-- Burnley Detector Selection Dialog -->
    <div v-if="showBurnleyDialog" class="modal-overlay" @click.self="showBurnleyDialog = false">
      <div class="modal-content dialog-wide">
        <h3>Select Detector from Burnley</h3>
        <div v-if="restock.burnleyDetectors.length === 0" class="empty-state">
          No available detectors at Burnley.
        </div>
        <div v-else class="detector-list dialog-list">
          <button
            v-for="det in restock.burnleyDetectors"
            :key="det.id"
            class="list-item"
            :class="{ selected: selectedBurnleyId === det.id }"
            @click="selectedBurnleyId = det.id"
          >
            <span class="det-label">{{ det.label }}</span>
            <span v-if="selectedBurnleyId === det.id" class="check">✓</span>
          </button>
        </div>
        <div class="modal-actions">
          <button 
            @click="addSelectedToCache" 
            :disabled="!selectedBurnleyId || isAdding"
            class="btn-success"
          >
            {{ isAdding ? 'Adding...' : 'Add to cache' }}
          </button>
          <button @click="showBurnleyDialog = false" class="btn-danger">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Success Dialog -->
    <div v-if="showSuccess" class="modal-overlay" @click.self="showSuccess = false">
      <div class="modal-content">
        <h3>Success</h3>
        <p>Detector has been transferred to district cache.</p>
        <button @click="showSuccess = false" class="btn-primary" style="margin-top: 12px; width: 100%;">OK</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRestockStore } from '../stores/restock'

const props = defineProps({
  district: String
})

const restock = useRestockStore()
const showFullError = ref(false)
const showBurnleyDialog = ref(false)
const showSuccess = ref(false)
const selectedBurnleyId = ref(null)
const isAdding = ref(false)

const slots = computed(() => {
  const count = restock.slotCount
  const cache = restock.cacheDetectors
  const transit = restock.transitDetectors
  const result = []

  for (let i = 0; i < count; i++) {
    if (i < cache.length) {
      result.push({ detector: cache[i], isTransit: false })
    } else if (i < cache.length + transit.length) {
      result.push({ detector: transit[i - cache.length], isTransit: true })
    } else {
      result.push({ detector: null, isTransit: false })
    }
  }
  return result
})

const overflowDetectors = computed(() => {
  const cache = restock.cacheDetectors
  const transit = restock.transitDetectors
  const count = restock.slotCount
  
  if (cache.length >= count) {
    return [...cache.slice(count), ...transit]
  }
  
  const transitInSlots = count - cache.length
  return transit.slice(transitInSlots)
})

const reloadData = async () => {
  await restock.fetchSlotCount()
  await restock.fetchCacheAndTransit()
}

const handleAddDetector = async () => {
  const total = restock.cacheDetectors.length + restock.transitDetectors.length
  if (total >= restock.slotCount) {
    showFullError.value = true
    return
  }
  
  selectedBurnleyId.value = null
  await restock.fetchBurnleyDetectors()
  showBurnleyDialog.value = true
}

const addSelectedToCache = async () => {
  if (!selectedBurnleyId.value) return
  
  isAdding.value = true
  try {
    await restock.addToCache(selectedBurnleyId.value)
    showBurnleyDialog.value = false
    showSuccess.value = true
    await reloadData()
  } catch (err) {
    alert('Failed to add detector to cache.')
  } finally {
    isAdding.value = false
  }
}

onMounted(async () => {
  restock.district = props.district
  await restock.fetchModels()
  await restock.resolveDistrictAndDI(props.district)
  await reloadData()
})
</script>

<style scoped>
.restock-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f3f4f6;
}
.app-header {
  background: #1f2937;
  color: white;
  padding: 16px;
  text-align: center;
}
.app-header h1 {
  margin: 0;
  font-size: 1.25rem;
}
.app-header p {
  margin: 4px 0 0;
  opacity: 0.8;
  font-size: 0.875rem;
}
.selector-bar {
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}
.select-input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}
.content-area {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}
.card-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cache-header {
  background: #dcfce7;
  color: #166534;
}
.card-header h2 {
  margin: 0;
  font-size: 1rem;
}
.badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(0,0,0,0.1);
}
.card-body {
  padding: 16px;
}
.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}
.slot-box {
  min-height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 12px 8px;
  border: 2px solid transparent;
}
.slot-occupied {
  background: #22c55e;
  color: white;
}
.slot-transit {
  background: #f59e0b;
  color: white;
}
.slot-empty {
  background: #ef4444;
  color: white;
}
.slot-label {
  font-size: 0.875rem;
  font-weight: 600;
  word-break: break-word;
  line-height: 1.3;
}
.transit-mark {
  display: block;
  font-size: 0.75rem;
  font-weight: 400;
  opacity: 0.9;
}
.slot-empty-label {
  opacity: 0.9;
  font-weight: 400;
}
.overflow-section {
  border-top: 1px dashed #d1d5db;
  padding-top: 12px;
}
.overflow-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 8px;
}
.list-item {
  width: 100%;
  padding: 12px;
  margin-bottom: 6px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-size: 0.9375rem;
}
.list-item.selected {
  background: #eff6ff;
  border-color: #2563eb;
}
.det-label {
  font-weight: 600;
}
.check {
  color: #2563eb;
  font-weight: 700;
  font-size: 1.125rem;
}
.action-bar {
  padding: 0 16px 16px;
}
.btn-primary {
  width: 100%;
  padding: 14px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
.btn-large {
  font-size: 1.125rem;
  padding: 16px;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}
.modal-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 320px;
  text-align: center;
}
.dialog-wide {
  max-width: 400px;
}
.dialog-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 12px 0;
}
.modal-content h3 {
  margin: 0 0 8px;
}
.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 24px;
}
.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
.btn-success {
  flex: 1;
  padding: 12px;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.btn-success:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
.btn-danger {
  flex: 1;
  padding: 12px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.state-message {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}
.error {
  color: #dc2626;
}
</style>