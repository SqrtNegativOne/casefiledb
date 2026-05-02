"""JSON exporter for the murder mystery death catalog."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from catalog.database import get_session
from catalog.models import Death, Media, Person

logger = logging.getLogger(__name__)


def export_json(path: str, media_id: Optional[str] = None) -> None:
    """Export media records to a JSON file.

    The output schema is identical to what import_json() expects, so
    export -> import is a lossless round-trip.

    Args:
        path:     Destination file path.
        media_id: When given, export only that wikidata_id; otherwise export all.
    """
    with get_session() as session:
        query = (
            select(Media)
            .options(
                joinedload(Media.tags),
                joinedload(Media.persons),
                joinedload(Media.deaths),
            )
        )
        if media_id is not None:
            query = query.where(Media.wikidata_id == media_id)

        records = session.execute(query).unique().scalars().all()
        output = [_serialize_media(m) for m in records]

    Path(path).write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Exported %d record(s) to %s", len(output), path)


def _serialize_media(media: Media) -> dict[str, Any]:
    return {
        "wikidata_id": media.wikidata_id,
        "tmdb_id": media.tmdb_id,
        "igdb_id": media.igdb_id,
        "isbn": media.isbn,
        "title": media.title,
        "media_type": media.media_type,
        "year": media.year,
        "creator": media.creator,
        "series_name": media.series_name,
        "series_number": media.series_number,
        "notes": media.notes,
        "tags": [t.name for t in media.tags],
        "persons": [_serialize_person(p) for p in media.persons],
        "deaths": [
            _serialize_death(d)
            for d in sorted(media.deaths, key=lambda d: d.ordinal or 0)
        ],
    }


def _serialize_person(person: Person) -> dict[str, Any]:
    skills: Any = person.skills
    if skills is not None:
        try:
            skills = json.loads(skills)
        except (json.JSONDecodeError, TypeError):
            skills = [skills]
    return {
        "name": person.name,
        "is_fictional": person.is_fictional,
        "role_in_story": person.role_in_story,
        "nationality": person.nationality,
        "ethnicity": person.ethnicity,
        "gender": person.gender,
        "approximate_age": person.approximate_age,
        "profession": person.profession,
        "skills": skills,
        "archetype": person.archetype,
        "notes": person.notes,
    }


def _serialize_death(death: Death) -> dict[str, Any]:
    return {
        "victim_name": death.victim_name,
        "ordinal": death.ordinal,
        "cause": death.cause,
        "cause_subtype": death.cause_subtype,
        "cause_detail": death.cause_detail,
        "death_type": death.death_type,
        "killer_name": death.killer_name,
        "motive": death.motive,
        "motive_detail": death.motive_detail,
        "is_central_death": death.is_central_death,
        "is_twist": death.is_twist,
        "chapter_or_act": death.chapter_or_act,
        "notes": death.notes,
    }
