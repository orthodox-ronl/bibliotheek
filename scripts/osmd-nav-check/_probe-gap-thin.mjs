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

  const thin = [];
  for (const el of mount.querySelectorAll("path, line, rect")) {
    let b;
    try {
      b = el.getBBox();
    } catch (e) {
      continue;
    }
    const st = getComputedStyle(el);
    if (st.display === "none" || st.visibility === "hidden") continue;
    // thin horizontal in bass-staff band, gap x
    if (b.height > 3.5 || b.width < 2 || b.width > 60) continue;
    if (b.y < 190 || b.y > 230) continue;
    if (b.x + b.width / 2 < 100 || b.x + b.width / 2 > 450) continue;
    const p = el.parentElement;
    thin.push({
      tag: el.tagName,
      cls: el.getAttribute("class") || "",
      parent: p ? p.getAttribute("class") || p.tagName : "",
      x: +(b.x + b.width / 2).toFixed(1),
      y: +b.y.toFixed(1),
      w: +b.width.toFixed(1),
      h: +b.height.toFixed(1),
      stroke: el.getAttribute("stroke"),
    });
  }
  thin.sort((a, b) => a.x - b.x);

  const breves = [...mount.querySelectorAll(".vsa-osmd-breve")].map((g) => {
    const e = g.querySelector("ellipse");
    return e
      ? {
          cx: +(+e.getAttribute("cx")).toFixed(1),
          cy: +(+e.getAttribute("cy")).toFixed(1),
          rx: +(+e.getAttribute("rx")).toFixed(1),
          ry: +(+e.getAttribute("ry")).toFixed(1),
        }
      : null;
  });

  return { thin, breves, build: window.__VSA_SCORE_OSMD_BUILD };
}, xml);

console.log(JSON.stringify(info, null, 2));
await browser.close();
