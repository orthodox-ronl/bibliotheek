/**
 * Schermstand SVG | OSMG. Default: svg. Sitebreed via localStorage —
 * geldt op catalogus én koormap. De wisselknop staat alleen in {} op
 * catalogus-bladen (label = de ándere stand).
 */
(function () {
  var STORAGE_KEY = "bibliotheek-schermstand";
  var DEFAULT_STAND = "svg";

  function readStand() {
    try {
      var v = (localStorage.getItem(STORAGE_KEY) || "").trim().toLowerCase();
      if (v === "svg" || v === "osmg") return v;
    } catch (e) {
      /* private mode / blocked */
    }
    return DEFAULT_STAND;
  }

  function writeStand(stand) {
    try {
      localStorage.setItem(STORAGE_KEY, stand);
    } catch (e) {
      /* ignore */
    }
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) el.setAttribute("hidden", "");
    else el.removeAttribute("hidden");
  }

  function otherStand(stand) {
    return stand === "osmg" ? "svg" : "osmg";
  }

  function labelFor(stand) {
    return stand === "osmg" ? "OSMG" : "SVG";
  }

  function applyRoot(root, stand) {
    if (!root) return;
    var panels = root.querySelectorAll("[data-scherm]");
    if (!panels.length) return;
    var hasStand = false;
    panels.forEach(function (panel) {
      var kind = (panel.getAttribute("data-scherm") || "").toLowerCase();
      if (kind === stand) hasStand = true;
    });
    var effective = hasStand
      ? stand
      : panels[0].getAttribute("data-scherm") || DEFAULT_STAND;
    panels.forEach(function (panel) {
      var kind = (panel.getAttribute("data-scherm") || "").toLowerCase();
      var show = kind === effective;
      setHidden(panel, !show);
      if (show && kind === "osmg" && typeof window.__vsaEnsureOsmd === "function") {
        window.__vsaEnsureOsmd(panel);
      }
    });
  }

  function applyButtons(stand) {
    var next = otherStand(stand);
    document.querySelectorAll("[data-schermstand-switch]").forEach(function (btn) {
      btn.setAttribute("data-schermstand", next);
      btn.textContent = labelFor(next);
      btn.setAttribute(
        "aria-label",
        "Schermweergave wisselen naar " + labelFor(next)
      );
    });
  }

  function applyAll(stand) {
    document.querySelectorAll("[data-scherm-root]").forEach(function (root) {
      applyRoot(root, stand);
    });
    applyButtons(stand);
  }

  /** Toon stand zonder localStorage te wijzigen (bv. tijdelijk OSMG bij translit). */
  function applyTemporary(stand) {
    if (stand !== "svg" && stand !== "osmg") return;
    applyAll(stand);
  }

  /** Herstel de opgeslagen (of default) schermstand. */
  function applyStored() {
    applyAll(readStand());
  }

  function onClick(event) {
    var btn = event.target.closest("[data-schermstand-switch]");
    if (!btn) return;
    event.preventDefault();
    var stand = (btn.getAttribute("data-schermstand") || "").toLowerCase();
    if (stand !== "svg" && stand !== "osmg") return;
    writeStand(stand);
    applyAll(stand);
    var tip = btn.closest("details.score-bron-tip");
    if (tip) tip.open = false;
  }

  function onTranslit(ev) {
    var aan = !!(ev && ev.detail && ev.detail.aan);
    if (aan) {
      /* Transliteratie zit alleen in OSMG; voorkeur in localStorage blijft staan. */
      applyTemporary("osmg");
    } else {
      applyStored();
    }
  }

  function init() {
    document.addEventListener("click", onClick);
    window.addEventListener("storage", function (ev) {
      if (ev.key !== STORAGE_KEY) return;
      applyStored();
    });
    window.addEventListener("bibliotheek:translit", onTranslit);
    /* Na translit-toggle (laadt eerder): als translit al «aan» is, OSMG tonen. */
    if (document.documentElement.dataset.translit === "aan") {
      applyTemporary("osmg");
    } else {
      applyStored();
    }
  }

  window.__bibliotheekApplySchermstand = applyStored;
  window.__bibliotheekApplySchermstandTemporary = applyTemporary;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
