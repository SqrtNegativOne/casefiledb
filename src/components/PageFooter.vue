<template>
    <footer class="site-footer">
        <span class="site-footer-copy">
            No copyright infringement intended.
        </span>
        <nav class="site-footer-links">
            <RouterLink to="/privacy">Privacy Policy</RouterLink>
            <RouterLink to="/about">About</RouterLink>
            <RouterLink to="/colophon">Colophon</RouterLink>
        </nav>
    </footer>
</template>

<style scoped>
.site-footer {
    padding: 0.75rem 0;
    margin-top: 2rem;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.72rem;
    color: var(--muted);
}

.site-footer-copy {
    max-width: 56ch;
    line-height: 1.4;
}

.site-footer-links {
    display: flex;
    gap: 1rem;
    white-space: nowrap;
}

.site-footer-links a {
    color: var(--muted);
    text-decoration: none;
    font-size: 0.72rem;
}

.site-footer-links a:hover {
    color: var(--accent);
}
</style>
