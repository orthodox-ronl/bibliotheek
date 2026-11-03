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
      // Open dropdown kan de chrome hoger maken.
      syncChromeHeight();
    });
  });

  document.addEventListener("click", function (event) {
    groups.forEach(function (group) {
      if (group.open && !group.contains(event.target)) group.open = false;
    });
    document.querySelectorAll("details.publicatiestatus-tip[open]").forEach(function (tip) {
      if (!tip.contains(event.target)) tip.open = false;
    });
    document.querySelectorAll("details.score-oefen-tip[open], details.score-bron-tip[open]").forEach(function (tip) {
      if (!tip.contains(event.target)) tip.open = false;
    });
    syncChromeHeight();
  });

  /* Houd absolute tip-/help-panelen binnen het venster (links/rechts/onder/boven). */
  function clearPopoverShift(panel) {
    if (!panel) return;
    panel.style.transform = "";
  }

  function placePopoverInViewport(panel) {
    if (!panel) return;
    clearPopoverShift(panel);
    var rect = panel.getBoundingClientRect();
    if (!(rect.width > 0) || !(rect.height > 0)) return;
    var margin = 8;
    var dx = 0;
    var dy = 0;
    if (rect.right > window.innerWidth - margin) {
      dx -= rect.right - (window.innerWidth - margin);
    }
    if (rect.left + dx < margin) {
      dx += margin - (rect.left + dx);
    }
    if (rect.bottom > window.innerHeight - margin) {
      dy -= rect.bottom - (window.innerHeight - margin);
    }
    if (rect.top + dy < margin) {
      dy += margin - (rect.top + dy);
    }
    if (dx || dy) {
      panel.style.transform = "translate(" + dx + "px, " + dy + "px)";
    }
  }

  window.bibliotheekPlacePopover = placePopoverInViewport;
  window.bibliotheekClearPopover = clearPopoverShift;

  function placeScoreActionHelp(menu) {
    var help = menu.querySelector(":scope > .score-action-help");
    if (!help) return;
    help.classList.remove("score-action-help--below");
    help.style.top = "";
    clearPopoverShift(help);
    // Standaard boven de knop; z-index 110 legt over sticky chrome heen.
    // Alleen omklappen als de popover nog buiten het venster valt.
    var rect = help.getBoundingClientRect();
    if (!(rect.height > 0) || rect.top >= 4) {
      placePopoverInViewport(help);
      return;
    }
    help.classList.add("score-action-help--below");
    var panel = menu.querySelector(".score-action-menu-panel");
    if (!panel) {
      placePopoverInViewport(help);
      return;
    }
    var panelStyle = getComputedStyle(panel);
    if (panelStyle.display === "none") {
      placePopoverInViewport(help);
      return;
    }
    // Keuzelijst zit ook onder de knop: zet uitleg eronder, niet eroverheen.
    var menuRect = menu.getBoundingClientRect();
    var panelRect = panel.getBoundingClientRect();
    help.style.top = panelRect.bottom - menuRect.top + 6 + "px";
    placePopoverInViewport(help);
  }

  function placeScoreActionMenuPanel(menu) {
    var panel = menu.querySelector(":scope > .score-action-menu-panel");
    if (!panel) return;
    var style = getComputedStyle(panel);
    if (style.display === "none") return;
    placePopoverInViewport(panel);
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
  });

  /* ♪/{}-klikpanelen: naast het icoon; verticaal gelijk aan knop, zo nodig omhoog. */
  function placeScoreTipPanel(tip) {
    var panel = tip.querySelector(".score-oefen-tip-panel, .score-bron-tip-panel");
    if (!panel) return;
    clearPopoverShift(panel);
    panel.style.top = "0px";
    var rect = panel.getBoundingClientRect();
    if (!(rect.height > 0)) return;
    var margin = 8;
    var shift = 0;
    if (rect.bottom > window.innerHeight - margin) {
      shift -= rect.bottom - (window.innerHeight - margin);
    }
    if (rect.top + shift < margin) {
      shift += margin - (rect.top + shift);
    }
    if (shift !== 0) {
      panel.style.top = shift + "px";
    }
    placePopoverInViewport(panel);
  }

  function bindScoreTipPlacement(tip) {
    tip.addEventListener("toggle", function () {
      if (!tip.open) {
        var panel = tip.querySelector(
          ".score-oefen-tip-panel, .score-bron-tip-panel"
        );
        if (panel) {
          panel.style.top = "";
          clearPopoverShift(panel);
        }
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

  document.querySelectorAll("details.publicatiestatus-tip").forEach(function (tip) {
    tip.addEventListener("toggle", function () {
      var panel = tip.querySelector(".publicatiestatus-tip-panel");
      if (!tip.open) {
        clearPopoverShift(panel);
        return;
      }
      requestAnimationFrame(function () {
        placePopoverInViewport(panel);
      });
    });
  });

  function bindChromeTipPlacement(tip) {
    var panel = tip.querySelector(":scope > .site-chrome-tip-panel");
    if (!panel) return;
    function place() {
      requestAnimationFrame(function () {
        placePopoverInViewport(panel);
      });
    }
    tip.addEventListener("mouseenter", place);
    tip.addEventListener("focusin", place);
    tip.addEventListener("mouseleave", function () {
      clearPopoverShift(panel);
    });
  }

  document.querySelectorAll(".site-chrome-tip").forEach(bindChromeTipPlacement);

  function placeOpenScoreMenus() {
    document
      .querySelectorAll(
        "details.score-oefen-tip[open], details.score-bron-tip[open]"
      )
      .forEach(placeScoreTipPanel);
    document
      .querySelectorAll("details.publicatiestatus-tip[open] .publicatiestatus-tip-panel")
      .forEach(placePopoverInViewport);
  }

  window.addEventListener("resize", function () {
    placeOpenScoreMenus();
  });

})();
