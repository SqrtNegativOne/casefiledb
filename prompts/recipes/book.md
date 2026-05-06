# Recipe: book

Unit of work: one **book** -> one worklist entry with `media_type: "book"`.

## Planning steps

1. Ask the user for: title, author, and series (if any).
2. Resolve a URL in this order:
   - Series-specific fandom wiki (e.g. `agathachristie.fandom.com`).
   - English Wikipedia.
   - TVTropes Literature namespace.
3. Append one worklist entry:
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
- Else: `scrape_media.py find "<title>" [--subdomain <sub>]`.

## Slug convention

Lowercase, hyphenated title. Disambiguate by year or author if the title is generic (e.g. `the-mysterious-affair-at-styles`, `and-then-there-were-none`).

## Notes for extractor

- Cover image: include an Open Library or Wikidata P18 reference if `temp/raw/<slug>.json` infobox has one; otherwise leave the image field null and let the frontend's lazy fetch handle it.
- Multiple deaths in one book: each gets its own entry in `deaths`, all sharing the book's top-level `persons` list.
