<template>
  <main class="main-bg">
    <div class="page">
      <div class="text-column">
        <h1 class="welcome-title">Найди нужные тебе товары и услуги в одном месте!</h1>
      </div>
      <div class="image-column">
       <img :src="welcomeImage" class="welcome-img" alt="Welcome" />
      </div>
    </div>
  </main>
</template>
<script setup>
  import welcomeImage from '@/assets/photo.jpg'
</script>

<style scoped>
.main-bg {
    background-color: rgba(211, 237, 255, 0.3);
    min-height: calc(100vh - 50px); 
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  max-width: 1250px;
  margin: 0 auto;
  align-items: center; 
  padding: 20px;
  box-sizing: border-box;
}

.welcome-title {
  font-size: 52px;
  font-weight: bold;
  margin-bottom: 24px;
  line-height: 1.2;
}

.text-column {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.welcome-img {
  width: 100%;
  height: auto;
  max-width: 700px;
  object-fit: contain;
  display: block;
  border-radius: 50px;
}

.image-column {
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (max-width: 1024px) {
  .welcome-title {
    font-size: 42px;
  }
}

@media (max-width: 900px) {
  .page {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 0;
  }

  .text-column {
    align-items: center;
    order: 2;
    padding-top: 0;
  }

  .image-column {
    order: 1;
    margin-bottom: -30px;
  }

  .welcome-title {
    font-size: 32px;
    margin-top: 10px;
  }

  .welcome-img {
    max-height: 400px;
    width: auto;
    max-width: 80%;
    margin: 0 auto;
  }
}
</style>