<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useData, allItems, deathCount } from '../composables/useData.js'
import { GAME_SERIES, gamesInSeries } from '../composables/gameSeries.js'
import { canReveal } from '../composables/useCompletion.js'

const { data, ensureLoaded } = useData()
const route = useRoute()
const router = useRouter()
onMounted(ensureLoaded)

const search = ref('')
const typeFilter = ref('')
const sortField = ref('title')
const sortDir = ref('asc')
const showFilters = ref(false)

const hasActiveFilters = computed(() =>
  typeFilter.value || sortField.value !== 'title' || sortDir.value !== 'asc'
)

onMounted(() => {
  if (route.query.type) typeFilter.value = String(route.query.type)
})

const mediaTypes = computed(() => {
  const counts = new Map()
  for (const m of allItems.value) {
    if (!m.media_type) continue
    counts.set(m.media_type, (counts.get(m.media_type) || 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])
})

const games = computed(() => data.value.games || [])
const seriesRows = computed(() =>
  GAME_SERIES.map((s) => {
    const list = gamesInSeries(s, games.value)
    const deaths = list.reduce((n, g) => n + deathCount(g), 0)
    return { ...s, games: list, deaths }
  }).filter((s) => s.games.length)
)

const showRows = computed(() => {
  // Both first-class tv_shows and virtual groupings of standalone tv_episodes
  // by series_name show up as a "Show" with aggregate stats.
  const map = new Map()
  for (const s of (data.value.tv_shows || [])) {
    map.set(s.title, { name: s.title, episodes: (s.episodes || []).length, deaths: deathCount(s) })
  }
  for (const ep of (data.value.tv_episodes || [])) {
    const key = ep.series_name || ep.title
    if (!map.has(key)) map.set(key, { name: key, episodes: 0, deaths: 0 })
    const e = map.get(key)
    e.episodes++
    e.deaths += (ep.deaths || []).length
  }
  return [...map.values()].sort((a, b) => b.deaths - a.deaths || a.name.localeCompare(b.name))
})

function sortValue(m, f) {
  // Per-work death counts are spoilers; only sort by them when revealed.
  if (f === 'deaths') return canReveal(m) ? deathCount(m) : -1
  if (f === 'year') return Number(m.year || 0)
  return String(m[f] || '').toLowerCase()
}

function deathCellLabel(m) {
  return canReveal(m) ? deathCount(m) : '—'
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const t = typeFilter.value
  const dir = sortDir.value === 'desc' ? -1 : 1
  return allItems.value
    .filter((m) => {
      if (t && m.media_type !== t) return false
      if (!q) return true
      const hay = [m.title, m.creator, m.series_name].filter(Boolean).join(' ').toLowerCase()
      return hay.includes(q)
    })
    .sort((a, b) => {
      const av = sortValue(a, sortField.value)
      const bv = sortValue(b, sortField.value)
      let r = typeof av === 'number' ? av - bv : String(av).localeCompare(String(bv), undefined, { sensitivity: 'base', numeric: true })
      if (r === 0) r = String(a.title).localeCompare(String(b.title))
      return r * dir
    })
})

function setSort(f) {
  if (sortField.value === f) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortField.value = f; sortDir.value = 'asc' }
}
function sortState(f) { return sortField.value === f ? sortDir.value : null }

function setType(t) {
  typeFilter.value = t
  router.replace({ query: t ? { type: t } : {} })
}

function authorRoute(name) {
  return { path: `/author/${encodeURIComponent(name)}` }
}
</script>

<template>
  <div>
    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search title, creator, series…" />
      <button type="button" :class="['filter-toggle-btn', { 'filter-toggle-btn-active': showFilters || hasActiveFilters }]" @click="showFilters = !showFilters">
        Filter &amp; Sort{{ hasActiveFilters ? ' ·' : '' }}
      </button>
    </div>

    <div v-show="showFilters" class="filter-panel">
      <div class="filter-chips">
        <button type="button" :class="['chip', { 'chip-active': typeFilter === '' }]" @click="setType('')">
          All <span class="muted">{{ allItems.length }}</span>
        </button>
        <button
          v-for="[t, n] in mediaTypes"
          :key="t"
          type="button"
          :class="['chip', { 'chip-active': typeFilter === t }]"
          @click="setType(t)"
        >
          {{ t.replace(/_/g, ' ') }} <span class="muted">{{ n }}</span>
        </button>
      </div>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.5rem">
        <select v-model="sortField">
          <option value="title">Sort: Title</option>
          <option value="creator">Sort: Creator</option>
          <option value="year">Sort: Year</option>
          <option value="series_name">Sort: Series</option>
          <option value="deaths">Sort: Deaths</option>
        </select>
        <select v-model="sortDir">
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
      </div>
    </div>
    <div class="meta-row">{{ rows.length }} item{{ rows.length === 1 ? '' : 's' }}</div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th :data-sort-state="sortState('title')" class="sortable" @click="setSort('title')">Title</th>
            <th :data-sort-state="sortState('media_type')" class="sortable" @click="setSort('media_type')">Type</th>
            <th :data-sort-state="sortState('creator')" class="sortable" @click="setSort('creator')">Creator</th>
            <th :data-sort-state="sortState('year')" class="sortable" @click="setSort('year')">Year</th>
            <th :data-sort-state="sortState('series_name')" class="sortable" @click="setSort('series_name')">Series</th>
            <th :data-sort-state="sortState('deaths')" class="sortable" @click="setSort('deaths')">Deaths</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length"><td colspan="6" class="muted">No matches.</td></tr>
          <tr v-for="m in rows" :key="m.slug">
            <td>
              <RouterLink :to="`/media/${m.slug}`">{{ m.title }}</RouterLink>
            </td>
            <td>
              <span :class="['badge', `badge-${m.media_type}`]">{{ m.media_type }}</span>
            </td>
            <td>
              <RouterLink v-if="m.creator" :to="authorRoute(m.creator)" class="muted">{{ m.creator }}</RouterLink>
              <span v-else class="muted">—</span>
            </td>
            <td>{{ m.year || '—' }}</td>
            <td>
              <span v-if="m.series_name">
                {{ m.series_name }}
                <span v-if="m.series_number != null" class="muted"> #{{ m.series_number }}</span>
              </span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <span v-if="canReveal(m)">{{ deathCount(m) }}</span>
              <span v-else class="muted" title="Mark this work as completed to reveal its death count">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <template v-if="(typeFilter === '' || typeFilter === 'game') && seriesRows.length">
      <h3>Game series</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Series</th><th>Games</th><th>Deaths</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in seriesRows" :key="s.slug">
              <td>
                <RouterLink :to="`/game-series/${s.slug}`">{{ s.name }}</RouterLink>
                <div class="muted" style="font-size:0.78rem">{{ s.description }}</div>
              </td>
              <td>{{ s.games.length }}</td>
              <td>{{ s.deaths }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template v-if="(typeFilter === '' || typeFilter === 'tv_show' || typeFilter === 'tv_episode') && showRows.length">
      <h3>Shows</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Show</th><th>Episodes</th><th>Deaths</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in showRows" :key="s.name">
              <td>
                <RouterLink :to="`/show/${encodeURIComponent(s.name)}`">{{ s.name }}</RouterLink>
              </td>
              <td>{{ s.episodes }}</td>
              <td>{{ s.deaths }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
