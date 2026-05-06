import { shallowRef, ref, computed } from 'vue'

const EMPTY = {
  books: [], games: [], movies: [], tv_episodes: [], tv_shows: [],
  short_stories: [], plays: [], podcasts: [],
}

const _data = shallowRef(EMPTY)
const _loaded = ref(false)
const _loading = ref(false)

export const allItems = computed(() => [
  ...(_data.value.books || []),
  ...(_data.value.games || []),
  ...(_data.value.movies || []),
  ...(_data.value.tv_episodes || []),
  ...(_data.value.tv_shows || []),
  ...(_data.value.short_stories || []),
  ...(_data.value.plays || []),
  ...(_data.value.podcasts || []),
])

export function useData() {
  async function ensureLoaded() {
    if (_loaded.value || _loading.value) return
    _loading.value = true
    try {
      _data.value = await fetch('./site_data.json').then((r) => r.json())
      _loaded.value = true
    } finally {
      _loading.value = false
    }
  }

  return { data: _data, allItems, loaded: _loaded, loading: _loading, ensureLoaded }
}

/** Sum deaths across all scopes of a media item. */
export function deathCount(media) {
  return (
    (media.deaths || []).length +
    (media.cases || []).reduce((n, c) => n + (c.deaths || []).length, 0) +
    (media.episodes || []).reduce((n, e) => n + (e.deaths || []).length, 0)
  )
}

/** Flatten all deaths from all scopes. */
export function allDeaths(media) {
  return [
    ...(media.deaths || []),
    ...(media.episodes || []).flatMap((e) => e.deaths || []),
    ...(media.cases || []).flatMap((c) => c.deaths || []),
  ]
}

/** Flatten all persons from all scopes. */
export function allPersons(media) {
  return [
    ...(media.persons || []),
    ...(media.episodes || []).flatMap((e) => e.persons || []),
    ...(media.cases || []).flatMap((c) => c.persons || []),
  ]
}

export function hasTwist(media) {
  return allDeaths(media).some((d) => d.is_twist)
}

/** Resolve a person ID to their display name within a scope's persons array. */
export function resolveName(persons, id) {
  if (!id) return null
  return persons?.find((p) => p.id === id)?.name ?? id
}
