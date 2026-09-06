import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/utils/api'

export const useReturnStore = defineStore('return', () => {
  const models = ref([])
  const selectedModelId = ref(null)
  const district = ref('')
  const burnleyLocation = ref(null)
  const trDetectors = ref([])
  const selectedIds = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const selectedCount = computed(() => selectedIds.value.length)

  const fetchModels = async () => {
    try {
      const data = await apiFetch('/detectormodels/')
      models.value = data
      const microRae = data.find(m => m.label === 'MicroRAE')
      selectedModelId.value = microRae?.id || data[0]?.id
    } catch (err) { console.error('Failed to fetch models:', err) }
  }

  const resolveBurnley = async () => {
    error.value = null
    try {
      const burnleyResults = await apiFetch(`/locations/?label=${encodeURIComponent('Burnley')}`)
      burnleyLocation.value = burnleyResults[0] || null
      if (!burnleyLocation.value) error.value = 'Burnley location not found.'
    } catch (err) {
      error.value = 'Failed to resolve Burnley location.'
      console.error(err)
    }
  }

  const fetchTRDetectors = async () => {
    if (!district.value || !selectedModelId.value) return
    isLoading.value = true
    error.value = null
    selectedIds.value = []
    try {
      const data = await apiFetch(`/detector-labels/?status=TR&detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
      trDetectors.value = data
    } catch (err) {
      error.value = 'Failed to fetch in-transit detectors.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const returnDetectors = async (detectorIds) => {
    if (!burnleyLocation.value) throw new Error('Burnley location not found')
    const payload = detectorIds.map(id => ({
      detector_id: id,
      location_id: burnleyLocation.value.id,
      status: 'OF'
    }))
    return apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  const toggleSelection = (id) => {
    const idx = selectedIds.value.indexOf(id)
    if (idx > -1) selectedIds.value.splice(idx, 1)
    else selectedIds.value.push(id)
  }

  return {
    models, selectedModelId, district, burnleyLocation, trDetectors, selectedIds,
    isLoading, error, selectedCount, fetchModels, resolveBurnley, fetchTRDetectors,
    returnDetectors, toggleSelection
  }
})
