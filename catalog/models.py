"""SQLAlchemy ORM models for the murder mystery death catalog.

All enum-like columns use TEXT + CHECK constraint rather than SQLAlchemy's
Enum type for reliable SQLite support.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Association table -- no ORM class needed.
media_tag = Table(
    "media_tag",
    Base.metadata,
    Column(
        "media_id",
        String,
        ForeignKey("media.wikidata_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Media(Base):
    __tablename__ = "media"
    __table_args__ = (
        CheckConstraint(
            "media_type IN ('book','movie','tv_show','tv_episode',"
            "'game','short_story','play','podcast')",
            name="ck_media_media_type",
        ),
    )

    wikidata_id: Mapped[str] = mapped_column(String, primary_key=True)
    tmdb_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    igdb_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    isbn: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    media_type: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    creator: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    series_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    series_number: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tags: Mapped[List[Tag]] = relationship(
        "Tag", secondary=media_tag, back_populates="media"
    )
    persons: Mapped[List[Person]] = relationship(
        "Person", back_populates="media", cascade="all, delete-orphan"
    )
    deaths: Mapped[List[Death]] = relationship(
        "Death", back_populates="media", cascade="all, delete-orphan"
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    media: Mapped[List[Media]] = relationship(
        "Media", secondary=media_tag, back_populates="tags"
    )


class Person(Base):
    __tablename__ = "person"
    __table_args__ = (
        CheckConstraint(
            "role_in_story IS NULL OR role_in_story IN ("
            "'protagonist','antagonist','victim','detective','bystander','unknown')",
            name="ck_person_role_in_story",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    media_id: Mapped[str] = mapped_column(
        String, ForeignKey("media.wikidata_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_fictional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role_in_story: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ethnicity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    approximate_age: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Stored as a JSON array string: '["toxicology","deduction"]'
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    archetype: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    media: Mapped[Media] = relationship("Media", back_populates="persons")
    deaths_as_victim: Mapped[List[Death]] = relationship(
        "Death",
        back_populates="victim",
        foreign_keys="[Death.victim_id]",
    )
    deaths_as_killer: Mapped[List[Death]] = relationship(
        "Death",
        back_populates="killer",
        foreign_keys="[Death.killer_id]",
    )


class Death(Base):
    __tablename__ = "death"
    __table_args__ = (
        CheckConstraint(
            "cause IN ('POISONED','SHOT','STABBED','CLUBBED','STRANGLED',"
            "'DROWNED','BURNED','HANGED','FELL','CRUSHED','SUFFOCATED',"
            "'EXPLODED','ELECTROCUTED','FROZEN','ILLNESS','EATEN','TORN_APART','OTHER')",
            name="ck_death_cause",
        ),
        CheckConstraint(
            "death_type IN ('murder','attempted_murder','manslaughter',"
            "'suicide','accident','natural_death','execution','unknown')",
            name="ck_death_death_type",
        ),
        CheckConstraint(
            "motive IS NULL OR motive IN ("
            "'greed_inheritance','greed_financial','blackmail','jealousy',"
            "'revenge','ideology','self_defense','concealment','passion','unknown','other')",
            name="ck_death_motive",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    media_id: Mapped[str] = mapped_column(
        String, ForeignKey("media.wikidata_id", ondelete="CASCADE"), nullable=False
    )
    victim_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("person.id", ondelete="SET NULL"), nullable=True
    )
    victim_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ordinal: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    cause: Mapped[str] = mapped_column(String, nullable=False)
    cause_subtype: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cause_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    death_type: Mapped[str] = mapped_column(String, nullable=False)

    killer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("person.id", ondelete="SET NULL"), nullable=True
    )
    killer_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    motive: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    motive_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_central_death: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_twist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    chapter_or_act: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    media: Mapped[Media] = relationship("Media", back_populates="deaths")
    victim: Mapped[Optional[Person]] = relationship(
        "Person",
        back_populates="deaths_as_victim",
        foreign_keys="[Death.victim_id]",
    )
    killer: Mapped[Optional[Person]] = relationship(
        "Person",
        back_populates="deaths_as_killer",
        foreign_keys="[Death.killer_id]",
    )
