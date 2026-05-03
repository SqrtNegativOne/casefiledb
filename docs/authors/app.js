(async function () {
    function esc(v) {
        const s = v == null ? "" : String(v);
        return s
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function deathCount(media) {
        const direct = (media.deaths || []).length;
        const inCases = (media.cases || []).reduce((n, c) => n + (c.deaths || []).length, 0);
        const inEpisodes = (media.episodes || []).reduce((n, e) => n + (e.deaths || []).length, 0);
        return direct + inCases + inEpisodes;
    }

    function getTheme() {
        const saved = localStorage.getItem("casefile-theme");
        if (saved === "light" || saved === "dark") return saved;
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("casefile-theme", theme);
        const btn = document.getElementById("themeToggle");
        if (btn) btn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
    }

    document.getElementById("themeToggle").addEventListener("click", () => {
        const cur = document.documentElement.getAttribute("data-theme");
        setTheme(cur === "dark" ? "light" : "dark");
    });
    setTheme(getTheme());

    const data = await fetch("../site_data.json").then((r) => r.json()).catch(() => []);

    // Aggregate by creator. Only top-level media items (not individual episodes).
    const byCreator = new Map();
    for (const item of data) {
        const creator = item.creator || "Unknown";
        if (!byCreator.has(creator)) {
            byCreator.set(creator, { name: creator, works: [], totalDeaths: 0, types: new Set() });
        }
        const entry = byCreator.get(creator);
        entry.works.push(item);
        entry.totalDeaths += deathCount(item);
        if (item.media_type) entry.types.add(item.media_type);
    }

    const authors = Array.from(byCreator.values());

    const searchInput = document.getElementById("searchInput");
    const sortField = document.getElementById("sortField");
    const sortDirection = document.getElementById("sortDirection");
    const resultCount = document.getElementById("resultCount");
    const tableBody = document.getElementById("tableBody");
    const sortableHeaders = Array.from(document.querySelectorAll("th.sortable"));

    function updateSortIndicators() {
        const field = sortField.value;
        const dir = sortDirection.value;
        sortableHeaders.forEach((th) => {
            const key = th.getAttribute("data-sort-key");
            if (key === field) {
                th.setAttribute("data-sort-state", dir);
            } else {
                th.removeAttribute("data-sort-state");
            }
        });
    }

    function sortValue(author, field) {
        if (field === "works") return author.works.length;
        if (field === "deaths") return author.totalDeaths;
        return author.name.toLowerCase();
    }

    function render() {
        const q = (searchInput.value || "").trim().toLowerCase();
        const field = sortField.value;
        const dir = sortDirection.value;
        const dirSign = dir === "desc" ? -1 : 1;

        const filtered = authors.filter((a) =>
            !q || a.name.toLowerCase().includes(q)
        );

        filtered.sort((a, b) => {
            const av = sortValue(a, field);
            const bv = sortValue(b, field);
            let result = 0;
            if (typeof av === "number" && typeof bv === "number") {
                result = av - bv;
            } else {
                result = String(av).localeCompare(String(bv), undefined, { sensitivity: "base" });
            }
            if (result === 0) result = a.name.localeCompare(b.name);
            return result * dirSign;
        });

        updateSortIndicators();
        resultCount.textContent = `${filtered.length} author${filtered.length === 1 ? "" : "s"}`;

        if (!filtered.length) {
            tableBody.innerHTML = '<tr><td colspan="4" class="muted">No matches.</td></tr>';
            return;
        }

        tableBody.innerHTML = filtered.map((author) => {
            const types = Array.from(author.types).sort().join(", ");
            const mediaLink = `../?creator=${encodeURIComponent(author.name)}`;
            return (
                "<tr>" +
                `<td><a href="${mediaLink}">${esc(author.name)}</a></td>` +
                `<td>${author.works.length}</td>` +
                `<td>${author.totalDeaths}</td>` +
                `<td><span class="muted">${esc(types)}</span></td>` +
                "</tr>"
            );
        }).join("");
    }

    searchInput.addEventListener("input", render);
    sortField.addEventListener("change", render);
    sortDirection.addEventListener("change", render);

    sortableHeaders.forEach((th) => {
        th.addEventListener("click", () => {
            const key = th.getAttribute("data-sort-key");
            if (!key) return;
            if (sortField.value === key) {
                sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
            } else {
                sortField.value = key;
                sortDirection.value = "asc";
            }
            render();
        });
    });

    render();
})();
