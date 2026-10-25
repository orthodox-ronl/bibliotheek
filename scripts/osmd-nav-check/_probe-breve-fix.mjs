import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..", "..");
const xml = readFileSync(
  resolve(
    REPO,
    "content-source/catalogus/alleluia/9a-toon-8/groningen/alleluia-9a-toon-8-groningen.mvsa.from-ir.musicxml"
  ),
  "utf8"
);
const js = readFileSync(resolve(REPO, "static/js/score-osmd.js"), "utf8");

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.setViewportSize({ width: 1100, height: 400 });
await page.setContent(
  `<!DOCTYPE html><html><body><div id="host" style="width:960px"></div>
<script src="https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.3/build/opensheetmusicdisplay.min.js"></script>
</body></html>`,
  { waitUntil: "networkidle" }
);
await page.addScriptTag({ content: js });

const info = await page.evaluate(async (xmlText) => {
  const mount = document.createElement("div");
  mount.className = "osmd-mount";
  document.getElementById("host").appendChild(mount);
  const osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(mount, {
    autoResize: false,
    backend: "svg",
    drawTitle: false,
    drawPartNames: false,
    drawMetronomeMarks: false,
    drawTimeSignatures: false,
    newSystemFromXML: true,
  });
  await osmd.load(
    URL.createObjectURL(new Blob([xmlText], { type: "application/xml" }))
  );
  osmd.render();
  window.__vsaScoreOsmdCenterMeasures(mount);
  window.__vsaScoreOsmdFinalizePrint(mount, xmlText);
  const painted = [...mount.querySelectorAll("[data-osmd-breve-paint='1']")];
  const marked = [...mount.querySelectorAll("[data-osmd-breve='1']")];
  const gapLedgers = [];
  for (const p of mount.querySelectorAll(".vf-ledgers path, .vf-ledgers")) {
    let b;
    try {
      b = p.getBBox();
    } catch (e) {
      continue;
    }
    const st = getComputedStyle(p);
    if (st.display === "none" || st.visibility === "hidden") continue;
    const cx = b.x + b.width / 2;
    if (cx > 130 && cx < 400) {
      gapLedgers.push({
        tag: p.tagName,
        cls: p.getAttribute("class"),
        x: +cx.toFixed(1),
        y: +b.y.toFixed(1),
        w: +b.width.toFixed(1),
      });
    }
  }
  return {
    build: window.__VSA_SCORE_OSMD_BUILD,
    painted: painted.length,
    marked: marked.length,
    paintSample: painted[0] ? painted[0].outerHTML.slice(0, 350) : null,
    gapLedgers,
  };
}, xml);

console.log(JSON.stringify(info, null, 2));
await page.screenshot({
  path: resolve(HERE, "out-breve-fix.png"),
  fullPage: true,
});
await browser.close();
