export interface SummaryStats {
    min: number | null
    max: number | null
    mean: number | null
  }
  
  export interface VisualizedSummary {
    temperature: SummaryStats
    humidity: SummaryStats
    air_quality: SummaryStats
  }
  