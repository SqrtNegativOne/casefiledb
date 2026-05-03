# Casefile Database

A catalogued database of deaths in murder mystery media (books, TV, games, etc.), browsable as a static website.

## Stack

- Python (uv) — validation and ingestion scripts
- Pydantic — schema validation (`schema/models.py`)
- JSON — source of truth (`docs/site_data.json`)
- Static HTML/CSS/JS — website (`docs/`)

## How to add new media

1. Write a JSON file to `temp/` following the schema in `AI_SCHEMA.md`. The file must be a JSON array of media objects.
2. Run the ingest script:
   ```
   uv run python scripts/ingest.py
   ```
   This validates the data, appends it to `docs/site_data.json`, and deletes the temp file.
3. If validation fails, errors are printed and `temp/` is left intact for fixing.

## Schema

See `AI_SCHEMA.md` for the full field reference and an example. Key rules:
- Every `victim_name` and `killer_name` in a death must match a name in the `persons` array of the same media item.
- `cause`, `death_type`, and `motive` are controlled vocabularies — see `schema/models.py` for allowed values.

## File structure

```
docs/
  index.html        — website entry point (GitHub Pages)
  app.js            — all UI logic
  styles.css        — styles
  site_data.json    — the full dataset (generated, committed)
schema/
  models.py         — Pydantic models (single source of schema truth)
scripts/
  ingest.py         — validate temp/ → append to site_data.json → clear temp/
temp/               — drop new JSON files here before ingesting
AI_SCHEMA.md        — LLM-facing instructions for generating valid JSON
```

## Python conventions

- Use `uv run` for all Python invocations.
- No `import *`, no `print` outside scripts, no `pandas`, no `pip`.
- All functions need type hints and docstrings.
- Use `polars` if dataframe work is ever needed (not `pandas`).
