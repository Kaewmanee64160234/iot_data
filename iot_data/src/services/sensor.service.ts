import type { VisualizedSensorData } from '@/types/visualized_data.type'
import http from './axios'
import type { VisualizedSummary } from '@/types/summary.sensor.types'

function uploadSensorCSV(file: File): Promise<{ message: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/sensor/data', formData, {
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
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ''
    )
  )
  return http.get('/sensor/processed', { params: cleanedParams })
}

function getVisualizedSummary(params: {
  start_time?: string
  end_time?: string
}): Promise<{ data: VisualizedSummary }> {
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ''
    )
  )
  return http.get('/sensor/aggregated', { params: cleanedParams })
}

 function getAllVisualizedData(params: {
  start_time?: string
  end_time?: string
  skip?: number
  limit?: number
  order?: string
}): Promise<{ total: number; data: VisualizedSensorData[] }> {
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(([_, v]) => v !== undefined && v !== null && v !== '')
  )
  return http.get('/sensor/visualized', { params: cleanedParams }).then(res => res.data)
}

function get7DayComparison() {
  return http.get('/sensor/7day-comparison')
}


// export
export default {
  uploadSensorCSV,
  getVisualizedSensorData,
  getVisualizedSummary,
  getAllVisualizedData,
  get7DayComparison,
  
}
