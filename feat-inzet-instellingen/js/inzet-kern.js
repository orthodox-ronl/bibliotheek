/**
 * Inzet: beginnoten van S, A, T en B uit een from-ir MusicXML, als frequenties,
 * plus de keuzes van de koorleider (hoger/lager, algemeen of per stuk).
 * Zonder DOM, zodat Node de functies kan testen (tests/inzet-kern.test.mjs).
 * Opbouw van from-ir: deel 1 = S (voice 1) en A (voice 2), deel 2 = T en B.
 * Contract: docs/specs/schermpartituur.md §2.4.
 */
(function (root) {
  var STEMMEN = ["S", "A", "T", "B"];
  var HALVE_TONEN = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  var TOON_SECONDEN = 0.5;
  var PAUZE_SECONDEN = 0.1;
  var MAX_HALVE_TONEN = 12;
  var NOOTNAMEN = ["C", "Des", "D", "Es", "E", "F", "Fis", "G", "As", "A", "Bes", "B"];

  function tagText(xml, tag) {
    var m = xml.match(new RegExp("<" + tag + ">\\s*([^<]*?)\\s*</" + tag + ">"));
    return m ? m[1] : "";
  }

  /** MIDI-nummer van de eerste klinkende noot van een stem, of null. */
  function eersteNoot(part, voice) {
    var notes = part.match(/<note[\s>][\s\S]*?<\/note>/g) || [];
    for (var i = 0; i < notes.length; i++) {
      var note = notes[i];
      if ((tagText(note, "voice") || "1") !== voice) continue;
      if (note.indexOf("<pitch>") < 0) continue; /* rust */
      var step = tagText(note, "step");
      var octave = parseInt(tagText(note, "octave"), 10);
      var alter = parseInt(tagText(note, "alter") || "0", 10);
      if (!(step in HALVE_TONEN) || isNaN(octave)) return null;
      return 12 * (octave + 1) + HALVE_TONEN[step] + alter;
    }
    return null;
  }

  /** [{stem, midi}] voor S, A, T, B; null als het bestand niet zo is opgebouwd. */
  function beginnoten(xml) {
    var parts = String(xml || "").match(/<part\s+id=[\s\S]*?<\/part>/g) || [];
    if (parts.length !== 2) return null;
    var midi = [
      eersteNoot(parts[0], "1"),
      eersteNoot(parts[0], "2"),
      eersteNoot(parts[1], "1"),
      eersteNoot(parts[1], "2"),
    ];
    if (midi.indexOf(null) >= 0) return null;
    return midi.map(function (m, i) {
      return { stem: STEMMEN[i], midi: m };
    });
  }

  /** Gelijkzwevende stemming, A4 (MIDI 69) = 440 Hz. */
  function frequentie(midi) {
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  /** Wanneer elke toon klinkt, in seconden vanaf de start. */
  function speelschema(noten) {
    return noten.map(function (noot, i) {
      return {
        stem: noot.stem,
        frequentie: frequentie(noot.midi),
        start: i * (TOON_SECONDEN + PAUZE_SECONDEN),
        duur: TOON_SECONDEN,
      };
    });
  }

  /** Toonklasse (0 = C) van do, uit de voortekens (majeur); null zonder. */
  function doUitKruizen(xml) {
    var kruizen = parseInt(tagText(String(xml || ""), "fifths"), 10);
    return isNaN(kruizen) ? null : (((kruizen * 7) % 12) + 12) % 12;
  }

  function nootnaam(midi) {
    return NOOTNAMEN[((midi % 12) + 12) % 12];
  }

  function grens(n) {
    n = Math.round(Number(n) || 0);
    return Math.max(-MAX_HALVE_TONEN, Math.min(MAX_HALVE_TONEN, n));
  }

  /** Verschuif alle noten; optioneel tenor en bas een octaaf extra omhoog. */
  function verschuif(noten, halveTonen, tbHoger) {
    return noten.map(function (noot) {
      var octaaf = tbHoger && (noot.stem === "T" || noot.stem === "B") ? 12 : 0;
      return { stem: noot.stem, midi: noot.midi + halveTonen + octaaf };
    });
  }

  function grootte(n) {
    var a = Math.abs(n);
    return (Math.floor(a / 2) || "") + (a % 2 ? "\u00bd" : "");
  }

  /** Voor in het paneel: "1\u00bd toon lager". */
  function verschuivingTekst(n) {
    if (!n) return "zoals genoteerd";
    var a = Math.abs(n);
    var hoeveel =
      a === 1 ? "een halve toon" : grootte(n) + (a % 2 === 0 && a > 2 ? " tonen" : " toon");
    return hoeveel + (n > 0 ? " hoger" : " lager");
  }

  /** Voor op de knop, in hele tonen: "+\u00bd", "\u22121". */
  function kortTeken(n) {
    if (!n) return "0";
    return (n > 0 ? "+" : "\u2212") + grootte(n);
  }

  /** Instellingen uit opslag opschonen: {algemeen, tbHoger, eigen: {id: n}}. */
  function instellingen(ruw) {
    var uit = { algemeen: 0, tbHoger: false, eigen: {} };
    if (!ruw || typeof ruw !== "object") return uit;
    uit.algemeen = grens(ruw.algemeen);
    uit.tbHoger = ruw.tbHoger === true;
    Object.keys(ruw.eigen || {}).forEach(function (id) {
      uit.eigen[id] = grens(ruw.eigen[id]);
    });
    return uit;
  }

  function heeftEigen(stand, id) {
    return Object.prototype.hasOwnProperty.call(stand.eigen, id);
  }

  function geldend(stand, id) {
    return heeftEigen(stand, id) ? stand.eigen[id] : stand.algemeen;
  }

  /** Eigen begint op de algemene waarde; terug naar algemeen wist de eigen. */
  function zetEigen(stand, id, aan) {
    if (!aan) delete stand.eigen[id];
    else if (!heeftEigen(stand, id)) stand.eigen[id] = stand.algemeen;
  }

  /** Een halve toon hoger of lager, voor het regime dat bij dit stuk geldt. */
  function stap(stand, id, delta) {
    if (heeftEigen(stand, id)) stand.eigen[id] = grens(stand.eigen[id] + delta);
    else stand.algemeen = grens(stand.algemeen + delta);
  }

  var api = {
    doUitKruizen: doUitKruizen,
    nootnaam: nootnaam,
    verschuif: verschuif,
    verschuivingTekst: verschuivingTekst,
    kortTeken: kortTeken,
    instellingen: instellingen,
    heeftEigen: heeftEigen,
    geldend: geldend,
    zetEigen: zetEigen,
    stap: stap,
    beginnoten: beginnoten,
    frequentie: frequentie,
    speelschema: speelschema,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.__inzetKern = api;
})(typeof window !== "undefined" ? window : globalThis);
