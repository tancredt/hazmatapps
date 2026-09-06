import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/utils/api'

export const useRestockStore = defineStore('restock', () => {
  const models = ref([])
  const selectedModelId = ref(null)
  const district = ref('')
  const diLocation = ref(null)
  const slotCount = ref(0)
  const cacheDetectors = ref([])
  const transitDetectors = ref([])
  const burnleyDetectors = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const totalDetectors = computed(() => cacheDetectors.value.length + transitDetectors.value.length)
  const hasSpace = computed(() => totalDetectors.value < slotCount.value)

  const fetchModels = async () => {
    try {
      const data = await apiFetch('/detectormodels/')
      models.value = data
      const microRae = data.find(m => m.label === 'MicroRAE')
      selectedModelId.value = microRae?.id || data[0]?.id
    } catch (err) { console.error('Failed to fetch models:', err) }
  }

  const resolveDistrictAndDI = async (dLabel) => {
    district.value = dLabel
    error.value = null
    try {
      const diResults = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(dLabel)}`)
      diLocation.value = diResults[0] || null
      if (!diLocation.value) error.value = `District Cache not found for district "${dLabel}".`
    } catch (err) {
      error.value = 'Failed to resolve district cache location.'
      console.error(err)
    }
  }

  const fetchSlotCount = async () => {
    if (!diLocation.value || !selectedModelId.value) return
    try {
      const slots = await apiFetch(`/locationdetectorslots/?location=${diLocation.value.id}&detector_model=${selectedModelId.value}`)
      slotCount.value = slots.length
    } catch (err) {
      console.error('Failed to fetch slot count:', err)
      slotCount.value = 0
    }
  }

  const fetchCacheAndTransit = async () => {
    if (!diLocation.value || !selectedModelId.value || !district.value) return
    isLoading.value = true
    error.value = null
    try {
      const [cacheData, transitData] = await Promise.all([
        apiFetch(`/detector-labels/?location=${diLocation.value.id}&detector_model=${selectedModelId.value}`),
        apiFetch(`/detector-labels/?status=TR&detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`)
      ])
      cacheDetectors.value = cacheData
      transitDetectors.value = transitData
    } catch (err) {
      error.value = 'Failed to fetch detectors.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchBurnleyDetectors = async () => {
    if (!selectedModelId.value) return
    try {
      const data = await apiFetch(`/detector-labels/?location__label=Burnley&status=IS&detector_model=${selectedModelId.value}`)
      burnleyDetectors.value = data
    } catch (err) {
      console.error('Failed to fetch Burnley detectors:', err)
      burnleyDetectors.value = []
    }
  }

  const addToCache = async (detectorId) => {
    if (!diLocation.value) throw new Error('District cache location not found')
    return apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify([{ detector_id: detectorId, location_id: diLocation.value.id, status: 'IS' }])
    })
  }

  return {
    models, selectedModelId, district, diLocation, slotCount, cacheDetectors, transitDetectors,
    burnleyDetectors, isLoading, error, totalDetectors, hasSpace, fetchModels, resolveDistrictAndDI,
    fetchSlotCount, fetchCacheAndTransit, fetchBurnleyDetectors, addToCache
  }
})
