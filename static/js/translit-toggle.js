(function () {
  /* Livereload kan dit script opnieuw injecteren; voorkom dubbele handlers. */
  if (window.__bibliotheekTranslitBound) return;
  window.__bibliotheekTranslitBound = true;

  var STORAGE_KEY = "bibliotheek-translit";
  var STORAGE_MODUS = "bibliotheek-translit-modus";
  var DEFAULT_MODUS = "nls";

  function readStoredAan() {
    try {
      return window.localStorage.getItem(STORAGE_KEY) === "aan";
    } catch (e) {
      return false;
    }
  }

  function writeStoredAan(aan) {
    try {
      window.localStorage.setItem(STORAGE_KEY, aan ? "aan" : "uit");
    } catch (e) {
      /* private mode / quota — UI blijft werken zonder persist. */
    }
  }

  function readStoredModus() {
    try {
      var m = (window.localStorage.getItem(STORAGE_MODUS) || "").toLowerCase();
      return m === "ksl" ? "ksl" : DEFAULT_MODUS;
    } catch (e) {
      return DEFAULT_MODUS;
    }
  }

  function writeStoredModus(modus) {
    try {
      window.localStorage.setItem(
        STORAGE_MODUS,
        modus === "ksl" ? "ksl" : DEFAULT_MODUS
      );
    } catch (e) {
      /* private mode / quota */
    }
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) el.setAttribute("hidden", "");
    else el.removeAttribute("hidden");
  }

  function applyTranslitViews(aan, modus) {
    document.querySelectorAll("[data-translit-view]").forEach(function (el) {
      var view = el.getAttribute("data-translit-view");
      if (view === "uit") {
        setHidden(el, aan);
        return;
      }
      if (view === "aan") {
        var forModus = (el.getAttribute("data-translit-for-modus") || "").toLowerCase();
        if (!forModus) forModus = DEFAULT_MODUS;
        setHidden(el, !(aan && forModus === modus));
        return;
      }
      setHidden(el, true);
    });
  }

  function applyPaginaPdfDownload(aan, modus) {
    document.querySelectorAll("[data-pagina-pdf-download]").forEach(function (a) {
      var href = a.getAttribute("data-pdf-uit") || "";
      var name = a.getAttribute("data-pdf-name-uit") || "";
      if (aan && modus === "ksl") {
        href = a.getAttribute("data-pdf-ksl") || href;
        name = a.getAttribute("data-pdf-name-ksl") || name;
      } else if (aan) {
        href = a.getAttribute("data-pdf-nls") || href;
        name = a.getAttribute("data-pdf-name-nls") || name;
      }
      if (href) {
        a.setAttribute("href", href);
        a.removeAttribute("hidden");
      } else {
        a.setAttribute("hidden", "");
      }
      if (name) a.setAttribute("download", name);
      var title = "PDF van deze hele pagina opslaan";
      if (aan && modus === "ksl") {
        title = "PDF met translit Ksl (Cyrillische hulpregel) opslaan";
      } else if (aan) {
        title = "PDF met translit Nls (Latijnse hulpregel) opslaan";
      }
      a.setAttribute("title", title);
    });
  }

  function applyState(aan, modus) {
    modus = modus === "ksl" ? "ksl" : DEFAULT_MODUS;
    var root = document.documentElement;
    root.dataset.translit = aan ? "aan" : "uit";
    root.dataset.translitModus = modus;
    root.classList.toggle("translit-aan", aan);
    root.classList.toggle("translit-uit", !aan);
    root.classList.toggle("translit-modus-nls", modus === "nls");
    root.classList.toggle("translit-modus-ksl", modus === "ksl");

    document.querySelectorAll("[data-translit-controls]").forEach(function (box) {
      box.dataset.translitOn = aan ? "true" : "false";
      box.dataset.translitModus = modus;
    });

    document.querySelectorAll("[data-translit-switch]").forEach(function (input) {
      input.checked = aan;
      input.setAttribute("aria-checked", aan ? "true" : "false");
    });

    document.querySelectorAll("[data-translit-modus]").forEach(function (input) {
      var val = (input.value || "").toLowerCase();
      input.checked = val === modus;
    });

    applyTranslitViews(aan, modus);
    applyPaginaPdfDownload(aan, modus);

    window.dispatchEvent(
      new CustomEvent("bibliotheek:translit", {
        detail: { aan: aan, modus: modus },
      })
    );
  }

  function currentModusFromDom() {
    var checked = document.querySelector("[data-translit-modus]:checked");
    if (checked && (checked.value || "").toLowerCase() === "ksl") return "ksl";
    return DEFAULT_MODUS;
  }

  function bindControls() {
    document.querySelectorAll("[data-translit-switch]").forEach(function (input) {
      if (input.__translitBound) return;
      input.__translitBound = true;
      input.addEventListener("change", function () {
        var aan = !!input.checked;
        var modus = currentModusFromDom();
        applyState(aan, modus);
        writeStoredAan(aan);
      });
    });

    document.querySelectorAll("[data-translit-modus]").forEach(function (input) {
      if (input.__translitModusBound) return;
      input.__translitModusBound = true;
      input.addEventListener("change", function () {
        if (!input.checked) return;
        var modus = (input.value || "").toLowerCase() === "ksl" ? "ksl" : DEFAULT_MODUS;
        var aan = document.documentElement.dataset.translit === "aan";
        applyState(aan, modus);
        writeStoredModus(modus);
      });
    });
  }

  /* Default = uit + nls; localStorage overschrijft. */
  applyState(readStoredAan(), readStoredModus());
  bindControls();

  document.addEventListener("DOMContentLoaded", function () {
    applyState(readStoredAan(), readStoredModus());
    bindControls();
  });
})();
