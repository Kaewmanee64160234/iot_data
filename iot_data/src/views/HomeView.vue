<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">Sensor Dashboard</h1>

    <!-- Upload Section -->
    <div class="border p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-2">Upload CSV</h2>
      <input type="file" @change="handleFileUpload" accept=".csv" class="mb-2" />
      <button
        @click="uploadFile"
        :disabled="!file"
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Upload
      </button>
    </div>

    <!-- Chart Section -->
    <div class="border p-4 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Sensor Data Chart</h2>
      <ApexChart
        v-if="chartOptions && chartSeries.length"
        type="line"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ApexChart from 'vue3-apexcharts'
import { useSensorStore } from '@/stores/sensor.store' // Fixed import
import type { VisualizedSensorData } from '@/types/visualized_data.type'

const store = useSensorStore() // Correctly initialize the store
const file = ref<File | null>(null)
const chartOptions = ref<any>(null)
const chartSeries = ref<any[]>([])

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
  const timestamps = data.map((d) => d.timestamp)

  chartSeries.value = [
    {
      name: 'Temperature',
      data: data.map((d) => d.temperature_smooth ?? d.temperature),
    },
    {
      name: 'Humidity',
      data: data.map((d) => d.humidity_smooth ?? d.humidity),
    },
    {
      name: 'Air Quality',
      data: data.map((d) => d.air_quality_smooth ?? d.air_quality),
    },
  ]

  chartOptions.value = {
    chart: { id: 'sensor-data' },
    xaxis: {
      categories: timestamps,
      type: 'datetime',
      labels: { rotate: -45 },
    },
    stroke: { curve: 'smooth' },
    tooltip: { shared: true, intersect: false },
    markers: { size: 4 },
  }
}

onMounted(async () => {
  await store.fetchVisualizedData()
  prepareChart()
})
</script>

<style scoped></style>
