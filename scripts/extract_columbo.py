#!/usr/bin/env python3
"""Extract Columbo episode data from scraped fandom pages into schema-valid JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CAUSE_PATTERNS: list[tuple[str, str, str]] = [
    (r'\bshot\b|\bshoots?\b|\bfirearm\b|\brevolver\b|\bpistol\b|\brifle\b|\bbullet\b|\bgunshot\b|\bsniped?\b', "SHOT", "gun"),
    (r'\bpoison(?:ed|s|ing)?\b|\barsenic\b|\bcyanide\b|\btoxin\b|\bdrug(?:ged|s)?\b', "POISONED", "poison"),
    (r'\bstab(?:bed|s|bing)?\b|\bknif(?:e|ing)\b|\bblade\b', "STABBED", "knife"),
    (r'\bstrangl(?:ed|es?|ing|e)\b|\bgarrot(?:t)?(?:ed|e)\b', "STRANGLED", "unmentioned"),
    (r'\bdrown(?:ed|s|ing)?\b', "DROWNED", "water"),
    (r'\bsuffocate[ds]?\b|\bsmothered?\b', "SUFFOCATED", "unmentioned"),
    (r'\bbeat(?:s|en|ing)? (?:to death|him|her|them)\b|\bbludgeon(?:ed)?\b|\bbash(?:ed|es)? (?:to|him|her)\b|\bmicroscope\b', "CLUBBED", "blunt object"),
    (r'\belectrocut(?:ed|ion)\b', "ELECTROCUTED", "electricity"),
    (r'\bexplo(?:sion|ded|de|sive)\b|\bbomb\b', "EXPLODED", "explosive"),
    (r'\bburn(?:ed|s|ing)? (?:to death|him|her)\b|\bset (?:on )?fire\b', "BURNED", "fire"),
    (r'\brun over\b|\bhit by (?:a |his )?car\b', "VEHICULAR", "vehicle"),
    (r'\bhang(?:ed|s|ing)?\b|\bnoose\b', "HANGED", "noose"),
]

MOTIVE_PATTERNS: list[tuple[str, str]] = [
    (r'\binherit(?:ance)?\b|\bestate\b', "greed_inheritance"),
    (r'\bblackmailing?\b|\bextort(?:ion)?\b', "blackmail"),
    (r'\baffair\b|\binfidelity\b|\bcannot (?:betray|reveal)\b', "concealment"),
    (r'\bcover(?:\s|-)?up\b|\bconceal\b|\bexpose[ds]?\b|\bsecret\b', "concealment"),
    (r'\bjealou(?:sy|s)\b', "jealousy"),
    (r'\brevenge\b|\bvengeance\b', "revenge"),
    (r'\binsurance\b|\bfraud\b|\bembezzle\b', "greed_financial"),
    (r'\bmoney\b|\bfinancial(?:ly)?\b|\bprofit\b|\bwealth\b', "greed_financial"),
    (r'\bpassion\b', "passion"),
    (r'\bself[- ]defense\b', "self_defense"),
    (r'\bfreedom\b|\bescape\b', "freedom"),
]

KILL_VERBS = r'kills?\b|murders?\b|shoots?\b|stabs?\b|strangles?\b|poisons?\b|drowns?\b|beats?\b.*?to death|executes?\b'
KILL_PASSIVE = r'is (?:killed|murdered|shot|stabbed|strangled|poisoned|drowned)\b|gets? (?:killed|murdered)\b|found dead|killed for|who (?:is )?killed\b'
# Victim patterns where the character is the OBJECT of a kill action
VICTIM_OBJECT = r'\b(?:kills?|murders?|shoots?|stabs?|poisons?|drowns?)\s+(?:her|him|them)\b|\bher (?:body|death|murder)\b|\bhis (?:body|death|murder)\b|\btheir (?:body|deaths|murders)\b'
# Killer patterns where the character is clearly the SUBJECT doing the killing
KILLER_SUBJECT = r'\bwho (?:kills?|murders?|shoots?|stabs?|poisons?|drowns?|strangles?|beats?\b)\b|\bwilling to kill\b|\bcommits? (?:the |a )?murder\b'


def slug_to_season_ep(slug: str) -> tuple[int, int]:
    m = re.search(r's(\d+)e(\d+)', slug)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def extract_char_from_structured_intro(intro_text: str) -> dict:
    """Parse Villain/Accomplice/Victim from structured Intro format (s00e01 style)."""
    result: dict = {"villain": None, "victim": None, "accomplice": None}
    lines = [l.strip() for l in intro_text.split('\n') if l.strip()]
    i = 0
    while i < len(lines):
        if lines[i] == "Villain" and i + 1 < len(lines):
            result["villain"] = lines[i + 1]
            i += 2
        elif lines[i] == "Victim" and i + 1 < len(lines):
            result["victim"] = lines[i + 1]
            i += 2
        elif lines[i] == "Accomplice" and i + 1 < len(lines):
            result["accomplice"] = lines[i + 1]
            i += 2
        else:
            i += 1
    return result


def parse_cast_entries(cast_text: str) -> list[dict]:
    """Parse cast entries in 'Actor as Character, description' format.
    Handles both newline-separated and single-paragraph formats."""
    # Normalise: if no newlines, try splitting on actor-as pattern
    if '\n' not in cast_text:
        # Insert newline before "Firstname Lastname as Character" patterns
        cast_text = re.sub(r'(?<=[\.!?])\s+(?=[A-Z][a-z]+ [A-Z][a-z]+ as [A-Z])', '\n', cast_text)
        cast_text = re.sub(r'\.\s+(?=[A-Z][a-z]+ [A-Z][a-z]+ as [A-Z])', '.\n', cast_text)

    entries = []
    for line in cast_text.split('\n'):
        line = line.strip()
        if ' as ' not in line:
            continue
        m = re.match(r'^(.+?)\s+as\s+(.+?)(?:\s*[,\.]\s*(.*))?$', line)
        if not m:
            continue
        char_raw = m.group(2).strip()
        # Extract clean character name (capitalize-word prefix)
        cn_m = re.match(r'^((?:[A-Z][a-zA-Z\'.\-]*(?: (?=[A-Z])|$))+)', char_raw)
        char_name = cn_m.group(1).strip() if cn_m else char_raw.split(',')[0].strip()
        desc = m.group(3) or ''
        full = (char_name + ' ' + desc).lower()

        role = 'bystander'
        # Check passive victim first (strongest signal)
        if re.search(KILL_PASSIVE, full):
            role = 'victim'
        # Check if character is object of kill action ("kills him/her")
        elif re.search(VICTIM_OBJECT, full):
            role = 'victim'
        # Check if character is clearly the killer subject
        elif re.search(KILLER_SUBJECT, full):
            role = 'antagonist'
        # Fallback: any kill verb + no passive -> antagonist
        elif re.search(r'\b(?:kills?\b|murders?\b|shoots?\b|stabs?\b|strangles?\b|poisons?\b|drowns?\b)', full):
            role = 'antagonist'
        elif re.search(r'\bcolumbo\b|\blieutenant\b', full):
            role = 'detective'
        entries.append({'name': char_name, 'role': role, 'desc': desc[:200]})
    return entries


def parse_narrative_chars(text: str) -> list[dict]:
    """Extract characters from narrative text using 'Name (Actor)' format."""
    # Pattern: "Firstname Lastname (Actor Name)"
    name_actor = re.compile(
        r'([A-Z][a-z]+(?: [A-Z][a-z.]+)+)\s+\(([A-Z][a-z]+(?: (?:Jr\.?|Sr\.?|[A-Z][a-z]+))*)\)'
    )
    chars = []
    seen = set()
    for m in name_actor.finditer(text):
        char_name = m.group(1)
        if char_name.lower() in ('peter falk', 'lieutenant columbo') or char_name in seen:
            continue
        seen.add(char_name)

        # Look at context around this character's mention
        start = m.start()
        context_before = text[max(0, start - 100): start + len(char_name) + 5]
        context_after = text[start: min(len(text), start + 300)]
        combined = (context_before + context_after).lower()

        role = 'bystander'
        # Check if this char kills someone
        if re.search(r'\b(?:' + KILL_VERBS + r')\b', context_after[:200].lower()):
            # Check it's not passive
            if not re.search(r'\b(?:' + KILL_PASSIVE + r')\b', context_after[:100].lower()):
                role = 'antagonist'
        # Check if this char is killed
        if re.search(r'\b(?:' + KILL_PASSIVE + r')\b', combined):
            role = 'victim'
        # Object pronoun right after kill verb in nearby context
        if re.search(r'\b(?:' + KILL_VERBS + r')\s+(?:her|him)\b', context_before.lower()):
            role = 'victim'

        chars.append({'name': char_name, 'role': role})
    return chars


def detect_cause(full_text: str) -> tuple[str, str]:
    text_lower = full_text.lower()
    for pattern, cause, means in CAUSE_PATTERNS:
        if re.search(pattern, text_lower):
            return cause, means
    return "UNKNOWN", "unknown"


def detect_motive(full_text: str) -> str:
    text_lower = full_text.lower()
    for pattern, motive in MOTIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return motive
    return "unknown"


def make_slug_id(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def extract_episode(slug: str) -> dict:
    raw_json = Path(f"temp/raw/{slug}.json").read_text(encoding='utf-8')
    raw_txt = Path(f"temp/raw/{slug}.txt").read_text(encoding='utf-8')
    d = json.loads(raw_json)

    sections = {s.get('heading', ''): s.get('text', '') for s in d['sections']}
    infobox = d.get('infobox', {})
    title = d.get('title', '')
    season, ep_num = slug_to_season_ep(slug)

    # Year
    year: int | None = None
    air_str = infobox.get('Air date', infobox.get('Airdate', ''))
    if air_str:
        ym = re.search(r'\b(19\d\d|20\d\d)\b', air_str)
        if ym:
            year = int(ym.group(1))
    if not year:
        ym2 = re.search(r'aired[^.]*?(\b(?:19|20)\d\d\b)', raw_txt[:800])
        if ym2:
            year = int(ym2.group(1))
    if not year:
        ym3 = re.search(r'\b(19\d\d|20\d\d)\b', raw_txt[:600])
        if ym3:
            year = int(ym3.group(1))

    cast_text = sections.get('Cast', '')
    intro_text = sections.get('Intro', '')
    plot_text = sections.get('Plot', sections.get('Summary', ''))
    appearances_text = sections.get('Appearances', '')

    villain_name: str | None = None
    victim_name: str | None = None
    accomplice_name: str | None = None

    # 1. Structured Villain/Victim format (s00e01 style)
    structured = extract_char_from_structured_intro(intro_text)
    villain_name = structured.get("villain")
    victim_name = structured.get("victim")
    accomplice_name = structured.get("accomplice")

    # 2. Parse Cast section (Actor as Character format)
    if (not villain_name or not victim_name) and cast_text:
        entries = parse_cast_entries(cast_text)
        if not villain_name:
            killers = [e for e in entries if e['role'] == 'antagonist']
            if killers:
                villain_name = killers[0]['name']
        if not victim_name:
            victims = [e for e in entries if e['role'] == 'victim']
            if victims:
                victim_name = victims[0]['name']

    # 3. Parse Appearances section (also "Actor as Character" format, e.g. s00e01)
    if (not villain_name or not victim_name) and appearances_text:
        entries = parse_cast_entries(appearances_text)
        if not villain_name:
            killers = [e for e in entries if e['role'] == 'antagonist']
            if killers:
                villain_name = killers[0]['name']
        if not victim_name:
            victims = [e for e in entries if e['role'] == 'victim']
            if victims:
                victim_name = victims[0]['name']

    # 4. Narrative "Character (Actor)" format
    if not villain_name or not victim_name:
        narrative = plot_text or intro_text
        if narrative:
            narrative_chars = parse_narrative_chars(narrative)
            if not villain_name:
                killers = [c for c in narrative_chars if c['role'] == 'antagonist']
                if killers:
                    villain_name = killers[0]['name']
            if not victim_name:
                victims = [c for c in narrative_chars if c['role'] == 'victim']
                if victims:
                    victim_name = victims[0]['name']

    # 5. Last resort: "X kills/murders Y" in raw text
    if not villain_name or not victim_name:
        narrative = plot_text or intro_text or raw_txt[:1000]
        m = re.search(
            r'([A-Z][a-z]+(?: [A-Z][a-z.]+)+)[^.]*?\b(?:kills?|murders?|shoots?)\b[^.]*?([A-Z][a-z]+(?: [A-Z][a-z.]+)+)',
            narrative
        )
        if m and not villain_name:
            villain_name = m.group(1)
        if m and not victim_name and len(m.groups()) >= 2:
            victim_name = m.group(2)

    # Detect cause and motive from full text
    cause, means = detect_cause(raw_txt)
    motive = detect_motive(raw_txt)

    # Build persons list
    persons: list[dict] = [
        {
            "name": "Lieutenant Columbo",
            "role_in_story": "detective",
            "is_solver": True,
            "is_fictional": True,
            "profession": "homicide detective",
            "gender": "male",
        }
    ]
    person_ids_used: set[str] = set()

    def add_person(name: str, role: str) -> str:
        pid = make_slug_id(name)
        if pid not in person_ids_used:
            person_ids_used.add(pid)
            persons.append({"id": pid, "name": name, "role_in_story": role, "is_fictional": True})
        return pid

    # Filter out obvious false positives
    _BAD_NAMES = {'Lieutenant Columbo', 'Columbo', 'Peter Falk'}
    _LOCATION_PAT = re.compile(r'\b(?:Los Angeles|New York|Chicago|Hollywood|San Diego)\b')
    if victim_name and (victim_name in _BAD_NAMES or _LOCATION_PAT.search(victim_name)):
        victim_name = None
    if villain_name and villain_name in _BAD_NAMES:
        villain_name = None

    victim_id = add_person(victim_name, "victim") if victim_name else None
    killer_id = add_person(villain_name, "antagonist") if villain_name else None
    if accomplice_name:
        add_person(accomplice_name, "antagonist")

    # Build deaths list
    deaths: list[dict] = []
    if victim_id or victim_name:
        killers_list = []
        if killer_id:
            killers_list.append({"person_id": killer_id, "mens_rea": "purposely", "circumstance": "neutral"})
        elif villain_name:
            killers_list.append({"name": villain_name, "mens_rea": "purposely", "circumstance": "neutral"})

        death: dict = {
            "cause": cause,
            "means": means,
            "death_type": "homicide",
            "motive": motive,
            "tropes": ["howcatchem"],
            "is_central_death": True,
            "killers": killers_list,
        }
        if victim_id:
            death["victim_id"] = victim_id
        else:
            death["victim_name"] = victim_name
        deaths.append(death)

    external_links: dict = {}
    source_url = d.get('url', '')
    if 'fandom.com' in source_url:
        fm = re.search(r'columbo\.fandom\.com/wiki/(.+)$', source_url)
        if fm:
            external_links["fandom_slug"] = f"columbo/{fm.group(1)}"

    episode: dict = {
        "title": title,
        "media_type": "tv_episode",
        "series_name": "Columbo",
        "creator": "Richard Levinson, William Link",
        "wikidata_id": None,
        "slug": slug,
        "persons": persons,
        "deaths": deaths,
    }
    if year:
        episode["year"] = year
    if season is not None:
        episode["season"] = season
    if ep_num:
        episode["episode_number"] = ep_num
    if external_links:
        episode["external_links"] = external_links

    return episode


def main() -> None:
    worklist_path = Path("temp/worklist.json")
    worklist = json.loads(worklist_path.read_text(encoding='utf-8'))

    items_to_process = [i for i in worklist["items"] if i["state"] == "scraped"]
    print(f"Processing {len(items_to_process)} scraped episodes...")

    for item in items_to_process:
        slug = item["slug"]
        try:
            episode = extract_episode(slug)
            out_path = Path(f"temp/{slug}.json")
            out_path.write_text(json.dumps([episode], indent=2, ensure_ascii=False), encoding='utf-8')
            d_info = ''
            if episode['deaths']:
                dth = episode['deaths'][0]
                vid = dth.get('victim_id', dth.get('victim_name', '-'))
                kid = dth['killers'][0].get('person_id', dth['killers'][0].get('name', '-')) if dth.get('killers') else '-'
                d_info = f"victim={vid}, killer={kid}, cause={dth['cause']}"
            item["state"] = "extracted"
            print(f"  OK  {slug}: {d_info}")
        except Exception as e:
            import traceback
            item["attempts"] += 1
            if item["attempts"] >= 2:
                item["state"] = "failed"
            item["error"] = str(e)[:200]
            print(f"  ERR {slug}: {e}")
            traceback.print_exc()

    worklist_path.write_text(json.dumps(worklist, indent=2, ensure_ascii=False), encoding='utf-8')
    extracted = sum(1 for i in worklist["items"] if i["state"] == "extracted")
    failed = sum(1 for i in worklist["items"] if i["state"] == "failed")
    print(f"\n{extracted} extracted, {failed} failed")


if __name__ == "__main__":
    main()
