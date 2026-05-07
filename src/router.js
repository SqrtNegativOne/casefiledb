import { createRouter, createWebHashHistory } from 'vue-router'
import Landing from './pages/Landing.vue'
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
import About from './pages/About.vue'
import Colophon from './pages/Colophon.vue'
import Privacy from './pages/Privacy.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Landing, meta: { fullscreen: true } },
    { path: '/deaths', component: Home },
    { path: '/methods', component: Methods },
    { path: '/people', component: People },
    { path: '/media', component: Media },
    { path: '/media/:slug', component: MediaDetail },
    { path: '/author/:name', component: AuthorDetail },
    { path: '/show/:name', component: ShowDetail },
    { path: '/game-series/:slug', component: GameSeriesDetail },
    { path: '/compare', component: Compare },
    { path: '/viz', component: Viz },
    { path: '/about', component: About },
    { path: '/colophon', component: Colophon },
    { path: '/privacy', component: Privacy },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
