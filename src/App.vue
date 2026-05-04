<script setup>
import { ref, onMounted } from 'vue'
import SiteNav from './components/SiteNav.vue'

const theme = ref('light')

function setTheme(t) {
  theme.value = t
  document.documentElement.setAttribute('data-theme', t)
  localStorage.setItem('casefile-theme', t)
}

function toggleTheme() {
  setTheme(theme.value === 'dark' ? 'light' : 'dark')
}

onMounted(() => {
  const saved = localStorage.getItem('casefile-theme')
  const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  setTheme(saved === 'light' || saved === 'dark' ? saved : preferred)
})
</script>

<template>
  <SiteNav :theme="theme" @toggle-theme="toggleTheme" />
  <div class="page-body">
    <RouterView />
  </div>
</template>
