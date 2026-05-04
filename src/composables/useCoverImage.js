import { ref, watch } from 'vue'

const cache = new Map()

/**
 * Lazily fetches a cover image URL for a media item.
 * Tries Open Library (ISBN) then Wikidata P18.
 * Returns a ref that resolves to a URL string or null.
 */
export function useCoverImage(mediaRef) {
  const url = ref(null)

  watch(
    mediaRef,
    async (media) => {
      if (!media) { url.value = null; return }
      const key = media.slug
      if (cache.has(key)) { url.value = cache.get(key); return }

      // Open Library for books with ISBN
      if (media.isbn) {
        const imgUrl = `https://covers.openlibrary.org/b/isbn/${media.isbn}-L.jpg`
        const ok = await imgExists(imgUrl)
        if (ok) { cache.set(key, imgUrl); url.value = imgUrl; return }
      }

      // Wikidata P18 → Wikimedia Commons
      const wdId = media.wikidata_id
      if (wdId && wdId.startsWith('Q')) {
        try {
          const res = await fetch(
            `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=${wdId}&props=claims&format=json&origin=*`
          )
          const json = await res.json()
          const p18 = json.entities?.[wdId]?.claims?.P18?.[0]?.mainsnak?.datavalue?.value
          if (p18) {
            const imgUrl =
              `https://commons.wikimedia.org/wiki/Special:FilePath/` +
              `${encodeURIComponent(p18.replace(/ /g, '_'))}?width=320`
            cache.set(key, imgUrl)
            url.value = imgUrl
            return
          }
        } catch (_) {}
      }

      cache.set(key, null)
      url.value = null
    },
    { immediate: true }
  )

  return url
}

function imgExists(src) {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => resolve(img.naturalWidth > 1)
    img.onerror = () => resolve(false)
    img.src = src
  })
}
