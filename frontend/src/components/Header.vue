<template>
  <header class="header">
    <div class="header-container">
      <div class="header-logo">
        <RouterLink to="/">
          <h3 class="logo-text">Барахолка</h3>
        </RouterLink>
      </div>

      <div class="header-right-side">
        <nav class="header-nav" :class="{ 'is-open': isMenuOpen }">
          <ul class="nav-list">
            <li @click="closeMenu">
                <RouterLink to="/ads" class="nav-link">Смотреть объявления</RouterLink>
            </li>
            <li @click="closeMenu">
                <RouterLink to="/ads" class="nav-link">Услуги</RouterLink>
            </li>
            <li @click="closeMenu">
                <RouterLink to="/ads" class="nav-link">Избранное</RouterLink>
            </li>
            <li @click="closeMenu">
                <RouterLink to="/createad" class="nav-link">Разместить объявление</RouterLink>
            </li>
            <template v-if="authStore.isAuthenticated">
              <li @click="closeMenu">
                <RouterLink to="/chats" class="nav-link">Сообщения</RouterLink>
              </li>
              <li class="user-greeting">
                Привет, {{ authStore.user?.name }}!
              </li>
              <li @click="logout">
                <button class="login-button">Выйти</button>
              </li>
            </template>

            <template v-else>
              <li @click="closeMenu">
                <RouterLink to="/register" class="nav-link">Регистрация</RouterLink>
              </li>
              <li @click="closeMenu">
                <RouterLink to="/login" class="login-button">Вход</RouterLink>
              </li>
            </template>
          </ul>
        </nav>

        <div v-if="isMenuOpen" class="overlay" @click="closeMenu"></div>

        <div>
          <button 
            class="burger-btn" 
            @click="isMenuOpen = !isMenuOpen" 
            :class="{ 'is-active': isMenuOpen }"
            aria-label="Меню">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const isMenuOpen = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const closeMenu = () => {
  isMenuOpen.value = false
}

const logout = async () => {
  closeMenu()
  await authStore.logout()
  router.push('/')
}
</script>

<style scoped>
:root {
  --primary-blue: #3b82f6;   
  --primary-purple: #8b5cf6;    
  --dark-text: #1e293b;         
  --light-bg: rgba(255, 255, 255, 0.85); 
  --gradient-main: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
}

.header {
  background-color: var(--light-bg);
  backdrop-filter: blur(12px); 
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  height: 70px;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 100;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.header-container {
  max-width: 1250px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 24px;
}

.header-logo a { 
  text-decoration: none; 
}

.logo-text {
  font-size: 30px;
  font-weight: 900;
  margin: 0;

  background: linear-gradient(135deg, #2563eb, #7c3aed);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.header-right-side {
  display: flex;
  align-items: center;
}

.nav-list {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 32px; 
  margin: 0;
  padding: 0;
}

.nav-link {
  text-decoration: none;
  color: #64748b; 
  font-weight: 500;
  font-size: 15px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #3b82f6;
}

.login-button {
  padding: 10px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
  color: white;
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.login-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(124, 58, 237, 0.35);
}

.login-button:active {
  transform: translateY(0);
}
.burger-btn {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 1001;
}

.burger-btn span {
  width: 24px;
  height: 2.5px;
  background-color: #334155;
  border-radius: 4px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: center;
}

.burger-btn:hover span {
  background-color: #7c3aed;
}

.burger-btn.is-active span:nth-child(1) {
  transform: translateY(7.5px) rotate(45deg);
  background-color: #7c3aed;
}
.burger-btn.is-active span:nth-child(2) {
  opacity: 0;
  transform: translateX(-10px);
}
.burger-btn.is-active span:nth-child(3) {
  transform: translateY(-7.5px) rotate(-45deg);
  background-color: #7c3aed;
}

@media (max-width: 900px) {
  .burger-btn {
    display: flex;
  }

  .header-nav {
    position: fixed;
    top: 0;
    right: -100%;
    width: 100%;
    max-width: 300px;
    height: 100vh;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    padding: 100px 30px;
    transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: -10px 0 40px rgba(0,0,0,0.1);
    z-index: 1000;
  }

  .header-nav.is-open {
    right: 0;
  }

  .nav-list {
    flex-direction: column;
    align-items: flex-start;
    gap: 30px;
  }

  .nav-link {
    font-size: 18px;
    color: #1e293b;
    font-weight: 600;
  }

  .login-button {
    width: 100%;
    text-align: center;
    justify-content: center;
    display: flex;
  }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(2px);
    z-index: 999;
    animation: fadeIn 0.3s ease;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>