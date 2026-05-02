# Murder Mystery Death Catalog

A SQLAlchemy 2.x database layer for cataloguing deaths across murder-mystery
fiction -- novels, short stories, films, games, and more.

## Setup

```bash
# Install dependencies (uv recommended)
uv pip install -r requirements.txt

# Copy and edit env config
cp .env.example .env

# Run migrations (creates the SQLite database)
python -m alembic upgrade head

# Seed with six Agatha Christie works
python seed.py
```

## Project layout

```
catalog/
  __init__.py     package root
  models.py       SQLAlchemy ORM models (Media, Tag, Person, Death)
  database.py     engine, SessionLocal, get_session(), init_db()
  importer.py     import_json(path) -> dict
  exporter.py     export_json(path, media_id=None) -> None
  seed.py         six idempotent seed entries
alembic/
  env.py          migration environment (reads DATABASE_URL from .env)
  versions/       migration scripts
alembic.ini       Alembic config
.env              local config (not committed)
.env.example      template
requirements.txt  pinned dependencies
seed.py           python seed.py entry point
```

## Usage

```python
from catalog.database import get_session, init_db
from catalog.models import Media, Death
from catalog.importer import import_json
from catalog.exporter import export_json
from sqlalchemy import select

# One-time setup (Alembic handles this in production)
init_db()

# Query
with get_session() as session:
    deaths = session.execute(
        select(Death).where(Death.cause == "POISONED")
    ).scalars().all()

# Round-trip
export_json("backup.json")
import_json("backup.json")

# Export a single title
export_json("orient.json", media_id="Q229390")
```

## Schema overview

| Table      | PK            | Notes                                        |
|------------|---------------|----------------------------------------------|
| `media`    | `wikidata_id` | Anchored to Wikidata; one row per work        |
| `tag`      | `id`          | Shared vocabulary (golden-age, cozy, etc.)   |
| `media_tag`| composite     | Many-to-many join                            |
| `person`   | `id`          | Scoped to a single media; fictional by default|
| `death`    | `id`          | Victim + killer FK into person; ordinal order|

All enum-like columns use `TEXT + CHECK` constraints for SQLite compatibility.

## Environment variables

| Variable       | Default                        | Description             |
|----------------|--------------------------------|-------------------------|
| `DATABASE_URL` | `sqlite:///./data/catalog.db`  | SQLAlchemy database URL |

## Running migrations manually

```bash
# Generate a new revision after model changes
python -m alembic revision --autogenerate -m "describe change"

# Apply
python -m alembic upgrade head

# Rollback one step
python -m alembic downgrade -1
```
