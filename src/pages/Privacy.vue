<template>
  <div class="prose-page">
    <h1>Privacy Policy</h1>
    <h2>Local storage</h2>
    <p>
      This site stores two pieces of information in your browser's <code>localStorage</code> — your
      chosen colour theme (light or dark) and the list of works you have marked as completed. Neither
      value is ever sent to a server. Clearing your browser data removes them.
    </p>
    <h2>Cookies</h2>
    <p>
      This site does not set any cookies directly. Google Fonts is loaded from
      <code>fonts.googleapis.com</code>; Google may set its own cookies or log your IP address
      according to its own privacy policy. No other third-party scripts or trackers are included.
    </p>
    <h2>Analytics</h2>
    <p>
      No analytics or tracking scripts are present. GitHub Pages may log standard HTTP access data
      (IP address, user-agent, referrer) for operational purposes; see GitHub's privacy statement for
      details.
    </p>
    <h2>Data collected by this site</h2>
    <p>None.</p>
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

code {
  font-family: ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 0.85em;
  background: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 0.1em 0.35em;
}

.prose-back {
  margin-top: 2rem;
  font-size: 0.85rem;
}
</style>
