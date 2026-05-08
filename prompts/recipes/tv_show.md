# Recipe: tv_show

Unit of work: one **episode** -> one worklist entry with `media_type: "tv_episode"`. The show itself does not become a worklist entry; it is implicit in the episodes' parent show metadata, which the extractor pulls from each episode page.

## Planning steps

1. Determine the show name and fandom subdomain.
   - If ADD.md includes a subdomain hint (e.g. `fandom subdomain: thementalist`), use it.
   - Otherwise, discover it: WebSearch `<show name> fandom wiki` and extract the subdomain from the result URL. Do not guess — the subdomain is often not simply the show name (e.g. `thementalist`, not `mentalist`).
2. Discover all episodes:
   - Run `uv run scripts/scrape_media.py list-episodes <subdomain> [--season N]`.
   - If that returns nothing, use WebFetch on `https://epguides.com/<ShowName>/` — it reliably returns S##E## numbers and titles for cross-referencing.
3. For each episode, append a worklist entry:
   ```json
   {
     "slug": "<show-slug>-s<NN>e<NN>",
     "media_type": "tv_episode",
     "title": "<episode title>",
     "url": "<fandom episode URL if known, else null>",
     "recipe": "tv_show",
     "state": "pending",
     "attempts": 0,
     "error": null
   }
   ```
4. Save and exit. Do not scrape episode bodies during planning.

## Scrape hints (used by dispatcher)

- If `url` is set: `scrape_media.py fetch <slug> --url <url>`.
- Else: `scrape_media.py find "<title>" --subdomain <sub>` (falls back to TVTropes).

## Extraction notes

Do not use regex patterns to extract death data from scraped text — manually review episodes or ask the user instead.

## Slug convention

`<show-slug>-s01e01`, e.g. `monk-s01e01`. Lowercase, hyphenated.
