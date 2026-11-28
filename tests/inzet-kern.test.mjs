import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const Kern = require("../static/js/inzet-kern.js");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const noot = (voice, step, octave, alter) =>
  `<note><pitch><step>${step}</step>${alter ? `<alter>${alter}</alter>` : ""}` +
  `<octave>${octave}</octave></pitch><voice>${voice}</voice></note>`;
const rust = (voice) => `<note><rest/><voice>${voice}</voice></note>`;
const stuk = (p1, p2) =>
  `<score-partwise><part-list><score-part id="P1"><part-name></part-name></score-part></part-list>` +
  `<part id="P1">${p1}</part><part id="P2">${p2}</part></score-partwise>`;

test("eerste noot per stem in de volgorde S, A, T, B; rust telt niet", () => {
  const xml = stuk(
    rust(1) + noot(1, "A", 4) + noot(1, "G", 4) + noot(2, "F", 4),
    noot(1, "C", 4) + noot(2, "B", 2, -1),
  );
  assert.deepEqual(Kern.beginnoten(xml), [
    { stem: "S", midi: 69 },
    { stem: "A", midi: 65 },
    { stem: "T", midi: 60 },
    { stem: "B", midi: 46 },
  ]);
});

test("ontbrekende stem of andere opbouw geeft null", () => {
  assert.equal(Kern.beginnoten(stuk(noot(1, "A", 4), noot(1, "C", 4))), null);
  assert.equal(Kern.beginnoten("<score-partwise/>"), null);
});

test("toonhoogte en tijden", () => {
  assert.equal(Kern.frequentie(69), 440);
  assert.equal(Kern.frequentie(57), 220);
  const schema = Kern.speelschema(
    ["S", "A", "T", "B"].map((stem) => ({ stem, midi: 69 })),
  );
  assert.deepEqual(
    schema.map((t) => [t.stem, Number(t.start.toFixed(1)), t.duur]),
    [["S", 0, 0.5], ["A", 0.6, 0.5], ["T", 1.2, 0.5], ["B", 1.8, 0.5]],
  );
});

test("elke from-ir in de catalogus levert vier beginnoten", () => {
  const dir = path.join(root, "content-source", "catalogus");
  const files = readdirSync(dir, { recursive: true }).filter((f) =>
    f.endsWith(".from-ir.musicxml"),
  );
  const fout = files.filter(
    (f) => !Kern.beginnoten(readFileSync(path.join(dir, f), "utf8")),
  );
  assert.deepEqual(fout, []);
});
