<script setup>
import { ref, computed, onMounted } from 'vue'
import Login from './Login.vue'
import { url } from './url'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'

const toast = useToast()
const lots = ref([])
const router = useRouter()
const vehicleRegistrationNumber = ref('')

async function getLotDetails() {
  const token = getToken()
  // console.log(token)
  if (!token || token.length === 0) {
    toast.error('Login first to proceed with booking')
    setTimeout(() => {
      router.push('/login')
    }, 5500)
    return
  } else {
    try {
      const response = await axios.get(`${url}/getlot`)
      // console.log('Get lot Response ', response)
      if (response.status === 200 && response.data.data) {
        lots.value = Object.entries(response.data.data).map(([name, lot]) => ({
          name,
          ...lot,



          occupied_slots: [...(lot.occupied_slots || [])],



        }))
      }
    } catch (error) {
      console.log('Error in Lot.vue', error)
    }
  }
}

onMounted(() => {
  getLotDetails()
})

const selectedCountry = ref('')
const selectedState = ref('')
const selectedCity = ref('')
const selectedLotName = ref('')
const startTime = ref('')
const endTime = ref('')
const isValid = ref(true)

const filteredStates = computed(() => {
  return [
    ...new Set(
      lots.value.filter((lot) => lot.country === selectedCountry.value).map((lot) => lot.state)
    ),
  ]
})

const filteredCities = computed(() => {
  return [
    ...new Set(
      lots.value.filter((lot) => lot.state === selectedState.value).map((lot) => lot.city)
    ),
  ]
})

const filteredLots = computed(() => {
  return lots.value.filter((lot) => lot.city === selectedCity.value)
})

const selectedLot = computed(() => {
  if (!Array.isArray(lots.value) || lots.value.length === 0) return null
  return lots.value.find((lot) => lot.name === selectedLotName.value)
})

const allSlots = computed(() => {
  if (!selectedLot.value) return []
  return Array.from({ length: selectedLot.value.total_slots }, (_, i) => `S${i + 1}`)
})

const calculatePayment = computed(() => {
  if (!startTime.value || !endTime.value || !selectedLot.value) return 0

  const start = new Date(startTime.value)
  const end = new Date(endTime.value)

  if (isNaN(start) || isNaN(end)) return 0

  const durationHours = Math.max((end - start) / (1000 * 60 * 60), 0)
  return Math.ceil(durationHours) * selectedLot.value.hourly_rate
})

const getToken = () => {
  const cookies = document.cookie.split(';')
  const tokenCookie = cookies.find((cookie) => cookie.trim().startsWith('token='))

  if (tokenCookie) {
    const tokenValue = tokenCookie.split('=')[1]
    // console.log('Token found:', tokenValue)
    return tokenValue
  }
  return ''
}

function generateDummyPaymentPayload(reservationId, amount) {
  const paymentMethods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash']
  const paymentMethod = paymentMethods[Math.floor(Math.random() * paymentMethods.length)]
  const transactionId = `TXN${Math.floor(1000000000 + Math.random() * 9000000000)}`
  return {
    reservation_id: reservationId,
    amount: amount,
    payment_method: paymentMethod,
    payment_status: 'completed',
    transaction_id: transactionId,
  }
}

function isOccupied(slot) {
  if (!selectedLot.value || !Array.isArray(selectedLot.value.occupied_slots)) {
    return false;
  }
  return selectedLot.value.occupied_slots.includes(slot);
}

async function confirmBooking() {
  try {
    if (!selectedLotName.value || !startTime.value || !endTime.value) {
      toast.warning('Please select a parking lot and time range', { timeout: 3000 })
      return
    }

    const payload = {
      name: selectedLotName.value,
      start_time: startTime.value,
      end_time: endTime.value,
      vehicle_registration_number: vehicleRegistrationNumber.value,
    }

    // console.log('Sending booking payload:', payload)

    const res = await axios.post(`${url}/reserve`, payload, {
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (res.data.success) {
      const payment_payload = generateDummyPaymentPayload(
        res.data.reservation_id,
        calculatePayment.value
      )

      const response = await axios.post(`${url}/payment`, payment_payload, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
        },
      })

      console.log('Payment Response: ', response)

      toast.success(res.data.message || 'Booking confirmed successfully!', {
        timeout: 3000,
      })
      console.log('Booking successful:', res.data)
      setTimeout(() => {
        router.push('/userdashboard')
      }, 5500)
    } else {
      toast.error(res.data.message || 'Failed to confirm booking', { timeout: 3000 })
    }
  } catch (err) {
    console.error('Error confirming booking:', err)

    if (err.response) {
      const status = err.response.status
      const msg = err.response.data.message || 'Unexpected error'

      if (status === 402) {
        toast.warning(msg, { timeout: 3000 })
      } else if (status === 500) {
        toast.error('Internal Server Error: Please try again later.', { timeout: 3000 })
      } else {
        toast.error(`Error (${status}): ${msg}`, { timeout: 3000 })
      }
    } else {
      toast.error('Network error: Unable to connect to server.', { timeout: 3000 })
    }
  }
}
</script>

<template>
  <div v-if="isValid" class="booking-container">
    <div class="banner">
      <div class="text">
        <p>Reserve Your Spot in Just a Few Clicks</p>
      </div>
    </div>

    <div class="top-section">
      <div class="dropdowns">
        <select v-model="selectedCountry">
          <option disabled value="">Select Country</option>
          <option v-for="lot in [...new Set(lots.map((l) => l.country))]" :key="lot">
            {{ lot }}
          </option>
        </select>

        <select v-if="selectedCountry" v-model="selectedState">
          <option disabled value="">Select State</option>
          <option v-for="state in filteredStates" :key="state">{{ state }}</option>
        </select>

        <select v-if="selectedState" v-model="selectedCity">
          <option disabled value="">Select City</option>
          <option v-for="city in filteredCities" :key="city">{{ city }}</option>
        </select>

        <select v-if="selectedCity" v-model="selectedLotName">
          <option disabled value="">Select Parking Lot</option>
          <option v-for="lot in filteredLots" :key="lot.name">{{ lot.name }}</option>
        </select>
      </div>

      <div class="payment-box" v-if="selectedLot">₹{{ calculatePayment }} /-</div>
    </div>

    <div v-if="selectedLot" class="lot-details">
      <h1>{{ selectedLot.name }}</h1>
      <p>
        📍 {{ selectedLot.city }}, {{ selectedLot.state }}, {{ selectedLot.country }} -
        {{ selectedLot.postal_code }}
      </p>
      <p>💰 Hourly Rate: ₹{{ selectedLot.hourly_rate }}</p>

      <div class="time-selection">
        <label>Start Time:</label>
        <input type="datetime-local" v-model="startTime" />

        <label>End Time:</label>
        <input type="datetime-local" v-model="endTime" />
      </div>

      <div class="vehicle-input">
        <label>Vehicle Registration No.:</label>
        <input
          type="text"
          v-model="vehicleRegistrationNumber"
          placeholder="e.g., MH12AB1234"
          class="vehicle-field"
        />
      </div>

      <div class="grid-container">
        <div
          v-for="slot in allSlots"
          :key="slot"
          :class="['slot', { occupied: isOccupied(slot) }]"
        >
          <span v-if="isOccupied(slot)">🚗</span>
          <span v-else>{{ slot }}</span>
        </div>
      </div>

      <!-- <div v-for="slot in allSlots" :key="slot">
        {{ slot }} - Occupied: {{ isOccupied(slot) }}
      </div> -->

      <button class="confirm-btn" @click="confirmBooking">Confirm Booking</button>
    </div>
  </div>
  <div v-else>
    <Login />
  </div>
</template>


<style scoped>
.booking-container {
  padding: 2rem;
  width: 90vw;
  min-height: 100vh;
  box-sizing: border-box;
}

.banner {
  width: 100%;
  padding: 2rem 5%;
  background: linear-gradient(90deg, #dbf9f1, #7adec6, #6bb2a1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.banner .text p {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.banner .export button {
  background-color: white;
  color: #6bb2a1;
  padding: 0.8rem 1.5rem;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}

.banner .export button:hover {
  background-color: #6bb2a1;
  color: white;
  transform: translateY(-2px);
}

.top-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.dropdowns {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.dropdowns select {
  margin: 10px 0;
  padding: 0.7rem 1.5rem;
  border-radius: 5px;
  border: 1px solid gray;
  font-size: 16px;
}

.payment-box {
  font-size: 32px;
  font-weight: 900;
  background-color: #7adec6;
  color: white;
  padding: 12px 25px;
  border-radius: 8px;
  margin-top: 10px;
}

.lot-details {
  margin-top: 3rem;
}

.time-selection {
  margin-bottom: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.time-selection input {
  padding: 0.6rem 1rem;
  border: 1px solid gray;
  border-radius: 5px;
  font-size: 16px;
}

.vehicle-input {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.vehicle-input label {
  font-weight: 600;
  font-size: 16px;
  color: #1a1a1a;
}

.vehicle-field {
  padding: 0.7rem 1rem;
  border: 2px solid #7adec6;
  border-radius: 5px;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease;
}

.vehicle-field:focus {
  border-color: #6bb2a1;
  box-shadow: 0 0 5px rgba(107, 178, 161, 0.3);
}

.vehicle-field::placeholder {
  color: #888;
  font-size: 14px;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 2rem;
  width: 100%;
}

.slot {
  border: 3px dotted #7adec6;
  border-radius: 8px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 28px;
}

.occupied {
  background-color: #f5f5f5;
  color: red;
}

.confirm-btn {
  padding: 1rem 2.5rem;
  background-color: #6bb2a1;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 20px;
  margin-top: 2rem;
}
</style>