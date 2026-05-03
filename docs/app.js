(async function () {
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

    const data = await fetch("site_data.json").then((r) => r.json()).catch(() => []);
    const body = document.getElementById("mediaTableBody");
    const searchInput = document.getElementById("searchInput");
    const typeFilter = document.getElementById("typeFilter");
    const deathsFilter = document.getElementById("deathsFilter");
    const twistFilter = document.getElementById("twistFilter");
    const sortField = document.getElementById("sortField");
    const sortDirection = document.getElementById("sortDirection");
    const resultCount = document.getElementById("resultCount");
    const themeToggle = document.getElementById("themeToggle");
    const sortableHeaders = Array.from(document.querySelectorAll("th.sortable"));
    const expandedRows = new Set();

    function escapeHtml(value) {
        const text = value == null ? "" : String(value);
        return text
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function noteHover(rawText) {
        if (!rawText) {
            return '<span class="muted">-</span>';
        }
        return (
            '<span class="note-hover">' +
            '<span class="note-trigger">Hover to expand</span>' +
            '<span class="note-popover sensitive">' +
            escapeHtml(rawText) +
            "</span>" +
            "</span>"
        );
    }

    function hasTwist(media) {
        const allDeaths = [
            ...(media.deaths || []),
            ...(media.cases || []).flatMap((c) => c.deaths || []),
            ...(media.episodes || []).flatMap((e) => e.deaths || []),
        ];
        return allDeaths.some((d) => Boolean(d.is_twist));
    }

    function deathCount(media) {
        const direct = (media.deaths || []).length;
        const inCases = (media.cases || []).reduce((n, c) => n + (c.deaths || []).length, 0);
        const inEpisodes = (media.episodes || []).reduce((n, e) => n + (e.deaths || []).length, 0);
        return direct + inCases + inEpisodes;
    }

    function sortValue(media, field) {
        if (field === "deaths") {
            return deathCount(media);
        }
        if (field === "year") {
            return Number(media.year || 0);
        }
        return String(media[field] || "").toLowerCase();
    }

    function updateSortIndicators() {
        const field = sortField.value;
        const direction = sortDirection.value;
        sortableHeaders.forEach((header) => {
            const key = header.getAttribute("data-sort-key");
            if (key === field) {
                header.setAttribute("data-sort-state", direction);
            } else {
                header.removeAttribute("data-sort-state");
            }
        });
    }

    function filteredAndSortedRows() {
        const q = (searchInput.value || "").trim().toLowerCase();
        const type = typeFilter.value;
        const minDeaths = deathsFilter.value;
        const onlyTwist = twistFilter.checked;
        const field = sortField.value;
        const direction = sortDirection.value;
        const directionSign = direction === "desc" ? -1 : 1;

        const filtered = data.filter((media) => {
            const tags = Array.isArray(media.tags) ? media.tags.join(" ") : "";
            const haystack = `${media.title || ""} ${media.creator || ""} ${media.media_type || ""} ${media.wikidata_id || ""} ${tags}`.toLowerCase();
            const matchesSearch = !q || haystack.includes(q);
            const matchesType = !type || media.media_type === type;
            const deaths = deathCount(media);
            const matchesDeaths =
                !minDeaths || (minDeaths === "0" ? deaths === 0 : deaths >= Number(minDeaths));
            const matchesTwist = !onlyTwist || hasTwist(media);
            return matchesSearch && matchesType && matchesDeaths && matchesTwist;
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
            if (result === 0) {
                result = String(a.title || "").localeCompare(String(b.title || ""));
            }
            return result * directionSign;
        });

        return filtered;
    }

    function renderDetails(media) {
        const persons = (media.persons || [])
            .map(
                (person) =>
                    "<tr>" +
                    `<td class="sensitive">${escapeHtml(person.name || "Unknown")}</td>` +
                    `<td>${escapeHtml(person.role_in_story || "unknown")}</td>` +
                    `<td>${noteHover(person.notes)}</td>` +
                    "</tr>"
            )
            .join("");

        const deaths = (media.deaths || [])
            .map((death) => {
                const cause = [death.cause, death.cause_subtype && `(${death.cause_subtype})`]
                    .filter(Boolean)
                    .join(" ");
                const twistLabel = death.is_twist ? "Yes" : "No";
                return (
                    "<tr>" +
                    `<td>${escapeHtml(death.ordinal || "-")}</td>` +
                    `<td class="sensitive">${escapeHtml(death.victim_name || "Unknown")}</td>` +
                    `<td class="sensitive">${escapeHtml(cause || "Unknown")}</td>` +
                    `<td class="sensitive">${escapeHtml(death.killer_name || "Unknown")}</td>` +
                    `<td>${escapeHtml(death.death_type || "unknown")}</td>` +
                    `<td>${twistLabel}</td>` +
                    `<td>${noteHover(death.notes || death.cause_detail || death.motive_detail)}</td>` +
                    "</tr>"
                );
            })
            .join("");

        return (
            '<div class="details-grid">' +
            "<div>" +
            (media.wikidata_id
                ? `<strong>Wikidata:</strong> <a href="https://www.wikidata.org/wiki/${encodeURIComponent(media.wikidata_id)}" target="_blank" rel="noopener noreferrer">${escapeHtml(media.wikidata_id)}</a>`
                : '<strong>Wikidata:</strong> <span class="muted">none</span>') +
            "</div>" +
            "<div>" +
            "<strong>Persons</strong>" +
            '<table class="mini-table">' +
            "<thead><tr><th>Name</th><th>Role</th><th>Notes</th></tr></thead>" +
            `<tbody>${persons || '<tr><td colspan="3" class="muted">No persons</td></tr>'}</tbody>` +
            "</table>" +
            "</div>" +
            "<div>" +
            "<strong>Deaths</strong>" +
            '<table class="mini-table">' +
            "<thead><tr><th>#</th><th>Victim</th><th>Cause</th><th>Killer</th><th>Type</th><th>Twist</th><th>Notes</th></tr></thead>" +
            `<tbody>${deaths || '<tr><td colspan="7" class="muted">No deaths</td></tr>'}</tbody>` +
            "</table>" +
            "</div>" +
            "</div>"
        );
    }

    function getTheme() {
        const saved = localStorage.getItem("casefile-theme");
        if (saved === "light" || saved === "dark") {
            return saved;
        }
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("casefile-theme", theme);
        themeToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
    }

    function render() {
        const rows = filteredAndSortedRows();
        updateSortIndicators();
        resultCount.textContent = `${rows.length} result${rows.length === 1 ? "" : "s"}`;

        if (!rows.length) {
            body.innerHTML = '<tr><td colspan="7" class="muted">No matches.</td></tr>';
            return;
        }

        body.innerHTML = rows
            .map((media) => {
                const open = expandedRows.has(media.slug);
                const title = escapeHtml(media.title || media.slug);
                const creator = escapeHtml(media.creator || "Unknown");
                const year = escapeHtml(media.year || "-");
                const type = escapeHtml(media.media_type || "-");
                const notes = noteHover(media.notes);
                const detailsClass = open ? "details-row" : "details-row hidden";
                const details = open ? renderDetails(media) : "";

                return (
                    "<tr>" +
                    "<td>" +
                    `<a href="media/?id=${encodeURIComponent(media.slug)}">${title}</a>` +
                    `<div class="mono">${escapeHtml(media.slug)}</div>` +
                    "</td>" +
                    `<td>${creator}</td>` +
                    `<td>${year}</td>` +
                    `<td>${type}</td>` +
                    `<td>${deathCount(media)}</td>` +
                    `<td>${notes}</td>` +
                    `<td><button type="button" class="toggle-details" data-id="${escapeHtml(media.slug)}">${open ? "Hide" : "Details"}</button></td>` +
                    "</tr>" +
                    `<tr class="${detailsClass}" data-details-id="${escapeHtml(media.slug)}"><td colspan="7">${details}</td></tr>`
                );
            })
            .join("");
    }

    function populateTypeFilter() {
        const types = Array.from(new Set(data.map((item) => item.media_type).filter(Boolean))).sort(
            (a, b) => a.localeCompare(b)
        );
        types.forEach((type) => {
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            typeFilter.appendChild(option);
        });
    }

    themeToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
        setTheme(current === "dark" ? "light" : "dark");
    });

    searchInput.addEventListener("input", render);
    typeFilter.addEventListener("change", render);
    deathsFilter.addEventListener("change", render);
    twistFilter.addEventListener("change", render);
    sortField.addEventListener("change", render);
    sortDirection.addEventListener("change", render);

    sortableHeaders.forEach((header) => {
        header.addEventListener("click", () => {
            const key = header.getAttribute("data-sort-key");
            if (!key) {
                return;
            }
            if (sortField.value === key) {
                sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
            } else {
                sortField.value = key;
                sortDirection.value = "asc";
            }
            render();
        });
    });

    body.addEventListener("click", (event) => {
        const button = event.target.closest(".toggle-details");
        if (!button) {
            return;
        }
        const id = button.getAttribute("data-id");
        if (!id) {
            return;
        }
        if (expandedRows.has(id)) {
            expandedRows.delete(id);
        } else {
            expandedRows.add(id);
        }
        render();
    });

    setTheme(getTheme());
    populateTypeFilter();
    render();
})();
