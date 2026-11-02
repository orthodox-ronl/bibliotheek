/**
 * Console-diagnose voor OSMD S8 (bibliotheek). Vereist geladen score-osmd.js
 * en een gerenderde .osmd-mount op de pagina.
 */
(function () {
  function formatPlain(report) {
    if (window.__vsaScoreOsmdPlainText) {
      return window.__vsaScoreOsmdPlainText(report);
    }
    return "Versie: " + (report.build || "?") + " ok=" + report.ok;
  }

  async function copyPlain(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      return false;
    }
  }

  async function runScoreOsmdDiagnose() {
    var host = document.querySelector("[data-osmd-src]");
    var mount = document.querySelector(".osmd-mount");
    if (!host) {
      console.error(
        "[VSA] Geen partituur op deze pagina. Open een catalogusblad met muziek."
      );
      return { ok: false, error: "no-host" };
    }
    if (!mount || !mount.querySelector(".vf-measure")) {
      console.error(
        "[VSA] Partituur laadt nog. Wacht tot de muziek zichtbaar is en voer opnieuw uit."
      );
      return { ok: false, error: "not-rendered" };
    }
    if (!window.__vsaScoreOsmdDiagnoseReport) {
      console.error(
        "[VSA] score-osmd.js is te oud. Ctrl+F5 en controleer de pagina opnieuw."
      );
      return { ok: false, error: "no-api" };
    }
    var src = host.getAttribute("data-osmd-src");
    var xmlText = await fetch(src).then(function (r) {
      if (!r.ok) {
        throw new Error("fetch " + src + " → " + r.status);
      }
      return r.text();
    });
    var report = window.__vsaScoreOsmdDiagnoseReport(mount, xmlText);
    var plain = formatPlain(report);
    report.plainText = plain;
    console.log(plain);
    var copied = await copyPlain(plain);
    if (copied) {
      console.log(
        "[VSA] ↑ Staat op je klembord. Plak in Cursor-chat met Ctrl+V en vul de laatste regel in."
      );
    } else {
      console.log(
        "[VSA] Klembord niet beschikbaar: selecteer de tekst hierboven, Ctrl+C, plak in chat."
      );
    }
    return report;
  }

  window.__vsaRunScoreOsmdDiagnose = runScoreOsmdDiagnose;
})();
