// Tests voor static/js/catalogus-zoek-kern.js (zoeken in de bibliotheek).
// Draaien: node --test tests/zoek-kern.test.mjs
// De teksten hieronder zijn zoals build_zoek_index.normalize_text ze maakt
// (kleine letters, geen accenten, harde streepjes los én aaneen).
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { createSearcher, norm } = require("../static/js/catalogus-zoek-kern.js");

function entry(id, title, text) {
  return { id, title, linkTitle: title, text };
}

const ENTRIES = [
  entry(
    "tropaar/zondag-toon-5/groningen",
    "Tropaar Zondag Toon 5 (Groningen)",
    "tropaar zondag toon 5 groningen gij heer bewaar ons tot in alle eeuwige eeuwigheid"
  ),
  entry(
    "communievers/onthoofding/hemelum",
    "Communievers Onthoofding (Hemelum)",
    "communievers onthoofding hemelum de rechtvaardige zal in eeuwige gedachtenis zijn"
  ),
  entry(
    "kondak/johannes-shanghai-toon-2/hemelum",
    "Kondak Johannes Shanghai Toon 2 (Hemelum)",
    "kondak johannes shanghai toon 2 hemelum beminde der heilige drie eenheid drieeenheid grote vader hierarch johannes gij die voor god staat"
  ),
  entry(
    "ektinia/slot/hemelum",
    "Ektinia Slot (Hemelum)",
    "ektinia slot hemelum heer ontferm u mysterien van gods genade"
  ),
  entry(
    "alleluia/toon-1/groningen",
    "Alleluia Toon 1 (Groningen)",
    "alleluia toon 1 groningen alleluia alleluia"
  ),
  entry(
    "tropaar/geboorte-mg-toon-4/hemelum",
    "Tropaar Geboorte MG Toon 4 (Hemelum)",
    "tropaar geboorte mg toon 4 hemelum uw geboorte o moeder gods heeft vreugde verkondigd aan heel de wereld eeuwige glorie"
  ),
];

const SYNONYMS = { alleluja: "alleluia", alleluia: "alleluia" };
const zoek = createSearcher(ENTRIES, SYNONYMS);
const ids = (q) => zoek.search(q).rows.map((r) => r.entry.id);

test("streepjes in de zoekterm maken geen verschil: eeuwige / eeu-wige / eeu-wi-ge", () => {
  const basis = ids("eeuwige").sort();
  assert.equal(basis.length, 3);
  assert.deepEqual(ids("eeu-wige").sort(), basis);
  assert.deepEqual(ids("eeu-wi-ge").sort(), basis);
});

test("accenten en trema's tellen niet mee, in zoekterm en tekst", () => {
  assert.deepEqual(ids("mysteriën"), ["ektinia/slot/hemelum"]);
  assert.deepEqual(ids("mysterien"), ["ektinia/slot/hemelum"]);
  assert.deepEqual(ids("hiërarch"), ["kondak/johannes-shanghai-toon-2/hemelum"]);
});

test("harde streepjes: drie-eenheid, drieeenheid en 'drie eenheid' vinden hetzelfde", () => {
  const verwacht = ["kondak/johannes-shanghai-toon-2/hemelum"];
  assert.deepEqual(ids("drie-eenheid"), verwacht);
  assert.deepEqual(ids("drieeenheid"), verwacht);
  assert.deepEqual(ids("drie eenheid"), verwacht);
});

test("een zoekwoord matcht vanaf het woordbegin, niet midden in een woord", () => {
  assert.equal(ids("eeuw").length, 3);
  assert.deepEqual(ids("ige"), []);
  assert.deepEqual(ids("wige"), []);
});

test("alle woorden moeten voorkomen; daarna komen deeltreffers", () => {
  const r = zoek.search("eeuwige glorie");
  assert.equal(r.tokenCount, 2);
  assert.equal(r.completeCount, 1);
  assert.equal(r.rows[0].entry.id, "tropaar/geboorte-mg-toon-4/hemelum");
  assert.equal(r.rows[0].complete, true);
  const deels = r.rows.slice(1);
  assert.ok(deels.length >= 1);
  assert.ok(deels.every((row) => row.complete === false));
});

test("zoveel mogelijk woorden eerst, dan de gezochte volgorde", () => {
  const e = [
    entry("a/a/a", "A", "heer bewaar ons gij"),
    entry("b/b/b", "B", "gij bewaar ons heer"),
    entry("c/c/c", "C", "gij ons"),
  ];
  const r = createSearcher(e, {}).search("heer bewaar ons gij");
  assert.deepEqual(
    r.rows.map((x) => x.entry.id),
    ["a/a/a", "b/b/b", "c/c/c"]
  );
  assert.equal(r.completeCount, 2);
  assert.equal(r.rows[2].complete, false);
});

test("alleen korte woorden (de, u) zijn geen reden voor een deeltreffer", () => {
  const e = [entry("a/a/a", "A", "heer ontferm u"), entry("b/b/b", "B", "de wereld")];
  const r = createSearcher(e, {}).search("wereld de");
  assert.deepEqual(r.rows.map((x) => x.entry.id), ["b/b/b"]);
  const s = createSearcher(e, {}).search("de u zijn");
  assert.equal(s.rows.length, 0);
});

test("synoniemen: alleluja vindt alleluia", () => {
  assert.deepEqual(ids("alleluja"), ["alleluia/toon-1/groningen"]);
});

test("een id plakken werkt (streepjes en schuine strepen)", () => {
  assert.equal(ids("tropaar/zondag-toon-5/groningen")[0], "tropaar/zondag-toon-5/groningen");
});

test("norm spiegelt build_zoek_index.normalize_text", () => {
  assert.equal(norm("De Drie-eenheid", {}), "de drie eenheid drieeenheid");
  assert.equal(norm("Mysteriën, Hiërarch", {}), "mysterien hierarch");
  assert.equal(norm("verhoor_ mij", {}), "verhoor mij");
});

test("lege zoekterm geeft geen treffers", () => {
  assert.deepEqual(zoek.search("   ").rows, []);
  assert.deepEqual(zoek.search("--").rows, []);
});
