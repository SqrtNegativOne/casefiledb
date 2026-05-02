"""Seed the database with six Agatha Christie works.

Idempotent: skips any media whose wikidata_id already exists.

Wikidata QIDs below are believed correct as of 2026; verify at wikidata.org
if the IDs matter downstream.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy import select

from catalog.database import get_session, init_db
from catalog.models import Death, Media, Person, Tag, media_tag

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Seed payload
# ---------------------------------------------------------------------------

_SEED: list[dict] = [
    # ------------------------------------------------------------------
    # 1. Murder on the Orient Express (1934)  Q229390
    # ------------------------------------------------------------------
    {
        "wikidata_id": "Q229390",
        "title": "Murder on the Orient Express",
        "media_type": "book",
        "year": 1934,
        "creator": "Agatha Christie",
        "series_name": "Hercule Poirot",
        "series_number": 10.0,
        "isbn": "978-0-00-813609-8",
        "notes": "Poirot solves a murder aboard a snowbound train.",
        "tags": ["golden-age", "cozy"],
        "persons": [
            {
                "name": "Hercule Poirot",
                "is_fictional": True,
                "role_in_story": "detective",
                "nationality": "Belgian",
                "gender": "male",
                "approximate_age": "50s",
                "profession": "Private detective",
                "skills": json.dumps(["deductive reasoning", "psychology", "observation"]),
                "archetype": "brilliant eccentric detective",
            },
            {
                "name": "Samuel Ratchett",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "American",
                "gender": "male",
                "approximate_age": "60s",
                "profession": "Fraudster / fugitive",
                "archetype": "wealthy fugitive with a dark past",
                "notes": "True name Cassetti; orchestrated the Daisy Armstrong kidnapping.",
            },
            {
                "name": "Mary Debenham",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "30s",
                "profession": "Governess",
                "archetype": "composed woman with a secret",
            },
            {
                "name": "Hector MacQueen",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "American",
                "gender": "male",
                "approximate_age": "30s",
                "profession": "Secretary",
                "archetype": "loyal accomplice seeking revenge",
            },
        ],
        "deaths": [
            {
                "victim_name": "Samuel Ratchett",
                "ordinal": 1,
                "cause": "STABBED",
                "cause_subtype": "multiple stab wounds",
                "cause_detail": "Stabbed twelve times by twelve different hands during the night.",
                "death_type": "murder",
                "killer_name": None,
                "motive": "revenge",
                "motive_detail": "All passengers were connected to the Daisy Armstrong case and acted collectively.",
                "is_central_death": True,
                "is_twist": True,
                "chapter_or_act": "Part Two",
                "notes": "Twist: every passenger on the Stamboul coach is equally guilty.",
            }
        ],
    },
    # ------------------------------------------------------------------
    # 2. And Then There Were None (1939)  Q229472
    # ------------------------------------------------------------------
    {
        "wikidata_id": "Q229472",
        "title": "And Then There Were None",
        "media_type": "book",
        "year": 1939,
        "creator": "Agatha Christie",
        "series_name": None,
        "series_number": None,
        "isbn": "978-0-00-813630-2",
        "notes": "Ten strangers are lured to an island and murdered one by one.",
        "tags": ["golden-age", "thriller", "locked-room"],
        "persons": [
            {
                "name": "Justice Lawrence Wargrave",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "70s",
                "profession": "Retired judge",
                "skills": json.dumps(["manipulation", "planning", "law"]),
                "archetype": "moralistic hanging judge turned vigilante killer",
                "notes": "Masterminds all ten deaths while feigning his own murder.",
            },
            {
                "name": "Vera Claythorne",
                "is_fictional": True,
                "role_in_story": "protagonist",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "20s",
                "profession": "Secretary / former governess",
                "archetype": "guilt-ridden survivor undone by her own conscience",
            },
            {
                "name": "Philip Lombard",
                "is_fictional": True,
                "role_in_story": "bystander",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "30s",
                "profession": "Mercenary / soldier of fortune",
                "skills": json.dumps(["survival", "firearms", "tracking"]),
                "archetype": "amoral adventurer who left men to die in Africa",
            },
            {
                "name": "Anthony Marston",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "20s",
                "profession": "Socialite",
                "archetype": "reckless youth with no moral compass",
            },
            {
                "name": "Mrs. Ethel Rogers",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "40s",
                "profession": "Cook / housekeeper",
                "archetype": "complicit wife crushed by guilt",
            },
            {
                "name": "General John Macarthur",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "60s",
                "profession": "Retired military officer",
                "archetype": "guilt-worn soldier who sent a rival to his death",
            },
        ],
        "deaths": [
            {
                "victim_name": "Anthony Marston",
                "ordinal": 1,
                "cause": "POISONED",
                "cause_subtype": "potassium cyanide",
                "cause_detail": "Cyanide slipped into his cocktail glass.",
                "death_type": "murder",
                "killer_name": "Justice Lawrence Wargrave",
                "motive": "ideology",
                "motive_detail": "Killed two children with reckless driving and showed no remorse.",
                "is_central_death": False,
                "is_twist": False,
                "chapter_or_act": "Chapter 3",
            },
            {
                "victim_name": "Mrs. Ethel Rogers",
                "ordinal": 2,
                "cause": "POISONED",
                "cause_subtype": "chloral hydrate overdose",
                "cause_detail": "Sleeping draught added to her nightcap; she never woke.",
                "death_type": "murder",
                "killer_name": "Justice Lawrence Wargrave",
                "motive": "ideology",
                "motive_detail": "Withheld medication from elderly employer, hastening her death.",
                "is_central_death": False,
                "is_twist": False,
                "chapter_or_act": "Chapter 4",
            },
            {
                "victim_name": "General John Macarthur",
                "ordinal": 3,
                "cause": "CLUBBED",
                "cause_subtype": "blunt instrument to the back of the skull",
                "cause_detail": "Struck from behind while sitting on the cliff overlooking the sea.",
                "death_type": "murder",
                "killer_name": "Justice Lawrence Wargrave",
                "motive": "ideology",
                "motive_detail": "Sent his wife's lover on a suicide mission during WWI.",
                "is_central_death": False,
                "is_twist": False,
                "chapter_or_act": "Chapter 6",
            },
        ],
    },
    # ------------------------------------------------------------------
    # 3. Death on the Nile (1937)  Q782407
    # ------------------------------------------------------------------
    {
        "wikidata_id": "Q782407",
        "title": "Death on the Nile",
        "media_type": "book",
        "year": 1937,
        "creator": "Agatha Christie",
        "series_name": "Hercule Poirot",
        "series_number": 17.0,
        "isbn": "978-0-00-813628-9",
        "notes": "Poirot investigates the murder of an heiress during a Nile cruise.",
        "tags": ["golden-age", "cozy"],
        "persons": [
            {
                "name": "Hercule Poirot",
                "is_fictional": True,
                "role_in_story": "detective",
                "nationality": "Belgian",
                "gender": "male",
                "approximate_age": "50s",
                "profession": "Private detective",
                "skills": json.dumps(["deductive reasoning", "psychology", "observation"]),
                "archetype": "brilliant eccentric detective",
            },
            {
                "name": "Linnet Ridgeway Doyle",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "American",
                "gender": "female",
                "approximate_age": "20s",
                "profession": "Heiress / socialite",
                "archetype": "golden girl who takes what she wants",
            },
            {
                "name": "Simon Doyle",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "30s",
                "profession": "Gentleman / former soldier",
                "archetype": "charming fortune-hunter",
            },
            {
                "name": "Jacqueline de Bellefort",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "French",
                "gender": "female",
                "approximate_age": "20s",
                "profession": "None (formerly engaged to Simon)",
                "skills": json.dumps(["marksmanship"]),
                "archetype": "scorned lover turned instrument of murder",
            },
        ],
        "deaths": [
            {
                "victim_name": "Linnet Ridgeway Doyle",
                "ordinal": 1,
                "cause": "SHOT",
                "cause_subtype": "small-calibre pistol, point-blank",
                "cause_detail": "Shot through the temple while she slept in her cabin.",
                "death_type": "murder",
                "killer_name": "Simon Doyle",
                "motive": "greed_inheritance",
                "motive_detail": "Simon and Jacqueline conspired to inherit Linnet's fortune.",
                "is_central_death": True,
                "is_twist": False,
                "chapter_or_act": "Chapter 16",
            },
            {
                "victim_name": "Jacqueline de Bellefort",
                "ordinal": 2,
                "cause": "SHOT",
                "cause_subtype": "small-calibre pistol",
                "cause_detail": "Simon shot Jacqueline to silence her after their plot unravelled.",
                "death_type": "murder",
                "killer_name": "Simon Doyle",
                "motive": "concealment",
                "motive_detail": "She was the only witness who could expose the conspiracy.",
                "is_central_death": False,
                "is_twist": True,
                "chapter_or_act": "Chapter 30",
                "notes": "Actually suicide: Jacqueline allowed Simon to shoot her to protect him.",
            },
        ],
    },
    # ------------------------------------------------------------------
    # 4. The ABC Murders (1936)  Q1781745
    # ------------------------------------------------------------------
    {
        "wikidata_id": "Q1781745",
        "title": "The ABC Murders",
        "media_type": "book",
        "year": 1936,
        "creator": "Agatha Christie",
        "series_name": "Hercule Poirot",
        "series_number": 13.0,
        "isbn": "978-0-00-813627-2",
        "notes": "A serial killer taunts Poirot with alphabetical murder announcements.",
        "tags": ["golden-age", "procedural"],
        "persons": [
            {
                "name": "Hercule Poirot",
                "is_fictional": True,
                "role_in_story": "detective",
                "nationality": "Belgian",
                "gender": "male",
                "approximate_age": "50s",
                "profession": "Private detective",
                "skills": json.dumps(["deductive reasoning", "psychology", "observation"]),
                "archetype": "brilliant eccentric detective",
            },
            {
                "name": "Franklin Clarke",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "40s",
                "profession": "Gentleman of leisure",
                "archetype": "calculating brother hiding behind a madman facade",
            },
            {
                "name": "Alexander Bonaparte Cust",
                "is_fictional": True,
                "role_in_story": "bystander",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "50s",
                "profession": "Travelling salesman (stockings)",
                "archetype": "unwitting patsy framed for alphabetical murders",
                "notes": "Suffers from epilepsy; manipulated into being the ABC suspect.",
            },
            {
                "name": "Alice Ascher",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "60s",
                "profession": "Tobacconist",
                "archetype": "innocent cover for the real target",
            },
            {
                "name": "Sir Carmichael Clarke",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "60s",
                "profession": "Wealthy collector",
                "archetype": "the true target: the rich brother",
            },
        ],
        "deaths": [
            {
                "victim_name": "Alice Ascher",
                "ordinal": 1,
                "cause": "CLUBBED",
                "cause_subtype": "cosh",
                "cause_detail": "Struck from behind in her tobacconist shop in Andover.",
                "death_type": "murder",
                "killer_name": "Franklin Clarke",
                "motive": "concealment",
                "motive_detail": "First decoy murder in the alphabetical series to mask the real target.",
                "is_central_death": False,
                "is_twist": False,
                "chapter_or_act": "Chapter 5",
            },
            {
                "victim_name": "Sir Carmichael Clarke",
                "ordinal": 3,
                "cause": "CLUBBED",
                "cause_subtype": "cosh",
                "cause_detail": "Murdered in his own grounds in Churston; the real target of the scheme.",
                "death_type": "murder",
                "killer_name": "Franklin Clarke",
                "motive": "greed_inheritance",
                "motive_detail": "Franklin stood to inherit his brother's estate once Carmichael was dead.",
                "is_central_death": True,
                "is_twist": True,
                "chapter_or_act": "Chapter 14",
                "notes": "The C murder reveals the true pattern: Clarke killed his own brother.",
            },
        ],
    },
    # ------------------------------------------------------------------
    # 5. Witness for the Prosecution (short story, 1925)  Q2577458
    # ------------------------------------------------------------------
    {
        "wikidata_id": "Q2577458",
        "title": "Witness for the Prosecution",
        "media_type": "short_story",
        "year": 1925,
        "creator": "Agatha Christie",
        "series_name": None,
        "series_number": None,
        "notes": "A seemingly open-and-shut murder trial turns on a devastating twist.",
        "tags": ["golden-age", "thriller"],
        "persons": [
            {
                "name": "Leonard Vole",
                "is_fictional": True,
                "role_in_story": "protagonist",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "30s",
                "profession": "Unemployed inventor",
                "archetype": "charming accused man who may or may not be guilty",
            },
            {
                "name": "Romaine Heilger",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "German",
                "gender": "female",
                "approximate_age": "30s",
                "profession": "Actress",
                "skills": json.dumps(["acting", "deception", "manipulation"]),
                "archetype": "calculating wife who engineers justice through deception",
                "notes": "Calls herself Romaine Vole in some versions; the witness who betrays and then saves Leonard.",
            },
            {
                "name": "Emily French",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "50s",
                "profession": "Wealthy widow",
                "archetype": "lonely spinster who befriends the wrong man",
            },
        ],
        "deaths": [
            {
                "victim_name": "Emily French",
                "ordinal": 1,
                "cause": "CLUBBED",
                "cause_subtype": "blunt object",
                "cause_detail": "Beaten to death in her home; Leonard Vole is accused.",
                "death_type": "murder",
                "killer_name": "Leonard Vole",
                "motive": "greed_inheritance",
                "motive_detail": "Emily had altered her will in Leonard's favour.",
                "is_central_death": True,
                "is_twist": True,
                "chapter_or_act": None,
                "notes": "Twist: Romaine's elaborate lie is itself a deception that reveals Leonard's guilt.",
            }
        ],
    },
    # ------------------------------------------------------------------
    # 6. The Murder at the Vicarage (1930)  Q534271
    # ------------------------------------------------------------------
    {
        "wikidata_id": "Q534271",
        "title": "The Murder at the Vicarage",
        "media_type": "book",
        "year": 1930,
        "creator": "Agatha Christie",
        "series_name": "Miss Marple",
        "series_number": 1.0,
        "isbn": "978-0-00-813619-7",
        "notes": "Miss Marple's debut novel; a colonel is murdered in the vicar's study.",
        "tags": ["golden-age", "cozy"],
        "persons": [
            {
                "name": "Miss Jane Marple",
                "is_fictional": True,
                "role_in_story": "detective",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "60s",
                "profession": "Retired village spinster",
                "skills": json.dumps(["observation", "human nature", "village analogy"]),
                "archetype": "deceptively sharp elderly amateur sleuth",
            },
            {
                "name": "Colonel Lucius Protheroe",
                "is_fictional": True,
                "role_in_story": "victim",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "60s",
                "profession": "Magistrate / landowner",
                "archetype": "universally disliked tyrant whose death no one mourns",
            },
            {
                "name": "Anne Protheroe",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "British",
                "gender": "female",
                "approximate_age": "30s",
                "profession": "Wife of the colonel",
                "archetype": "trophy wife trapped in a loveless marriage",
            },
            {
                "name": "Lawrence Redding",
                "is_fictional": True,
                "role_in_story": "antagonist",
                "nationality": "British",
                "gender": "male",
                "approximate_age": "30s",
                "profession": "Artist",
                "archetype": "passionate lover who acts rashly",
            },
        ],
        "deaths": [
            {
                "victim_name": "Colonel Lucius Protheroe",
                "ordinal": 1,
                "cause": "SHOT",
                "cause_subtype": "revolver",
                "cause_detail": "Shot in the head in the vicar's study; at first two people confess.",
                "death_type": "murder",
                "killer_name": "Anne Protheroe",
                "motive": "passion",
                "motive_detail": "Anne and Lawrence Redding conspired to escape the colonel's tyranny.",
                "is_central_death": True,
                "is_twist": False,
                "chapter_or_act": "Chapter 2",
                "notes": "Both Anne and Lawrence separately confess to protect each other.",
            }
        ],
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_seed() -> None:
    """Insert seed data idempotently and log results."""
    init_db()
    inserted = 0
    skipped = 0

    with get_session() as session:
        for entry in _SEED:
            wid: str = entry["wikidata_id"]

            if session.get(Media, wid) is not None:
                logger.info("SKIP  %s  %s", wid, entry["title"])
                skipped += 1
                continue

            # Media row
            media = Media(
                wikidata_id=wid,
                title=entry["title"],
                media_type=entry["media_type"],
                year=entry.get("year"),
                creator=entry.get("creator"),
                series_name=entry.get("series_name"),
                series_number=entry.get("series_number"),
                isbn=entry.get("isbn"),
                notes=entry.get("notes"),
            )
            session.add(media)
            session.flush()

            # Tags
            for tag_name in entry.get("tags", []):
                tag = session.execute(
                    select(Tag).where(Tag.name == tag_name)
                ).scalar_one_or_none()
                if tag is None:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    session.flush()
                session.execute(
                    media_tag.insert().values(media_id=wid, tag_id=tag.id)
                )

            # Persons -- collect name->id for death resolution
            name_to_id: dict[str, int] = {}
            for pd in entry.get("persons", []):
                person = Person(
                    media_id=wid,
                    name=pd["name"],
                    is_fictional=pd.get("is_fictional", True),
                    role_in_story=pd.get("role_in_story"),
                    nationality=pd.get("nationality"),
                    gender=pd.get("gender"),
                    approximate_age=pd.get("approximate_age"),
                    profession=pd.get("profession"),
                    skills=pd.get("skills"),
                    archetype=pd.get("archetype"),
                    notes=pd.get("notes"),
                )
                session.add(person)
                session.flush()
                name_to_id[pd["name"]] = person.id

            # Deaths
            for dd in entry.get("deaths", []):
                vname: str | None = dd.get("victim_name")
                kname: str | None = dd.get("killer_name")
                death = Death(
                    media_id=wid,
                    victim_id=name_to_id.get(vname) if vname else None,
                    victim_name=vname,
                    ordinal=dd.get("ordinal"),
                    cause=dd["cause"],
                    cause_subtype=dd.get("cause_subtype"),
                    cause_detail=dd.get("cause_detail"),
                    death_type=dd["death_type"],
                    killer_id=name_to_id.get(kname) if kname else None,
                    killer_name=kname,
                    motive=dd.get("motive"),
                    motive_detail=dd.get("motive_detail"),
                    is_central_death=dd.get("is_central_death", False),
                    is_twist=dd.get("is_twist", False),
                    chapter_or_act=dd.get("chapter_or_act"),
                    notes=dd.get("notes"),
                )
                session.add(death)

            logger.info("INSERT %s  %s", wid, entry["title"])
            inserted += 1

    logger.info("Done -- inserted: %d  skipped: %d", inserted, skipped)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_seed()
