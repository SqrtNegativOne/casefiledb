<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

defineProps(['theme'])
defineEmits(['toggle-theme'])

const menuOpen = ref(false)
const route = useRoute()

const links = [
  { to: '/', label: 'Media' },
  { to: '/authors', label: 'Authors' },
  { to: '/episodes', label: 'Episodes' },
  { to: '/methods', label: 'Methods' },
  { to: '/detectives', label: 'Detectives' },
  { to: '/games', label: 'Games' },
  { to: '/books', label: 'Books' },
  { to: '/compare', label: 'Compare' },
  { to: '/viz', label: 'Viz' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function closeMenu() {
  menuOpen.value = false
}
</script>

<template>
  <div class="site-header">
    <div class="header-inner">
      <RouterLink to="/" class="site-logo" @click="closeMenu">
        <span class="logo-mark">⬡</span>
        <span>Casefile Database</span>
      </RouterLink>
      <div class="header-actions">
        <button
          class="theme-btn"
          type="button"
          @click="$emit('toggle-theme')"
          :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
        >{{ theme === 'dark' ? '☀' : '☾' }}</button>
        <button
          :class="['nav-toggle', { open: menuOpen }]"
          type="button"
          @click="menuOpen = !menuOpen"
          :aria-expanded="menuOpen"
          aria-label="Toggle navigation"
        >
          <span /><span /><span />
        </button>
      </div>
    </div>
    <nav :class="['site-nav', { 'nav-open': menuOpen }]">
      <RouterLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        :class="{ active: isActive(link.to) }"
        @click="closeMenu"
      >{{ link.label }}</RouterLink>
    </nav>
  </div>
</template>
