# Recipe: tv_show

Unit of work: one **episode** -> one worklist entry with `media_type: "tv_episode"`. The show itself does not become a worklist entry; it is implicit in the episodes' parent show metadata, which the extractor pulls from each episode page.

## Planning steps

1. Ask the user for: show name, fandom subdomain (or "none"), and which seasons to ingest (default: all).
2. Discover episodes:
   - If subdomain given: `uv run scripts/scrape_media.py list-episodes <subdomain> [--season N]`.
   - Else: fall back to Wikipedia's "List of <show> episodes" page — fetch it and extract episode titles from the wikitable rows.
3. For each episode, append a worklist entry:
   ```json
   {
     "slug": "<show-slug>-s<NN>e<NN>",
     "media_type": "tv_episode",
     "title": "<episode title>",
     "url": "<fandom or wikipedia URL if known, else null>",
     "recipe": "tv_show",
     "state": "pending",
     "attempts": 0,
     "error": null
   }
   ```
4. Save and exit. Do not scrape episode bodies during planning.

## Scrape hints (used by dispatcher)

- If `url` is set: `scrape_media.py fetch <slug> --url <url>`.
- Else: `scrape_media.py find "<title>" --subdomain <sub>` (will fall back to Wikipedia, then TVTropes).

## Extraction notes

Do not use regex patterns to extract death data from scraped text—manually review episodes or ask the user instead.

## Slug convention

`<show-slug>-s01e01`, e.g. `monk-s01e01`. Lowercase, hyphenated.
