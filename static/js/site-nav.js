(function () {
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
    syncChromeHeight();
  });

  function placeScoreActionHelp(menu) {
    var help = menu.querySelector(":scope > .score-action-help");
    if (!help) return;
    help.classList.remove("score-action-help--below");
    help.style.top = "";
    // Standaard boven de knop; z-index 110 legt over sticky chrome heen.
    // Alleen omklappen als de popover nog buiten het venster valt.
    var rect = help.getBoundingClientRect();
    if (!(rect.height > 0) || rect.top >= 4) return;
    help.classList.add("score-action-help--below");
    var panel = menu.querySelector(".score-action-menu-panel");
    if (!panel) return;
    var panelStyle = getComputedStyle(panel);
    if (panelStyle.display === "none") return;
    // Keuzelijst zit ook onder de knop: zet uitleg eronder, niet eroverheen.
    var menuRect = menu.getBoundingClientRect();
    var panelRect = panel.getBoundingClientRect();
    help.style.top = panelRect.bottom - menuRect.top + 6 + "px";
  }

  document.querySelectorAll(".score-action-menu").forEach(function (menu) {
    if (!menu.querySelector(":scope > .score-action-help")) return;
    menu.addEventListener("mouseenter", function () {
      placeScoreActionHelp(menu);
    });
    menu.addEventListener("focusin", function () {
      placeScoreActionHelp(menu);
    });
  });

  document.querySelectorAll("[data-pagina-print]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      window.print();
    });
  });
})();
