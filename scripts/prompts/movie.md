# Prompt: Add a Movie to Casefile Database

You are adding a **movie** to the Casefile Database.

## Your task

1. Look up the movie on Wikidata (wikidata.org) and TMDB (themoviedb.org).
2. Find the TV Tropes page and Wikipedia article.
3. List all deaths with full spoilers — include killers and motives.
4. Write a JSON file and save to `temp/`. Run `uv run python scripts/ingest.py`.

## Schema

```json
[
  {
    "wikidata_id": "Q...",
    "tmdb_id": "12345",
    "title": "Movie Title",
    "media_type": "movie",
    "creator": "Director Name",
    "year": 2019,
    "tags": ["whodunit", "ensemble"],
    "external_links": {
      "tvtropes_url": "https://tvtropes.org/pmwiki/pmwiki.php/Film/...",
      "wikipedia_url": "https://en.wikipedia.org/wiki/..."
    },
    "notes": "Optional brief note.",
    "persons": [
      { "name": "Harlan Thrombey", "role_in_story": "victim", "profession": "author", "approximate_age": "85" },
      { "name": "Ransom Drysdale", "role_in_story": "antagonist" },
      { "name": "Benoit Blanc", "role_in_story": "detective" }
    ],
    "deaths": [
      {
        "victim_name": "Harlan Thrombey",
        "killer_name": "Ransom Drysdale",
        "cause": "OTHER",
        "cause_detail": "Throat cut with a prop knife",
        "death_type": "murder",
        "motive": "greed_inheritance",
        "tropes": ["whodunit", "least_likely_suspect"],
        "ordinal": 1,
        "is_central_death": true,
        "is_twist": true,
        "notes": "Initially staged as suicide."
      }
    ],
    "episodes": [],
    "cases": []
  }
]
```

## Tips for movies

- `tmdb_id`: find at themoviedb.org — the number in the URL.
- For a film series (Knives Out, Columbo TV movies), each film is a separate entry.
- Use `series_name` and `series_number` for franchises.
- `tropes`: common film tropes: `whodunit`, `closed_circle`, `least_likely_suspect`, `howcatchem`, `inverted`, `frame_up`.
- `is_twist: true` for any death whose circumstances or perpetrator is a major reveal.
- `is_central_death: true` for the primary murder the story revolves around.
- Include off-screen deaths if they are part of the mystery narrative.

## Cause guide

| Situation | Use |
|-----------|-----|
| Drug, chemical, plant poison | `POISONED` |
| Firearm, arrow | `SHOT` |
| Knife, blade, sharp object | `STABBED` |
| Blunt object, bludgeon | `CLUBBED` |
| Hands around throat, rope around neck | `STRANGLED` |
| Car, train, vehicle | `VEHICULAR` |
| Method unclear or not shown | `UNKNOWN` |
| Anything not fitting above | `OTHER` |
