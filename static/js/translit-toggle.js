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
