import type { VisualizedSensorData } from '@/types/visualized_data.type'
import http from './axios'

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

// export
export default {
  uploadSensorCSV,
  getVisualizedSensorData,
}
