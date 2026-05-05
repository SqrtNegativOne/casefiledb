<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useData, allDeaths } from '../composables/useData.js'

const { data, ensureLoaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

// Homicide data from UNODC Global Study on Homicide & national statistics offices
// rate = intentional homicides per 100,000 population per year
const REAL_WORLD = [
  { id: 'world',           name: 'Entire World',              pop: 8045311447, homicides: 458000, rate: 5.8,   year: 2021, category: 'world'   },
  { id: 'af-ng',           name: 'Nigeria',                   pop: 206139589,  homicides: 22000,  rate: 10.0,  year: 2021, category: 'country' },
  { id: 'af-za',           name: 'South Africa',              pop: 59893885,   homicides: 27494,  rate: 45.8,  year: 2022, category: 'country' },
  { id: 'am-br',           name: 'Brazil',                    pop: 215353593,  homicides: 47508,  rate: 22.1,  year: 2022, category: 'country' },
  { id: 'am-ca',           name: 'Canada',                    pop: 38781292,   homicides: 836,    rate: 2.2,   year: 2022, category: 'country' },
  { id: 'am-co',           name: 'Colombia',                  pop: 51874024,   homicides: 16762,  rate: 32.9,  year: 2022, category: 'country' },
  { id: 'am-hn',           name: 'Honduras',                  pop: 10278345,   homicides: 3578,   rate: 34.7,  year: 2022, category: 'country' },
  { id: 'am-jm',           name: 'Jamaica',                   pop: 2827595,    homicides: 1597,   rate: 57.1,  year: 2022, category: 'country' },
  { id: 'am-mx',           name: 'Mexico',                    pop: 130207371,  homicides: 33681,  rate: 25.9,  year: 2022, category: 'country' },
  { id: 'am-us',           name: 'United States',             pop: 331449281,  homicides: 22900,  rate: 6.9,   year: 2022, category: 'country' },
  { id: 'am-ve',           name: 'Venezuela',                 pop: 28887118,   homicides: 13325,  rate: 45.9,  year: 2022, category: 'country' },
  { id: 'as-au',           name: 'Australia',                 pop: 25499884,   homicides: 280,    rate: 1.1,   year: 2022, category: 'country' },
  { id: 'as-cn',           name: 'China',                     pop: 1412600000, homicides: 9800,   rate: 0.7,   year: 2021, category: 'country' },
  { id: 'as-in',           name: 'India',                     pop: 1380004385, homicides: 33033,  rate: 2.4,   year: 2022, category: 'country' },
  { id: 'as-jp',           name: 'Japan',                     pop: 125681593,  homicides: 299,    rate: 0.2,   year: 2022, category: 'country' },
  { id: 'eu-de',           name: 'Germany',                   pop: 83783942,   homicides: 720,    rate: 0.9,   year: 2022, category: 'country' },
  { id: 'eu-fr',           name: 'France',                    pop: 67391582,   homicides: 870,    rate: 1.3,   year: 2022, category: 'country' },
  { id: 'eu-gb',           name: 'United Kingdom',            pop: 67886011,   homicides: 697,    rate: 1.0,   year: 2022, category: 'country' },
  { id: 'eu-ru',           name: 'Russia',                    pop: 145934462,  homicides: 9000,   rate: 6.2,   year: 2022, category: 'country' },
  { id: 'city-cape-town',  name: 'Cape Town, South Africa',   pop: 4618000,    homicides: 4532,   rate: 98.1,  year: 2022, category: 'city'    },
  { id: 'city-chicago',    name: 'Chicago, USA',              pop: 2696555,    homicides: 695,    rate: 25.7,  year: 2022, category: 'city'    },
  { id: 'city-detroit',    name: 'Detroit, USA',              pop: 632464,     homicides: 271,    rate: 42.8,  year: 2022, category: 'city'    },
  { id: 'city-la',         name: 'Los Angeles, USA',          pop: 3979576,    homicides: 382,    rate: 9.6,   year: 2022, category: 'city'    },
  { id: 'city-london',     name: 'London, UK',                pop: 8961989,    homicides: 141,    rate: 1.6,   year: 2022, category: 'city'    },
  { id: 'city-medellin',   name: 'Medellín, Colombia',        pop: 2627683,    homicides: 682,    rate: 26.2,  year: 2022, category: 'city'    },
  { id: 'city-nyc',        name: 'New York City, USA',        pop: 8336817,    homicides: 488,    rate: 5.9,   year: 2022, category: 'city'    },
  { id: 'city-sps',        name: 'San Pedro Sula, Honduras',  pop: 900000,     homicides: 970,    rate: 107.7, year: 2022, category: 'city'    },
  { id: 'city-tijuana',    name: 'Tijuana, Mexico',           pop: 2002920,    homicides: 2005,   rate: 100.1, year: 2022, category: 'city'    },
  { id: 'city-tokyo',      name: 'Tokyo, Japan',              pop: 13960000,   homicides: 35,     rate: 0.25,  year: 2022, category: 'city'    },
]

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
  if (mode === 'real') {
    const byCategory = (cat) =>
      REAL_WORLD.filter((l) => l.category === cat)
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((l) => ({ value: `real:${l.id}`, label: l.name }))
    return [
      ...byCategory('world'),
      { value: '', label: '── Countries ──', disabled: true },
      ...byCategory('country'),
      { value: '', label: '── Cities ──', disabled: true },
      ...byCategory('city'),
    ]
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
  if (type === 'real') {
    const loc = REAL_WORLD.find((l) => l.id === key)
    return loc ? { name: loc.name, type: 'real', location: loc } : null
  }
  if (type === 'author') {
    const a = authors.value.find((x) => x.name === key)
    return a ? { name: a.name, type: 'fiction', stats: statsFor(a.works) } : null
  }
  const item = data.value.find((m) => m.slug === key)
  return item ? { name: `${item.title} (${item.creator || '?'}, ${item.year || '?'})`, type: 'fiction', stats: statsFor([item]) } : null
}

const panelA = computed(() => resolve(selA.value))
const panelB = computed(() => resolve(selB.value))

// Deep-link
watch(() => data.value.length, () => {
  if (!route.query.a && !route.query.b) return
  if (route.query.a) {
    const [t] = route.query.a.split(':')
    modeA.value = t === 'media' ? 'media' : t === 'real' ? 'real' : 'author'
    selA.value = route.query.a
  }
  if (route.query.b) {
    const [t] = route.query.b.split(':')
    modeB.value = t === 'media' ? 'media' : t === 'real' ? 'real' : 'author'
    selB.value = route.query.b
  }
}, { once: true })

function fmt(s) { return s.toLowerCase().replace(/_/g, ' ') }
function fmtNum(n) { return n.toLocaleString() }
function categoryLabel(cat) { return cat === 'world' ? 'World' : cat === 'country' ? 'Country' : 'City' }
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
          <option value="real">Real World</option>
        </select>
        <select :value="sel" @change="side === 0 ? selA = $event.target.value : selB = $event.target.value">
          <option value="">— select —</option>
          <option v-for="o in optionsFor(mode)" :key="o.value + o.label" :value="o.value" :disabled="o.disabled">{{ o.label }}</option>
        </select>
      </div>
      <div class="compare-panel-body">
        <template v-if="!panel">
          <p class="compare-hint">{{ mode === 'real' ? 'Select a location above.' : 'Select an author or work above.' }}</p>
        </template>
        <template v-else-if="panel.type === 'real'">
          <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;flex-wrap:wrap">
            <span style="font-weight:600;font-size:1.05rem">{{ panel.name }}</span>
            <span class="real-badge">{{ categoryLabel(panel.location.category) }}</span>
          </div>
          <div class="stat-row"><span class="stat-label">Population</span><span class="stat-value">{{ fmtNum(panel.location.pop) }}</span></div>
          <div class="stat-row"><span class="stat-label">Annual homicides</span><span class="stat-value">{{ fmtNum(panel.location.homicides) }}</span></div>
          <div class="stat-row">
            <span class="stat-label">Rate per 100k/yr</span>
            <span class="stat-value">{{ panel.location.rate.toFixed(1) }}</span>
          </div>
          <div class="stat-row"><span class="stat-label">Data year</span><span class="stat-value">{{ panel.location.year }}</span></div>
          <p class="real-source">Source: UNODC Global Study on Homicide &amp; national statistics offices</p>
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
