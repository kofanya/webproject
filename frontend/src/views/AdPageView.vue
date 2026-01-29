<template>
  <div v-if="ad" class="container-2">
    <div class="ad-top-section">
      <div class="gallery-column">
        <div class="gallery-wrapper">
          <div v-if="ad.photos && ad.photos.length > 0" class="image-frame">
            <img :src="getCurrentPhotoUrl()" alt="Фото" class="ad-image"/>
            <button v-if="ad.photos.length > 1" class="nav-btn prev" @click="prevPhoto">&#10094;</button>
            <button v-if="ad.photos.length > 1" class="nav-btn next" @click="nextPhoto">&#10095;</button>
          </div>
          <div v-else class="image-frame placeholder">
            <span>Нет фото</span>
          </div>
        </div>
        
        <div v-if="ad.photos && ad.photos.length > 1" class="little-row">
          <div 
            v-for="(photo, index) in ad.photos" :key="index" class="little-item"
            :class="{ active: index === currentPhotoIndex }"
            @click="currentPhotoIndex = index">
            <img :src="`${BACKEND_URL}/static/uploads/${photo}`" alt="thumb">
          </div>
        </div>
      </div>

      <div class="info-column">
        <h1 class="ad-title">{{ ad.title }}</h1>
        <div class="ad-price">{{ formatPrice(ad.price) }} ₽</div>

        <div class="meta-clean">
          <div class="meta-row">
            <span class="label">Категория:</span>
            <span class="value">{{ getCategoryName(ad.category, ad.ad_type) }}</span>
          </div>
          <div class="meta-row">
            <span class="label">Район:</span>
            <span class="value">Владивосток, {{ ad.district }} район</span>
          </div>
          <div class="meta-row">
            <span class="label">Адрес:</span>
            <span class="value">{{ ad.address || 'Не указан' }}</span>
          </div>
          <div class="meta-row">
            <span class="label">Дата:</span>
            <span class="value">{{ formatDate(ad.created_date) }}</span>
          </div>
          <div class="meta-row">
            <span class="label">Просмотров:</span>
            <span class="value">{{ ad.views }}</span>
          </div>
        </div>

        <div class="actions-panel">
          <div v-if="isOwner" class="owner-controls">
            <button @click="editAd" type="button" class="button">Редактировать</button>
            <button @click="deleteAd" type="button" class="button">Удалить</button>
          </div>
          <div v-else>
            <button @click="contactAuthor" class="button">Написать автору</button>
          </div>
        </div>
      </div>
    </div>

    <div class="description-section">
      <div class="section-title">Описание</div>
      <div class="vacancy-text">{{ ad.description }}</div>
    </div>

    <div class="seller-info-box"> 
      <RouterLink :to="`/users/${ad.user_id}`" class="seller-link">
        Перейти в профиль пользователя
      </RouterLink>
    </div>

    <div v-if="authStore.isAuthenticated && !isOwner" class="review-form-section">
      <h3>Оставить отзыв</h3>
      <div class="star-input">
        <span  v-for="i in 5" :key="i" @click="newReview.rating = i" class="star-btn" :class="{ active: i <= newReview.rating }">★</span>
      </div>
      <textarea v-model="newReview.text" class="form-control"></textarea>
      <button @click="sendReview" class="button">Отправить отзыв</button>
    </div>
    <div class="back">
      <RouterLink to="/ads">← Вернуться к списку объявлений</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ITEM_CATEGORIES, SERVICE_CATEGORIES } from '@/utils/categories'

const BACKEND_URL = 'http://127.0.0.1:5000'
const route = useRoute() 
const router = useRouter()
const authStore = useAuthStore()
const ad = ref(null)         
const currentPhotoIndex = ref(0) 
const newReview = ref({ rating: 0, text: '' })

const fetchAd = async () => {
  try {
    const response = await fetch(`/api/ads/${route.params.id}`)
    
    if (!response.ok) {
      throw new Error('Ошибка при загрузке')
    }
    ad.value = await response.json()
    
  } catch (error) {
    console.error(error)
    alert('Не удалось загрузить объявление')
    router.push('/ads') 
  } 
}

const getCurrentPhotoUrl = () => {
  if (!ad.value.photos || ad.value.photos.length === 0) {
    return '/placeholder-image.png' 
  }
  const filename = ad.value.photos[currentPhotoIndex.value]
  return `${BACKEND_URL}/static/uploads/${filename}`
}

const nextPhoto = () => {
  const totalPhotos = ad.value.photos.length
  if (currentPhotoIndex.value < totalPhotos - 1) {
    currentPhotoIndex.value++
  } else {
    currentPhotoIndex.value = 0 
  }
}

const prevPhoto = () => {
  const totalPhotos = ad.value.photos.length
  if (currentPhotoIndex.value > 0) {
    currentPhotoIndex.value--
  } else {
    currentPhotoIndex.value = totalPhotos - 1
  }
}
const isOwner = computed(() => {
  if (!ad.value || !authStore.user) return false
 
  return ad.value.user_id === authStore.user.id
})

const deleteAd = async () => {
  const confirmed = confirm('Вы уверены, что хотите удалить объявление?')
  if (!confirmed) return 

  try {
    const response = await fetch(`/api/ads/${ad.value.id}`, {
      method: 'DELETE',
      headers: { 
        'Authorization': `Bearer ${authStore.token}` 
      }
    })
    if (response.ok) {
      alert('Объявление удалено')
      router.push('/ads') 
    } else {
      const data = await response.json()
      alert(data.error || 'Ошибка при удалении')
    }
  } catch (error) {
    alert('Ошибка сети')
  }
}

const editAd = () => {
  router.push({name: 'edit-ad', params: { id: ad.value.id },
    state: { adData: JSON.parse(JSON.stringify(ad.value)) } 
  })
}
const contactAuthor = () => {
  if (!authStore.user) {
    router.push('/login')
    return
  }
  router.push({
    name: 'active-chat',
    params: { adId: ad.value.id, partnerId: ad.value.user_id }
  })
}
const sendReview = async () => {
  if (newReview.value.rating === 0) {
    alert('Поставьте оценку')
    return
  }

  try {
    const res = await fetch('/api/reviews', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        ad_id: ad.value.id,
        rating: newReview.value.rating,
        text: newReview.value.text
      })
    })
    const data = await res.json()
    
    if (res.ok) {
      alert('Спасибо за отзыв!')
      newReview.value = { rating: 0, text: '' }
    } else {
      alert(data.error)
    }
  } catch (error) {
    console.error(error)
  }
}
const getCategoryName = (categoryKey, adType) => {
  const categoriesList = adType === 'service' ? SERVICE_CATEGORIES : ITEM_CATEGORIES
  return categoriesList[categoryKey] || categoryKey
}

const formatPrice = (price) => {
  if (price === null || price === undefined) return '0'
  return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ")
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}
onMounted(() => { 
  fetchAd() 
})
</script>

<style scoped>
.ad-top-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}

.gallery-column { width: 100%; }
.gallery-wrapper {
  position: relative;
  width: 100%;
  padding-top: 90%;
  background-color: #f3f4f6;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 15px;
}

.image-frame {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #eee;
}

.ad-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.8);
  border: none;
  font-size: 24px;
  width: 40px; 
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 2;
  display: flex; 
  align-items: center; 
  justify-content: center;
}
.nav-btn:hover { background: white; }
.prev { left: 10px; }
.next { right: 10px; }
.little-row {
  display: flex; 
  gap: 10px;
  overflow-x: auto; 
  padding-bottom: 5px;
}

.little-item {
  width: 70px;
  height: 70px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  opacity: 0.7;
  transition: opacity 0.2s, border-color 0.2s;
}

.little-item:hover,
.little-item.active {
  opacity: 1;
}

.little-item.active {
  border-color: #3b82f6;
}

.little-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.info-column { 
  display: flex; 
  flex-direction: column; 
}

.ad-title { 
  font-size: 2rem; 
  margin: 0 0 10px 0; 
  color: #333; 
  line-height: 1.2; 
}

.ad-price { 
  font-size: 2rem; 
  font-weight: 700; 
  color: #2c3e50; 
  margin-bottom: 25px; 
}

.meta-clean { margin-bottom: 30px; }

.meta-row { 
  display: flex; 
  margin-bottom: 12px; 
  font-size: 1.05rem; 
}

.label { 
  color: #888; 
  width: 120px; 
  flex-shrink: 0; 
}

.value { 
  color: #333; 
  font-weight: 500; 
}

.actions-panel { margin-top: auto; }

.button { 
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%); 
  color: white; 
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.owner-controls { 
  display: flex; 
  gap: 15px; 
  flex-direction: column; 
}

.description-section { 
  margin-top: 20px; 
  padding-top: 20px; 
  border-top: 1px solid #eee; 
}

.section-title { 
  font-size: 1.5rem; 
  font-weight: 600; 
  margin-bottom: 15px; 
  color: #333; 
}

.vacancy-text { 
  line-height: 1.6; 
  font-size: 1.1rem; 
  color: #444; 
  white-space: pre-wrap; 
}
.seller-link { 
  color: #3b82f6; 
  text-decoration: underline; 
  font-weight: bold; 
}

.star-btn { 
  cursor: pointer; 
  font-size: 1.5rem; 
  color: #ccc; 
  margin-right: 5px;
}

.star-btn.active { 
  color: #fbbf24; 
}

.form-control {
  width: 100%;
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  min-height: 80px;
}

.back { 
  margin-top: 50px; 
  text-align: center; 
}

.back a { 
  color: #888; 
  text-decoration: none; 
}

.loading-state { 
  text-align: center; 
  padding: 50px; 
  color: #666; 
}

@media (max-width: 768px) {
  .ad-top-section { 
    grid-template-columns: 1fr; 
    gap: 20px; 
  }
  .gallery-wrapper {
    padding-top: 75%;
  }
}
</style>