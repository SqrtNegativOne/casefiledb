#!/usr/bin/env python3
"""Post-ingest cleanup: sync worklist from site_data.json and delete stale raw files.

Run this after every `cargo run --bin ingest` call.

Actions:
  1. Mark any worklist item whose slug now exists in site_data.json as 'ingested'.
  2. Delete temp/raw/<slug>.{txt,json} for every newly-ingested slug.
  3. Remove all 'ingested' entries from the worklist (they're in site_data now).
  4. Print a summary.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


WORKLIST = Path("temp/worklist.json")
SITE_DATA = Path("public/site_data.json")
RAW_DIR = Path("temp/raw")


def _all_slugs(site_data: dict) -> set[str]:
    """Collect all slugs from every collection in site_data."""
    slugs: set[str] = set()
    for collection in site_data.values():
        if isinstance(collection, list):
            for item in collection:
                if isinstance(item, dict) and item.get("slug"):
                    slugs.add(item["slug"])
    return slugs


def main() -> None:
    """Sync worklist, delete raw files, trim ingested entries."""
    wl = json.loads(WORKLIST.read_text(encoding="utf-8"))
    items: list[dict] = wl["items"]

    site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
    ingested_slugs = _all_slugs(site_data)

    newly_ingested: list[str] = []
    for item in items:
        if item["state"] == "scraped" and item["slug"] in ingested_slugs:
            item["state"] = "ingested"
            newly_ingested.append(item["slug"])

    # Delete raw files for every ingested slug (newly or previously)
    deleted = 0
    for item in items:
        if item["state"] == "ingested":
            for ext in (".txt", ".json"):
                p = RAW_DIR / f"{item['slug']}{ext}"
                if p.exists():
                    p.unlink()
                    deleted += 1

    # Drop ingested entries — they're persisted in site_data
    wl["items"] = [i for i in items if i["state"] != "ingested"]
    WORKLIST.write_text(json.dumps(wl, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = Counter(i["state"] for i in wl["items"])
    print(f"Newly ingested: {len(newly_ingested)}")
    print(f"Raw files deleted: {deleted}")
    print(f"Worklist remaining: {dict(counts)}")


if __name__ == "__main__":
    main()
