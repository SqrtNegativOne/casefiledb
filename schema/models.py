"""Pydantic models for the murder mystery death catalog."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, model_validator

MediaType = Literal[
    "book", "movie", "tv_show", "tv_episode",
    "game", "short_story", "play", "podcast",
]

RoleInStory = Literal[
    "protagonist", "antagonist", "victim",
    "detective", "bystander", "unknown",
]

Cause = Literal[
    "POISONED", "SHOT", "STABBED", "CLUBBED", "STRANGLED",
    "DROWNED", "BURNED", "HANGED", "FELL", "CRUSHED",
    "SUFFOCATED", "EXPLODED", "ELECTROCUTED", "FROZEN",
    "ILLNESS", "EATEN", "TORN_APART", "VEHICULAR", "UNKNOWN", "OTHER",
]

DeathType = Literal[
    "murder", "attempted_murder", "manslaughter",
    "suicide", "accident", "natural_death", "execution", "unknown",
]

Motive = Literal[
    "greed_inheritance", "greed_financial", "blackmail", "jealousy",
    "revenge", "ideology", "self_defense", "concealment", "passion",
    "vigilante_justice", "freedom", "family_protection", "pathological",
    "mercy_killing", "penance",
    "unknown", "other",
]


class PersonModel(BaseModel):
    name: str
    is_fictional: bool = True
    role_in_story: Optional[RoleInStory] = None
    nationality: Optional[str] = None
    ethnicity: Optional[str] = None
    gender: Optional[str] = None
    approximate_age: Optional[str] = None
    profession: Optional[str] = None
    skills: Optional[list[str]] = None
    archetype: Optional[str] = None
    notes: Optional[str] = None


class DeathModel(BaseModel):
    victim_name: Optional[str] = None
    ordinal: Optional[int] = None
    cause: Cause
    cause_subtype: Optional[str] = None
    cause_detail: Optional[str] = None
    death_type: DeathType
    killer_name: Optional[str] = None
    motive: Optional[Motive] = None
    motive_detail: Optional[str] = None
    is_central_death: bool = False
    is_twist: bool = False
    chapter_or_act: Optional[str] = None
    notes: Optional[str] = None


class MediaModel(BaseModel):
    wikidata_id: str
    tmdb_id: Optional[str] = None
    igdb_id: Optional[str] = None
    isbn: Optional[str] = None
    title: str
    media_type: MediaType
    year: Optional[int] = None
    creator: Optional[str] = None
    series_name: Optional[str] = None
    series_number: Optional[float] = None
    notes: Optional[str] = None
    tags: list[str] = []
    persons: list[PersonModel] = []
    deaths: list[DeathModel] = []

    @model_validator(mode="after")
    def _check_death_names(self) -> "MediaModel":
        known = {p.name for p in self.persons}
        for death in self.deaths:
            if death.victim_name and death.victim_name not in known:
                raise ValueError(
                    f"victim_name '{death.victim_name}' not in persons for '{self.title}'"
                )
            if death.killer_name and death.killer_name not in known:
                raise ValueError(
                    f"killer_name '{death.killer_name}' not in persons for '{self.title}'"
                )
        return self
