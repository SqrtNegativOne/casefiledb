<script setup>
import { computed } from 'vue'
import NoteHover from './NoteHover.vue'
import CauseBadge from './CauseBadge.vue'

const props = defineProps({
  item: Object,
  revealed: { type: Boolean, default: false },
})

const hasDeaths = computed(() => (props.item?.deaths?.length || 0) > 0)
const hasPersons = computed(() => (props.item?.persons?.length || 0) > 0)

function resolveName(persons, id) {
  if (!id) return null
  return persons?.find((p) => p.id === id)?.name ?? id
}
</script>

<template>
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
</template>
