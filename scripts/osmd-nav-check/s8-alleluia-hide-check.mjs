/**
 * A1-contract: S8-adapter op alleluia-9a-toon-8-groningen from-ir
 * (zelfde finalize als score-osmd.js). Spacer-koppen moeten weg; lyrics blijven.
 * Zie docs/specs/schermpartituur.md §5.1.
 */
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..", "..");
const XML = resolve(
  REPO,
  "content-source/catalogus/alleluia/9a-toon-8/groningen/alleluia-9a-toon-8-groningen.mvsa.from-ir.musicxml"
);
const SCORE_OSMD = resolve(REPO, "static/js/score-osmd.js");
const OSMD_CDN =
  "https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.3/build/opensheetmusicdisplay.min.js";

async function main() {
  const xmlText = readFileSync(XML, "utf8");
  const scoreOsmdJs = readFileSync(SCORE_OSMD, "utf8");
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="${OSMD_CDN}"></script>
</head><body><div id="host" style="width:960px"></div></body></html>`;

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.addScriptTag({ content: scoreOsmdJs });
  const result = await page.evaluate(async (xml) => {
    var host = document.getElementById("host");
    var mount = document.createElement("div");
    mount.className = "osmd-mount";
    host.appendChild(mount);
    var OSMD = opensheetmusicdisplay.OpenSheetMusicDisplay;
    var osmd = new OSMD(mount, {
      autoResize: false,
      backend: "svg",
      drawTitle: false,
      drawPartNames: false,
      drawMetronomeMarks: false,
      drawTimeSignatures: false,
      newSystemFromXML: true,
    });
    var blob = new Blob([xml], { type: "application/xml" });
    var url = URL.createObjectURL(blob);
    await osmd.load(url);
    osmd.render();
    if (typeof window.__vsaScoreOsmdFinalizePrint === "function") {
      window.__vsaScoreOsmdFinalizePrint(mount, xml);
    }
    if (typeof window.__vsaScoreOsmdDiagnoseReport === "function") {
      return window.__vsaScoreOsmdDiagnoseReport(mount, xml);
    }
    return { ok: false, error: "no diagnose api" };
  }, xmlText);
  await browser.close();

  if (!result.ok) {
    console.error("S8 A1 adapter check FAILED");
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }
  console.log("S8 A1 adapter check OK");
  console.log(
    "boven keepVisible=" +
      result.staven.boven.keepVisibleHeads +
      " spacer=" +
      result.staven.boven.spacerVisibleHeads +
      " cadence=" +
      result.staven.boven.cadenceVisibleHeads
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
