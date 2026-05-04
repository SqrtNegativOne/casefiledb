<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData, deathCount } from '../composables/useData.js'

const { data, ensureLoaded } = useData()
onMounted(ensureLoaded)

const search = ref('')
const sortField = ref('name')
const sortDir = ref('asc')

const authors = computed(() => {
  const map = new Map()
  for (const item of data.value) {
    const creator = item.creator || 'Unknown'
    if (!map.has(creator)) {
      map.set(creator, { name: creator, works: [], totalDeaths: 0, types: new Set() })
    }
    const e = map.get(creator)
    e.works.push(item)
    e.totalDeaths += deathCount(item)
    if (item.media_type) e.types.add(item.media_type)
  }
  return [...map.values()]
})

function sortValue(a, f) {
  if (f === 'works') return a.works.length
  if (f === 'deaths') return a.totalDeaths
  return a.name.toLowerCase()
}

const rows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const dir = sortDir.value === 'desc' ? -1 : 1

  return authors.value
    .filter((a) => !q || a.name.toLowerCase().includes(q))
    .sort((a, b) => {
      const av = sortValue(a, sortField.value)
      const bv = sortValue(b, sortField.value)
      let r = typeof av === 'number' ? av - bv : String(av).localeCompare(String(bv), undefined, { sensitivity: 'base' })
      if (r === 0) r = a.name.localeCompare(b.name)
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
      <input v-model="search" type="text" placeholder="Search author…" />
      <select v-model="sortField">
        <option value="name">Sort: Name</option>
        <option value="works">Sort: Works</option>
        <option value="deaths">Sort: Deaths</option>
      </select>
      <select v-model="sortDir">
        <option value="asc">Asc</option>
        <option value="desc">Desc</option>
      </select>
    </div>
    <div class="meta-row">{{ rows.length }} author{{ rows.length === 1 ? '' : 's' }}</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th :data-sort-state="sortState('name')" class="sortable" @click="setSort('name')">Author / Creator</th>
            <th :data-sort-state="sortState('works')" class="sortable" @click="setSort('works')">Works</th>
            <th :data-sort-state="sortState('deaths')" class="sortable" @click="setSort('deaths')">Total deaths</th>
            <th>Media types</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length"><td colspan="4" class="muted">No matches.</td></tr>
          <tr v-for="a in rows" :key="a.name">
            <td>
              <RouterLink :to="{ path: '/', query: { creator: a.name } }">{{ a.name }}</RouterLink>
            </td>
            <td>{{ a.works.length }}</td>
            <td>{{ a.totalDeaths }}</td>
            <td><span class="muted">{{ [...a.types].sort().join(', ') }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
