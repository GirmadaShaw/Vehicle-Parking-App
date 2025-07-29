<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { url } from './url'
import LotModal from './LotModal.vue'
import DeleteConfirmation from './DeleteConfirmation.vue'

const lots = ref([])
const currentIndex = ref(0)
const showModal = ref(false)
const modalMode = ref('create')
const selectedLot = ref(null)
const showDeletePopup = ref(false)
let autoSlideInterval

const fetchLotStats = async () => {
  try {
    const res = await axios.get(`${url}/lotstats`)
    if (res.data.success) {
      lots.value = res.data.lot_stats
      startAutoSlide()
    }
  } catch (err) {
    console.error('Error fetching lot stats:', err)
  }
}

const startAutoSlide = () => {
  autoSlideInterval = setInterval(() => {
    nextCard()
  }, 4000)
}

const nextCard = () => {
  currentIndex.value = (currentIndex.value + 1) % lots.value.length
}
const prevCard = () => {
  currentIndex.value = (currentIndex.value - 1 + lots.value.length) % lots.value.length
}

const openAddModal = () => {
  modalMode.value = 'create'
  selectedLot.value = null
  showModal.value = true
}

const openEditModal = (lot) => {
  modalMode.value = 'edit'
  selectedLot.value = { ...lot }
  showModal.value = true
}

const openDeletePopup = (lot) => {
  selectedLot.value = { ...lot }
  showDeletePopup.value = true
}

const handleLotDeleted = (lotName) => {
  lots.value = lots.value.filter((l) => l.lot_name !== lotName)
  showDeletePopup.value = false
}

const handleLotSaved = (newLot) => {
  fetchLotStats()
  showModal.value = false
}

onMounted(fetchLotStats)
</script>

<template>
  <div class="slider-container">
    <div class="crud-buttons">
      <button class="btn add" @click="openAddModal">+ Add Lot</button>
      <button class="btn edit" @click="openEditModal(lots[currentIndex])">✏️ Edit</button>
      <button class="btn delete" @click="openDeletePopup(lots[currentIndex])">🗑️ Delete</button>
    </div>

    <div class="slider-wrapper" :style="{ transform: `translateX(-${currentIndex * 100}%)` }">
      <div class="lot-card" v-for="lot in lots" :key="lot.lot_id">
        <div class="lot-header">
          <h3>{{ lot.lot_name }}</h3>
          <p class="city">{{ lot.city }}</p>
        </div>
        <div class="metrics-grid">
          <div class="metric">
            <span class="label">Available Slots</span
            ><span class="value available">{{ lot.available_slots }}</span>
          </div>
          <div class="metric">
            <span class="label">Occupied Slots</span
            ><span class="value occupied">{{ lot.occupied_slots }}</span>
          </div>
          <div class="metric">
            <span class="label">Total Slots</span><span class="value">{{ lot.total_slots }}</span>
          </div>
          <div class="metric">
            <span class="label">Reservations</span
            ><span class="value">{{ lot.total_reservations }}</span>
          </div>
          <div class="metric revenue-box">
            <span class="label">Revenue</span
            ><span class="value revenue">₹{{ lot.total_revenue.toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>

    <button class="nav-btn left" @click="prevCard">‹</button>
    <button class="nav-btn right" @click="nextCard">›</button>

    <LotModal
      v-if="showModal"
      :mode="modalMode"
      :lotData="selectedLot"
      @saved="handleLotSaved"
      @close="showModal = false"
    />

    <DeleteConfirmation
      v-if="showDeletePopup"
      :lotName="selectedLot?.lot_name"
      @deleted="handleLotDeleted"
      @close="showDeletePopup = false"
    />
  </div>
</template>


<style scoped>
.slider-container {
  background: whitesmoke;
  border-radius: 16px;
  padding: 1.5rem;
  width: 95%;
  max-width: 1200px;
  margin: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  transition: box-shadow 0.3s ease, filter 0.3s ease;
}
.slider-container:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.slider-wrapper {
  display: flex;
  transition: transform 2s ease-out;
  width: 100%;
  gap: 0.5rem;
  margin-top: 1rem;
}

.crud-buttons {
  position: absolute;
  top: 10px;
  right: 15px;
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.btn.add {
  background: #7adec6;
  color: white;
}
.btn.add:hover {
  background: #6bb2a1;
}
.btn.edit {
  background: #c9f7ec;
  color: #4b8c7a;
}
.btn.edit:hover {
  background: #85eace;
}
.btn.delete {
  background: #dbf9f1;
  color: #4b8c7a;
}
.btn.delete:hover {
  background: #7adec6;
  color: white;
}

.lot-card {
  flex: 0 0 calc(100% - 1rem); /* each card fits correctly with gap */
  background: #e7e5e5;
  border-radius: 14px;
  padding: 0.1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: whitesmoke;
  margin: 0.5em;
}

.lot-header h3 {
  font-size: 1.6rem;
  color: #4b8c7a;
  margin-bottom: 0.2rem;
  font-weight: bold;
  padding: 1rem;
}
.city {
  font-size: 1rem;
  font-style: italic;
  color: #6bb2a1;
  margin-bottom: 1.5rem;
  padding: 1rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3rem 1rem;
  padding: 1rem;
}
.metric {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.label {
  font-size: 0.9rem;
  color: #4b8c7a;
  opacity: 0.9;
}
.value {
  font-weight: bolder;
  font-size: 1.2rem;
  color: #4b8c7a;
}
.available {
  color: #7adec6;
}
.occupied {
  color: #6bb2a1;
}
.revenue {
  font-size: 1.8rem;
  color: #4b8c7a;
}
.revenue-box {
  grid-column: span 2;
  background: #dbf9f1;
  border-radius: 8px;
  padding: 0.1rem 1rem;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(148, 144, 144, 0.3);
  color: white;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  border-radius: 50%;
  padding: 0.3rem 0.7rem;
  transition: background 0.3s;
}
.nav-btn:hover {
  background: rgba(0, 0, 0, 0.6);
}
.left {
  left: 10px;
}
.right {
  right: 10px;
}
</style> 
