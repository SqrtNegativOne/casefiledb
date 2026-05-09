#!/usr/bin/env python3
"""Fix enum casing in extracted temp/*.json files.

The Rust validator expects PascalCase for all enum fields.
AI_SCHEMA.md historically showed SCREAMING_SNAKE_CASE / lowercase,
so this script normalises any files that used the old conventions.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Mapping: normalised_lower_no_special -> PascalCase wire value
CAUSE_MAP = {
    "poisoned": "Poisoned", "shot": "Shot", "stabbed": "Stabbed",
    "clubbed": "Clubbed", "strangled": "Strangled", "drowned": "Drowned",
    "burned": "Burned", "hanged": "Hanged", "fell": "Fell",
    "crushed": "Crushed", "suffocated": "Suffocated", "exploded": "Exploded",
    "electrocuted": "Electrocuted", "frozen": "Frozen", "illness": "Illness",
    "eaten": "Eaten", "tornapart": "TornApart", "torn_apart": "TornApart",
    "vehicular": "Vehicular", "unknown": "Unknown", "other": "Other",
}

DEATH_TYPE_MAP = {
    "homicide": "Homicide", "attemptedhomicide": "AttemptedHomicide",
    "attempted_homicide": "AttemptedHomicide", "execution": "Execution",
    "accident": "Accident", "naturaldeath": "NaturalDeath",
    "natural_death": "NaturalDeath", "unknown": "Unknown",
}

MOTIVE_MAP = {
    "greedinheritance": "GreedInheritance", "greed_inheritance": "GreedInheritance",
    "greedfinancial": "GreedFinancial", "greed_financial": "GreedFinancial",
    "blackmail": "Blackmail", "jealousy": "Jealousy", "revenge": "Revenge",
    "ideology": "Ideology", "selfdefense": "SelfDefense", "self_defense": "SelfDefense",
    "concealment": "Concealment", "passion": "Passion",
    "vigilantejustice": "VigilanteJustice", "vigilante_justice": "VigilanteJustice",
    "freedom": "Freedom", "familyprotection": "FamilyProtection",
    "family_protection": "FamilyProtection", "pathological": "Pathological",
    "mercy": "Mercy", "penance": "Penance", "unknown": "Unknown", "other": "Other",
    "needsreview": "NeedsReview", "needs_review": "NeedsReview",
}

MENS_REA_MAP = {
    "purposely": "Purposely", "knowingly": "Knowingly", "recklessly": "Recklessly",
    "negligently": "Negligently", "accidentally": "Accidentally",
    "unknown": "Unknown", "needsreview": "NeedsReview", "needs_review": "NeedsReview",
}

CIRCUMSTANCE_MAP = {
    "justified": "Justified", "mitigated": "Mitigated", "neutral": "Neutral",
    "unknown": "Unknown", "needsreview": "NeedsReview", "needs_review": "NeedsReview",
}

TROPE_MAP = {
    "lockedroom": "LockedRoom", "locked_room": "LockedRoom",
    "impossiblecrime": "ImpossibleCrime", "impossible_crime": "ImpossibleCrime",
    "howcatchem": "HowCatchem", "how_catchem": "HowCatchem",
    "whodunit": "Whodunit", "whydunit": "Whydunit", "howdunit": "Howdunit",
    "dyingclue": "DyingClue", "dying_clue": "DyingClue",
    "alibitrick": "AlibiTrick", "alibi_trick": "AlibiTrick",
    "closedcircle": "ClosedCircle", "closed_circle": "ClosedCircle",
    "needleinhaystack": "NeedleInHaystack", "needle_in_haystack": "NeedleInHaystack",
    "leastlikelysuspect": "LeastLikelySuspect", "least_likely_suspect": "LeastLikelySuspect",
    "frameup": "FrameUp", "frame_up": "FrameUp",
    "mistakenidentity": "MistakenIdentity", "mistaken_identity": "MistakenIdentity",
}

ROLE_MAP = {
    "protagonist": "Protagonist", "antagonist": "Antagonist", "victim": "Victim",
    "detective": "Detective", "bystander": "Bystander", "unknown": "Unknown",
}

MEDIA_TYPE_MAP = {
    "book": "Book", "movie": "Movie", "tvshow": "TvShow", "tv_show": "TvShow",
    "tvepisode": "TvEpisode", "tv_episode": "TvEpisode", "game": "Game",
    "shortstory": "ShortStory", "short_story": "ShortStory",
    "play": "Play", "podcast": "Podcast",
}

EXT_STATUS_MAP = {
    "exists": "Exists", "none": "None", "needsreview": "NeedsReview",
    "needs_review": "NeedsReview",
}


def _norm(s: str) -> str:
    """Normalise to lowercase with no underscores for map lookup."""
    return s.lower().replace("_", "").replace("-", "")


def _fix_value(v: str | None, mapping: dict[str, str]) -> str | None:
    if v is None:
        return None
    key = v.lower().replace("-", "_")
    if key in mapping:
        return mapping[key]
    key2 = _norm(v)
    return mapping.get(key2, mapping.get(v.lower(), v))


def _fix_death(d: dict) -> dict:
    """Fix enum fields in a death object."""
    if "cause" in d:
        d["cause"] = _fix_value(d["cause"], CAUSE_MAP)
    if "death_type" in d:
        d["death_type"] = _fix_value(d["death_type"], DEATH_TYPE_MAP)
    if "motive" in d:
        d["motive"] = _fix_value(d["motive"], MOTIVE_MAP)
    # motive is required unless death_type is Accident or NaturalDeath
    if not d.get("motive") and d.get("death_type") not in ("Accident", "NaturalDeath"):
        d["motive"] = "Unknown"
    if "tropes" in d and isinstance(d["tropes"], list):
        d["tropes"] = [_fix_value(t, TROPE_MAP) for t in d["tropes"]]
    if "killers" in d and isinstance(d["killers"], list):
        for k in d["killers"]:
            if "mens_rea" in k:
                k["mens_rea"] = _fix_value(k["mens_rea"], MENS_REA_MAP)
            if "circumstance" in k:
                k["circumstance"] = _fix_value(k["circumstance"], CIRCUMSTANCE_MAP)
    return d


def _fix_person(p: dict) -> dict:
    if "role_in_story" in p:
        p["role_in_story"] = _fix_value(p["role_in_story"], ROLE_MAP)
    return p


def _fix_item(item: dict) -> dict:
    """Fix all enum fields in a media item."""
    if "media_type" in item:
        item["media_type"] = _fix_value(item["media_type"], MEDIA_TYPE_MAP)
    if "persons" in item and isinstance(item["persons"], list):
        item["persons"] = [_fix_person(p) for p in item["persons"]]
    if "deaths" in item and isinstance(item["deaths"], list):
        item["deaths"] = [_fix_death(d) for d in item["deaths"]]
    if "episodes" in item and isinstance(item["episodes"], list):
        for ep in item["episodes"]:
            if "persons" in ep:
                ep["persons"] = [_fix_person(p) for p in ep["persons"]]
            if "deaths" in ep:
                ep["deaths"] = [_fix_death(d) for d in ep["deaths"]]
    if "cases" in item and isinstance(item["cases"], list):
        for case in item["cases"]:
            if "persons" in case:
                case["persons"] = [_fix_person(p) for p in case["persons"]]
            if "deaths" in case:
                case["deaths"] = [_fix_death(d) for d in case["deaths"]]
    if "external_links" in item and isinstance(item["external_links"], dict):
        el = item["external_links"]
        for k in list(el.keys()):
            if k.endswith("_status"):
                el[k] = _fix_value(el[k], EXT_STATUS_MAP)
    return item


def fix_file(path: Path) -> int:
    """Fix a single file in place. Returns number of items fixed."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        fixed = [_fix_item(item) if isinstance(item, dict) else item for item in raw]
    elif isinstance(raw, dict):
        fixed = _fix_item(raw)
    else:
        return 0
    path.write_text(json.dumps(fixed, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(fixed) if isinstance(fixed, list) else 1


def main() -> None:
    """Fix all temp/*.json files (except worklist.json)."""
    paths = sorted(Path("temp").glob("*.json"))
    paths = [p for p in paths if p.name != "worklist.json"]
    if not paths:
        print("No files to fix.")
        return
    for p in paths:
        n = fix_file(p)
        print(f"  fixed {p.name} ({n} item(s))")
    print(f"Done. Fixed {len(paths)} file(s).")


if __name__ == "__main__":
    main()
