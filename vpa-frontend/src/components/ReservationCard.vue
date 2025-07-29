<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Chart, PieController, ArcElement, Tooltip, Legend, BarController, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { url } from '../components/url'

Chart.register(PieController, ArcElement, Tooltip, Legend, BarController, BarElement, CategoryScale, LinearScale)

const pieChartRef = ref(null)
const barChartRef = ref(null)
const reservations = ref([])

const fetchReservations = async () => {
  try {
    const res = await axios.get(`${url}/getreservations`)
    if (res.data.success) {
      reservations.value = res.data.reservations
      renderCharts()
    }
  } catch (err) {
    console.error('Error fetching reservations:', err)
  }
}

const renderCharts = () => {
  const statusCounts = { occupied: 0, available: 0 }
  const lotStatus = {}

  reservations.value.forEach(r => {
    statusCounts[r.status] = (statusCounts[r.status] || 0) + 1
    if (!lotStatus[r.lot]) lotStatus[r.lot] = { occupied: 0, available: 0 }
    lotStatus[r.lot][r.status]++
  })


  new Chart(pieChartRef.value, {
    type: 'pie',
    data: {
      labels: ['Occupied', 'Available'],
      datasets: [{
        data: [statusCounts.occupied, statusCounts.available],
        backgroundColor: ['#6BB2A1', '#7ADEC6'],
        borderColor: '#fff',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } }
    }
  })

  const lots = Object.keys(lotStatus)
  const occupied = lots.map(l => lotStatus[l].occupied)
  const available = lots.map(l => lotStatus[l].available)

  new Chart(barChartRef.value, {
    type: 'bar',
    data: {
      labels: lots,
      datasets: [
        { label: 'Occupied', data: occupied, backgroundColor: '#6BB2A1' },
        { label: 'Available', data: available, backgroundColor: '#7ADEC6' }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true }
      }
    }
  })
}

onMounted(fetchReservations)
</script>

<template>
  <div class="chart-container">
    <div class="chart-box">
      <canvas ref="pieChartRef"></canvas>
    </div>
    <div class="chart-box">
      <canvas ref="barChartRef"></canvas>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  background: whitesmoke;
  border-radius: 16px;
  padding: 1.5rem;
  width: 95%;
  max-width: 1200px;
  margin: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  display: flex;
  gap: 10rem; /* space between charts */
  justify-content: center;
  align-items: center;
  transition: box-shadow 0.3s ease, filter 0.3s ease;
}
.chart-container:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}
.chart-box {
  background: #e7e5e5;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  width: 45%; 
  height: 300px; 
}
canvas {
  max-width: 100%;
  max-height: 100%;
}
</style>
