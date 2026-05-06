import { ref } from 'vue'

const STORAGE_KEY = 'casefile-completion'
const MNESIA_KEY = 'casefile-mnesia'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return new Set()
    return new Set(JSON.parse(raw))
  } catch {
    return new Set()
  }
}

export const completed = ref(load())
export const mnesia = ref(localStorage.getItem(MNESIA_KEY) === '1')

function persist(set) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify([...set])) } catch {}
}

export function mediaKey(slug)   { return `media:${slug}` }
export function authorKey(name)  { return `author:${name}` }
export function showKey(name)    { return `show:${name}` }

export function addKey(key) {
  const next = new Set(completed.value)
  next.add(key)
  completed.value = next
  persist(next)
}

export function removeKey(key) {
  const next = new Set(completed.value)
  next.delete(key)
  completed.value = next
  persist(next)
}

export function setMnesia(v) {
  mnesia.value = !!v
  try { localStorage.setItem(MNESIA_KEY, v ? '1' : '0') } catch {}
}

/**
 * True when the user has elected to see spoilers for this media item —
 * either because Mnesia mode is on, the work itself is marked completed,
 * its author is marked completed, or its parent show is marked completed.
 */
export function canReveal(media) {
  if (!media) return false
  if (mnesia.value) return true
  const set = completed.value
  if (set.has(mediaKey(media.slug))) return true
  if (media.creator && set.has(authorKey(media.creator))) return true
  if (media.media_type === 'tv_show' && set.has(showKey(media.title))) return true
  if (media.media_type === 'tv_episode') {
    const showName = media.series_name || media.title
    if (set.has(showKey(showName))) return true
  }
  return false
}

export function useCompletion() {
  return { completed, mnesia, addKey, removeKey, setMnesia, canReveal }
}
