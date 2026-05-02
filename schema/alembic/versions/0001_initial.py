"""Initial schema -- all tables.

Revision ID: 0001
Revises:
Create Date: 2026-05-02
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "media",
        sa.Column("wikidata_id", sa.String(), nullable=False),
        sa.Column("tmdb_id", sa.String(), nullable=True),
        sa.Column("igdb_id", sa.String(), nullable=True),
        sa.Column("isbn", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("media_type", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("creator", sa.String(), nullable=True),
        sa.Column("series_name", sa.String(), nullable=True),
        sa.Column("series_number", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "media_type IN ('book','movie','tv_show','tv_episode',"
            "'game','short_story','play','podcast')",
            name="ck_media_media_type",
        ),
        sa.PrimaryKeyConstraint("wikidata_id"),
    )

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "media_tag",
        sa.Column("media_id", sa.String(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["media_id"], ["media.wikidata_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("media_id", "tag_id"),
    )

    op.create_table(
        "person",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("media_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_fictional", sa.Boolean(), nullable=False),
        sa.Column("role_in_story", sa.String(), nullable=True),
        sa.Column("nationality", sa.String(), nullable=True),
        sa.Column("ethnicity", sa.String(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("approximate_age", sa.String(), nullable=True),
        sa.Column("profession", sa.String(), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("archetype", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "role_in_story IS NULL OR role_in_story IN ("
            "'protagonist','antagonist','victim','detective','bystander','unknown')",
            name="ck_person_role_in_story",
        ),
        sa.ForeignKeyConstraint(
            ["media_id"], ["media.wikidata_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "death",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("media_id", sa.String(), nullable=False),
        sa.Column("victim_id", sa.Integer(), nullable=True),
        sa.Column("victim_name", sa.String(), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=True),
        sa.Column("cause", sa.String(), nullable=False),
        sa.Column("cause_subtype", sa.String(), nullable=True),
        sa.Column("cause_detail", sa.Text(), nullable=True),
        sa.Column("death_type", sa.String(), nullable=False),
        sa.Column("killer_id", sa.Integer(), nullable=True),
        sa.Column("killer_name", sa.String(), nullable=True),
        sa.Column("motive", sa.String(), nullable=True),
        sa.Column("motive_detail", sa.Text(), nullable=True),
        sa.Column("is_central_death", sa.Boolean(), nullable=False),
        sa.Column("is_twist", sa.Boolean(), nullable=False),
        sa.Column("chapter_or_act", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "cause IN ('POISONED','SHOT','STABBED','CLUBBED','STRANGLED',"
            "'DROWNED','BURNED','HANGED','FELL','CRUSHED','SUFFOCATED',"
            "'EXPLODED','ELECTROCUTED','FROZEN','ILLNESS','EATEN','TORN_APART','OTHER')",
            name="ck_death_cause",
        ),
        sa.CheckConstraint(
            "death_type IN ('murder','attempted_murder','manslaughter',"
            "'suicide','accident','natural_death','execution','unknown')",
            name="ck_death_death_type",
        ),
        sa.CheckConstraint(
            "motive IS NULL OR motive IN ("
            "'greed_inheritance','greed_financial','blackmail','jealousy',"
            "'revenge','ideology','self_defense','concealment','passion','unknown','other')",
            name="ck_death_motive",
        ),
        sa.ForeignKeyConstraint(
            ["media_id"], ["media.wikidata_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["victim_id"], ["person.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["killer_id"], ["person.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("death")
    op.drop_table("person")
    op.drop_table("media_tag")
    op.drop_table("tag")
    op.drop_table("media")
