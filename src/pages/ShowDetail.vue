<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useData } from '../composables/useData.js'
import { entriesFromMedia } from '../composables/useStatistics.js'
import StatisticsPanel from '../components/StatisticsPanel.vue'
import { canReveal, showKey, completed } from '../composables/useCompletion.js'

const { data, ensureLoaded, loaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

const showName = computed(() => decodeURIComponent(String(route.params.name || '')))

/**
 * A "show" is either:
 *   - a tv_show item (has its own slug + nested episodes), or
 *   - a virtual grouping of standalone tv_episode items sharing a series_name.
 * Both feed StatisticsPanel via entriesFromMedia.
 */
const directShow = computed(() =>
  (data.value.tv_shows || []).find((s) => s.title === showName.value) || null
)

const episodes = computed(() => {
  if (directShow.value) return directShow.value.episodes || []
  return (data.value.tv_episodes || [])
    .filter((ep) => (ep.series_name || ep.title) === showName.value)
    .slice()
    .sort((a, b) => (Number(a.series_number) || 0) - (Number(b.series_number) || 0))
})

const entries = computed(() => {
  if (directShow.value) return entriesFromMedia([directShow.value])
  return entriesFromMedia(episodes.value)
})

function epLink(ep) {
  // Standalone tv_episode → /media/:slug. Nested episode → media/show?ep=index.
  if (directShow.value) return null
  return `/media/${ep.slug}`
}

function epLabel(ep) {
  if (ep.season != null && ep.episode_number != null) return `S${ep.season}E${ep.episode_number}`
  if (ep.series_number != null) {
    const sn = Math.round(ep.series_number * 100)
    const s = Math.floor(sn / 100)
    const e = sn % 100
    if (s && e) return `S${s}E${e}`
  }
  return ''
}

// A show is "revealed" if it (or its author) is in the completed set or Mnesia is on.
// We build a synthetic media-like object so canReveal() can do its checks.
const showRevealed = computed(() => {
  if (!showName.value) return false
  // Mnesia handled inside canReveal; pass a synthetic object.
  const synth = {
    slug: `show:${showName.value}`,
    media_type: 'tv_show',
    title: showName.value,
    creator: directShow.value?.creator,
  }
  // canReveal checks slug (won't match), then creator, then for tv_show it checks showKey(title).
  // Also check the showKey directly since canReveal only does that for tv_show media_type.
  return canReveal({ ...synth, slug: directShow.value?.slug || '' }) ||
    completed.value.has(showKey(showName.value))
})

const detectives = computed(() => {
  const set = new Set()
  for (const ep of episodes.value) {
    for (const p of (ep.persons || [])) {
      if (p.role_in_story === 'detective') set.add(p.name)
    }
  }
  return [...set]
})
</script>

<template>
  <div v-if="!loaded" class="muted">Loading…</div>
  <template v-else>
    <nav class="breadcrumb">
      <RouterLink to="/media">Media</RouterLink> / Shows / {{ showName }}
    </nav>

    <div class="media-header">
      <h2>{{ showName }}</h2>
      <div class="media-meta">
        <span>{{ episodes.length }} episode{{ episodes.length === 1 ? '' : 's' }}</span>
        <span class="badge badge-tv_show">show</span>
      </div>
      <div v-if="detectives.length" class="muted" style="margin-top:0.4rem">
        Featured detectives:
        <span class="sensitive">{{ detectives.join(', ') }}</span>
      </div>
    </div>

    <p v-if="!episodes.length" class="muted">No episodes recorded for this show.</p>

    <template v-else>
      <StatisticsPanel :entries="entries" :title="`${showName} — death statistics`" />

      <h3>Episodes</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>S/E</th><th>Title</th><th>Year</th><th v-if="showRevealed">Deaths</th></tr>
          </thead>
          <tbody>
            <tr v-for="(ep, i) in episodes" :key="ep.slug || i">
              <td class="mono">{{ epLabel(ep) }}</td>
              <td>
                <RouterLink v-if="epLink(ep)" :to="epLink(ep)">{{ ep.title }}</RouterLink>
                <span v-else>{{ ep.title }}</span>
              </td>
              <td>{{ ep.year || '—' }}</td>
              <td v-if="showRevealed">{{ (ep.deaths || []).length }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </template>
</template>
