<template>
  <div class="container">
    <h1 class="title">Вход</h1>
    <form  @submit.prevent="login" class="login-form">
      <label>Почта</label>
      <input  type="email" v-model="form.email" class="form-control" required>
      
      <label>Пароль</label>
      <input  type="password" v-model="form.password" class="form-control" required>
      
      <div class="back">
        <RouterLink to="/register">
          Нет аккаунта? Зарегистрируйтесь, чтобы продолжить
        </RouterLink>
      </div>

      <button class="button" type="submit">Войти</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const form = ref({ email: '', password: '' })

const login = async (e) => {
  e.preventDefault()
  await authStore.login(form.value)
  router.push('/')
}
</script>

<style scoped>
.container {
  margin: 0 auto;
  padding: 0 20px;
}

.title {
  margin-top: 50px;
  font-size: 52px;
  text-align: center;
  margin-bottom: 30px;
}

.login-form {
  display: flex;
  flex-direction: column; 
}

.form-control {
  width: 100%;
  margin-bottom: 15px; 
  padding: 10px;
  box-sizing: border-box;
}

.back {
  text-align: center;
  margin-bottom: 20px;
}

.button {
  display: block;     
  margin: 10px auto 0;  
  
  width: 100%;
  max-width: 250px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(124, 58, 237, 0.35);
}
</style>