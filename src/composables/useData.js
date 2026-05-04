import { shallowRef, ref } from 'vue'

const _data = shallowRef([])
const _loaded = ref(false)
const _loading = ref(false)

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

  return { data: _data, loaded: _loaded, loading: _loading, ensureLoaded }
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
