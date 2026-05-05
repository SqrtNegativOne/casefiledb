"""Migrate site_data.json to schema v2.

Changes applied:
  1. Deaths: killer_name + killer_culpability + killer_circumstance → killers list
  2. External links: full URLs → slug/ID fields + status fields

Usage:
    uv run python scripts/migrate_schema_v2.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).parent.parent
SITE_DATA = ROOT / "public" / "site_data.json"


# ---------------------------------------------------------------------------
# URL → slug/id extractors
# ---------------------------------------------------------------------------

def _wikipedia_slug(url: str) -> str:
    """Extract article slug from a Wikipedia URL, URL-decoding it."""
    m = re.search(r'wikipedia\.org/wiki/(.+)', url)
    return unquote(m.group(1)) if m else url


def _tvtropes_slug(url: str) -> str:
    """Extract Namespace/Title from a TVTropes URL."""
    m = re.search(r'tvtropes\.org/pmwiki/pmwiki\.php/(.+)', url)
    return m.group(1) if m else url


def _fandom_slug(url: str) -> str:
    """Extract subdomain/PageTitle from a Fandom URL."""
    m = re.match(r'https?://([^.]+)\.fandom\.com/wiki/(.+)', url)
    if m:
        return f"{m.group(1)}/{unquote(m.group(2))}"
    return url


def _goodreads_id(url: str) -> str:
    """Extract numeric book ID from a Goodreads URL."""
    m = re.search(r'/show/(\d+)', url)
    return m.group(1) if m else url


def _steam_id(url: str) -> str:
    """Extract numeric app ID from a Steam URL."""
    m = re.search(r'/app/(\d+)', url)
    return m.group(1) if m else url


def _itch_slug(url: str) -> str:
    """Extract author/game-slug from an itch.io URL."""
    m = re.match(r'https?://([^.]+)\.itch\.io/(.+)', url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return url


URL_EXTRACTORS = {
    "tvtropes_url":  ("tvtropes_slug",  _tvtropes_slug),
    "wikipedia_url": ("wikipedia_slug", _wikipedia_slug),
    "fandom_url":    ("fandom_slug",    _fandom_slug),
    "goodreads_url": ("goodreads_id",   _goodreads_id),
    "steam_url":     ("steam_id",       _steam_id),
    "itch_url":      ("itch_slug",      _itch_slug),
}

STATUS_FIELDS = {
    "tvtropes_slug":  "tvtropes_status",
    "wikipedia_slug": "wikipedia_status",
    "fandom_slug":    "fandom_status",
    "goodreads_id":   "goodreads_status",
    "steam_id":       "steam_status",
    "itch_slug":      "itch_status",
}


def _migrate_external_links(el: dict | None) -> dict | None:
    """Convert old URL fields to slug/id + status fields."""
    if el is None:
        return None
    new: dict = {}
    for old_field, (new_field, extractor) in URL_EXTRACTORS.items():
        url = el.get(old_field)
        status_field = STATUS_FIELDS[new_field]
        if url:
            new[new_field] = extractor(url)
            new[status_field] = "exists"
        else:
            new[new_field] = None
            new[status_field] = el.get(status_field, "needs_review")
    return new


# ---------------------------------------------------------------------------
# Death migration: flat killer fields → killers list
# ---------------------------------------------------------------------------

def _migrate_death(death: dict) -> dict:
    """Convert killer_name/killer_culpability/killer_circumstance to killers list."""
    d = {k: v for k, v in death.items()
         if k not in ("killer_name", "killer_culpability", "killer_circumstance")}

    killers = death.get("killers", [])
    if not killers:
        name = death.get("killer_name")
        if name:
            killers = [{
                "name": name,
                "mens_rea": death.get("killer_culpability", "needs_review"),
                "circumstance": death.get("killer_circumstance", "needs_review"),
            }]
        else:
            killers = []

    d["killers"] = killers
    return d


def _migrate_deaths(deaths: list[dict]) -> list[dict]:
    return [_migrate_death(d) for d in deaths]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def migrate() -> None:
    """Apply all v2 migrations to site_data.json in place."""
    data: list[dict] = json.loads(SITE_DATA.read_text(encoding="utf-8"))

    deaths_migrated = 0
    links_migrated = 0

    for item in data:
        item["deaths"] = _migrate_deaths(item.get("deaths", []))
        deaths_migrated += len(item["deaths"])

        for ep in item.get("episodes", []):
            ep["deaths"] = _migrate_deaths(ep.get("deaths", []))
            deaths_migrated += len(ep["deaths"])

        for case in item.get("cases", []):
            case["deaths"] = _migrate_deaths(case.get("deaths", []))
            deaths_migrated += len(case["deaths"])

        if item.get("external_links") is not None:
            item["external_links"] = _migrate_external_links(item["external_links"])
            links_migrated += 1

    SITE_DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Migrated {deaths_migrated} death(s), {links_migrated} external_links object(s).")


if __name__ == "__main__":
    migrate()
