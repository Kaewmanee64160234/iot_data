export interface VisualizedSensorData {
  id: number
  timestamp: Date
  temperature: number
  humidity: number
  air_quality: number
  temperature_smooth: number
  humidity_smooth: number
  air_quality_smooth: number
  temperature_anomaly: boolean
  humidity_anomaly: boolean
  air_quality_anomaly: boolean
}
