# AI Instruction Manual: Adding New Works

To add a new book, movie, or game to the Casefile Database, generate a JSON array containing the work's details. Follow these strict rules to ensure the data is compatible with the database.

## JSON Structure

The output must be a **JSON Array** of objects. Each object represents one media item.

### Media Fields (Required)
- `wikidata_id`: (string) The official Wikidata ID (e.g., "Q2577458").
- `title`: (string) The full title of the work.
- `media_type`: (string) Must be one of: `book`, `movie`, `tv_show`, `tv_episode`, `game`, `short_story`, `play`, `podcast`.
- `persons`: (array) List of characters involved (see below).
- `deaths`: (array) List of death events (see below).

### Media Fields (Optional)
- `creator`: Author, director, or primary creator name.
- `year`: (integer) Publication/release year.
- `series_name`: (string) Name of the series if applicable.
- `series_number`: (number) Position in the series.
- `notes`: (string) General observations (keep it brief).
- `tags`: (array of strings) e.g., `["golden-age", "whodunit"]`.

---

## Persons (Characters)
Every person mentioned in a `death` event (victim or killer) **must** be defined in the `persons` array.

- `name`: (string, Required) Full character name.
- `role_in_story`: (string) Must be one of: `protagonist`, `antagonist`, `victim`, `detective`, `bystander`, `unknown`.
- `is_fictional`: (boolean) Default is `true`.
- `notes`: (string) Brief character description.

---

## Deaths (Events)
- `victim_name`: (string) Must match a name in the `persons` array.
- `killer_name`: (string) Must match a name in the `persons` array.
- `cause`: (string, Required) **MUST be one of**:
  `POISONED`, `SHOT`, `STABBED`, `CLUBBED`, `STRANGLED`, `DROWNED`, `BURNED`, `HANGED`, `FELL`, `CRUSHED`, `SUFFOCATED`, `EXPLODED`, `ELECTROCUTED`, `FROZEN`, `ILLNESS`, `EATEN`, `TORN_APART`, `OTHER`.
- `death_type`: (string, Required) **MUST be one of**:
  `murder`, `attempted_murder`, `manslaughter`, `suicide`, `accident`, `natural_death`, `execution`, `unknown`.
- `motive`: (string) **MUST be one of**:
  `greed_inheritance`, `greed_financial`, `blackmail`, `jealousy`, `revenge`, `ideology`, `self_defense`, `concealment`, `passion`, `unknown`, `other`.
- `is_central_death`: (boolean) Set to `true` if this is the primary mystery of the work.
- `is_twist`: (boolean) Set to `true` if the death or its circumstances involve a major plot twist.

---

## Example JSON
```json
[
  {
    "wikidata_id": "Q12345",
    "title": "Example Mystery",
    "media_type": "book",
    "creator": "Jane Doe",
    "year": 2024,
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
        "is_central_death": true
      }
    ]
  }
]
```
