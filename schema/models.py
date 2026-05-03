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
    """A character or person referenced in a death event."""

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
    """A single death event."""

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


def _validate_death_refs(
    persons: list[PersonModel], deaths: list[DeathModel], context: str
) -> None:
    """Raise ValueError if any death references a name absent from persons."""
    known = {p.name for p in persons}
    for death in deaths:
        if death.victim_name and death.victim_name not in known:
            raise ValueError(
                f"victim_name '{death.victim_name}' not in persons for '{context}'"
            )
        if death.killer_name and death.killer_name not in known:
            raise ValueError(
                f"killer_name '{death.killer_name}' not in persons for '{context}'"
            )


class TvEpisodeModel(BaseModel):
    """A single episode nested within a tv_show entry."""

    wikidata_id: Optional[str] = None
    title: str
    season: Optional[int] = None
    episode_number: Optional[int] = None
    year: Optional[int] = None
    notes: Optional[str] = None
    tags: list[str] = []
    persons: list[PersonModel] = []
    deaths: list[DeathModel] = []

    @model_validator(mode="after")
    def _validate_deaths(self) -> "TvEpisodeModel":
        """Check all death names exist in this episode's persons list."""
        _validate_death_refs(self.persons, self.deaths, self.title)
        return self


class GameCaseModel(BaseModel):
    """A case or chapter nested within a game entry."""

    title: str
    case_number: Optional[int] = None
    notes: Optional[str] = None
    tags: list[str] = []
    persons: list[PersonModel] = []
    deaths: list[DeathModel] = []

    @model_validator(mode="after")
    def _validate_deaths(self) -> "GameCaseModel":
        """Check all death names exist in this case's persons list."""
        _validate_death_refs(self.persons, self.deaths, self.title)
        return self


class MediaModel(BaseModel):
    """A top-level media item (book, show, game, episode, etc.)."""

    slug: Optional[str] = None
    wikidata_id: Optional[str] = None
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
    episodes: list[TvEpisodeModel] = []
    cases: list[GameCaseModel] = []

    @model_validator(mode="after")
    def _validate_deaths_and_slug(self) -> "MediaModel":
        """Populate slug from wikidata_id if absent; validate death name refs."""
        if self.slug is None:
            if self.wikidata_id:
                self.slug = self.wikidata_id
            else:
                raise ValueError("Either slug or wikidata_id must be provided")
        _validate_death_refs(self.persons, self.deaths, self.title)
        return self
