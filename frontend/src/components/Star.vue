<template>
  <div class="stars">
    <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= value }">
      ★
    </span>
  </div>
</template>

<script setup>
defineProps({
  value: Number
})
</script>

<style scoped>
.star {
  color: #ddd;
  font-size: 1.2rem;
}
.star.filled {
  color: #f8e72f;
}
</style>