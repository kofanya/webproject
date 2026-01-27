import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import CreateAdView from '../views/CreateAdView.vue'
import AdsView from '../views/AdsView.vue'
import AdView from '../views/AdPageView.vue'
import EditAdView from '../views/EditAdView.vue'
import ChatView from '../views/ChatView.vue'

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
  ],
})

export default router
