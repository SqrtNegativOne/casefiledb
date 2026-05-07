<template>
  <div class="prose-page">
    <h1>About</h1>
    <p>
      Casefile Database is a catalogued index of deaths in murder mystery media — books, television,
      games, films, and more. Each entry records the victim, cause of death, killer, and motive,
      behind a spoiler screen until you mark the work as completed.
    </p>
    <p>
      The project exists because the genre rewards obsessive pattern-finding: who dies most often,
      which poisons are fashionable in which decades, whether the detective ever gets it wrong.
      Having the data in one place makes those questions answerable.
    </p>
    <h2>Spoilers</h2>
    <p>
      All plot details are hidden by default. Use <em>Mark as completed</em> in the navigation bar
      to reveal the data for works you have already finished. Enable <em>Mnesia mode</em> to reveal
      everything at once if you do not mind spoilers.
    </p>
    <h2>Contributing</h2>
    <p>
      The source data is maintained as JSON and the full schema is documented in the repository.
      Corrections and additions are welcome via the project's issue tracker.
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
