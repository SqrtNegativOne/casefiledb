<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useData, allItems, deathCount } from '../composables/useData.js'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'
import StatisticsPanel from '../components/StatisticsPanel.vue'
import { entriesFromMedia, STATS_THRESHOLD } from '../composables/useStatistics.js'
import { canReveal, completed, mediaKey, addKey, removeKey } from '../composables/useCompletion.js'

const { loaded, ensureLoaded } = useData()
const route = useRoute()
const router = useRouter()

onMounted(ensureLoaded)

const media = computed(() => allItems.value.find((m) => m.slug === route.params.slug) || null)
const epIndex = computed(() => route.query.ep != null ? parseInt(route.query.ep, 10) : null)
const caseIndex = computed(() => route.query.case != null ? parseInt(route.query.case, 10) : null)

const displayItem = computed(() => {
  if (!media.value) return null
  if (epIndex.value !== null && media.value.episodes?.[epIndex.value]) {
    return { item: media.value.episodes[epIndex.value], kind: 'episode', parent: media.value }
  }
  if (caseIndex.value !== null && media.value.cases?.[caseIndex.value]) {
    return { item: media.value.cases[caseIndex.value], kind: 'case', parent: media.value }
  }
  return { item: media.value, kind: null, parent: null }
})

// Redirect if slug is actually a nested episode wikidata_id
watch(() => allItems.value.length, () => {
  if (media.value) return
  const slug = route.params.slug
  for (const item of allItems.value) {
    if (!item.episodes) continue
    const idx = item.episodes.findIndex((e) => e.wikidata_id === slug)
    if (idx !== -1) {
      router.replace({ path: `/media/${item.slug}`, query: { ep: idx } })
      return
    }
  }
}, { once: true })

const coverMediaRef = computed(() => displayItem.value?.parent || media.value)
const coverUrl = useCoverImage(coverMediaRef)

const statsEntries = computed(() => {
  // Only top-level items get an aggregate stats panel — sub-items (single
  // episode / single case) almost never clear the threshold.
  if (!displayItem.value || displayItem.value.kind || !displayItem.value.item) return []
  return entriesFromMedia([displayItem.value.item])
})
// Per-work statistics are themselves a spoiler (cause/motive distribution
// reveals plot shape), so only show them once the user has marked the work
// as completed (or enabled Mnesia mode).
const showsStats = computed(() =>
  statsEntries.value.length >= STATS_THRESHOLD && canReveal(media.value)
)

const isMediaRevealed = computed(() => canReveal(media.value))
const isMarkedDirectly = computed(() =>
  media.value ? completed.value.has(mediaKey(media.value.slug)) : false
)
function toggleSelfCompletion() {
  if (!media.value) return
  const k = mediaKey(media.value.slug)
  if (completed.value.has(k)) removeKey(k)
  else addKey(k)
}

// ── Series navigation ────────────────────────────────────────────
const seriesMates = computed(() => {
  if (!media.value?.series_name) return []
  return allItems.value
    .filter(m => m.series_name === media.value.series_name)
    .sort((a, b) => (a.series_number ?? 0) - (b.series_number ?? 0))
})

const seriesIndex = computed(() =>
  seriesMates.value.findIndex(m => m.slug === media.value?.slug)
)

const prevInSeries = computed(() =>
  seriesIndex.value > 0 ? seriesMates.value[seriesIndex.value - 1] : null
)

const nextInSeries = computed(() =>
  seriesIndex.value >= 0 && seriesIndex.value < seriesMates.value.length - 1
    ? seriesMates.value[seriesIndex.value + 1]
    : null
)

const seriesExpanded = ref(false)
watch(() => media.value?.slug, () => { seriesExpanded.value = false })

// Compact context window for large series (show neighbours around current)
const seriesContextSlice = computed(() => {
  const total = seriesMates.value.length
  const idx = seriesIndex.value
  const start = Math.max(0, idx - 2)
  const end = Math.min(total, idx + 3)
  return seriesMates.value.slice(start, end)
})

// ── Other works by same creator (not in same series) ─────────────
const otherByCreator = computed(() => {
  if (!media.value?.creator) return []
  const currentSeries = media.value.series_name
  return allItems.value
    .filter(m =>
      m.creator === media.value.creator &&
      m.slug !== media.value.slug &&
      (currentSeries == null || m.series_name !== currentSeries)
    )
    .sort((a, b) => (a.year ?? 0) - (b.year ?? 0))
})

// ── Sub-item sibling navigation (episode or case prev/next) ──────
const prevSibling = computed(() => {
  const di = displayItem.value
  if (!di?.kind) return null
  if (di.kind === 'episode') {
    const idx = epIndex.value - 1
    const ep = di.parent.episodes?.[idx]
    return ep ? { title: ep.title, query: { ep: idx } } : null
  }
  if (di.kind === 'case') {
    const idx = caseIndex.value - 1
    const c = di.parent.cases?.[idx]
    return c ? { title: c.title, query: { case: idx } } : null
  }
  return null
})

const nextSibling = computed(() => {
  const di = displayItem.value
  if (!di?.kind) return null
  if (di.kind === 'episode') {
    const idx = epIndex.value + 1
    const ep = di.parent.episodes?.[idx]
    return ep ? { title: ep.title, query: { ep: idx } } : null
  }
  if (di.kind === 'case') {
    const idx = caseIndex.value + 1
    const c = di.parent.cases?.[idx]
    return c ? { title: c.title, query: { case: idx } } : null
  }
  return null
})

// ── SubItemSection ───────────────────────────────────────────────
const SubItemSection = {
  name: 'SubItemSection',
  components: { NoteHover, CauseBadge },
  props: { item: Object, revealed: { type: Boolean, default: false } },
  computed: {
    hasDeaths() { return (this.item?.deaths?.length || 0) > 0 },
    hasPersons() { return (this.item?.persons?.length || 0) > 0 },
  },
  methods: {
    resolveName(persons, id) {
      if (!id) return null
      return persons?.find((p) => p.id === id)?.name ?? id
    },
  },
  template: `
    <template v-if="!revealed && (hasDeaths || hasPersons)">
      <div class="hidden-spoiler-card">
        <h3 style="margin-top:0">Cast &amp; deaths hidden</h3>
        <p class="muted" style="margin:0">
          Mark this work (or its show / author) as completed to reveal its cast,
          victims, killers, and the rest of the case file.
        </p>
      </div>
    </template>
    <template v-if="revealed && hasPersons">
      <h3>Persons</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th><th>Role</th><th>Solver?</th><th>Profession</th><th>Archetype</th><th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in item.persons" :key="p.name">
              <td>
                <RouterLink v-if="p.role_in_story === 'detective'" :to="{ path: '/people', query: { filter: 'detective', q: p.name } }">{{ p.name }}</RouterLink>
                <template v-else>{{ p.name }}</template>
              </td>
              <td>{{ p.role_in_story || '—' }}</td>
              <td>{{ p.is_solver ? '✓' : '' }}</td>
              <td>{{ p.profession || '—' }}</td>
              <td>{{ p.archetype || '—' }}</td>
              <td><NoteHover :text="p.notes" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <template v-if="revealed && hasDeaths">
      <h3>Deaths</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>#</th><th>Victim</th><th>Cause</th><th>Killer</th><th>Motive</th><th>Type</th><th>Twist</th><th>Notes</th></tr>
          </thead>
          <tbody>
            <tr v-for="(d, i) in item.deaths" :key="i">
              <td>{{ d.ordinal || '—' }}</td>
              <td>{{ resolveName(item.persons, d.victim_id) || 'Unknown' }}</td>
              <td><CauseBadge :cause="d.cause" :means="d.means" /></td>
              <td>{{ d.killers?.map(k => resolveName(item.persons, k.person_id)).join(', ') || 'Unknown' }}</td>
              <td>{{ d.motive ? d.motive.charAt(0).toUpperCase() + d.motive.slice(1).replace(/_/g, ' ') : '—' }}</td>
              <td>{{ d.death_type || '—' }}</td>
              <td>{{ d.is_twist ? 'Yes' : 'No' }}</td>
              <td><NoteHover :text="d.notes || d.cause_detail || d.motive_detail" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  `,
}

// ── Helpers ──────────────────────────────────────────────────────
function extLinks(m) {
  const el = m.external_links
  if (!el) return []
  const links = []
  if (el.wikipedia_slug)
    links.push({ label: 'Wikipedia', url: `https://en.wikipedia.org/wiki/${el.wikipedia_slug}` })
  if (el.tvtropes_slug)
    links.push({ label: 'TV Tropes', url: `https://tvtropes.org/pmwiki/pmwiki.php/${el.tvtropes_slug}` })
  if (el.fandom_slug) {
    const slash = el.fandom_slug.indexOf('/')
    const sub = el.fandom_slug.slice(0, slash)
    const page = el.fandom_slug.slice(slash + 1)
    links.push({ label: 'Fandom', url: `https://${sub}.fandom.com/wiki/${page}` })
  }
  if (el.goodreads_id)
    links.push({ label: 'Goodreads', url: `https://www.goodreads.com/book/show/${el.goodreads_id}` })
  if (el.steam_id)
    links.push({ label: 'Steam', url: `https://store.steampowered.com/app/${el.steam_id}/` })
  if (el.itch_slug) {
    const slash = el.itch_slug.indexOf('/')
    const author = el.itch_slug.slice(0, slash)
    const slug = el.itch_slug.slice(slash + 1)
    links.push({ label: 'itch.io', url: `https://${author}.itch.io/${slug}` })
  }
  return links
}

function episodeDetectives(ep) {
  return (ep.persons || []).filter(p => p.role_in_story === 'detective').map(p => p.name)
}

function caseDetectives(c) {
  return (c.persons || []).filter(p => p.role_in_story === 'detective').map(p => p.name)
}
</script>

<template>
  <div v-if="!loaded" class="muted">Loading…</div>
  <div v-else-if="!media">
    <p class="muted">Media not found: <code>{{ route.params.slug }}</code></p>
    <RouterLink to="/">← Back to index</RouterLink>
  </div>
  <template v-else-if="displayItem">
    <!-- Sub-item (episode or case) -->
    <template v-if="displayItem.kind">
      <nav class="breadcrumb">
        <RouterLink to="/">Casefile Database</RouterLink> /
        <RouterLink :to="`/media/${displayItem.parent.slug}`">{{ displayItem.parent.title }}</RouterLink> /
        {{ displayItem.item.title }}
      </nav>

      <!-- Prev/Next sibling navigation -->
      <div v-if="prevSibling || nextSibling" class="sibling-nav">
        <RouterLink
          v-if="prevSibling"
          :to="{ path: `/media/${displayItem.parent.slug}`, query: prevSibling.query }"
        >← {{ prevSibling.title }}</RouterLink>
        <span v-else></span>
        <RouterLink
          v-if="nextSibling"
          :to="{ path: `/media/${displayItem.parent.slug}`, query: nextSibling.query }"
        >{{ nextSibling.title }} →</RouterLink>
      </div>

      <div class="media-header">
        <h2>{{ displayItem.item.title }}</h2>
        <div class="media-meta">
          <template v-if="displayItem.kind === 'episode'">
            <span v-if="displayItem.item.season != null">Season {{ displayItem.item.season }}</span>
            <span v-if="displayItem.item.episode_number != null">Episode {{ displayItem.item.episode_number }}</span>
            <span v-if="displayItem.item.year">{{ displayItem.item.year }}</span>
          </template>
          <template v-else>
            <span v-if="displayItem.item.case_number != null">Case {{ displayItem.item.case_number }}</span>
          </template>
          <span class="badge">{{ displayItem.kind }}</span>
        </div>
        <div v-if="displayItem.item.notes" class="media-notes">{{ displayItem.item.notes }}</div>
      </div>
      <SubItemSection :item="displayItem.item" :revealed="isMediaRevealed" />
    </template>

    <!-- Top-level media item -->
    <template v-else>
      <nav class="breadcrumb">
        <RouterLink to="/">Casefile Database</RouterLink> / {{ displayItem.item.title }}
      </nav>
      <div class="media-header" style="display:flex;gap:1.5rem;align-items:flex-start">
        <div style="flex:1;min-width:0">
          <h2>{{ displayItem.item.title }}</h2>
          <div class="media-meta">
            <RouterLink
              v-if="displayItem.item.creator"
              :to="{ path: `/author/${encodeURIComponent(displayItem.item.creator)}` }"
              style="color:var(--muted)"
            >{{ displayItem.item.creator }}</RouterLink>
            <span v-if="displayItem.item.year">{{ displayItem.item.year }}</span>
            <span :class="['badge', `badge-${displayItem.item.media_type}`]">{{ displayItem.item.media_type }}</span>
            <span v-if="displayItem.item.series_name" class="muted">
              {{ displayItem.item.series_name }}{{ displayItem.item.series_number != null ? ` #${displayItem.item.series_number}` : '' }}
            </span>
            <a
              v-if="displayItem.item.wikidata_id"
              :href="`https://www.wikidata.org/wiki/${displayItem.item.wikidata_id}`"
              target="_blank"
              rel="noopener noreferrer"
              class="mono"
            >{{ displayItem.item.wikidata_id }}</a>
          </div>
          <div v-if="displayItem.item.tags?.length" class="tag-list">
            <span v-for="t in displayItem.item.tags" :key="t" class="badge">{{ t }}</span>
          </div>
          <div v-if="extLinks(displayItem.item).length" class="ext-links">
            <a v-for="l in extLinks(displayItem.item)" :key="l.url" :href="l.url" target="_blank" rel="noopener noreferrer" class="ext-link">{{ l.label }}</a>
          </div>
          <p v-if="displayItem.item.notes" class="media-notes">{{ displayItem.item.notes }}</p>
          <div class="completion-row">
            <button
              type="button"
              :class="['btn', isMarkedDirectly ? '' : 'btn-primary']"
              @click="toggleSelfCompletion"
            >
              {{ isMarkedDirectly ? '✓ Marked as completed' : 'Mark as completed' }}
            </button>
            <span v-if="isMediaRevealed && !isMarkedDirectly" class="muted" style="font-size:0.82rem">
              (revealed via author / show / Mnesia mode)
            </span>
            <span v-else-if="!isMediaRevealed" class="muted" style="font-size:0.82rem">
              Spoilers stay hidden until marked.
            </span>
          </div>
        </div>
        <div v-if="coverUrl" style="flex-shrink:0;width:140px">
          <img :src="coverUrl" :alt="displayItem.item.title + ' cover'" style="width:100%;border-radius:6px;border:1px solid var(--border)" loading="lazy" @error="$event.target.style.display='none'" />
        </div>
      </div>

      <!-- Series navigation -->
      <template v-if="seriesMates.length > 1">
        <div class="series-nav">
          <span class="muted">{{ displayItem.item.series_name }}:</span>
          <span class="muted">{{ seriesIndex + 1 }} / {{ seriesMates.length }}</span>
          <RouterLink v-if="prevInSeries" :to="`/media/${prevInSeries.slug}`" class="series-step">← {{ prevInSeries.title }}</RouterLink>
          <RouterLink v-if="nextInSeries" :to="`/media/${nextInSeries.slug}`" class="series-step">{{ nextInSeries.title }} →</RouterLink>
        </div>
        <!-- Compact list for small series, context window for large -->
        <div class="series-list">
          <template v-if="seriesMates.length <= 20 || seriesExpanded">
            <RouterLink
              v-for="m in seriesMates"
              :key="m.slug"
              :to="`/media/${m.slug}`"
              :class="['series-item', m.slug === displayItem.item.slug ? 'series-item-current' : '']"
            >{{ m.title }}</RouterLink>
          </template>
          <template v-else>
            <RouterLink
              v-for="m in seriesContextSlice"
              :key="m.slug"
              :to="`/media/${m.slug}`"
              :class="['series-item', m.slug === displayItem.item.slug ? 'series-item-current' : '']"
            >{{ m.title }}</RouterLink>
            <button type="button" class="btn" style="font-size:0.8rem;padding:0.15rem 0.5rem" @click="seriesExpanded = true">
              + {{ seriesMates.length - seriesContextSlice.length }} more
            </button>
          </template>
        </div>
      </template>

      <!-- Other works by same creator -->
      <div v-if="otherByCreator.length" class="related-works">
        <span class="muted">More by {{ displayItem.item.creator }}:</span>
        <span v-for="(w, i) in otherByCreator.slice(0, 5)" :key="w.slug">
          <RouterLink :to="`/media/${w.slug}`">{{ w.title }}</RouterLink><!--
          --><span v-if="i < Math.min(otherByCreator.length, 5) - 1" class="muted">, </span>
        </span>
        <span v-if="otherByCreator.length > 5" class="muted"> +{{ otherByCreator.length - 5 }} more</span>
      </div>

      <!-- TV show episodes -->
      <template v-if="displayItem.item.media_type === 'tv_show' && displayItem.item.episodes?.length">
        <h3>Episodes</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>S</th><th>Ep</th><th>Title</th><th>Year</th><th v-if="isMediaRevealed">Deaths</th><th>Detectives</th></tr></thead>
            <tbody>
              <tr v-for="(ep, idx) in displayItem.item.episodes" :key="idx">
                <td>{{ ep.season ?? '—' }}</td>
                <td>{{ ep.episode_number ?? '—' }}</td>
                <td><RouterLink :to="{ path: `/media/${displayItem.item.slug}`, query: { ep: idx } }">{{ ep.title }}</RouterLink></td>
                <td>{{ ep.year ?? '—' }}</td>
                <td v-if="isMediaRevealed">{{ (ep.deaths || []).length }}</td>
                <td class="sensitive">{{ episodeDetectives(ep).join(', ') || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- Game cases -->
      <template v-if="displayItem.item.media_type === 'game' && displayItem.item.cases?.length">
        <h3>Cases</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Title</th><th v-if="isMediaRevealed">Deaths</th><th>Detectives</th></tr></thead>
            <tbody>
              <tr v-for="(c, idx) in displayItem.item.cases" :key="idx">
                <td>{{ c.case_number ?? idx + 1 }}</td>
                <td><RouterLink :to="{ path: `/media/${displayItem.item.slug}`, query: { case: idx } }">{{ c.title }}</RouterLink></td>
                <td v-if="isMediaRevealed">{{ (c.deaths || []).length }}</td>
                <td class="sensitive">{{ caseDetectives(c).join(', ') || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <StatisticsPanel
        v-if="showsStats"
        :entries="statsEntries"
        :title="`${displayItem.item.title} — death statistics`"
      />

      <SubItemSection :item="displayItem.item" :revealed="isMediaRevealed" />
    </template>
  </template>
</template>
