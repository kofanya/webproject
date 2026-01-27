<template>
  <div class="chat-container">
    
    <div class="chat-sidebar" :class="{ 'mobile-hidden': isMobileChatActive }">
      <h2 class="sidebar-title">Сообщения</h2>
      
      <div v-if="isLoadingList" class="loading">Загрузка...</div>
      
      <div v-else-if="chats.length === 0" class="empty-list">
        У вас пока нет диалогов
      </div>

      <div class="chat-list">
        <div 
          v-for="chat in chats" 
          :key="chat.ad_id + '-' + chat.partner_id"
          class="chat-item"
          :class="{ active: isChatActive(chat) }"
          @click="selectChat(chat)"
        >
          <div class="chat-avatar">
            <img v-if="chat.ad_photo" :src="`${BACKEND_URL}/static/uploads/${chat.ad_photo}`" alt="ad">
            <div v-else class="avatar-placeholder">{{ chat.partner_name[0] }}</div>
          </div>
          <div class="chat-details">
            <div class="chat-header">
              <span class="partner-name">{{ chat.partner_name }}</span>
              <span class="chat-date">{{ formatTime(chat.last_message_date) }}</span>
            </div>
            <div class="ad-name">{{ chat.ad_title }}</div>
            <div class="last-message">{{ chat.last_message }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-main" :class="{ 'mobile-visible': isMobileChatActive }">
      
      <div v-if="activePartnerId" class="messages-wrapper">
        <div class="messages-header">
          <button class="back-btn" @click="closeChat">←</button>
          <div class="header-info">
             <h3>Чат по объявлению #{{ activeAdId }}</h3>
          </div>
        </div>

        <div class="messages-list" ref="messagesContainer">
          <div v-if="messagesLoading" class="loading">Загрузка истории...</div>
          
          <div 
            v-for="msg in messages" 
            :key="msg.id" 
            class="message-bubble"
            :class="{ 'mine': msg.is_mine, 'theirs': !msg.is_mine }"
          >
            <div class="message-text">{{ msg.body }}</div>
            <div class="message-time">{{ formatTime(msg.created_date) }}</div>
          </div>
        </div>

        <div class="message-input-area">
          <input 
            v-model="newMessage" 
            @keyup.enter="sendMessage"
            type="text" 
            placeholder="Сообщение" 
            class="input-field"
          >
          <button @click="sendMessage" class="send-btn" :disabled="!newMessage.trim()">
            ➤
          </button>
        </div>
      </div>

      <div v-else class="no-chat-selected">
        <p>Выберите чат слева или начните новый со страницы объявления</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const BACKEND_URL = 'http://127.0.0.1:5000'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const chats = ref([])
const messages = ref([])
const newMessage = ref('')
const isLoadingList = ref(true)
const messagesLoading = ref(false)
const messagesContainer = ref(null)

const activeAdId = computed(() => route.params.adId)
const activePartnerId = computed(() => route.params.partnerId)
const isMobileChatActive = computed(() => !!activeAdId.value)

let pollingInterval = null

const fetchChats = async () => {
  try {
    const res = await fetch('/api/chats', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      chats.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingList.value = false
  }
}

const fetchMessages = async () => {
  if (!activeAdId.value || !activePartnerId.value) return

  if (messages.value.length === 0) messagesLoading.value = true

  try {
    const res = await fetch(`/api/chats/${activeAdId.value}/${activePartnerId.value}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      const newMessages = await res.json()
      if (newMessages.length > messages.value.length) {
        messages.value = newMessages
        scrollToBottom()
      } else {
        messages.value = newMessages
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    messagesLoading.value = false
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return

  const body = newMessage.value
  newMessage.value = ''

  try {
    const res = await fetch('/api/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        ad_id: activeAdId.value,
        recipient_id: activePartnerId.value,
        body: body
      })
    })

    if (res.ok) {
      await fetchMessages()
      await fetchChats()    
    } else {
      alert('Ошибка отправки')
    }
  } catch (e) {
    alert('Ошибка сети')
  }
}

const selectChat = (chat) => {
  router.push({
    name: 'active-chat',
    params: { adId: chat.ad_id, partnerId: chat.partner_id }
  })
}

const closeChat = () => {
  router.push('/chats')
}

const isChatActive = (chat) => {
  return String(chat.ad_id) === String(activeAdId.value) && 
         String(chat.partner_id) === String(activePartnerId.value)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (isoString) => {
  if (!isoString) return ''
  if (!isoString.endsWith('Z') && !isoString.includes('+')) {
    isoString += 'Z'
  }

  const date = new Date(isoString)
  const now = new Date()
  const isToday = date.getDate() === now.getDate() &&
                  date.getMonth() === now.getMonth() &&
                  date.getFullYear() === now.getFullYear()
  if (isToday) {
    return date.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } 
  else {
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
    }) + ' ' + date.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  fetchChats()
  
  if (activeAdId.value) {
    fetchMessages()
  }

  pollingInterval = setInterval(() => {
    if (activeAdId.value) fetchMessages()
    fetchChats()
  }, 3000)
})

onUnmounted(() => {
  clearInterval(pollingInterval)
})

watch(() => route.params, (newParams) => {
  if (newParams.adId && newParams.partnerId) {
    messages.value = []
    fetchMessages()
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 80px); 
  max-width: 1200px;
  margin: 20px auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  overflow: hidden;
}

.chat-sidebar {
  width: 350px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.sidebar-title {
  padding: 20px;
  margin: 0;
  font-size: 1.2rem;
  border-bottom: 1px solid #ddd;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
}

.chat-item {
  display: flex;
  padding: 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.chat-item:hover { background: #f0f0f0; }
.chat-item.active { background: #e6f0ff; border-left: 4px solid #3b82f6; }

.chat-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
  background: #ddd;
  flex-shrink: 0;
}

.chat-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder { display: flex; align-items: center; justify-content: center; height: 100%; font-weight: bold; color: #666; font-size: 1.2rem; }

.chat-details { flex: 1; overflow: hidden; }
.chat-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.partner-name { font-weight: 600; font-size: 0.95rem; }
.chat-date { font-size: 0.8rem; color: #888; }
.ad-name { font-size: 0.85rem; color: #3b82f6; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.last-message { font-size: 0.9rem; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
}
.messages-header h3 { margin: 0; font-size: 1.1rem; }
.back-btn { display: none; background: none; border: none; font-size: 1.5rem; cursor: pointer; }

.messages-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #f4f6f8;
}

.message-bubble {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 12px;
  position: relative;
  font-size: 0.95rem;
  line-height: 1.4;
}

.message-bubble.mine {
  align-self: flex-end;
  background-color: #3b82f6;
  color: white;
  border-bottom-right-radius: 2px;
}

.message-bubble.theirs {
  align-self: flex-start;
  background-color: #fff;
  border: 1px solid #ddd;
  color: #333;
  border-bottom-left-radius: 2px;
}

.message-time {
  font-size: 0.7rem;
  margin-top: 5px;
  text-align: right;
  opacity: 0.7;
}

.message-input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

.input-field {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 25px;
  outline: none;
}
.input-field:focus { border-color: #3b82f6; }

.send-btn {
  background: #3b82f6;
  color: white;
  border: none;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex; align-items: center; justify-content: center;
}
.send-btn:disabled { background: #ccc; }

.no-chat-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.loading, .empty-list { text-align: center; padding: 20px; color: #888; }

@media (max-width: 768px) {
  .chat-sidebar { width: 100%; border-right: none; }
  .chat-main { display: none; }
  .mobile-hidden { display: none; }
  .chat-main.mobile-visible { display: flex; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 100; }
  .back-btn { display: block; }
}
</style>