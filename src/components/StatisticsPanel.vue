<script setup>
import { computed } from 'vue'
import { computeStats, STATS_THRESHOLD } from '../composables/useStatistics.js'
import WaffleChart from './WaffleChart.vue'

const props = defineProps({
  entries: { type: Array, required: true },
  threshold: { type: Number, default: STATS_THRESHOLD },
  title: { type: String, default: 'Statistics' },
})

const stats = computed(() => computeStats(props.entries))
const enough = computed(() => stats.value.total >= props.threshold)
</script>

<template>
  <section class="stats-panel">
    <header class="stats-header">
      <h3 class="stats-title">{{ title }}</h3>
      <span class="muted">
        {{ stats.total }} death{{ stats.total === 1 ? '' : 's' }}
        <template v-if="stats.works">· {{ stats.works }} work{{ stats.works === 1 ? '' : 's' }}</template>
      </span>
    </header>

    <p v-if="!enough" class="muted stats-empty">
      Not enough data for statistics — needs at least {{ threshold }} deaths
      ({{ stats.total }} so far).
    </p>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-pill">
          <span class="stat-pill-num">{{ stats.total }}</span>
          <span class="stat-pill-label">Deaths</span>
        </div>
        <div class="stat-pill">
          <span class="stat-pill-num">{{ stats.causeSegments[0]?.label || '—' }}</span>
          <span class="stat-pill-label">Top method</span>
        </div>
        <div class="stat-pill">
          <span class="stat-pill-num">{{ stats.typeSegments[0]?.label || '—' }}</span>
          <span class="stat-pill-label">Most common type</span>
        </div>
        <div class="stat-pill">
          <span class="stat-pill-num">{{ stats.twistCount }}</span>
          <span class="stat-pill-label">Twist deaths</span>
        </div>
      </div>

      <div class="waffle-row">
        <div class="waffle-card">
          <h4>Methods</h4>
          <WaffleChart :segments="stats.causeSegments" />
        </div>
        <div class="waffle-card">
          <h4>Type of death</h4>
          <WaffleChart :segments="stats.typeSegments" />
        </div>
      </div>

      <div class="stats-lists">
        <div v-if="stats.topMotives.length">
          <h4>Top motives</h4>
          <ul class="top-list">
            <li v-for="m in stats.topMotives" :key="m.key">
              <span>{{ m.label }}</span><span>{{ m.count }}</span>
            </li>
          </ul>
        </div>
        <div v-if="stats.topMeans.length">
          <h4>Most-used means</h4>
          <ul class="top-list">
            <li v-for="m in stats.topMeans" :key="m.key">
              <span>{{ m.label }}</span><span>{{ m.count }}</span>
            </li>
          </ul>
        </div>
        <div v-if="stats.topTropes.length">
          <h4>Frequent tropes</h4>
          <ul class="top-list">
            <li v-for="t in stats.topTropes" :key="t.key">
              <span>{{ t.label }}</span><span>{{ t.count }}</span>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </section>
</template>
