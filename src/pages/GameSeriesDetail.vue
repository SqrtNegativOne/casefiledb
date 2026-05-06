<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useData, deathCount } from '../composables/useData.js'
import { findGameSeries, gamesInSeries } from '../composables/gameSeries.js'
import { entriesFromMedia } from '../composables/useStatistics.js'
import StatisticsPanel from '../components/StatisticsPanel.vue'
import { canReveal } from '../composables/useCompletion.js'

const { data, ensureLoaded, loaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

const series = computed(() => findGameSeries(String(route.params.slug)))
const games = computed(() =>
  gamesInSeries(series.value, data.value.games || [])
    .slice()
    .sort((a, b) => (Number(a.series_number) || 0) - (Number(b.series_number) || 0))
)

const entries = computed(() => entriesFromMedia(games.value))

const totalCases = computed(() => games.value.reduce((n, g) => n + (g.cases || []).length, 0))
</script>

<template>
  <div v-if="!loaded" class="muted">Loading…</div>
  <template v-else-if="!series">
    <p class="muted">Game series not found: <code>{{ route.params.slug }}</code></p>
    <RouterLink to="/media">← Back to Media</RouterLink>
  </template>
  <template v-else>
    <nav class="breadcrumb">
      <RouterLink to="/media">Media</RouterLink> / Game series / {{ series.name }}
    </nav>

    <div class="media-header">
      <h2>{{ series.name }}</h2>
      <div class="media-meta">
        <span>{{ games.length }} game{{ games.length === 1 ? '' : 's' }}</span>
        <span>· {{ totalCases }} case{{ totalCases === 1 ? '' : 's' }}</span>
        <span class="badge badge-game">game series</span>
      </div>
      <p v-if="series.description" class="media-notes">{{ series.description }}</p>
    </div>

    <StatisticsPanel :entries="entries" :title="`${series.name} — death statistics`" />

    <h3>Games</h3>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>#</th><th>Title</th><th>Year</th><th>Cases</th><th>Deaths</th></tr>
        </thead>
        <tbody>
          <tr v-for="g in games" :key="g.slug">
            <td>{{ g.series_number != null ? g.series_number : '—' }}</td>
            <td><RouterLink :to="`/media/${g.slug}`">{{ g.title }}</RouterLink></td>
            <td>{{ g.year || '—' }}</td>
            <td>{{ (g.cases || []).length }}</td>
            <td>
              <span v-if="canReveal(g)">{{ deathCount(g) }}</span>
              <span v-else class="muted" title="Mark this game as completed to reveal">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
</template>
