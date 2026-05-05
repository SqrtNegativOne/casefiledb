<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData, deathCount } from '../composables/useData.js'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const { data, ensureLoaded } = useData()
onMounted(ensureLoaded)

const search = ref('')
const seriesFilter = ref('')
const sortField = ref('title')
const sortDir = ref('asc')
const expanded = ref(new Set())

const books = computed(() =>
  data.value.filter((m) => m.media_type === 'book')
)

const series = computed(() =>
  [...new Set(books.value.map((b) => b.series_name).filter(Boolean))].sort()
)

function sortValue(b, f) {
  if (f === 'deaths') return deathCount(b)
  if (f === 'year') return Number(b.year || 0)
  if (f === 'series_number') return Number(b.series_number || 0)
  return String(b[f] || '').toLowerCase()
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const ser = seriesFilter.value
  const dir = sortDir.value === 'desc' ? -1 : 1
  return books.value
    .filter((b) => {
      if (ser && b.series_name !== ser) return false
      if (q && !`${b.title} ${b.creator || ''} ${b.series_name || ''}`.toLowerCase().includes(q)) return false
      return true
    })
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
      <input v-model="search" type="text" placeholder="Search books…" />
      <select v-model="seriesFilter">
        <option value="">All series</option>
        <option v-for="s in series" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="sortField">
        <option value="title">Sort: Title</option>
        <option value="creator">Sort: Author</option>
        <option value="year">Sort: Year</option>
        <option value="series_name">Sort: Series</option>
        <option value="series_number">Sort: Series #</option>
        <option value="deaths">Sort: Deaths</option>
      </select>
      <select v-model="sortDir">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
    </div>
    <div class="meta-row">{{ rows.length }} book{{ rows.length === 1 ? '' : 's' }}</div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th :data-sort-state="sortState('title')" class="sortable" @click="setSort('title')">Title</th>
            <th :data-sort-state="sortState('creator')" class="sortable" @click="setSort('creator')">Author</th>
            <th :data-sort-state="sortState('year')" class="sortable" @click="setSort('year')">Year</th>
            <th :data-sort-state="sortState('series_name')" class="sortable" @click="setSort('series_name')">Series</th>
            <th :data-sort-state="sortState('deaths')" class="sortable" @click="setSort('deaths')">Deaths</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length"><td colspan="6" class="muted">No books found.</td></tr>
          <template v-for="b in rows" :key="b.slug">
            <tr>
              <td>
                <RouterLink :to="`/media/${b.slug}`">{{ b.title }}</RouterLink>
                <div class="mono">{{ b.slug }}</div>
              </td>
              <td>
                <RouterLink :to="{ path: '/authors' }" style="color:var(--muted)">{{ b.creator || '—' }}</RouterLink>
              </td>
              <td>{{ b.year || '—' }}</td>
              <td>
                <span v-if="b.series_name">
                  {{ b.series_name }}
                  <span v-if="b.series_number != null" class="muted"> #{{ b.series_number }}</span>
                </span>
                <span v-else class="muted">—</span>
              </td>
              <td>{{ deathCount(b) }}</td>
              <td>
                <button type="button" class="btn-primary btn" @click="toggleExpand(b.slug)">
                  {{ expanded.has(b.slug) ? 'Hide' : 'Details' }}
                </button>
              </td>
            </tr>
            <tr v-if="expanded.has(b.slug)" class="details-row">
              <td colspan="6">
                <BookDetail :book="b" />
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
import { deathCount } from '../composables/useData.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const BookDetail = defineComponent({
  name: 'BookDetail',
  components: { NoteHover, CauseBadge },
  props: { book: Object },
  setup(props) {
    const coverUrl = useCoverImage(toRef(props, 'book'))
    return { coverUrl, deathCount }
  },
  template: `
    <div class="details-grid">
      <div v-if="coverUrl" class="cover-img-wrap">
        <img :src="coverUrl" :alt="book.title + ' cover'" loading="lazy" @error="$event.target.style.display='none'" />
      </div>
      <div>
        <template v-if="book.isbn">
          <strong>ISBN:</strong> <span class="mono">{{ book.isbn }}</span><br/>
        </template>
        <template v-if="book.wikidata_id">
          <strong>Wikidata:</strong>
          <a :href="'https://www.wikidata.org/wiki/' + book.wikidata_id" target="_blank" rel="noopener noreferrer" class="mono">{{ book.wikidata_id }}</a>
        </template>
      </div>
      <div v-if="book.persons?.length">
        <strong>Persons</strong>
        <table class="mini-table">
          <thead><tr><th>Name</th><th>Role</th><th>Solver?</th><th>Notes</th></tr></thead>
          <tbody>
            <tr v-for="p in book.persons" :key="p.name">
              <td class="sensitive">{{ p.name }}</td>
              <td>{{ p.role_in_story || '—' }}</td>
              <td>{{ p.is_solver ? '✓' : '' }}</td>
              <td><NoteHover :text="p.notes" /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="book.deaths?.length">
        <strong>Deaths</strong>
        <table class="mini-table">
          <thead><tr><th>#</th><th>Victim</th><th>Cause</th><th>Killer</th><th>Type</th><th>Twist</th><th>Notes</th></tr></thead>
          <tbody>
            <tr v-for="(d, i) in book.deaths" :key="i">
              <td>{{ d.ordinal || '—' }}</td>
              <td class="sensitive">{{ d.victim_name || 'Unknown' }}</td>
              <td><CauseBadge :cause="d.cause" :subtype="d.cause_subtype" /></td>
              <td class="sensitive">{{ d.killers?.map(k => k.name).join(', ') || 'Unknown' }}</td>
              <td>{{ d.death_type || '—' }}</td>
              <td>{{ d.is_twist ? 'Yes' : 'No' }}</td>
              <td><NoteHover :text="d.notes || d.cause_detail || d.motive_detail" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
})
</script>
