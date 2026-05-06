/**
 * Game series are not stored in site_data.json — they are a derived view
 * that groups existing `game` items together. Add new groups here.
 *
 * Each entry has:
 *   slug      — URL slug used in /game-series/:slug
 *   name      — display name
 *   matches   — function (game) => boolean
 *   description — optional blurb
 */

export const GAME_SERIES = [
  {
    slug: 'ace-attorney',
    name: 'Ace Attorney',
    description: 'The complete Ace Attorney franchise.',
    matches: (g) => g.series_name === 'Ace Attorney',
  },
  {
    slug: 'original-ace-attorney-trilogy',
    name: 'Original Ace Attorney Trilogy',
    description: 'Phoenix Wright: Ace Attorney through Trials and Tribulations (1–3).',
    matches: (g) => g.series_name === 'Ace Attorney' && Number(g.series_number) >= 1 && Number(g.series_number) <= 3,
  },
  {
    slug: 'apollo-justice-trilogy',
    name: 'Apollo Justice Trilogy',
    description: 'Apollo Justice through Spirit of Justice (4–6).',
    matches: (g) => g.series_name === 'Ace Attorney' && Number(g.series_number) >= 4 && Number(g.series_number) <= 6,
  },
  {
    slug: 'ace-attorney-investigations-duology',
    name: 'Ace Attorney Investigations Duology',
    description: 'The two Miles Edgeworth–led spin-off games.',
    matches: (g) => /^Ace Attorney Investigations/i.test(g.title || ''),
  },
  {
    slug: 'danganronpa-trilogy',
    name: 'Danganronpa Trilogy',
    description: 'The three mainline Danganronpa games.',
    matches: (g) => g.series_name === 'Danganronpa',
  },
]

export function findGameSeries(slug) {
  return GAME_SERIES.find((s) => s.slug === slug) || null
}

export function gamesInSeries(series, allGames) {
  if (!series) return []
  return allGames.filter(series.matches)
}
