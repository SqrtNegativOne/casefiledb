<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import MarkCompletedModal from './MarkCompletedModal.vue'
import { mnesia } from '../composables/useCompletion.js'

defineProps(['theme'])
defineEmits(['toggle-theme'])

const menuOpen = ref(false)
const completedModalOpen = ref(false)
const route = useRoute()

const links = [
  { to: '/', label: 'Deaths' },
  { to: '/methods', label: 'Methods' },
  { to: '/people', label: 'People' },
  { to: '/media', label: 'Media' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  // /media should also light up for /media/:slug, /author/:name, /show/:name, /game-series/:slug.
  if (path === '/media') {
    return (
      route.path === '/media' ||
      route.path.startsWith('/media/') ||
      route.path.startsWith('/author/') ||
      route.path.startsWith('/show/') ||
      route.path.startsWith('/game-series/')
    )
  }
  if (path === '/people') return route.path.startsWith('/people')
  return route.path.startsWith(path)
}

function closeMenu() {
  menuOpen.value = false
}

function openCompletedModal() {
  completedModalOpen.value = true
  menuOpen.value = false
}
</script>

<template>
  <div class="site-header">
    <div class="header-inner">
      <RouterLink to="/" class="site-logo" @click="closeMenu">
        <img src="/icon.png" alt="Casefile Database" class="logo-icon" />
      </RouterLink>
      <nav :class="['site-nav', { 'nav-open': menuOpen }]">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          :class="{ active: isActive(link.to) }"
          @click="closeMenu"
        >{{ link.label }}</RouterLink>
      </nav>
      <div class="header-actions">
        <button
          class="completed-btn"
          type="button"
          @click="openCompletedModal"
          :title="mnesia ? 'Mnesia mode is on — everything is visible' : 'Mark works as completed to reveal their spoilers'"
        >
          <span class="completed-btn-label">Mark as completed</span>
          <span v-if="mnesia" class="completed-btn-mnesia" aria-label="Mnesia mode on">✦</span>
        </button>
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
  </div>
  <MarkCompletedModal :open="completedModalOpen" @close="completedModalOpen = false" />
</template>
