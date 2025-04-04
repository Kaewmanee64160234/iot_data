<template>
  <div class="p-6 space-y-8">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold">Sensor Data</h2>
      <div class="flex space-x-4">
        <label>
          <input type="checkbox" v-model="latestOnly" />
          Latest Only
        </label>
        <label>
          Skip:
          <input type="number" v-model.number="skip" min="0" class="border px-2 py-1 rounded" />
        </label>
        <label>
          Limit:
          <input type="number" v-model.number="limit" min="1" max="1000" class="border px-2 py-1 rounded" />
        </label>
        <button @click="fetchData" class="bg-blue-500 text-white px-4 py-2 rounded">Fetch</button>
      </div>
    </div>

    <ApexChart
      v-if="chartSeries.length"
      type="line"
      height="400"
      :options="chartOptions"
      :series="chartSeries"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSensorStore } from '@/stores/sensor.store'
import ApexChart from 'vue3-apexcharts'

const store = useSensorStore()
const latestOnly = ref(false)
const skip = ref(0)
const limit = ref(100)
const chartSeries = ref<any[]>([])

const chartOptions = computed(() => ({
  chart: {
    id: 'sensor-chart',
    zoom: { enabled: true },
    toolbar: { show: true }
  },
  xaxis: {
    type: 'datetime',
    title: { text: 'Time' },
    labels: { rotate: -45 }
  },
  yaxis: {
    title: { text: 'Values' }
  },
  tooltip: {
    shared: true
  },
  stroke: {
    curve: 'smooth'
  }
}))

async function fetchData() {
  await store.fetchVisualizedData({
    latest_only: latestOnly.value,
    skip: skip.value,
    limit: limit.value
  })

  chartSeries.value = [
    {
      name: 'Temperature',
      data: store.visualizedData.map((item) => ({
        x: new Date(item.timestamp),
        y: item.temperature
      }))
    },
    {
      name: 'Humidity',
      data: store.visualizedData.map((item) => ({
        x: new Date(item.timestamp),
        y: item.humidity
      }))
    },
    {
      name: 'Air Quality',
      data: store.visualizedData.map((item) => ({
        x: new Date(item.timestamp),
        y: item.air_quality
      }))
    }
  ]
}

fetchData()
</script>

<style scoped>
input {
  width: 80px;
}
button {
  cursor: pointer;
}
</style>
