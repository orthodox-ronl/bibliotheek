import { readFileSync, writeFileSync } from "node:fs";
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
await page.setViewportSize({ width: 1100, height: 500 });
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
  if (typeof window.__vsaScoreOsmdCenterMeasures === "function") {
    window.__vsaScoreOsmdCenterMeasures(mount);
  }
  window.__vsaScoreOsmdFinalizePrint(mount, xmlText);

  // Alle zichtbare SVG-elementen in de gap-zone (tussen breve ~152 en cadens ~380)
  // op de bas-staf (y ~ 174..250)
  const svg = mount.querySelector("svg");
  const all = [...svg.querySelectorAll("*")];
  const hits = [];
  for (const el of all) {
    let b;
    try {
      b = el.getBBox();
    } catch (e) {
      continue;
    }
    if (b.width < 0.5 && b.height < 0.5) continue;
    const st = getComputedStyle(el);
    if (st.display === "none" || st.visibility === "hidden") continue;
    const cx = b.x + b.width / 2;
    const cy = b.y + b.height / 2;
    // gap x 160..370 — hele hoogte (streepjes kunnen lyrics- of balk-y hebben)
    if (cx < 160 || cx > 370) continue;
    // skip staff lines (very wide thin)
    if (b.width > 200 && b.height < 3) continue;
    hits.push({
      tag: el.tagName,
      cls: el.getAttribute("class") || "",
      text: String(el.textContent || "").trim().slice(0, 30),
      x: +cx.toFixed(1),
      y: +cy.toFixed(1),
      w: +b.width.toFixed(1),
      h: +b.height.toFixed(1),
      fill: el.getAttribute("fill"),
      stroke: el.getAttribute("stroke"),
      parentCls: el.parentElement
        ? el.parentElement.getAttribute("class") || el.parentElement.tagName
        : "",
    });
  }
  hits.sort((a, b) => a.x - b.x || a.y - b.y);

  // Breve notehead path detail (upper voice note 1)
  const notes = [
    ...mount.querySelectorAll(".vf-measure")[0].querySelectorAll("g.vf-stavenote"),
  ];
  const breve = notes[1];
  const nh = breve.querySelector(".vf-notehead, path.vf-notehead, .vf-note path");
  return {
    hits,
    breveOuter: breve.outerHTML.slice(0, 1200),
    noteheadHTML: nh ? nh.outerHTML.slice(0, 400) : null,
  };
}, xml);

writeFileSync(resolve(HERE, "out-gap-els.json"), JSON.stringify(info, null, 2));
console.log("hits", info.hits.length);
console.log(JSON.stringify(info.hits.slice(0, 40), null, 2));
await browser.close();
