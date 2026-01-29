import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import CreateAdView from '../views/CreateAdView.vue'
import AdsView from '../views/AdsView.vue'
import AdView from '../views/AdPageView.vue'
import EditAdView from '../views/EditAdView.vue'
import ChatView from '../views/ChatView.vue'
import ServicesView from '../views/ServicesView.vue'
import FavoritesView from '../views/FavoritesView.vue'
import UserView from '../views/UserView.vue'
import AdminView from '../views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/ads', component: AdsView },
    { path: '/ads/:id', component: AdView },
    { path: '/ads/edit/:id', name: 'edit-ad', component: EditAdView },
    { path: '/createad', component: CreateAdView },
    { path: '/chats', name: 'chats', component: ChatView },
    { path: '/chats/:adId/:partnerId', name: 'active-chat', component: ChatView },
    { path: '/services', component: ServicesView },
    { path: '/favorites', component: FavoritesView },
    { path: '/users/:id', component: UserView },
    { path: '/admin', component: AdminView },
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAdmin) {
    if (authStore.isAuthenticated && authStore.user?.is_admin) {
      next() 
    } else {
      next('/') 
    }
  } else {
    next()
  }
})

export default router
