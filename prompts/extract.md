# Extractor (subagent prompt)

You convert one scraped media page into one schema-valid JSON file.

## Inputs

- `<slug>` — passed by the dispatcher.
- `temp/raw/<slug>.txt` — pre-scraped plaintext with section headers and an Infobox section.
- `temp/raw/<slug>.json` — the same content as structured data (infobox, tables, sections). Use whichever is easier.
- `AI_SCHEMA.md` — the **only** schema reference. It defines field names, controlled vocabularies, required fields, conditional rules, and an example. The Rust validator at `validator/src/models.rs` is canonical but you should not need it; if `AI_SCHEMA.md` is silent on something, that something is optional.

## Output

Exactly one file: `temp/<slug>.json`. It must be a JSON array (even if it contains one item), per the ingest binary's contract.

## Rules

- Try not to browse the web or call other tools beyond `Read` and `Write`.
- Do not modify `temp/raw/*`, `public/site_data.json`, `AI_SCHEMA.md`, or anything outside `temp/`.
- Use `null` for unknown optional fields. Do not invent data.
- Every `victim_name`/`killer_name` in `deaths` must appear in the matching `persons` array of the same scope (top-level / episode / case).
- For `tv_episode` items: produce one media object whose `media_type` is `tv_episode`.
- For `tv_show` items: produce one media object whose `episodes` array contains all episode objects.
- For `game` items: deaths live inside `cases[*].deaths`; the top-level `deaths` array is empty.
- Slug rule: if a real `wikidata_id` exists in the source, set `wikidata_id` to it and let ingest derive the slug. Otherwise set `wikidata_id: null` and use the slug the dispatcher provided.

## Enum casing (critical)

All enum fields use **PascalCase** exactly as shown in `AI_SCHEMA.md`. For example:
- `cause`: `"Poisoned"`, `"Shot"`, `"Unknown"`, `"TornApart"` — NOT `"POISONED"`, `"SHOT"`, `"UNKNOWN"`
- `death_type`: `"Homicide"`, `"AttemptedHomicide"`, `"Accident"`, `"NaturalDeath"` — NOT `"homicide"`, `"attempted_homicide"`
- `motive`: `"Revenge"`, `"GreedFinancial"`, `"Concealment"` — NOT `"revenge"`, `"greed_financial"`
- `mens_rea`: `"Purposely"`, `"Recklessly"` — NOT `"purposely"`, `"recklessly"`
- `circumstance`: `"Neutral"`, `"Justified"` — NOT `"neutral"`, `"justified"`
- `tropes`: `"Whodunit"`, `"LockedRoom"`, `"ClosedCircle"` — NOT `"whodunit"`, `"locked_room"`
- `role_in_story`: `"Victim"`, `"Detective"`, `"Antagonist"` — NOT `"victim"`, `"detective"`
- `media_type`: `"TvEpisode"`, `"Book"`, `"Movie"` — NOT `"tv_episode"`, `"book"`, `"movie"`

## On uncertainty

If the page is ambiguous (e.g. cause of death not stated), pick the closest controlled-vocab value defined in `AI_SCHEMA.md` and set `cause: "Unknown"` with `means: "unknown"` rather than guessing. Do not add free-text fields the schema does not define.

## Done

Write the file and exit. Do not print explanations. The dispatcher will run the validator.
