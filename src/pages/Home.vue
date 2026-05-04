<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useData, deathCount, hasTwist } from '../composables/useData.js'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const { data, ensureLoaded } = useData()
const route = useRoute()
const router = useRouter()

const search = ref('')
const typeFilter = ref('')
const deathsFilter = ref('')
const twistFilter = ref(false)
const sortField = ref('title')
const sortDir = ref('asc')
const expanded = ref(new Set())

// Pre-fill from ?creator= query param
onMounted(async () => {
  await ensureLoaded()
  if (route.query.creator) {
    search.value = route.query.creator
  }
})

const types = computed(() =>
  [...new Set(data.value.map((m) => m.media_type).filter(Boolean))].sort()
)

function sortValue(media, field) {
  if (field === 'deaths') return deathCount(media)
  if (field === 'year') return Number(media.year || 0)
  return String(media[field] || '').toLowerCase()
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const type = typeFilter.value
  const minDeaths = deathsFilter.value
  const onlyTwist = twistFilter.value
  const dir = sortDir.value === 'desc' ? -1 : 1

  const filtered = data.value.filter((m) => {
    const tags = (m.tags || []).join(' ')
    const hay = `${m.title||''} ${m.creator||''} ${m.media_type||''} ${m.wikidata_id||''} ${tags}`.toLowerCase()
    if (q && !hay.includes(q)) return false
    if (type && m.media_type !== type) return false
    const dc = deathCount(m)
    if (minDeaths === '0' && dc !== 0) return false
    if (minDeaths === '1' && dc < 1) return false
    if (minDeaths === '2' && dc < 2) return false
    if (onlyTwist && !hasTwist(m)) return false
    return true
  })

  filtered.sort((a, b) => {
    const av = sortValue(a, sortField.value)
    const bv = sortValue(b, sortField.value)
    let r = typeof av === 'number' && typeof bv === 'number'
      ? av - bv
      : String(av).localeCompare(String(bv), undefined, { sensitivity: 'base', numeric: true })
    if (r === 0) r = String(a.title || '').localeCompare(String(b.title || ''))
    return r * dir
  })

  return filtered
})

function setSort(field) {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDir.value = 'asc'
  }
}

function sortState(field) {
  if (sortField.value !== field) return null
  return sortDir.value
}

function toggleExpand(slug) {
  const s = new Set(expanded.value)
  if (s.has(slug)) s.delete(slug)
  else s.add(slug)
  expanded.value = s
}

// Per-row cover image: only fetch when expanded
const expandedMediaRef = ref(null)
const coverUrl = useCoverImage(expandedMediaRef)
watch(expanded, (s) => {
  // No-op; individual rows handle their own cover via ExpandedRow
})

function allPersons(media) {
  return media.persons || []
}

function allDeathsForMedia(media) {
  return media.deaths || []
}

// Episodes/cases scoped deaths shown in detail
function scopedDeaths(media) {
  const eps = (media.episodes || []).flatMap((e, ei) =>
    (e.deaths || []).map((d) => ({ ...d, _scope: e.title, _scopeIdx: ei, _kind: 'ep' }))
  )
  const cs = (media.cases || []).flatMap((c, ci) =>
    (c.deaths || []).map((d) => ({ ...d, _scope: c.title, _scopeIdx: ci, _kind: 'case' }))
  )
  return [...(media.deaths || []), ...eps, ...cs]
}

function scopedPersons(media) {
  const eps = (media.episodes || []).flatMap((e) => e.persons || [])
  const cs = (media.cases || []).flatMap((c) => c.persons || [])
  return [...(media.persons || []), ...eps, ...cs]
}
</script>

<template>
  <div>
    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search title, creator, type…" />
      <select v-model="typeFilter" aria-label="Filter by type">
        <option value="">All types</option>
        <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="deathsFilter" aria-label="Filter by deaths">
        <option value="">Any deaths</option>
        <option value="0">No deaths</option>
        <option value="1">1+ deaths</option>
        <option value="2">2+ deaths</option>
      </select>
      <label class="checkbox-filter">
        <input type="checkbox" v-model="twistFilter" /> Has twist
      </label>
      <select v-model="sortField" aria-label="Sort field">
        <option value="title">Sort: Title</option>
        <option value="creator">Sort: Creator</option>
        <option value="year">Sort: Year</option>
        <option value="media_type">Sort: Type</option>
        <option value="deaths">Sort: Deaths</option>
      </select>
      <select v-model="sortDir" aria-label="Sort direction">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
    </div>

    <div class="meta-row">{{ rows.length }} result{{ rows.length === 1 ? '' : 's' }}</div>

    <div class="table-wrap">
      <table aria-label="Casefile media table">
        <thead>
          <tr>
            <th :data-sort-state="sortState('title')" class="sortable" @click="setSort('title')">Title</th>
            <th :data-sort-state="sortState('creator')" class="sortable" @click="setSort('creator')">Creator</th>
            <th :data-sort-state="sortState('year')" class="sortable" @click="setSort('year')">Year</th>
            <th :data-sort-state="sortState('media_type')" class="sortable" @click="setSort('media_type')">Type</th>
            <th :data-sort-state="sortState('deaths')" class="sortable" @click="setSort('deaths')">Deaths</th>
            <th>Notes</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-if="!rows.length">
            <tr><td colspan="7" class="muted">No matches.</td></tr>
          </template>
          <template v-for="media in rows" :key="media.slug">
            <tr>
              <td>
                <RouterLink :to="`/media/${media.slug}`">{{ media.title || media.slug }}</RouterLink>
                <div class="mono">{{ media.slug }}</div>
              </td>
              <td>{{ media.creator || '—' }}</td>
              <td>{{ media.year || '—' }}</td>
              <td><span :class="['badge', `badge-${media.media_type}`]">{{ media.media_type || '—' }}</span></td>
              <td>{{ deathCount(media) }}</td>
              <td><NoteHover :text="media.notes" /></td>
              <td>
                <button type="button" class="btn-primary btn" @click="toggleExpand(media.slug)">
                  {{ expanded.has(media.slug) ? 'Hide' : 'Details' }}
                </button>
              </td>
            </tr>
            <tr v-if="expanded.has(media.slug)" class="details-row">
              <td colspan="7">
                <ExpandedDetail :media="media" />
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
// Sub-component for the expanded detail row to isolate image loading per row
import { defineComponent, toRef, computed } from 'vue'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const ExpandedDetail = defineComponent({
  name: 'ExpandedDetail',
  components: { NoteHover, CauseBadge },
  props: { media: Object },
  setup(props) {
    const mediaRef = toRef(props, 'media')
    const coverUrl = useCoverImage(mediaRef)

    const persons = computed(() => {
      const eps = (props.media.episodes || []).flatMap((e) => e.persons || [])
      const cs = (props.media.cases || []).flatMap((c) => c.persons || [])
      return [...(props.media.persons || []), ...eps, ...cs]
    })

    const deaths = computed(() => {
      const direct = (props.media.deaths || []).map((d) => ({ ...d, _scope: null }))
      const eps = (props.media.episodes || []).flatMap((e) =>
        (e.deaths || []).map((d) => ({ ...d, _scope: e.title }))
      )
      const cs = (props.media.cases || []).flatMap((c) =>
        (c.deaths || []).map((d) => ({ ...d, _scope: c.title }))
      )
      return [...direct, ...eps, ...cs]
    })

    return { coverUrl, persons, deaths }
  },
  template: `
    <div class="details-grid">
      <div v-if="coverUrl" class="cover-img-wrap">
        <img :src="coverUrl" :alt="media.title + ' cover'" loading="lazy" @error="$event.target.style.display='none'" />
      </div>
      <div>
        <template v-if="media.wikidata_id">
          <strong>Wikidata:</strong>
          <a :href="'https://www.wikidata.org/wiki/' + media.wikidata_id" target="_blank" rel="noopener noreferrer" class="mono">{{ media.wikidata_id }}</a>
        </template>
        <template v-else>
          <strong>Wikidata:</strong> <span class="muted">none</span>
        </template>
      </div>
      <div>
        <strong>Persons</strong>
        <table class="mini-table">
          <thead><tr><th>Name</th><th>Role</th><th>Solver?</th><th>Notes</th></tr></thead>
          <tbody>
            <tr v-if="!persons.length"><td colspan="4" class="muted">No persons</td></tr>
            <tr v-for="p in persons" :key="p.name">
              <td class="sensitive">{{ p.name }}</td>
              <td>{{ p.role_in_story || '—' }}</td>
              <td>{{ p.is_solver ? '✓' : '' }}</td>
              <td><NoteHover :text="p.notes" /></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div>
        <strong>Deaths</strong>
        <table class="mini-table">
          <thead><tr><th>#</th><th>Victim</th><th>Cause</th><th>Killer</th><th>Type</th><th>Twist</th><th>Notes</th></tr></thead>
          <tbody>
            <tr v-if="!deaths.length"><td colspan="7" class="muted">No deaths</td></tr>
            <tr v-for="(d, i) in deaths" :key="i">
              <td>{{ d.ordinal || '—' }}<span v-if="d._scope" class="muted" style="display:block;font-size:0.75rem">{{ d._scope }}</span></td>
              <td class="sensitive">{{ d.victim_name || 'Unknown' }}</td>
              <td><CauseBadge :cause="d.cause" :subtype="d.cause_subtype" /></td>
              <td class="sensitive">{{ d.killer_name || 'Unknown' }}</td>
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
