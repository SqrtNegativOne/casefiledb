<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useData } from '../composables/useData.js'

const { data, ensureLoaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

const search = ref('')
const showFilter = ref('')
const sortField = ref('show')
const sortDir = ref('asc')

const episodes = computed(() => {
  const out = []

  // Nested episodes inside tv_show items
  for (const item of data.value) {
    if (item.media_type !== 'tv_show' || !item.episodes?.length) continue
    for (let i = 0; i < item.episodes.length; i++) {
      const ep = item.episodes[i]
      out.push({
        show: item.title,
        showLink: `/media/${item.slug}`,
        isTopLevel: false,
        title: ep.title,
        season: ep.season,
        episode_number: ep.episode_number,
        year: ep.year,
        deaths: (ep.deaths || []).length,
        slug: item.slug,
        epIndex: i,
        detectives: (ep.persons || []).filter(p => p.role_in_story === 'detective').map(p => p.name),
      })
    }
  }

  // Standalone tv_episode items (e.g. Monk episodes stored individually)
  for (const item of data.value) {
    if (item.media_type !== 'tv_episode') continue
    let season = null, episode_number = null
    if (item.series_number != null) {
      const snInt = Math.round(item.series_number * 100)
      season = Math.floor(snInt / 100)
      episode_number = snInt % 100
    }
    out.push({
      show: item.series_name || item.title,
      showLink: null,
      isTopLevel: true,
      title: item.title,
      season,
      episode_number,
      year: item.year,
      deaths: (item.deaths || []).length,
      slug: item.slug,
      epIndex: null,
      detectives: (item.persons || []).filter(p => p.role_in_story === 'detective').map(p => p.name),
    })
  }

  return out
})

const shows = computed(() => [...new Set(episodes.value.map((e) => e.show))].sort())

onMounted(() => {
  if (route.query.show && shows.value.includes(route.query.show)) {
    showFilter.value = route.query.show
  }
})

function sortValue(ep, f) {
  if (f === 'season') return ep.season ?? 9999
  if (f === 'episode') return ep.episode_number ?? 9999
  if (f === 'year') return ep.year ?? 0
  if (f === 'deaths') return ep.deaths
  if (f === 'show') return ep.show.toLowerCase()
  if (f === 'title') return ep.title.toLowerCase()
  return 0
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const show = showFilter.value
  const dir = sortDir.value === 'desc' ? -1 : 1

  return episodes.value
    .filter((ep) => {
      if (show && ep.show !== show) return false
      if (q && !`${ep.title} ${ep.show}`.toLowerCase().includes(q)) return false
      return true
    })
    .sort((a, b) => {
      const av = sortValue(a, sortField.value)
      const bv = sortValue(b, sortField.value)
      let r = typeof av === 'number' ? av - bv : String(av).localeCompare(String(bv), undefined, { sensitivity: 'base', numeric: true })
      if (r === 0) r = a.show.localeCompare(b.show)
      if (r === 0) r = (a.season ?? 0) - (b.season ?? 0)
      if (r === 0) r = (a.episode_number ?? 0) - (b.episode_number ?? 0)
      return r * dir
    })
})

function setSort(f) {
  if (sortField.value === f) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortField.value = f; sortDir.value = 'asc' }
}
function sortState(f) { return sortField.value === f ? sortDir.value : null }
</script>

<template>
  <div>
    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search title, show…" />
      <select v-model="showFilter">
        <option value="">All shows</option>
        <option v-for="s in shows" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="sortField">
        <option value="show">Sort: Show</option>
        <option value="season">Sort: Season</option>
        <option value="episode">Sort: Episode</option>
        <option value="year">Sort: Year</option>
        <option value="deaths">Sort: Deaths</option>
        <option value="title">Sort: Title</option>
      </select>
      <select v-model="sortDir">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
    </div>
    <div class="meta-row">{{ rows.length }} episode{{ rows.length === 1 ? '' : 's' }}</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th :data-sort-state="sortState('show')" class="sortable" @click="setSort('show')">Show</th>
            <th :data-sort-state="sortState('season')" class="sortable" @click="setSort('season')">S</th>
            <th :data-sort-state="sortState('episode')" class="sortable" @click="setSort('episode')">Ep</th>
            <th :data-sort-state="sortState('title')" class="sortable" @click="setSort('title')">Title</th>
            <th :data-sort-state="sortState('year')" class="sortable" @click="setSort('year')">Year</th>
            <th :data-sort-state="sortState('deaths')" class="sortable" @click="setSort('deaths')">Deaths</th>
            <th>Detectives</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length"><td colspan="7" class="muted">No matches.</td></tr>
          <tr v-for="ep in rows" :key="`${ep.slug}-${ep.epIndex ?? 'top'}`">
            <td>
              <RouterLink v-if="ep.showLink" :to="ep.showLink">{{ ep.show }}</RouterLink>
              <RouterLink v-else :to="{ path: '/episodes', query: { show: ep.show } }">{{ ep.show }}</RouterLink>
            </td>
            <td>{{ ep.season ?? '—' }}</td>
            <td>{{ ep.episode_number ?? '—' }}</td>
            <td>
              <RouterLink v-if="ep.isTopLevel" :to="`/media/${ep.slug}`">{{ ep.title }}</RouterLink>
              <RouterLink v-else :to="{ path: `/media/${ep.slug}`, query: { ep: ep.epIndex } }">{{ ep.title }}</RouterLink>
            </td>
            <td>{{ ep.year ?? '—' }}</td>
            <td>{{ ep.deaths }}</td>
            <td class="sensitive">{{ ep.detectives.join(', ') || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
