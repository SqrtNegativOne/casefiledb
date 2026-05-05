<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useData } from '../composables/useData.js'
import { useCoverImage } from '../composables/useCoverImage.js'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const { data, ensureLoaded } = useData()
const route = useRoute()
const router = useRouter()

onMounted(ensureLoaded)

const media = computed(() => data.value.find((m) => m.slug === route.params.slug) || null)
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
watch(() => data.value.length, () => {
  if (media.value) return
  const slug = route.params.slug
  for (const item of data.value) {
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
</script>

<template>
  <div v-if="!data.length" class="muted">Loading…</div>
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
      <SubItemSection :item="displayItem.item" />
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
            <span v-if="displayItem.item.creator">{{ displayItem.item.creator }}</span>
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
        </div>
        <div v-if="coverUrl" style="flex-shrink:0;width:140px">
          <img :src="coverUrl" :alt="displayItem.item.title + ' cover'" style="width:100%;border-radius:6px;border:1px solid var(--border)" loading="lazy" @error="$event.target.style.display='none'" />
        </div>
      </div>

      <!-- TV show episodes -->
      <template v-if="displayItem.item.media_type === 'tv_show' && displayItem.item.episodes?.length">
        <h3>Episodes</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>S</th><th>Ep</th><th>Title</th><th>Year</th><th>Deaths</th></tr></thead>
            <tbody>
              <tr v-for="(ep, idx) in displayItem.item.episodes" :key="idx">
                <td>{{ ep.season ?? '—' }}</td>
                <td>{{ ep.episode_number ?? '—' }}</td>
                <td><RouterLink :to="{ path: `/media/${displayItem.item.slug}`, query: { ep: idx } }">{{ ep.title }}</RouterLink></td>
                <td>{{ ep.year ?? '—' }}</td>
                <td>{{ (ep.deaths || []).length }}</td>
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
            <thead><tr><th>#</th><th>Title</th><th>Deaths</th></tr></thead>
            <tbody>
              <tr v-for="(c, idx) in displayItem.item.cases" :key="idx">
                <td>{{ c.case_number ?? idx + 1 }}</td>
                <td><RouterLink :to="{ path: `/media/${displayItem.item.slug}`, query: { case: idx } }">{{ c.title }}</RouterLink></td>
                <td>{{ (c.deaths || []).length }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <SubItemSection :item="displayItem.item" />
    </template>
  </template>
</template>

<script>
import { defineComponent } from 'vue'
import NoteHover from '../components/NoteHover.vue'
import CauseBadge from '../components/CauseBadge.vue'

const SubItemSection = defineComponent({
  name: 'SubItemSection',
  components: { NoteHover, CauseBadge },
  props: { item: Object },
  template: `
    <template v-if="item.persons?.length">
      <h3>Persons</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Name</th><th>Role</th><th>Solver?</th><th>Profession</th><th>Notes</th></tr></thead>
          <tbody>
            <tr v-for="p in item.persons" :key="p.name">
              <td class="sensitive">{{ p.name }}</td>
              <td>{{ p.role_in_story || '—' }}</td>
              <td>{{ p.is_solver ? '✓' : '' }}</td>
              <td>{{ p.profession || '—' }}</td>
              <td><NoteHover :text="p.notes" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <template v-if="item.deaths?.length">
      <h3>Deaths</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>#</th><th>Victim</th><th>Cause</th><th>Killer</th><th>Type</th><th>Twist</th><th>Notes</th></tr></thead>
          <tbody>
            <tr v-for="(d, i) in item.deaths" :key="i">
              <td>{{ d.ordinal || '—' }}</td>
              <td class="sensitive">{{ d.victim_name || 'Unknown' }}</td>
              <td><CauseBadge :cause="d.cause" :means="d.means" /></td>
              <td class="sensitive">{{ d.killers?.map(k => k.name).join(', ') || 'Unknown' }}</td>
              <td>{{ d.death_type || '—' }}</td>
              <td>{{ d.is_twist ? 'Yes' : 'No' }}</td>
              <td><NoteHover :text="d.notes || d.cause_detail || d.motive_detail" /></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  `,
})
</script>
