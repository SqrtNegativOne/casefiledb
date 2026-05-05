"""One-time migration: rename cause_subtype → means; enforce new motive rules.

Changes applied to every death in every scope:
  - cause_subtype renamed to means
  - means added (needs_review) for causes that lacked it, except:
      UNKNOWN  → means: "unknown"  (cause unknown implies means unknown)
      OTHER    → no means field (Other carries no mandatory means)
  - accident / natural_death deaths: motive removed, appended to notes
  - unknown death_type without motive: motive set to needs_review
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE_DATA = ROOT / "public" / "site_data.json"

CAUSES_NEEDING_MEANS: frozenset[str] = frozenset({
    "POISONED", "SHOT", "STABBED", "CLUBBED", "STRANGLED",
    "DROWNED", "BURNED", "HANGED", "FELL", "CRUSHED",
    "SUFFOCATED", "EXPLODED", "ELECTROCUTED", "FROZEN",
    "ILLNESS", "EATEN", "TORN_APART", "VEHICULAR", "UNKNOWN",
})

DEATH_TYPES_NEEDING_MOTIVE: frozenset[str] = frozenset({
    "murder", "attempted_murder", "manslaughter",
    "suicide", "execution", "unknown",
})

DEATH_TYPES_NO_MOTIVE: frozenset[str] = frozenset({"accident", "natural_death"})


def migrate_death(death: dict) -> dict:
    """Return death dict with all migrations applied."""
    cause = death.get("cause", "")
    death_type = death.get("death_type", "")

    # Rename cause_subtype → means (only keep the value if non-null)
    if "cause_subtype" in death:
        val = death.pop("cause_subtype")
        if val is not None:
            death["means"] = val

    # Drop means: null — treated identically to means being absent
    if death.get("means") is None:
        death.pop("means", None)

    # Add means where required but missing
    if cause in CAUSES_NEEDING_MEANS and "means" not in death:
        death["means"] = "unknown" if cause == "UNKNOWN" else "needs_review"

    # Strip means from OTHER (no means field in the new schema)
    if cause == "OTHER":
        death.pop("means", None)

    # accident / natural_death: remove motive, append it to notes
    if death_type in DEATH_TYPES_NO_MOTIVE and death.get("motive") is not None:
        motive = death.pop("motive")
        motive_detail = death.pop("motive_detail", None)
        note = f"[Former motive: {motive}"
        if motive_detail:
            note += f" — {motive_detail}"
        note += "]"
        existing = (death.get("notes") or "").strip()
        death["notes"] = f"{existing} {note}".strip() if existing else note

    # Other death types: ensure motive is present
    if death_type in DEATH_TYPES_NEEDING_MOTIVE and death.get("motive") is None:
        death["motive"] = "needs_review"

    return death


def migrate_scope(scope: dict) -> None:
    """Migrate all deaths inside a scope in place."""
    scope["deaths"] = [migrate_death(d) for d in scope.get("deaths", [])]


def main() -> None:
    """Run migration on public/site_data.json."""
    data: list[dict] = json.loads(SITE_DATA.read_text(encoding="utf-8"))

    for item in data:
        migrate_scope(item)
        for ep in item.get("episodes", []):
            migrate_scope(ep)
        for case in item.get("cases", []):
            migrate_scope(case)

    SITE_DATA.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("Migration complete.")


if __name__ == "__main__":
    main()
