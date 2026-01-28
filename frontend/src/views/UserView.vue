<template>
  <div class="container-2">
    <div v-if="loading" class="loading">Загрузка профиля...</div>
    
    <div v-else class="profile-layout">
      <div class="profile-header">
        <div class="profile-info">
          <h1>{{ userInfo.user_name }}</h1>
          <div class="rating-block">
            <span class="rating-num">{{ userInfo.average_rating }}</span>
            <Star :value="Math.round(userInfo.average_rating)" />
            <span class="review-count">({{ userInfo.reviews.length }})</span>
          </div>
        </div>
      </div>

      <hr class="divider">

      <h2 class="section-title">Отзывы</h2>
      
      <div v-if="userInfo.reviews.length === 0" class="empty">
        Отзывов пока нет
      </div>

      <div v-else class="reviews-list">
        <div v-for="review in userInfo.reviews" :key="review.id" class="review-card">
          <div class="review-top">
            <span class="author-name">{{ review.author_name }}</span>
            <span class="review-date">{{ formatDate(review.date) }}</span>
          </div>
          <Star :value="review.rating" />
          <p class="review-text">{{ review.text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Star from '@/components/Star.vue' 

const route = useRoute()
const loading = ref(true)
const userInfo = ref(null)

const fetchProfile = async () => {
  try {
    const userId = route.params.id 
    const res = await fetch(`/api/users/${userId}/reviews`)
    if (res.ok) {
      userInfo.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('ru-RU')
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.container-2 {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header { 
  margin-bottom: 20px; 
}

.rating-block { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  margin-top: 5px; 
}

.divider { 
  border: 0; 
  border-top: 1px solid #eee; 
  margin: 20px 0; 
}

.review-card { 
  padding: 15px 0; 
  border-bottom: 1px solid #eee; 
}

.review-top { 
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 5px; 
}

.review-text { 
  margin-top: 8px; 
}

.loading, .empty { 
  text-align: center; 
  padding: 20px; 
}
</style>