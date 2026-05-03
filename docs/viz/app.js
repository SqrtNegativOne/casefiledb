(async function () {
    function esc(v) {
        const s = v == null ? "" : String(v);
        return s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
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
        renderAll();
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

    // ─── SVG helpers ────────────────────────────────────────────────────────
    const NS = "http://www.w3.org/2000/svg";

    function svgEl(tag, attrs = {}) {
        const el = document.createElementNS(NS, tag);
        for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
        return el;
    }

    function svgText(content, attrs = {}) {
        const el = svgEl("text", attrs);
        el.textContent = content;
        return el;
    }

    // ─── Chart 1: deaths by year (bar + error bars) ─────────────────────────
    function buildYearChart() {
        const yearCounts = {};
        for (const item of data) {
            const deaths = allDeaths(item);
            if (!deaths.length) continue;
            const year = item.year;
            if (!year) continue;
            yearCounts[year] = (yearCounts[year] || 0) + deaths.length;
        }

        const years = Object.keys(yearCounts).map(Number).sort((a, b) => a - b);
        if (!years.length) return null;

        const counts = years.map((y) => yearCounts[y]);
        const maxCount = Math.max(...counts);

        const W = 860, H = 260;
        const padL = 40, padR = 20, padT = 30, padB = 50;
        const chartW = W - padL - padR;
        const chartH = H - padT - padB;
        const barW = Math.max(2, Math.floor(chartW / years.length) - 2);

        const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, style: "width:100%;height:auto;overflow:visible" });

        // Gridlines
        const gridSteps = 4;
        for (let i = 0; i <= gridSteps; i++) {
            const y = padT + chartH - (i / gridSteps) * chartH;
            const line = svgEl("line", {
                class: "gridline",
                x1: padL, y1: y, x2: padL + chartW, y2: y,
            });
            svg.appendChild(line);
            if (i > 0) {
                svg.appendChild(svgText(Math.round((i / gridSteps) * maxCount), {
                    class: "axis-label",
                    x: padL - 6, y: y + 4,
                    "text-anchor": "end",
                }));
            }
        }

        // Bars + error bars + labels
        const xStep = chartW / years.length;
        years.forEach((year, i) => {
            const count = yearCounts[year];
            const barH = (count / maxCount) * chartH;
            const x = padL + i * xStep + (xStep - barW) / 2;
            const y = padT + chartH - barH;

            // Bar
            const rect = svgEl("rect", {
                class: "bar",
                x, y, width: barW, height: barH,
                rx: 2,
            });
            rect.appendChild(svgEl("title"));
            rect.querySelector("title").textContent = `${year}: ${count} deaths`;
            svg.appendChild(rect);

            // Error bar (±√count, visually represents sampling uncertainty)
            const err = Math.max(1, Math.round(Math.sqrt(count)));
            const errPx = (err / maxCount) * chartH;
            const cx = x + barW / 2;
            const capW = Math.max(3, barW * 0.4);

            const errLine = svgEl("line", {
                class: "error-bar",
                x1: cx, y1: y - errPx, x2: cx, y2: y + errPx,
            });
            svg.appendChild(errLine);
            svg.appendChild(svgEl("line", { class: "error-cap", x1: cx - capW / 2, y1: y - errPx, x2: cx + capW / 2, y2: y - errPx }));
            svg.appendChild(svgEl("line", { class: "error-cap", x1: cx - capW / 2, y1: y + errPx, x2: cx + capW / 2, y2: y + errPx }));
        });

        // X axis labels (every N years to avoid crowding)
        const labelEvery = years.length > 40 ? 10 : years.length > 20 ? 5 : 1;
        years.forEach((year, i) => {
            if (i % labelEvery !== 0) return;
            const cx = padL + i * xStep + xStep / 2;
            svg.appendChild(svgText(year, {
                class: "axis-label",
                x: cx, y: padT + chartH + 18,
                "text-anchor": "middle",
            }));
        });

        // Axis lines
        svg.appendChild(svgEl("line", { stroke: "var(--border)", x1: padL, y1: padT, x2: padL, y2: padT + chartH }));
        svg.appendChild(svgEl("line", { stroke: "var(--border)", x1: padL, y1: padT + chartH, x2: padL + chartW, y2: padT + chartH }));

        return svg;
    }

    // ─── Chart 2: death causes (horizontal bars) ──────────────────────────
    function buildCausesChart() {
        const counts = {};
        for (const item of data) {
            for (const d of allDeaths(item)) {
                if (d.cause) counts[d.cause] = (counts[d.cause] || 0) + 1;
            }
        }

        const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
        const total = sorted.reduce((n, [, c]) => n + c, 0);
        const maxCount = sorted[0]?.[1] ?? 1;

        const rowH = 26, padL = 110, padR = 60, padT = 10, padB = 10;
        const barAreaW = 520;
        const W = padL + barAreaW + padR;
        const H = padT + rowH * sorted.length + padB;

        const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, style: "width:100%;max-width:700px;height:auto" });

        sorted.forEach(([cause, count], i) => {
            const y = padT + i * rowH;
            const barW = (count / maxCount) * barAreaW;
            const cx = y + rowH / 2 + 5;

            // Label
            svg.appendChild(svgText(cause.charAt(0) + cause.slice(1).toLowerCase(), {
                class: "axis-label",
                x: padL - 8, y: cx,
                "text-anchor": "end",
                "dominant-baseline": "middle",
            }));

            // Bar
            const rect = svgEl("rect", {
                class: "bar",
                x: padL, y: y + 4,
                width: Math.max(2, barW), height: rowH - 8,
                rx: 3,
            });
            rect.appendChild(svgEl("title"));
            rect.querySelector("title").textContent = `${cause}: ${count} (${((count / total) * 100).toFixed(1)}%)`;
            svg.appendChild(rect);

            // Count label
            svg.appendChild(svgText(`${count}`, {
                x: padL + barW + 6, y: cx,
                "dominant-baseline": "middle",
                "font-size": "11",
                fill: "var(--muted)",
            }));
        });

        return svg;
    }

    // ─── Chart 3: deaths by media type ────────────────────────────────────
    function buildTypeChart() {
        const counts = {};
        const workCounts = {};
        for (const item of data) {
            const t = item.media_type || "unknown";
            workCounts[t] = (workCounts[t] || 0) + 1;
            counts[t] = (counts[t] || 0) + allDeaths(item).length;
        }

        const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
        const maxCount = sorted[0]?.[1] ?? 1;

        const rowH = 30, padL = 90, padR = 70, padT = 10, padB = 10;
        const barAreaW = 480;
        const W = padL + barAreaW + padR;
        const H = padT + rowH * sorted.length + padB;

        const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, style: "width:100%;max-width:680px;height:auto" });

        sorted.forEach(([type, count], i) => {
            const y = padT + i * rowH;
            const barW = (count / maxCount) * barAreaW;
            const cy = y + rowH / 2 + 4;
            const works = workCounts[type] || 0;
            const perWork = works > 0 ? (count / works).toFixed(1) : "0";

            svg.appendChild(svgText(type, {
                class: "axis-label",
                x: padL - 8, y: cy,
                "text-anchor": "end",
                "dominant-baseline": "middle",
            }));

            // Background track
            svg.appendChild(svgEl("rect", {
                class: "bar-secondary",
                x: padL, y: y + 6,
                width: barAreaW, height: rowH - 12,
                rx: 3,
            }));

            // Actual bar
            const rect = svgEl("rect", {
                class: "bar",
                x: padL, y: y + 6,
                width: Math.max(2, barW), height: rowH - 12,
                rx: 3,
            });
            rect.appendChild(svgEl("title"));
            rect.querySelector("title").textContent =
                `${type}: ${count} deaths across ${works} work${works !== 1 ? "s" : ""} (${perWork} avg)`;
            svg.appendChild(rect);

            svg.appendChild(svgText(`${count} deaths · ${perWork}/work`, {
                x: padL + barAreaW + 8, y: cy,
                "dominant-baseline": "middle",
                "font-size": "11",
                fill: "var(--muted)",
            }));
        });

        return svg;
    }

    // ─── Render ─────────────────────────────────────────────────────────────
    function renderAll() {
        const wrap = document.getElementById("vizWrap");
        wrap.innerHTML = "";

        const yearSvg = buildYearChart();
        if (yearSvg) {
            const card = document.createElement("div");
            card.className = "viz-card";
            card.innerHTML =
                '<h2>Deaths per year</h2>' +
                '<p class="viz-subtitle">Total recorded deaths by publication / air year. Error bars show ±√n.</p>';
            card.appendChild(yearSvg);
            card.innerHTML +=
                '<div class="viz-legend">' +
                '<span><span class="legend-dot"></span> deaths</span>' +
                '<span style="color:var(--muted);font-size:0.78rem">error bars: ±√n</span>' +
                "</div>";
            wrap.appendChild(card);
        }

        const causesCard = document.createElement("div");
        causesCard.className = "viz-card";
        causesCard.innerHTML =
            '<h2>Deaths by method</h2>' +
            '<p class="viz-subtitle">All recorded death causes across the database.</p>';
        causesCard.appendChild(buildCausesChart());
        wrap.appendChild(causesCard);

        const typeCard = document.createElement("div");
        typeCard.className = "viz-card";
        typeCard.innerHTML =
            '<h2>Deaths by media type</h2>' +
            '<p class="viz-subtitle">Total deaths and per-work average, broken down by format.</p>';
        typeCard.appendChild(buildTypeChart());
        wrap.appendChild(typeCard);
    }

    renderAll();
})();
