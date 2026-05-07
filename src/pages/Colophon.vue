<template>
  <div class="prose-page">
    <h1>Colophon</h1>
    <p>
      Casefile Database is a static website built with
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a> and
      <a href="https://vitejs.dev/" target="_blank" rel="noopener">Vite</a>,
      deployed on <a href="https://pages.github.com/" target="_blank" rel="noopener">GitHub Pages</a>.
      Client-side routing uses Vue Router in hash mode so no server configuration is needed.
    </p>
    <h2>Data</h2>
    <p>
      The dataset is a single JSON file committed to the repository. A Rust binary validates and ingests
      new entries; a separate check binary validates the file without modifying it. The Rust schema is
      the single source of truth for field names and controlled vocabularies.
    </p>
    <h2>Typography</h2>
    <p>
      Body text uses the system sans-serif stack.
      Display headings and the site wordmark use
      <a href="https://fonts.google.com/specimen/Major+Mono+Display" target="_blank" rel="noopener">Major Mono Display</a>
      by Emilio Corredera Rubio, served by Google Fonts.
      Typewriter accents use
      <a href="https://fonts.google.com/specimen/Special+Elite" target="_blank" rel="noopener">Special Elite</a>
      by Brian J. Bonislawsky.
    </p>
    <h2>Wikidata</h2>
    <p>
      Where available, items are linked to
      <a href="https://www.wikidata.org/" target="_blank" rel="noopener">Wikidata</a> entries,
      and cover images are fetched lazily from the Open Library and Wikidata APIs.
    </p>
    <div class="prose-back">
      <RouterLink to="/">← Home</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.prose-page {
  max-width: 62ch;
  padding: 2rem 0 3rem;
}

h1 {
  font-family: 'Major Mono Display', monospace;
  font-size: 1.6rem;
  margin: 0 0 1.25rem;
  color: var(--text);
}

h2 {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--muted);
  margin: 1.75rem 0 0.5rem;
}

p {
  font-size: 0.92rem;
  line-height: 1.7;
  color: var(--text);
  margin: 0 0 0.75rem;
}

.prose-back {
  margin-top: 2rem;
  font-size: 0.85rem;
}
</style>
