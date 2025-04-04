<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useSensorStore } from '@/stores/sensor.store'

const store = useSensorStore()

const filters = ref({
  start_time: '',
  end_time: '',
  page: 1,
  perPage: 30,
  sort_order: 'desc' 
})


const skip = computed(() => (filters.value.page - 1) * filters.value.perPage)

const data = computed(() => store.visualizedData)
const loading = computed(() => store.loading)
const error = computed(() => store.error)

const fetchData = async () => {
  await store.fetchAllVisualizedData({
    start_time: filters.value.start_time,
    end_time: filters.value.end_time,
    skip: skip.value,
    limit: filters.value.perPage,
    order: filters.value.sort_order
  })
}

const nextPage = () => {
  filters.value.page++
  fetchData()
}

const prevPage = () => {
  if (filters.value.page > 1) {
    filters.value.page--
    fetchData()
  }
}

onMounted(() => {
  fetchData()
})
</script>
<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <h1 class="text-2xl font-bold mb-6 text-gray-800">📊 Visualized Sensor Data</h1>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-6 grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div>
        <label class="block font-medium text-sm mb-1">Start Time</label>
        <input v-model="filters.start_time" type="datetime-local" class="w-full border px-3 py-2 rounded" />
      </div>
      <div>
        <label class="block font-medium text-sm mb-1">End Time</label>
        <input v-model="filters.end_time" type="datetime-local" class="w-full border px-3 py-2 rounded" />
      </div>
      <div>
  <label class="block font-medium text-sm mb-1">Sort Order</label>
  <select v-model="filters.sort_order" class="w-full border px-3 py-2 rounded">
    <option value="desc">Newest First</option>
    <option value="asc">Oldest First</option>
  </select>
</div>

      <div class="flex items-end">
        <button @click="fetchData" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded w-full">
          Fetch Data
        </button>
      </div>
    </div>

    <!-- Loading & Error -->
    <div v-if="loading" class="text-blue-600 font-medium">Loading data...</div>
    <div v-if="error" class="text-red-500 font-semibold">{{ error }}</div>

    <!-- Data Table -->
    <div v-if="data.length" class="overflow-x-auto bg-white shadow rounded-lg">
      <table class="min-w-full table-auto text-sm text-left border">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-2 border">Timestamp</th>
            <th class="px-4 py-2 border">Temperature</th>
            <th class="px-4 py-2 border">Humidity</th>
            <th class="px-4 py-2 border">Air Quality</th>
            <th class="px-4 py-2 border">Anomaly</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in data" :key="index" class="hover:bg-gray-50">
            <td class="px-4 py-2 border">{{ new Date(item.timestamp).toLocaleString() }}</td>
            <td class="px-4 py-2 border">{{ item.temperature ?? 'N/A' }}</td>
            <td class="px-4 py-2 border">{{ item.humidity ?? 'N/A' }}</td>
            <td class="px-4 py-2 border">{{ item.air_quality ?? 'N/A' }}</td>
            <td class="px-4 py-2 border">
              <span v-if="item.temperature_anomaly || item.humidity_anomaly || item.air_quality_anomaly" class="text-red-600 font-semibold">⚠️</span>
              <span v-else class="text-green-500">✔️</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="data.length" class="flex justify-between items-center mt-4">
      <button @click="prevPage" :disabled="filters.page === 1" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50">Previous</button>
      <span>Page {{ filters.page }}</span>
      <button @click="nextPage" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Next</button>
    </div>

    <div v-else-if="!loading && !error" class="text-gray-500 mt-4">No data available for selected filters.</div>
  </div>
</template>
