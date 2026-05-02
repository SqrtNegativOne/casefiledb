"""JSON importer for the murder mystery death catalog."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select

from schema.database import get_session
from schema.models import Death, Media, Person, Tag, media_tag

logger = logging.getLogger(__name__)


def import_json(path: str) -> dict[str, Any]:
    """Import media objects from a JSON file into the database.

    The file must contain a JSON array of media objects matching the schema
    produced by export_json().  The entire import runs in one transaction;
    any unhandled exception rolls back all changes.

    Args:
        path: Path to the source JSON file.

    Returns:
        {"inserted": int, "updated": int, "skipped": int, "errors": list[str]}
    """
    results: dict[str, Any] = {
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": [],
    }

    raw = Path(path).read_text(encoding="utf-8")
    items: list[dict[str, Any]] = json.loads(raw)

    with get_session() as session:
        for item in items:
            wikidata_id: str | None = item.get("wikidata_id")
            if not wikidata_id:
                results["errors"].append(f"Item missing wikidata_id: {item!r}")
                continue

            # 1. Upsert media row.
            existing_media = session.get(Media, wikidata_id)
            if existing_media:
                _update_media(existing_media, item)
                results["updated"] += 1
            else:
                session.add(_build_media(item))
                results["inserted"] += 1

            session.flush()

            # 2-3. Upsert tags; create MediaTag links (skip duplicates).
            for tag_name in item.get("tags", []):
                tag = session.execute(
                    select(Tag).where(Tag.name == tag_name)
                ).scalar_one_or_none()
                if tag is None:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    session.flush()

                link_exists = session.execute(
                    select(media_tag).where(
                        media_tag.c.media_id == wikidata_id,
                        media_tag.c.tag_id == tag.id,
                    )
                ).first()
                if link_exists is None:
                    session.execute(
                        media_tag.insert().values(
                            media_id=wikidata_id, tag_id=tag.id
                        )
                    )

            # 4. Upsert persons by (media_id, name).
            person_name_to_id: dict[str, int] = {}
            for person_data in item.get("persons", []):
                name: str = person_data.get("name", "")
                existing_person = session.execute(
                    select(Person).where(
                        Person.media_id == wikidata_id,
                        Person.name == name,
                    )
                ).scalar_one_or_none()

                if existing_person is not None:
                    _update_person(existing_person, person_data)
                    session.flush()
                    person_name_to_id[name] = existing_person.id
                else:
                    p = _build_person(wikidata_id, person_data)
                    session.add(p)
                    session.flush()
                    person_name_to_id[name] = p.id

            # 5. Insert deaths; skip if (media_id, ordinal) already exists.
            for death_data in item.get("deaths", []):
                ordinal: int | None = death_data.get("ordinal")
                if ordinal is not None:
                    exists = session.execute(
                        select(Death).where(
                            Death.media_id == wikidata_id,
                            Death.ordinal == ordinal,
                        )
                    ).scalar_one_or_none()
                    if exists is not None:
                        results["skipped"] += 1
                        continue

                # victim_id and killer_id resolved from person names within this media.
                session.add(_build_death(wikidata_id, death_data, person_name_to_id))

    return results


# ---------------------------------------------------------------------------
# Internal builders / updaters
# ---------------------------------------------------------------------------

def _build_media(data: dict[str, Any]) -> Media:
    return Media(
        wikidata_id=data["wikidata_id"],
        tmdb_id=data.get("tmdb_id"),
        igdb_id=data.get("igdb_id"),
        isbn=data.get("isbn"),
        title=data["title"],
        media_type=data["media_type"],
        year=data.get("year"),
        creator=data.get("creator"),
        series_name=data.get("series_name"),
        series_number=data.get("series_number"),
        notes=data.get("notes"),
    )


def _update_media(media: Media, data: dict[str, Any]) -> None:
    media.tmdb_id = data.get("tmdb_id", media.tmdb_id)
    media.igdb_id = data.get("igdb_id", media.igdb_id)
    media.isbn = data.get("isbn", media.isbn)
    media.title = data.get("title", media.title)
    media.media_type = data.get("media_type", media.media_type)
    media.year = data.get("year", media.year)
    media.creator = data.get("creator", media.creator)
    media.series_name = data.get("series_name", media.series_name)
    media.series_number = data.get("series_number", media.series_number)
    media.notes = data.get("notes", media.notes)


def _build_person(media_id: str, data: dict[str, Any]) -> Person:
    skills = data.get("skills")
    if isinstance(skills, list):
        skills = json.dumps(skills)
    return Person(
        media_id=media_id,
        name=data["name"],
        is_fictional=data.get("is_fictional", True),
        role_in_story=data.get("role_in_story"),
        nationality=data.get("nationality"),
        ethnicity=data.get("ethnicity"),
        gender=data.get("gender"),
        approximate_age=data.get("approximate_age"),
        profession=data.get("profession"),
        skills=skills,
        archetype=data.get("archetype"),
        notes=data.get("notes"),
    )


def _update_person(person: Person, data: dict[str, Any]) -> None:
    skills = data.get("skills", person.skills)
    if isinstance(skills, list):
        skills = json.dumps(skills)
    person.is_fictional = data.get("is_fictional", person.is_fictional)
    person.role_in_story = data.get("role_in_story", person.role_in_story)
    person.nationality = data.get("nationality", person.nationality)
    person.ethnicity = data.get("ethnicity", person.ethnicity)
    person.gender = data.get("gender", person.gender)
    person.approximate_age = data.get("approximate_age", person.approximate_age)
    person.profession = data.get("profession", person.profession)
    person.skills = skills
    person.archetype = data.get("archetype", person.archetype)
    person.notes = data.get("notes", person.notes)


def _build_death(
    media_id: str,
    data: dict[str, Any],
    person_map: dict[str, int],
) -> Death:
    victim_name: str | None = data.get("victim_name")
    killer_name: str | None = data.get("killer_name")
    return Death(
        media_id=media_id,
        victim_id=person_map.get(victim_name) if victim_name else None,
        victim_name=victim_name,
        ordinal=data.get("ordinal"),
        cause=data["cause"],
        cause_subtype=data.get("cause_subtype"),
        cause_detail=data.get("cause_detail"),
        death_type=data["death_type"],
        killer_id=person_map.get(killer_name) if killer_name else None,
        killer_name=killer_name,
        motive=data.get("motive"),
        motive_detail=data.get("motive_detail"),
        is_central_death=data.get("is_central_death", False),
        is_twist=data.get("is_twist", False),
        chapter_or_act=data.get("chapter_or_act"),
        notes=data.get("notes"),
    )
