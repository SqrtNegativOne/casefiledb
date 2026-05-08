# Dispatcher

You are the orchestrator for adding new media to casefiledb. You do not extract data yourself — you maintain a worklist and delegate.

## Single source of truth: `temp/worklist.json`

```json
{
  "items": [
    {
      "slug": "monk-s01e01",
      "media_type": "tv_episode",
      "title": "Mr. Monk and the Candidate",
      "url": "https://monk.fandom.com/wiki/Mr._Monk_and_the_Candidate",
      "recipe": "tv_show",
      "state": "pending",
      "attempts": 0,
      "error": null
    }
  ]
}
```

States: `pending` -> `scraped` -> `extracted` -> `ingested`, or `failed` (terminal until manually reset).

## Loop

### Initialization (run once if worklist is absent or empty)

0. If `temp/worklist.json` exists and is non-empty, skip to **Processing** below.
1. Check `prompts/ADD.md`. If it has content, expand each line into individual worklist entries by running the matching recipe's **planning steps** (episode discovery, book discovery, etc.) — no need to ask the user for items already named there. If ADD.md is also empty, ask the user what to add, then run the matching recipe.
2. Write all discovered entries to `temp/worklist.json` with `state: pending`.
3. **Stop here. Do not begin processing in the same turn.**

### Processing

4. Read `temp/worklist.json`. Process entries in this order, one at a time:
   - `pending` -> run `scripts/scrape_media.py` (use `fetch` if `url` is set, else `find` with the recipe's hints). On success set `state: scraped`. On failure increment `attempts`; if `attempts >= 2` set `state: failed` with the error.
   - `scraped` -> spawn one subagent with `prompts/extract.md`. Pass it the slug. On success (subagent wrote `temp/<slug>.json`) set `state: extracted`. On failure same retry rule.
   - `extracted` -> run `cargo run --bin ingest --manifest-path validator/Cargo.toml`. If it succeeds for this slug, set `state: ingested`. If validation fails, capture stderr into `error` and set `state: failed`.
5. Stop when no `pending`/`scraped`/`extracted` entries remain. Print a one-line summary: `N ingested, M failed`.

## Rules

- Never read `temp/raw/*.txt` yourself — that is the subagent's job. Keep your context clean.
- Never edit `public/site_data.json` directly. The Rust ingest binary owns it.
- Idempotent: re-running the dispatcher must be safe. Skip non-actionable states.
- Bounded retries (2). On `failed`, move on; the user triages later.
- One subagent at a time per slug. Do not batch extraction.
