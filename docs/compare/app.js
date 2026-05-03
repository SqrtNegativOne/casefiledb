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

    function allDeaths(item) {
        return [
            ...(item.deaths || []),
            ...(item.episodes || []).flatMap((e) => e.deaths || []),
            ...(item.cases || []).flatMap((c) => c.deaths || []),
        ];
    }

    function deathCount(item) {
        return allDeaths(item).length;
    }

    // Build author aggregates
    const authorMap = new Map();
    for (const item of data) {
        const creator = item.creator || "Unknown";
        if (!authorMap.has(creator)) {
            authorMap.set(creator, { name: creator, works: [] });
        }
        authorMap.get(creator).works.push(item);
    }
    const authors = Array.from(authorMap.values()).sort((a, b) =>
        a.name.localeCompare(b.name)
    );

    function topN(counts, n) {
        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, n);
    }

    function statsForItems(items) {
        const deaths = items.flatMap(allDeaths);
        const total = deaths.length;
        const works = items.length;
        const twists = deaths.filter((d) => d.is_twist).length;
        const twistRate = total > 0 ? ((twists / total) * 100).toFixed(1) : "0.0";

        const causeCounts = {};
        const motiveCounts = {};
        const typeCounts = {};
        for (const d of deaths) {
            if (d.cause) causeCounts[d.cause] = (causeCounts[d.cause] || 0) + 1;
            if (d.motive) motiveCounts[d.motive] = (motiveCounts[d.motive] || 0) + 1;
            if (d.death_type) typeCounts[d.death_type] = (typeCounts[d.death_type] || 0) + 1;
        }

        return {
            works,
            total,
            avgPerWork: works > 0 ? (total / works).toFixed(1) : "0.0",
            twists,
            twistRate,
            topCauses: topN(causeCounts, 3),
            topMotives: topN(motiveCounts, 3),
            topTypes: topN(typeCounts, 3),
        };
    }

    function statsForAuthor(author) {
        return statsForItems(author.works);
    }

    function statsForMedia(item) {
        return statsForItems([item]);
    }

    function renderTopList(pairs) {
        if (!pairs.length) return '<span class="muted">none</span>';
        return (
            '<ul class="top-list">' +
            pairs
                .map(
                    ([label, count]) =>
                        `<li><span>${esc(label.toLowerCase().replace(/_/g, " "))}</span><strong>${count}</strong></li>`
                )
                .join("") +
            "</ul>"
        );
    }

    function renderPanel(stats, name) {
        const avgNum = parseFloat(stats.avgPerWork);
        return (
            `<div style="font-weight:600;font-size:1.05rem;margin-bottom:0.75rem">${esc(name)}</div>` +
            '<div class="stat-row">' +
            '<span class="stat-label">Works</span>' +
            `<span class="stat-value">${stats.works}</span>` +
            "</div>" +
            '<div class="stat-row">' +
            '<span class="stat-label">Total deaths</span>' +
            `<span class="stat-value">${stats.total}</span>` +
            "</div>" +
            '<div class="stat-row">' +
            '<span class="stat-label">Avg deaths / work</span>' +
            `<span class="stat-value">${stats.avgPerWork}</span>` +
            "</div>" +
            '<div class="stat-row">' +
            '<span class="stat-label">Twist deaths</span>' +
            `<span class="stat-value">${stats.twists} <span class="muted" style="font-weight:400;font-size:0.85rem">(${stats.twistRate}%)</span></span>` +
            "</div>" +
            '<div class="stat-row" style="flex-direction:column;align-items:flex-start;gap:0.3rem">' +
            '<span class="stat-label">Top causes</span>' +
            renderTopList(stats.topCauses) +
            "</div>" +
            '<div class="stat-row" style="flex-direction:column;align-items:flex-start;gap:0.3rem">' +
            '<span class="stat-label">Top motives</span>' +
            renderTopList(stats.topMotives) +
            "</div>" +
            '<div class="stat-row" style="flex-direction:column;align-items:flex-start;gap:0.3rem">' +
            '<span class="stat-label">Death types</span>' +
            renderTopList(stats.topTypes) +
            "</div>"
        );
    }

    function populateSelect(selectEl, mode) {
        selectEl.innerHTML = '<option value="">— select —</option>';
        if (mode === "author") {
            authors.forEach((a) => {
                const opt = document.createElement("option");
                opt.value = "author:" + a.name;
                opt.textContent = `${a.name} (${a.works.length} works)`;
                selectEl.appendChild(opt);
            });
        } else {
            const sorted = [...data].sort((a, b) =>
                String(a.title).localeCompare(String(b.title))
            );
            sorted.forEach((item) => {
                const opt = document.createElement("option");
                opt.value = "media:" + item.slug;
                opt.textContent = `${item.title} (${item.year || "?"})`;
                selectEl.appendChild(opt);
            });
        }
    }

    function getStatsAndName(value) {
        if (!value) return null;
        const [type, key] = value.split(/:(.+)/);
        if (type === "author") {
            const author = authorMap.get(key);
            if (!author) return null;
            return { name: author.name, stats: statsForAuthor(author) };
        } else {
            const item = data.find((m) => m.slug === key);
            if (!item) return null;
            return {
                name: `${item.title} (${item.creator || "?"}, ${item.year || "?"})`,
                stats: statsForMedia(item),
            };
        }
    }

    const modeA = document.getElementById("modeA");
    const modeB = document.getElementById("modeB");
    const selectA = document.getElementById("selectA");
    const selectB = document.getElementById("selectB");
    const panelA = document.getElementById("panelA");
    const panelB = document.getElementById("panelB");

    populateSelect(selectA, "author");
    populateSelect(selectB, "author");

    function updatePanel(selectEl, panelEl) {
        const result = getStatsAndName(selectEl.value);
        if (!result) {
            panelEl.innerHTML = '<p class="compare-hint">Select an author or work above.</p>';
            return;
        }
        panelEl.innerHTML = renderPanel(result.stats, result.name);
    }

    modeA.addEventListener("change", () => {
        populateSelect(selectA, modeA.value);
        updatePanel(selectA, panelA);
    });
    modeB.addEventListener("change", () => {
        populateSelect(selectB, modeB.value);
        updatePanel(selectB, panelB);
    });
    selectA.addEventListener("change", () => updatePanel(selectA, panelA));
    selectB.addEventListener("change", () => updatePanel(selectB, panelB));

    // Deep-link: ?a=author:Agatha+Christie&b=author:Andy+Breckman
    const params = new URLSearchParams(window.location.search);
    const aParam = params.get("a");
    const bParam = params.get("b");
    if (aParam) {
        const [aType] = aParam.split(":");
        modeA.value = aType === "media" ? "media" : "author";
        populateSelect(selectA, modeA.value);
        selectA.value = aParam;
        updatePanel(selectA, panelA);
    }
    if (bParam) {
        const [bType] = bParam.split(":");
        modeB.value = bType === "media" ? "media" : "author";
        populateSelect(selectB, modeB.value);
        selectB.value = bParam;
        updatePanel(selectB, panelB);
    }
})();
