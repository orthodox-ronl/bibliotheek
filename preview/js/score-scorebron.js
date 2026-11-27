/**
 * Scherm: Notatie (.vsa.svg) ↔ Partituur (.mvsa.svg / from-ir), via {}.
 * Alleen als beide aanwezig zijn op het blad. Keuze sitebreed in
 * localStorage (`bibliotheek-scorebron`). Default: notatie (VSA).
 * Contract: docs/specs/schermpartituur.md §2 (scorebron).
 */
(function () {
  var STORAGE_KEY = "bibliotheek-scorebron";
  var DEFAULT_BRON = "notatie";

  function bronFromSrc(src) {
    var n = String(src || "").toLowerCase();
    if (
      n.indexOf(".vsa.mvsa.") >= 0 ||
      n.indexOf(".mvsa.translit") >= 0 ||
      n.indexOf(".mscz.translit") >= 0 ||
      /\.mvsa\.svg(\?|#|$)/.test(n) ||
      /\.mscz\.svg(\?|#|$)/.test(n) ||
      n.indexOf(".from-ir.musicxml") >= 0
    ) {
      return "partituur";
    }
    if (
      n.indexOf("/vsa/bladermap/") >= 0 ||
      n.indexOf(".vsa.translit") >= 0 ||
      /\.vsa\.svg(\?|#|$)/.test(n)
    ) {
      return "notatie";
    }
    return "partituur";
  }

  function readBron() {
    try {
      var v = (localStorage.getItem(STORAGE_KEY) || "").trim().toLowerCase();
      if (v === "notatie" || v === "partituur") return v;
    } catch (e) {
      /* private mode */
    }
    return DEFAULT_BRON;
  }

  function writeBron(bron) {
    try {
      localStorage.setItem(STORAGE_KEY, bron);
    } catch (e) {
      /* ignore */
    }
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) el.setAttribute("hidden", "");
    else el.removeAttribute("hidden");
  }

  function otherBron(bron) {
    return bron === "notatie" ? "partituur" : "notatie";
  }

  function labelFor(bron) {
    return bron === "notatie" ? "Notatie" : "Partituur";
  }

  function tagRoot(root) {
    if (!root || root.getAttribute("data-scorebron-tagged")) return;
    root.setAttribute("data-scorebron-tagged", "1");
    var hasNotatie = false;
    var hasPartituur = false;
    root.querySelectorAll(".vsa-container").forEach(function (box) {
      var src = "";
      var img = box.querySelector("img.vsa-notation");
      if (img) src = img.getAttribute("src") || "";
      else src = box.getAttribute("data-osmd-src") || "";
      if (!src) return;
      var bron = bronFromSrc(src);
      box.setAttribute("data-scorebron", bron);
      if (bron === "notatie") hasNotatie = true;
      if (bron === "partituur") hasPartituur = true;
    });
    if (hasNotatie && hasPartituur) {
      root.setAttribute("data-scorebron-dual", "");
    }
  }

  function applyRoot(root, bron) {
    tagRoot(root);
    if (!root.hasAttribute("data-scorebron-dual")) {
      root.removeAttribute("data-scorebron-active");
      return;
    }
    var hasBron = false;
    root.querySelectorAll(".vsa-container[data-scorebron]").forEach(function (box) {
      if ((box.getAttribute("data-scorebron") || "") === bron) hasBron = true;
    });
    var effective = hasBron ? bron : otherBron(bron);
    root.setAttribute("data-scorebron-active", effective);
    root.querySelectorAll(".vsa-container[data-scorebron]").forEach(function (box) {
      var b = box.getAttribute("data-scorebron") || "";
      setHidden(box, b !== effective);
    });
    try {
      document.dispatchEvent(
        new CustomEvent("vsa:scorebron", {
          detail: { root: root, bron: effective },
        })
      );
    } catch (e) {
      /* oudere browsers */
    }
  }

  function applyButtons(bron) {
    var next = otherBron(bron);
    document.querySelectorAll("[data-scorebron-switch]").forEach(function (btn) {
      var root = btn.closest(".score-bundle");
      var dual = root && root.querySelector("[data-scorebron-dual]");
      setHidden(btn.closest(".score-action-menu") || btn, !dual);
      btn.setAttribute("data-scorebron", next);
      btn.textContent = labelFor(next);
      btn.setAttribute(
        "aria-label",
        "Scherm wisselen naar " + labelFor(next)
      );
    });
  }

  function applyAll(bron) {
    document.querySelectorAll("[data-scherm-root]").forEach(function (root) {
      applyRoot(root, bron);
    });
    applyButtons(bron);
    /* Na scorebron: schermstand opnieuw (OSMG alleen bij partituur). */
    if (typeof window.__bibliotheekApplySchermstand === "function") {
      window.__bibliotheekApplySchermstand();
    }
  }

  function applyStored() {
    applyAll(readBron());
  }

  function onClick(event) {
    var btn = event.target.closest("[data-scorebron-switch]");
    if (!btn) return;
    event.preventDefault();
    var bron = (btn.getAttribute("data-scorebron") || "").toLowerCase();
    if (bron !== "notatie" && bron !== "partituur") return;
    writeBron(bron);
    applyAll(bron);
    var tip = btn.closest("details.score-bron-tip");
    if (tip) tip.open = false;
  }

  function init() {
    document.addEventListener("click", onClick);
    window.addEventListener("storage", function (ev) {
      if (ev.key !== STORAGE_KEY) return;
      applyStored();
    });
    applyStored();
  }

  window.__bibliotheekApplyScorebron = applyStored;
  window.__bibliotheekScorebronFromSrc = bronFromSrc;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
