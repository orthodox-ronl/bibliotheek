(function () {
  /* Livereload kan dit script opnieuw injecteren; voorkom dubbele click-handlers
     (anders opent ♪ en sluit meteen weer). */
  if (window.__bibliotheekSiteNavBound) return;
  window.__bibliotheekSiteNavBound = true;

  function syncChromeHeight() {
    var chrome = document.querySelector(".site-chrome");
    var oefHeader = document.querySelector(".oefenhoek-header");
    var chromeHeight = chrome ? chrome.offsetHeight : 0;
    var oefHeight = oefHeader ? oefHeader.offsetHeight : 0;
    document.documentElement.style.setProperty(
      "--site-chrome-height",
      chromeHeight + "px"
    );
    document.documentElement.style.setProperty(
      "--oefenhoek-header-height",
      oefHeight + "px"
    );
  }

  syncChromeHeight();
  window.addEventListener("resize", syncChromeHeight);
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(syncChromeHeight).catch(function () {});
  }

  var groups = document.querySelectorAll(".site-nav-group");

  groups.forEach(function (group) {
    group.addEventListener("toggle", function () {
      if (!group.open) return;
      groups.forEach(function (other) {
        if (other !== group) other.open = false;
      });
      syncChromeHeight();
      if (group.open) {
        requestAnimationFrame(function () {
          placePopoverInViewport(group.querySelector(".site-nav-menu"), group);
        });
      }
    });
  });

  document.addEventListener("click", function (event) {
    groups.forEach(function (group) {
      if (group.open && !group.contains(event.target)) {
        group.open = false;
        clearPopoverShift(group.querySelector(".site-nav-menu"));
      }
    });
    document.querySelectorAll("details.publicatiestatus-tip[open]").forEach(function (tip) {
      if (!tip.contains(event.target)) tip.open = false;
    });
    document.querySelectorAll("details.score-oefen-tip[open], details.score-bron-tip[open]").forEach(function (tip) {
      if (!tip.contains(event.target)) tip.open = false;
    });
    syncChromeHeight();
  });

  var MARGIN = 8;
  /* Kleine overlap i.p.v. gat: anders verliest :hover de tip bij fixed-plaatsing. */
  var GAP = 2;

  function clearPopoverShift(panel) {
    if (!panel) return;
    panel.style.transform = "";
    panel.style.position = "";
    panel.style.left = "";
    panel.style.right = "";
    panel.style.top = "";
    panel.style.bottom = "";
    panel.style.width = "";
    panel.style.maxWidth = "";
    panel.style.minWidth = "";
    panel.classList.remove("is-popover-placed");
  }

  function findPopoverAnchor(panel) {
    if (!panel) return null;
    var wrap = panel.closest(
      ".site-chrome-tip, .catalogus-zoek-tip, .catalogus-zoek-rate, .publicatiestatus-tip, .score-oefen-tip, .score-bron-tip, .score-action-menu, .site-nav-group"
    );
    if (!wrap) return panel.parentElement;
    if (wrap.matches(".site-nav-group")) {
      return wrap.querySelector("summary") || wrap;
    }
    if (wrap.matches(".publicatiestatus-tip, .score-oefen-tip, .score-bron-tip")) {
      return wrap.querySelector("summary") || wrap;
    }
    if (wrap.matches(".catalogus-zoek-tip, .catalogus-zoek-rate")) {
      return (
        wrap.querySelector(
          ".catalogus-zoek-tip-trigger, .catalogus-zoek-rate-trigger"
        ) || wrap
      );
    }
    if (wrap.matches(".score-action-menu")) {
      return (
        wrap.querySelector(
          ":scope > .score-action-menu-trigger, :scope > .btn, :scope > a.btn, :scope > button"
        ) || wrap
      );
    }
    /* site-chrome-tip: knop / label / zoek-toggle */
    return (
      wrap.querySelector(
        ":scope > a, :scope > button, :scope > label, :scope > .site-zoek-toggle, :scope > summary"
      ) || wrap
    );
  }

  function prefersEndAlign(panel) {
    if (!panel) return false;
    if (panel.classList.contains("site-chrome-tip-panel--end")) return true;
    if (panel.closest(".catalogus-zoek-tip--id, .catalogus-zoek-tip--help")) {
      return true;
    }
    if (panel.classList.contains("publicatiestatus-tip-panel")) return true;
    if (panel.classList.contains("score-bron-tip-panel")) return true;
    var cs = panel.getAttribute("data-popover-align");
    return cs === "end";
  }

  function prefersAbove(panel) {
    if (!panel) return false;
    if (panel.classList.contains("score-action-help")) return true;
    if (panel.classList.contains("catalogus-zoek-rate-panel")) return true;
    if (panel.closest(".catalogus-zoek-tip--id")) return true;
    return false;
  }

  function prefersBeside(panel) {
    return !!(
      panel &&
      (panel.classList.contains("score-oefen-tip-panel") ||
        panel.classList.contains("score-bron-tip-panel"))
    );
  }

  /**
   * Zet tip-/menu-panelen met position:fixed in het venster.
   * Ontsnapt overflow op html/body/header; voorkomt afknippen rechts/links.
   */
  function placePopoverInViewport(panel, anchor) {
    if (!panel) return;
    clearPopoverShift(panel);

    var hadHidden = panel.hasAttribute("hidden");
    if (hadHidden) panel.hidden = false;

    var prevDisplay = panel.style.display;
    var cs = getComputedStyle(panel);
    var forcedDisplay = false;
    if (cs.display === "none") {
      panel.style.setProperty("display", "block", "important");
      forcedDisplay = true;
    }

    var anchorEl = anchor || findPopoverAnchor(panel);
    if (!anchorEl) {
      if (forcedDisplay) panel.style.display = prevDisplay;
      if (hadHidden) panel.hidden = true;
      return;
    }

    var a = anchorEl.getBoundingClientRect();
    var vw = window.innerWidth;
    var vh = window.innerHeight;
    var maxW = Math.max(120, vw - MARGIN * 2);

    panel.classList.add("is-popover-placed");
    panel.style.position = "fixed";
    panel.style.right = "auto";
    panel.style.bottom = "auto";
    panel.style.left = "0px";
    panel.style.top = "0px";
    panel.style.maxWidth = maxW + "px";
    var pw = Math.min(panel.offsetWidth || 0, maxW);
    if (pw > 0) panel.style.width = Math.round(pw) + "px";
    var ph = panel.offsetHeight || 0;
    if (!(pw > 0) || !(ph > 0)) {
      clearPopoverShift(panel);
      if (forcedDisplay) panel.style.display = prevDisplay;
      if (hadHidden) panel.hidden = true;
      return;
    }

    var left;
    var top;
    var beside = prefersBeside(panel);
    var end = prefersEndAlign(panel);

    if (beside) {
      /* ♪ rechts van knop, {} links — val terug naar onder bij te weinig ruimte. */
      var sideLeft = end ? a.left - GAP - pw : a.right + GAP;
      var sideOk =
        sideLeft >= MARGIN && sideLeft + pw <= vw - MARGIN;
      if (sideOk) {
        left = sideLeft;
        top = a.top;
        if (top + ph > vh - MARGIN) {
          top = Math.max(MARGIN, vh - MARGIN - ph);
        }
        if (top < MARGIN) top = MARGIN;
      } else {
        beside = false;
      }
    }

    if (!beside) {
      left = end ? a.right - pw : a.left;
      if (left + pw > vw - MARGIN) left = vw - MARGIN - pw;
      if (left < MARGIN) left = MARGIN;

      var above = prefersAbove(panel);
      if (above) {
        top = a.top - GAP - ph;
        if (top < MARGIN) top = a.bottom + GAP;
      } else {
        top = a.bottom + GAP;
        if (top + ph > vh - MARGIN) {
          var up = a.top - GAP - ph;
          if (up >= MARGIN) top = up;
          else top = Math.max(MARGIN, vh - MARGIN - ph);
        }
      }
      if (top + ph > vh - MARGIN) {
        top = Math.max(MARGIN, vh - MARGIN - ph);
      }
      if (top < MARGIN) top = MARGIN;
    }

    panel.style.left = Math.round(left) + "px";
    panel.style.top = Math.round(top) + "px";

    if (forcedDisplay) {
      /* Laat CSS (:hover / .is-open) de zichtbaarheid bepalen; fixed-coords blijven. */
      panel.style.removeProperty("display");
    }
  }

  window.bibliotheekPlacePopover = placePopoverInViewport;
  window.bibliotheekClearPopover = clearPopoverShift;

  function placeScoreActionHelp(menu) {
    var help = menu.querySelector(":scope > .score-action-help");
    if (!help) return;
    help.classList.remove("score-action-help--below");
    help.style.top = "";
    placePopoverInViewport(help, menu);
  }

  function placeScoreActionMenuPanel(menu) {
    var panel = menu.querySelector(":scope > .score-action-menu-panel");
    if (!panel) return;
    var style = getComputedStyle(panel);
    if (style.display === "none") return;
    placePopoverInViewport(panel, menu);
  }

  document.querySelectorAll(".score-action-menu").forEach(function (menu) {
    menu.addEventListener("mouseenter", function () {
      if (menu.querySelector(":scope > .score-action-help")) {
        placeScoreActionHelp(menu);
      }
      placeScoreActionMenuPanel(menu);
    });
    menu.addEventListener("focusin", function () {
      if (menu.querySelector(":scope > .score-action-help")) {
        placeScoreActionHelp(menu);
      }
      placeScoreActionMenuPanel(menu);
    });
    menu.addEventListener("mouseleave", function () {
      clearPopoverShift(menu.querySelector(":scope > .score-action-help"));
      clearPopoverShift(menu.querySelector(":scope > .score-action-menu-panel"));
    });
  });

  function placeScoreTipPanel(tip) {
    var panel = tip.querySelector(".score-oefen-tip-panel, .score-bron-tip-panel");
    if (!panel) return;
    placePopoverInViewport(panel, tip);
  }

  function bindScoreTipPlacement(tip) {
    tip.addEventListener("toggle", function () {
      if (!tip.open) {
        clearPopoverShift(
          tip.querySelector(".score-oefen-tip-panel, .score-bron-tip-panel")
        );
        return;
      }
      requestAnimationFrame(function () {
        placeScoreTipPanel(tip);
      });
    });
  }

  document
    .querySelectorAll("details.score-oefen-tip, details.score-bron-tip")
    .forEach(bindScoreTipPlacement);

  /* Hover-labels naast ♪/{}: spiegelen als ze van het scherm af lopen. */
  document
    .querySelectorAll(".score-oefen-tip-trigger, .score-bron-tip-trigger")
    .forEach(function (trigger) {
      trigger.addEventListener("mouseenter", function () {
        trigger.classList.remove("score-tip-label--flip");
        requestAnimationFrame(function () {
          var tip = trigger.closest(".score-oefen-tip, .score-bron-tip");
          var isBron = tip && tip.classList.contains("score-bron-tip");
          var rect = trigger.getBoundingClientRect();
          /* Pseudo-label ~ max 14rem; als te weinig ruimte: flip. */
          var need = Math.min(14 * 16, window.innerWidth * 0.7) + 12;
          if (isBron) {
            if (rect.left < need) trigger.classList.add("score-tip-label--flip");
          } else if (rect.right + need > window.innerWidth - MARGIN) {
            trigger.classList.add("score-tip-label--flip");
          }
        });
      });
      trigger.addEventListener("mouseleave", function () {
        trigger.classList.remove("score-tip-label--flip");
      });
    });

  document.querySelectorAll("details.publicatiestatus-tip").forEach(function (tip) {
    tip.addEventListener("toggle", function () {
      var panel = tip.querySelector(".publicatiestatus-tip-panel");
      if (!tip.open) {
        clearPopoverShift(panel);
        return;
      }
      requestAnimationFrame(function () {
        placePopoverInViewport(panel, tip);
      });
    });
  });

  function bindChromeTipPlacement(tip) {
    var panel = tip.querySelector(":scope > .site-chrome-tip-panel");
    if (!panel) return;
    function place() {
      requestAnimationFrame(function () {
        placePopoverInViewport(panel, tip);
      });
    }
    tip.addEventListener("mouseenter", place);
    tip.addEventListener("focusin", place);
    tip.addEventListener("mouseleave", function () {
      clearPopoverShift(panel);
    });
  }

  document.querySelectorAll(".site-chrome-tip").forEach(bindChromeTipPlacement);

  function placeOpenPopovers() {
    document
      .querySelectorAll(
        "details.score-oefen-tip[open], details.score-bron-tip[open]"
      )
      .forEach(placeScoreTipPanel);
    document
      .querySelectorAll(
        "details.publicatiestatus-tip[open] .publicatiestatus-tip-panel"
      )
      .forEach(function (panel) {
        placePopoverInViewport(panel);
      });
    document.querySelectorAll("details.site-nav-group[open]").forEach(function (group) {
      placePopoverInViewport(group.querySelector(".site-nav-menu"), group);
    });
    document.querySelectorAll(".catalogus-zoek-tip.is-open .catalogus-zoek-tip-panel").forEach(function (panel) {
      placePopoverInViewport(panel);
    });
    document.querySelectorAll(".catalogus-zoek-rate.is-open .catalogus-zoek-rate-panel").forEach(function (panel) {
      placePopoverInViewport(panel);
    });
  }

  window.addEventListener("resize", placeOpenPopovers);
  window.addEventListener(
    "scroll",
    function () {
      placeOpenPopovers();
    },
    true
  );

})();
