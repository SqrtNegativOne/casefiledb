#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests>=2.31", "beautifulsoup4>=4.12"]
# ///
"""Batch-scrape all pending items in temp/worklist.json.

Runs scripts/scrape_media.py fetch <slug> --url <URL> for each pending item.
Updates worklist state to 'scraped' on success, increments attempts on failure.
Items with attempts >= 2 are marked 'failed'.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKLIST = Path("temp/worklist.json")
SCRIPT = Path("scripts/scrape_media.py")


def main() -> None:
    """Scrape all pending items and update worklist."""
    data = json.loads(WORKLIST.read_text(encoding="utf-8"))
    items = data["items"]

    pending = [i for i in items if i["state"] == "pending"]
    print(f"Found {len(pending)} pending items to scrape.", flush=True)

    for idx, item in enumerate(pending, 1):
        slug = item["slug"]
        url = item.get("url")
        print(f"[{idx}/{len(pending)}] Scraping {slug} ...", end=" ", flush=True)

        recipe = item.get("recipe", "")
        title = item.get("title", slug)

        if url:
            cmd = ["uv", "run", "--script", str(SCRIPT), "fetch", slug, "--url", url]
        elif recipe == "book":
            # No URL: use TVTropes find
            cmd = ["uv", "run", "--script", str(SCRIPT), "find", title,
                   "--slug", slug, "--source", "tvtropes"]
        else:
            print("SKIP (no url, unsupported recipe)")
            continue

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            item["state"] = "scraped"
            item["error"] = None
            print("OK")
        else:
            item["attempts"] = item.get("attempts", 0) + 1
            err = (result.stderr or result.stdout or "unknown error").strip()
            item["error"] = err[:200]
            if item["attempts"] >= 2:
                item["state"] = "failed"
                print(f"FAILED (attempt {item['attempts']}): {err[:80]}")
            else:
                print(f"RETRY later (attempt {item['attempts']}): {err[:80]}")

        # Save after each item so progress is durable
        WORKLIST.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    scraped = sum(1 for i in items if i["state"] == "scraped")
    failed = sum(1 for i in items if i["state"] == "failed")
    still_pending = sum(1 for i in items if i["state"] == "pending")
    print(f"\nDone. scraped={scraped}, failed={failed}, still_pending={still_pending}")


if __name__ == "__main__":
    main()
