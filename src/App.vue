<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import SiteNav from './components/SiteNav.vue'

const theme = ref('light')
const route = useRoute()

const isFullscreen = computed(() => route.meta?.fullscreen)

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

  document.addEventListener('click', (e) => {
    const el = e.target.closest('.sensitive')
    if (el) el.classList.toggle('revealed')
  })
})
</script>

<template>
  <SiteNav :theme="theme" @toggle-theme="toggleTheme" />
  <div :class="isFullscreen ? null : 'page-body'">
    <RouterView />
  </div>
</template>
