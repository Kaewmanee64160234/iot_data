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
  // Remove empty strings before sending request
  const cleanedParams = Object.fromEntries(
    Object.entries(params).filter(
      ([_, v]) => v !== undefined && v !== null && v !== ''
    )
  )
  return http.get('/sensor/processed', { params: cleanedParams })
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
  return http.get('/sensor/aggregated', { params: cleanedParams })
}




// export
export default {
  uploadSensorCSV,
  getVisualizedSensorData,
  getVisualizedSummary,
}
