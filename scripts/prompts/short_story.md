# Prompt: Add a Short Story to Casefile Database

You are adding a **short story** to the Casefile Database.

## Your task

1. Look up the story on Wikidata if a dedicated entry exists (many short stories don't have one — that's fine).
2. If there is no Wikidata entry, set `wikidata_id: null` and write a `slug` in the form `"author-last-name-story-title-year"` (lowercase, hyphen-separated, no special chars).
3. Compile deaths, characters, and relevant tropes.
4. Write a JSON file and save to `temp/`. Run `uv run python scripts/ingest.py`.

## Schema

```json
[
  {
    "wikidata_id": null,
    "slug": "christie-witness-prosecution-1925",
    "title": "Witness for the Prosecution",
    "media_type": "short_story",
    "creator": "Agatha Christie",
    "year": 1925,
    "series_name": "Hercule Poirot",
    "tags": ["courtroom", "alibi"],
    "external_links": {
      "wikipedia_url": "https://en.wikipedia.org/wiki/Witness_for_the_Prosecution_(short_story)"
    },
    "notes": "Optional.",
    "persons": [
      { "name": "Emily French", "role_in_story": "victim" },
      { "name": "Leonard Vole", "role_in_story": "antagonist" }
    ],
    "deaths": [
      {
        "victim_name": "Emily French",
        "killer_name": "Leonard Vole",
        "cause": "CLUBBED",
        "death_type": "murder",
        "motive": "greed_inheritance",
        "tropes": ["alibi_trick", "least_likely_suspect"],
        "ordinal": 1,
        "is_central_death": true,
        "is_twist": true
      }
    ],
    "episodes": [],
    "cases": []
  }
]
```

## Slug rules (when `wikidata_id` is null)

- Format: `author-surname-story-title-year` — all lowercase, hyphens only.
- Strip articles (the, a, an) from the start of story titles.
- Examples:
  - `"christie-murder-roger-ackroyd-1926"`
  - `"chesterton-blue-cross-1910"`
  - `"doyle-speckled-band-1892"`

## Tips for short stories

- Golden Age short story collections (e.g. Poirot Investigates, The Adventures of Sherlock Holmes) should be entered as individual stories, not as a collection.
- Many short stories won't have Wikidata entries — use `null` and provide a slug.
- Check the story's Wikipedia page for publication year (first magazine appearance, not book collection date).
- `series_name` is the detective series (e.g. "Hercule Poirot", "Father Brown", "Sherlock Holmes").
