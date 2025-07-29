<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'
import { url } from '../components/url'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const toast = useToast()
const cards = ref([])
const chartCanvas = ref(null)
const upcomingBookings = ref([])
const router = useRouter()
const selectedLocation = ref(""); 
let first_name = ref('')


onMounted(async () => {
  try {
    const res = await axios.get(`${url}/userdashboard`, {
      withCredentials: true,
    })

    const data = res.data
    // const data = {
    //   first_name: 'Dum',
    //   total_bookings: 23,
    //   total_hours_parked: 102,
    //   active_bookings: 3,
    //   most_visited_location: 'Pune Central',
    //   monthly_chart_data: [
    //     { month: 'Jan', count: 5 },
    //     { month: 'Feb', count: 10 },
    //     { month: 'March', count: 15 },
    //     { month: 'Apr', count: 20 },
    //     { month: 'Jun', count: 50 },
    //     { month: 'Jul', count: 40 },
    //     { month: 'Aug', count: 10 },
    //     { month: 'Sept', count: 90 },
    //     { month: 'Oct', count: 15 },
    //     { month: 'Nov', count: 1 },
    //   ],
    // }

    first_name = data.first_name
    cards.value = [
      { title: 'Total Bookings', value: data.total_bookings },
      { title: 'Total Hours Parked', value: data.total_hours_parked },
      { title: 'Active Bookings', value: data.active_bookings },
      { title: 'Most Visited Location', value: data.most_visited_location },
    ]

    new Chart(chartCanvas.value, {
      type: 'bar',
      data: {
        labels: data.monthly_chart_data.map((d) => d.month),
        datasets: [
          {
            label: 'Bookings per Month',
            data: data.monthly_chart_data.map((d) => d.count),
            backgroundColor: '#7ADEC6',
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true },
        },
      },
    })
  } catch (err) {
    console.error('Error fetching dashboard data: ', err)
  }
})

async function getUpcomingBookings() {
  try {
    const res = await axios.get(`${url}/userupcomingbookings`, {
      withCredentials: true,
    })

    upcomingBookings.value = res.data
    // upcomingBookings.value = [
    //   {
    //     location: 'Downtown Parking Garage',
    //     slot: 'Slot A1',
    //     start_time: '2025-06-14T10:00:00',
    //     end_time: '2025-06-14T12:30:00',
    //     status: 'reserved',
    //   },
    //   {
    //     location: 'Airport Parking Zone',
    //     slot: 'Slot B4',
    //     start_time: '2025-06-15T08:00:00',
    //     end_time: '2025-06-15T11:00:00',
    //     status: 'occupied',
    //   },
    //   {
    //     location: 'Mall Parking Area',
    //     slot: 'Slot C2',
    //     start_time: '2025-06-16T14:00:00',
    //     end_time: '2025-06-16T16:00:00',
    //     status: 'reserved',
    //   },
    //   {
    //     location: 'City Center Parking',
    //     slot: 'Slot D3',
    //     start_time: '2025-06-17T09:00:00',
    //     end_time: '2025-06-17T11:30:00',
    //     status: 'occupied',
    //   },
    // ]
  } catch (err) {
    console.error('Failed to load upcoming bookings', err)
    if (err.response) {
      const status = err.response.status
      const msg = err.response.data.message || 'Unexpected error'

      if (status === 401) {
        toast.error('Unauthorized: ' + msg, { timeout: 2000 })
      } else if (status === 402) {
        // toast.warning('Session expired: ' + msg, { timeout: 2000 })
      } else if (status === 500) {
        toast.error('Server error: Please try again later', { timeout: 2000 })
      } else {
        toast.error(`Error (${status}): ${msg}`, { timeout: 2000 })
      }
    } else {
      
      toast.error('Network error: Unable to connect to server', { timeout: 2000 })
    }

    
    upcomingBookings.value = []
  }
}

function goToBooking() {
  router.push('/booklot')
}

function toggleOccupied(index) {
  if (!upcomingBookings.value[index]) {
    console.warn('Invalid index:', index)
    return
  }

  selectedLocation.value = upcomingBookings.value[index].location;
  const currentStatus = upcomingBookings.value[index].status
  const newStatus = currentStatus === 'occupied' ? 'available' : 'occupied'
  upcomingBookings.value[index].status = newStatus

  axios
    .put(
      `${url}/reserve`,
      { 
        new_status: newStatus,
        location_name: selectedLocation.value,
      },
      {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    .then((response) => {
      if (response.data.success) {
        upcomingBookings.value[index].status = newStatus
        // console.log('response: ', response)
      } else {
        console.error('Failed to update status:', response.data.message)
      }
    })
    .catch((error) => {
      if (error.response) {
        const status = error.response.status
        const msg = error.response.data.message || 'Unexpected error'

        if (status === 401) {
          toast.error('Reservation not found. Please refresh.', { timeout: 2000 })
        } else if (status === 402) {
          toast.warning('Session expired. Please log in again.', { timeout: 2000 })
        } else if (status === 500) {
          toast.error('Server error. Try again later.', { timeout: 2000 })
        } else {
          toast.error(`Error (${status}): ${msg}`, { timeout: 2000 })
        }
      } else {
        toast.error('Network error. Check your connection.', { timeout: 2000 })
      }

      upcomingBookings.value[index].status = currentStatus
    })
}

async function downloadUserData() {
  try {
    const response = await axios.get(`${url}/userdatadownload`, {
      withCredentials: true,
      responseType: 'blob',
    })

    const blob = new Blob([response.data], { type: 'application/json' })
    const downloadUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = 'kwikpark_data.pdf'
    link.click()
    URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    console.error('Download failed:', error)
  }
}

getUpcomingBookings()
</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard-wrapper">
      <h1 class="dashboard-title">Your Dashboard, {{ first_name }}</h1>
      <div class="dashboard-buttons">
        <button class="dashboard-btn" @click="goToBooking">Book a Parking Lot</button>
        <button class="dashboard-btn" @click="downloadUserData">Download Your Data</button>
      </div>

      <div v-if="upcomingBookings.length" class="upcoming-bookings">
        <h2 class="upcoming-title">Upcoming Bookings</h2>
        <ul class="upcoming-list">
          <li
            v-for="(booking, index) in upcomingBookings"
            :key="booking.start_time"
            class="upcoming-item"
          >
            <div class="booking-header">
              <div>
                <strong class="booking-location">{{ booking.location }}</strong>
                <span class="booking-slot">{{ booking.slot }}</span>
              </div>
              <button
                class="status-toggle"
                @click="toggleOccupied(index)"
                :title="booking.status === 'occupied' ? 'occupied' : 'realsed'"
              >
                <span v-if="booking.status === 'occupied'">🔒</span>
                <span v-else>✅</span>
              </button>
            </div>
            <div class="booking-time">{{ booking.start_time }} → {{ booking.end_time }}</div>
          </li>
        </ul>
      </div>

      <div class="dashboard-cards">
        <div v-for="card in cards" :key="card.title" class="dashboard-card">
          <h2 class="card-title">{{ card.title }}</h2>
          <p class="card-value">{{ card.value }}</p>
        </div>
      </div>

      <div class="chart-container">
        <h2 class="chart-title">Monthly Booking Trends</h2>
        <canvas ref="chartCanvas" height="120"></canvas>
      </div>
    </div>
  </div>
</template>


<style scoped>
.upcoming-bookings {
  background-color: whitesmoke;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.upcoming-title {
  font-size: 24px;
  color: #6bb2a1;
  margin-bottom: 16px;
}

.upcoming-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.upcoming-item {
  background-color: white;
  border-left: 6px solid #7adec6;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 10px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.upcoming-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}
.booking-header {
  font-size: 18px;
  font-weight: 600;
  color: #6bb2a1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* .booking-slot {
  font-size: 16px;
  color: #888;
  margin-left: 1rem;
} */

.booking-slot {
  display: inline-block;
  font-size: 14px;
  font-weight: 500;
  color: #6bb2a1;
  background-color: whitesmoke; /* Bootstrap primary blue */
  padding: 4px 10px;
  border-radius: 12px;
  margin-left: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
  transition: background-color 0.3s ease;
}

.booking-slot:hover {
  background-color: rgb(231, 231, 231);
  cursor: default;
}

.booking-time {
  margin-top: 8px;
  font-size: 15px;
  color: #444;
}
.status-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  margin-left: 12px;
  color: #6bb2a1;
  transition: transform 0.2s ease;
}

.status-toggle:hover {
  transform: scale(1.2);
}

.dashboard-container {
  background-color: white;
  min-height: 100vh;
  padding: 24px;
  font-family: 'Segoe UI', sans-serif;
}

.dashboard-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-title {
  font-size: 32px;
  font-weight: bold;
  color: #6bb2a1;
  margin-bottom: 24px;
  text-align: left;
}
.dashboard-buttons {
  display: flex;
  gap: 20rem;
  justify-content: center;
  margin-bottom: 24px;
}

.dashboard-btn {
  padding: 20px 46px;
  background-color: #7adec6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 18px;
  transition: background 0.3s;
}

.dashboard-btn:hover {
  background-color: #6bb2a1;
}

.dashboard-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 40px;
}

.dashboard-card {
  flex: 1 1 250px;
  background-color: whitesmoke;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: background 0.3s;
}

.dashboard-card:hover {
  background-color: rgb(231, 231, 231);
  box-shadow: 10px 10px 20px rgba(218, 20, 20, 0.1);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #6bb2a1;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #7adec6;
}

.chart-container {
  background-color: whitesmoke;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-title {
  font-size: 24px;
  color: #6bb2a1;
  margin-bottom: 16px;
}
</style>
