<template>
  <div class="container">
    <h1 class="title">Редактирование объявления</h1>
    
    <div v-if="isLoading" class="loading">Загрузка данных...</div>

    <form v-else @submit.prevent="updateAd">
      <label>Тип объявления</label>
      <div class="type-selector">
        <label class="radio-label">
          <input type="radio" value="item" v-model="form.ad_type">
          <span>Товар</span>
        </label>
        <label class="radio-label">
          <input type="radio" value="service" v-model="form.ad_type">
          <span>Услуга</span>
        </label>
      </div>

      <label>Название</label>
      <input v-model="form.title" type="text" class="form-control" required>

      <label>Цена (₽)</label>
      <input v-model.number="form.price" type="number" class="form-control" placeholder="0"> 

      <label>Описание</label>
      <textarea v-model="form.description" class="form-control textarea-scrollable" rows="10" required></textarea>

      <label>Фотографии</label>
      <div class="photos-container">
        <div v-for="(photo, index) in uploadedPhotos" :key="index" class="photo-preview">
          <img :src="`http://127.0.0.1:5000/static/uploads/${photo}`" alt="preview">
          <button type="button" class="remove-btn" @click="removePhoto(index)">×</button>
        </div>

        <label class="upload-btn" v-if="uploadedPhotos.length < 5">
          <input type="file" @change="handleFileUpload" accept="image/*" hidden>
          <span v-if="!isUploading">+</span>
          <span v-else class="loader">...</span>
        </label>
      </div>

      <label>Категория</label>
      <select v-model="form.category" class="form-control" required>
        <option disabled value="">Выберите категорию</option>
        <option v-for="(name, key) in currentCategories" :value="key" :key="key">
          {{ name }}
        </option>
      </select>

      <label>Район</label>
      <select v-model="form.district" class="form-control" required>
        <option disabled value="">Выберите район</option>
        <option v-for="dist in DISTRICTS" :key="dist" :value="dist">
          {{ dist }}
        </option>
      </select>

      <label>Адрес</label>
      <input v-model="form.address" type="text" class="form-control" required>

      <div class="button-group">
        <button class="button" type="submit">Сохранить изменения</button>
        <button class="z-button" type="button" @click="$router.back()">Отмена</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ITEM_CATEGORIES, SERVICE_CATEGORIES, DISTRICTS } from '@/utils/categories'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isLoading = ref(true)
const isUploading = ref(false)

const form = ref({
  title: '',
  description: '',
  price: null,
  district: '',
  address: '',
  category: '',
  ad_type: 'item'
})

const uploadedPhotos = ref([])

const currentCategories = computed(() => {
  return form.value.ad_type === 'item' ? ITEM_CATEGORIES : SERVICE_CATEGORIES
})

watch(() => form.value.ad_type, (newVal, oldVal) => {
    if (oldVal !== undefined && !isLoading.value) {
        form.value.category = '' 
    }
})

const loadAdData = async () => {
  try {
    const adId = route.params.id
    const response = await fetch(`/api/ads/${adId}`)
    
    if (!response.ok) throw new Error('Ошибка при загрузке данных')
    
    const data = await response.json()
    
    form.value = {
      title: data.title,
      description: data.description, 
      price: data.price,
      district: data.district,
      address: data.address,
      category: data.category,
      ad_type: data.ad_type
    }
    
    if (data.photos) {
        uploadedPhotos.value = data.photos
    }
    
  } catch (e) {
    console.error(e)
    alert('Не удалось загрузить объявление')
    router.push('/ads')
  } finally {
    isLoading.value = false
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUploading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${authStore.token}` },
      body: formData
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error)

    uploadedPhotos.value.push(data.filename)
  } catch (e) {
    alert('Ошибка загрузки фото: ' + e.message)
  } finally {
    isUploading.value = false
    event.target.value = ''
  }
}

const removePhoto = (index) => {
  uploadedPhotos.value.splice(index, 1)
}

const updateAd = async () => {
  try {
    const adId = route.params.id
    const response = await fetch(`/api/ads/${adId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        ...form.value,
        photos: uploadedPhotos.value 
      })
    })

    const data = await response.json()
    
    if (!response.ok) {
        throw new Error(data.error || 'Ошибка при обновлении')
    }

    alert('Объявление успешно обновлено!')
    router.push(`/ads/${adId}`) 

  } catch (e) {
    alert(e.message)
  }
}

onMounted(() => {
  loadAdData()
})
</script>

<style scoped>
form {
  width: 100%;
  max-width: 700px; 
  padding: 0 20px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px; 
}
.loading {
    text-align: center;
    font-size: 1.2rem;
    color: #666;
    margin-top: 50px;
}
.type-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 5px;
}
.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.photos-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.photo-preview {
  width: 80px;
  height: 80px;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
.photo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.remove-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(0,0,0,0.6);
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.upload-btn {
  width: 80px;
  height: 80px;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #718096;
  font-size: 24px;
  transition: all 0.2s;
}
.upload-btn:hover {
  border-color: #7c3aed;
  color: #7c3aed;
  background: #f7fafc;
}
.button-group {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 16px;              
  margin-top: 12px;
}
.button, .z-button {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 50px;           
  width: 100%;            
  max-width: 400px;       
  border-radius: 12px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  margin: 0;
}
.button {
    background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
    color: white;
}
.button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.35);
}
.z-button {
  border: 2px solid transparent;
  background: 
    linear-gradient(#fff, #fff) padding-box, 
    linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%) border-box;
  color: #7c3aed;
}
.z-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
  background: 
    linear-gradient(#f8faff, #f8faff) padding-box, 
    linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%) border-box;
}
@media (max-width: 600px) {
  .button-group {
    flex-direction: column;
    align-items: center;   
  }
  .button, .z-button {
    max-width: 100%;       
  }
}
</style>