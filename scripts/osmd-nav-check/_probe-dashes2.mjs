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

  function collectDashes(label) {
    const out = [];
    const texts = [...mount.querySelectorAll("text")];
    for (const t of texts) {
      const s = String(t.textContent || "").trim();
      if (s !== "-" && s !== "–" && s !== "—") continue;
      const b = t.getBBox();
      const st = getComputedStyle(t);
      out.push({
        label,
        kind: "text",
        s,
        x: +b.x.toFixed(1),
        y: +b.y.toFixed(1),
        w: +b.width.toFixed(1),
        h: +b.height.toFixed(1),
        vis: st.visibility,
        disp: st.display,
        parent: t.parentElement
          ? t.parentElement.getAttribute("class") || ""
          : "",
      });
    }
    for (const g of mount.querySelectorAll("g.vf-text.dash, g.vf-annotation")) {
      const b = g.getBBox();
      const st = getComputedStyle(g);
      out.push({
        label,
        kind: "g",
        cls: g.getAttribute("class"),
        x: +b.x.toFixed(1),
        y: +b.y.toFixed(1),
        w: +b.width.toFixed(1),
        h: +b.height.toFixed(1),
        vis: st.visibility,
        disp: st.display,
        text: String(g.textContent || "").trim().slice(0, 20),
      });
    }
    // thin horizontal paths (possible drawn hyphens)
    for (const p of mount.querySelectorAll("path")) {
      let b;
      try {
        b = p.getBBox();
      } catch (e) {
        continue;
      }
      if (b.height > 4 || b.width < 3 || b.width > 40) continue;
      const st = getComputedStyle(p);
      if (st.display === "none" || st.visibility === "hidden") continue;
      const cls = p.getAttribute("class") || "";
      if (cls.includes("stem") || cls.includes("staff")) continue;
      out.push({
        label,
        kind: "path",
        cls,
        x: +(b.x + b.width / 2).toFixed(1),
        y: +b.y.toFixed(1),
        w: +b.width.toFixed(1),
        h: +b.height.toFixed(1),
        parent: p.parentElement
          ? p.parentElement.getAttribute("class") || ""
          : "",
      });
    }
    return out;
  }

  const before = collectDashes("before-finalize");
  window.__vsaScoreOsmdFinalizePrint(mount, xmlText);
  const after = collectDashes("after-finalize");

  // breve visual: is notehead path a normal oval?
  const notes = [
    ...mount.querySelectorAll(".vf-measure")[0].querySelectorAll("g.vf-stavenote"),
  ];
  const al = notes[0].querySelector(".vf-notehead path, .vf-note path");
  const br = notes[1].querySelector(".vf-notehead path, .vf-note path");
  return {
    beforeCount: before.length,
    afterCount: after.length,
    before: before.slice(0, 30),
    afterVisible: after.filter((d) => d.vis !== "hidden" && d.disp !== "none"),
    alD: al ? (al.getAttribute("d") || "").slice(0, 80) : null,
    brD: br ? (br.getAttribute("d") || "").slice(0, 80) : null,
    alBB: al ? al.getBBox() : null,
    brBB: br ? br.getBBox() : null,
  };
}, xml);

console.log(JSON.stringify(info, null, 2));
await browser.close();
