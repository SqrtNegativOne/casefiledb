<template>
  <div class="landing-page">
    <div class="landing-center">
      <div class="landing-title" aria-label="Casefile Database">
        <span>CASE</span>
        <span>FILE</span>
        <span>dAtA</span>
        <span>bAse</span>
      </div>
    </div>
    <footer class="landing-footer">
      <span class="landing-footer-copy">
        No copyright infringement is intended. Only basic facts (names, methods, motives) from published works of fiction are stored here. Facts are not copyrightable.
      </span>
      <nav class="landing-footer-links">
        <RouterLink to="/privacy">Privacy Policy</RouterLink>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/colophon">Colophon</RouterLink>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
.landing-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 52px);
  overflow: hidden;
}

.landing-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.landing-title {
  display: flex;
  flex-direction: column;
  font-family: 'Major Mono Display', monospace;
  font-size: clamp(2.8rem, 8vw, 7rem);
  line-height: 1.05;
  color: var(--text);
  text-align: center;
  user-select: none;
}

.landing-footer {
  padding: 0.75rem 1.5rem;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.72rem;
  color: var(--muted);
}

.landing-footer-copy {
  max-width: 56ch;
  line-height: 1.4;
}

.landing-footer-links {
  display: flex;
  gap: 1rem;
  white-space: nowrap;
}

.landing-footer-links a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.72rem;
}

.landing-footer-links a:hover {
  color: var(--accent);
}
</style>
