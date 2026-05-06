import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Methods from './pages/Methods.vue'
import People from './pages/People.vue'
import Media from './pages/Media.vue'
import MediaDetail from './pages/MediaDetail.vue'
import AuthorDetail from './pages/AuthorDetail.vue'
import ShowDetail from './pages/ShowDetail.vue'
import GameSeriesDetail from './pages/GameSeriesDetail.vue'
import Compare from './pages/Compare.vue'
import Viz from './pages/Viz.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/methods', component: Methods },
    { path: '/people', component: People },
    { path: '/media', component: Media },
    { path: '/media/:slug', component: MediaDetail },
    { path: '/author/:name', component: AuthorDetail },
    { path: '/show/:name', component: ShowDetail },
    { path: '/game-series/:slug', component: GameSeriesDetail },
    { path: '/compare', component: Compare },
    { path: '/viz', component: Viz },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
