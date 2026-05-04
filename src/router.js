import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Authors from './pages/Authors.vue'
import Episodes from './pages/Episodes.vue'
import Methods from './pages/Methods.vue'
import Compare from './pages/Compare.vue'
import Viz from './pages/Viz.vue'
import Detectives from './pages/Detectives.vue'
import Games from './pages/Games.vue'
import Books from './pages/Books.vue'
import MediaDetail from './pages/MediaDetail.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/authors', component: Authors },
    { path: '/episodes', component: Episodes },
    { path: '/methods', component: Methods },
    { path: '/compare', component: Compare },
    { path: '/viz', component: Viz },
    { path: '/detectives', component: Detectives },
    { path: '/games', component: Games },
    { path: '/books', component: Books },
    { path: '/media/:slug', component: MediaDetail },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
