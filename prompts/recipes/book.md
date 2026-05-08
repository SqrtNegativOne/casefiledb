# Recipe: book

Unit of work: one **book** -> one worklist entry with `media_type: "book"`.

## Planning steps

1. Determine the title(s) to add.
   - If called from the dispatcher via ADD.md with a single title: use that directly.
   - If the ADD.md entry specifies an author, series, or "all books by X": first discover the full list. Use WebSearch (`<author> complete bibliography novels list`) and WebFetch on the best result (bookseriesinorder.com and similar sites work well; see note on Wikipedia below). Collect all titles before creating entries.
2. For each title, resolve a source URL in this order:
   - Series-specific fandom wiki (e.g. `agathachristie.fandom.com`).
   - TVTropes Literature namespace (`https://tvtropes.org/pmwiki/pmwiki.php/Literature/<PascalCaseTitle>`).
   - English Wikipedia — **note: Wikipedia returns 403 from this host and cannot be scraped by `scrape_media.py`.** Only use Wikipedia URLs as a last resort; prefer fandom or TVTropes.
3. Append one worklist entry per title:
   ```json
   {
     "slug": "<book-slug>",
     "media_type": "book",
     "title": "<title>",
     "url": "<best URL found, or null>",
     "recipe": "book",
     "state": "pending",
     "attempts": 0,
     "error": null
   }
   ```

## Scrape hints

- If `url` is set: `scrape_media.py fetch <slug> --url <url>`.
- Else: `scrape_media.py find "<title>" [--subdomain <sub>]` (tries fandom if subdomain given, then TVTropes).

## Slug convention

Lowercase, hyphenated title. Disambiguate by year or author if the title is generic (e.g. `the-mysterious-affair-at-styles`, `and-then-there-were-none`).

## Notes for extractor

- Multiple deaths in one book: each gets its own entry in `deaths`, all sharing the book's top-level `persons` list.
- Cover images are fetched lazily by the frontend from Wikidata P18 / Open Library — the schema has no image field, so do not invent one.
