import { defineStore } from 'pinia'
import { ref } from 'vue'

import sensorService from '@/services/sensor.service'
import type { VisualizedSensorData } from '@/types/visualized_data.type'
import type { VisualizedSummary } from '@/types/summary.sensor.types'
import type { AggregatedInsight } from '@/types/aggregated_insight.type'

export const useSensorStore = defineStore('sensor', () => {
  const visualizedData = ref<VisualizedSensorData[]>([])
  const aggregatedInsights = ref<AggregatedInsight[]>([])
  const loading = ref(false)
  const total = ref(0)
  const error = ref<string | null>(null)
  const summary = ref<VisualizedSummary | null>(null)
  const filterParams = ref({
    start_time: '',
    end_time: '',
    metrics: [] as string[],
    smooth: true,
    anomaly_only: false,
  })

  const sevenDayComparison = ref<any[]>([])

  const fetchVisualizedData = async (params?: {
    start_time?: string
    end_time?: string
    metrics?: string[]
    smooth?: boolean
    anomaly_only?: boolean
    latest_only?: boolean
    limit?: number
  }) => {
    loading.value = true
    error.value = null
    try {
      const mergedParams = { ...filterParams.value, ...params }
      const res = await sensorService.getVisualizedSensorData(mergedParams)
      visualizedData.value = res.data
    } catch (err) {
      error.value = (err as Error).message || 'Failed to fetch sensor data'
    } finally {
      loading.value = false
    }
  }

  const uploadCSV = async (file: File) => {
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

  const resetFilters = () => {
    filterParams.value = {
      start_time: '',
      end_time: '',
      metrics: [],
      smooth: true,
      anomaly_only: false,
    }
  }

  const fetchSummary = async (params?: {
    start_time?: string
    end_time?: string
  }) => {
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

  const fetchAllVisualizedData = async (params: {
    start_time?: string
    end_time?: string
    skip?: number
    limit?: number
    order?: string
  }) => {
    loading.value = true
    error.value = null
    try {
      const res = await sensorService.getAllVisualizedData(params)
      visualizedData.value = res.data
      total.value = res.total
      return { total: res.total }
    } catch (err) {
      error.value = (err as Error).message || 'Failed to fetch all visualized data'
      total.value = 0
      return { total: 0 }
    } finally {
      loading.value = false
    }
  }

  const fetch7DayComparison = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await sensorService.get7DayComparison()
      sevenDayComparison.value = res.data
    } catch (err) {
      error.value = (err as Error).message || 'Failed to fetch 7-day comparison chart'
    } finally {
      loading.value = false
    }
  }

  const fetchAggregatedInsight = async (params: {
    window: string
    start_time?: string
    end_time?: string
  }) => {
    loading.value = true
    error.value = null
    try {
      const res = await sensorService.getAggregatedInsight(params)
      aggregatedInsights.value = res
      console.log('aggregatedInsights', aggregatedInsights.value)
    } catch (err) {
      error.value = (err as Error).message || 'Failed to fetch aggregated insights'
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
    fetchSummary,
    summary,
    fetchAllVisualizedData,
    total,
    fetch7DayComparison,
    sevenDayComparison,
    fetchAggregatedInsight,
    aggregatedInsights,
  }
})
