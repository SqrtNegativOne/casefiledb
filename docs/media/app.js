(async function () {
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

    // Fix hover-popup gap: track pointer entry/exit via delegation so the popup
    // stays open even when the cursor moves from the trigger into the popup itself.
    document.addEventListener("mouseover", (e) => {
        const hover = e.target.closest(".note-hover");
        if (hover) hover.classList.add("note-active");
    });
    document.addEventListener("mouseout", (e) => {
        const hover = e.target.closest(".note-hover");
        if (hover && !hover.contains(e.relatedTarget)) {
            hover.classList.remove("note-active");
        }
    });

    const data = await fetch("../site_data.json").then((r) => r.json()).catch(() => []);

    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    const epParam = params.get("ep");
    const caseParam = params.get("case");
    const epIndex = epParam !== null ? parseInt(epParam, 10) : null;
    const caseIndex = caseParam !== null ? parseInt(caseParam, 10) : null;

    const content = document.getElementById("content");

    function esc(v) {
        const s = v == null ? "" : String(v);
        return s
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function badge(text, extra) {
        return `<span class="badge${extra ? " " + extra : ""}">${esc(text)}</span>`;
    }

    function noteHover(rawText) {
        if (!rawText) return '<span class="muted">-</span>';
        return (
            '<span class="note-hover">' +
            '<span class="note-trigger">Hover to expand</span>' +
            '<span class="note-popover sensitive">' + esc(rawText) + "</span>" +
            "</span>"
        );
    }

    function personsTable(persons) {
        if (!persons || !persons.length) {
            return '<p class="muted">No persons listed.</p>';
        }
        const rows = persons
            .map(
                (p) =>
                    "<tr>" +
                    `<td class="sensitive">${esc(p.name || "Unknown")}</td>` +
                    `<td>${esc(p.role_in_story || "-")}</td>` +
                    `<td>${esc(p.profession || "-")}</td>` +
                    `<td>${noteHover(p.notes)}</td>` +
                    "</tr>"
            )
            .join("");
        return (
            '<div class="table-wrap">' +
            "<table>" +
            "<thead><tr><th>Name</th><th>Role</th><th>Profession</th><th>Notes</th></tr></thead>" +
            `<tbody>${rows}</tbody>` +
            "</table>" +
            "</div>"
        );
    }

    function deathsTable(deaths) {
        if (!deaths || !deaths.length) {
            return '<p class="muted">No deaths recorded.</p>';
        }
        const rows = deaths
            .map((d) => {
                const cause = [d.cause, d.cause_subtype && `(${d.cause_subtype})`]
                    .filter(Boolean)
                    .join(" ");
                return (
                    "<tr>" +
                    `<td>${esc(d.ordinal || "-")}</td>` +
                    `<td class="sensitive">${esc(d.victim_name || "Unknown")}</td>` +
                    `<td class="sensitive">${esc(cause)}</td>` +
                    `<td class="sensitive">${esc(d.killer_name || "Unknown")}</td>` +
                    `<td>${esc(d.death_type || "-")}</td>` +
                    `<td>${d.is_twist ? "Yes" : "No"}</td>` +
                    `<td>${noteHover(d.notes || d.cause_detail || d.motive_detail)}</td>` +
                    "</tr>"
                );
            })
            .join("");
        return (
            '<div class="table-wrap">' +
            "<table>" +
            "<thead><tr><th>#</th><th>Victim</th><th>Cause</th><th>Killer</th><th>Type</th><th>Twist</th><th>Notes</th></tr></thead>" +
            `<tbody>${rows}</tbody>` +
            "</table>" +
            "</div>"
        );
    }

    function metaLine(items) {
        const parts = items.filter(Boolean).map((x) => `<span>${x}</span>`).join("");
        return parts ? `<div class="media-meta">${parts}</div>` : "";
    }

    function tagList(tags) {
        if (!tags || !tags.length) return "";
        return '<div class="tag-list">' + tags.map((t) => badge(t)).join("") + "</div>";
    }

    if (!id) {
        content.innerHTML = '<p class="muted">No media ID specified. <a href="../">Back to index</a></p>';
        return;
    }

    let media = data.find((m) => m.slug === id);

    if (!media) {
        // Check if the id is an episode wikidata_id nested inside a show
        for (const item of data) {
            if (item.episodes) {
                const epIdx = item.episodes.findIndex((e) => e.wikidata_id === id);
                if (epIdx !== -1) {
                    window.location.replace(
                        `?id=${encodeURIComponent(item.wikidata_id)}&ep=${epIdx}`
                    );
                    return;
                }
            }
        }
        content.innerHTML = `<p class="muted">Media not found: <code>${esc(id)}</code>. <a href="../">Back to index</a></p>`;
        return;
    }

    let displayItem = null;
    let parentMedia = null;
    let subKind = null;

    if (epIndex !== null && media.episodes && media.episodes[epIndex]) {
        displayItem = media.episodes[epIndex];
        parentMedia = media;
        subKind = "episode";
    } else if (caseIndex !== null && media.cases && media.cases[caseIndex]) {
        displayItem = media.cases[caseIndex];
        parentMedia = media;
        subKind = "case";
    }

    function renderTopLevel(m) {
        document.title = `${m.title} — Casefile Database`;

        const wikidataLink = m.wikidata_id
            ? `<a href="https://www.wikidata.org/wiki/${encodeURIComponent(m.wikidata_id)}" target="_blank" rel="noopener noreferrer" class="mono">${esc(m.wikidata_id)}</a>`
            : '<span class="muted mono">no Wikidata entry</span>';

        const seriesInfo =
            m.series_name
                ? esc(m.series_name) + (m.series_number != null ? ` #${m.series_number}` : "")
                : null;

        let html =
            '<nav class="breadcrumb"><a href="../">Casefile Database</a> / ' +
            esc(m.title) +
            "</nav>" +
            '<div class="media-header">' +
            `<h2>${esc(m.title)}</h2>` +
            metaLine([m.creator && esc(m.creator), m.year && esc(m.year), badge(m.media_type), seriesInfo && `<span class="muted">${seriesInfo}</span>`, wikidataLink]) +
            tagList(m.tags) +
            (m.notes ? `<p class="media-notes">${esc(m.notes)}</p>` : "") +
            "</div>";

        if (m.media_type === "tv_show" && m.episodes && m.episodes.length) {
            html += "<h3>Episodes</h3>";
            html +=
                '<div class="table-wrap"><table>' +
                "<thead><tr><th>S</th><th>Ep</th><th>Title</th><th>Year</th><th>Deaths</th></tr></thead>" +
                "<tbody>" +
                m.episodes
                    .map((ep, idx) => {
                        const url = `?id=${encodeURIComponent(m.wikidata_id)}&ep=${idx}`;
                        return (
                            "<tr>" +
                            `<td>${esc(ep.season != null ? ep.season : "-")}</td>` +
                            `<td>${esc(ep.episode_number != null ? ep.episode_number : "-")}</td>` +
                            `<td><a href="${url}">${esc(ep.title)}</a></td>` +
                            `<td>${esc(ep.year != null ? ep.year : "-")}</td>` +
                            `<td>${(ep.deaths || []).length}</td>` +
                            "</tr>"
                        );
                    })
                    .join("") +
                "</tbody></table></div>";
        }

        if (m.media_type === "game" && m.cases && m.cases.length) {
            html += "<h3>Cases</h3>";
            html +=
                '<div class="table-wrap"><table>' +
                "<thead><tr><th>#</th><th>Title</th><th>Deaths</th></tr></thead>" +
                "<tbody>" +
                m.cases
                    .map((c, idx) => {
                        const url = `?id=${encodeURIComponent(m.wikidata_id)}&case=${idx}`;
                        return (
                            "<tr>" +
                            `<td>${esc(c.case_number != null ? c.case_number : idx + 1)}</td>` +
                            `<td><a href="${url}">${esc(c.title)}</a></td>` +
                            `<td>${(c.deaths || []).length}</td>` +
                            "</tr>"
                        );
                    })
                    .join("") +
                "</tbody></table></div>";
        }

        if (m.persons && m.persons.length) {
            html += "<h3>Persons</h3>" + personsTable(m.persons);
        }

        if (m.deaths && m.deaths.length) {
            html += "<h3>Deaths</h3>" + deathsTable(m.deaths);
        }

        content.innerHTML = html;
    }

    function renderSubItem(item, parent, kind) {
        document.title = `${item.title} — ${parent.title} — Casefile Database`;

        const parentUrl = `?id=${encodeURIComponent(parent.wikidata_id)}`;
        const kindLabel = kind === "episode" ? "episode" : "case";

        const metaParts = [];
        if (kind === "episode") {
            if (item.season != null) metaParts.push(`Season ${esc(item.season)}`);
            if (item.episode_number != null) metaParts.push(`Episode ${esc(item.episode_number)}`);
            if (item.year != null) metaParts.push(esc(item.year));
        } else {
            if (item.case_number != null) metaParts.push(`Case ${esc(item.case_number)}`);
        }

        let html =
            '<nav class="breadcrumb">' +
            '<a href="../">Casefile Database</a> / ' +
            `<a href="${parentUrl}">${esc(parent.title)}</a> / ` +
            esc(item.title) +
            "</nav>" +
            '<div class="media-header">' +
            `<h2>${esc(item.title)}</h2>` +
            metaLine([...metaParts.map((p) => `<span>${p}</span>`), badge(kindLabel)].filter(Boolean)) +
            tagList(item.tags) +
            (item.notes ? `<p class="media-notes">${esc(item.notes)}</p>` : "") +
            "</div>";

        if (item.persons && item.persons.length) {
            html += "<h3>Persons</h3>" + personsTable(item.persons);
        }

        if (item.deaths && item.deaths.length) {
            html += "<h3>Deaths</h3>" + deathsTable(item.deaths);
        }

        content.innerHTML = html;
    }

    if (displayItem) {
        renderSubItem(displayItem, parentMedia, subKind);
    } else {
        renderTopLevel(media);
    }
})();
