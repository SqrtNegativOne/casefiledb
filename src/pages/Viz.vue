<script setup>
import { ref, onMounted, watch } from 'vue'
import { useData, allItems, allDeaths } from '../composables/useData.js'

const { loaded, ensureLoaded } = useData()
const vizWrap = ref(null)

onMounted(async () => {
  await ensureLoaded()
  render()
})

watch(loaded, (v) => { if (v) render() })

const NS = 'http://www.w3.org/2000/svg'
function el(tag, attrs = {}) {
  const e = document.createElementNS(NS, tag)
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v)
  return e
}
function txt(content, attrs = {}) {
  const e = el('text', attrs)
  e.textContent = content
  return e
}

function buildYearChart() {
  const yearCounts = {}
  for (const item of allItems.value) {
    const deaths = allDeaths(item)
    if (!deaths.length || !item.year) continue
    yearCounts[item.year] = (yearCounts[item.year] || 0) + deaths.length
  }
  const years = Object.keys(yearCounts).map(Number).sort((a, b) => a - b)
  if (!years.length) return null

  const counts = years.map((y) => yearCounts[y])
  const maxCount = Math.max(...counts)
  const W = 860, H = 260, padL = 40, padR = 20, padT = 30, padB = 50
  const chartW = W - padL - padR, chartH = H - padT - padB
  const barW = Math.max(2, Math.floor(chartW / years.length) - 2)
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;height:auto;overflow:visible' })

  for (let i = 0; i <= 4; i++) {
    const y = padT + chartH - (i / 4) * chartH
    svg.appendChild(el('line', { class: 'gridline', x1: padL, y1: y, x2: padL + chartW, y2: y }))
    if (i > 0) svg.appendChild(txt(Math.round((i / 4) * maxCount), { class: 'axis-label', x: padL - 6, y: y + 4, 'text-anchor': 'end' }))
  }

  const xStep = chartW / years.length
  years.forEach((year, i) => {
    const count = yearCounts[year]
    const barH = (count / maxCount) * chartH
    const x = padL + i * xStep + (xStep - barW) / 2
    const y = padT + chartH - barH
    const rect = el('rect', { class: 'bar', x, y, width: barW, height: barH, rx: 2 })
    const title = el('title'); title.textContent = `${year}: ${count} deaths`
    rect.appendChild(title)
    svg.appendChild(rect)

    const err = Math.max(1, Math.round(Math.sqrt(count)))
    const errPx = (err / maxCount) * chartH
    const cx = x + barW / 2, capW = Math.max(3, barW * 0.4)
    svg.appendChild(el('line', { class: 'error-bar', x1: cx, y1: y - errPx, x2: cx, y2: y + errPx }))
    svg.appendChild(el('line', { class: 'error-cap', x1: cx - capW / 2, y1: y - errPx, x2: cx + capW / 2, y2: y - errPx }))
    svg.appendChild(el('line', { class: 'error-cap', x1: cx - capW / 2, y1: y + errPx, x2: cx + capW / 2, y2: y + errPx }))
  })

  const labelEvery = years.length > 40 ? 10 : years.length > 20 ? 5 : 1
  years.forEach((year, i) => {
    if (i % labelEvery !== 0) return
    const cx = padL + i * xStep + xStep / 2
    svg.appendChild(txt(year, { class: 'axis-label', x: cx, y: padT + chartH + 18, 'text-anchor': 'middle' }))
  })
  svg.appendChild(el('line', { stroke: 'var(--border)', x1: padL, y1: padT, x2: padL, y2: padT + chartH }))
  svg.appendChild(el('line', { stroke: 'var(--border)', x1: padL, y1: padT + chartH, x2: padL + chartW, y2: padT + chartH }))
  return svg
}

function buildCausesChart() {
  const counts = {}
  for (const item of allItems.value) {
    for (const d of allDeaths(item)) {
      if (d.cause) counts[d.cause] = (counts[d.cause] || 0) + 1
    }
  }
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1])
  const total = sorted.reduce((n, [, c]) => n + c, 0)
  const maxCount = sorted[0]?.[1] ?? 1
  const rowH = 26, padL = 110, padR = 60, padT = 10, padB = 10, barAreaW = 520
  const W = padL + barAreaW + padR, H = padT + rowH * sorted.length + padB
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;max-width:700px;height:auto' })

  sorted.forEach(([cause, count], i) => {
    const y = padT + i * rowH, barW = (count / maxCount) * barAreaW, cy = y + rowH / 2 + 5
    svg.appendChild(txt(cause.charAt(0) + cause.slice(1).toLowerCase(), { class: 'axis-label', x: padL - 8, y: cy, 'text-anchor': 'end', 'dominant-baseline': 'middle' }))
    const rect = el('rect', { class: 'bar', x: padL, y: y + 4, width: Math.max(2, barW), height: rowH - 8, rx: 3 })
    const title = el('title'); title.textContent = `${cause}: ${count} (${((count / total) * 100).toFixed(1)}%)`
    rect.appendChild(title); svg.appendChild(rect)
    svg.appendChild(txt(`${count}`, { x: padL + barW + 6, y: cy, 'dominant-baseline': 'middle', 'font-size': '11', fill: 'var(--muted)' }))
  })
  return svg
}

function buildTypeChart() {
  const counts = {}, workCounts = {}
  for (const item of allItems.value) {
    const t = item.media_type || 'unknown'
    workCounts[t] = (workCounts[t] || 0) + 1
    counts[t] = (counts[t] || 0) + allDeaths(item).length
  }
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1])
  const maxCount = sorted[0]?.[1] ?? 1
  const rowH = 30, padL = 90, padR = 80, padT = 10, padB = 10, barAreaW = 480
  const W = padL + barAreaW + padR, H = padT + rowH * sorted.length + padB
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, style: 'width:100%;max-width:680px;height:auto' })

  sorted.forEach(([type, count], i) => {
    const y = padT + i * rowH, barW = (count / maxCount) * barAreaW, cy = y + rowH / 2 + 4
    const works = workCounts[type] || 0, perWork = works > 0 ? (count / works).toFixed(1) : '0'
    svg.appendChild(txt(type, { class: 'axis-label', x: padL - 8, y: cy, 'text-anchor': 'end', 'dominant-baseline': 'middle' }))
    svg.appendChild(el('rect', { class: 'bar-secondary', x: padL, y: y + 6, width: barAreaW, height: rowH - 12, rx: 3 }))
    const rect = el('rect', { class: 'bar', x: padL, y: y + 6, width: Math.max(2, barW), height: rowH - 12, rx: 3 })
    const title = el('title'); title.textContent = `${type}: ${count} deaths · ${perWork}/work`
    rect.appendChild(title); svg.appendChild(rect)
    svg.appendChild(txt(`${count} · ${perWork}/work`, { x: padL + barAreaW + 8, y: cy, 'dominant-baseline': 'middle', 'font-size': '11', fill: 'var(--muted)' }))
  })
  return svg
}

function card(title, subtitle, svgEl, legendHtml = '') {
  const div = document.createElement('div')
  div.className = 'viz-card'
  div.innerHTML = `<h2>${title}</h2><p class="viz-subtitle">${subtitle}</p>`
  div.appendChild(svgEl)
  if (legendHtml) div.innerHTML += legendHtml
  return div
}

function render() {
  if (!vizWrap.value || !allItems.value.length) return
  vizWrap.value.innerHTML = ''
  const yearSvg = buildYearChart()
  if (yearSvg) {
    vizWrap.value.appendChild(card(
      'Deaths per year',
      'Total recorded deaths by publication / air year. Error bars show ±√n.',
      yearSvg,
      '<div class="viz-legend"><span><span class="legend-dot"></span> deaths</span><span style="color:var(--muted);font-size:0.78rem">error bars: ±√n</span></div>'
    ))
  }
  vizWrap.value.appendChild(card('Deaths by method', 'All recorded death causes across the database.', buildCausesChart()))
  vizWrap.value.appendChild(card('Deaths by media type', 'Total deaths and per-work average, broken down by format.', buildTypeChart()))
}
</script>

<template>
  <div ref="vizWrap" class="viz-wrap">
    <p class="muted">Loading…</p>
  </div>
</template>
