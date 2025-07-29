<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { url } from '../components/url'

const metrics = ref({})
const loading = ref(true)

const fetchMetrics = async () => {
  try {
    const res = await axios.get(`${url}/admindashboard`)
    if (res.data.success) {
      metrics.value = res.data.metrics
    } else {
      console.log('Failed to fetch dashboard metrics')
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchMetrics)
</script>

<template>
  <div class="dashboard-container">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="cards-grid">
      <div class="card" v-for="(value, key) in metrics" :key="key">
        <h3 class="metric-title">{{ key.replace(/_/g, ' ') }}</h3>
        <p class="metric-value">{{ value }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  background-color: whitesmoke;
  min-height: 50vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 95%;
  max-width: 1200px;
  margin: 2rem auto;
  transition: box-shadow 0.3s ease, filter 0.3s ease;
}

.dashboard-container:hover {
  box-shadow: 0 6px 20px rgba(7, 7, 7, 0.2);
}


.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  width: 80%;
}


.card {
  background-color: #DBF9F1;
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(107, 178, 161, 0.25);
  transition: transform 0.2s ease, background-color 0.3s ease;
}

.card:hover {
  background-color: #C9F7EC;
  transform: translateY(-4px);
}

.metric-title {
  font-size: 1rem;
  color: #7ADEC6;
  text-transform: capitalize;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: bold;
  color: #6BB2A1;
}

.loading {
  font-size: 1.2rem;
  color: #6BB2A1;
}
</style>