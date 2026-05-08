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

0. Create `temp/worklist.json` if it doesn't exist, using the list given in `prompts/ADD.md`.
1. Read `temp/worklist.json`. If missing or empty, ask the user what to add and run the matching recipe in `prompts/recipes/*.md` to populate it. Stop after planning — do not extract in the same turn.
2. Otherwise, process entries in this order, one at a time:
   - `pending` -> run `scripts/scrape_media.py` (use `fetch` if `url` is set, else `find` with the recipe's hints). On success set `state: scraped`. On failure increment `attempts`; if `attempts >= 2` set `state: failed` with the error.
   - `scraped` -> spawn one subagent with `prompts/extract.md`. Pass it the slug. On success (subagent wrote `temp/<slug>.json`) set `state: extracted`. On failure same retry rule.
   - `extracted` -> run `cargo run --bin ingest --manifest-path validator/Cargo.toml`. If it succeeds for this slug, set `state: ingested`. If validation fails, capture stderr into `error` and set `state: failed`.
3. Stop when no `pending`/`scraped`/`extracted` entries remain. Print a one-line summary: `N ingested, M failed`.

## Rules

- Never read `temp/raw/*.txt` yourself — that is the subagent's job. Keep your context clean.
- Never edit `public/site_data.json` directly. The Rust ingest binary owns it.
- Idempotent: re-running the dispatcher must be safe. Skip non-actionable states.
- Bounded retries (2). On `failed`, move on; the user triages later.
- One subagent at a time per slug. Do not batch extraction.
