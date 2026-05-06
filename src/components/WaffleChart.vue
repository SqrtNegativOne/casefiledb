<script setup>
import { computed } from 'vue'

const props = defineProps({
  segments: { type: Array, required: true }, // [{ key, label, count, color }]
  cells: { type: Number, default: 100 },
  cols: { type: Number, default: 10 },
})

const total = computed(() => props.segments.reduce((n, s) => n + s.count, 0))

// Map segments to integer cell counts that sum to props.cells, using
// largest-remainder rounding so small segments still get a single cell when
// they round to ≥0.5.
const cellList = computed(() => {
  if (total.value === 0) return []
  const target = props.cells
  const items = props.segments.map((s) => {
    const raw = (s.count / total.value) * target
    return { ...s, raw, floor: Math.floor(raw), rem: raw - Math.floor(raw) }
  })
  let used = items.reduce((n, it) => n + it.floor, 0)
  let remaining = target - used
  // Give a remainder cell to the segments with the largest fractional part,
  // skipping any whose count is 0.
  const order = [...items].filter((it) => it.count > 0).sort((a, b) => b.rem - a.rem)
  let i = 0
  while (remaining > 0 && order.length) {
    order[i % order.length].floor++
    remaining--
    i++
  }
  // Build flat cell list, grouping by segment in original order.
  const cells = []
  for (const it of items) {
    for (let k = 0; k < it.floor; k++) {
      cells.push({ color: it.color, label: `${it.label}: ${it.count}` })
    }
  }
  return cells
})
</script>

<template>
  <div class="waffle-wrap" v-if="total > 0">
    <div class="waffle-grid" :style="{ '--waffle-cols': cols }">
      <span
        v-for="(c, i) in cellList"
        :key="i"
        class="waffle-cell"
        :style="{ background: c.color }"
        :title="c.label"
      />
    </div>
    <ul class="waffle-legend">
      <li v-for="s in segments" :key="s.key">
        <span class="waffle-swatch" :style="{ background: s.color }" />
        <span class="waffle-label">{{ s.label }}</span>
        <span class="waffle-count muted">
          {{ s.count }}
          <span v-if="total">({{ ((s.count / total) * 100).toFixed(0) }}%)</span>
        </span>
      </li>
    </ul>
  </div>
  <div v-else class="muted">No data.</div>
</template>
