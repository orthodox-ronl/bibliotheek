/**
 * Inzet: beginnoten van S, A, T en B uit een from-ir MusicXML, als frequenties.
 * Zonder DOM, zodat Node de functies kan testen (tests/inzet-kern.test.mjs).
 * Opbouw van from-ir: deel 1 = S (voice 1) en A (voice 2), deel 2 = T en B.
 * Contract: docs/specs/schermpartituur.md §2.4.
 */
(function (root) {
  var STEMMEN = ["S", "A", "T", "B"];
  var HALVE_TONEN = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  var TOON_SECONDEN = 0.5;
  var PAUZE_SECONDEN = 0.1;

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

  var api = {
    beginnoten: beginnoten,
    frequentie: frequentie,
    speelschema: speelschema,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.__inzetKern = api;
})(typeof window !== "undefined" ? window : globalThis);
