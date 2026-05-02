"""Engine, session factory, and database initialisation."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from catalog.models import Base

load_dotenv()

_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/catalog.db")

# Auto-create the parent directory for SQLite files.
if _DATABASE_URL.startswith("sqlite:///"):
    _db_path = Path(_DATABASE_URL.removeprefix("sqlite:///"))
    _db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(_DATABASE_URL, echo=False)


@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record) -> None:
    """SQLite disables FK enforcement by default; flip it on per connection."""
    if "sqlite" in _DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine, autocommit=False, autoflush=False
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Yield a transactional session.

    Commits on clean exit, rolls back and re-raises on any exception.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create all tables if they do not exist.

    Use Alembic (`alembic upgrade head`) for production migrations.
    """
    Base.metadata.create_all(bind=engine)
