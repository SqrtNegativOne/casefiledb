#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests>=2.31", "beautifulsoup4>=4.12"]
# ///
"""Scrape a media page (Fandom -> TVTropes fallback) into temp/raw/.

Outputs two files per page:
    temp/raw/<slug>.txt   - plaintext with section headers
    temp/raw/<slug>.json  - {source, url, title, infobox, tables, sections}

Subcommands:
    fetch <slug> --url <URL>
        Scrape a known URL. Source is inferred from the hostname.

    find <title> [--subdomain SUB] [--source fandom|tvtropes]
        Try sources in order until one returns a usable page, then scrape it.
        Default order: fandom (if --subdomain) -> tvtropes.

    list-episodes <subdomain> [--season N]
        For a Fandom show, return episode page titles found via the Episodes
        category. Prints one title per line on stdout.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup, Tag

UA = "casefiledb-scraper/0.1 (https://github.com/SqrtNegativOne/casefiledb; bot; contact via GitHub issues)"
OUT_DIR = Path("temp/raw")
TIMEOUT = 30


@dataclass
class Page:
    """A scraped page in normalized form."""

    source: str
    url: str
    title: str
    infobox: dict[str, str]
    tables: list[list[list[str]]]
    sections: list[dict[str, str]]

    def plaintext(self) -> str:
        """Render sections as a single plaintext document with headers."""
        out: list[str] = [f"# {self.title}", f"<source: {self.source}> <url: {self.url}>", ""]
        if self.infobox:
            out.append("## Infobox")
            for k, v in self.infobox.items():
                out.append(f"- {k}: {v}")
            out.append("")
        for sec in self.sections:
            out.append(f"## {sec['heading']}")
            out.append(sec["text"])
            out.append("")
        return "\n".join(out)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict of the page."""
        return {
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "infobox": self.infobox,
            "tables": self.tables,
            "sections": self.sections,
        }


def _get(url: str, params: dict[str, str] | None = None) -> requests.Response:
    """HTTP GET with our UA header. Raises on non-2xx."""
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=TIMEOUT)
    r.raise_for_status()
    return r


def _clean_text(node: Tag) -> str:
    """Extract human-readable text from an HTML node, dropping refs and edit links."""
    for sel in [".reference", ".mw-editsection", "sup.reference", ".noprint", "style", "script"]:
        for el in node.select(sel):
            el.decompose()
    text = node.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _parse_table(tbl: Tag) -> list[list[str]]:
    """Convert a <table> into a list of rows of cell strings."""
    rows: list[list[str]] = []
    for tr in tbl.find_all("tr"):
        cells = [_clean_text(c) for c in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    return rows


def _split_sections(content: Tag) -> list[dict[str, str]]:
    """Walk a MediaWiki content div and group paragraphs under headings."""
    sections: list[dict[str, str]] = []
    current_heading = "Intro"
    current_buf: list[str] = []

    def flush() -> None:
        text = "\n".join(b for b in current_buf if b).strip()
        if text:
            sections.append({"heading": current_heading, "text": text})

    for el in content.find_all(["h2", "h3", "h4", "p", "ul", "ol"], recursive=True):
        if el.name in {"h2", "h3", "h4"}:
            flush()
            current_heading = _clean_text(el)
            current_buf = []
        else:
            t = _clean_text(el)
            if t:
                current_buf.append(t)
    flush()
    return sections


# ---------- Fandom ----------

def fetch_fandom(subdomain: str, title: str) -> Page:
    """Fetch a page from <subdomain>.fandom.com via the MediaWiki parse API."""
    api = f"https://{subdomain}.fandom.com/api.php"
    r = _get(api, {"action": "parse", "page": title, "prop": "text", "format": "json", "redirects": "1"})
    data = r.json()
    if "error" in data:
        raise LookupError(f"fandom: {data['error'].get('info', 'unknown error')}")
    parse = data["parse"]
    html = parse["text"]["*"]
    real_title = parse["title"]
    soup = BeautifulSoup(html, "html.parser")

    infobox: dict[str, str] = {}
    aside = soup.find("aside", class_=re.compile(r"portable-infobox"))
    if isinstance(aside, Tag):
        for item in aside.find_all(class_=re.compile(r"pi-item")):
            label = item.find(class_=re.compile(r"pi-data-label"))
            value = item.find(class_=re.compile(r"pi-data-value"))
            if isinstance(label, Tag) and isinstance(value, Tag):
                infobox[_clean_text(label)] = _clean_text(value)
        aside.decompose()

    tables = [_parse_table(t) for t in soup.find_all("table", class_=re.compile(r"wikitable|article-table"))]
    sections = _split_sections(soup)
    url = f"https://{subdomain}.fandom.com/wiki/{quote(real_title.replace(' ', '_'))}"
    return Page("fandom", url, real_title, infobox, tables, sections)


def list_fandom_episodes(subdomain: str, season: int | None) -> list[str]:
    """Return episode page titles from <subdomain>.fandom.com via the Episodes category."""
    api = f"https://{subdomain}.fandom.com/api.php"

    # Try category members first (most reliable)
    cat = f"Season {season}" if season is not None else "Episodes"
    try:
        r = _get(api, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{cat}",
                       "cmlimit": "500", "cmnamespace": "0", "format": "json"})
        data = r.json()
        members = [m["title"] for m in data.get("query", {}).get("categorymembers", [])]
        # Drop meta-pages: transcripts, list pages, galleries, specials
        skip = re.compile(r"(^List |^Portal:|/|^Category:|^Template:)", re.I)
        members = [t for t in members if not skip.search(t)]
        if members:
            return members
    except (requests.HTTPError, KeyError):
        pass

    # Fallback: parse links from known episode-list pages
    candidates = ["List_of_episodes", "Episodes", "Episode_Guide"]
    if season is not None:
        candidates = [f"Season_{season}"] + candidates
    for cand in candidates:
        try:
            r = _get(api, {"action": "parse", "page": cand, "prop": "links", "format": "json", "redirects": "1"})
        except requests.HTTPError:
            continue
        data = r.json()
        if "error" in data:
            continue
        links = [lk["*"] for lk in data["parse"].get("links", []) if lk.get("ns") == 0]
        episodish = [t for t in links if re.search(r"(episode|pilot|chapter|s\d+e\d+)", t, re.I)]
        if episodish:
            return episodish
        if links:
            return links
    return []


# ---------- TVTropes ----------

def fetch_tvtropes(title: str, namespace: str = "Series") -> Page:
    """Fetch a page from tvtropes.org. Title is the PascalCase wiki name."""
    url = f"https://tvtropes.org/pmwiki/pmwiki.php/{namespace}/{title}"
    r = _get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.find("div", id="main-article") or soup.find("div", class_="page-content") or soup.body
    if main is None:
        raise LookupError("tvtropes: no main article found")
    real_title = _clean_text(soup.find("h1")) if soup.find("h1") else title
    sections = _split_sections(main)
    tables = [_parse_table(t) for t in main.find_all("table")]
    return Page("tvtropes", url, real_title, {}, tables, sections)


# ---------- Dispatch ----------

def fetch_url(url: str) -> Page:
    """Dispatch to the right fetcher based on the URL hostname."""
    host = urlparse(url).hostname or ""
    path = urlparse(url).path
    if host.endswith(".fandom.com"):
        sub = host.split(".")[0]
        m = re.search(r"/wiki/(.+)$", path)
        if not m:
            raise ValueError(f"cannot parse fandom title from {url}")
        return fetch_fandom(sub, m.group(1).replace("_", " "))
    if host.endswith("tvtropes.org"):
        m = re.match(r"/pmwiki/pmwiki\.php/([^/]+)/([^/?#]+)", path)
        if not m:
            raise ValueError(f"cannot parse tvtropes title from {url}")
        return fetch_tvtropes(m.group(2), m.group(1))
    raise ValueError(f"unsupported host: {host}")


def find_page(title: str, subdomain: str | None, source: str | None) -> Page:
    """Try sources in fallback order until one succeeds."""
    order: list[str] = [source] if source else []
    if not order:
        if subdomain:
            order.append("fandom")
        order.append("tvtropes")

    errors: list[str] = []
    for src in order:
        try:
            if src == "fandom":
                if not subdomain:
                    raise ValueError("fandom requires --subdomain")
                return fetch_fandom(subdomain, title)
            if src == "tvtropes":
                pascal = re.sub(r"[^A-Za-z0-9]", "", title.title())
                return fetch_tvtropes(pascal)
        except (requests.HTTPError, LookupError, ValueError) as e:
            errors.append(f"{src}: {e}")
            continue
    raise LookupError("all sources failed:\n  " + "\n  ".join(errors))


def write_page(slug: str, page: Page) -> tuple[Path, Path]:
    """Write the scraped page to temp/raw/<slug>.{txt,json}."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    txt_path = OUT_DIR / f"{slug}.txt"
    json_path = OUT_DIR / f"{slug}.json"
    txt_path.write_text(page.plaintext(), encoding="utf-8")
    json_path.write_text(json.dumps(page.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return txt_path, json_path


def main() -> int:
    """CLI entry point. Returns a process exit code."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("fetch", help="Scrape a known URL")
    pf.add_argument("slug", help="Output slug (used as filename)")
    pf.add_argument("--url", required=True)

    pfd = sub.add_parser("find", help="Try fallbacks until one source returns a page")
    pfd.add_argument("title")
    pfd.add_argument("--slug", help="Output slug (default: derived from title)")
    pfd.add_argument("--subdomain", help="Fandom subdomain, e.g. 'monk' for monk.fandom.com")
    pfd.add_argument("--source", choices=["fandom", "tvtropes"], help="Force a specific source")

    pl = sub.add_parser("list-episodes", help="List episode page titles for a Fandom show")
    pl.add_argument("subdomain")
    pl.add_argument("--season", type=int, default=None)

    args = p.parse_args()

    if args.cmd == "fetch":
        page = fetch_url(args.url)
        tp, jp = write_page(args.slug, page)
        print(f"OK {page.source} -> {tp} {jp}")
        return 0

    if args.cmd == "find":
        page = find_page(args.title, args.subdomain, args.source)
        slug = args.slug or re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")
        tp, jp = write_page(slug, page)
        print(f"OK {page.source} -> {tp} {jp}")
        return 0

    if args.cmd == "list-episodes":
        for t in list_fandom_episodes(args.subdomain, args.season):
            print(t)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
