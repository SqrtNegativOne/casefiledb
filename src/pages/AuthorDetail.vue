<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useData, allItems, deathCount } from '../composables/useData.js'
import { entriesFromMedia } from '../composables/useStatistics.js'
import StatisticsPanel from '../components/StatisticsPanel.vue'
import { canReveal } from '../composables/useCompletion.js'

const { ensureLoaded, loaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

const name = computed(() => decodeURIComponent(String(route.params.name || '')))

const works = computed(() =>
  allItems.value
    .filter((m) => (m.creator || '').trim() === name.value.trim())
    .slice()
    .sort((a, b) => (a.year ?? 0) - (b.year ?? 0) || String(a.title).localeCompare(b.title))
)

const entries = computed(() => entriesFromMedia(works.value))

const mediaTypes = computed(() => {
  const set = new Set()
  for (const w of works.value) if (w.media_type) set.add(w.media_type)
  return [...set]
})

const yearRange = computed(() => {
  const ys = works.value.map((w) => w.year).filter(Boolean)
  if (!ys.length) return null
  const min = Math.min(...ys), max = Math.max(...ys)
  return min === max ? String(min) : `${min}–${max}`
})
</script>

<template>
  <div v-if="!loaded" class="muted">Loading…</div>
  <template v-else>
    <nav class="breadcrumb">
      <RouterLink to="/media">Media</RouterLink> / Authors / {{ name }}
    </nav>

    <div class="media-header">
      <h2>{{ name }}</h2>
      <div class="media-meta">
        <span>{{ works.length }} work{{ works.length === 1 ? '' : 's' }}</span>
        <span v-if="yearRange">· {{ yearRange }}</span>
        <span v-for="t in mediaTypes" :key="t" :class="['badge', `badge-${t}`]">{{ t }}</span>
      </div>
    </div>

    <p v-if="!works.length" class="muted">No works recorded for this creator.</p>

    <template v-else>
      <StatisticsPanel :entries="entries" :title="`${name} — death statistics`" />

      <h3>Works</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Title</th><th>Type</th><th>Year</th><th>Series</th><th>Deaths</th></tr>
          </thead>
          <tbody>
            <tr v-for="w in works" :key="w.slug">
              <td>
                <RouterLink :to="`/media/${w.slug}`">{{ w.title }}</RouterLink>
              </td>
              <td>
                <span :class="['badge', `badge-${w.media_type}`]">{{ w.media_type }}</span>
              </td>
              <td>{{ w.year || '—' }}</td>
              <td>
                <span v-if="w.series_name">
                  {{ w.series_name }}
                  <span v-if="w.series_number != null" class="muted"> #{{ w.series_number }}</span>
                </span>
                <span v-else class="muted">—</span>
              </td>
              <td>
                <span v-if="canReveal(w)">{{ deathCount(w) }}</span>
                <span v-else class="muted" title="Mark this work as completed to reveal">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </template>
</template>
