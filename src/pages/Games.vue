<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData } from '../composables/useData.js'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const { data, ensureLoaded } = useData()
onMounted(ensureLoaded)

const search = ref('')
const sortField = ref('title')
const sortDir = ref('asc')
const expanded = ref(new Set())

const games = computed(() =>
  data.value.filter((m) => m.media_type === 'game')
)

function totalDeaths(g) {
  return (g.cases || []).reduce((n, c) => n + (c.deaths || []).length, 0) + (g.deaths || []).length
}

function sortValue(g, f) {
  if (f === 'deaths') return totalDeaths(g)
  if (f === 'cases') return (g.cases || []).length
  if (f === 'year') return Number(g.year || 0)
  return String(g[f] || '').toLowerCase()
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const dir = sortDir.value === 'desc' ? -1 : 1
  return games.value
    .filter((g) => !q || `${g.title} ${g.creator || ''}`.toLowerCase().includes(q))
    .sort((a, b) => {
      const av = sortValue(a, sortField.value), bv = sortValue(b, sortField.value)
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

function toggleExpand(slug) {
  const s = new Set(expanded.value)
  s.has(slug) ? s.delete(slug) : s.add(slug)
  expanded.value = s
}
</script>

<template>
  <div>
    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search games…" />
      <select v-model="sortField">
        <option value="title">Sort: Title</option>
        <option value="creator">Sort: Developer</option>
        <option value="year">Sort: Year</option>
        <option value="cases">Sort: Cases</option>
        <option value="deaths">Sort: Deaths</option>
      </select>
      <select v-model="sortDir">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
    </div>
    <div class="meta-row">{{ rows.length }} game{{ rows.length === 1 ? '' : 's' }}</div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th :data-sort-state="sortState('title')" class="sortable" @click="setSort('title')">Title</th>
            <th :data-sort-state="sortState('creator')" class="sortable" @click="setSort('creator')">Developer</th>
            <th :data-sort-state="sortState('year')" class="sortable" @click="setSort('year')">Year</th>
            <th :data-sort-state="sortState('cases')" class="sortable" @click="setSort('cases')">Cases</th>
            <th :data-sort-state="sortState('deaths')" class="sortable" @click="setSort('deaths')">Deaths</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length"><td colspan="6" class="muted">No games found.</td></tr>
          <template v-for="g in rows" :key="g.slug">
            <tr>
              <td>
                <RouterLink :to="`/media/${g.slug}`">{{ g.title }}</RouterLink>
                <div class="mono">{{ g.slug }}</div>
              </td>
              <td>{{ g.creator || '—' }}</td>
              <td>{{ g.year || '—' }}</td>
              <td>{{ (g.cases || []).length }}</td>
              <td>{{ totalDeaths(g) }}</td>
              <td>
                <button type="button" class="btn-primary btn" @click="toggleExpand(g.slug)">
                  {{ expanded.has(g.slug) ? 'Hide' : 'Cases' }}
                </button>
              </td>
            </tr>
            <tr v-if="expanded.has(g.slug)" class="details-row">
              <td colspan="6">
                <GameDetail :game="g" />
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { defineComponent, toRef } from 'vue'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const GameDetail = defineComponent({
  name: 'GameDetail',
  components: { NoteHover, CauseBadge },
  props: { game: Object },
  setup(props) {
    const coverUrl = useCoverImage(toRef(props, 'game'))
    return { coverUrl }
  },
  template: `
    <div class="details-grid">
      <div v-if="coverUrl" class="cover-img-wrap">
        <img :src="coverUrl" :alt="game.title" loading="lazy" @error="$event.target.style.display='none'" />
      </div>
      <div v-if="!game.cases?.length" class="muted">No cases recorded.</div>
      <template v-else>
        <div v-for="(c, idx) in game.cases" :key="idx" style="margin-bottom:1rem">
          <strong>Case {{ c.case_number ?? idx + 1 }}: {{ c.title }}</strong>
          <span class="muted" style="margin-left:0.5rem;font-size:0.85rem">{{ (c.deaths || []).length }} death{{ (c.deaths||[]).length===1?'':'s' }}</span>
          <table v-if="c.deaths?.length" class="mini-table" style="margin-top:0.4rem">
            <thead><tr><th>Victim</th><th>Cause</th><th>Killer</th><th>Type</th><th>Notes</th></tr></thead>
            <tbody>
              <tr v-for="(d, di) in c.deaths" :key="di">
                <td class="sensitive">{{ d.victim_name || 'Unknown' }}</td>
                <td><CauseBadge :cause="d.cause" :subtype="d.cause_subtype" /></td>
                <td class="sensitive">{{ d.killer_name || 'Unknown' }}</td>
                <td>{{ d.death_type || '—' }}</td>
                <td><NoteHover :text="d.notes || d.cause_detail" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  `,
})
</script>
