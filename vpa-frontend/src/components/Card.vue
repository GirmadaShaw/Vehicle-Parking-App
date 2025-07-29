<script setup>
defineProps({
    review : Object
})
</script>

<template>
  <div class="card">
    <h2 class="username">{{ review.username }}</h2>
    <p class="rating">⭐ {{ review.rating }} / 5</p>
    <p class="review-text">"{{ review.review_text }}"</p>
  </div>
</template>

<style scoped>
.card { 

  background-color: #C9F7EC;
  /* #DBF9F1; */
  border: 1px solid #C9F7EC;
  /* #DBF9F1; */
  /* #ddd; */
  border-radius: 10px;
  padding: 20px;
  height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.username {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.rating {
  font-size: 20px;
  font-weight: 500;
  color: #fbbf24; 
}

.review-text {
  font-size: 16px;
  font-style: italic;
  color: #555;
}
</style>