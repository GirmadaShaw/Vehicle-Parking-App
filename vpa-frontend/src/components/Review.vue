<script setup>
    import { ref, onMounted } from 'vue'
    import Card from "./Card.vue"
    import {url} from './url'
    import axios from 'axios'

    const reviews = ref([])

    async function getReviews() {
        await axios
        .get(`${url}/get-reviews`)
        .then((response) => {
            if( response.status == 200 )
                reviews.value = response.data.data
            
        })
        .catch((err) => {
            console.log("Error in Review.vue", err)
        })
    }

    onMounted(getReviews)

</script>

<template>

  <div class="reviews-container">
    <h1 class="title">Our Reviews</h1>
    <div class="slider">
      <div class="slides" :style="{ width: `${reviews.length * 33.33}%` }">
        <div
          v-for="(review, index) in reviews"
          :key="index"
          class="slide"
        >
          <Card :review="review" />
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>

.reviews-container {
  max-width: 98vw;
  height: 80vh;
  margin: 5px auto;
  text-align: center;
  background-color: #DBF9F1;
}

.title {
  font-size: 48px;
  font-weight: 900;
  margin-top: 3rem;
  padding: 30px;
  
}

.slider {
  overflow: hidden;
  width: 100%;
  border-radius: 10px;
  box-shadow: 0 1px 10px whitesmoke;
}

.slides {
  display: flex;
  animation: slide 45s infinite linear;
}

.slide {
  width: 33.33%;
  padding: 20px;
  box-sizing: border-box;
}


@keyframes slide {
  0% { transform: translateX(0%); }
  25% { transform: translateX(-33.33%); }
  50% { transform: translateX(-66.66%); }
  75% { transform: translateX(-33.33%); }
  100% { transform: translateX(0%); }
}
</style>