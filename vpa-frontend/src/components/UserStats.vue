<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { url } from '../components/url'

const activeUsers = ref(0)
const newUsers = ref(0)
const topUsers = ref([])
const currentIndex = ref(0)

const fetchUserStats = async () => {
  try {
    const res = await axios.get(`${url}/userstats`)
    if (res.data.success) {
      activeUsers.value = res.data.data.active_users
      newUsers.value = res.data.data.new_users_this_month
      topUsers.value = res.data.data.top_users
    }
  } catch (err) {
    console.error('Error fetching user stats:', err)
  }
}


const sliderStyle = computed(() => {
  const cardWidth = 100 / 3 
  return {
    transform: `translateX(-${currentIndex.value * cardWidth}%)`
  }
})

const nextSlide = () => {
  if (currentIndex.value < topUsers.value.length - 3) {
    currentIndex.value += 1
  } else {
    currentIndex.value = 0
  }
}

const prevSlide = () => {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
  } else {
    currentIndex.value = Math.max(topUsers.value.length - 3, 0)
  }
}

onMounted(fetchUserStats)
</script>

<template>
  <div class="userstats-container">
    <div class="top-metrics">
      <div class="metric-box">Active Users: <span>{{ activeUsers }}</span></div>
      <div class="metric-box">Users (Last 30 days): <span>{{ newUsers }}</span></div>
    </div>

    <div class="slider-section">
      <button class="nav-btn left" @click="prevSlide">‹</button>
      <div class="slider-wrapper">
        <div class="user-slider" :style="sliderStyle">
          <div class="user-card" v-for="(user, index) in topUsers" :key="index">
            <h3>{{ user.username }}</h3>
            <p>Reservations: {{ user.reservations }}</p>
          </div>
        </div>
      </div>
      <button class="nav-btn right" @click="nextSlide">›</button>
    </div>
  </div>
</template>

<style scoped>
.userstats-container {
  height: 40vh;
  background: whitesmoke;
  border-radius: 16px;
  padding: 1.5rem;
  width: 95%;
  max-width: 1200px;
  margin: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  position: relative;
  transition: box-shadow 0.3s ease, filter 0.3s ease;
}
.userstats-container:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

.top-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.metric-box {
  background: #DBF9F1;
  color: #4B8C7A;
  font-weight: bold;
  font-size: 1.1rem;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.metric-box span {
  color: #4B8C7A;
  font-size: 1.3rem;
}


.slider-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}


.slider-wrapper {
  width: 100%;
  overflow: hidden;
}

.user-slider {
  display: flex;
  transition: transform 0.5s ease;
  width: max-content;
}

.user-card {
  flex: 0 0 calc(100% / 3);
  background: #e7e5e5;
  border-radius: 12px;
  padding: 1.2rem;
  margin-right: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  color: #4B8C7A;
  text-align: center;
  height: 8rem;
}
.user-card h3 {
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
  font-weight: bold;
  color: #4B8C7A;
}
.user-card p {
  font-size: 1rem;
  color: #6BB2A1;
}


.nav-btn {
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
</style>
