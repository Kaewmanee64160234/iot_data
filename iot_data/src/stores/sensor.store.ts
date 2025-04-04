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

  const chartData = ref<any[]>([])
  const anomalies = ref<any[]>([])
  const anomalyPoints = ref<any[]>([])

  async function fetchVisualizedData(params?: {
    start_time?: string
    end_time?: string
    metrics?: string[]
    smooth?: boolean
    anomaly_only?: boolean
    latest_only?: boolean
    limit?: number
  }) {
    loading.value = true
    error.value = null
    try {
      clearChartData()
  
      const mergedParams = { ...filterParams.value, ...params }
      const res = await sensorService.getVisualizedSensorData(mergedParams)
      visualizedData.value = res.data
      console.log('visualizedData', visualizedData.value.length);
      console.log('res', res.data);
      
      
    } catch (err) {
      error.value = (err as Error).message || 'Failed to fetch sensor data'
    } finally {
      loading.value = false
    }
  }

  async function uploadCSV(file: File) {
    loading.value = true
    error.value = null
    try {

      await sensorService.uploadSensorCSV(file)
  clearChartData()

      await fetchVisualizedData()
    } catch (err) {
      error.value = (err as Error).message || 'Failed to upload CSV'
    } finally {
      loading.value = false
    }
  }

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
async function fetchSummary(params?: {
  start_time?: string
  end_time?: string
}) {
  clearChartData()
  loading.value = true
  error.value = null
  try {
    const res = await sensorService.getVisualizedSummary(params || {})
    summary.value = res.data
    console.log('summary', res.data);
    
  } catch (err) {
    error.value = (err as Error).message || 'Failed to fetch summary data'
  } finally {
    loading.value = false
  }
}

// clear chart data
function clearChartData() {
  chartData.value = []
  anomalies.value = []
  anomalyPoints.value = []
}

async function fetchAllVisualizedData(params?: {
  start_time?: string
  end_time?: string
  skip?: number
  limit?: number
  order?: string // 'asc' | 'desc'
}) {
  loading.value = true
  error.value = null
  try {
    const res = await sensorService.getAllVisualizedData(params || {})
    visualizedData.value = res.data
    console.log('Fetched all visualized data:', visualizedData.value.length)
  } catch (err) {
    error.value = (err as Error).message || 'Failed to fetch all visualized data'
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
    chartData,
    anomalies,
    anomalyPoints,
    fetchAllVisualizedData,
  }
})
