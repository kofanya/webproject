import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    user: { name: '', id: null, is_admin: false },
    isCheckingAuth: true 
  }),
  actions: {
    async login(credentials) {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      const data = await res.json()
      if (data.success) {
        await this.checkAuth()
      } else {
        alert(data.error || 'Ошибка входа')
      }
    },
    async checkAuth() {
      this.isCheckingAuth = true 
      try {
        const res = await fetch('/api/auth/me', { credentials: 'include' })
        if (res.ok) {
          const data = await res.json()
          this.isAuthenticated = true
          this.user = { name: data.user.name, id: data.user.id, is_admin: data.user.is_admin }
        } else {
          const refreshRes = await fetch('/api/auth/refresh', { method: 'POST', credentials: 'include' })
          if (refreshRes.ok) {
            await this.checkAuth()
            return
          }
          this.logout()
        }
      } finally {
        this.isCheckingAuth = false
      }
    },
    logout() {
      fetch('/api/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => {})
      this.isAuthenticated = false
      this.user = { name: '', id: null, is_admin: false }
      this.isCheckingAuth = false
    }
  }
})