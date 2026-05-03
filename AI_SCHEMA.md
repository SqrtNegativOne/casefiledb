# AI Instruction Manual: Adding New Works

To add a new book, movie, game, or episode to the Casefile Database:

1. Write a JSON file to `temp/` (e.g. `temp/my_new_data.json`).
2. Run `uv run python scripts/ingest.py`.

The script will validate, append to the website data, and delete your temp file. If validation fails, it will print errors and leave your file in `temp/` so you can fix it.

---

## JSON Structure

The file must be a **JSON array** of objects. Each object is one media item.

### Media Fields (Required)
- `title`: (string) Full title of the work.
- `wikidata_id`: (string or null) The Wikidata ID (e.g. `"Q2577458"`). Look it up at wikidata.org. Set to `null` if no Wikidata entry exists.
- `slug`: (string) Unique identifier. **If `wikidata_id` is set, omit this field** — the ingest script fills it in automatically. If `wikidata_id` is null, provide a URL-safe slug, e.g. `"monk-s08e16"` or `"columbo-s01e01"`.
- `media_type`: (string) One of: `book`, `movie`, `tv_show`, `tv_episode`, `game`, `short_story`, `play`, `podcast`.
- `persons`: (array) Every character mentioned in a death event (see below).
- `deaths`: (array) Death events (see below).

### Media Fields (Optional)
- `creator`: Author, director, or primary creator name.
- `year`: (integer) Release/publication year.
- `series_name`: (string) Series name if applicable.
- `series_number`: (number) Position in the series.
- `tmdb_id`, `igdb_id`, `isbn`: External IDs.
- `notes`: (string) Brief observations.
- `tags`: (array of strings) e.g. `["golden-age", "whodunit"]`.
- `episodes`: (array of episode objects) — **for `tv_show` only**. Each episode has its own persons and deaths. See Episode Fields below.
- `cases`: (array of case objects) — **for `game` only**. Each case/chapter has its own persons and deaths. See Case Fields below.

### Episode Fields (nested inside a `tv_show`)
- `title`: (string, required) Episode title.
- `season`: (integer, optional)
- `episode_number`: (integer, optional)
- `year`: (integer, optional) Air year.
- `wikidata_id`: (string, optional) Episode Wikidata ID if one exists.
- `notes`, `tags`: same as Media Fields.
- `persons`, `deaths`: same as top-level Media Fields — scoped to this episode only.

### Case Fields (nested inside a `game`)
- `title`: (string, required) Case or chapter title.
- `case_number`: (integer, optional)
- `notes`, `tags`: same as Media Fields.
- `persons`, `deaths`: same as top-level Media Fields — scoped to this case only.

---

## Persons (Characters)

Every name used in a `death` event **must** be defined here first.

- `name`: (string, required)
- `role_in_story`: One of: `protagonist`, `antagonist`, `victim`, `detective`, `bystander`, `unknown`.
- `is_fictional`: (boolean, default `true`)
- `nationality`, `ethnicity`, `gender`, `approximate_age`, `profession`: (string, optional)
- `skills`: (array of strings, optional)
- `archetype`: (string, optional)
- `notes`: (string, optional)

---

## Deaths (Events)

- `victim_name`: Must match a name in `persons`.
- `killer_name`: Must match a name in `persons`.
- `cause`: (required) One of:
  `POISONED`, `SHOT`, `STABBED`, `CLUBBED`, `STRANGLED`, `DROWNED`, `BURNED`, `HANGED`, `FELL`, `CRUSHED`, `SUFFOCATED`, `EXPLODED`, `ELECTROCUTED`, `FROZEN`, `ILLNESS`, `EATEN`, `TORN_APART`, `VEHICULAR`, `UNKNOWN`, `OTHER`.
  Use `VEHICULAR` for deaths caused by a vehicle (car, train, etc.). Use `UNKNOWN` when the method is not specified in the narrative. Reserve `OTHER` only for methods that fit none of the above.
- `death_type`: (required) One of:
  `murder`, `attempted_murder`, `manslaughter`, `suicide`, `accident`, `natural_death`, `execution`, `unknown`.
- `motive`: One of:
  `greed_inheritance`, `greed_financial`, `blackmail`, `jealousy`, `revenge`, `ideology`, `self_defense`, `concealment`, `passion`,
  `vigilante_justice`, `freedom`, `family_protection`, `pathological`, `mercy_killing`, `penance`,
  `unknown`, `other`.
  Key distinctions: `vigilante_justice` = self-appointed execution of those deemed guilty who escaped legal justice; `family_protection` = killing to shield family from ruin or scandal; `freedom` = escaping an unwanted relationship or controlling figure; `pathological` = compulsive or irrational psychological motive; `mercy_killing` = ending another's suffering; `penance` = atonement or confession-driven act. Reserve `other` only when none of the above fit.
- `cause_subtype`, `cause_detail`, `motive_detail`: (string, optional) Extra detail.
- `ordinal`: (integer, optional) Order of death within the work.
- `is_central_death`: (boolean) `true` if this is the primary mystery.
- `is_twist`: (boolean) `true` if the death involves a major plot twist.
- `chapter_or_act`: (string, optional)
- `notes`: (string, optional)

---

## Example

```json
[
  {
    "wikidata_id": "Q12345",
    "title": "Example Mystery",
    "media_type": "book",
    "creator": "Jane Doe",
    "year": 2024,
    "tags": ["golden-age"],
    "persons": [
      { "name": "Alice", "role_in_story": "victim" },
      { "name": "Bob", "role_in_story": "antagonist" }
    ],
    "deaths": [
      {
        "victim_name": "Alice",
        "killer_name": "Bob",
        "cause": "POISONED",
        "death_type": "murder",
        "motive": "revenge",
        "is_central_death": true,
        "is_twist": false
      }
    ]
  }
]
```
