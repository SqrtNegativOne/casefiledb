"""Backfill killer_culpability and killer_circumstance on all existing deaths.

Sets both fields to 'needs_review' wherever they are absent.

Usage:
    uv run python scripts/backfill_killer_classification.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE_DATA = ROOT / "public" / "site_data.json"

DEFAULTS = {
    "killer_culpability": "needs_review",
    "killer_circumstance": "needs_review",
}


def _backfill_deaths(deaths: list[dict]) -> int:
    """Add missing classification fields to each death. Returns count of deaths touched."""
    touched = 0
    for death in deaths:
        changed = False
        for key, value in DEFAULTS.items():
            if key not in death:
                death[key] = value
                changed = True
        if changed:
            touched += 1
    return touched


def backfill() -> None:
    """Walk every death in site_data.json and fill in missing classification fields."""
    data: list[dict] = json.loads(SITE_DATA.read_text(encoding="utf-8"))

    total = 0
    for item in data:
        total += _backfill_deaths(item.get("deaths", []))
        for ep in item.get("episodes", []):
            total += _backfill_deaths(ep.get("deaths", []))
        for case in item.get("cases", []):
            total += _backfill_deaths(case.get("deaths", []))

    SITE_DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Backfilled {total} death(s) with needs_review classification.")


if __name__ == "__main__":
    backfill()
