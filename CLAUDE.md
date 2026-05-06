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
npm run build        # build to docs/ (commits this for GitHub Pages)
```

Pages: `/` Deaths · `/authors` · `/episodes` · `/methods` · `/detectives` · `/games` · `/books` · `/compare` · `/viz` · `/media/:slug`

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

## Schema

See `AI_SCHEMA.md` for the full field reference and an example. Key rules:
- `slug` is the primary key. For items with a real `wikidata_id`, slug equals wikidata_id and is auto-populated by ingest. Items with no Wikidata entry have `wikidata_id: null` and a hand-written slug (e.g. `monk-s01e01`).
- Every `victim_name` and `killer_name` in a death must match a name in the `persons` array of the **same scope** (top-level item, episode, or game case).
- For `game` entries, deaths live inside `cases[*].deaths` — the top-level `deaths` list is empty. Count deaths by summing across cases.
- For `tv_show` entries, deaths live inside `episodes[*].deaths`.
- `cause`, `death_type`, and `motive` are controlled vocabularies — see `validator/src/models.rs` for the canonical enum definitions.
- `means` is required on every death except when `cause` is `OTHER`. When `cause` is `UNKNOWN`, set `means: "unknown"`.
- `motive` is required on every death except when `death_type` is `accident` or `natural_death`.

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
    useData.js      — singleton data loader + shared helpers (deathCount, allDeaths…)
    useCoverImage.js — lazy cover image fetch (Open Library / Wikidata P18)
  components/
    SiteNav.vue     — hamburger nav shared across all pages
    NoteHover.vue   — spoiler hover popover
    CauseBadge.vue  — colour-coded cause-of-death badge
  pages/
    Home.vue        — deaths table (/)
    Authors.vue     — /authors
    Episodes.vue    — /episodes
    Methods.vue     — /methods
    Detectives.vue  — /detectives (all detective characters)
    Games.vue       — /games
    Books.vue       — /books
    Compare.vue     — /compare
    Viz.vue         — /viz
    MediaDetail.vue — /media/:slug
public/
  site_data.json    — the full dataset (source of truth, committed)
docs/               — Vite build output (committed for GitHub Pages)
validator/
  Cargo.toml        — Rust crate manifest
  src/
    models.rs       — Rust types (single source of schema truth)
    main.rs         — ingest binary
    check.rs        — validate-only binary
scripts/
  validate_wikidata.py — check real Wikidata IDs against live Wikidata API
temp/               — drop new JSON files here before ingesting
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
