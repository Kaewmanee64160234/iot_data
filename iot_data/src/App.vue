<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <!-- Navigation Bar -->
  <nav class="bg-blue-500 text-white p-4 shadow">
    <div class="container mx-auto flex justify-between items-center">
      <h1 class="text-2xl font-bold">Sensor Dashboard</h1>
      <ul class="flex space-x-4">
        <li>
          <RouterLink to="/" class="hover:underline">Home</RouterLink>
        </li>
        <li>
          <RouterLink to="/sensor" class="hover:underline">Sensor Data</RouterLink>
        </li>
        <li>
          <RouterLink to="/visualized" class="hover:underline">Visualized Data</RouterLink>
        </li>
        <li>
          <a href="http://localhost:8000/docs" target="_blank" class="hover:underline">API Docs</a>
        </li>
      </ul>
    </div>
  </nav>

  <!-- Main Content -->
  <RouterView />
</template>

<style scoped>
nav {
  font-family: 'Segoe UI', sans-serif;
}

a {
  text-decoration: none;
  color: white;
}

a:hover {
  text-decoration: underline;
}
</style>


