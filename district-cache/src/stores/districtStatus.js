import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/utils/api'

export const useDistrictStatusStore = defineStore('districtStatus', () => {
  const models = ref([])
  const selectedModelId = ref(null)
  const district = ref('')
  const diLocation = ref(null)
  const slotCount = ref(0)
  const cacheDetectors = ref([])
  const transitDetectors = ref([])
  const movementLogs = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const totalDetectors = computed(() => cacheDetectors.value.length + transitDetectors.value.length)
  const availableSlots = computed(() => slotCount.value - totalDetectors.value)

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

  const fetchMovementLogs = async () => {
    if (!district.value || !selectedModelId.value) return
    try {
      const twoWeeksAgo = new Date()
      twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14)
      const gteStr = twoWeeksAgo.toISOString()

      // Get all detectors of this model in this district to know their IDs
      const districtDetectors = await apiFetch(
        `/detectors/?detector_model=${selectedModelId.value}&location__district=${encodeURIComponent(district.value)}`
      )
      const detectorIdSet = new Set(districtDetectors.map(d => d.id))

      // Also get detectors that were recently in transit in this district
      const transitDets = await apiFetch(
        `/detectors/?detector_model=${selectedModelId.value}&status=TR&location__district=${encodeURIComponent(district.value)}`
      )
      transitDets.forEach(d => detectorIdSet.add(d.id))

      // Fetch logs for the district in the last 2 weeks
      const logs = await apiFetch(
        `/locationdetectorlogs/?district=${encodeURIComponent(district.value)}&updated_gte=${encodeURIComponent(gteStr)}`
      )

      // Filter to only logs involving detectors of the selected model
      movementLogs.value = logs
        .filter(l => detectorIdSet.has(l.detector))
        .sort((a, b) => new Date(b.updated) - new Date(a.updated))
    } catch (err) {
      console.error('Failed to fetch movement logs:', err)
      movementLogs.value = []
    }
  }

  const fetchAll = async () => {
    await Promise.all([
      fetchSlotCount(),
      fetchCacheAndTransit(),
      fetchMovementLogs()
    ])
  }

  return {
    models, selectedModelId, district, diLocation, slotCount,
    cacheDetectors, transitDetectors, movementLogs,
    isLoading, error, totalDetectors, availableSlots,
    fetchModels, resolveDistrictAndDI, fetchSlotCount,
    fetchCacheAndTransit, fetchMovementLogs, fetchAll
  }
})
