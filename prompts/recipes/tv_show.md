# Recipe: tv_show

Unit of work: one **episode** -> one worklist entry with `media_type: "tv_episode"`. The show itself does not become a worklist entry; it is implicit in the episodes' parent show metadata, which the extractor pulls from each episode page.

## Planning steps

1. Determine the show name, fandom subdomain, and which seasons to ingest (default: all).
   - If called from the dispatcher via ADD.md, the show name is already known — skip asking the user.
   - If the fandom subdomain is not given, discover it: WebSearch `<show name> fandom wiki` and read the subdomain from the result URL (e.g. `thementalist` from `thementalist.fandom.com`). Do not guess — the subdomain is often not simply the show name.
2. Discover episodes:
   - If subdomain known: `uv run scripts/scrape_media.py list-episodes <subdomain> [--season N]`.
   - If that returns nothing or subdomain is unknown: use WebFetch on a reliable episode-list site such as `https://epguides.com/<ShowName>/` — it reliably returns S##E## numbers and titles. Do **not** use Wikipedia (it returns 403 from this host).
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
- Else: `scrape_media.py find "<title>" --subdomain <sub>` (will fall back to TVTropes).

## Extraction notes

Do not use regex patterns to extract death data from scraped text — manually review episodes or ask the user instead.

## Slug convention

`<show-slug>-s01e01`, e.g. `monk-s01e01`. Lowercase, hyphenated.
