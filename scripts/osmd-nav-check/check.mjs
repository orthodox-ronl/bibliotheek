/**
 * Steekproef: OSMD tekent speelplan-navigatie uit committed `.from-ir.musicxml`.
 *
 * Geen XML-pariteitstest (dat is VSA-tooling) — hier alleen: als de MusicXML
 * herhaal/volta/segno/coda/fine bevat, moet OSMD die na render aantoonbaar
 * in VexFlow-modifiers / SVG zetten.
 *
 * Gebruik: node check.mjs   (cwd: scripts/osmd-nav-check of via wrapper)
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..", "..");
const OSMD_CDN =
  "https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.3/build/opensheetmusicdisplay.min.js";

/** VexFlow BarlineType (OSMD 1.9 / VF): REPEAT_BEGIN=4, REPEAT_END=5 */
const VF_REPEAT_BEGIN = 4;
const VF_REPEAT_END = 5;

const SAMPLES = [
  {
    id: "alleluia-9a-toon-1-groningen",
    fromIrRel:
      "content-source/catalogus/alleluia/9a-toon-1/groningen/alleluia-9a-toon-1-groningen.mvsa.from-ir.musicxml",
    // Dit blad moet speelplan-bladvorm (volta) in from-ir hebben.
    requireNavInXml: true,
  },
];

function expectFromXml(xml) {
  const endingLabels = [
    ...xml.matchAll(/<ending\b[^>]*\bnumber\s*=\s*["']([^"']+)["']/gi),
  ].map((m) => m[1].trim());
  return {
    repeatForward: /<repeat\b[^>]*direction\s*=\s*["']forward["']/i.test(xml),
    repeatBackward: /<repeat\b[^>]*direction\s*=\s*["']backward["']/i.test(xml),
    volta: /<ending\b/i.test(xml),
    endingLabels: [...new Set(endingLabels)],
    segno: /<segno\b/i.test(xml) || />\s*segno\s*</i.test(xml),
    coda: /<coda\b/i.test(xml) || />\s*coda\s*</i.test(xml),
    fine: />\s*Fine\s*</i.test(xml) || /type\s*=\s*["']fine["']/i.test(xml),
  };
}

function anyExpected(exp) {
  return (
    exp.repeatForward ||
    exp.repeatBackward ||
    exp.volta ||
    exp.segno ||
    exp.coda ||
    exp.fine
  );
}

async function renderDrawn(page, xmlText) {
  return page.evaluate(async (xml) => {
    const OSMD = opensheetmusicdisplay.OpenSheetMusicDisplay;
    const host = document.getElementById("osmd");
    host.innerHTML = "";
    const osmd = new OSMD(host, {
      autoResize: false,
      backend: "svg",
      drawTitle: false,
      drawSubtitle: false,
      drawComposer: false,
      drawLyricist: false,
      drawCredits: false,
      drawPartNames: false,
      drawPartAbbreviations: false,
      drawMeasureNumbers: true,
      drawMetronomeMarks: false,
      drawTimeSignatures: false,
      newSystemFromXML: true,
    });
    await osmd.load(xml);
    osmd.render();

    // Zelfde correctie als static/js/score-osmd.js (OSMD 1.9 knipt «1,2» → «1»).
    const doc = new DOMParser().parseFromString(xml, "application/xml");
    const part = doc.querySelector("part");
    const byNum = {};
    if (part) {
      for (const m of part.querySelectorAll(":scope > measure")) {
        const num = m.getAttribute("number");
        if (!num) continue;
        const ending =
          m.querySelector('barline[location="left"] ending') ||
          m.querySelector('barline[location="right"] ending');
        const label = ending?.getAttribute("number")?.trim();
        if (label) byNum[num] = label;
      }
    }
    for (const g of host.querySelectorAll("g.vf-measure")) {
      const id = g.getAttribute("id");
      const label = id && byNum[id];
      if (!label) continue;
      const first = label.split(",")[0].trim();
      for (const child of g.children) {
        if (String(child.tagName || "").toLowerCase() !== "text") continue;
        const cur = String(child.textContent || "").trim();
        if (cur === first && cur !== label) child.textContent = label;
      }
    }

    const barTypes = new Set();
    const cats = new Set();
    for (const row of osmd.GraphicSheet.MeasureList || []) {
      for (const m of row || []) {
        if (!m) continue;
        const stave = m.stave || m.vfStave;
        if (!stave || !stave.getModifiers) continue;
        for (const mod of stave.getModifiers()) {
          const cat = mod.getCategory ? mod.getCategory() : null;
          if (cat) cats.add(cat);
          if (cat === "barlines" && mod.getType) {
            barTypes.add(mod.getType());
          }
        }
      }
    }

    const root = host;
    const texts = [
      ...new Set(
        [...root.querySelectorAll("text")]
          .map((t) => (t.textContent || "").trim())
          .filter(Boolean)
      ),
    ];

    return {
      barTypes: [...barTypes],
      cats: [...cats],
      bracketCount: root.querySelectorAll(".vf-bracket").length,
      texts,
      hasSvg: !!root.querySelector("svg"),
    };
  }, xmlText);
}

function checkSample(id, expect, drawn) {
  const errors = [];
  if (!drawn.hasSvg) {
    errors.push(`${id}: OSMD leverde geen SVG`);
    return errors;
  }
  if (expect.repeatForward && !drawn.barTypes.includes(VF_REPEAT_BEGIN)) {
    errors.push(
      `${id}: MusicXML heeft herhaal-begin, maar OSMD tekende geen REPEAT_BEGIN-maatstreep (VF type ${VF_REPEAT_BEGIN})`
    );
  }
  if (expect.repeatBackward && !drawn.barTypes.includes(VF_REPEAT_END)) {
    errors.push(
      `${id}: MusicXML heeft herhaal-eind, maar OSMD tekende geen REPEAT_END-maatstreep (VF type ${VF_REPEAT_END})`
    );
  }
  if (expect.volta) {
    const hasVoltaMod = drawn.cats.includes("voltas");
    if (!hasVoltaMod) {
      errors.push(
        `${id}: MusicXML heeft <ending>, maar OSMD tekende geen volta (geen VF-voltas)`
      );
    }
    for (const label of expect.endingLabels || []) {
      if (label.includes(",") && !drawn.texts.includes(label)) {
        errors.push(
          `${id}: volta-label «${label}» ontbreekt in OSMD-tekst (verwacht na score-osmd-correctie)`
        );
      }
    }
  }
  // Segno/coda/Fine: steekproef volgt later (eigen catalogusblad).
  return errors;
}

async function main() {
  const failures = [];

  const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="${OSMD_CDN}"></script>
</head><body><div id="osmd" style="width:1000px"></div></body></html>`;

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: "networkidle" });
  const osmdOk = await page.evaluate(
    () =>
      !!(
        window.opensheetmusicdisplay &&
        window.opensheetmusicdisplay.OpenSheetMusicDisplay
      )
  );
  if (!osmdOk) {
    await browser.close();
    console.error("ERROR: OSMD-CDN laden mislukt");
    process.exit(1);
  }

  for (const sample of SAMPLES) {
    const path = join(REPO, sample.fromIrRel);
    if (!existsSync(path)) {
      failures.push(`${sample.id}: bestand ontbreekt: ${sample.fromIrRel}`);
      continue;
    }
    const xml = readFileSync(path, "utf8");
    const expect = expectFromXml(xml);
    if (sample.requireNavInXml && !anyExpected(expect)) {
      failures.push(
        `${sample.id}: from-ir MusicXML bevat geen herhaal/volta/segno/coda/fine — vernieuw Score-IR/from-ir (mvsa score-ir --musicxml of sync_mvsa_products) zodat speelplan-navigatie in het product staat`
      );
      continue;
    }
    if (!anyExpected(expect)) {
      console.log(`SKIP ${sample.id}: geen navigatiemarkeringen in MusicXML`);
      continue;
    }
    let drawn;
    try {
      drawn = await renderDrawn(page, xml);
    } catch (e) {
      failures.push(`${sample.id}: OSMD-render faalde: ${e}`);
      continue;
    }
    const errs = checkSample(sample.id, expect, drawn);
    if (errs.length) {
      failures.push(...errs);
      console.log(
        `FAIL ${sample.id}: expect=${JSON.stringify(expect)} drawn=${JSON.stringify(
          {
            barTypes: drawn.barTypes,
            cats: drawn.cats,
            bracketCount: drawn.bracketCount,
            has12: drawn.has12,
          }
        )}`
      );
    } else {
      console.log(
        `OK   ${sample.id}: OSMD tekent navigatie (${Object.entries(expect)
          .filter(([, v]) => v)
          .map(([k]) => k)
          .join(", ")})`
      );
    }
  }

  await browser.close();

  if (failures.length) {
    console.error("");
    console.error("OSMD-navigatie-zichtbaarheid: FOUTEN");
    for (const f of failures) console.error(`  - ${f}`);
    process.exit(1);
  }
  console.log("OK: OSMD-navigatie zichtbaar op steekproef");
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
