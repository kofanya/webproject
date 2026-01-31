import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  server: {
    port: 5173,
    strictPort: true,
    host: true,
    watch: {
      usePolling: true
    },
    hmr: {
      port: 5173,
      clientPort: 5173,
      host: 'localhost'
    },
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost'
      }
    },
    '/static': {
        target: 'http://backend:5000',
        changeOrigin: true,
      }
  }

})
