# AI Instruction Manual: Adding New Works

To add a new book, movie, game, or episode to the Casefile Database:

1. Write a JSON file to `temp/` (e.g. `temp/my_new_data.json`).
2. Run `cargo run --bin ingest --manifest-path validator/Cargo.toml`.

The script will validate, append to the website data, and delete your temp file. If validation fails, it will print errors and leave your file in `temp/` so you can fix it.

---

## JSON Structure

The file must be a **JSON array** of objects. Each object is one media item.

### Media Fields (Required)
- `title`: (string) Full title of the work.
- `wikidata_id`: (string or null) The Wikidata ID (e.g. `"Q2577458"`). Look it up at wikidata.org. Set to `null` if no Wikidata entry exists.
- `slug`: (string) Unique identifier. **If `wikidata_id` is set, omit this field** — the ingest script fills it in automatically. If `wikidata_id` is null, provide a URL-safe slug, e.g. `"monk-s08e16"` or `"columbo-s01e01"`.
- `media_type`: (string) One of: `Book`, `Movie`, `TvShow`, `TvEpisode`, `Game`, `ShortStory`, `Play`, `Podcast`.
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
- `external_links`: (object, optional) External resource URLs — see External Links below.
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

- `id`: (string, optional) Stable slug identifier for this person within this scope (e.g. `"emily-inglethorp"`). The ingest tool auto-generates it from the name if omitted — you only need to supply it when you want a specific value (e.g. to avoid a collision or match a pre-existing ID).
- `name`: (string, required)
- `role_in_story`: (optional) One of: `Protagonist`, `Antagonist`, `Victim`, `Detective`, `Bystander`, `Unstated`.
- `is_solver`: (boolean, optional) `true` if this person actively cracks the central mystery. Use this to distinguish the detective who *nominally* investigates from whoever *actually* solves it. In Sherlock Holmes, Holmes gets `is_solver: true`; in Knives Out, Marta gets `is_solver: true` (not Blanc). Leave null if ambiguous or irrelevant.
- `is_fictional`: (boolean, default `true`)
- `nationality`, `ethnicity`, `gender`, `approximate_age`, `profession`: (string, optional)
- `skills`: (array of strings, optional)
- `archetype`: (string, optional)
- `notes`: (string, optional)

---

## Deaths (Events)

- `victim_id`: ID of the victim — must match an `id` in `persons`. You may instead supply `victim_name` (the person's display name) and the ingest tool will resolve it to the ID automatically.
- (killers) `person_id`: ID of the killer — must match an `id` in `persons`. You may instead supply `name` (the person's display name) and the ingest tool will resolve it.
- `cause`: (required) One of:
  `Poisoned`, `Shot`, `Stabbed`, `Clubbed`, `Strangled`, `Drowned`, `Burned`, `Hanged`, `Fell`, `Crushed`, `Suffocated`, `Exploded`, `Electrocuted`, `Frozen`, `Illness`, `Eaten`, `TornApart`, `Vehicular`, `Unstated`, `Other`.
  Use `Vehicular` for deaths caused by a vehicle (car, train, etc.). Use `Unstated` when the cause is not specified in the narrative. Reserve `Other` only for methods that fit none of the above.
  **`means` is required for every `cause` except `Other`** — see below.
- `death_type`: (required) One of:
  `Homicide`, `AttemptedHomicide`, `Execution`, `Accident`, `NaturalDeath`, `Unstated`.
  Key rules: **suicide** is represented as `Homicide` with the victim also listed in `killers` (killer == victim). **Manslaughter** is represented as `Homicide` with the killer's `mens_rea` set to `Recklessly` or `Negligently`. **Accidents involving no human culprit** use `Accident` with an empty `killers` list.
- `motive`: One of:
  `GreedInheritance`, `GreedFinancial`, `Blackmail`, `Jealousy`, `Revenge`, `Ideology`, `SelfDefense`, `Concealment`, `Passion`,
  `VigilanteJustice`, `Freedom`, `FamilyProtection`, `Pathological`, `Mercy`, `Penance`,
  `Unstated`, `Other`, `NeedsReview`.
  Key distinctions: `VigilanteJustice` = self-appointed execution of those deemed guilty who escaped legal justice; `FamilyProtection` = killing to shield family from ruin or scandal; `Freedom` = escaping an unwanted relationship or controlling figure; `Pathological` = compulsive or irrational psychological motive; `Mercy` = ending another's suffering; `Penance` = atonement or confession-driven act. Reserve `Other` only when none of the above fit. Use `Unstated` when the narrative genuinely does not state a reason; use `NeedsReview` as a placeholder when you have not yet researched it.
  **Required for all `death_type` values except `Accident` and `NaturalDeath`** — use `Unstated` if the reason is not stated in the narrative, or `NeedsReview` if not yet researched. For `Homicide` representing a suicide, use the victim's own motive (e.g. `Penance`, `Freedom`, `Pathological`).
- `killers`: (array, default `[]`) Each entry is an object describing one killer's role in the death. A death may have zero, one, or multiple killers (e.g. co-conspirators with different levels of involvement):
  - `person_id`: (string) Must match an `id` in `persons`. Alternatively, supply `name` (the person's display name) and ingest resolves it. One of the two is required.
  - `mens_rea`: **(required)** MPC mens rea — choose the highest that applies:
    - `Purposely` — desired the death (classic premeditation)
    - `Knowingly` — didn't desire death per se but knew it was certain
    - `Recklessly` — consciously disregarded a substantial risk of death
    - `Negligently` — should have known their conduct risked death
    - `Accidentally` — zero culpability; pure accident
    - `Unstated` — media does not make the mental state clear
    - `NeedsReview` — placeholder; not yet researched
  - `circumstance`: **(required)** Contextual justification or mitigation:
    - `Justified` — war, self-defense, euthanasia
    - `Mitigated` — diminished capacity, coercion, extreme duress
    - `Neutral` — no special circumstance
    - `Unstated` — media does not make it clear
    - `NeedsReview` — placeholder; not yet researched
- `tropes`: (array of strings, optional) Mystery tropes that apply to this death. Choose from:
  - `LockedRoom` — death occurred in a sealed space with no apparent entry/exit
  - `ImpossibleCrime` — the crime appears physically impossible
  - `HowCatchem` — killer is known from the start; interest is the investigation
  - `Whodunit` — identity of the killer is unknown until the end
  - `Whydunit` — killer's identity is known; the motive is the mystery
  - `Howdunit` — the method of the crime is the central puzzle
  - `DyingClue` — the victim left a cryptic clue pointing to the killer
  - `AlibiTrick` — the killer's alibi is constructed or faked
  - `ClosedCircle` — suspects are isolated together (snowbound house, island, train, etc.)
  - `NeedleInHaystack` — the killer is hidden among many plausible suspects
  - `LeastLikelySuspect` — the killer is the character the reader would least expect
  - `FrameUp` — an innocent person is deliberately framed
  - `MistakenIdentity` — the crime stems from a case of mistaken identity
- `means`: (string) **Required** for every `cause` except `Other`. Specify the exact substance, weapon, or mechanism (e.g. `"arsenic"`, `"revolver"`, `"kitchen knife"`, `"cliff edge"`, `"car"`). When `cause` is `Unstated`, set `means` to `"unknown"` as well. Three additional reserved values: `"unmentioned"` if the narrative never names the specific item; `"unknown"` if the protagonist genuinely does not know what was used (an open in-story mystery); `"needs_review"` if you have not yet looked it up.
- `cause_detail`, `motive_detail`: (string, optional) Extra narrative detail.
- `ordinal`: (integer, optional) Order of death within the work.
- `is_central_death`: (boolean, optional, default `false`) `true` if this is the primary mystery.
- `is_twist`: (boolean, optional, default `false`) `true` if the death involves a major plot twist.
- `chapter_or_act`: (string, optional)
- `notes`: (string, optional)

---

## External Links

Optional object on a media item. Store the **identifier** for each source, not the full URL. Each source also has a `*_status` field tracking whether a page exists.

| Slug/ID field | What to store | Example |
|---|---|---|
| `tvtropes_slug` | `Namespace/Title` after `/pmwiki/pmwiki.php/` | `"Literature/AndThenThereWereNone"` |
| `wikipedia_slug` | Article title (underscores, no hostname) | `"And_Then_There_Were_None"` |
| `fandom_slug` | `subdomain/PageTitle` | `"agathachristie/And_Then_There_Were_None"` |
| `goodreads_id` | Numeric book ID only | `"16299"` |
| `steam_id` | Numeric app ID only | `"1234567"` |
| `itch_slug` | `author/game-slug` | `"inkle/80-days"` |

Each source has a paired `*_status` field — `"Exists"`, `"None"`, or `"NeedsReview"` (default). Setting a slug auto-implies `"Exists"`; use `"None"` to record that you confirmed no page exists for this work.

```json
"external_links": {
  "tvtropes_slug": "Literature/AndThenThereWereNone",
  "wikipedia_slug": "And_Then_There_Were_None",
  "fandom_slug": "agathachristie/And_Then_There_Were_None",
  "fandom_status": "Exists",
  "goodreads_id": "16299",
  "steam_status": "None"
}
```

Only include fields you have data for. All fields are optional.

---

## Example

```json
[
  {
    "wikidata_id": "Q12345",
    "title": "Example Mystery",
    "media_type": "Book",
    "creator": "Jane Doe",
    "year": 2024,
    "tags": ["golden-age"],
    "external_links": {
      "goodreads_id": "12345",
      "tvtropes_slug": "Literature/ExampleMystery"
    },
    "persons": [
      { "name": "Alice", "role_in_story": "Victim" },
      { "name": "Bob", "role_in_story": "Antagonist" }
    ],
    "deaths": [
      {
        "victim_id": "alice",
        "cause": "Poisoned",
        "means": "arsenic",
        "death_type": "Homicide",
        "killers": [
          { "person_id": "bob", "mens_rea": "Purposely", "circumstance": "Neutral" }
        ],
        "motive": "Revenge",
        "tropes": ["Whodunit", "ClosedCircle"],
        "is_central_death": true,
        "is_twist": false
      }
    ]
  }
]
```
