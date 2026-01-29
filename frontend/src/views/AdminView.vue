<template>
  <div v-if="authStore.user?.is_admin" class="admin-container">
    <h1>Панель администратора</h1>
    
    <div class="tabs">
      <button @click="currentTab = 'users'" class="tab-btn" :class="{ active: currentTab === 'users' }">
        Пользователи
      </button>
      <button @click="currentTab = 'ads'" class="tab-btn" :class="{ active: currentTab === 'ads' }">
        Объявления
      </button>
      <button @click="currentTab = 'reviews'" class="tab-btn" :class="{ active: currentTab === 'reviews' }">
        Отзывы
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="currentTab === 'users'">
        <h2>Список пользователей</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Email</th>
              <th>Кол-во объявлений</th>
              <th>Роль</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.name }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.ads_count }}</td>
              <td>
                <span v-if="user.is_admin">Админ</span>
                <span v-else>Пользователь</span>
              </td>
              <td>
                <button v-if="!user.is_admin" @click="makeAdmin(user)" class="btn-green">
                  Сделать админом
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="users.length === 0">Пользователей нет.</div>
      </div>

      <div v-if="currentTab === 'ads'">
        <h2>Список объявлений</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Заголовок</th>
              <th>Ссылка на объявление</th> 
              <th>Пользователь</th>
              <th>Дата создания</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ad in ads" :key="ad.id">
              <td>{{ ad.id }}</td>
              <td>{{ ad.title }}</td>
              <td>
                <RouterLink :to="`/ads/${ad.id}`" target="_blank" class="link-view">
                  Посмотреть
                </RouterLink>
              </td>
              <td>{{ ad.author_email }}</td>
              <td>{{ new Date(ad.created_date).toLocaleDateString() }}</td>
              <td>
                <button @click="deleteAd(ad.id)" class="btn-delete">
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="ads.length === 0">Объявлений нет.</div>
      </div>

      <div v-if="currentTab === 'reviews'">
        <h2>Все отзывы на сайте</h2>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Оценка</th>
              <th>Текст</th>
              <th>Ссылка на объявление</th>
              <th>Автор</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="review in reviews" :key="review.id">
              <td>{{ review.id }}</td>
              <td>{{ review.rating }}</td>
              <td>{{ review.text }}</td>
              <td>
                <RouterLink v-if="review.ad_id" :to="`/ads/${review.ad_id}`" target="_blank" class="link-view">
                  Посмотреть
                </RouterLink>
                <span v-else style="color:gray">Товар удален</span>
              </td>
              <td>{{ review.author }}</td>
              <td>
                <button @click="deleteReview(review.id)" class="btn-delete">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="reviews.length === 0">Отзывов пока нет.</div>
      </div>
    </div>
  </div>
  <div v-else >
    <h1>Доступ запрещен</h1>
    <p>Эта страница доступна только администраторам.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const currentTab = ref('users');
const users = ref([]);
const ads = ref([]);
const reviews = ref([]);
const error = ref(null);

const fetchUsers = async () => {
  try {
    const res = await fetch('/api/admin/users', { credentials: 'include' });
    if (res.ok) users.value = await res.json();
  } catch (e) {
    error.value = "Ошибка загрузки пользователей";
  } 
};

const makeAdmin = async (user) => {
  if (!confirm(`Сделать пользователя ${user.name} администратором?`)) return;

  try {
    const res = await fetch(`/api/admin/users/${user.id}/make_admin`, {
      method: 'PUT',
      credentials: 'include'
    });
    if (res.ok) {
      alert('Пользователь теперь админ!');
      user.is_admin = true;
    } else {
      alert('Ошибка при назначении');
    }
  } catch (e) {
    alert('Ошибка сети');
  }
};
const fetchAds = async () => {
  try {
    const res = await fetch('/api/admin/ads', { credentials: 'include' });
    if (res.ok) ads.value = await res.json();
  } catch (e) {
      console.error(e);
  }
};

const deleteAd = async (id) => {
  if (!confirm('Удалить это объявлеие?')) return;
  await fetch(`/api/admin/ads/${id}`, { method: 'DELETE', credentials: 'include' });
  ads.value = ads.value.filter(item => item.id !== id);
};

const fetchReviews = async () => {
  try {
    const res = await fetch('/api/admin/reviews', { credentials: 'include' });
    if (res.ok) reviews.value = await res.json();
  } catch (e) {
      console.error(e);
  }
};

const deleteReview = async (id) => {
  if (!confirm('Удалить этот отзыв?')) return;
  await fetch(`/api/admin/reviews/${id}`, 
  { method: 'DELETE', credentials: 'include' });
  reviews.value = reviews.value.filter(item => item.id !== id);
};

onMounted(() => { fetchUsers(); });

watch(currentTab, (newTab) => {
  if (newTab === 'users') fetchUsers();
  if (newTab === 'ads') fetchAds();
  if (newTab === 'reviews') fetchReviews();
});
</script>

<style scoped>
.admin-container {
  padding: 20px;
}

.tabs {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
.tab-btn {
  padding: 8px 16px;
  cursor: pointer;
  background: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 12px;
}

.tab-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.table th, .table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}

.btn-green {
  background: rgb(7, 192, 34);
  color: white;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 12px;
}
.btn-delete {
  background: rgb(192, 7, 7);
  color: white;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 12px;
}
.link-view {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}
.link-view:hover {
  text-decoration: underline;
}
</style>