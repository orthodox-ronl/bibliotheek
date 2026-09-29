/**
 * Client-side zoeken over static/zoek/index.json.
 * Activeert alleen als #bibliotheek-zoek-form op de pagina staat.
 */
(function () {
  const form = document.getElementById("bibliotheek-zoek-form");
  if (!form) return;

  const input = document.getElementById("bibliotheek-zoek-q");
  const out = document.getElementById("bibliotheek-zoek-resultaten");
  const meta = document.getElementById("bibliotheek-zoek-meta");
  if (!input || !out) return;

  let entries = [];

  function normalize(s) {
    return String(s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\w\s]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function tokenSort(s) {
    return Array.from(new Set(normalize(s).split(" ").filter(Boolean)))
      .sort()
      .join(" ");
  }

  function score(entry, qNorm, qTokens) {
    if (!qNorm) return 0;
    let s = 0;
    const title = normalize(entry.title + " " + entry.linkTitle);
    const id = normalize(entry.id.replace(/\//g, " ").replace(/-/g, " "));
    if (title.includes(qNorm)) s += 50;
    if (id.includes(qNorm)) s += 30;
    if ((entry.text || "").includes(qNorm)) s += 20;
    if (qTokens && entry.tokens && entry.tokens.includes(qTokens)) s += 25;
    // Deelmatches op query-woorden
    const words = qNorm.split(" ").filter(Boolean);
    let hit = 0;
    for (const w of words) {
      if ((entry.text || "").includes(w) || title.includes(w)) hit += 1;
    }
    if (words.length) s += (hit / words.length) * 15;
    return s;
  }

  function render(rows, q) {
    if (!q) {
      out.innerHTML = "<p class=\"bibliotheek-zoek-leeg\">Typ een titel, id of stukje tekst.</p>";
      if (meta) meta.textContent = "";
      return;
    }
    if (!rows.length) {
      out.innerHTML = "<p class=\"bibliotheek-zoek-leeg\">Geen treffers.</p>";
      if (meta) meta.textContent = "";
      return;
    }
    if (meta) meta.textContent = rows.length + " treffer(s)";
    const html = ["<ul class=\"bibliotheek-zoek-lijst\">"];
    for (const row of rows.slice(0, 40)) {
      const e = row.entry;
      const status = e.status ? ` <span class="bibliotheek-zoek-status">${escapeHtml(e.status)}</span>` : "";
      const incipit = e.incipit
        ? `<div class="bibliotheek-zoek-incipit">${escapeHtml(e.incipit)}</div>`
        : "";
      html.push(
        `<li><a href="${escapeAttr(e.url)}"><strong>${escapeHtml(e.title)}</strong></a>` +
          status +
          `<div class="bibliotheek-zoek-id"><code>${escapeHtml(e.id)}</code></div>` +
          incipit +
          `</li>`
      );
    }
    html.push("</ul>");
    out.innerHTML = html.join("");
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function run() {
    const q = input.value.trim();
    const qNorm = normalize(q);
    const qTokens = tokenSort(q);
    const scored = [];
    for (const entry of entries) {
      const sc = score(entry, qNorm, qTokens);
      if (sc > 0) scored.push({ entry, sc });
    }
    scored.sort((a, b) => b.sc - a.sc || a.entry.id.localeCompare(b.entry.id));
    render(scored, q);
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    run();
  });
  input.addEventListener("input", function () {
    run();
  });

  const indexUrl = form.getAttribute("data-index") || "/zoek/index.json";
  fetch(indexUrl)
    .then(function (r) {
      if (!r.ok) throw new Error("index niet geladen");
      return r.json();
    })
    .then(function (data) {
      entries = data.entries || [];
      if (meta) {
        meta.textContent =
          (data.count || entries.length) + " uitvoeringsvormen in de index";
      }
      if (input.value.trim()) run();
    })
    .catch(function () {
      out.innerHTML =
        "<p class=\"bibliotheek-zoek-leeg\">Zoekindex ontbreekt. Draai <code>python scripts\\build_zoek_index.py</code> (na lyrics-products).</p>";
    });
})();
