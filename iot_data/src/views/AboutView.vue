<template>
  <div
    class="p-6 min-h-screen bg-cover bg-center flex items-center justify-center"
    :style="{ backgroundImage: isImageLoaded ? `url(${backgroundImage})` : '' }"
    ref="backgroundRef"
  >
    <!-- Weather Info -->
    <div class="bg-white/60 backdrop-blur-md p-6 rounded-lg shadow text-center w-96 h-96 flex flex-col justify-center">
      <h1 class="text-3xl font-bold mb-2">Weather Overview</h1>

      <div class="text-xl mb-4">
        <div class="text-gray-800 font-medium">{{ formattedDate }}</div>
        <div class="text-2xl font-bold">{{ formattedTime }}</div>
      </div>

      <div class="text-4xl font-bold">
        {{ summary.temperature }}°C
        <span class="text-sm text-gray-600 block font-medium">Temperature</span>
      </div>

      <div class="mt-2">
        <div class="text-xl">💧 {{ summary.humidity }}%</div>
        <div class="text-sm text-gray-600">Humidity</div>
      </div>

      <div class="mt-2">
        <div class="text-xl">🌀 AQI {{ summary.aqi }}</div>
        <div class="text-sm" :class="aqiColor(summary.aqi).text">{{ aqiColor(summary.aqi).label }}</div>
      </div>

      <div class="mt-4 text-xs text-gray-500">
        Last updated: {{ lastUpdated }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSensorStore } from '@/stores/sensor.store'
import type { VisualizedSensorData } from '@/types/visualized_data.type'

const store = useSensorStore()
const summary = ref({ temperature: 'N/A', humidity: 'N/A', aqi: 'N/A' })
const lastUpdated = ref('')
const backgroundImage = ref('/default.jpg')
const isImageLoaded = ref(false)
const backgroundRef = ref<HTMLElement | null>(null)

const formattedDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

const formattedTime = computed(() => {
  const now = new Date()
  return now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
})

function aqiColor(aqi: number | string) {
  const val = Number(aqi)
  if (isNaN(val)) return { text: 'text-gray-500', label: 'N/A' }
  if (val <= 50) return { text: 'text-green-600', label: 'Good' }
  if (val <= 100) return { text: 'text-yellow-500', label: 'Moderate' }
  if (val <= 150) return { text: 'text-orange-500', label: 'Unhealthy for Sensitive Groups' }
  if (val <= 200) return { text: 'text-red-500', label: 'Unhealthy' }
  if (val <= 300) return { text: 'text-purple-500', label: 'Very Unhealthy' }
  return { text: 'text-pink-700', label: 'Hazardous' }
}

function setBackground(temp: number | string) {
  const t = Number(temp)
  if (isNaN(t)) return (backgroundImage.value = '/default.jpg')
  if (t >= 30) backgroundImage.value = '/sunny.jpg'
  else if (t >= 20) backgroundImage.value = '/cloudy.jpg'
  else backgroundImage.value = '/rainy.jpg'
}

onMounted(async () => {
  await store.fetchVisualizedData()
  const latest = store.visualizedData.slice(-1)[0] as VisualizedSensorData | undefined
  if (latest) {
    summary.value = {
      temperature: latest.temperature?.toFixed(1),
      humidity: latest.humidity?.toFixed(1),
      aqi: latest.air_quality?.toFixed(1)
    }
    lastUpdated.value = new Date(latest.timestamp).toLocaleString()
    setBackground(latest.temperature)
  } else {
    summary.value = { temperature: 'N/A', humidity: 'N/A', aqi: 'N/A' }
    backgroundImage.value = '/default.jpg'
  }

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        isImageLoaded.value = true
        observer.disconnect()
      }
    },
    { threshold: 0.1 }
  )
  if (backgroundRef.value) observer.observe(backgroundRef.value)
})
</script>

<style scoped>
body {
  font-family: 'Segoe UI', sans-serif;
}
</style>
