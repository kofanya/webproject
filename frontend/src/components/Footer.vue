<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="footer">
    <div class="footer-container">
      
      <div class="footer-brand">
        <RouterLink to="/" class="brand-link">
          <h3 class="logo-text">Барахолка</h3>
        </RouterLink>
      </div>

      <ul class="footer-social">
        <li>
          <a href="https://github.com/kofanya/webproject" target="_blank" class="social-link" aria-label="GitHub">
            GitHub
          </a>
        </li>
      </ul>

    </div>
  </footer>
</template>

<style scoped>
.footer {
  background-color: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(0, 0, 0, 0.05); 
  padding: 24px 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1250px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 10px;
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

.copyright {
  color: #94a3b8; 
  font-size: 14px;
  font-weight: 400;
  border-left: 1px solid #e2e8f0;
  padding-left: 20px;
  margin-left: 0px;
}
.footer-social {
  list-style: none;
  display: flex;
  gap: 24px;
  margin: 0;
  padding: 0;
}

.social-link {
  text-decoration: none;
  color: #64748b; 
  font-weight: 500;
  font-size: 14px;
  transition: color 0.2s;
}

.social-link:hover {
  color: #4f46e5; 
}

@media (max-width: 600px) {
  .footer-container {
    flex-direction: column; 
    gap: 20px;
    text-align: center;
  }

  .footer-brand {
    flex-direction: column;
    gap: 12px;
  }
}
</style>