<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const authStore = useAuthStore()
const isReady = ref(false)
onMounted(async () => {
  await authStore.checkAuth()
  isReady.value = true
})
</script>

<template>
  <div class="page">
    <div v-if="isReady" class="page">
    <Header />
    <main class="content"><RouterView /></main>
    <Footer />
  </div>
  <div v-else>Загрузка...</div>
  </div>
</template>

<style>
.page{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content{
  flex: 1;
  padding-top: 70px;
}

</style>
