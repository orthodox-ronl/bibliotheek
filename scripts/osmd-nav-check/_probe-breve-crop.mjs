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
await page.evaluate(async (xmlText) => {
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
}, xml);

await page.screenshot({
  path: resolve(HERE, "out-breve-crop.png"),
  clip: { x: 100, y: 40, width: 120, height: 220 },
});
await page.screenshot({
  path: resolve(HERE, "out-gap-bass-crop.png"),
  clip: { x: 160, y: 170, width: 240, height: 80 },
});
await browser.close();
console.log("wrote crops");
