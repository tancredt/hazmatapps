import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/utils/api'

export const useSwapStore = defineStore('swap', () => {
  const models = ref([])
  const selectedModelId = ref(null)
  const stationLocation = ref(null)
  const districtLocation = ref(null)
  const trLocation = ref(null)
  const unknownLocation = ref(null)
  const stationDetectors = ref([])
  const districtDetectors = ref([])
  const stationSlotCount = ref(0)
  const districtSlotCount = ref(0)
  const isLoading = ref(false)
  const error = ref(null)

  const currentModel = computed(() => models.value.find(m => m.id === selectedModelId.value) || null)

  const fetchModels = async () => {
    try {
      const data = await apiFetch('/detectormodels/')
      models.value = data
      const microRae = data.find(m => m.label === 'MicroRAE')
      if (microRae) selectedModelId.value = microRae.id
      else if (data.length > 0 && !selectedModelId.value) selectedModelId.value = data[0].id
    } catch (err) { console.error('Failed to fetch models:', err) }
  }

  const resolveLocations = async (district, locationLabel) => {
    error.value = null
    try {
      // 1. Station Location
      const stationResults = await apiFetch(`/locations/?label=${encodeURIComponent(locationLabel)}&district=${encodeURIComponent(district)}`)
      stationLocation.value = stationResults[0] || null

      // 2. District Cache Location
      const districtResults = await apiFetch(`/locations/?location_type=DI&district=${encodeURIComponent(district)}`)
      districtLocation.value = districtResults[0] || null

      // 3. Transit Location (Specific to this district)
      const trResults = await apiFetch(`/locations/?location_type=TR&district=${encodeURIComponent(district)}`)
      trLocation.value = trResults[0] || null

      // 🎯 4. Unknown Location (Type: ET, District: AL)
      const unknownResults = await apiFetch(`/locations/?location_type=ET&district=AL`)
      unknownLocation.value = unknownResults[0] || null

      // Validation Errors
      if (!stationLocation.value) error.value = `Station location "${locationLabel}" not found.`
      if (!districtLocation.value) error.value = `District Cache not found for district "${district}".`
      if (!trLocation.value) error.value = `Transit (TR) location not found for district "${district}".`
      if (!unknownLocation.value) error.value = `Unknown (ET/AL) location not found in database.`
      
    } catch (err) {
      error.value = 'Failed to resolve locations.'
      console.error(err)
    }
  }



  const fetchSlotCounts = async () => {
    if (!stationLocation.value || !districtLocation.value || !selectedModelId.value) return
    try {
      const [stationSlots, districtSlots] = await Promise.all([
        apiFetch(`/locationdetectorslots/?location=${stationLocation.value.id}&detector_model=${selectedModelId.value}`),
        apiFetch(`/locationdetectorslots/?location=${districtLocation.value.id}&detector_model=${selectedModelId.value}`)
      ])
      stationSlotCount.value = stationSlots.length
      districtSlotCount.value = districtSlots.length
    } catch (err) {
      console.error('Failed to fetch slot counts:', err)
      stationSlotCount.value = 0
      districtSlotCount.value = 0
    }
  }

  const fetchDetectors = async () => {
    if (!stationLocation.value || !districtLocation.value || !selectedModelId.value) return
    isLoading.value = true
    error.value = null
    try {
      await fetchSlotCounts()
      const [stationData, districtData] = await Promise.all([
        apiFetch(`/detector-labels/?location=${stationLocation.value.id}&detector_model=${selectedModelId.value}`),
        apiFetch(`/detector-labels/?location=${districtLocation.value.id}&detector_model=${selectedModelId.value}`)
      ])
      stationDetectors.value = stationData
      districtDetectors.value = districtData
    } catch (err) {
      error.value = 'Failed to fetch detectors.'
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const performSwap = async (detectorId, locationId, status) => {
    return apiFetch('/detectors/update-location-status/', {
      method: 'POST',
      body: JSON.stringify([{ detector_id: detectorId, location_id: locationId, status: status }])
    })
  }

  return {
    models, selectedModelId, stationLocation, districtLocation, trLocation, unknownLocation,
    stationDetectors, districtDetectors, stationSlotCount, districtSlotCount,
    isLoading, error, currentModel, fetchModels, resolveLocations, fetchDetectors, performSwap
  }
})
