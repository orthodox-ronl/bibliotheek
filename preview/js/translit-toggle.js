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

  function safeDownloadName(name, fallback) {
    var n = (name || fallback || "blad.pdf").replace(/[\\/:*?"<>|]+/g, "-").trim();
    if (!/\.pdf$/i.test(n)) n += ".pdf";
    return n;
  }

  /** Raden van translit-beide-URL als het data-attribuut ontbreekt. */
  function deriveBeidePdfUrl(a) {
    var beide = a.getAttribute("data-pdf-beide") || "";
    if (beide) return beide;
    var nls = a.getAttribute("data-pdf-nls") || "";
    if (nls.indexOf(".translit-nls.pdf") !== -1) {
      return nls.split(".translit-nls.pdf").join(".translit-beide.pdf");
    }
    var ksl = a.getAttribute("data-pdf-ksl") || "";
    if (ksl.indexOf(".translit-ksl.pdf") !== -1) {
      return ksl.split(".translit-ksl.pdf").join(".translit-beide.pdf");
    }
    return "";
  }

  function pdfCandidates(a, aan, modus) {
    var uit = {
      href: a.getAttribute("data-pdf-uit") || "",
      name: a.getAttribute("data-pdf-name-uit") || "blad.pdf",
    };
    var nls = {
      href: a.getAttribute("data-pdf-nls") || "",
      name: a.getAttribute("data-pdf-name-nls") || uit.name,
    };
    var ksl = {
      href: a.getAttribute("data-pdf-ksl") || "",
      name: a.getAttribute("data-pdf-name-ksl") || uit.name,
    };
    var beide = {
      href: deriveBeidePdfUrl(a),
      name: a.getAttribute("data-pdf-name-beide") || "blad (translit beide).pdf",
    };
    var list = [];
    if (aan && modus === "ksl") {
      if (ksl.href) list.push(ksl);
      if (uit.href) list.push(uit);
    } else if (aan && modus === "beide") {
      if (beide.href) list.push(beide);
      /* Geen gecombineerde PDF (404 op oude server): los Nls + Ksl. */
      if (nls.href) list.push(nls);
      if (ksl.href) list.push(ksl);
      if (uit.href) list.push(uit);
    } else if (aan) {
      if (nls.href) list.push(nls);
      if (uit.href) list.push(uit);
    } else if (uit.href) {
      list.push(uit);
    }
    return list;
  }

  function triggerBlobDownload(blob, filename) {
    var url = URL.createObjectURL(blob);
    var tmp = document.createElement("a");
    tmp.href = url;
    tmp.download = safeDownloadName(filename, "blad.pdf");
    tmp.rel = "noopener";
    document.body.appendChild(tmp);
    tmp.click();
    tmp.remove();
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 2000);
  }

  function fetchPdf(href) {
    return fetch(href, { method: "GET", credentials: "same-origin" }).then(
      function (res) {
        if (!res.ok) throw new Error("pdf-http-" + res.status);
        return res.blob();
      }
    );
  }

  function delay(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
  }

  /**
   * Probeer kandidaten tot er een PDF binnenkomt.
   * Bij modus beide: eerst gecombineerde PDF; bij 404 alle losse
   * translit-PDF’s (Nls én Ksl) achter elkaar.
   */
  function downloadPdfCandidates(cands, modus) {
    if (!cands.length) return Promise.resolve(false);

    var combined = [];
    var loose = [];
    cands.forEach(function (c) {
      if (!c || !c.href) return;
      if (/translit-beide\.pdf/i.test(c.href)) combined.push(c);
      else loose.push(c);
    });

    function tryOneOf(list, i) {
      if (i >= list.length) return Promise.resolve(false);
      return fetchPdf(list[i].href)
        .then(function (blob) {
          triggerBlobDownload(blob, list[i].name);
          return true;
        })
        .catch(function () {
          return tryOneOf(list, i + 1);
        });
    }

    function downloadAllLoose(list, i, any) {
      if (i >= list.length) return Promise.resolve(!!any);
      /* Alleen translit-varianten als «los»; geen kale PDF erbij als
         er al een translit gelukt is — die staat als laatste fallback. */
      return fetchPdf(list[i].href)
        .then(function (blob) {
          triggerBlobDownload(blob, list[i].name);
          return delay(350).then(function () {
            return downloadAllLoose(list, i + 1, true);
          });
        })
        .catch(function () {
          return downloadAllLoose(list, i + 1, any);
        });
    }

    if (modus === "beide") {
      return tryOneOf(combined, 0).then(function (ok) {
        if (ok) return true;
        var translits = loose.filter(function (c) {
          return /translit-(nls|ksl)\.pdf/i.test(c.href);
        });
        var plain = loose.filter(function (c) {
          return !/translit-(nls|ksl)\.pdf/i.test(c.href);
        });
        return downloadAllLoose(translits, 0, false).then(function (got) {
          if (got) return true;
          return tryOneOf(plain, 0);
        });
      });
    }

    return tryOneOf(cands, 0);
  }
  function applyPaginaPdfDownload(aan, modus) {
    document.querySelectorAll("[data-pagina-pdf-download]").forEach(function (a) {
      var cands = pdfCandidates(a, aan, modus);
      a.__pdfCandidates = cands;
      a.__pdfModus = aan ? modus : "uit";
      var href = cands.length ? cands[0].href : "";
      var name = cands.length ? cands[0].name : "";
      if (href) {
        a.setAttribute("href", href);
        a.removeAttribute("hidden");
      } else {
        a.setAttribute("hidden", "");
      }
      if (name) a.setAttribute("download", safeDownloadName(name, "blad.pdf"));
      var title = "Pagina als PDF downloaden";
      if (aan && modus === "ksl") {
        title = "PDF met translit Ksl downloaden";
      } else if (aan && modus === "beide") {
        title = "PDF met beide translits downloaden";
      } else if (aan) {
        title = "PDF met translit Nls downloaden";
      }
      a.setAttribute("title", title);
      a.setAttribute("aria-label", title);
    });
  }

  function bindPdfDownloadClicks() {
    document.querySelectorAll("[data-pagina-pdf-download]").forEach(function (a) {
      if (a.__pdfDownloadBound) return;
      a.__pdfDownloadBound = true;
      a.addEventListener("click", function (ev) {
        var cands = a.__pdfCandidates;
        if (!cands || !cands.length) return;
        ev.preventDefault();
        ev.stopPropagation();
        downloadPdfCandidates(cands, a.__pdfModus || "uit").then(function (ok) {
          if (!ok && cands[0] && cands[0].href) {
            /* Laatste redmiddel: gewone navigatie. */
            window.location.href = cands[0].href;
          }
        });
      });
    });
  }

  /** Oefenen (Coria): gewone MXL of …translit.mxl, zelfde stand als de knoppen. */
  function applyCoriaOefenen(aan) {
    document.querySelectorAll("[data-coria-uit]").forEach(function (a) {
      var href = a.getAttribute("data-coria-uit") || "";
      if (aan) {
        href = a.getAttribute("data-coria-translit") || href;
      }
      if (href) a.setAttribute("href", href);
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
    applyCoriaOefenen(aan);

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
  bindPdfDownloadClicks();

  document.addEventListener("DOMContentLoaded", function () {
    var again = readStoredFlags();
    applyState(again.nls, again.ksl);
    bindControls();
    bindPdfDownloadClicks();
  });
})();
