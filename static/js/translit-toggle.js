(function () {
  /* Livereload kan dit script opnieuw injecteren; voorkom dubbele handlers. */
  if (window.__bibliotheekTranslitBound) return;
  window.__bibliotheekTranslitBound = true;

  var STORAGE_KEY = "bibliotheek-translit";

  function readStored() {
    try {
      return window.localStorage.getItem(STORAGE_KEY) === "aan";
    } catch (e) {
      return false;
    }
  }

  function writeStored(aan) {
    try {
      window.localStorage.setItem(STORAGE_KEY, aan ? "aan" : "uit");
    } catch (e) {
      /* private mode / quota — UI blijft werken zonder persist. */
    }
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) el.setAttribute("hidden", "");
    else el.removeAttribute("hidden");
  }

  function pageHasTranslit() {
    return !!document.querySelector("[data-has-translit], [data-translit-view='aan'] .osmd-container");
  }

  function preferOsmgForTranslit() {
    if (!pageHasTranslit()) return;
    var root = document.querySelector("[data-scherm-root]");
    if (!root) return;
    var osmg = root.querySelector('[data-scherm="osmg"]');
    if (!osmg) return;
    root.querySelectorAll("[data-scherm]").forEach(function (panel) {
      var kind = (panel.getAttribute("data-scherm") || "").toLowerCase();
      setHidden(panel, kind !== "osmg");
    });
    if (typeof window.__vsaEnsureOsmd === "function") {
      window.__vsaEnsureOsmd(osmg);
    }
  }

  function applyTranslitViews(aan) {
    var want = aan ? "aan" : "uit";
    document.querySelectorAll("[data-translit-view]").forEach(function (el) {
      var view = el.getAttribute("data-translit-view");
      setHidden(el, view !== want);
    });
    if (aan) {
      preferOsmgForTranslit();
    }
    var osmg = document.querySelector('[data-scherm="osmg"]');
    if (osmg && !osmg.hasAttribute("hidden") && typeof window.__vsaEnsureOsmd === "function") {
      window.__vsaEnsureOsmd(osmg);
    }
  }

  function applyState(aan) {
    var root = document.documentElement;
    root.dataset.translit = aan ? "aan" : "uit";
    root.classList.toggle("translit-aan", aan);
    root.classList.toggle("translit-uit", !aan);

    document.querySelectorAll("[data-translit-switch]").forEach(function (input) {
      input.checked = aan;
      input.setAttribute("aria-checked", aan ? "true" : "false");
      var label = input.closest(".pagina-acties-translit");
      if (!label) return;
      var stateEl = label.querySelector("[data-translit-state]");
      if (stateEl) stateEl.textContent = aan ? "aan" : "uit";
    });

    applyTranslitViews(aan);

    window.dispatchEvent(
      new CustomEvent("bibliotheek:translit", { detail: { aan: aan } })
    );
  }

  function bindSwitches() {
    document.querySelectorAll("[data-translit-switch]").forEach(function (input) {
      if (input.__translitBound) return;
      input.__translitBound = true;
      input.addEventListener("change", function () {
        applyState(!!input.checked);
        writeStored(!!input.checked);
      });
    });
  }

  /* Default = uit; alleen «aan» als localStorage dat zegt. */
  applyState(readStored());
  bindSwitches();

  document.addEventListener("DOMContentLoaded", function () {
    applyState(readStored());
    bindSwitches();
  });
})();
