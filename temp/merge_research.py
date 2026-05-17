#!/usr/bin/env python3
"""Merge researched death data into site_data.json.

Reads all JSON files from temp/research/, matches each entry to an existing
item in site_data.json by wikidata_id or slug, and updates persons + deaths.
"""

import json
import sys
from pathlib import Path
from typing import Any


SITE_DATA = Path("public/site_data.json")
RESEARCH_DIR = Path("temp/research")


def load_json(path: Path) -> Any:
    """Load JSON from path."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    """Save JSON to path with pretty formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def build_lookups(site_data: dict) -> tuple[dict, dict]:
    """Build wikidata_id and slug lookup dicts pointing to item dicts."""
    by_wikidata: dict[str, dict] = {}
    by_slug: dict[str, dict] = {}
    for collection in site_data.values():
        for item in collection:
            wid = item.get("wikidata_id")
            slug = item.get("slug")
            if wid:
                by_wikidata[wid] = item
            if slug:
                by_slug[slug] = item
    return by_wikidata, by_slug


def is_placeholder_death(deaths: list[dict]) -> bool:
    """Return True if deaths list contains only the NeedsReview placeholder."""
    if len(deaths) != 1:
        return False
    d = deaths[0]
    return (
        d.get("cause") == "Unstated"
        and d.get("death_type") == "Homicide"
        and d.get("motive") == "NeedsReview"
        and d.get("killers") == []
        and d.get("is_central_death") is True
    )


def main() -> None:
    """Run the merge."""
    if not SITE_DATA.exists():
        print(f"ERROR: {SITE_DATA} not found", file=sys.stderr)
        sys.exit(1)

    research_files = sorted(RESEARCH_DIR.glob("*.json"))
    if not research_files:
        print(f"No JSON files found in {RESEARCH_DIR}")
        sys.exit(0)

    site_data = load_json(SITE_DATA)
    by_wikidata, by_slug = build_lookups(site_data)

    updated = 0
    skipped_no_match = 0
    skipped_already_filled = 0
    errors: list[str] = []

    for research_file in research_files:
        print(f"\nProcessing {research_file.name}...")
        try:
            entries = load_json(research_file)
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error in {research_file.name}: {e}")
            continue

        if not isinstance(entries, list):
            errors.append(f"{research_file.name}: expected a JSON array at top level")
            continue

        for entry in entries:
            entry_id = entry.get("id")
            if not entry_id:
                errors.append(f"Entry missing 'id' in {research_file.name}")
                continue

            item = by_wikidata.get(entry_id) or by_slug.get(entry_id)
            if item is None:
                errors.append(f"  No match for id '{entry_id}'")
                skipped_no_match += 1
                continue

            title = item.get("title", entry_id)

            new_deaths = entry.get("deaths", [])
            new_persons = entry.get("persons", [])

            # Only update if research provides real data (not another placeholder)
            if not new_deaths or is_placeholder_death(new_deaths):
                print(f"  SKIP (no real data): {title}")
                skipped_already_filled += 1
                continue

            existing_deaths = item.get("deaths", [])
            if existing_deaths and not is_placeholder_death(existing_deaths):
                print(f"  SKIP (already has real data): {title}")
                skipped_already_filled += 1
                continue

            item["persons"] = new_persons
            item["deaths"] = new_deaths
            updated += 1
            print(f"  UPDATED: {title} ({len(new_deaths)} death(s))")

    save_json(SITE_DATA, site_data)

    print(f"\n{'='*50}")
    print(f"Updated:          {updated}")
    print(f"Skipped (no data):{skipped_already_filled}")
    print(f"Skipped (no match):{skipped_no_match}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
