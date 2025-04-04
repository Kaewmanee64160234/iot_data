<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">Sensor Dashboard</h1>

    <!-- Upload Section -->
    <div class="border p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-2">Upload CSV</h2>
      <input type="file" @change="handleFileUpload" accept=".csv" class="mb-2" />
      <button @click="uploadFile" :disabled="!file" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Upload
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white shadow rounded-lg p-4 text-center">
        <h3 class="font-semibold">Temperature (°C)</h3>
        <p>Min: {{ stats.temperature?.min }}</p>
        <p>Max: {{ stats.temperature?.max }}</p>
        <p>Avg: {{ stats.temperature?.mean }}</p>
      </div>
      <div class="bg-white shadow rounded-lg p-4 text-center">
        <h3 class="font-semibold">Humidity (%)</h3>
        <p>Min: {{ stats.humidity?.min }}</p>
        <p>Max: {{ stats.humidity?.max }}</p>
        <p>Avg: {{ stats.humidity?.mean }}</p>
      </div>
      <div class="bg-white shadow rounded-lg p-4 text-center">
        <h3 class="font-semibold">Air Quality</h3>
        <p>Min: {{ stats.air_quality?.min }}</p>
        <p>Max: {{ stats.air_quality?.max }}</p>
        <p>Avg: {{ stats.air_quality?.mean }}</p>
      </div>
    </div>

    <!-- Line Chart (Hourly/Daily) with anomaly points -->
    <div class="border p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Sensor Data Line Chart (with Anomalies)</h2>
      <ApexChart
        v-if="chartOptions && chartSeries.length"
        type="line"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      />
    </div>

    <!-- Past 7-Day Chart (Daily Comparison) -->
    <div class="border p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">7-Day Comparison Chart</h2>
      <ApexChart
        v-if="dailyOptions && dailySeries.length"
        type="line"
        height="350"
        :options="dailyOptions"
        :series="dailySeries"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSensorStore } from '@/stores/sensor.store'
import type { VisualizedSensorData } from '@/types/visualized_data.type'
import { ref, onMounted } from 'vue'
import ApexChart from 'vue3-apexcharts'

const store = useSensorStore()
const file = ref<File | null>(null)
const chartOptions = ref<any>(null)
const chartSeries = ref<any[]>([])
const dailyOptions = ref<any>(null)
const dailySeries = ref<any[]>([])
const stats = ref<any>({})

const handleFileUpload = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    file.value = target.files[0]
  }
}

const uploadFile = async () => {
  if (file.value) {
    await store.uploadCSV(file.value)
    prepareChart()
  }
}

const prepareChart = () => {
  const data = store.visualizedData as VisualizedSensorData[]
  const timestamps = data.map((d) => new Date(d.timestamp)) // Ensure timestamps are Date objects

  chartSeries.value = [
    {
      name: 'Temperature',
      data: data.map((d) => ({ x: new Date(d.timestamp), y: d.temperature_smooth ?? d.temperature })),
      color: '#FF5733'
    },
    {
      name: 'Humidity',
      data: data.map((d) => ({ x: new Date(d.timestamp), y: d.humidity_smooth ?? d.humidity })),
      color: '#2980B9'
    },
    {
      name: 'Air Quality',
      data: data.map((d) => ({ x: new Date(d.timestamp), y: d.air_quality_smooth ?? d.air_quality })),
      color: '#27AE60'
    },
    {
      name: 'Anomalies',
      type: 'scatter',
      data: data.filter(d => d.temperature_anomaly || d.humidity_anomaly || d.air_quality_anomaly)
        .map((d) => ({ x: new Date(d.timestamp), y: d.temperature })),
      color: '#E74C3C'
    }
  ]

  chartOptions.value = {
    chart: { id: 'sensor-data', zoom: { enabled: true } },
    xaxis: { type: 'datetime', labels: { rotate: -45 } },
    tooltip: { shared: true, intersect: false },
    markers: { size: 4 },
    stroke: { curve: 'smooth' }
  }

  // Summary statistics (today only)
  const today = new Date().toISOString().split('T')[0]
  const todayData = data.filter((d) => new Date(d.timestamp).toISOString().startsWith(today)) // Convert timestamp to Date
  stats.value = {
    temperature: summarize(todayData.map(d => d.temperature)),
    humidity: summarize(todayData.map(d => d.humidity)),
    air_quality: summarize(todayData.map(d => d.air_quality))
  }

  // 7-Day Grouping
  const dailyGrouped = groupByDay(data)
  dailySeries.value = Object.entries(dailyGrouped).map(([day, values]) => ({
    name: day,
    data: values.map((v) => ({ x: new Date(v.timestamp).getHours(), y: v.temperature }))
  }))

  dailyOptions.value = {
    chart: { id: 'daily-comparison' },
    xaxis: {
      title: { text: 'Hour' },
      categories: Array.from({ length: 24 }, (_, i) => i.toString())
    },
    stroke: { curve: 'smooth' }
  }
}

function summarize(values: number[]) {
  const mean = +(values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
  const min = Math.min(...values)
  const max = Math.max(...values)
  return { mean, min, max }
}

function groupByDay(data: VisualizedSensorData[]) {
  return data.reduce((acc, item) => {
    const dateKey = new Date(item.timestamp).toISOString().split('T')[0] // Convert timestamp to Date
    if (!acc[dateKey]) acc[dateKey] = []
    acc[dateKey].push(item)
    return acc
  }, {} as Record<string, VisualizedSensorData[]>)
}

onMounted(async () => {
  await store.fetchVisualizedData()
  prepareChart()
})
</script>

<style scoped>
</style>