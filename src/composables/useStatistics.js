/**
 * Modular statistics: take a flat list of death events (with their `persons`
 * scope attached) and produce a summary. The same shape powers Authors,
 * Shows and Game Series pages.
 *
 * Each entry must look like:
 *   { death, media, persons, scope?: { kind, title } }
 * where `persons` is the array used to resolve victim_id / killer person_id.
 */

export const STATS_THRESHOLD = 12

export const CAUSE_COLORS = {
  POISONED: '#27ae60',
  SHOT: '#c0392b',
  STABBED: '#922b21',
  STRANGLED: '#7d3c98',
  DROWNED: '#2471a3',
  BURNED: '#e67e22',
  CLUBBED: '#7e5109',
  HANGED: '#6e2f1a',
  FELL: '#95a5a6',
  CRUSHED: '#5d6d7e',
  SUFFOCATED: '#616a6b',
  EXPLODED: '#d35400',
  ELECTROCUTED: '#f1c40f',
  FROZEN: '#2e86c1',
  ILLNESS: '#76b041',
  EATEN: '#8b4513',
  TORN_APART: '#641e16',
  VEHICULAR: '#7f8c8d',
  UNSTATED: '#bdc3c7',
  OTHER: '#a04000',
}

export const TYPE_LABELS = {
  murder: 'Murder',
  suicide: 'Suicide',
  manslaughter: 'Manslaughter',
  attempted_murder: 'Attempted murder',
  natural_death: 'Natural death',
  accident: 'Accident',
  execution: 'Execution',
  unknown: 'Unstated',
}

export const TYPE_COLORS = {
  murder: '#c0392b',
  suicide: '#7d3c98',
  manslaughter: '#e67e22',
  attempted_murder: '#f1c40f',
  natural_death: '#76b041',
  accident: '#5d6d7e',
  execution: '#641e16',
  unknown: '#bdc3c7',
}

export function causeLabel(c) {
  if (!c) return 'Unstated'
  return c.charAt(0) + c.slice(1).toLowerCase().replace(/_/g, ' ')
}

export function motiveLabel(m) {
  if (!m) return '—'
  return m.charAt(0).toUpperCase() + m.slice(1).replace(/_/g, ' ')
}

/**
 * Bucket a death into a high-level type category.
 * Suicide = homicide whose only killer is the victim themselves.
 * Manslaughter = homicide with any killer's mens_rea recklessly/negligently.
 */
export function categorizeDeath(death) {
  const dt = death.death_type
  if (dt === 'attempted_homicide') return 'attempted_murder'
  if (dt === 'execution') return 'execution'
  if (dt === 'accident') return 'accident'
  if (dt === 'natural_death') return 'natural_death'
  if (dt === 'homicide') {
    const killers = death.killers || []
    if (killers.length && killers.every((k) => k.person_id && k.person_id === death.victim_id)) {
      return 'suicide'
    }
    if (killers.some((k) => k.mens_rea === 'recklessly' || k.mens_rea === 'negligently')) {
      return 'manslaughter'
    }
    return 'murder'
  }
  return 'unknown'
}

function topN(map, n) {
  return [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, n)
}

/**
 * Compute statistics from an array of entries.
 * @param {Array} entries  [{ death, media, persons, scope? }]
 */
export function computeStats(entries) {
  const total = entries.length
  const causeMap = new Map()
  const typeMap = new Map()
  const motiveMap = new Map()
  const meansMap = new Map()
  const tropeMap = new Map()
  const works = new Set()
  let twistCount = 0
  let centralCount = 0

  for (const { death, media } of entries) {
    if (media?.slug) works.add(media.slug)
    const cause = death.cause || 'UNSTATED'
    causeMap.set(cause, (causeMap.get(cause) || 0) + 1)
    const cat = categorizeDeath(death)
    typeMap.set(cat, (typeMap.get(cat) || 0) + 1)
    if (death.motive) motiveMap.set(death.motive, (motiveMap.get(death.motive) || 0) + 1)
    if (death.means && death.means !== 'unmentioned' && death.means !== 'needs_review') {
      const key = String(death.means).toLowerCase()
      meansMap.set(key, (meansMap.get(key) || 0) + 1)
    }
    for (const t of (death.tropes || [])) tropeMap.set(t, (tropeMap.get(t) || 0) + 1)
    if (death.is_twist) twistCount++
    if (death.is_central_death) centralCount++
  }

  const causeSegments = [...causeMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([cause, count]) => ({
      key: cause,
      label: causeLabel(cause),
      count,
      color: CAUSE_COLORS[cause] || '#888',
    }))

  const typeSegments = [...typeMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([k, count]) => ({
      key: k,
      label: TYPE_LABELS[k] || k,
      count,
      color: TYPE_COLORS[k] || '#888',
    }))

  return {
    total,
    works: works.size,
    twistCount,
    centralCount,
    causeSegments,
    typeSegments,
    topMotives: topN(motiveMap, 6).map(([k, count]) => ({ key: k, label: motiveLabel(k), count })),
    topMeans: topN(meansMap, 6).map(([k, count]) => ({ key: k, label: k, count })),
    topTropes: topN(tropeMap, 6).map(([k, count]) => ({ key: k, label: k.replace(/_/g, ' '), count })),
  }
}

/** Flatten an array of media items into death entries. */
export function entriesFromMedia(items) {
  const out = []
  for (const m of items) {
    for (const d of (m.deaths || [])) {
      out.push({ death: d, media: m, persons: m.persons || [], scope: null })
    }
    for (const ep of (m.episodes || [])) {
      for (const d of (ep.deaths || [])) {
        out.push({ death: d, media: m, persons: ep.persons || [], scope: { kind: 'episode', title: ep.title, ref: ep } })
      }
    }
    for (const c of (m.cases || [])) {
      for (const d of (c.deaths || [])) {
        out.push({ death: d, media: m, persons: c.persons || [], scope: { kind: 'case', title: c.title, ref: c } })
      }
    }
  }
  return out
}
