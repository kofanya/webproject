<template>
  <div class="container-2">
    <h1 class="title">Моё избранное</h1>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="ads.length === 0" class="empty">
      У вас пока нет избранных объявлений.
    </div>

    <div v-else class="blog-cards">
      <div 
        v-for="ad in ads" 
        :key="ad.id" 
        class="blog-card" 
        @click="goToAd(ad.id)"
      >
        <div class="card-image-wrapper">
          <img :src="getPhotoUrl(ad.main_photo)" class="card-image">
          <button class="favorite-btn" @click.stop="removeFromFavorites(ad)">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#ff4757" stroke="#ff4757" stroke-width="2" class="heart-icon liked">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
          </button>
        </div>

        <div class="card-content">
          <h3 class="card-title">{{ ad.title }}</h3>
          <div class="price-wrapper">
            <span class="price">{{ formatPrice(ad.price) }} ₽</span>
          </div>
          <div class="meta-info">
            <span class="district">{{ ad.district }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const ads = ref([])
const loading = ref(true)
const BACKEND_URL = 'http://127.0.0.1:5000'

const fetchFavorites = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const response = await fetch(`/api/favorites`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      ads.value = await response.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const removeFromFavorites = async (ad) => {
  try {
    const response = await fetch(`/api/ads/${ad.id}/favorite`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      ads.value = ads.value.filter(item => item.id !== ad.id)
    }
  } catch (e) {
    console.error(e)
  }
}

const getPhotoUrl = (filename) => filename ? `${BACKEND_URL}/static/uploads/${filename}` : '/placeholder-image.png'
const formatPrice = (p) => p ? p.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") : '0'
const goToAd = (id) => router.push(`/ads/${id}`)

onMounted(() => {
  fetchFavorites()
})
</script>