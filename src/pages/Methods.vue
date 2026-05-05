<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData, allDeaths } from '../composables/useData.js'
import NoteHover from '../components/NoteHover.vue'

const { data, ensureLoaded } = useData()
onMounted(ensureLoaded)

const expanded = ref(new Set())

function causeLabel(c) {
  return c.charAt(0) + c.slice(1).toLowerCase().replace(/_/g, ' ')
}

const methods = computed(() => {
  const map = new Map()
  for (const item of data.value) {
    const direct = (item.deaths || []).map((d) => ({ death: d, media: item, context: null }))
    const eps = (item.episodes || []).flatMap((e) =>
      (e.deaths || []).map((d) => ({ death: d, media: item, context: e }))
    )
    const cs = (item.cases || []).flatMap((c) =>
      (c.deaths || []).map((d) => ({ death: d, media: item, context: c }))
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

function byMedia(entries) {
  const map = new Map()
  for (const { death, media, context } of entries) {
    if (!map.has(media.slug)) map.set(media.slug, { media, context, deaths: [] })
    map.get(media.slug).deaths.push(death)
  }
  return [...map.values()].sort((a, b) => String(a.media.title).localeCompare(String(b.media.title)))
}
</script>

<template>
  <div>
    <div class="meta-row">{{ methods.length }} methods, {{ total }} deaths total</div>
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
                  {{ expanded.has(m.cause) ? 'Hide' : 'Show' }}
                </button>
              </td>
            </tr>
            <template v-if="expanded.has(m.cause)">
              <tr v-for="({ media, context, deaths }) in byMedia(m.entries)" :key="media.slug" class="details-row">
                <td colspan="4">
                  <strong>
                    <RouterLink :to="`/media/${media.slug}`">{{ media.title }}</RouterLink>
                  </strong>
                  <span v-if="context" class="muted"> — {{ context.title }}</span>
                  <table class="mini-table" style="margin-top:0.4rem">
                    <thead><tr><th>Victim</th><th>Killer</th><th>Cause detail</th></tr></thead>
                    <tbody>
                      <tr v-for="(d, i) in deaths" :key="i">
                        <td class="sensitive">{{ d.victim_name || 'Unknown' }}</td>
                        <td class="sensitive">{{ d.killers?.map(k => k.name).join(', ') || 'Unknown' }}</td>
                        <td>
                          {{ d.cause }}
                          <span v-if="d.cause_subtype" class="muted">({{ d.cause_subtype }})</span>
                          <span v-if="d.is_twist" class="badge" style="margin-left:0.3rem">twist</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
