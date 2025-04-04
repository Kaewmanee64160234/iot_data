<template>
  <div class="p-6 space-y-8 bg-gray-50 min-h-screen">

    <h1 class="text-3xl font-bold text-gray-800">Sensor Dashboard</h1>

    <!-- Upload  -->
    <div class="border p-6 rounded-lg shadow bg-white">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">Upload CSV</h2>
      <div class="flex items-center gap-4">
        <input type="file" @change="handleFileUpload" accept=".csv" class="border px-4 py-2 rounded w-full" />
        <button @click="uploadFile" :disabled="!file"
          class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 disabled:opacity-50">
          Upload
        </button>
      </div>
    </div>

    <!-- Filter  -->
    <div class="border p-6 rounded-lg shadow bg-white grid grid-cols-1 md:grid-cols-3 gap-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
        <input type="date" v-model="filters.start" class="w-full border px-4 py-2 rounded" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
        <input type="date" v-model="filters.end" class="w-full border px-4 py-2 rounded" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Limit</label>
        <input type="number" v-model.number="filters.limit" min="1" max="1000"
          class="w-full border px-4 py-2 rounded" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Latest Only</label>
        <input type="checkbox" v-model="filters.latestOnly" class="w-6 h-6" />
      </div>

      <div class="col-span-3">
        <label class="block text-sm font-medium text-gray-700 mb-1">Metrics</label>
        <div class="flex gap-4">
          <label class="flex items-center gap-2"><input type="checkbox" value="temperature" v-model="filters.metrics" />
            Temperature</label>
          <label class="flex items-center gap-2"><input type="checkbox" value="humidity" v-model="filters.metrics" />
            Humidity</label>
          <label class="flex items-center gap-2"><input type="checkbox" value="air_quality" v-model="filters.metrics" />
            Air Quality</label>
        </div>
      </div>
      <div class="col-span-3 text-right">
        <p v-if="dateError" class="text-red-500 text-sm mb-2">{{ dateError }}</p>
        <button @click="applyFilters" class="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
          :disabled="!!dateError">
          Apply Filters
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white shadow rounded-lg p-6 text-center">
        <h3 class="font-semibold text-lg text-gray-700">Temperature (°C)</h3>
        <p class="text-gray-600">Min: {{ formatStat(stats.temperature?.min) }}</p>
        <p class="text-gray-600">Max: {{ formatStat(stats.temperature?.max) }}</p>
        <p class="text-gray-600">Avg: {{ formatStat(stats.temperature?.mean) }}</p>
      </div>
      <div class="bg-white shadow rounded-lg p-6 text-center">
        <h3 class="font-semibold text-lg text-gray-700">Humidity (%)</h3>
        <p class="text-gray-600">Min: {{ formatStat(stats.humidity?.min) }}</p>
        <p class="text-gray-600">Max: {{ formatStat(stats.humidity?.max) }}</p>
        <p class="text-gray-600">Avg: {{ formatStat(stats.humidity?.mean) }}</p>
      </div>
      <div class="bg-white shadow rounded-lg p-6 text-center">
        <h3 class="font-semibold text-lg text-gray-700">Air Quality</h3>
        <p class="text-gray-600">Min: {{ formatStat(stats.air_quality?.min) }}</p>
        <p class="text-gray-600">Max: {{ formatStat(stats.air_quality?.max) }}</p>
        <p class="text-gray-600">Avg: {{ formatStat(stats.air_quality?.mean) }}</p>
      </div>
    </div>

    <div class="border p-6 rounded-lg shadow bg-white">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">Sensor Data Line Chart (with Anomalies)</h2>
      <ApexChart v-if="chartOptions && chartSeries.length" type="line" height="350" :options="chartOptions"
        :series="chartSeries" />
    </div>

    <div class="border p-6 rounded-lg shadow bg-white">
      <h2 class="text-xl font-semibold text-gray-700 mb-4">📈 7-Day Temperature Comparison</h2>
      <ApexChart v-if="dailyOptions && dailySeries.length" type="line" height="350" :options="dailyOptions"
        :series="dailySeries" />
      <p v-else class="text-gray-400 text-sm">No 7-day comparison data available.</p>
    </div>



    <!-- Loading Spinner -->
    <div v-if="loading" class="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 z-50">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSensorStore } from '@/stores/sensor.store'
import type { VisualizedSensorData } from '@/types/visualized_data.type'
import { ref, onMounted, watch } from 'vue'
import ApexChart from 'vue3-apexcharts'
import Swal from 'sweetalert2'

const store = useSensorStore()
const file = ref<File | null>(null)
const chartOptions = ref<any>(null)
const chartSeries = ref<any[]>([])
const dailyOptions = ref<any>(null)
const dailySeries = ref<any[]>([])
const stats = ref<any>({})
const loading = ref(false)
const dateError = ref<string | null>(null)

const filters = ref({
  start: '',
  end: '',
  metrics: ['temperature', 'humidity', 'air_quality'],
  latestOnly: false,
  limit: 100
})

const handleFileUpload = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    file.value = target.files[0]
  }
}

const uploadFile = async () => {
  if (file.value) {
    await store.uploadCSV(file.value)
    await fetchAndRender()
  }
}

async function applyFilters() {
  await fetchAndRender()
}

async function fetchAndRender() {
  loading.value = true
  try {
    await store.fetchVisualizedData({
      start_time: filters.value.start ? filters.value.start + 'T00:00:00' : undefined,
      end_time: filters.value.end ? filters.value.end + 'T23:59:59' : undefined,
      metrics: filters.value.metrics,
      smooth: true,
      anomaly_only: false,
      latest_only: filters.value.latestOnly,
      limit: filters.value.limit
    })

    if (!store.visualizedData.length) {
      Swal.fire({
        icon: 'info',
        title: 'No Data',
        text: 'No data available for the selected filters.',
      })
      return
    }

    await store.fetchSummary({
      start_time: filters.value.start ? filters.value.start + 'T00:00:00' : undefined,
      end_time: filters.value.end ? filters.value.end + 'T23:59:59' : undefined
    })

    stats.value = store.summary
    await fetch7DayData()

    prepareChart()
  } finally {
    loading.value = false
  }
}

function prepareChart() {
  const data = store.visualizedData
  const timestamps = data.map((d) => new Date(d.timestamp))

  chartSeries.value = []

  if (filters.value.metrics.includes('temperature')) {
    chartSeries.value.push({
      name: 'Temperature',
      data: data.map((d) => ({ x: new Date(d.timestamp), y: d.temperature_smooth ?? d.temperature })),
      color: '#FF5733'
    })
  }
  if (filters.value.metrics.includes('humidity')) {
    chartSeries.value.push({
      name: 'Humidity',
      data: data.map((d) => ({ x: new Date(d.timestamp), y: d.humidity_smooth ?? d.humidity })),
      color: '#2980B9'
    })
  }
  if (filters.value.metrics.includes('air_quality')) {
    chartSeries.value.push({
      name: 'Air Quality',
      data: data.map((d) => ({ x: new Date(d.timestamp), y: d.air_quality_smooth ?? d.air_quality })),
      color: '#27AE60'
    })
  }

  chartSeries.value.push({
    name: 'Anomalies',
    type: 'scatter',
    data: data.filter(d => d.temperature_anomaly || d.humidity_anomaly || d.air_quality_anomaly)
      .map((d) => ({ x: new Date(d.timestamp), y: d.temperature })),
    color: '#E74C3C'
  })

  chartOptions.value = {
    chart: { id: 'sensor-data', zoom: { enabled: true } },
    xaxis: { type: 'datetime', labels: { rotate: -45 } },
    tooltip: { shared: true, intersect: false },
    markers: { size: 4 },
    stroke: { curve: 'smooth' }
  }

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

const fetch7DayData = async () => {
  await store.fetch7DayComparison()
  dailySeries.value = store.sevenDayComparison

  dailyOptions.value = {
    chart: { id: 'daily-comparison' },
    xaxis: {
      title: { text: 'Hour' },
      type: 'numeric',
      tickAmount: 12,
      min: 0,
      max: 23
    },
    yaxis: {
      title: { text: 'Temperature (°C)' }
    },
    stroke: { curve: 'smooth' },
    tooltip: {
      x: { formatter: (val: number) => `Hour ${val}` }
    }
  }
}


function groupByDay(data: VisualizedSensorData[]) {
  return data.reduce((acc, item) => {
    const dateKey = new Date(item.timestamp).toISOString().split('T')[0]
    if (!acc[dateKey]) acc[dateKey] = []
    acc[dateKey].push(item)
    return acc
  }, {} as Record<string, VisualizedSensorData[]>)
}

function formatStat(value: number | undefined | null): string {
  if (value === undefined || value === null || isNaN(value) || !isFinite(value)) {
    return 'N/A'
  }
  return value.toFixed(2)
}

watch(
  () => [filters.value.start, filters.value.end],
  ([start, end]) => {
    if (start && end && new Date(start) > new Date(end)) {
      dateError.value = 'Start date cannot be later than end date.'
    } else {
      dateError.value = null
    }
  }
)

watch(() => store.error, (error) => {
  if (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error,
    })
  }
})

onMounted(async () => {
  await fetchAndRender()
})
</script>

<style scoped>
/* Add styles for the loading spinner */
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>
