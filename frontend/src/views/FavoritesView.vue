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

<style scoped>
    .container-2 {
    max-width: 1250px; 
    margin: 0 auto;
    padding: 0 20px;
    }

    .title {
    text-align: center;
    margin: 40px 0 30px;
    color: #333;
    font-size: 2rem;
    }

    .loading, .empty {
    text-align: center;
    font-size: 1.2rem;
    color: #666;
    padding: 40px;
    }

    .blog-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 60px;
    }

    .blog-card {
    background-color: #ffffff;
    border-radius: 16px; 
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    height: 100%;
    }

    .blog-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
    }

    .card-image-wrapper {
    position: relative;
    width: 100%;
    padding-top: 75%;
    background-color: #f3f4f6;
    }

    .card-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    }

    .favorite-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.8);
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    z-index: 2; 
    }

    .favorite-btn:hover {
    background: white;
    transform: scale(1.1);
    }

    .heart-icon {
    width: 20px;
    height: 20px;
    color: #666; 
    transition: fill 0.2s, color 0.2s;
    }
    .heart-icon.liked {
      fill: #ff4757;
      color: #ff4757; 
      transform: scale(1.1);
    }

    .favorite-btn:active .heart-icon {
    fill: #ff4757;
    color: #ff4757;
    }

    .card-content {
    padding: 16px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    }

    .card-title {
    font-size: 1.1rem;
    font-weight: 500;
    color: #222;
    margin: 0 0 8px 0;
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    }

    .price-wrapper {
    margin-bottom: 8px;
    }

    .price {
    font-size: 1.25rem;
    font-weight: 700;
    color: #000;
    }

    .meta-info {
    margin-top: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: #888;
    }

    .district {
    padding: 4px 8px;
    border-radius: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 90%;
    }
      .filters {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-bottom: 30px;
    flex-wrap: wrap;
  }

  .form-control{
    max-width: 500px;
  }
</style>