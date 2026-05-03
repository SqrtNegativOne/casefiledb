# Prompt: Add a Game to Casefile Database

You are adding a **game** to the Casefile Database.

## Your task

1. Look up the game on Wikidata and IGDB.
2. Find a walkthrough or wiki with all cases/chapters and their deaths.
3. Deaths are organised **inside cases** (not at the top level).
4. Write a JSON file and save to `temp/`. Run `uv run python scripts/ingest.py`.

## Important structural rule

For a `game`, **deaths go inside each case** — the top-level `deaths` array is always empty.
Each case has its own `persons` and `deaths` arrays.

## Schema

```json
[
  {
    "wikidata_id": "Q...",
    "igdb_id": "12345",
    "title": "Game Title",
    "media_type": "game",
    "creator": "Developer / Studio Name",
    "year": 2001,
    "series_name": "Ace Attorney",
    "series_number": 1,
    "tags": ["visual-novel", "courtroom"],
    "external_links": {
      "fandom_url": "https://aceattorney.fandom.com/wiki/Game_Title",
      "steam_url": "https://store.steampowered.com/app/...",
      "tvtropes_url": "https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/...",
      "wikipedia_url": "https://en.wikipedia.org/wiki/..."
    },
    "notes": "Optional.",
    "persons": [],
    "deaths": [],
    "episodes": [],
    "cases": [
      {
        "title": "Case 1: The First Turnabout",
        "case_number": 1,
        "notes": "Tutorial case.",
        "tags": [],
        "persons": [
          { "name": "Cindy Stone", "role_in_story": "victim" },
          { "name": "Frank Sahwit", "role_in_story": "antagonist" },
          { "name": "Phoenix Wright", "role_in_story": "protagonist" }
        ],
        "deaths": [
          {
            "victim_name": "Cindy Stone",
            "killer_name": "Frank Sahwit",
            "cause": "CLUBBED",
            "death_type": "murder",
            "motive": "concealment",
            "tropes": ["whodunit"],
            "ordinal": 1,
            "is_central_death": true,
            "is_twist": false,
            "notes": "Struck with a clock/statue."
          }
        ]
      }
    ]
  }
]
```

## Tips for games

- Visual novels and mystery games often have cases that serve as self-contained mysteries. Treat each as a separate `case` object.
- For games with a continuous story and no discrete cases (e.g. adventure games), create one case per chapter or act.
- `igdb_id`: find at igdb.com — useful for future lookups.
- `steam_url`: include if the game is on Steam.
- `tropes`: common game tropes: `locked_room`, `impossible_crime`, `dying_clue`, `whodunit`, `least_likely_suspect`.
- Use `is_twist: true` for deaths where the killer reveal is a major story moment.
- Include all deaths that are part of the mystery, including deaths-before-the-game-starts that the player investigates.
