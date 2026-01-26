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

        <div v-if="ad.photos && ad.photos.length > 1" class="thumbnails-row">
          <div v-for="(photo, index) in ad.photos" :key="index" class="thumbnail-item":class="{ active: index === currentPhotoIndex }"
          @click="currentPhotoIndex = index">
            <img :src="`${BACKEND_URL}/static/uploads/${photo}`" alt="thumb">
          </div>
        </div>

      </div>

      <div class="info-column">
        <h1 class="ad-title">{{ ad.title }}</h1>
        <div class="ad-price">
          {{ formatPrice(ad.price) }} ₽
        </div>

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
            <button @click="editAd" type="button" class="button edit-button">
                Редактировать
            </button>
            <button @click="deleteAd" type="button" class="button delete-button">
                Удалить
            </button>
          </div>
          <div v-else>
            <div v-if="authStore.isAuthenticated">
              <button class="button contact-button">Написать автору</button>
            </div>
            <div v-else>
              <RouterLink to="/login" class="button contact-button">
                Войдите, чтобы написать
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="description-section">
      <div class="section-title">Описание</div>
      <div class="vacancy-text">
        {{ ad.description }}
      </div>
    </div>

    <div class="back">
      <RouterLink to="/ads">← Вернуться к списку объявлений</RouterLink>
    </div>
  </div>

  <div v-else class="loading-state">
    <p>Загрузка объявления...</p>
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
const isLoading = ref(true)

const fetchAd = async () => {
  try {
    const response = await fetch(`/api/ads/${route.params.id}`)
    if (!response.ok) throw new Error('Ошибка загрузки')
    ad.value = await response.json()
  } catch (e) {
    console.error(e)
    alert('Не удалось загрузить объявление')
    router.push('/ads')
  } finally {
    isLoading.value = false
  }
}

const getCurrentPhotoUrl = () => {
  if (!ad.value.photos || ad.value.photos.length === 0) return '/placeholder-image.png'
  const filename = ad.value.photos[currentPhotoIndex.value]
  return `${BACKEND_URL}/static/uploads/${filename}`
}

const nextPhoto = () => {
  if (ad.value.photos.length > 1) {
    currentPhotoIndex.value = (currentPhotoIndex.value + 1) % ad.value.photos.length
  }
}

const prevPhoto = () => {
  if (ad.value.photos.length > 1) {
    currentPhotoIndex.value = (currentPhotoIndex.value - 1 + ad.value.photos.length) % ad.value.photos.length
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
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      alert('Объявление удалено')
      router.push('/ads')
    } else {
      const data = await response.json()
      alert(data.error || 'Ошибка при удалении')
    }
  } catch (e) { alert('Ошибка сети') }
}

const editAd = () => {
  router.push({
    name: 'edit-ad', 
    params: { id: ad.value.id },
    state: { adData: JSON.parse(JSON.stringify(ad.value)) } 
  })
}

const getCategoryName = (key, type) => {
  const categories = type === 'service' ? SERVICE_CATEGORIES : ITEM_CATEGORIES
  return categories[key] || key
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}

const formatPrice = (price) => {
  if (price === null || price === undefined) return '0'
  return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ")
}

onMounted(() => { fetchAd() })
</script>

<style scoped>
.container-2 {
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 20px;
  font-family: 'Segoe UI', sans-serif;
}

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

.thumbnails-row {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.thumbnail-item {
  width: 70px;
  height: 70px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  opacity: 0.7;
  transition: all 0.2s;
}

.thumbnail-item:hover {
  opacity: 1;
}

.thumbnail-item.active {
  border-color: #3b82f6;
  opacity: 1;
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-column { 
    display: flex; 
    flex-direction: column; }
.ad-title { 
    font-size: 2rem; 
    margin: 0 0 10px 0; 
    color: #333; 
    line-height: 1.2; }
.ad-price { 
    font-size: 2rem; 
    font-weight: 700; 
    color: #2c3e50; 
    margin-bottom: 25px; }
.meta-clean { 
    margin-bottom: 30px; }
.meta-row { 
    display: flex; 
    margin-bottom: 12px; 
    font-size: 1.05rem; }
.label { 
    color: #888; 
    width: 120px; 
    flex-shrink: 0; }
.value { 
    color: #333; 
    font-weight: 500; }
.description-section { 
    margin-top: 20px; 
    padding-top: 20px; 
    border-top: 1px solid #eee; }
.section-title { 
    font-size: 1.5rem; 
    font-weight: 600; 
    margin-bottom: 15px; 
    color: #333; }
.vacancy-text { 
    line-height: 1.6; 
    font-size: 1.1rem; 
    color: #444; 
    white-space: pre-wrap; }

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.8);
  color: #333;
  border: none;
  font-size: 24px;
  width: 40px; 
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 2;
  display: flex; align-items: center; justify-content: center;
}
.nav-btn:hover { background: white; }
.prev { left: 10px; }
.next { right: 10px; }

.actions-panel { margin-top: auto; }
.contact-button { 
    background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%); 
    color: white; }
.owner-controls { 
    display: flex; 
    gap: 15px; 
    flex-direction: column; }
.edit-button { 
    background-color: #eaab46; 
    color: white; }
.delete-button { 
    background-color: #f55b4a; 
    color: white; }
.back { 
    margin-top: 50px; 
    text-align: center; }
.back a { 
    color: #888; 
    text-decoration: none; }
.loading-state { 
    text-align: center; 
    padding: 50px; 
    color: #666; }

@media (max-width: 768px) {
    .ad-top-section { 
        grid-template-columns: 1fr; gap: 20px; 
    }
    .gallery-wrapper {
    height: 350px; 
  }
}
</style>