# Casefile Database

A catalogued database of deaths in murder mystery media (books, TV, games, etc.), browsable as a static website.

## Stack

- Rust (`validator/`) — schema types + ingest binary (`cargo run --bin ingest`)
- JSON — source of truth (`public/site_data.json`)
- Vue 3 + Vite — frontend SPA (source in `src/`, built to `docs/`)
- Vue Router — hash-mode client-side routing (`/#/`, `/#/books`, etc.)

## Frontend development

```
npm install          # install deps (first time)
npm run dev          # dev server at localhost:5173
npm run build        # build to docs/ (deployed via GitHub Actions; docs/ is gitignored)
```

Pages: `/` Landing · `/deaths` · `/methods` · `/people` · `/media` · `/media/:slug` · `/author/:name` · `/show/:name` · `/game-series/:slug` · `/compare` · `/viz` · `/about` · `/colophon` · `/privacy`

## How to add new media

1. Write a JSON file to `temp/` following the schema in `AI_SCHEMA.md`. The file must be a JSON array of media objects.
2. Run the ingest binary:
   ```
   cargo run --bin ingest --manifest-path validator/Cargo.toml
   ```
   This validates the data, appends it to `public/site_data.json`, and deletes the temp file. Run `npm run build` afterward to rebuild the site.
3. If validation fails, errors are printed and `temp/` is left intact for fixing.

To validate `public/site_data.json` without modifying it:
   ```
   cargo run --bin check --manifest-path validator/Cargo.toml
   ```

To assign person IDs to all existing records (one-shot migration, idempotent):
   ```
   cargo run --bin migrate --manifest-path validator/Cargo.toml
   ```

## Schema

See `AI_SCHEMA.md` for the full field reference and an example. Key rules:
- `slug` is the primary key. For items with a real `wikidata_id`, slug equals wikidata_id and is auto-populated by ingest. Items with no Wikidata entry have `wikidata_id: null` and a hand-written slug (e.g. `monk-s01e01`).
- People are referenced by `id` (`victim_id` on a death, `person_id` on a killer). On input you may instead supply `victim_name` / killer `name`; ingest resolves these against the `persons` array of the **same scope** (top-level item, episode, or game case) and rewrites them to IDs. Unresolved names fail validation.
- Every `Person` gets an `id` (auto-assigned by `slugify(name)` with a numeric suffix on collision); IDs must be unique within their scope.
- Every `killer` entry requires `mens_rea` and `circumstance` (both controlled vocabularies).
- For `game` entries, deaths live inside `cases[*].deaths` — the top-level `deaths` list is empty. Count deaths by summing across cases.
- For `tv_show` entries, deaths live inside `episodes[*].deaths`.
- `cause`, `death_type`, `motive`, `mens_rea`, `circumstance`, `tropes`, `role_in_story`, and the `external_links` `*_status` fields are all controlled vocabularies — see `validator/src/models.rs` for the canonical enum definitions.
- `means` is required on every death except when `cause` is `OTHER` or `UNSTATED`.
- `motive` is required on every death except when `death_type` is `accident` or `natural_death` (i.e. required for `homicide`, `attempted_homicide`, `execution`, and `unstated`).
- Optional per-death fields: `ordinal`, `cause_detail`, `motive_detail`, `tropes`, `is_central_death`, `is_twist`, `chapter_or_act`, `notes`.
- Optional per-item fields beyond the basics: `tmdb_id`, `igdb_id`, `isbn`, `series_name`, `series_number`, `tags`, `external_links` (TVTropes / Wikipedia / Fandom / Goodreads / Steam / itch — each with a slug/id and a `_status` enum that ingest auto-sets to `EXISTS` when the slug is present).

## Data format

`public/site_data.json` is a **typed-collections object**, not a flat array:

```json
{
  "books":        [ … ],
  "games":        [ … ],
  "movies":       [ … ],
  "tv_episodes":  [ … ],
  "tv_shows":     [ … ],
  "short_stories":[ … ],
  "plays":        [ … ],
  "podcasts":     [ … ]
}
```

Each array holds only items of that `media_type`. The ingest binary automatically routes new items to the correct array. The frontend exposes `allItems` (a module-level Vue computed in `useData.js`) that merges all arrays for cross-type pages.

## File structure

```
src/
  main.js           — Vue app entry point
  router.js         — Vue Router (hash mode) route definitions
  App.vue           — root component (nav + router-view)
  styles/main.css   — detective theme CSS (all pages)
  composables/
    useData.js          — singleton data loader + shared helpers (deathCount, allDeaths…)
    useCoverImage.js    — lazy cover image fetch (Open Library / Wikidata P18)
    useCompletion.js    — user "completed" state (localStorage)
    useStatistics.js    — aggregate stats helpers
    gameSeries.js       — game-series grouping helpers
  components/
    SiteNav.vue              — hamburger nav shared across all pages
    PageFooter.vue           — site footer
    NoteHover.vue            — spoiler hover popover
    CauseBadge.vue           — colour-coded cause-of-death badge
    StatisticsPanel.vue      — stats summary panel
    WaffleChart.vue          — waffle chart viz
    SubItemSection.vue       — episode / case sub-list rendering
    MarkCompletedModal.vue   — "mark as completed" dialog
  pages/
    Landing.vue           — / (landing page)
    Home.vue              — /deaths (deaths table)
    Methods.vue           — /methods
    People.vue            — /people
    Media.vue             — /media (all items)
    MediaDetail.vue       — /media/:slug
    AuthorDetail.vue      — /author/:name
    ShowDetail.vue        — /show/:name
    GameSeriesDetail.vue  — /game-series/:slug
    Compare.vue           — /compare
    Viz.vue               — /viz
    About.vue             — /about
    Colophon.vue          — /colophon
    Privacy.vue           — /privacy
public/
  site_data.json    — the full dataset (source of truth, committed)
docs/               — Vite build output (committed for GitHub Pages)
validator/
  Cargo.toml        — Rust crate manifest
  src/
    models.rs       — Rust types (single source of schema truth)
    main.rs         — ingest binary
    check.rs        — validate-only binary
    migrate.rs      — one-shot person-ID assignment binary
scripts/
  validate_wikidata.py — check real Wikidata IDs against live Wikidata API
temp/               — drop new JSON files here before ingesting; also the home for one-time-use scripts (migrations, fixups, extractions) — never put these in scripts/
AI_SCHEMA.md        — LLM-facing instructions for generating valid JSON
```

## Python conventions

- Use `uv run` for all Python invocations.
- No `import *`, no `print` outside scripts, no `pandas`, no `pip`.
- All functions need type hints and docstrings.
- Use `polars` if dataframe work is ever needed (not `pandas`).
- Always open files with `encoding='utf-8'` — site_data.json contains non-ASCII characters.

## Shell environment

- The Bash tool runs `/usr/bin/bash` (POSIX). Use the PowerShell tool for Windows commands (`New-Item`, `Write-Host`, etc.).

## In conversations (very important)

Do not refer to any specific deaths or cases or plot twists or plot points of any pieces of media, to avoid giving anyone working on this project spoilers.
