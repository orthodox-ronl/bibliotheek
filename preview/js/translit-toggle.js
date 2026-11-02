(function () {
  /* Livereload kan dit script opnieuw injecteren; voorkom dubbele handlers. */
  if (window.__bibliotheekTranslitBound) return;
  window.__bibliotheekTranslitBound = true;

  var STORAGE_KEY = "bibliotheek-translit";
  var STORAGE_MODUS = "bibliotheek-translit-modus";

  function flagsFromModus(modus) {
    var m = (modus || "").toLowerCase();
    if (m === "beide") return { nls: true, ksl: true };
    if (m === "ksl") return { nls: false, ksl: true };
    if (m === "nls") return { nls: true, ksl: false };
    return { nls: false, ksl: false };
  }

  function modusFromFlags(nls, ksl) {
    if (nls && ksl) return "beide";
    if (ksl) return "ksl";
    if (nls) return "nls";
    return "uit";
  }

  function readStoredFlags() {
    try {
      var storedModus = (window.localStorage.getItem(STORAGE_MODUS) || "").toLowerCase();
      var storedAan = window.localStorage.getItem(STORAGE_KEY);
      if (storedModus === "beide" || storedModus === "nls" || storedModus === "ksl") {
        var flags = flagsFromModus(storedModus);
        /* Oude combo: modus nls + power uit → beide knoppen uit. */
        if (storedAan === "uit") return { nls: false, ksl: false };
        if (storedAan === "aan" || storedAan === null) return flags;
        return flags;
      }
      if (storedModus === "uit") return { nls: false, ksl: false };
      /* Legacy: alleen power-key, default modus was nls. */
      if (storedAan === "aan") return { nls: true, ksl: false };
    } catch (e) {
      /* private mode */
    }
    return { nls: false, ksl: false };
  }

  function writeStoredFlags(nls, ksl) {
    var modus = modusFromFlags(nls, ksl);
    try {
      window.localStorage.setItem(STORAGE_MODUS, modus);
      window.localStorage.setItem(STORAGE_KEY, nls || ksl ? "aan" : "uit");
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
        if (!forModus) forModus = "nls";
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
      } else if (aan && modus === "beide") {
        href =
          a.getAttribute("data-pdf-nls") ||
          a.getAttribute("data-pdf-ksl") ||
          href;
        name =
          a.getAttribute("data-pdf-name-nls") ||
          a.getAttribute("data-pdf-name-ksl") ||
          name;
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
      var title = "Pagina als PDF downloaden";
      if (aan && modus === "ksl") {
        title = "PDF met translit Ksl downloaden";
      } else if (aan && modus === "beide") {
        title = "PDF met translit downloaden";
      } else if (aan) {
        title = "PDF met translit Nls downloaden";
      }
      a.setAttribute("title", title);
      a.setAttribute("aria-label", title);
    });
  }

  function applyState(nls, ksl) {
    nls = !!nls;
    ksl = !!ksl;
    var aan = nls || ksl;
    var modus = modusFromFlags(nls, ksl);
    var root = document.documentElement;
    root.dataset.translit = aan ? "aan" : "uit";
    root.dataset.translitModus = modus;
    root.classList.toggle("translit-aan", aan);
    root.classList.toggle("translit-uit", !aan);
    root.classList.toggle("translit-modus-nls", modus === "nls");
    root.classList.toggle("translit-modus-ksl", modus === "ksl");
    root.classList.toggle("translit-modus-beide", modus === "beide");

    document.querySelectorAll("[data-translit-controls]").forEach(function (box) {
      box.dataset.translitOn = aan ? "true" : "false";
      box.dataset.translitModus = modus;
    });

    document.querySelectorAll("[data-translit-modus]").forEach(function (input) {
      var val = (input.getAttribute("data-translit-modus") || input.value || "").toLowerCase();
      input.checked = val === "nls" ? nls : val === "ksl" ? ksl : false;
    });

    applyTranslitViews(aan, modus === "uit" ? "nls" : modus);
    applyPaginaPdfDownload(aan, modus === "uit" ? "nls" : modus);

    window.dispatchEvent(
      new CustomEvent("bibliotheek:translit", {
        detail: { aan: aan, modus: modus, nls: nls, ksl: ksl },
      })
    );
  }

  function flagsFromDom() {
    var nls = false;
    var ksl = false;
    document.querySelectorAll("[data-translit-modus]").forEach(function (input) {
      var val = (input.getAttribute("data-translit-modus") || input.value || "").toLowerCase();
      if (val === "nls") nls = !!input.checked;
      if (val === "ksl") ksl = !!input.checked;
    });
    return { nls: nls, ksl: ksl };
  }

  function bindControls() {
    document.querySelectorAll("[data-translit-modus]").forEach(function (input) {
      if (input.__translitModusBound) return;
      input.__translitModusBound = true;
      input.addEventListener("change", function () {
        var flags = flagsFromDom();
        applyState(flags.nls, flags.ksl);
        writeStoredFlags(flags.nls, flags.ksl);
      });
    });
  }

  var initial = readStoredFlags();
  applyState(initial.nls, initial.ksl);
  bindControls();

  document.addEventListener("DOMContentLoaded", function () {
    var again = readStoredFlags();
    applyState(again.nls, again.ksl);
    bindControls();
  });
})();
