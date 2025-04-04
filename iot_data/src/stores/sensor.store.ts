import { defineStore } from 'pinia'
import { ref } from 'vue'

import sensorService from '@/services/sensor.service'
import type { VisualizedSensorData } from '@/types/visualized_data.type'
import type { VisualizedSummary } from '@/types/summary.sensor.types'

export const useSensorStore = defineStore('sensor', () => {
  const visualizedData = ref<VisualizedSensorData[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const summary = ref<VisualizedSummary | null>(null)
  const filterParams = ref({
    start_time: '',
    end_time: '',
    metrics: [] as string[],
    smooth: true,
    anomaly_only: false,
  })

  // 📥 Load visualized sensor data with filter
  async function fetchVisualizedData(params?: {
    start_time?: string
    end_time?: string
    metrics?: string[]
    smooth?: boolean
    anomaly_only?: boolean
  }) {
    loading.value = true
    error.value = null
    try {
      const mergedParams = { ...filterParams.value, ...params }
      const res = await sensorService.getVisualizedSensorData(mergedParams)
      console.log('Fetched visualized data:', res.data);
      
      visualizedData.value = res.data
    } catch (err) {
      error.value = (err as Error).message || 'Failed to fetch sensor data'
    } finally {
      loading.value = false
    }
  }

  // 📤 Upload sensor CSV
  async function uploadCSV(file: File) {
    loading.value = true
    error.value = null
    try {
      await sensorService.uploadSensorCSV(file)
      await fetchVisualizedData()
    } catch (err) {
      error.value = (err as Error).message || 'Failed to upload CSV'
    } finally {
      loading.value = false
    }
  }

  // 🧹 Reset filters to default
  function resetFilters() {
    filterParams.value = {
      start_time: '',
      end_time: '',
      metrics: [],
      smooth: true,
      anomaly_only: false,
    }
  }

  function setFilters(params: Partial<typeof filterParams.value>) {
    filterParams.value = { ...filterParams.value, ...params }
  }
// 📊 Load summary data
async function fetchSummary(params?: {
  start_time?: string
  end_time?: string
}) {
  loading.value = true
  error.value = null
  try {
    const res = await sensorService.getVisualizedSummary(params || {})
    summary.value = res.data
  } catch (err) {
    error.value = (err as Error).message || 'Failed to fetch summary data'
  } finally {
    loading.value = false
  }
}

  return {
    visualizedData,
    loading,
    error,
    filterParams,
    fetchVisualizedData,
    uploadCSV,
    resetFilters,
    setFilters,
    fetchSummary,
    summary,
  }
})
