#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fix enum casing in extracted JSON files to match Rust model definitions."""
import json
from pathlib import Path

COLUMBO_FILES = sorted(Path("temp").glob("columbo-s*.json"))

# Maps for all enum conversions (handle both uppercase and lowercase inputs)
def fix_cause(val: str) -> str:
    """Fix Cause enum casing."""
    mapping = {
        "POISONED": "Poisoned", "poisoned": "Poisoned",
        "SHOT": "Shot", "shot": "Shot",
        "STABBED": "Stabbed", "stabbed": "Stabbed",
        "CLUBBED": "Clubbed", "clubbed": "Clubbed",
        "STRANGLED": "Strangled", "strangled": "Strangled",
        "DROWNED": "Drowned", "drowned": "Drowned",
        "BURNED": "Burned", "burned": "Burned",
        "HANGED": "Hanged", "hanged": "Hanged",
        "FELL": "Fell", "fell": "Fell",
        "CRUSHED": "Crushed", "crushed": "Crushed",
        "SUFFOCATED": "Suffocated", "suffocated": "Suffocated",
        "EXPLODED": "Exploded", "exploded": "Exploded",
        "ELECTROCUTED": "Electrocuted", "electrocuted": "Electrocuted",
        "FROZEN": "Frozen", "frozen": "Frozen",
        "ILLNESS": "Illness", "illness": "Illness",
        "EATEN": "Eaten", "eaten": "Eaten",
        "TORN_APART": "TornApart", "torn_apart": "TornApart",
        "VEHICULAR": "Vehicular", "vehicular": "Vehicular",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
        "OTHER": "Other", "other": "Other",
    }
    return mapping.get(val, val)

def fix_death_type(val: str) -> str:
    """Fix RawDeathType enum casing."""
    mapping = {
        "HOMICIDE": "Homicide", "homicide": "Homicide",
        "ATTEMPTED_HOMICIDE": "AttemptedHomicide", "attempted_homicide": "AttemptedHomicide",
        "EXECUTION": "Execution", "execution": "Execution",
        "ACCIDENT": "Accident", "accident": "Accident",
        "NATURAL_DEATH": "NaturalDeath", "natural_death": "NaturalDeath",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
    }
    return mapping.get(val, val)

def fix_motive(val: str) -> str:
    """Fix Motive enum casing."""
    mapping = {
        "GREED_INHERITANCE": "GreedInheritance", "greed_inheritance": "GreedInheritance",
        "GREED_FINANCIAL": "GreedFinancial", "greed_financial": "GreedFinancial",
        "BLACKMAIL": "Blackmail", "blackmail": "Blackmail",
        "JEALOUSY": "Jealousy", "jealousy": "Jealousy",
        "REVENGE": "Revenge", "revenge": "Revenge",
        "IDEOLOGY": "Ideology", "ideology": "Ideology",
        "SELF_DEFENSE": "SelfDefense", "self_defense": "SelfDefense",
        "CONCEALMENT": "Concealment", "concealment": "Concealment",
        "PASSION": "Passion", "passion": "Passion",
        "VIGILANTE_JUSTICE": "VigilanteJustice", "vigilante_justice": "VigilanteJustice",
        "FREEDOM": "Freedom", "freedom": "Freedom",
        "FAMILY_PROTECTION": "FamilyProtection", "family_protection": "FamilyProtection",
        "PATHOLOGICAL": "Pathological", "pathological": "Pathological",
        "MERCY": "Mercy", "mercy": "Mercy",
        "PENANCE": "Penance", "penance": "Penance",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
        "OTHER": "Other", "other": "Other",
        "NEEDS_REVIEW": "NeedsReview", "needs_review": "NeedsReview",
    }
    return mapping.get(val, val)

def fix_role_in_story(val: str) -> str:
    """Fix RoleInStory enum casing."""
    mapping = {
        "PROTAGONIST": "Protagonist", "protagonist": "Protagonist",
        "ANTAGONIST": "Antagonist", "antagonist": "Antagonist",
        "VICTIM": "Victim", "victim": "Victim",
        "DETECTIVE": "Detective", "detective": "Detective",
        "BYSTANDER": "Bystander", "bystander": "Bystander",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
    }
    return mapping.get(val, val)

def fix_mens_rea(val: str) -> str:
    """Fix MensRea enum casing."""
    mapping = {
        "PURPOSELY": "Purposely", "purposely": "Purposely",
        "KNOWINGLY": "Knowingly", "knowingly": "Knowingly",
        "RECKLESSLY": "Recklessly", "recklessly": "Recklessly",
        "NEGLIGENTLY": "Negligently", "negligently": "Negligently",
        "ACCIDENTALLY": "Accidentally", "accidentally": "Accidentally",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
        "NEEDS_REVIEW": "NeedsReview", "needs_review": "NeedsReview",
    }
    return mapping.get(val, val)

def fix_circumstance(val: str) -> str:
    """Fix KillerCircumstance enum casing."""
    mapping = {
        "JUSTIFIED": "Justified", "justified": "Justified",
        "MITIGATED": "Mitigated", "mitigated": "Mitigated",
        "NEUTRAL": "Neutral", "neutral": "Neutral",
        "UNKNOWN": "Unknown", "unknown": "Unknown",
        "NEEDS_REVIEW": "NeedsReview", "needs_review": "NeedsReview",
    }
    return mapping.get(val, val)

def fix_mystery_trope(val: str) -> str:
    """Fix MysteryTrope enum casing."""
    mapping = {
        "LOCKED_ROOM": "LockedRoom", "locked_room": "LockedRoom",
        "IMPOSSIBLE_CRIME": "ImpossibleCrime", "impossible_crime": "ImpossibleCrime",
        "HOW_CATCHEM": "HowCatchem", "how_catchem": "HowCatchem", "howcatchem": "HowCatchem",
        "WHODUNIT": "Whodunit", "whodunit": "Whodunit",
        "WHYDUNIT": "Whydunit", "whydunit": "Whydunit",
        "HOWDUNIT": "Howdunit", "howdunit": "Howdunit",
        "DYING_CLUE": "DyingClue", "dying_clue": "DyingClue",
        "ALIBI_TRICK": "AlibiTrick", "alibi_trick": "AlibiTrick",
        "CLOSED_CIRCLE": "ClosedCircle", "closed_circle": "ClosedCircle",
        "NEEDLE_IN_HAYSTACK": "NeedleInHaystack", "needle_in_haystack": "NeedleInHaystack",
        "LEAST_LIKELY_SUSPECT": "LeastLikelySuspect", "least_likely_suspect": "LeastLikelySuspect",
        "FRAME_UP": "FrameUp", "frame_up": "FrameUp",
        "MISTAKEN_IDENTITY": "MistakenIdentity", "mistaken_identity": "MistakenIdentity",
    }
    return mapping.get(val, val)

def fix_file(path: Path) -> None:
    """Fix enum casing in a single JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Files are arrays of items
    if not isinstance(data, list):
        data = [data]

    for item in data:
        # Fix top-level media_type
        if "media_type" in item:
            if item["media_type"] == "tv_episode":
                item["media_type"] = "TvEpisode"

        # Fix persons array (both top-level and in deaths)
        for person in item.get("persons", []):
            if "role_in_story" in person and isinstance(person["role_in_story"], str):
                person["role_in_story"] = fix_role_in_story(person["role_in_story"])

        # Fix deaths array
        for death in item.get("deaths", []):
            if "cause" in death and isinstance(death["cause"], str):
                death["cause"] = fix_cause(death["cause"])
            if "death_type" in death and isinstance(death["death_type"], str):
                death["death_type"] = fix_death_type(death["death_type"])
            if "motive" in death and isinstance(death["motive"], str):
                death["motive"] = fix_motive(death["motive"])
            if "tropes" in death and isinstance(death["tropes"], list):
                death["tropes"] = [fix_mystery_trope(t) for t in death["tropes"]]
            # Fix killers
            for killer in death.get("killers", []):
                if "mens_rea" in killer:
                    killer["mens_rea"] = fix_mens_rea(killer["mens_rea"])
                if "circumstance" in killer:
                    killer["circumstance"] = fix_circumstance(killer["circumstance"])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

for path in COLUMBO_FILES:
    fix_file(path)
    print(f"Fixed {path.name}")

print(f"\nFixed {len(COLUMBO_FILES)} files")
