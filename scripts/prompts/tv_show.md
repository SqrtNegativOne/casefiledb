# Prompt: Add a TV Show to Casefile Database

You are adding a **TV show** (one or more seasons) to the Casefile Database.

## Your task

1. Look up the show on Wikidata to get its ID.
2. Find a list of all episodes (Wikipedia or Fandom wiki).
3. For each episode: find all deaths, characters involved, and the killer.
4. Write a JSON file and save to `temp/`. Run `uv run python scripts/ingest.py`.

## Important structural rule

For a `tv_show`, **deaths go inside each episode** — the top-level `deaths` array is always empty.
Each episode has its own `persons` and `deaths` arrays, scoped to that episode only.

## Schema

```json
[
  {
    "wikidata_id": "Q...",
    "title": "Show Title",
    "media_type": "tv_show",
    "creator": "Creator Name",
    "year": 1989,
    "tags": ["procedural", "detective"],
    "external_links": {
      "fandom_url": "https://showname.fandom.com/wiki/Show_Title",
      "tvtropes_url": "https://tvtropes.org/pmwiki/pmwiki.php/Series/...",
      "wikipedia_url": "https://en.wikipedia.org/wiki/..."
    },
    "notes": "Optional.",
    "persons": [],
    "deaths": [],
    "cases": [],
    "episodes": [
      {
        "wikidata_id": "Q...",
        "title": "Episode Title",
        "season": 1,
        "episode_number": 1,
        "year": 1989,
        "tags": [],
        "notes": "Optional.",
        "persons": [
          { "name": "Victim Name", "role_in_story": "victim" },
          { "name": "Killer Name", "role_in_story": "antagonist" },
          { "name": "Detective Name", "role_in_story": "detective" }
        ],
        "deaths": [
          {
            "victim_name": "Victim Name",
            "killer_name": "Killer Name",
            "cause": "STABBED",
            "death_type": "murder",
            "motive": "greed_financial",
            "tropes": ["howcatchem"],
            "ordinal": 1,
            "is_central_death": true,
            "is_twist": false
          }
        ]
      }
    ]
  }
]
```

## Tips for TV shows

- If adding multiple seasons, include all episodes in a single object.
- For procedural shows (Columbo, Monk, Poirot), set `tropes: ["howcatchem"]` on the central murder since the killer is usually shown committing the crime at the start.
- `wikidata_id` on individual episodes is optional but helpful when it exists.
- The show-level `slug` derives from the show's `wikidata_id`. Episode URLs use `?id=<show_wikidata_id>&ep=<index>`.
- When a show has a regular detective character, list them in the episode's `persons` with `role_in_story: "detective"`.
- Use `is_twist: true` when a death's circumstances or killer are a major surprise reveal.

## Fandom wiki strategy

The show's Fandom wiki (e.g. `monk.fandom.com`) usually has per-episode articles listing:
- Victim name
- Cause of death
- Killer name
- Brief plot summary

Use `scripts/scrape_fandom.py <fandom_episode_url>` for a quick character/death extract.
