<template>
  <div class="container">
    <h1 class="title">Регистрация</h1>
    
    <form @submit.prevent="register" class="registration-form">
      <label>Имя</label>
      <input type="text" v-model="registerForm.name" class="form-control" required>

      <label>Фамилия</label>
      <input type="text" v-model="registerForm.last_name" class="form-control" required>

      <label>Почта</label>
      <input type="email" v-model="registerForm.email" class="form-control" required>

      <label>Пароль</label>
      <input type="password" v-model="registerForm.password" class="form-control" required>

      <div class="back">
        <RouterLink to="/login">
          Уже зарегистрированы? Войдите, чтобы продолжить
        </RouterLink>
      </div>
      
      <button class="button" type="submit">Зарегистрироваться</button>
    </form>
  </div>
</template>

<style scoped>
.container {
  margin: 0 auto;
  padding: 20px;
}

.title {
  text-align: center;
  margin-top: 50px;
  margin-bottom: 30px;
}

.registration-form {
  display: flex;
  flex-direction: column;
}

.form-control {
  width: 100%;
  margin-bottom: 15px;
  padding: 8px;
  box-sizing: border-box;
}

.back {
  text-align: center;
  margin-bottom: 20px;
}

.button {
  display: block;    
  margin: 20px auto 0;  
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
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(124, 58, 237, 0.35);
}
</style>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const registerForm = ref({
  name: '',
  last_name: '',
  email: '',
  password: ''
})

const register = async () => {
  if (loading.value) return

  loading.value = true
  try {
    const res = await fetch('/api/auth/register', { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerForm.value)
    })

    const data = await res.json()

    if (res.ok) {
      alert('Регистрация успешна!')
      router.push('/login')
    } else {
      alert(data.error || 'Ошибка регистрации')
    }
  } catch (err) {
    console.error(err)
    alert('Не удалось подключиться к серверу')
  } finally {
    loading.value = false
  }
}
</script>