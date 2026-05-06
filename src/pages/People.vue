<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useData, allItems, deathCount } from '../composables/useData.js'

const { ensureLoaded } = useData()
const route = useRoute()
const router = useRouter()
onMounted(ensureLoaded)

const search = ref('')
const filter = ref('all') // all | victim | killer | detective | solver

onMounted(() => {
  if (route.query.filter) filter.value = String(route.query.filter)
  if (route.query.q) search.value = String(route.query.q)
})

/**
 * Aggregate every person across every scope, grouped by name. For each
 * person we record: the works they appear in, and counts of the four roles
 * they show up as (victim / killer / detective / solver).
 */
const people = computed(() => {
  const map = new Map()

  function ensure(name) {
    if (!map.has(name)) {
      map.set(name, {
        name,
        sample: null,
        works: new Map(),
        victimCount: 0,
        killerCount: 0,
        detectiveCount: 0,
        solverCount: 0,
      })
    }
    return map.get(name)
  }

  function bestSample(cur, p) {
    if (!cur) return p
    const score = (x) =>
      (x.profession ? 1 : 0) + (x.skills?.length || 0) + (x.archetype ? 1 : 0) + (x.notes ? 1 : 0) + (x.nationality ? 1 : 0)
    return score(p) > score(cur) ? p : cur
  }

  for (const media of allItems.value) {
    const scopes = [
      { persons: media.persons || [], deaths: media.deaths || [], context: media },
      ...(media.episodes || []).map((e) => ({ persons: e.persons || [], deaths: e.deaths || [], context: media })),
      ...(media.cases || []).map((c) => ({ persons: c.persons || [], deaths: c.deaths || [], context: media })),
    ]

    for (const { persons, deaths, context } of scopes) {
      const idToPerson = new Map(persons.map((p) => [p.id, p]))

      // Persons table → record name + roles
      for (const p of persons) {
        const e = ensure(p.name)
        e.sample = bestSample(e.sample, p)
        e.works.set(context.slug, context)
        if (p.role_in_story === 'detective') e.detectiveCount++
        if (p.is_solver === true) e.solverCount++
      }

      // Deaths → record victim and killers
      for (const d of deaths) {
        const victim = idToPerson.get(d.victim_id)
        if (victim) {
          const e = ensure(victim.name)
          e.victimCount++
          e.works.set(context.slug, context)
        }
        for (const k of (d.killers || [])) {
          const killer = idToPerson.get(k.person_id)
          if (killer) {
            const e = ensure(killer.name)
            e.killerCount++
            e.works.set(context.slug, context)
          }
        }
      }
    }
  }

  return [...map.values()].map((e) => ({
    ...e,
    workList: [...e.works.values()],
  }))
})

const counts = computed(() => ({
  all: people.value.length,
  victim: people.value.filter((p) => p.victimCount > 0).length,
  killer: people.value.filter((p) => p.killerCount > 0).length,
  detective: people.value.filter((p) => p.detectiveCount > 0).length,
  solver: people.value.filter((p) => p.solverCount > 0).length,
}))

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = people.value
  if (filter.value === 'victim') list = list.filter((p) => p.victimCount > 0)
  else if (filter.value === 'killer') list = list.filter((p) => p.killerCount > 0)
  else if (filter.value === 'detective') list = list.filter((p) => p.detectiveCount > 0)
  else if (filter.value === 'solver') list = list.filter((p) => p.solverCount > 0)
  if (q) list = list.filter((p) => p.name.toLowerCase().includes(q))
  return list.slice().sort((a, b) => {
    // Order detectives/solvers by works, victims/killers by count, all by works.
    const f = filter.value
    if (f === 'victim') return b.victimCount - a.victimCount || a.name.localeCompare(b.name)
    if (f === 'killer') return b.killerCount - a.killerCount || a.name.localeCompare(b.name)
    if (f === 'solver') return b.solverCount - a.solverCount || a.name.localeCompare(b.name)
    return b.workList.length - a.workList.length || a.name.localeCompare(b.name)
  })
})

function setFilter(f) {
  filter.value = f
  router.replace({ query: { ...(f === 'all' ? {} : { filter: f }), ...(search.value ? { q: search.value } : {}) } })
}

function roleBadges(p) {
  const out = []
  if (p.victimCount) out.push({ label: `victim ×${p.victimCount}`, cls: 'role-victim' })
  if (p.killerCount) out.push({ label: `killer ×${p.killerCount}`, cls: 'role-killer' })
  if (p.detectiveCount) out.push({ label: `detective ×${p.detectiveCount}`, cls: 'role-detective' })
  if (p.solverCount) out.push({ label: `solver ×${p.solverCount}`, cls: 'role-solver' })
  return out
}
</script>

<template>
  <div>
    <div class="filter-chips">
      <button type="button" :class="['chip', { 'chip-active': filter === 'all' }]" @click="setFilter('all')">
        All <span class="muted">{{ counts.all }}</span>
      </button>
      <button type="button" :class="['chip', { 'chip-active': filter === 'victim' }]" @click="setFilter('victim')">
        Victims <span class="muted">{{ counts.victim }}</span>
      </button>
      <button type="button" :class="['chip', { 'chip-active': filter === 'killer' }]" @click="setFilter('killer')">
        Killers <span class="muted">{{ counts.killer }}</span>
      </button>
      <button type="button" :class="['chip', { 'chip-active': filter === 'detective' }]" @click="setFilter('detective')">
        Detectives <span class="muted">{{ counts.detective }}</span>
      </button>
      <button type="button" :class="['chip', { 'chip-active': filter === 'solver' }]" @click="setFilter('solver')">
        Solvers <span class="muted">{{ counts.solver }}</span>
      </button>
    </div>

    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search by name…" />
    </div>
    <div class="meta-row">{{ filtered.length }} {{ filter === 'all' ? 'person' : filter }}{{ filtered.length === 1 ? '' : 's' }}</div>

    <div class="people-grid">
      <p v-if="!filtered.length" class="muted">No people found.</p>
      <div v-for="p in filtered" :key="p.name" class="person-card">
        <p class="person-name sensitive">{{ p.name }}</p>
        <div class="person-meta">
          <span>{{ p.workList.length }} work{{ p.workList.length === 1 ? '' : 's' }}</span>
          <span v-if="p.sample?.profession" class="muted">· {{ p.sample.profession }}</span>
          <span v-if="p.sample?.nationality" class="muted">· {{ p.sample.nationality }}</span>
        </div>
        <div class="role-badges">
          <span v-for="(b, i) in roleBadges(p)" :key="i" :class="['badge', b.cls]">{{ b.label }}</span>
        </div>
        <div v-if="p.sample?.archetype" class="person-archetype">{{ p.sample.archetype }}</div>
        <div v-if="p.sample?.skills?.length" class="person-skills">
          <span v-for="sk in p.sample.skills.slice(0, 4)" :key="sk" class="badge">{{ sk }}</span>
        </div>
        <div class="person-works">
          <RouterLink
            v-for="(w, i) in p.workList.slice(0, 5)"
            :key="w.slug"
            :to="`/media/${w.slug}`"
            class="muted"
          >{{ w.title }}<span v-if="i < Math.min(p.workList.length, 5) - 1">, </span></RouterLink>
          <span v-if="p.workList.length > 5" class="muted"> +{{ p.workList.length - 5 }} more</span>
        </div>
      </div>
    </div>
  </div>
</template>
