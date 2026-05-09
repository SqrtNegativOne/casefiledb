<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData, allItems, resolveName } from '../composables/useData.js'
import { canReveal, mnesia, completed } from '../composables/useCompletion.js'
import CauseBadge from '../components/CauseBadge.vue'

const { ensureLoaded } = useData()
onMounted(ensureLoaded)

const revealedItems = computed(() => allItems.value.filter(canReveal))

const search = ref('')
const causeFilter = ref('')
const typeFilter = ref('')
const deathTypeFilter = ref('')
const twistFilter = ref(false)
const sortField = ref('media')
const sortDir = ref('asc')
const showFilters = ref(false)

const hasActiveFilters = computed(() =>
  causeFilter.value || typeFilter.value || deathTypeFilter.value || twistFilter.value || sortField.value !== 'media' || sortDir.value !== 'asc'
)

const allDeathRows = computed(() => {
  const out = []
  for (const item of revealedItems.value) {
    for (const d of (item.deaths || [])) {
      out.push({ death: d, media: item, scope: null, persons: item.persons || [] })
    }
    for (const ep of (item.episodes || [])) {
      for (const d of (ep.deaths || [])) {
        out.push({ death: d, media: item, scope: ep.title, persons: ep.persons || [] })
      }
    }
    for (const c of (item.cases || [])) {
      for (const d of (c.deaths || [])) {
        out.push({ death: d, media: item, scope: c.title, persons: c.persons || [] })
      }
    }
  }
  return out
})

const causes = computed(() =>
  [...new Set(allDeathRows.value.map(r => r.death.cause).filter(Boolean))].sort()
)
const deathTypes = computed(() =>
  [...new Set(allDeathRows.value.map(r => r.death.death_type).filter(Boolean))].sort()
)
const mediaTypes = computed(() =>
  [...new Set(allItems.value.map(m => m.media_type).filter(Boolean))].sort()
)

function motiveLabel(m) {
  return m ? m.replace(/_/g, ' ') : '—'
}

function sortValue(row, field) {
  const { death, media } = row
  if (field === 'victim') return (resolveName(row.persons, death.victim_id) || '').toLowerCase()
  if (field === 'cause') return death.cause || ''
  if (field === 'killer') return (resolveName(row.persons, death.killers?.[0]?.person_id) || '').toLowerCase()
  if (field === 'motive') return death.motive || ''
  if (field === 'death_type') return death.death_type || ''
  if (field === 'year') return media.year || 0
  return (media.title || '').toLowerCase()
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const cause = causeFilter.value
  const type = typeFilter.value
  const dtype = deathTypeFilter.value
  const twist = twistFilter.value
  const dir = sortDir.value === 'desc' ? -1 : 1

  return allDeathRows.value
    .filter(row => {
      const { death, media } = row
      if (cause && death.cause !== cause) return false
      if (type && media.media_type !== type) return false
      if (dtype && death.death_type !== dtype) return false
      if (twist && !death.is_twist) return false
      if (q) {
        const hay = [
          resolveName(row.persons, death.victim_id),
          ...(death.killers || []).map(k => resolveName(row.persons, k.person_id)),
          media.title,
          death.motive,
        ].filter(Boolean).join(' ').toLowerCase()
        if (!hay.includes(q)) return false
      }
      return true
    })
    .sort((a, b) => {
      const av = sortValue(a, sortField.value)
      const bv = sortValue(b, sortField.value)
      let r = typeof av === 'number' && typeof bv === 'number'
        ? av - bv
        : String(av).localeCompare(String(bv), undefined, { sensitivity: 'base', numeric: true })
      if (r === 0) r = (a.media.title || '').localeCompare(b.media.title || '')
      return r * dir
    })
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
</script>

<template>
  <div>
    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search victim, killer, media…" />
      <button type="button" :class="['filter-toggle-btn', { 'filter-toggle-btn-active': showFilters || hasActiveFilters }]" @click="showFilters = !showFilters">
        Filter &amp; Sort{{ hasActiveFilters ? ' ·' : '' }}
      </button>
    </div>

    <div v-show="showFilters" class="filter-panel">
      <select v-model="causeFilter" aria-label="Filter by cause">
        <option value="">All causes</option>
        <option v-for="c in causes" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="deathTypeFilter" aria-label="Filter by death type">
        <option value="">All death types</option>
        <option v-for="t in deathTypes" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="typeFilter" aria-label="Filter by media type">
        <option value="">All media types</option>
        <option v-for="t in mediaTypes" :key="t" :value="t">{{ t }}</option>
      </select>
      <label class="checkbox-filter">
        <input type="checkbox" v-model="twistFilter" /> Twist only
      </label>
      <select v-model="sortField" aria-label="Sort field">
        <option value="media">Sort: Media</option>
        <option value="year">Sort: Year</option>
        <option value="victim">Sort: Victim</option>
        <option value="cause">Sort: Cause</option>
        <option value="killer">Sort: Killer</option>
        <option value="motive">Sort: Motive</option>
        <option value="death_type">Sort: Death type</option>
      </select>
      <select v-model="sortDir" aria-label="Sort direction">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
    </div>

    <div v-if="!revealedItems.length" class="empty-spoiler-notice">
      <p><strong>Deaths are hidden until you mark works as completed.</strong></p>
      <p class="muted">
        Casefile Database catalogues mystery plots by their solutions. Browsing them by victim and killer would spoil
        every twist for new readers/viewers. Use <em>Mark as completed</em> in the top bar to reveal works you've
        already finished — or enable <em>Mnesia mode</em> if you don't mind spoilers.
      </p>
    </div>
    <div v-else class="meta-row">
      {{ rows.length }} death{{ rows.length === 1 ? '' : 's' }}
      <span v-if="!mnesia" class="muted"> · across {{ revealedItems.length }} completed work{{ revealedItems.length === 1 ? '' : 's' }}</span>
    </div>

    <div v-if="revealedItems.length" class="table-wrap">
      <table aria-label="Deaths table">
        <thead>
          <tr>
            <th :data-sort-state="sortState('victim')" class="sortable" @click="setSort('victim')">Victim</th>
            <th :data-sort-state="sortState('cause')" class="sortable" @click="setSort('cause')">Cause</th>
            <th :data-sort-state="sortState('killer')" class="sortable" @click="setSort('killer')">Killer(s)</th>
            <th :data-sort-state="sortState('motive')" class="sortable" @click="setSort('motive')">Motive</th>
            <th :data-sort-state="sortState('death_type')" class="sortable" @click="setSort('death_type')">Type</th>
            <th>Twist</th>
            <th :data-sort-state="sortState('media')" class="sortable" @click="setSort('media')">Media</th>
            <th :data-sort-state="sortState('year')" class="sortable" @click="setSort('year')">Year</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length"><td colspan="8" class="muted">No matches.</td></tr>
          <tr v-for="(row, i) in rows" :key="i">
            <td class="sensitive">{{ resolveName(row.persons, row.death.victim_id) || '—' }}</td>
            <td><CauseBadge :cause="row.death.cause" :means="row.death.means" /></td>
            <td class="sensitive">{{ row.death.killers?.map(k => resolveName(row.persons, k.person_id)).join(', ') || '—' }}</td>
            <td>{{ motiveLabel(row.death.motive) }}</td>
            <td>{{ row.death.death_type || '—' }}</td>
            <td>{{ row.death.is_twist ? '✓' : '' }}</td>
            <td>
              <RouterLink :to="`/media/${row.media.slug}`">{{ row.media.title }}</RouterLink>
              <span v-if="row.scope" class="muted" style="display:block;font-size:0.78rem">{{ row.scope }}</span>
              <span :class="['badge', `badge-${row.media.media_type}`]" style="display:block;font-size:0.72rem;margin-top:0.15rem">{{ row.media.media_type }}</span>
            </td>
            <td>{{ row.media.year || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
