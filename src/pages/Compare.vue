<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useData, allDeaths } from '../composables/useData.js'

const { data, ensureLoaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

const modeA = ref('author')
const modeB = ref('author')
const selA = ref('')
const selB = ref('')

const authors = computed(() => {
  const map = new Map()
  for (const item of data.value) {
    const c = item.creator || 'Unknown'
    if (!map.has(c)) map.set(c, { name: c, works: [] })
    map.get(c).works.push(item)
  }
  return [...map.values()].sort((a, b) => a.name.localeCompare(b.name))
})

function optionsFor(mode) {
  if (mode === 'author') {
    return authors.value.map((a) => ({ value: `author:${a.name}`, label: `${a.name} (${a.works.length} works)` }))
  }
  return [...data.value]
    .sort((a, b) => String(a.title).localeCompare(String(b.title)))
    .map((m) => ({ value: `media:${m.slug}`, label: `${m.title} (${m.year || '?'})` }))
}

function topN(counts, n) {
  return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, n)
}

function statsFor(items) {
  const deaths = items.flatMap(allDeaths)
  const total = deaths.length
  const works = items.length
  const twists = deaths.filter((d) => d.is_twist).length
  const causeCounts = {}, motiveCounts = {}, typeCounts = {}
  for (const d of deaths) {
    if (d.cause) causeCounts[d.cause] = (causeCounts[d.cause] || 0) + 1
    if (d.motive) motiveCounts[d.motive] = (motiveCounts[d.motive] || 0) + 1
    if (d.death_type) typeCounts[d.death_type] = (typeCounts[d.death_type] || 0) + 1
  }
  return {
    works, total,
    avg: works > 0 ? (total / works).toFixed(1) : '0.0',
    twists,
    twistRate: total > 0 ? ((twists / total) * 100).toFixed(1) : '0.0',
    topCauses: topN(causeCounts, 3),
    topMotives: topN(motiveCounts, 3),
    topTypes: topN(typeCounts, 3),
  }
}

function resolve(value) {
  if (!value) return null
  const [type, key] = value.split(/:(.+)/)
  if (type === 'author') {
    const a = authors.value.find((x) => x.name === key)
    return a ? { name: a.name, stats: statsFor(a.works) } : null
  }
  const item = data.value.find((m) => m.slug === key)
  return item ? { name: `${item.title} (${item.creator||'?'}, ${item.year||'?'})`, stats: statsFor([item]) } : null
}

const panelA = computed(() => resolve(selA.value))
const panelB = computed(() => resolve(selB.value))

// Deep-link
watch(() => data.value.length, () => {
  if (!route.query.a && !route.query.b) return
  if (route.query.a) {
    const [t] = route.query.a.split(':')
    modeA.value = t === 'media' ? 'media' : 'author'
    selA.value = route.query.a
  }
  if (route.query.b) {
    const [t] = route.query.b.split(':')
    modeB.value = t === 'media' ? 'media' : 'author'
    selB.value = route.query.b
  }
}, { once: true })

function fmt(s) { return s.toLowerCase().replace(/_/g, ' ') }
</script>

<template>
  <div class="compare-grid">
    <div v-for="({ mode, sel, panel }, side) in [
      { mode: modeA, sel: selA, panel: panelA },
      { mode: modeB, sel: selB, panel: panelB },
    ]" :key="side" class="compare-panel">
      <div class="compare-panel-header">
        <select :value="mode" @change="side === 0 ? (modeA = $event.target.value, selA = '') : (modeB = $event.target.value, selB = '')">
          <option value="author">Author</option>
          <option value="media">Work</option>
        </select>
        <select :value="sel" @change="side === 0 ? selA = $event.target.value : selB = $event.target.value">
          <option value="">— select —</option>
          <option v-for="o in optionsFor(mode)" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </div>
      <div class="compare-panel-body">
        <template v-if="!panel">
          <p class="compare-hint">Select an author or work above.</p>
        </template>
        <template v-else>
          <div style="font-weight:600;font-size:1.05rem;margin-bottom:0.75rem">{{ panel.name }}</div>
          <div class="stat-row"><span class="stat-label">Works</span><span class="stat-value">{{ panel.stats.works }}</span></div>
          <div class="stat-row"><span class="stat-label">Total deaths</span><span class="stat-value">{{ panel.stats.total }}</span></div>
          <div class="stat-row"><span class="stat-label">Avg / work</span><span class="stat-value">{{ panel.stats.avg }}</span></div>
          <div class="stat-row">
            <span class="stat-label">Twist deaths</span>
            <span class="stat-value">{{ panel.stats.twists }} <span class="muted" style="font-weight:400;font-size:0.85rem">({{ panel.stats.twistRate }}%)</span></span>
          </div>
          <div class="stat-row" style="flex-direction:column;align-items:flex-start;gap:0.3rem">
            <span class="stat-label">Top causes</span>
            <ul class="top-list">
              <li v-if="!panel.stats.topCauses.length"><span class="muted">none</span></li>
              <li v-for="[label, count] in panel.stats.topCauses" :key="label">
                <span>{{ fmt(label) }}</span><strong>{{ count }}</strong>
              </li>
            </ul>
          </div>
          <div class="stat-row" style="flex-direction:column;align-items:flex-start;gap:0.3rem">
            <span class="stat-label">Top motives</span>
            <ul class="top-list">
              <li v-if="!panel.stats.topMotives.length"><span class="muted">none</span></li>
              <li v-for="[label, count] in panel.stats.topMotives" :key="label">
                <span>{{ fmt(label) }}</span><strong>{{ count }}</strong>
              </li>
            </ul>
          </div>
          <div class="stat-row" style="flex-direction:column;align-items:flex-start;gap:0.3rem">
            <span class="stat-label">Death types</span>
            <ul class="top-list">
              <li v-if="!panel.stats.topTypes.length"><span class="muted">none</span></li>
              <li v-for="[label, count] in panel.stats.topTypes" :key="label">
                <span>{{ fmt(label) }}</span><strong>{{ count }}</strong>
              </li>
            </ul>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
