(function () {
  function fileNameFromHref(href) {
    if (!href) return "bron.txt";
    try {
      var path = href.split("?")[0].split("#")[0];
      var parts = path.split("/");
      return parts[parts.length - 1] || "bron.txt";
    } catch (e) {
      return "bron.txt";
    }
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) {
      el.setAttribute("hidden", "");
    } else {
      el.removeAttribute("hidden");
    }
  }

  function bronnenMenu(bundle) {
    return bundle.querySelector('[data-score-role="bronnen"]');
  }

  function isMultiBronnen(menu) {
    return !!(menu && menu.querySelector(".score-action-menu-panel"));
  }

  function singleBronnenLink(menu) {
    if (!menu || isMultiBronnen(menu)) return null;
    return menu.querySelector("a.score-bron-show, a.btn");
  }

  function ensureBackItem(menu) {
    if (!menu || !isMultiBronnen(menu)) return;
    var panel = menu.querySelector(".score-action-menu-panel");
    if (!panel || panel.querySelector("[data-bron-back]")) return;
    var li = document.createElement("li");
    li.setAttribute("role", "none");
    li.className = "score-bron-back-item";
    var a = document.createElement("a");
    a.setAttribute("role", "menuitem");
    a.href = "#";
    a.setAttribute("data-bron-back", "");
    a.innerHTML =
      '<span class="score-action-menu-label">Partituur</span>' +
      '<span class="score-action-menu-detail">Terug naar de gerenderde weergave</span>';
    li.appendChild(a);
    var hint = panel.querySelector(".score-action-menu-hint");
    if (hint && hint.parentNode === panel) {
      panel.insertBefore(li, hint.nextSibling);
    } else {
      panel.insertBefore(li, panel.firstChild);
    }
  }

  function removeBackItem(menu) {
    if (!menu) return;
    menu.querySelectorAll(".score-bron-back-item").forEach(function (el) {
      el.remove();
    });
  }

  function setSingleBronnenLabel(bundle, inBronView) {
    var link = singleBronnenLink(bronnenMenu(bundle));
    if (!link) return;
    link.textContent = inBronView ? "Partituur" : "Bronnen";
  }

  function showPartituur(bundle) {
    bundle.classList.remove("is-bron-view");
    delete bundle.dataset.activeBronKey;
    delete bundle.dataset.activeBronHref;
    setHidden(bundle.querySelector(".score-partituur"), false);
    bundle.querySelectorAll(".score-bron-panel").forEach(function (panel) {
      setHidden(panel, true);
    });
    bundle.querySelectorAll(".score-action-menu--bron-mode").forEach(function (el) {
      setHidden(el, true);
    });
    removeBackItem(bronnenMenu(bundle));
    setSingleBronnenLabel(bundle, false);
  }

  function showBron(bundle, key, href) {
    var panel = bundle.querySelector(
      '.score-bron-panel[data-bron-panel="' + CSS.escape(key) + '"]'
    );
    if (!panel) return;

    bundle.classList.add("is-bron-view");
    bundle.dataset.activeBronKey = key;
    bundle.dataset.activeBronHref =
      href || panel.getAttribute("data-bron-href") || "";

    setHidden(bundle.querySelector(".score-partituur"), true);
    bundle.querySelectorAll(".score-bron-panel").forEach(function (other) {
      setHidden(other, other !== panel);
    });
    bundle.querySelectorAll(".score-action-menu--bron-mode").forEach(function (el) {
      setHidden(el, false);
    });

    var dl = bundle.querySelector("[data-bron-download]");
    if (dl) {
      dl.setAttribute("href", bundle.dataset.activeBronHref);
      dl.setAttribute("download", fileNameFromHref(bundle.dataset.activeBronHref));
    }

    var menu = bronnenMenu(bundle);
    ensureBackItem(menu);
    setSingleBronnenLabel(bundle, true);
  }

  function printBron(bundle) {
    var key = bundle.dataset.activeBronKey;
    if (!key) return;
    var panel = bundle.querySelector(
      '.score-bron-panel[data-bron-panel="' + CSS.escape(key) + '"]'
    );
    if (!panel) return;
    var pre = panel.querySelector(".score-bron-text");
    var text = pre ? pre.textContent : "";
    var title = fileNameFromHref(bundle.dataset.activeBronHref);
    var frame = document.createElement("iframe");
    frame.className = "score-bron-print-frame";
    frame.title = "Print-bron";
    document.body.appendChild(frame);
    var doc = frame.contentDocument || frame.contentWindow.document;
    doc.open();
    doc.write(
      "<!DOCTYPE html><html lang=\"nl\"><head><meta charset=\"utf-8\">" +
        "<title></title>" +
        "<style>body{margin:1.5rem;font:12pt/1.4 Consolas,monospace;white-space:pre-wrap;}</style>" +
        "</head><body></body></html>"
    );
    doc.close();
    doc.title = title;
    doc.body.textContent = text;
    setTimeout(function () {
      try {
        frame.contentWindow.focus();
        frame.contentWindow.print();
      } catch (e) {
        /* negeren */
      }
      setTimeout(function () {
        frame.remove();
      }, 2000);
    }, 50);
  }

  document.addEventListener("click", function (event) {
    var back = event.target.closest("[data-bron-back]");
    if (back) {
      var backBundle = back.closest(".score-bundle");
      if (backBundle) {
        event.preventDefault();
        showPartituur(backBundle);
      }
      return;
    }

    var printBtn = event.target.closest("[data-bron-print]");
    if (printBtn) {
      var printBundle = printBtn.closest(".score-bundle");
      if (printBundle) {
        event.preventDefault();
        printBron(printBundle);
      }
      return;
    }

    var link = event.target.closest(".score-bron-show");
    if (!link) return;
    var bundle = link.closest(".score-bundle");
    if (!bundle) return;
    event.preventDefault();

    var key = link.getAttribute("data-bron-key");
    var href = link.getAttribute("data-bron-href") || link.getAttribute("href");
    var already =
      bundle.classList.contains("is-bron-view") &&
      bundle.dataset.activeBronKey === key;

    // Zelfde bron opnieuw (of enige knop die nu "Partituur" heet): terug.
    if (already) {
      showPartituur(bundle);
      return;
    }

    showBron(bundle, key, href);
  });
})();
