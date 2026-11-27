/**
 * Zoekkern voor de bibliotheek: normaliseren, zoekterm lezen en scoren.
 *
 * Geen DOM-code, zodat dezelfde logica in de browser (catalogus-zoek.js)
 * en in Node-tests (scripts/zoek-kern.test.mjs) draait.
 *
 * Regels (zie handleiding "Zoeken"):
 * - Hoofdletters, accenten/trema's, leestekens en _ tellen niet mee.
 * - Streepjes binnen een woord ("eeu-wi-ge", "Drie-eenheid") tellen niet
 *   mee: de zoekterm wordt ook zonder streepjes gezocht. In de index staat
 *   een samengesteld woord zowel los als aaneen (zie build_zoek_index.py).
 * - Een zoekwoord matcht vanaf het begin van een woord ("eeuw" vindt "eeuwige").
 * - Eerst komen de uitvoeringsvormen waarin alle woorden voorkomen; daarna
 *   die met zoveel mogelijk woorden. Binnen gelijke aantallen wint wie de
 *   woorden in de gezochte volgorde (en aaneen) bevat, daarna wie ze in de
 *   titel of het id heeft.
 */
(function (global, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    global.CatalogusZoekKern = api;
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /** Vanaf zoveel letters wordt een zoekwoord ook als begin van een synoniem gezocht. */
  const SYNONYM_PREFIX_MIN = 3;
  /** Woorden van hoogstens zoveel letters ("de", "u") tellen niet als enige reden voor een deeltreffer. */
  const KORT_WOORD = 2;
  /** Bovengrens aan combinaties van synoniemvarianten die als frase worden geprobeerd. */
  const MAX_FRASEN = 24;
  const GEWICHT = { titel: 3, id: 2, tekst: 1 };

  const COMPOUND = /[\p{L}\p{N}_]+(?:-[\p{L}\p{N}_]+)+/gu;
  const NIET_WOORD = /[^\p{L}\p{N}_\s]+/gu;

  /** Kleine letters, zonder accenten of trema's (mysteriën -> mysterien). */
  function stripAccents(s) {
    return String(s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  /** "drie-eenheid" -> "drie eenheid drieeenheid" (los én aaneen). */
  function expandCompounds(s) {
    return s.replace(COMPOUND, function (m) {
      const parts = m.split("-");
      return parts.join(" ") + " " + parts.join("");
    });
  }

  /** Zelfde normalisatie als scripts/build_zoek_index.py (normalize_text). */
  function norm(s, synonyms) {
    const map = synonyms || {};
    return expandCompounds(stripAccents(s).replace(/_/g, ""))
      .replace(NIET_WOORD, " ")
      .split(/\s+/)
      .filter(Boolean)
      .map(function (token) {
        return map[token] || token;
      })
      .join(" ");
  }

  function createSearcher(entries, synonymsIn) {
    const synonyms = synonymsIn && typeof synonymsIn === "object" ? synonymsIn : {};

    /** Exacte synoniemen; vanaf 3 letters ook begin van een synoniemsleutel of -waarde. */
    function expandToken(token) {
      if (!token) return [];
      const exact = synonyms[token];
      if (exact) return [exact];
      const alts = [token];
      if (token.length < SYNONYM_PREFIX_MIN) return alts;
      const seen = Object.create(null);
      seen[token] = true;
      Object.keys(synonyms).forEach(function (key) {
        const canon = synonyms[key];
        if (!canon) return;
        if (key.startsWith(token) || canon.startsWith(token)) {
          if (!seen[canon]) {
            seen[canon] = true;
            alts.push(canon);
          }
        }
      });
      return alts;
    }

    /**
     * Zoekterm -> lijst zoekwoorden. Elk zoekwoord heeft alternatieven:
     * "eeu-wi-ge" -> ["eeuwige", "eeu wi ge"]; "alleluja" -> ["alleluia"].
     */
    function queryTokens(raw) {
      const cleaned = stripAccents(raw)
        .replace(/_/g, "")
        .replace(/[^\p{L}\p{N}_\s-]+/gu, " ")
        .replace(/(^|\s)-+/g, "$1")
        .replace(/-+(?=\s|$)/g, "");
      const tokens = [];
      cleaned
        .split(/\s+/)
        .filter(Boolean)
        .forEach(function (t) {
          const parts = t.split("-").filter(Boolean);
          if (!parts.length) return;
          const joined = parts.join("");
          const forms = [joined];
          if (parts.length > 1) forms.push(parts.join(" "));
          const alts = [];
          const seen = Object.create(null);
          forms.forEach(function (f) {
            expandToken(f).forEach(function (a) {
              if (!seen[a]) {
                seen[a] = true;
                alts.push(a);
              }
            });
          });
          tokens.push({ alts: alts, kort: joined.length <= KORT_WOORD });
        });
      return tokens;
    }

    function phrases(tokens) {
      let result = [[]];
      for (let i = 0; i < tokens.length; i++) {
        const next = [];
        for (let p = 0; p < result.length; p++) {
          for (let a = 0; a < tokens[i].alts.length; a++) {
            next.push(result[p].concat([tokens[i].alts[a]]));
          }
        }
        result = next;
        if (result.length > MAX_FRASEN) {
          result = result.slice(0, MAX_FRASEN);
        }
      }
      return result.map(function (words) {
        return words.join(" ");
      });
    }

    const prepared = (entries || []).map(function (entry) {
      return {
        entry: entry,
        titel: " " + norm((entry.title || "") + " " + (entry.linkTitle || ""), synonyms) + " ",
        id: " " + norm(String(entry.id || "").replace(/[/-]+/g, " "), synonyms) + " ",
        tekst: " " + norm(entry.text || "", synonyms) + " ",
      };
    });

    function search(rawQ) {
      const tokens = queryTokens(rawQ);
      const n = tokens.length;
      if (!n) return { rows: [], tokenCount: 0, completeCount: 0 };
      const frasen = phrases(tokens);
      const heeftLang = tokens.some(function (t) {
        return !t.kort;
      });
      const minimum = n === 1 ? 1 : Math.max(1, Math.ceil(n / 2));
      const rows = [];

      prepared.forEach(function (p) {
        let hits = 0;
        let langeHits = 0;
        let gewicht = 0;
        const posities = [];
        tokens.forEach(function (tok) {
          let best = 0;
          let pos = -1;
          tok.alts.forEach(function (alt) {
            const needle = " " + alt;
            if (p.titel.includes(needle)) best = Math.max(best, GEWICHT.titel);
            if (p.id.includes(needle)) best = Math.max(best, GEWICHT.id);
            const at = p.tekst.indexOf(needle);
            if (at >= 0) {
              best = Math.max(best, GEWICHT.tekst);
              if (pos < 0 || at < pos) pos = at;
            }
          });
          if (best) {
            hits += 1;
            if (!tok.kort) langeHits += 1;
            gewicht += best;
          }
          posities.push(pos);
        });
        const complete = hits === n;
        if (!complete) {
          if (hits < minimum) return;
          if (heeftLang && langeHits < 1) return;
        }
        let volgorde = 0;
        for (let k = 0; k + 1 < posities.length; k++) {
          if (posities[k] >= 0 && posities[k + 1] > posities[k]) volgorde += 1;
        }
        const frase = frasen.some(function (ph) {
          const needle = " " + ph;
          return (
            p.tekst.includes(needle) || p.titel.includes(needle) || p.id.includes(needle)
          );
        })
          ? 1
          : 0;
        rows.push({
          entry: p.entry,
          complete: complete,
          hits: hits,
          frase: frase,
          volgorde: volgorde,
          gewicht: gewicht,
        });
      });

      rows.sort(function (a, b) {
        return (
          b.hits - a.hits ||
          b.frase - a.frase ||
          b.volgorde - a.volgorde ||
          b.gewicht - a.gewicht ||
          String(a.entry.id).localeCompare(String(b.entry.id))
        );
      });
      const completeCount = rows.filter(function (r) {
        return r.complete;
      }).length;
      return { rows: rows, tokenCount: n, completeCount: completeCount };
    }

    return { search: search };
  }

  return { createSearcher: createSearcher, norm: norm, stripAccents: stripAccents };
});
