"""Check real Wikidata IDs in site_data.json against live Wikidata labels and dates.

Usage:
    uv run python scripts/validate_wikidata.py [--limit N]

Skips synthetic IDs that don't match the pattern Q<digits>.
Prints a report of mismatches and unreachable IDs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE_DATA = ROOT / "docs" / "site_data.json"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
REAL_ID_RE = re.compile(r"^Q\d+$")
BATCH_SIZE = 50


def is_real_id(wikidata_id: str) -> bool:
    """Return True for proper Wikidata IDs (Q followed only by digits)."""
    return bool(REAL_ID_RE.match(wikidata_id))


def fetch_entities(ids: list[str]) -> dict:
    """Fetch a batch of Wikidata entities; return the parsed JSON response."""
    params = urllib.parse.urlencode(
        {
            "action": "wbgetentities",
            "ids": "|".join(ids),
            "props": "labels|claims",
            "languages": "en",
            "format": "json",
        }
    )
    url = f"{WIKIDATA_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "casefiledb-validator/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_year(claims: dict) -> int | None:
    """Pull the first year from P577 (publication date) or P571 (inception)."""
    for prop in ("P577", "P571"):
        for claim in claims.get(prop, []):
            try:
                time_val = (
                    claim["mainsnak"]["datavalue"]["value"]["time"]
                )
                year = int(time_val.lstrip("+").split("-")[0])
                if year > 0:
                    return year
            except (KeyError, ValueError, TypeError):
                continue
    return None


def check_batch(
    batch: list[dict],
    entities: dict,
) -> list[dict]:
    """Compare a batch of media items against their Wikidata entities.

    Returns a list of issue dicts.
    """
    issues: list[dict] = []
    for item in batch:
        wid = item["wikidata_id"]
        entity = entities.get(wid)

        if entity is None or entity.get("missing") == "":
            issues.append(
                {
                    "slug": item["slug"],
                    "wikidata_id": wid,
                    "title": item["title"],
                    "problem": "ID does not exist on Wikidata",
                }
            )
            continue

        wd_label = (
            entity.get("labels", {}).get("en", {}).get("value", "")
        )
        local_title = item.get("title", "")
        if wd_label and wd_label.lower() != local_title.lower():
            issues.append(
                {
                    "slug": item["slug"],
                    "wikidata_id": wid,
                    "title": local_title,
                    "problem": f"Title mismatch — Wikidata label: '{wd_label}'",
                }
            )

        wd_year = extract_year(entity.get("claims", {}))
        local_year = item.get("year")
        if wd_year and local_year and wd_year != local_year:
            issues.append(
                {
                    "slug": item["slug"],
                    "wikidata_id": wid,
                    "title": local_title,
                    "problem": f"Year mismatch — local: {local_year}, Wikidata: {wd_year}",
                }
            )

    return issues


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Check only the first N real IDs (0 = all).",
    )
    args = parser.parse_args()

    data: list[dict] = json.loads(SITE_DATA.read_text(encoding="utf-8"))

    real_items = [m for m in data if m.get("wikidata_id") and is_real_id(m["wikidata_id"])]
    synthetic_count = len(data) - len(real_items)

    if args.limit:
        real_items = real_items[: args.limit]

    print(
        f"Checking {len(real_items)} real IDs "
        f"(skipping {synthetic_count} synthetic)…"
    )

    all_issues: list[dict] = []

    for start in range(0, len(real_items), BATCH_SIZE):
        batch = real_items[start : start + BATCH_SIZE]
        ids = [m["wikidata_id"] for m in batch]
        batch_num = start // BATCH_SIZE + 1
        total_batches = (len(real_items) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch {batch_num}/{total_batches}: {ids[0]} … {ids[-1]}")

        try:
            response = fetch_entities(ids)
            entities = response.get("entities", {})
            all_issues.extend(check_batch(batch, entities))
        except Exception as exc:
            print(f"  ERROR fetching batch: {exc}", file=sys.stderr)

        if start + BATCH_SIZE < len(real_items):
            time.sleep(0.5)

    print()
    if not all_issues:
        print("No issues found.")
    else:
        print(f"{len(all_issues)} issue(s) found:\n")
        for issue in all_issues:
            print(f"  {issue['slug']}  ({issue['wikidata_id']})  {issue['title']}")
            print(f"    → {issue['problem']}")


if __name__ == "__main__":
    main()
