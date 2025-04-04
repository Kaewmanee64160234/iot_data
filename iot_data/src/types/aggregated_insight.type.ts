export interface AggregatedInsight {
    timestamp: string 
    temperature_min: number | null
    temperature_max: number | null
    temperature_mean: number | null
    temperature_median: number | null
  
    humidity_min: number | null
    humidity_max: number | null
    humidity_mean: number | null
    humidity_median: number | null
  
    air_quality_min: number | null
    air_quality_max: number | null
    air_quality_mean: number | null
    air_quality_median: number | null
  }
  