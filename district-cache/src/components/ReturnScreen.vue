<template>
  <div class="return-wrapper">
    <header class="app-header">
      <h1>FRV - Detector Return</h1>
      <p>{{ district }}</p>
    </header>

    <!-- Model Selector -->
    <div class="selector-bar">
      <select v-model="ret.selectedModelId" @change="reloadData" class="select-input" disabled>
        <option v-for="model in ret.models" :key="model.id" :value="model.id">
          {{ model.label }}
        </option>
      </select>
    </div>

    <div v-if="ret.isLoading" class="state-message">Loading detectors...</div>
    <div v-else-if="ret.error" class="state-message error">{{ ret.error }}</div>
    <div v-else class="content-area">
      <section class="card">
        <div class="card-header return-header">
          <h2>Select detectors that have been returned to Burnley</h2>
        </div>
        <div class="card-body">
          <div v-if="ret.trDetectors.length === 0" class="empty-state">
            No in-transit detectors found.
          </div>
          <div v-else class="detector-list">
            <button
              v-for="det in ret.trDetectors"
              :key="det.id"
              class="list-item"
              :class="{ selected: ret.selectedIds.includes(det.id) }"
              @click="ret.toggleSelection(det.id)"
            >
              <span class="det-label">{{ det.label }}</span>
              <span v-if="ret.selectedIds.includes(det.id)" class="check">✓</span>
            </button>
          </div>
        </div>
      </section>
    </div>

    <footer class="app-footer" v-if="!ret.isLoading && ret.trDetectors.length > 0">
      <button 
        @click="showConfirm = true" 
        :disabled="ret.selectedIds.length === 0 || isProcessing"
        class="btn-primary btn-large"
      >
        {{ isProcessing ? 'Processing...' : `Return (${ret.selectedIds.length})` }}
      </button>
    </footer>

    <!-- Confirmation Modal -->
    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
      <div class="modal-content">
        <h3>Confirm Return</h3>
        <p>Ensure detectors are placed in the correct return bin</p>
        <div class="modal-actions">
          <button @click="executeReturn" class="btn-success">OK</button>
          <button @click="showConfirm = false" class="btn-danger">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useReturnStore } from '../stores/return'

const props = defineProps({
  district: String
})

const ret = useReturnStore()
const showConfirm = ref(false)
const isProcessing = ref(false)

const reloadData = async () => {
  ret.selectedIds.value = []
  await ret.fetchTRDetectors()
}

const executeReturn = async () => {
  isProcessing.value = true
  showConfirm.value = false

  try {
    await ret.returnDetectors([...ret.selectedIds])
    ret.selectedIds = []
    await ret.fetchTRDetectors()
    alert('Detectors returned to Burnley successfully.')
  } catch (error) {
    alert('Failed to return detectors. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

onMounted(async () => {
  ret.district = props.district
  await ret.fetchModels()
  await ret.resolveBurnley()
  await ret.fetchTRDetectors()
})
</script>

<style scoped>
.return-wrapper {
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
}
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}
.card-header {
  padding: 14px 16px;
}
.return-header {
  background: #fef3c7;
  color: #92400e;
}
.card-header h2 {
  margin: 0;
  font-size: 1rem;
}
.card-body {
  padding: 16px;
}
.empty-state {
  text-align: center;
  color: #6b7280;
  padding: 24px;
}
.detector-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.list-item {
  width: 100%;
  padding: 14px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.15s;
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
.app-footer {
  padding: 16px;
  background: white;
  border-top: 1px solid #e5e7eb;
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
.modal-content h3 {
  margin: 0 0 8px;
}
.modal-content p {
  margin: 0 0 16px;
  color: #4b5563;
}
.modal-actions {
  display: flex;
  gap: 12px;
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