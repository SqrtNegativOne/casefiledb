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

    // Flatten all episodes from tv_show items
    const episodes = [];
    for (const item of data) {
        if (item.media_type === "tv_show" && item.episodes && item.episodes.length) {
            for (let i = 0; i < item.episodes.length; i++) {
                const ep = item.episodes[i];
                episodes.push({
                    show: item.title,
                    showSlug: item.slug,
                    epIndex: i,
                    title: ep.title,
                    season: ep.season,
                    episode_number: ep.episode_number,
                    year: ep.year,
                    deaths: (ep.deaths || []).length,
                    url: `../media/?id=${encodeURIComponent(item.slug)}&ep=${i}`,
                });
            }
        }
    }

    const searchInput = document.getElementById("searchInput");
    const showFilter = document.getElementById("showFilter");
    const sortField = document.getElementById("sortField");
    const sortDirection = document.getElementById("sortDirection");
    const resultCount = document.getElementById("resultCount");
    const tableBody = document.getElementById("tableBody");
    const sortableHeaders = Array.from(document.querySelectorAll("th.sortable"));

    // Populate show filter
    const shows = Array.from(new Set(episodes.map((e) => e.show))).sort((a, b) =>
        a.localeCompare(b)
    );
    shows.forEach((show) => {
        const opt = document.createElement("option");
        opt.value = show;
        opt.textContent = show;
        showFilter.appendChild(opt);
    });

    // Pre-filter by ?show= param
    const params = new URLSearchParams(window.location.search);
    const showParam = params.get("show");
    if (showParam && shows.includes(showParam)) {
        showFilter.value = showParam;
    }

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

    function sortValue(ep, field) {
        if (field === "season") return ep.season ?? 9999;
        if (field === "episode") return ep.episode_number ?? 9999;
        if (field === "year") return ep.year ?? 0;
        if (field === "deaths") return ep.deaths;
        if (field === "show") return ep.show.toLowerCase();
        if (field === "title") return ep.title.toLowerCase();
        return 0;
    }

    function render() {
        const q = (searchInput.value || "").trim().toLowerCase();
        const show = showFilter.value;
        const field = sortField.value;
        const dir = sortDirection.value;
        const dirSign = dir === "desc" ? -1 : 1;

        const filtered = episodes.filter((ep) => {
            const matchesShow = !show || ep.show === show;
            const haystack = `${ep.title} ${ep.show}`.toLowerCase();
            const matchesSearch = !q || haystack.includes(q);
            return matchesShow && matchesSearch;
        });

        filtered.sort((a, b) => {
            const av = sortValue(a, field);
            const bv = sortValue(b, field);
            let result = 0;
            if (typeof av === "number" && typeof bv === "number") {
                result = av - bv;
            } else {
                result = String(av).localeCompare(String(bv), undefined, {
                    sensitivity: "base",
                    numeric: true,
                });
            }
            if (result === 0) result = a.show.localeCompare(b.show);
            if (result === 0) result = (a.season ?? 0) - (b.season ?? 0);
            if (result === 0) result = (a.episode_number ?? 0) - (b.episode_number ?? 0);
            return result * dirSign;
        });

        updateSortIndicators();
        resultCount.textContent = `${filtered.length} episode${filtered.length === 1 ? "" : "s"}`;

        if (!filtered.length) {
            tableBody.innerHTML = '<tr><td colspan="6" class="muted">No matches.</td></tr>';
            return;
        }

        tableBody.innerHTML = filtered
            .map((ep) => {
                const showUrl = `../media/?id=${encodeURIComponent(ep.showSlug)}`;
                return (
                    "<tr>" +
                    `<td><a href="${showUrl}">${esc(ep.show)}</a></td>` +
                    `<td>${ep.season ?? '<span class="muted">-</span>'}</td>` +
                    `<td>${ep.episode_number ?? '<span class="muted">-</span>'}</td>` +
                    `<td><a href="${ep.url}">${esc(ep.title)}</a></td>` +
                    `<td>${ep.year ?? '<span class="muted">-</span>'}</td>` +
                    `<td>${ep.deaths}</td>` +
                    "</tr>"
                );
            })
            .join("");
    }

    searchInput.addEventListener("input", render);
    showFilter.addEventListener("change", render);
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
