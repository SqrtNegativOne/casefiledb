"""Validate temp/*.json and append to docs/site_data.json.

Usage:
    uv run python scripts/ingest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).parent.parent
TEMP_DIR = ROOT / "temp"
SITE_DATA = ROOT / "public" / "site_data.json"

sys.path.insert(0, str(ROOT))
from schema.models import MediaModel


def load_site_data() -> list[dict]:
    if SITE_DATA.exists():
        return json.loads(SITE_DATA.read_text(encoding="utf-8"))
    return []


def ingest() -> None:
    temp_files = sorted(TEMP_DIR.glob("*.json"))
    if not temp_files:
        print("Nothing in temp/ to ingest.")
        return

    incoming: list[dict] = []
    for path in temp_files:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            raw = [raw]
        incoming.extend(raw)

    print(f"Validating {len(incoming)} item(s) from {len(temp_files)} file(s)...")

    errors: list[str] = []
    validated: list[dict] = []
    for item in incoming:
        try:
            model = MediaModel.model_validate(item)
            validated.append(model.model_dump(mode="json"))
        except ValidationError as exc:
            title = item.get("title") or item.get("wikidata_id") or repr(item)
            errors.append(f"  {title}:\n    " + "\n    ".join(str(e["msg"]) + f" ({'.'.join(str(l) for l in e['loc'])})" for e in exc.errors()))

    if errors:
        print("Validation failed — temp/ not cleared:\n")
        for err in errors:
            print(err)
        sys.exit(1)

    existing = load_site_data()
    existing_slugs = {m["slug"] for m in existing}

    added, skipped = 0, 0
    for item in validated:
        if item["slug"] in existing_slugs:
            print(f"  SKIP (already exists): {item['title']} ({item['slug']})")
            skipped += 1
        else:
            existing.append(item)
            existing_slugs.add(item["slug"])
            added += 1

    SITE_DATA.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    for path in temp_files:
        path.unlink()

    print(f"\nDone: {added} added, {skipped} skipped. temp/ cleared.")


if __name__ == "__main__":
    ingest()
