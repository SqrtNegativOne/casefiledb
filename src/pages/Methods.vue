<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData, allItems, resolveName } from '../composables/useData.js'
import { canReveal } from '../composables/useCompletion.js'
import NoteHover from '../components/NoteHover.vue'

const { ensureLoaded } = useData()
onMounted(ensureLoaded)

const expanded = ref(new Set())

function causeLabel(c) {
  return c.charAt(0) + c.slice(1).toLowerCase().replace(/_/g, ' ')
}

const methods = computed(() => {
  const map = new Map()
  for (const item of allItems.value) {
    const direct = (item.deaths || []).map((d) => ({ death: d, media: item, context: null, persons: item.persons || [] }))
    const eps = (item.episodes || []).flatMap((e) =>
      (e.deaths || []).map((d) => ({ death: d, media: item, context: e, persons: e.persons || [] }))
    )
    const cs = (item.cases || []).flatMap((c) =>
      (c.deaths || []).map((d) => ({ death: d, media: item, context: c, persons: c.persons || [] }))
    )
    for (const entry of [...direct, ...eps, ...cs]) {
      const cause = entry.death.cause || 'UNKNOWN'
      if (!map.has(cause)) map.set(cause, [])
      map.get(cause).push(entry)
    }
  }
  return [...map.entries()]
    .map(([cause, entries]) => ({ cause, entries }))
    .sort((a, b) => b.entries.length - a.entries.length)
})

const total = computed(() => methods.value.reduce((n, m) => n + m.entries.length, 0))

function toggleExpand(cause) {
  const s = new Set(expanded.value)
  if (s.has(cause)) s.delete(cause)
  else s.add(cause)
  expanded.value = s
}

/**
 * Group entries by media (and optional sub-context) and split into:
 *   - revealed: works the user has marked as completed (full details visible)
 *   - hiddenCount: number of additional works whose details stay spoiler-protected
 */
function byMedia(entries) {
  const map = new Map()
  for (const { death, media, context, persons } of entries) {
    const key = `${media.slug}::${context?.title ?? ''}`
    if (!map.has(key)) map.set(key, { media, context, persons, deaths: [] })
    map.get(key).deaths.push(death)
  }
  const grouped = [...map.values()].sort((a, b) =>
    String(a.media.title).localeCompare(String(b.media.title))
  )
  const revealed = grouped.filter((g) => canReveal(g.media))
  const hidden = grouped.filter((g) => !canReveal(g.media))
  const hiddenDeaths = hidden.reduce((n, g) => n + g.deaths.length, 0)
  return { revealed, hiddenWorks: hidden.length, hiddenDeaths }
}
</script>

<template>
  <div>
    <div class="meta-row">{{ methods.length }} methods, {{ total }} deaths total</div>
    <p class="muted" style="font-size:0.85rem;margin:0 0 0.75rem">
      Each method shows aggregate counts. The list of works that use it is collapsed —
      expand it to see works you've marked as completed; other works stay hidden so they
      can't spoil their twists.
    </p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Deaths</th>
            <th>% of total</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="m in methods" :key="m.cause">
            <tr>
              <td><span :class="['badge', `cause-${m.cause}`]">{{ causeLabel(m.cause) }}</span></td>
              <td>{{ m.entries.length }}</td>
              <td>{{ total > 0 ? ((m.entries.length / total) * 100).toFixed(1) : '0.0' }}%</td>
              <td>
                <button type="button" @click="toggleExpand(m.cause)">
                  {{ expanded.has(m.cause) ? 'Hide' : 'Show works' }}
                </button>
              </td>
            </tr>
            <template v-if="expanded.has(m.cause)">
              <template v-for="group in [byMedia(m.entries)]" :key="m.cause + ':grp'">
                <tr v-if="!group.revealed.length && group.hiddenWorks" class="details-row">
                  <td colspan="4" class="muted" style="font-style:italic">
                    {{ group.hiddenWorks }} work{{ group.hiddenWorks === 1 ? '' : 's' }} use this method
                    ({{ group.hiddenDeaths }} death{{ group.hiddenDeaths === 1 ? '' : 's' }}).
                    Mark them as completed to reveal.
                  </td>
                </tr>
                <tr
                  v-for="({ media, context, persons, deaths }) in group.revealed"
                  :key="`${media.slug}::${context?.title ?? ''}`"
                  class="details-row"
                >
                  <td colspan="4">
                    <strong>
                      <RouterLink :to="`/media/${media.slug}`">{{ media.title }}</RouterLink>
                    </strong>
                    <span v-if="context" class="muted"> — {{ context.title }}</span>
                    <table class="mini-table" style="margin-top:0.4rem">
                      <thead><tr><th>Victim</th><th>Killer</th><th>Cause detail</th></tr></thead>
                      <tbody>
                        <tr v-for="(d, i) in deaths" :key="i">
                          <td>{{ resolveName(persons, d.victim_id) || 'Unknown' }}</td>
                          <td>{{ d.killers?.map(k => resolveName(persons, k.person_id)).join(', ') || 'Unknown' }}</td>
                          <td>
                            {{ d.cause }}
                            <span v-if="d.means" class="muted">({{ d.means }})</span>
                            <span v-if="d.is_twist" class="badge" style="margin-left:0.3rem">twist</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
                <tr
                  v-if="group.revealed.length && group.hiddenWorks"
                  class="details-row"
                >
                  <td colspan="4" class="muted" style="font-style:italic">
                    + {{ group.hiddenWorks }} other work{{ group.hiddenWorks === 1 ? '' : 's' }}
                    ({{ group.hiddenDeaths }} death{{ group.hiddenDeaths === 1 ? '' : 's' }}) hidden — mark them as completed to reveal.
                  </td>
                </tr>
              </template>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
