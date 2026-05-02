"""Merge the three seed data parts and import into the database."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from catalog.database import init_db
from catalog.importer import import_json

logging.basicConfig(level=logging.INFO, format="%(message)s")

PARTS = [
    "seed_data_part1.json",
    "seed_data_part2.json",
    "seed_data_part3.json",
]

merged: list = []
for part in PARTS:
    p = Path(part)
    if not p.exists():
        logging.warning("Missing: %s", part)
        continue
    data = json.loads(p.read_text(encoding="utf-8"))
    merged.extend(data)
    logging.info("Loaded %d records from %s", len(data), part)

merged_path = Path("seed_data_merged.json")
merged_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
logging.info("Wrote %d total records to %s", len(merged), merged_path)

init_db()
result = import_json(str(merged_path))
logging.info(
    "Import complete — inserted: %d, updated: %d, skipped: %d, errors: %d",
    result["inserted"],
    result["updated"],
    result["skipped"],
    len(result["errors"]),
)
if result["errors"]:
    for err in result["errors"]:
        logging.error("  ERROR: %s", err)
