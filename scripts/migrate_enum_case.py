"""Migrate site_data.json enum values from snake_case/SCREAMING_SNAKE_CASE to PascalCase."""

import json
import sys
from pathlib import Path

CAUSE_MAP: dict[str, str] = {
    "POISONED": "Poisoned", "SHOT": "Shot", "STABBED": "Stabbed",
    "CLUBBED": "Clubbed", "STRANGLED": "Strangled", "DROWNED": "Drowned",
    "BURNED": "Burned", "HANGED": "Hanged", "FELL": "Fell",
    "CRUSHED": "Crushed", "SUFFOCATED": "Suffocated", "EXPLODED": "Exploded",
    "ELECTROCUTED": "Electrocuted", "FROZEN": "Frozen", "ILLNESS": "Illness",
    "EATEN": "Eaten", "TORN_APART": "TornApart", "VEHICULAR": "Vehicular",
    "UNKNOWN": "Unknown", "OTHER": "Other",
}

DEATH_TYPE_MAP: dict[str, str] = {
    "homicide": "Homicide", "attempted_homicide": "AttemptedHomicide",
    "execution": "Execution", "accident": "Accident",
    "natural_death": "NaturalDeath", "unknown": "Unknown",
}

MOTIVE_MAP: dict[str, str] = {
    "greed_inheritance": "GreedInheritance", "greed_financial": "GreedFinancial",
    "blackmail": "Blackmail", "jealousy": "Jealousy", "revenge": "Revenge",
    "ideology": "Ideology", "self_defense": "SelfDefense",
    "concealment": "Concealment", "passion": "Passion",
    "vigilante_justice": "VigilanteJustice", "freedom": "Freedom",
    "family_protection": "FamilyProtection", "pathological": "Pathological",
    "mercy": "Mercy", "penance": "Penance", "unknown": "Unknown",
    "other": "Other", "needs_review": "NeedsReview",
}

MENS_REA_MAP: dict[str, str] = {
    "purposely": "Purposely", "knowingly": "Knowingly",
    "recklessly": "Recklessly", "negligently": "Negligently",
    "accidentally": "Accidentally", "unknown": "Unknown",
    "needs_review": "NeedsReview",
}

CIRCUMSTANCE_MAP: dict[str, str] = {
    "justified": "Justified", "mitigated": "Mitigated",
    "neutral": "Neutral", "unknown": "Unknown", "needs_review": "NeedsReview",
}

TROPE_MAP: dict[str, str] = {
    "locked_room": "LockedRoom", "impossible_crime": "ImpossibleCrime",
    "howcatchem": "HowCatchem", "whodunit": "Whodunit",
    "whydunit": "Whydunit", "howdunit": "Howdunit",
    "dying_clue": "DyingClue", "alibi_trick": "AlibiTrick",
    "closed_circle": "ClosedCircle", "needle_in_haystack": "NeedleInHaystack",
    "least_likely_suspect": "LeastLikelySuspect", "frame_up": "FrameUp",
    "mistaken_identity": "MistakenIdentity",
}

ROLE_MAP: dict[str, str] = {
    "protagonist": "Protagonist", "antagonist": "Antagonist",
    "victim": "Victim", "detective": "Detective",
    "bystander": "Bystander", "unknown": "Unknown",
}

MEDIA_TYPE_MAP: dict[str, str] = {
    "book": "Book", "movie": "Movie", "tv_show": "TvShow",
    "tv_episode": "TvEpisode", "game": "Game", "short_story": "ShortStory",
    "play": "Play", "podcast": "Podcast",
}

STATUS_MAP: dict[str, str] = {
    "exists": "Exists", "none": "None", "needs_review": "NeedsReview",
}


def remap(value: str, mapping: dict[str, str], field: str) -> str:
    """Map an old enum string to its new PascalCase form."""
    if value not in mapping:
        print(f"WARNING: unknown {field} value: {repr(value)}", file=sys.stderr)
        return value
    return mapping[value]


def migrate_death(death: dict) -> dict:
    """Migrate all enum fields within a single death object."""
    if "cause" in death:
        death["cause"] = remap(death["cause"], CAUSE_MAP, "cause")
    if "death_type" in death:
        death["death_type"] = remap(death["death_type"], DEATH_TYPE_MAP, "death_type")
    if "motive" in death:
        death["motive"] = remap(death["motive"], MOTIVE_MAP, "motive")
    if "tropes" in death:
        death["tropes"] = [remap(t, TROPE_MAP, "trope") for t in death["tropes"]]
    for killer in death.get("killers", []):
        if "mens_rea" in killer:
            killer["mens_rea"] = remap(killer["mens_rea"], MENS_REA_MAP, "mens_rea")
        if "circumstance" in killer:
            killer["circumstance"] = remap(killer["circumstance"], CIRCUMSTANCE_MAP, "circumstance")
    return death


def migrate_person(person: dict) -> dict:
    """Migrate enum fields within a person object."""
    if "role_in_story" in person and person["role_in_story"] is not None:
        person["role_in_story"] = remap(person["role_in_story"], ROLE_MAP, "role_in_story")
    return person


def migrate_external_links(links: dict) -> dict:
    """Migrate status enum fields within external_links."""
    for field in ("tvtropes_status", "wikipedia_status", "fandom_status",
                  "goodreads_status", "steam_status", "itch_status"):
        if field in links:
            links[field] = remap(links[field], STATUS_MAP, field)
    return links


def migrate_item(item: dict) -> dict:
    """Migrate all enum fields in a media item (top-level, episodes, cases)."""
    if "media_type" in item:
        item["media_type"] = remap(item["media_type"], MEDIA_TYPE_MAP, "media_type")
    if "external_links" in item and item["external_links"] is not None:
        item["external_links"] = migrate_external_links(item["external_links"])
    for person in item.get("persons", []):
        migrate_person(person)
    for death in item.get("deaths", []):
        migrate_death(death)
    for episode in item.get("episodes", []):
        for person in episode.get("persons", []):
            migrate_person(person)
        for death in episode.get("deaths", []):
            migrate_death(death)
    for case in item.get("cases", []):
        for person in case.get("persons", []):
            migrate_person(person)
        for death in case.get("deaths", []):
            migrate_death(death)
    return item


def main() -> None:
    """Read site_data.json, migrate enum values, write back in place."""
    path = Path(__file__).parent.parent / "public" / "site_data.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for collection in data.values():
        for item in collection:
            migrate_item(item)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Migration complete.")


if __name__ == "__main__":
    main()
