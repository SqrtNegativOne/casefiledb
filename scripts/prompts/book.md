# Prompt: Add a Book to Casefile Database

You are adding a **book** (novel or short story collection) to the Casefile Database.

## Your task

1. Look up the book on Wikidata (wikidata.org) to get its Wikidata ID.
2. Look up the book on Goodreads to get its URL.
3. Look up the book's TV Tropes page if one exists.
4. Compile all deaths and key characters from the book.
5. Write a JSON file following the schema below and save it to `temp/`.
6. Run `uv run python scripts/ingest.py`.

## Source material

Use the book's Wikipedia article, Fandom wiki, Goodreads page, and TV Tropes page as sources.
Spoilers are expected and required — include all deaths, including the killer's identity.

## Schema

```json
[
  {
    "wikidata_id": "Q...",
    "title": "Full Title",
    "media_type": "book",
    "creator": "Author Full Name",
    "year": 1930,
    "series_name": "Series Name",
    "series_number": 1,
    "tags": ["golden-age", "whodunit"],
    "external_links": {
      "goodreads_url": "https://www.goodreads.com/book/show/...",
      "tvtropes_url": "https://tvtropes.org/pmwiki/pmwiki.php/Literature/...",
      "wikipedia_url": "https://en.wikipedia.org/wiki/..."
    },
    "notes": "One sentence summary if useful.",
    "persons": [
      { "name": "Name", "role_in_story": "victim|antagonist|protagonist|detective|bystander|unknown", "profession": "occupation if known" }
    ],
    "deaths": [
      {
        "victim_name": "Name",
        "killer_name": "Name",
        "cause": "POISONED|SHOT|STABBED|CLUBBED|STRANGLED|DROWNED|BURNED|HANGED|FELL|CRUSHED|SUFFOCATED|EXPLODED|ELECTROCUTED|FROZEN|ILLNESS|EATEN|TORN_APART|VEHICULAR|UNKNOWN|OTHER",
        "death_type": "murder|suicide|accident|natural_death|execution|manslaughter|unknown",
        "motive": "greed_inheritance|greed_financial|blackmail|jealousy|revenge|ideology|self_defense|concealment|passion|vigilante_justice|freedom|family_protection|pathological|mercy_killing|penance|unknown|other",
        "tropes": ["whodunit", "locked_room"],
        "ordinal": 1,
        "is_central_death": true,
        "is_twist": false,
        "chapter_or_act": "Chapter 12",
        "notes": "Optional brief note."
      }
    ],
    "episodes": [],
    "cases": []
  }
]
```

## Field notes

- `wikidata_id`: Required if the book has a Wikidata entry. Otherwise set to `null` and provide a `slug` like `"christie-mysterious-affair-1920"`.
- `series_number`: Use decimals for sub-entries (e.g. 3.5 for a novella between books 3 and 4).
- `tropes`: See AI_SCHEMA.md for the full list. Common book tropes: `whodunit`, `closed_circle`, `locked_room`, `least_likely_suspect`, `dying_clue`, `alibi_trick`.
- Every name in `deaths` must appear in `persons` first.
- `deaths` is empty for a `tv_show` — deaths go inside each episode instead.
- `episodes` and `cases` should be empty arrays for a book.

## Cause guide

| Situation | Use |
|-----------|-----|
| Drug, chemical, plant | `POISONED` |
| Firearm, arrow | `SHOT` |
| Knife, blade, sharp object | `STABBED` |
| Blunt object, bludgeon | `CLUBBED` |
| Hands around throat, rope | `STRANGLED` |
| Car, train, vehicle | `VEHICULAR` |
| Method not described | `UNKNOWN` |
| Anything else | `OTHER` |
