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

    // Fix hover-popup gap
    document.addEventListener("mouseover", (e) => {
        const hover = e.target.closest(".note-hover");
        if (hover) hover.classList.add("note-active");
    });
    document.addEventListener("mouseout", (e) => {
        const hover = e.target.closest(".note-hover");
        if (hover && !hover.contains(e.relatedTarget)) hover.classList.remove("note-active");
    });

    const data = await fetch("../site_data.json").then((r) => r.json()).catch(() => []);

    // Collect every death with its parent media context
    const deathsByMethod = new Map();
    for (const item of data) {
        const deaths = [
            ...(item.deaths || []).map((d) => ({ death: d, media: item, context: null })),
            ...(item.episodes || []).flatMap((ep) =>
                (ep.deaths || []).map((d) => ({ death: d, media: item, context: ep }))
            ),
            ...(item.cases || []).flatMap((c) =>
                (c.deaths || []).map((d) => ({ death: d, media: item, context: c }))
            ),
        ];
        for (const { death, media, context } of deaths) {
            const cause = death.cause || "UNKNOWN";
            if (!deathsByMethod.has(cause)) {
                deathsByMethod.set(cause, []);
            }
            deathsByMethod.get(cause).push({ death, media, context });
        }
    }

    const totalDeaths = Array.from(deathsByMethod.values()).reduce((n, arr) => n + arr.length, 0);

    // Sort methods by count descending
    const methods = Array.from(deathsByMethod.entries())
        .map(([cause, entries]) => ({ cause, entries }))
        .sort((a, b) => b.entries.length - a.entries.length);

    const resultCount = document.getElementById("resultCount");
    const tableBody = document.getElementById("tableBody");

    resultCount.textContent = `${methods.length} method${methods.length === 1 ? "" : "s"}, ${totalDeaths} deaths total`;

    const expandedMethods = new Set();

    function causeLabel(cause) {
        return cause.charAt(0) + cause.slice(1).toLowerCase().replace(/_/g, " ");
    }

    function renderExpandedRows(cause, entries) {
        // Group by media title for display
        const byMedia = new Map();
        for (const { death, media, context } of entries) {
            const key = media.slug;
            if (!byMedia.has(key)) {
                byMedia.set(key, { media, context, deaths: [] });
            }
            byMedia.get(key).deaths.push(death);
        }

        const rows = Array.from(byMedia.values())
            .sort((a, b) => String(a.media.title).localeCompare(String(b.media.title)))
            .map(({ media, context, deaths: ds }) => {
                const mediaUrl = `../media/?id=${encodeURIComponent(media.slug)}`;
                const contextLabel = context
                    ? ` <span class="muted">${esc(context.title || "")}</span>`
                    : "";
                const deathList = ds.map((d) => {
                    const cause = [d.cause, d.cause_subtype && `(${d.cause_subtype})`].filter(Boolean).join(" ");
                    const victim = d.victim_name || "Unknown";
                    const killer = d.killer_name || "Unknown";
                    const twist = d.is_twist ? ' <span class="badge">twist</span>' : "";
                    return (
                        "<tr>" +
                        `<td class="sensitive">${esc(victim)}</td>` +
                        `<td class="sensitive">${esc(killer)}</td>` +
                        `<td>${esc(cause)}${twist}</td>` +
                        "</tr>"
                    );
                }).join("");

                return (
                    `<tr class="details-row"><td colspan="4">` +
                    `<strong><a href="${mediaUrl}">${esc(media.title)}</a></strong>${contextLabel}` +
                    `<table class="mini-table" style="margin-top:0.4rem">` +
                    `<thead><tr><th>Victim</th><th>Killer</th><th>Cause</th></tr></thead>` +
                    `<tbody>${deathList}</tbody>` +
                    `</table>` +
                    `</td></tr>`
                );
            }).join("");

        return rows;
    }

    function render() {
        tableBody.innerHTML = methods.map(({ cause, entries }) => {
            const pct = totalDeaths > 0 ? ((entries.length / totalDeaths) * 100).toFixed(1) : "0.0";
            const open = expandedMethods.has(cause);
            const mainRow =
                "<tr>" +
                `<td>${esc(causeLabel(cause))}</td>` +
                `<td>${entries.length}</td>` +
                `<td>${pct}%</td>` +
                `<td><button type="button" class="toggle-method" data-cause="${esc(cause)}">${open ? "Hide" : "Show"}</button></td>` +
                "</tr>";
            const expandedHtml = open ? renderExpandedRows(cause, entries) : "";
            return mainRow + expandedHtml;
        }).join("");
    }

    tableBody.addEventListener("click", (e) => {
        const btn = e.target.closest(".toggle-method");
        if (!btn) return;
        const cause = btn.getAttribute("data-cause");
        if (!cause) return;
        if (expandedMethods.has(cause)) {
            expandedMethods.delete(cause);
        } else {
            expandedMethods.add(cause);
        }
        render();
    });

    render();
})();
