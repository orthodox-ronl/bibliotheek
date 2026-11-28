/**
 * Scherm: weergave VSA (.vsa.svg) of partituur (.mvsa.svg / .mscz.svg /
 * from-ir), per muziekstuk, via de knop naast de muzieknoot. Alleen als
 * beide aanwezig zijn. Eerste keuze: data-weergave op [data-scherm-root]
 * (bieb/muziek > blad-index.md > vsa). De keuze van de lezer geldt voor dat
 * ene stuk, zolang de pagina open is.
 * Contract: docs/specs/schermpartituur.md §2.1.
 */
(function () {
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
      return "vsa";
    }
    return "partituur";
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) el.setAttribute("hidden", "");
    else el.removeAttribute("hidden");
  }

  function otherBron(bron) {
    return bron === "vsa" ? "partituur" : "vsa";
  }

  function tagRoot(root) {
    if (!root || root.getAttribute("data-scorebron-tagged")) return;
    root.setAttribute("data-scorebron-tagged", "1");
    var hasVsa = false;
    var hasPartituur = false;
    root.querySelectorAll(".vsa-container").forEach(function (box) {
      var src = "";
      var img = box.querySelector("img.vsa-notation");
      if (img) src = img.getAttribute("src") || "";
      else src = box.getAttribute("data-osmd-src") || "";
      if (!src) return;
      var bron = bronFromSrc(src);
      box.setAttribute("data-scorebron", bron);
      if (bron === "vsa") hasVsa = true;
      if (bron === "partituur") hasPartituur = true;
    });
    if (hasVsa && hasPartituur) {
      root.setAttribute("data-scorebron-dual", "");
    }
  }

  function wanted(root) {
    return (
      root.__weergaveKeuze ||
      (root.getAttribute("data-weergave") === "partituur" ? "partituur" : "vsa")
    );
  }

  function buttonsFor(root) {
    var bundle = root.closest(".score-bundle");
    return bundle ? bundle.querySelector(".score-weergave") : null;
  }

  function applyRoot(root) {
    tagRoot(root);
    var group = buttonsFor(root);
    if (!root.hasAttribute("data-scorebron-dual")) {
      root.removeAttribute("data-scorebron-active");
      setHidden(group, true);
      return;
    }
    var bron = wanted(root);
    root.setAttribute("data-scorebron-active", bron);
    /* Per paneel (translit-stand, OSMG): ontbreekt daar de gekozen
       weergave, dan blijft wat er wel is zichtbaar. */
    root.querySelectorAll("[data-translit-view], [data-scherm='osmg']").forEach(function (panel) {
      var boxes = panel.querySelectorAll(".vsa-container[data-scorebron]");
      var has = false;
      boxes.forEach(function (box) {
        if (box.getAttribute("data-scorebron") === bron) has = true;
      });
      var show = has ? bron : otherBron(bron);
      boxes.forEach(function (box) {
        setHidden(box, box.getAttribute("data-scorebron") !== show);
      });
    });
    if (group) {
      setHidden(group, false);
      group.querySelectorAll("[data-weergave-kies]").forEach(function (btn) {
        btn.setAttribute(
          "aria-pressed",
          btn.getAttribute("data-weergave-kies") === bron ? "true" : "false"
        );
      });
    }
    try {
      document.dispatchEvent(
        new CustomEvent("vsa:scorebron", {
          detail: { root: root, bron: bron },
        })
      );
    } catch (e) {
      /* oudere browsers */
    }
  }

  function applyAll() {
    document.querySelectorAll("[data-scherm-root]").forEach(applyRoot);
    /* Na de weergave: schermstand opnieuw (OSMG alleen bij partituur). */
    if (typeof window.__bibliotheekApplySchermstand === "function") {
      window.__bibliotheekApplySchermstand();
    }
  }

  function onClick(event) {
    var btn = event.target.closest("[data-weergave-kies]");
    if (!btn) return;
    event.preventDefault();
    var bundle = btn.closest(".score-bundle");
    var root = bundle && bundle.querySelector("[data-scherm-root]");
    if (!root) return;
    root.__weergaveKeuze = btn.getAttribute("data-weergave-kies");
    applyRoot(root);
    if (typeof window.__bibliotheekApplySchermstand === "function") {
      window.__bibliotheekApplySchermstand();
    }
  }

  function init() {
    document.addEventListener("click", onClick);
    applyAll();
  }

  window.__bibliotheekApplyScorebron = applyAll;
  window.__bibliotheekScorebronFromSrc = bronFromSrc;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
