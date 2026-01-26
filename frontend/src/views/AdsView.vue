<template>
  <div class="container-2">
    <h1 class="title">Актуальные объявления</h1>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="ads.length === 0" class="empty">Нет активных объявлений</div>

    <div v-else class="blog-cards">
      
      <div 
        v-for="ad in ads" 
        :key="ad.id" 
        class="blog-card" 
        @click="goToAd(ad.id)"
      >
        <div class="card-image-wrapper">
          <img 
            :src="getPhotoUrl(ad.main_photo)" 
            alt="Фото товара" 
            class="card-image"
          >
          <button class="favorite-btn" @click.stop="toggleFavorite(ad)">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="heart-icon">
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
            <span class="district">Владивосток, {{ ad.district }} район</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const ads = ref([])
const loading = ref(true)


const BACKEND_URL = 'http://127.0.0.1:5000'

const fetchAds = async () => {
  try {
    const response = await fetch('/api/ads') 
    if (!response.ok) {
      throw new Error('Ошибка загрузки')
    }
    ads.value = await response.json()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const getPhotoUrl = (filename) => {
  if (!filename) return '/placeholder-image.png'
  return `${BACKEND_URL}/static/uploads/${filename}`
}

const formatPrice = (price) => {
  if (price === null || price === undefined) return '0'
  return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ")
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

const goToAd = (id) => {
  router.push(`/ads/${id}`)
}

const toggleFavorite = (ad) => {
  console.log('Добавить в избранное:', ad.id)
  // Здесь будет логика отправки запроса на сервер
}

onMounted(() => {
  fetchAds()
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
</style>