<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useData, allItems, deathCount } from '../composables/useData.js'

const { ensureLoaded } = useData()
const route = useRoute()
onMounted(ensureLoaded)

const search = ref('')

onMounted(() => {
  if (route.query.q) search.value = route.query.q
})

/**
 * Aggregate all persons with role_in_story === 'detective' across every scope.
 * Groups by name so Poirot appearing in 50 books shows as one entry.
 */
const detectives = computed(() => {
  const map = new Map()

  for (const media of allItems.value) {
    const scopes = [
      { persons: media.persons || [], context: media },
      ...(media.episodes || []).map((e) => ({ persons: e.persons || [], context: media })),
      ...(media.cases || []).map((c) => ({ persons: c.persons || [], context: media })),
    ]

    for (const { persons, context } of scopes) {
      for (const p of persons) {
        if (p.role_in_story !== 'detective') continue
        if (!map.has(p.name)) {
          map.set(p.name, {
            name: p.name,
            sample: p,
            works: new Map(),
            solverCount: 0,
            nonSolverCount: 0,
          })
        }
        const entry = map.get(p.name)
        entry.works.set(context.slug, context)
        if (p.is_solver === true) entry.solverCount++
        else if (p.is_solver === false) entry.nonSolverCount++
        // Keep richest person record (most fields filled)
        const cur = entry.sample
        const score = (x) => (x.profession ? 1 : 0) + (x.skills?.length || 0) + (x.archetype ? 1 : 0) + (x.notes ? 1 : 0) + (x.nationality ? 1 : 0)
        if (score(p) > score(cur)) entry.sample = p
      }
    }
  }

  return [...map.values()]
    .map((e) => ({
      ...e,
      workList: [...e.works.values()],
      totalDeaths: [...e.works.values()].reduce((n, w) => n + deathCount(w), 0),
    }))
    .sort((a, b) => b.workList.length - a.workList.length)
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return detectives.value
  return detectives.value.filter((d) => d.name.toLowerCase().includes(q))
})

function solverLabel(d) {
  if (d.solverCount > 0 && d.nonSolverCount === 0) return 'solver'
  if (d.solverCount > 0) return 'sometimes solver'
  if (d.nonSolverCount > 0) return 'not the solver'
  return null
}

function skillTags(p) {
  return (p.skills || []).slice(0, 4)
}
</script>

<template>
  <div>
    <div class="controls-bar">
      <input v-model="search" type="text" placeholder="Search detective name…" />
    </div>
    <div class="meta-row">{{ filtered.length }} detective{{ filtered.length === 1 ? '' : 's' }}</div>

    <div class="detectives-grid">
      <div
        v-for="d in filtered"
        :key="d.name"
        class="detective-card"
      >
        <div class="detective-icon">🔍</div>
        <div style="flex:1;min-width:0">
          <p class="detective-name sensitive">{{ d.name }}</p>
          <div class="detective-meta">
            <span>{{ d.workList.length }} work{{ d.workList.length === 1 ? '' : 's' }}</span>
            <span class="muted">· {{ d.totalDeaths }} death{{ d.totalDeaths === 1 ? '' : 's' }}</span>
            <span v-if="d.sample.profession" class="muted">· {{ d.sample.profession }}</span>
            <span v-if="d.sample.nationality" class="muted">· {{ d.sample.nationality }}</span>
            <span v-if="solverLabel(d)" class="solver-badge">{{ solverLabel(d) }}</span>
          </div>
          <div v-if="d.sample.archetype" style="margin-top:0.25rem;font-size:0.82rem;color:var(--muted)">
            {{ d.sample.archetype }}
          </div>
          <div v-if="skillTags(d.sample).length" style="margin-top:0.4rem;display:flex;gap:0.3rem;flex-wrap:wrap">
            <span v-for="sk in skillTags(d.sample)" :key="sk" class="badge">{{ sk }}</span>
          </div>
          <div style="margin-top:0.5rem;font-size:0.82rem;color:var(--muted)">
            <span
              v-for="(w, i) in d.workList.slice(0, 5)"
              :key="w.slug"
            >
              <RouterLink :to="`/media/${w.slug}`" style="color:var(--muted)">{{ w.title }}</RouterLink><!--
              --><span v-if="i < Math.min(d.workList.length, 5) - 1">, </span>
            </span>
            <span v-if="d.workList.length > 5" class="muted"> +{{ d.workList.length - 5 }} more</span>
          </div>
        </div>
      </div>
      <p v-if="!filtered.length" class="muted">No detectives found.</p>
    </div>
  </div>
</template>
