"""Scrape a Fandom wiki page and extract a skeleton JSON for ingest.

Usage:
    uv run python scripts/scrape_fandom.py <fandom_url> [--out temp/output.json]

The script fetches the page, heuristically extracts character names, infobox
fields, and any tables that look like character or death lists, then writes a
skeleton MediaModel JSON to stdout (or a file) that you can fill in and ingest.

This is a best-effort helper — always review the output before ingesting.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, unquote


# ─── Minimal HTML extractor ────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    """Collects visible text while skipping scripts/styles."""

    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self.chunks.append(stripped)


class _TableExtractor(HTMLParser):
    """Extracts all <table> contents as lists of rows × cells."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._in_table = 0
        self._in_row = False
        self._in_cell = False
        self._skip = 0
        self._current_table: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in {"script", "style"}:
            self._skip += 1
            return
        if tag == "table":
            self._in_table += 1
            if self._in_table == 1:
                self._current_table = []
        elif tag == "tr" and self._in_table == 1:
            self._in_row = True
            self._current_row = []
        elif tag in {"td", "th"} and self._in_table == 1:
            self._in_cell = True
            self._current_cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip > 0:
            self._skip -= 1
            return
        if tag == "table":
            if self._in_table == 1 and self._current_table:
                self.tables.append(self._current_table)
            self._in_table = max(0, self._in_table - 1)
        elif tag == "tr" and self._in_table == 1 and self._in_row:
            if self._current_row:
                self._current_table.append(self._current_row)
            self._in_row = False
        elif tag in {"td", "th"} and self._in_table == 1 and self._in_cell:
            self._current_row.append(" ".join(self._current_cell).strip())
            self._in_cell = False

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.strip()
        if text and self._in_cell:
            self._current_cell.append(text)


class _InfoboxExtractor(HTMLParser):
    """Extracts key-value pairs from a Fandom infobox aside/table."""

    def __init__(self) -> None:
        super().__init__()
        self.pairs: dict[str, str] = {}
        self._in_aside = False
        self._in_key = False
        self._in_val = False
        self._skip = 0
        self._current_key: list[str] = []
        self._current_val: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attr_dict = dict(attrs)
        if tag in {"script", "style"}:
            self._skip += 1
            return
        classes = attr_dict.get("class", "")
        if tag == "aside" or (tag == "table" and "infobox" in classes):
            self._in_aside = True
        if self._in_aside:
            if tag == "h3" or (tag == "div" and "pi-data-label" in classes):
                self._in_key = True
                self._current_key = []
            elif tag == "div" and "pi-data-value" in classes:
                self._in_val = True
                self._current_val = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip > 0:
            self._skip -= 1
            return
        if self._in_aside:
            if tag == "h3" or (tag == "div" and self._in_key):
                if self._current_key:
                    self._last_key = " ".join(self._current_key).strip()
                self._in_key = False
            elif tag == "div" and self._in_val:
                key = getattr(self, "_last_key", "")
                val = " ".join(self._current_val).strip()
                if key and val:
                    self.pairs[key] = val
                self._in_val = False

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.strip()
        if text:
            if self._in_key:
                self._current_key.append(text)
            elif self._in_val:
                self._current_val.append(text)


# ─── Fetching ───────────────────────────────────────────────────────────────

def fetch_html(url: str) -> str:
    """Fetch a URL and return its HTML as a string."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; CasefileDB/1.0; research scraper)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        charset = "utf-8"
        ct = resp.headers.get("Content-Type", "")
        m = re.search(r"charset=([^\s;]+)", ct)
        if m:
            charset = m.group(1).strip('"')
        return resp.read().decode(charset, errors="replace")


# ─── Heuristics ─────────────────────────────────────────────────────────────

_DEATH_KEYWORDS = re.compile(
    r"\b(murder|kill|death|victim|deceased|shot|stabb|poison|strangle|drown|hung|hang"
    r"|suffoc|bludgeon|beat|chok|electro|push|fell|fell|push|burn|explo)\w*\b",
    re.IGNORECASE,
)

_PERSON_HEADERS = re.compile(
    r"\b(character|cast|person|victim|suspect|killer|murderer|detective|witness)\w*\b",
    re.IGNORECASE,
)


def _guess_persons_from_tables(tables: list[list[list[str]]]) -> list[str]:
    """Return candidate person names from tables with character-like headers."""
    names: list[str] = []
    for table in tables:
        if not table:
            continue
        header = table[0]
        header_text = " ".join(header).lower()
        if not _PERSON_HEADERS.search(header_text):
            continue
        # First column is usually the name
        for row in table[1:]:
            if row and row[0]:
                candidate = row[0].strip()
                # Skip if it looks like a number or is very long
                if candidate and not candidate.isdigit() and len(candidate) < 60:
                    names.append(candidate)
    return names


def _guess_title_from_url(url: str) -> str:
    """Derive a human-readable title from the Fandom URL path."""
    path = urlparse(url).path
    slug = path.rstrip("/").split("/")[-1]
    return unquote(slug).replace("_", " ")


# ─── Main skeleton builder ───────────────────────────────────────────────────

def build_skeleton(url: str) -> dict:
    """Fetch a Fandom URL and return a best-effort skeleton dict."""
    print(f"Fetching {url} ...", file=sys.stderr)
    html = fetch_html(url)

    # Extract title
    title_m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    raw_title = title_m.group(1).strip() if title_m else _guess_title_from_url(url)
    # Fandom titles are usually "Page title | Wiki Name"
    page_title = raw_title.split("|")[0].strip()
    page_title = re.sub(r"\s*[-–]\s*.*$", "", page_title).strip()

    # Tables
    table_parser = _TableExtractor()
    table_parser.feed(html)

    # Infobox
    info_parser = _InfoboxExtractor()
    info_parser.feed(html)

    # Text chunks for death keyword scan
    text_parser = _TextExtractor()
    text_parser.feed(html)
    all_text = "\n".join(text_parser.chunks)

    # Heuristic: find sentences mentioning death
    death_lines = [
        line.strip()
        for line in all_text.splitlines()
        if _DEATH_KEYWORDS.search(line) and 10 < len(line) < 200
    ][:20]

    # Person names from tables
    candidate_names = _guess_persons_from_tables(table_parser.tables)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_names: list[str] = []
    for n in candidate_names:
        if n not in seen:
            seen.add(n)
            unique_names.append(n)

    persons = [
        {"name": name, "role_in_story": "unknown"}
        for name in unique_names[:30]
    ]

    skeleton = {
        "wikidata_id": None,
        "slug": "FILL_IN",
        "title": page_title,
        "media_type": "FILL_IN (book|movie|tv_show|tv_episode|game|short_story|play|podcast)",
        "creator": info_parser.pairs.get("Author", info_parser.pairs.get("Director", "FILL_IN")),
        "year": None,
        "tags": [],
        "external_links": {
            "fandom_url": url,
        },
        "notes": None,
        "persons": persons if persons else [
            {"name": "FILL_IN victim", "role_in_story": "victim"},
            {"name": "FILL_IN killer", "role_in_story": "antagonist"},
        ],
        "deaths": [
            {
                "victim_name": "FILL_IN",
                "killer_name": "FILL_IN",
                "cause": "FILL_IN (POISONED|SHOT|STABBED|CLUBBED|STRANGLED|...)",
                "death_type": "murder",
                "motive": "unknown",
                "tropes": [],
                "ordinal": 1,
                "is_central_death": True,
                "is_twist": False,
                "notes": None,
            }
        ],
        "episodes": [],
        "cases": [],
        "_scraper_notes": {
            "source_url": url,
            "infobox_fields": info_parser.pairs,
            "death_context_lines": death_lines[:10],
            "candidate_names": unique_names[:30],
        },
    }

    return skeleton


# ─── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Scrape a Fandom wiki page into a Casefile skeleton JSON.")
    parser.add_argument("url", help="Fandom wiki URL to scrape")
    parser.add_argument("--out", "-o", default=None, help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        skeleton = build_skeleton(args.url)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps([skeleton], indent=2, ensure_ascii=False)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Written to {out_path}", file=sys.stderr)
        print("Review and fill in FILL_IN fields, then run: uv run python scripts/ingest.py", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
