# Recipe: movie

Unit of work: one **movie** -> one worklist entry with `media_type: "movie"`.

## Planning steps

1. Ask the user for the movie title (and franchise if it shares a fandom wiki, e.g. *Wake Up Dead Man* lives at `knives-out.fandom.com`).
2. Resolve a URL in this order:
   - Franchise fandom wiki, if one exists.
   - English Wikipedia.
   - TVTropes Film namespace.
3. Append one worklist entry:
   ```json
   {
     "slug": "<movie-slug>",
     "media_type": "movie",
     "title": "<title>",
     "url": "<best URL found, or null>",
     "recipe": "movie",
     "state": "pending",
     "attempts": 0,
     "error": null
   }
   ```

## Scrape hints

- If `url` is set: `scrape_media.py fetch <slug> --url <url>`.
- Else: `scrape_media.py find "<title>"` (Wikipedia -> TVTropes fallback).

## Slug convention

Lowercase, hyphenated title; disambiguate sequels with a year if needed (e.g. `knives-out-2019`, `knives-out-glass-onion`).
