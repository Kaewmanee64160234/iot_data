import type { VisualizedSensorData } from '@/types/visualized_data.type'
import http from './axios'
import type { VisualizedSummary } from '@/types/summary.sensor.types'

function uploadSensorCSV(file: File): Promise<{ message: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/sensor/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

function getVisualizedSensorData(params: {
  start_time?: string
  end_time?: string
  metrics?: string[]
  smooth?: boolean
  anomaly_only?: boolean
}): Promise<{ data: VisualizedSensorData[] }> {
  // Remove empty strings before sending request
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ''
    )
  )
  return http.get('/sensor/visualized', { params: cleanedParams })
}

// create a new function to get visualized sensor data with summary
function getVisualizedSummary(params: {
  start_time?: string
  end_time?: string
}): Promise<{ data: VisualizedSummary }> {
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ''
    )
  )
  return http.get('/sensor/visualized/summary', { params: cleanedParams })
}

function getChartData(params: {
  start_time?: string
  end_time?: string
  resolution?: 'hourly' | 'daily'
}) {
  return http.get('/sensor/visualized/chart-data', { params })
}

function getChartDataWithAnomalies(params: {
  start_time?: string
  end_time?: string
  resolution?: 'hourly' | 'daily'
}): Promise<{ graph: any[]; anomalies: any[] }> {
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ''
    )
  )
  return http.get('/sensor/visualized/chart-data', { params: cleanedParams })
}

// export
export default {
  uploadSensorCSV,
  getVisualizedSensorData,
  getVisualizedSummary,
  getChartData,
  getChartDataWithAnomalies,
}
