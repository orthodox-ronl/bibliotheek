/**
 * Client-side zoeken over static/zoek/index.json.
 *
 * Werkt op elke .catalogus-zoek-root (pagina-formulier én header-overlay).
 * Synoniemen uit index.json (data/zoek-synoniemen.yaml).
 * Trefferregel: afspelen .mp3 (snelheid via popover, default 1,5×,
 * sessionStorage) + klik op id kopieert {{< bieb id="…" >}}.
 */
(function () {
  const roots = Array.from(document.querySelectorAll(".catalogus-zoek"));
  if (!roots.length) return;

  let entries = [];
  let synonyms = {};
  let indexPromise = null;

  /** Één gedeelde speler voor zoektreffers. */
  const player = new Audio();
  let playingBtn = null;

  /** Afspeelsnelheid voor treffers: tab-sessie (sessionStorage), default 1,5×. */
  const RATE_KEY = "orthodox-ronl-bibliotheek-zoek-rate";
  const DEFAULT_RATE = 1.5;
  const RATE_OPTIONS = [0.75, 1, 1.25, 1.5, 2];
  let memoryRate = DEFAULT_RATE;

  function formatRate(rate) {
    const n = Number(rate);
    if (!isFinite(n)) return "1,5×";
    return String(n).replace(".", ",") + "×";
  }

  function normalizeRate(value) {
    const n = parseFloat(value, 10);
    if (!isFinite(n)) return DEFAULT_RATE;
    for (let i = 0; i < RATE_OPTIONS.length; i++) {
      if (Math.abs(RATE_OPTIONS[i] - n) < 0.001) return RATE_OPTIONS[i];
    }
    return DEFAULT_RATE;
  }

  function getRate() {
    try {
      const raw = sessionStorage.getItem(RATE_KEY);
      if (raw != null && raw !== "") {
        memoryRate = normalizeRate(raw);
        return memoryRate;
      }
    } catch (e) {
      /* private mode / geblokkeerd: geheugen blijft gelden tot tab dicht */
    }
    return memoryRate;
  }

  function setRate(value) {
    memoryRate = normalizeRate(value);
    try {
      sessionStorage.setItem(RATE_KEY, String(memoryRate));
    } catch (e) {
      /* ignore */
    }
    applyPlaybackRate();
    syncRateUi(document);
  }

  function applyPlaybackRate() {
    try {
      player.playbackRate = getRate();
    } catch (e) {
      try {
        player.playbackRate = DEFAULT_RATE;
      } catch (e2) {
        /* ignore */
      }
    }
  }

  function syncRateUi(scope) {
    const root = scope || document;
    const label = formatRate(getRate());
    root.querySelectorAll(".catalogus-zoek-rate-trigger").forEach(function (btn) {
      btn.textContent = label;
      btn.setAttribute(
        "aria-label",
        "Afspeelsnelheid zoektreffers: " + label + ". Klik om te wijzigen."
      );
      btn.title = "Afspeelsnelheid voor zoektreffers (" + label + ")";
    });
    root.querySelectorAll(".catalogus-zoek-rate-option").forEach(function (opt) {
      const active = normalizeRate(opt.getAttribute("data-rate")) === getRate();
      opt.classList.toggle("is-active", active);
      opt.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function closeAllRatePanels(scope) {
    const root = scope || document;
    root.querySelectorAll(".catalogus-zoek-rate.is-open").forEach(function (wrap) {
      wrap.classList.remove("is-open");
      const btn = wrap.querySelector(".catalogus-zoek-rate-trigger");
      const panel = wrap.querySelector(".catalogus-zoek-rate-panel");
      if (btn) btn.setAttribute("aria-expanded", "false");
      if (panel) panel.hidden = true;
    });
  }

  function rateControlHtml() {
    const current = getRate();
    const opts = RATE_OPTIONS.map(function (r) {
      const active = r === current;
      return (
        '<button type="button" class="catalogus-zoek-rate-option' +
        (active ? " is-active" : "") +
        '" data-rate="' +
        r +
        '" aria-pressed="' +
        (active ? "true" : "false") +
        '">' +
        formatRate(r) +
        "</button>"
      );
    }).join("");
    return (
      '<span class="catalogus-zoek-rate">' +
      '<button type="button" class="catalogus-zoek-rate-trigger" aria-expanded="false" title="Afspeelsnelheid voor zoektreffers (' +
      escapeAttr(formatRate(current)) +
      ')">' +
      escapeHtml(formatRate(current)) +
      "</button>" +
      '<span class="catalogus-zoek-rate-panel" hidden role="dialog" aria-label="Afspeelsnelheid zoektreffers">' +
      "<p>Snelheid voor beluisteren bij zoektreffers. Geldt voor deze browsersessie tot je de site (of dit tabblad) sluit.</p>" +
      '<div class="catalogus-zoek-rate-options">' +
      opts +
      "</div>" +
      "</span></span>"
    );
  }

  function strip(s) {
    return String(s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\w\s]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalize(s) {
    const base = strip(s);
    if (!base) return "";
    return base
      .split(" ")
      .filter(Boolean)
      .map(function (token) {
        return synonyms[token] || token;
      })
      .join(" ");
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
    const words = qNorm.split(" ").filter(Boolean);
    let hit = 0;
    for (const w of words) {
      if ((entry.text || "").includes(w) || title.includes(w)) hit += 1;
    }
    if (words.length) s += (hit / words.length) * 15;
    return s;
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

  function resolveUrl(root, url) {
    if (!url) return "#";
    if (/^(https?:|mailto:|tel:|#)/i.test(url)) return url;
    const base = root.getAttribute("data-base") || "/";
    const path = String(url).replace(/^\//, "");
    const baseNorm = base.endsWith("/") ? base : base + "/";
    return baseNorm + path;
  }

  function biebShortcode(id) {
    return "{{< bieb id=\"" + id + "\" >}}";
  }

  const STATUS_MEANINGS = {
    voorzien:
      "Nog gepland: er is nog geen oefenbare uitgave van dit stuk op de site.",
    concept:
      "Eerste versie: er kunnen nog duidelijke fouten in zitten. Beheerders werken het stuk verder uit.",
    reviewable:
      "Er staat oefenmateriaal; het zou goed moeten zijn. Opmerkingen en correcties zijn welkom.",
    productie:
      "Bewust als oefenmateriaal vrijgegeven. Meld fouten alsnog als je ze tegenkomt.",
  };

  function closeAllTips(root) {
    root.querySelectorAll(".catalogus-zoek-tip.is-open").forEach(function (tip) {
      tip.classList.remove("is-open");
      const btn = tip.querySelector(".catalogus-zoek-tip-trigger");
      const panel = tip.querySelector(".catalogus-zoek-tip-panel");
      if (btn) btn.setAttribute("aria-expanded", "false");
      if (panel) panel.hidden = true;
    });
  }

  function feedbackSnippet(root, entry) {
    const email = root.getAttribute("data-feedback-email") || "";
    const github = root.getAttribute("data-github") || "";
    const pageUrl = entry && entry.url ? resolveUrl(root, entry.url) : "";
    const pageTitle = entry && entry.title ? entry.title : "Catalogus";
    const parts = [];
    if (email && pageUrl) {
      const subject = encodeURIComponent(
        "Oefenhoek: " + pageTitle + " (" + (entry.status || "") + ")"
      );
      const body = encodeURIComponent(
        "Pagina: " + pageTitle + "\nAdres: " + pageUrl + "\n\nUw opmerking:\n"
      );
      parts.push(
        '<a href="mailto:' +
          escapeAttr(email) +
          "?subject=" +
          subject +
          "&body=" +
          body +
          '">e-mail</a>'
      );
    }
    if (github && pageUrl) {
      const issueTitle = encodeURIComponent("Oefenhoek: " + pageTitle);
      const issueBody = encodeURIComponent(
        "Pagina: " + pageTitle + "\nAdres: " + pageUrl + "\n\nOpmerking:\n"
      );
      const issueHref =
        github.replace(/\/$/, "") +
        "/issues/new?title=" +
        issueTitle +
        "&body=" +
        issueBody;
      parts.push(
        '<a href="' + escapeAttr(issueHref) + '">GitHub-issue</a>'
      );
    }
    if (!parts.length) return "";
    return (
      "<p>Feedback over dit stuk: " +
      parts.join(" · ") +
      ".</p>"
    );
  }

  function statusHelpHtml(root, statusRaw, entry) {
    const key = String(statusRaw || "").toLowerCase();
    const meaning =
      STATUS_MEANINGS[key] ||
      "De publicatiestatus zegt koorleden wat ze van deze pagina mogen verwachten.";
    const statusHelpUrl = resolveUrl(
      root,
      "handleiding/publiceren/2-status-en-check/"
    );
    let extra = "";
    if (key === "concept") {
      extra =
        "<p>Als koorlid: oefen vooral niet als enige bron zonder check; wel fouten doorgeven helpt. " +
        "Als beheerder: na controle en inhoudelijke afronding zet je de status op " +
        "<code>reviewable</code> (zie handleiding).</p>";
    } else if (key === "reviewable" || key === "productie") {
      extra =
        "<p>Typo, tekst of muziek niet kloppend? Geef het door — ook bij " +
        "<code>productie</code>.</p>";
    } else if (key === "voorzien") {
      extra =
        "<p>Er is nog weinig te oefenen; status wijzigt wanneer er materiaal klaarstaat.</p>";
    }
    return (
      '<span class="catalogus-zoek-tip catalogus-zoek-tip--status">' +
      '<button type="button" class="catalogus-zoek-tip-trigger" aria-expanded="false" aria-label="Uitleg over publicatiestatus ' +
      escapeAttr(key || statusRaw) +
      '">?</button>' +
      '<span class="catalogus-zoek-tip-panel" hidden role="tooltip">' +
      "<p><strong>" +
      escapeHtml(statusRaw) +
      ":</strong> " +
      escapeHtml(meaning) +
      "</p>" +
      extra +
      feedbackSnippet(root, entry) +
      '<p><a href="' +
      escapeAttr(statusHelpUrl) +
      '">Meer in de handleiding (status en check)</a></p>' +
      "</span></span>"
    );
  }

  function idHelpHtml(root) {
    const bladerUrl = resolveUrl(root, "handleiding/publiceren/1-bladermap/");
    const koormapUrl = resolveUrl(
      root,
      "handleiding/start/catalogus-en-koormappen/"
    );
    return (
      '<span class="catalogus-zoek-tip catalogus-zoek-tip--id">' +
      '<button type="button" class="catalogus-zoek-tip-trigger" aria-expanded="false" aria-label="Uitleg: id kopiëren voor koormap">?</button>' +
      '<span class="catalogus-zoek-tip-panel" hidden role="tooltip">' +
      "<p>Klik op het id links van dit vraagteken. Dan kopieer je een korte Hugo-regel naar het klembord, " +
      "bijvoorbeeld " +
      "<code>" +
      escapeHtml(biebShortcode("zangstuk/variant/uitvoeringsvorm")) +
      "</code>.</p>" +
      "<p>Plak die regel in het Markdown-bestand van een koormap of liturgie-overzicht. " +
      "De site toont daar automatisch oefen- en downloadknoppen voor dat stuk.</p>" +
      '<p><a href="' +
      escapeAttr(bladerUrl) +
      '">Bladermap en koormap</a> · ' +
      '<a href="' +
      escapeAttr(koormapUrl) +
      '">Catalogus en koormappen</a></p>' +
      "</span></span>"
    );
  }

  function stopAudio() {
    player.pause();
    try {
      player.removeAttribute("src");
      player.load();
    } catch (e) {
      /* ignore */
    }
    if (playingBtn) {
      playingBtn.classList.remove("is-playing");
      playingBtn.setAttribute("aria-pressed", "false");
      playingBtn.setAttribute("aria-label", "Beluisteren");
      playingBtn = null;
    }
  }

  function setPlayingButton(btn, playing) {
    if (playingBtn && playingBtn !== btn) {
      playingBtn.classList.remove("is-playing");
      playingBtn.setAttribute("aria-pressed", "false");
      playingBtn.setAttribute("aria-label", "Beluisteren");
    }
    playingBtn = playing ? btn : null;
    if (btn) {
      btn.classList.toggle("is-playing", !!playing);
      btn.setAttribute("aria-pressed", playing ? "true" : "false");
      btn.setAttribute("aria-label", playing ? "Stoppen" : "Beluisteren");
    }
  }

  function playAudio(root, btn, audioPath) {
    if (!audioPath) return;
    const src = resolveUrl(root, audioPath);
    let abs;
    try {
      abs = new URL(src, window.location.href).href;
    } catch (e) {
      return;
    }

    const same =
      playingBtn === btn &&
      (player.src === abs || player.currentSrc === abs);

    if (same) {
      if (player.paused) {
        applyPlaybackRate();
        player.play().catch(function () {
          stopAudio();
        });
        setPlayingButton(btn, true);
      } else {
        stopAudio();
      }
      return;
    }

    stopAudio();
    player.src = src;
    applyPlaybackRate();
    setPlayingButton(btn, true);
    player.play().catch(function () {
      stopAudio();
    });
  }

  player.addEventListener("ended", function () {
    stopAudio();
  });

  function copyText(text, feedbackEl) {
    function ok() {
      if (!feedbackEl) return;
      feedbackEl.classList.add("is-copied");
      feedbackEl.setAttribute("data-copy-label", "gekopieerd");
      window.setTimeout(function () {
        feedbackEl.classList.remove("is-copied");
        feedbackEl.removeAttribute("data-copy-label");
      }, 1200);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok).catch(function () {
        fallbackCopy(text, ok);
      });
    } else {
      fallbackCopy(text, ok);
    }
  }

  function fallbackCopy(text, ok) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
      ok();
    } catch (e) {
      /* ignore */
    }
    document.body.removeChild(ta);
  }

  function render(root, out, meta, rows, q) {
    closeAllTips(root);
    if (!q) {
      out.innerHTML =
        '<p class="catalogus-zoek-leeg">Typ een titel, id of stukje tekst.</p>';
      if (meta) meta.textContent = "";
      return;
    }
    if (!rows.length) {
      out.innerHTML = '<p class="catalogus-zoek-leeg">Geen treffers.</p>';
      if (meta) meta.textContent = "";
      return;
    }
    if (meta) meta.textContent = rows.length + " treffer(s)";
    const html = ['<ul class="catalogus-zoek-lijst">'];
    for (const row of rows.slice(0, 40)) {
      const e = row.entry;
      const status = e.status
        ? ' <span class="catalogus-zoek-status-line">' +
          '<span class="catalogus-zoek-status">' +
          escapeHtml(e.status) +
          "</span>" +
          statusHelpHtml(root, e.status, e) +
          "</span>"
        : "";
      const incipit = e.incipit
        ? '<div class="catalogus-zoek-incipit">' +
          escapeHtml(e.incipit) +
          "</div>"
        : "";
      const audio = e.audio
        ? '<span class="catalogus-zoek-play-wrap">' +
          '<button type="button" class="catalogus-zoek-play" data-audio="' +
          escapeAttr(e.audio) +
          '" aria-label="Beluisteren" aria-pressed="false" title="Beluisteren">▶</button>' +
          rateControlHtml() +
          "</span>"
        : '<span class="catalogus-zoek-play catalogus-zoek-play--empty" aria-hidden="true"></span>';
      html.push(
        "<li>" +
          '<a class="catalogus-zoek-title" href="' +
          escapeAttr(resolveUrl(root, e.url)) +
          '"><strong>' +
          escapeHtml(e.title) +
          "</strong></a>" +
          status +
          '<div class="catalogus-zoek-id-rij">' +
          audio +
          '<button type="button" class="catalogus-zoek-id" data-id="' +
          escapeAttr(e.id) +
          '" title="Kopieer bieb-shortcode">' +
          "<code>" +
          escapeHtml(e.id) +
          "</code>" +
          "</button>" +
          idHelpHtml(root) +
          "</div>" +
          incipit +
          "</li>"
      );
    }
    html.push("</ul>");
    out.innerHTML = html.join("");
    syncRateUi(out);
  }

  function runRoot(root) {
    const input = root.querySelector(".catalogus-zoek-input, input[type='search']");
    const out = root.querySelector(".catalogus-zoek-resultaten");
    const meta = root.querySelector(".catalogus-zoek-meta");
    if (!input || !out) return;

    const q = input.value.trim();
    stopAudio();
    const qNorm = normalize(q);
    const qTokens = tokenSort(q);
    const scored = [];
    for (const entry of entries) {
      const sc = score(entry, qNorm, qTokens);
      if (sc > 0) scored.push({ entry, sc });
    }
    scored.sort(
      (a, b) => b.sc - a.sc || a.entry.id.localeCompare(b.entry.id)
    );
    render(root, out, meta, scored, q);
  }

  function loadIndex(root) {
    if (indexPromise) return indexPromise;
    const indexUrl = root.getAttribute("data-index") || "/zoek/index.json";
    indexPromise = fetch(indexUrl)
      .then(function (r) {
        if (!r.ok) throw new Error("index niet geladen");
        return r.json();
      })
      .then(function (data) {
        entries = data.entries || [];
        synonyms =
          data.synonyms && typeof data.synonyms === "object"
            ? data.synonyms
            : {};
        return data;
      });
    return indexPromise;
  }

  function closeNavPanel(root) {
    const panel = root.querySelector(".site-zoek-panel");
    const toggle = root.querySelector(".site-zoek-toggle");
    if (!panel) return;
    panel.hidden = true;
    document.body.classList.remove("site-zoek-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
    stopAudio();
  }

  function openNavPanel(root) {
    const panel = root.querySelector(".site-zoek-panel");
    const toggle = root.querySelector(".site-zoek-toggle");
    const input = root.querySelector(".catalogus-zoek-input, input[type='search']");
    if (!panel) return;
    panel.hidden = false;
    document.body.classList.add("site-zoek-open");
    if (toggle) toggle.setAttribute("aria-expanded", "true");
    window.setTimeout(function () {
      if (input) input.focus();
    }, 10);
  }

  function bindRoot(root) {
    const form = root.querySelector(".catalogus-zoek-form");
    const input = root.querySelector(".catalogus-zoek-input, input[type='search']");
    const out = root.querySelector(".catalogus-zoek-resultaten");
    const meta = root.querySelector(".catalogus-zoek-meta");
    if (!form || !input || !out) return;

    const isNav = root.classList.contains("site-zoek");
    const toggle = root.querySelector(".site-zoek-toggle");

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      runRoot(root);
    });
    input.addEventListener("input", function () {
      runRoot(root);
    });

    out.addEventListener("click", function (ev) {
      const rateOpt = ev.target.closest(".catalogus-zoek-rate-option");
      if (rateOpt) {
        ev.preventDefault();
        ev.stopPropagation();
        setRate(rateOpt.getAttribute("data-rate"));
        closeAllRatePanels(root);
        return;
      }
      const rateTrigger = ev.target.closest(".catalogus-zoek-rate-trigger");
      if (rateTrigger) {
        ev.preventDefault();
        ev.stopPropagation();
        const wrap = rateTrigger.closest(".catalogus-zoek-rate");
        const panel = wrap && wrap.querySelector(".catalogus-zoek-rate-panel");
        const open = wrap && !wrap.classList.contains("is-open");
        closeAllTips(root);
        closeAllRatePanels(root);
        if (wrap && open) {
          wrap.classList.add("is-open");
          rateTrigger.setAttribute("aria-expanded", "true");
          if (panel) panel.hidden = false;
        }
        return;
      }
      const tipTrigger = ev.target.closest(".catalogus-zoek-tip-trigger");
      if (tipTrigger) {
        ev.preventDefault();
        ev.stopPropagation();
        const tip = tipTrigger.closest(".catalogus-zoek-tip");
        const panel = tip && tip.querySelector(".catalogus-zoek-tip-panel");
        const open = tip && !tip.classList.contains("is-open");
        closeAllTips(root);
        closeAllRatePanels(root);
        if (tip && open) {
          tip.classList.add("is-open");
          tipTrigger.setAttribute("aria-expanded", "true");
          if (panel) panel.hidden = false;
        }
        return;
      }
      if (ev.target.closest(".catalogus-zoek-tip-panel a")) {
        return;
      }
      const play = ev.target.closest(".catalogus-zoek-play");
      if (play && play.dataset.audio) {
        ev.preventDefault();
        closeAllRatePanels(root);
        playAudio(root, play, play.dataset.audio);
        return;
      }
      const idBtn = ev.target.closest(".catalogus-zoek-id");
      if (idBtn && idBtn.dataset.id) {
        ev.preventDefault();
        copyText(biebShortcode(idBtn.dataset.id), idBtn);
      }
    });

    document.addEventListener("click", function (ev) {
      if (!root.contains(ev.target)) return;
      if (ev.target.closest(".catalogus-zoek-tip")) return;
      if (ev.target.closest(".catalogus-zoek-rate")) return;
      closeAllTips(root);
      closeAllRatePanels(root);
    });

    if (isNav && toggle) {
      toggle.addEventListener("click", function () {
        const panel = root.querySelector(".site-zoek-panel");
        if (!panel) return;
        if (panel.hidden) openNavPanel(root);
        else closeNavPanel(root);
      });
      root.querySelectorAll("[data-site-zoek-close]").forEach(function (el) {
        el.addEventListener("click", function () {
          closeNavPanel(root);
        });
      });
      document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape") {
          closeAllRatePanels(root);
          closeAllTips(root);
          closeNavPanel(root);
        }
      });
    }

    loadIndex(root)
      .then(function (data) {
        if (meta && !input.value.trim()) {
          meta.textContent =
            (data.count || entries.length) + " uitvoeringsvormen in de index";
        }
        if (input.value.trim()) runRoot(root);
      })
      .catch(function () {
        out.innerHTML =
          '<p class="catalogus-zoek-leeg">Zoekindex ontbreekt. Draai <code>python scripts\\build_zoek_index.py</code> (na lyrics-products).</p>';
      });
  }

  roots.forEach(bindRoot);

  window.addEventListener("pagehide", stopAudio);
  window.addEventListener("beforeunload", stopAudio);
})();
