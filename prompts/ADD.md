# Media to add

The worklist (`temp/worklist.json`) tracks the specific state of each item.
Items already in the database have been removed from the worklist.

## Status summary

**Psych (USA Network, 2006–2014)**
- Seasons 1–7 and the original Psych movie: complete in the database.
- Season 8: episodes 1–2, 4–9 added. Episodes 3, 10 still pending (state: scraped).
- Missing episode scrapes: s02e06, s03e02, s04e11 (state: failed — fandom pages could not be scraped).
- Psych 2: Lassie Come Home and Psych 3: This Is Gus: scraped but not yet extracted.
- Fandom subdomain: `psychusa`

**The Mentalist (CBS, 2008–2015)**
- Episodes s03e01–s03e03, s04e13, s05e08, s06e15: failed to scrape (state: failed).
- Fandom subdomain: `thementalist`

**Sherlock Holmes novels (Arthur Conan Doyle)**
- The Hound of the Baskervilles: complete in the database.
- A Study in Scarlet, The Sign of the Four, The Valley of Fear: scraped, not yet extracted.
- Short story collections (Adventures, Memoirs, Return, His Last Bow, Case Book): failed to scrape.

**Father Brown (G.K. Chesterton)**
- All 5 collections: failed to scrape.

**John Dickson Carr novels**
- All titles: failed to scrape.

## Dispatcher instructions

Run the dispatcher (`prompts/dispatcher.md`) to continue processing items in the worklist.
For items in `failed` state, the scraping step needs to be retried first.
