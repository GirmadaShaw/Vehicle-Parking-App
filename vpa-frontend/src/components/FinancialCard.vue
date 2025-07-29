<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { url } from '../components/url'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const totalRevenue = ref(0)
const chartCanvas = ref(null)
let chartInstance = null

const fetchFinancialStats = async () => {
  try {
    const res = await axios.get(`${url}/financialstats`)
    if (res.data.success) {
      const stats = res.data.data
      totalRevenue.value = stats.total_revenue

      const labels = stats.payment_method_breakdown.map(item => item.method)
      const amounts = stats.payment_method_breakdown.map(item => item.total_amount)

      renderChart(labels, amounts)
    }
  } catch (err) {
    console.error('Error fetching financial stats:', err)
  }
}

const renderChart = (labels, data) => {
  if (chartInstance) chartInstance.destroy()

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Amount Paid',
          data,
          backgroundColor: ['#6BB2A1', '#4B8C7A', '#7ADEC6'],
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: '#4B8C7A', font: { weight: 'bold' } }
        },
        tooltip: {
          callbacks: {
            label: context => `₹${context.raw.toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#4B8C7A', font: { weight: 'bold' } },
          grid: { display: false }
        },
        y: {
          ticks: { color: '#4B8C7A' },
          grid: { color: 'rgba(0,0,0,0.05)' }
        }
      }
    }
  })
}

onMounted(fetchFinancialStats)
</script>

<template>
  <div class="finance-container">
    <div class="revenue-box">Total Revenue: ₹{{ totalRevenue.toFixed(2) }}</div>
    <div class="chart-wrapper">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<style scoped>
.finance-container {
  background: whitesmoke;
  border-radius: 16px;
  padding: 1.5rem;
  height:70vh ;
  width: 95%;
  max-width: 1200px;
  margin: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  position: relative;
  transition: box-shadow 0.3s ease, filter 0.3s ease;
}
.finance-container:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

.revenue-box {
  position: absolute;
  top: 1.2rem;
  left: 1.5rem;
  background: #DBF9F1;
  color: #4B8C7A;
  font-weight: bold;
  font-size: 1.2rem;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 3rem;
  height:65vh;
}

canvas {
  background: #e7e5e5;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  max-width: 700px;
  width: 100%;
  padding: 1rem;
}
</style>
