/**
 * Schermpartituur via OpenSheetMusicDisplay.
 * Bron: sibling ``*.from-ir.musicxml`` (Score-IR → MusicXML).
 *
 * S8-recite (A1): ``<notehead>none</notehead>`` in from-ir is een marker,
 * geen OSMD-native hide. Na render verbergt deze adapter spacer-koppen /
 * ledgers / lyric-streepjes (productgedrag; zie schermpartituur §5.1).
 *
 * Cues op eerste noot, gedeelde hoogte per systeem. Maatbreedte: maten met
 * cues krijgen ruimte van maten zonder cue (wit rechts), zodat cues binnen
 * de maatstrepen blijven — zonder systeemovergangen te forceren. Daarna noten
 * + lyrics centreren in die (vaak verbrede) maten; cues blijven staan.
 */
(function () {
  var OSMD_SRC =
    "https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.3/build/opensheetmusicdisplay.min.js";
  var FONT_CSS =
    "https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap";
  var FONT_FAMILY = "Source Sans 3";
  var CUE_GAP_PX = 10;
  var CUE_LINE_PX = 22;

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (
        window.opensheetmusicdisplay &&
        window.opensheetmusicdisplay.OpenSheetMusicDisplay
      ) {
        resolve();
        return;
      }
      var existing = document.querySelector("script[data-osmd-cdn]");
      if (existing) {
        existing.addEventListener("load", function () {
          resolve();
        });
        existing.addEventListener("error", function () {
          reject(new Error("OSMD-script laden mislukt"));
        });
        return;
      }
      var s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.setAttribute("data-osmd-cdn", "1");
      s.onload = function () {
        resolve();
      };
      s.onerror = function () {
        reject(new Error("OSMD-script laden mislukt"));
      };
      document.head.appendChild(s);
    });
  }

  function loadScoreFont() {
    return new Promise(function (resolve) {
      if (!document.querySelector('link[data-osmd-font]')) {
        var link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = FONT_CSS;
        link.setAttribute("data-osmd-font", "1");
        document.head.appendChild(link);
      }
      if (document.fonts && document.fonts.load) {
        document.fonts
          .load('13px "' + FONT_FAMILY + '"')
          .then(function () {
            resolve();
          })
          .catch(function () {
            resolve();
          });
        return;
      }
      setTimeout(resolve, 120);
    });
  }

  function setStatus(host, text) {
    var el = host.querySelector(".osmd-status");
    if (el) {
      el.textContent = text;
    }
  }

  function cueTextsPerMeasure(xmlText) {
    var doc = new DOMParser().parseFromString(xmlText, "application/xml");
    var part = doc.querySelector("part");
    if (!part) {
      return [];
    }
    return Array.prototype.map.call(
      part.querySelectorAll(":scope > measure"),
      function (m) {
        var w = m.querySelector("direction-type words");
        return w ? String(w.textContent || "").trim() : null;
      }
    );
  }

  function cueLines(text) {
    return String(text || "")
      .split(/\r?\n/)
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
  }

  function maxCueLineLen(text) {
    var lines = cueLines(text);
    var max = 0;
    for (var i = 0; i < lines.length; i += 1) {
      if (lines[i].length > max) {
        max = lines[i].length;
      }
    }
    return max;
  }

  async function fetchXml(src) {
    var url = src;
    if (url.indexOf("?") < 0) {
      url = url + "?v=1";
    }
    var r = await fetch(url, { cache: "no-store" });
    if (!r.ok) {
      throw new Error("MusicXML HTTP " + r.status);
    }
    return r.text();
  }

  function xmlLocalTag(el) {
    if (!el) {
      return "";
    }
    if (el.localName) {
      return String(el.localName).toLowerCase();
    }
    return String(el.tagName || "").replace(/^[^:]+:/, "").toLowerCase();
  }

  function textContentTrim(el) {
    return String(el.textContent || "").trim();
  }

  function measureLayout(mount) {
    var raw = Array.prototype.map.call(
      mount.querySelectorAll(".vf-measure"),
      function (m) {
        var b = m.getBBox();
        var n0 = m.querySelector(".vf-stavenote");
        var nb = n0 ? n0.getBBox() : null;
        return {
          x: b.x,
          y: b.y,
          w: b.width,
          firstX: nb ? nb.x : b.x + 20,
        };
      }
    );
    raw.sort(function (a, b) {
      return a.y - b.y || a.x - b.x;
    });
    var systems = [];
    for (var i = 0; i < raw.length; i += 1) {
      var m = raw[i];
      var sys = systems[systems.length - 1];
      if (!sys || m.y - sys.lastY > 150) {
        systems.push({ lastY: m.y, ms: [m] });
      } else {
        sys.ms.push(m);
        sys.lastY = m.y;
      }
    }
    var firstXs = [];
    var staffTops = [];
    var lefts = [];
    var rights = [];
    for (var s = 0; s < systems.length; s += 1) {
      var ms = systems[s].ms;
      var minY = ms[0].y;
      for (var j = 1; j < ms.length; j += 1) {
        if (ms[j].y < minY) {
          minY = ms[j].y;
        }
      }
      var treble = ms.filter(function (mm) {
        return mm.y <= minY + 55;
      });
      treble.sort(function (a, b) {
        return a.x - b.x;
      });
      var prevX = null;
      for (var t = 0; t < treble.length; t += 1) {
        if (prevX !== null && Math.abs(treble[t].x - prevX) < 8) {
          continue;
        }
        firstXs.push(treble[t].firstX);
        staffTops.push(minY);
        lefts.push(treble[t].x);
        rights.push(treble[t].x + treble[t].w);
        prevX = treble[t].x;
      }
    }
    return {
      firstXs: firstXs,
      staffTops: staffTops,
      lefts: lefts,
      rights: rights,
    };
  }

  /**
   * Startfactoren op basis van wrap-regels (langste regel), niet op één
   * lange regel — maatbreedte blijft het «twee-regels»-uitgangspunt.
   */
  function applyInitialWidthFactors(osmd, xmlText) {
    var cues = cueTextsPerMeasure(xmlText);
    var sms = osmd.Sheet && osmd.Sheet.SourceMeasures;
    if (!sms) {
      return;
    }
    for (var i = 0; i < sms.length; i += 1) {
      var f = 0.9;
      if (cues[i]) {
        var len = maxCueLineLen(cues[i]);
        f = Math.min(1.28, 1.0 + len * 0.012);
      }
      sms[i].widthFactor = f;
      sms[i].WidthFactor = f;
    }
  }

  function measureTextWidth(svg, sampleEl, text) {
    var probe = sampleEl.cloneNode(false);
    probe.textContent = text;
    probe.setAttribute("x", "0");
    probe.setAttribute("y", "0");
    svg.appendChild(probe);
    var w = 0;
    try {
      w = probe.getBBox().width;
    } catch (e) {
      w = text.length * 7.5;
    }
    svg.removeChild(probe);
    return w;
  }

  /**
   * Na vaste maatbreedte: twee-regelige cue → één regel als die nóg past.
   * Past hij niet: wrap laten staan (maat was daarop berekend).
   */
  function collapseWrappedCuesIfTheyFit(mount, xmlText) {
    var svg = mount.querySelector("svg");
    if (!svg) {
      return;
    }
    var cues = cueTextsPerMeasure(xmlText);
    var layout = measureLayout(mount);
    var allText = Array.prototype.slice.call(mount.querySelectorAll("text"));

    for (var mi = 0; mi < cues.length && mi < layout.rights.length; mi += 1) {
      if (!cues[mi]) {
        continue;
      }
      var lines = cueLines(cues[mi]);
      if (lines.length < 2) {
        continue;
      }
      var single = lines.join(" ");
      var staffTop = layout.staffTops[mi];
      var targetX = Math.max(layout.firstXs[mi], layout.lefts[mi] + 4);
      var maxW = layout.rights[mi] - targetX - 8;
      if (!(maxW > 20)) {
        continue;
      }

      var tops = [];
      var bottoms = [];
      for (var i = 0; i < allText.length; i += 1) {
        var el = allText[i];
        var s = textContentTrim(el);
        var b = el.getBBox();
        if (b.y > staffTop + 8 || b.y < staffTop - 160) {
          continue;
        }
        if (s === lines[0]) {
          tops.push(el);
        } else if (lines.indexOf(s) > 0) {
          bottoms.push(el);
        }
      }
      if (!tops.length || !bottoms.length) {
        continue;
      }

      var sample = tops[0];
      var needW = measureTextWidth(svg, sample, single);
      if (needW > maxW) {
        continue; // past niet → twee regels laten
      }

      // Past wel → één regel op de onderste cue-hoogte (niet de bovenste).
      var keeper = bottoms[0];
      for (var bi = 1; bi < bottoms.length; bi += 1) {
        if (bottoms[bi].getBBox().y > keeper.getBBox().y) {
          keeper = bottoms[bi];
        }
      }
      keeper.textContent = single;
      for (var k = 0; k < allText.length; k += 1) {
        var el3 = allText[k];
        if (el3 === keeper || !el3.parentNode) {
          continue;
        }
        var s3 = textContentTrim(el3);
        var b3 = el3.getBBox();
        if (b3.y > staffTop + 8 || b3.y < staffTop - 160) {
          continue;
        }
        if (
          s3 === single ||
          s3 === lines[0] ||
          lines.indexOf(s3) > 0
        ) {
          el3.parentNode.removeChild(el3);
        }
      }

      var yAttr = parseFloat(keeper.getAttribute("y"));
      var box = keeper.getBBox();
      if (isFinite(yAttr)) {
        var targetBottom = staffTop - CUE_GAP_PX;
        keeper.setAttribute("x", String(targetX));
        keeper.setAttribute(
          "y",
          String(yAttr + (targetBottom - (box.y + box.height)))
        );
      }
    }
  }

  function cueExtent(mount, cueText, staffTop) {
    var lines = cueLines(cueText);
    var matchTexts =
      lines.length === 1 ? [cueText] : lines;
    var allText = mount.querySelectorAll("text");
    var left = Infinity;
    var right = -Infinity;
    for (var li = 0; li < matchTexts.length; li += 1) {
      for (var i = 0; i < allText.length; i += 1) {
        if (textContentTrim(allText[i]) !== matchTexts[li]) {
          continue;
        }
        var b = allText[i].getBBox();
        if (b.y > staffTop + 8 || b.y < staffTop - 160) {
          continue;
        }
        left = Math.min(left, b.x);
        right = Math.max(right, b.x + b.width);
      }
    }
    if (!(right > left)) {
      return null;
    }
    return { left: left, right: right };
  }

  /**
   * Cues die buiten de maat vallen → die maat breder, maten zonder cue
   * op hetzelfde systeem smaller. Geen middeling naar 1 (dat maakt bumps ongedaan).
   */
  function redistributeForOverflow(osmd, mount, xmlText) {
    var cues = cueTextsPerMeasure(xmlText);
    var layout = measureLayout(mount);
    var sms = osmd.Sheet && osmd.Sheet.SourceMeasures;
    if (!sms || !layout.rights.length) {
      return false;
    }
    var bumped = false;
    var pad = 8;

    for (var mi = 0; mi < cues.length && mi < layout.rights.length; mi += 1) {
      if (!cues[mi]) {
        continue;
      }
      var ext = cueExtent(mount, cues[mi], layout.staffTops[mi]);
      if (!ext) {
        continue;
      }
      var mRight = layout.rights[mi];
      var mLeft = layout.lefts[mi];
      var overflow = ext.right - (mRight - pad);
      if (overflow <= 0) {
        continue;
      }
      var mWidth = Math.max(mRight - mLeft, 50);
      var grow = Math.min(1.28, 1 + overflow / mWidth);
      var cur = sms[mi].widthFactor || 1;
      var next = Math.min(1.4, cur * Math.max(grow, 1.1));
      if (next > cur + 0.03) {
        sms[mi].widthFactor = next;
        sms[mi].WidthFactor = next;
        bumped = true;
      }
      var st = layout.staffTops[mi];
      for (var j = 0; j < layout.staffTops.length; j += 1) {
        if (j === mi || cues[j]) {
          continue;
        }
        if (Math.abs(layout.staffTops[j] - st) > 40) {
          continue;
        }
        var sj = sms[j].widthFactor || 1;
        var reduced = Math.max(0.72, sj * 0.9);
        if (reduced < sj - 0.02) {
          sms[j].widthFactor = reduced;
          sms[j].WidthFactor = reduced;
          bumped = true;
        }
      }
    }
    return bumped;
  }

  function layoutCues(mount, xmlText) {
    var cues = cueTextsPerMeasure(xmlText);
    var layout = measureLayout(mount);
    var firstXs = layout.firstXs;
    var staffTops = layout.staffTops;
    var lefts = layout.lefts;
    if (!cues.length || !firstXs.length) {
      return;
    }
    var allText = Array.prototype.slice.call(mount.querySelectorAll("text"));

    var maxLinesByStaffTop = {};
    for (var mi0 = 0; mi0 < cues.length && mi0 < staffTops.length; mi0 += 1) {
      if (!cues[mi0]) {
        continue;
      }
      var n0 = cueLines(cues[mi0]).length;
      var key0 = String(Math.round(staffTops[mi0]));
      if (!maxLinesByStaffTop[key0] || n0 > maxLinesByStaffTop[key0]) {
        maxLinesByStaffTop[key0] = n0;
      }
    }

    for (var mi = 0; mi < cues.length && mi < firstXs.length; mi += 1) {
      if (!cues[mi]) {
        continue;
      }
      var lines = cueLines(cues[mi]);
      if (!lines.length) {
        continue;
      }
      var targetX = Math.max(firstXs[mi], lefts[mi] + 4);
      var staffTop = staffTops[mi];
      var maxLines = maxLinesByStaffTop[String(Math.round(staffTop))] || 1;
      for (var li = 0; li < lines.length; li += 1) {
        // Eén-regelcue: altijd op de onderste cue-rij (zelfde hoogte als
        // de laatste regel van een wrap), niet op de bovenste.
        var row = lines.length === 1 ? maxLines - 1 : li;
        var targetGlyphBottom =
          staffTop - CUE_GAP_PX - (maxLines - 1 - row) * CUE_LINE_PX;
        for (var j = 0; j < allText.length; j += 1) {
          var el = allText[j];
          if (textContentTrim(el) !== lines[li]) {
            continue;
          }
          var box = el.getBBox();
          if (box.y > staffTop + 8 || box.y < staffTop - 160) {
            continue;
          }
          var yAttr = parseFloat(el.getAttribute("y"));
          if (!isFinite(yAttr)) {
            continue;
          }
          el.setAttribute("x", String(targetX));
          el.setAttribute(
            "y",
            String(yAttr + (targetGlyphBottom - (box.y + box.height)))
          );
        }
      }
    }

    resolveCueOverlaps(mount, cues, layout);
  }

  /**
   * Na vaste maatbreedte (vaak verbreed voor cues): schuif noten+lyrics
   * horizontaal naar het midden van de maat. Cues blijven staan.
   */
  function centerMeasureContents(mount) {
    var raw = Array.prototype.map.call(
      mount.querySelectorAll(".vf-measure"),
      function (m) {
        var b = m.getBBox();
        var clef = m.querySelector(".vf-clef");
        var key = m.querySelector(".vf-keysignature");
        var musicStart = b.x + 6;
        if (clef) {
          var cb = clef.getBBox();
          musicStart = Math.max(musicStart, cb.x + cb.width + 4);
        }
        if (key) {
          var kb = key.getBBox();
          musicStart = Math.max(musicStart, kb.x + kb.width + 4);
        }
        return {
          el: m,
          x: b.x,
          y: b.y,
          w: b.width,
          musicStart: musicStart,
          right: b.x + b.width,
        };
      }
    );
    raw.sort(function (a, b) {
      return a.y - b.y || a.x - b.x;
    });
    var systems = [];
    for (var i = 0; i < raw.length; i += 1) {
      var m = raw[i];
      var sys = systems[systems.length - 1];
      if (!sys || m.y - sys.lastY > 150) {
        systems.push({ lastY: m.y, ms: [m] });
      } else {
        sys.ms.push(m);
        sys.lastY = m.y;
      }
    }
    var lyricGs = Array.prototype.slice.call(
      mount.querySelectorAll("g.vf-text.lyrics, g.vf-text.dash")
    );

    for (var s = 0; s < systems.length; s += 1) {
      var ms = systems[s].ms;
      var minY = ms[0].y;
      var maxY = ms[0].y;
      for (var j = 1; j < ms.length; j += 1) {
        if (ms[j].y < minY) {
          minY = ms[j].y;
        }
        if (ms[j].y > maxY) {
          maxY = ms[j].y;
        }
      }
      var lyricY0 = minY - 20;
      var lyricY1 = maxY + 220;
      var treble = ms
        .filter(function (mm) {
          return mm.y <= minY + 55;
        })
        .sort(function (a, b) {
          return a.x - b.x;
        });
      var prevX = null;
      for (var t = 0; t < treble.length; t += 1) {
        if (prevX !== null && Math.abs(treble[t].x - prevX) < 8) {
          continue;
        }
        var col = ms.filter(function (mm) {
          return Math.abs(mm.x - treble[t].x) < 8;
        });
        var left = treble[t].musicStart;
        var right = treble[t].right - 8;
        var cMin = Infinity;
        var cMax = -Infinity;
        for (var c = 0; c < col.length; c += 1) {
          var notes = col[c].el.querySelectorAll(".vf-stavenote");
          for (var n = 0; n < notes.length; n += 1) {
            var bb = notes[n].getBBox();
            cMin = Math.min(cMin, bb.x);
            cMax = Math.max(cMax, bb.x + bb.width);
          }
        }
        if (!(cMax > cMin)) {
          prevX = treble[t].x;
          continue;
        }
        var padL = cMin - left;
        var padR = right - cMax;
        var dx = (padR - padL) / 2;
        if (padR + padL < 24 || Math.abs(dx) < 6) {
          prevX = treble[t].x;
          continue;
        }
        if (cMin + dx < left) {
          dx = left - cMin;
        }
        if (cMax + dx > right) {
          dx = right - cMax;
        }
        if (Math.abs(dx) < 6) {
          prevX = treble[t].x;
          continue;
        }
        for (var c2 = 0; c2 < col.length; c2 += 1) {
          var moveEls = col[c2].el.querySelectorAll(
            ".vf-stavenote, .vf-ledgers"
          );
          for (var e = 0; e < moveEls.length; e += 1) {
            var el = moveEls[e];
            if (el.getAttribute("data-osmd-center")) {
              continue;
            }
            var prev = el.getAttribute("transform") || "";
            el.setAttribute(
              "transform",
              (prev ? prev + " " : "") + "translate(" + dx + " 0)"
            );
            el.setAttribute("data-osmd-center", "1");
          }
        }
        for (var li = 0; li < lyricGs.length; li += 1) {
          var g = lyricGs[li];
          if (g.getAttribute("data-osmd-center")) {
            continue;
          }
          var gb = g.getBBox();
          var mid = gb.x + gb.width / 2;
          var cy = gb.y + gb.height / 2;
          if (cy < lyricY0 || cy > lyricY1) {
            continue;
          }
          if (mid < treble[t].x || mid >= treble[t].right) {
            continue;
          }
          var gPrev = g.getAttribute("transform") || "";
          g.setAttribute(
            "transform",
            (gPrev ? gPrev + " " : "") + "translate(" + dx + " 0)"
          );
          g.setAttribute("data-osmd-center", "1");
        }
        prevX = treble[t].x;
      }
    }
  }

  function resolveCueOverlaps(mount, cues, layout) {
    var allText = Array.prototype.slice.call(mount.querySelectorAll("text"));
    var placed = [];
    for (var mi = 0; mi < cues.length; mi += 1) {
      if (!cues[mi] || mi >= layout.staffTops.length) {
        continue;
      }
      var lines = cueLines(cues[mi]);
      if (!lines.length) {
        continue;
      }
      var staffTop = layout.staffTops[mi];
      var els = allText.filter(function (t) {
        if (textContentTrim(t) !== lines[0]) {
          return false;
        }
        var b = t.getBBox();
        return b.y <= staffTop + 8 && b.y >= staffTop - 160;
      });
      if (!els.length) {
        continue;
      }
      var el = els[0];
      var box = el.getBBox();
      var x0 = box.x;
      for (var p = 0; p < placed.length; p += 1) {
        var prev = placed[p];
        if (Math.abs(prev.staffTop - staffTop) > 40) {
          continue;
        }
        if (
          x0 < prev.right + 8 &&
          box.y < prev.bottom + 4 &&
          box.y + box.height > prev.top - 4
        ) {
          x0 = prev.right + 8;
        }
      }
      var maxX = layout.rights[mi] - 8 - box.width;
      if (maxX < layout.lefts[mi] + 4) {
        maxX = layout.lefts[mi] + 4;
      }
      if (x0 > maxX) {
        x0 = maxX;
      }
      var dx = x0 - box.x;
      if (Math.abs(dx) > 0.5) {
        for (var li = 0; li < lines.length; li += 1) {
          for (var j = 0; j < allText.length; j += 1) {
            var t = allText[j];
            if (textContentTrim(t) !== lines[li]) {
              continue;
            }
            var tb = t.getBBox();
            if (tb.y > staffTop + 8 || tb.y < staffTop - 160) {
              continue;
            }
            var xa = parseFloat(t.getAttribute("x"));
            if (!isFinite(xa)) {
              continue;
            }
            t.setAttribute("x", String(xa + dx));
          }
        }
        box = el.getBBox();
      }
      placed.push({
        staffTop: staffTop,
        right: box.x + box.width,
        top: box.y,
        bottom: box.y + box.height,
      });
    }
  }

  /**
   * MusicXML ``<ending number="1,2">`` → label per maatnummer.
   * OSMD 1.9 leest komma-lijsten als alleen het eerste cijfer (volta «1»
   * i.p.v. «1,2»); corrigeer de getekende labels na render.
   */
  function endingLabelByMeasureNumber(xmlText) {
    var doc = new DOMParser().parseFromString(xmlText, "application/xml");
    var part = doc.querySelector("part");
    var map = {};
    if (!part) {
      return map;
    }
    Array.prototype.forEach.call(
      part.querySelectorAll(":scope > measure"),
      function (m) {
        var num = m.getAttribute("number");
        if (!num) {
          return;
        }
        var start = m.querySelector('barline[location="left"] ending');
        var stop = m.querySelector('barline[location="right"] ending');
        var ending = start || stop;
        if (!ending) {
          return;
        }
        var label = ending.getAttribute("number");
        if (label) {
          map[String(num)] = String(label).trim();
        }
      }
    );
    return map;
  }

  function noteheadKindFromXmlNote(noteEl) {
    var nh = noteEl.querySelector("notehead");
    if (!nh) {
      return "normal";
    }
    return textContentTrim(nh).toLowerCase();
  }

  /**
   * S8 per part/maat: één slot per metrische positie (v1 + v2), volgorde =
   * chronologische MusicXML-slots (niet DOM-volgorde van OSMD).
   */
  function s8PrintSlotsByPartMeasure(xmlText) {
    var doc = new DOMParser().parseFromString(xmlText, "application/xml");
    var parts = Array.prototype.slice.call(doc.querySelectorAll("part"));
    return parts.map(function (part) {
      var byNum = {};
      var measures = [];
      Array.prototype.forEach.call(part.children, function (ch) {
        if (xmlLocalTag(ch) === "measure") {
          measures.push(ch);
        }
      });
      Array.prototype.forEach.call(measures, function (measure, mi) {
        var num = measure.getAttribute("number");
        if (!num) {
          num = String(mi + 1);
        }
        var byVoice = { 1: [], 2: [] };
        Array.prototype.forEach.call(measure.children, function (ch) {
          if (xmlLocalTag(ch) !== "note") {
            return;
          }
          if (ch.querySelector("rest")) {
            return;
          }
          if (ch.querySelector("chord")) {
            return;
          }
          var vEl = ch.querySelector("voice");
          var v = vEl ? parseInt(textContentTrim(vEl), 10) : 1;
          if (v !== 1 && v !== 2) {
            v = 1;
          }
          byVoice[v].push(noteheadKindFromXmlNote(ch));
        });
        var slots = [];
        var n = Math.max(byVoice[1].length, byVoice[2].length);
        var i;
        for (i = 0; i < n; i += 1) {
          var h1 = i < byVoice[1].length ? byVoice[1][i] : "normal";
          var h2 = i < byVoice[2].length ? byVoice[2][i] : "normal";
          var spacer = h1 === "none" || h2 === "none";
          slots.push({
            spacer: spacer,
            breve: !spacer && (h1 === "breve" || h2 === "breve"),
          });
        }
        byNum[String(num)] = slots;
      });
      return byNum;
    });
  }

  /** @deprecated alleen diagnose-compat */
  function noteheadNoneFlagsByPartMeasure(xmlText) {
    return s8PrintSlotsByPartMeasure(xmlText).map(function (byNum) {
      var out = {};
      Object.keys(byNum).forEach(function (k) {
        out[k] = byNum[k].map(function (s) {
          return s.spacer;
        });
      });
      return out;
    });
  }

  function osmdHideSvgEl(el) {
    el.setAttribute("visibility", "hidden");
    el.setAttribute("display", "none");
    el.style.visibility = "hidden";
    el.style.display = "none";
  }

  function svgElIsVisible(el) {
    var s = window.getComputedStyle(el);
    return s.display !== "none" && s.visibility !== "hidden";
  }

  function staveNoteHasVisibleNotehead(staveNoteEl) {
    var shapes = staveNoteEl.querySelectorAll(
      ".vf-note path, .vf-note circle, .vf-note ellipse, .vf-note rect, .vf-note use, .vf-notehead, path.vf-notehead, .vf-stavenote > path"
    );
    for (var i = 0; i < shapes.length; i += 1) {
      if (svgElIsVisible(shapes[i])) {
        return true;
      }
    }
    return false;
  }

  function hideStaveNoteheadGraphics(staveNoteEl) {
    staveNoteEl.setAttribute("data-osmd-spacer", "1");
    Array.prototype.forEach.call(
      staveNoteEl.querySelectorAll(".vf-stem, .vf-flag, .vf-beam"),
      osmdHideSvgEl
    );
    var note = staveNoteEl.querySelector(".vf-note");
    if (note) {
      // OSMD/VexFlow: kop vaak als path.vf-notehead naast g.vf-notehead — alles
      // onder .vf-note weg; stavenote zelf blijft voor lyric-anker / spacing.
      osmdHideSvgEl(note);
      Array.prototype.forEach.call(note.querySelectorAll("*"), osmdHideSvgEl);
    }
    Array.prototype.forEach.call(
      staveNoteEl.querySelectorAll(
        ".vf-beam, .vf-modifiers, .vf-notehead, path.vf-notehead"
      ),
      osmdHideSvgEl
    );
    Array.prototype.forEach.call(
      staveNoteEl.querySelectorAll("path, circle, ellipse, rect, use, polygon"),
      function (el) {
        if (el.closest && el.closest("text")) {
          return;
        }
        osmdHideSvgEl(el);
      }
    );
  }

  var S8_CLUSTER_X_TOL = 6;

  /**
   * OSMD tekent per part meestal eerst alle voice-1-noten, daarna voice 2
   * (zelfde volgorde als MusicXML-slots). Chunks van ``slotCount`` = één stem.
   * Betrouwbaarder dan x-clustering ná hide (spacer-bbox → 0 → kolommen schuiven).
   */
  function voiceNoteRowsFromDom(staveNoteEls, slotCount) {
    var notes = Array.prototype.slice.call(staveNoteEls);
    if (!notes.length || !slotCount) {
      return [];
    }
    if (notes.length <= slotCount) {
      return [notes];
    }
    var rows = [];
    var offset = 0;
    while (offset < notes.length) {
      rows.push(notes.slice(offset, offset + slotCount));
      offset += slotCount;
    }
    return rows;
  }

  function clusterStaveNotesBySvgX(staveNoteEls, xTol) {
    var items = [];
    for (var i = 0; i < staveNoteEls.length; i += 1) {
      var bb = staveNoteEls[i].getBBox();
      // Inclusief verborgen spacers (w≈0): anders schuift de kolom-index na hide.
      var x = bb.width > 0.5 ? bb.x + bb.width / 2 : bb.x;
      items.push({ el: staveNoteEls[i], x: x });
    }
    items.sort(function (a, b) {
      return a.x - b.x;
    });
    var clusters = [];
    for (var j = 0; j < items.length; j += 1) {
      var it = items[j];
      var last = clusters[clusters.length - 1];
      if (!last || Math.abs(it.x - last.x) > xTol) {
        clusters.push({ x: it.x, notes: [it.el] });
      } else {
        last.notes.push(it.el);
        last.x = (last.x + it.x) / 2;
      }
    }
    return clusters;
  }

  function alignClustersToSlotCount(clusters, slotCount) {
    if (!clusters.length || !slotCount) {
      return clusters;
    }
    if (clusters.length === slotCount) {
      return clusters;
    }
    if (clusters.length > slotCount) {
      return clusters.slice(0, slotCount);
    }
    return clusters;
  }

  function hideLedgersNearX(measureEl, xCenter, xTol) {
    var tol = xTol + 10;
    Array.prototype.forEach.call(
      measureEl.querySelectorAll(".vf-ledgers, .vf-ledger"),
      function (el) {
        var bb;
        try {
          bb = el.getBBox();
        } catch (e) {
          return;
        }
        var cx = bb.x + bb.width / 2;
        if (Math.abs(cx - xCenter) <= tol) {
          osmdHideSvgEl(el);
        }
      }
    );
  }

  function markBreveStaveNotes(notes) {
    for (var i = 0; i < notes.length; i += 1) {
      notes[i].setAttribute("data-osmd-breve", "1");
      Array.prototype.forEach.call(
        notes[i].querySelectorAll(".vf-stem, .vf-flag"),
        osmdHideSvgEl
      );
    }
  }

  function hideS8SlotsInMeasure(measureEl, slots, staveNoteEls) {
    if (!slots || !slots.length) {
      return;
    }
    var rows = voiceNoteRowsFromDom(staveNoteEls, slots.length);
    var usedDomRows = false;
    var ri;
    var s;
    if (rows.length && rows[0].length === slots.length) {
      usedDomRows = true;
      for (ri = 0; ri < rows.length; ri += 1) {
        var row = rows[ri];
        for (s = 0; s < slots.length && s < row.length; s += 1) {
          if (slots[s].spacer) {
            hideStaveNoteheadGraphics(row[s]);
          } else if (slots[s].breve) {
            markBreveStaveNotes([row[s]]);
          }
        }
      }
      for (s = 0; s < slots.length; s += 1) {
        if (!slots[s].spacer) {
          continue;
        }
        var sample = rows[0][s];
        if (!sample) {
          continue;
        }
        try {
          var bb = sample.getBBox();
          hideLedgersNearX(
            measureEl,
            bb.x + bb.width / 2,
            S8_CLUSTER_X_TOL
          );
        } catch (e) {
          /* ignore */
        }
      }
    }
    if (usedDomRows) {
      return;
    }
    // Fallback: x-clustering (zeldzaam als DOM-volgorde ≠ slotCount).
    var clusters = alignClustersToSlotCount(
      clusterStaveNotesBySvgX(staveNoteEls, S8_CLUSTER_X_TOL),
      slots.length
    );
    for (s = 0; s < slots.length && s < clusters.length; s += 1) {
      var slot = slots[s];
      var col = clusters[s].notes;
      var ni;
      if (slot.spacer) {
        for (ni = 0; ni < col.length; ni += 1) {
          hideStaveNoteheadGraphics(col[ni]);
        }
        hideLedgersNearX(measureEl, clusters[s].x, S8_CLUSTER_X_TOL);
      } else if (slot.breve) {
        markBreveStaveNotes(col);
      }
    }
  }

  function hideNoteheadNoneGraphics(mount, xmlText) {
    var byPart = s8PrintSlotsByPartMeasure(xmlText);
    if (!byPart.length) {
      return;
    }
    var raw = Array.prototype.map.call(
      mount.querySelectorAll(".vf-measure"),
      function (m) {
        var b = m.getBBox();
        return {
          el: m,
          id: m.getAttribute("id"),
          x: b.x,
          y: b.y,
        };
      }
    );
    raw.sort(function (a, b) {
      return a.y - b.y || a.x - b.x;
    });
    var systems = [];
    for (var i = 0; i < raw.length; i += 1) {
      var mm = raw[i];
      var sys = systems[systems.length - 1];
      if (!sys || mm.y - sys.lastY > 150) {
        systems.push({ lastY: mm.y, ms: [mm] });
      } else {
        sys.ms.push(mm);
        sys.lastY = mm.y;
      }
    }
    for (var si = 0; si < systems.length; si += 1) {
      var ms = systems[si].ms.slice();
      ms.sort(function (a, b) {
        return a.x - b.x || a.y - b.y;
      });
      var colStart = 0;
      for (var j = 1; j <= ms.length; j += 1) {
        if (j < ms.length && Math.abs(ms[j].x - ms[colStart].x) < 8) {
          continue;
        }
        var col = ms.slice(colStart, j);
        colStart = j;
        col.sort(function (a, b) {
          return a.y - b.y;
        });
        for (var pi = 0; pi < col.length && pi < byPart.length; pi += 1) {
          var measureNum = col[pi].id;
          if (!measureNum) {
            continue;
          }
          var slots = byPart[pi][String(measureNum)];
          if (!slots || !slots.length) {
            continue;
          }
          var notes = Array.prototype.slice.call(
            col[pi].el.querySelectorAll(".vf-stavenote")
          );
          hideS8SlotsInMeasure(col[pi].el, slots, notes);
        }
      }
    }
    if (xmlText.indexOf("<notehead>none</notehead>") !== -1) {
      Array.prototype.forEach.call(
        mount.querySelectorAll(
          "g.vf-text.dash, g.vf-text.lyrics line, g.vf-text.lyrics path"
        ),
        osmdHideSvgEl
      );
      Array.prototype.forEach.call(mount.querySelectorAll("text"), function (t) {
        if (String(t.textContent || "").trim() !== "-") {
          return;
        }
        osmdHideSvgEl(t);
        if (t.parentElement) {
          osmdHideSvgEl(t.parentElement);
        }
      });
      Array.prototype.forEach.call(
        mount.querySelectorAll(".vf-ledgers"),
        function (g) {
          if (g.getAttribute("data-osmd-spacer-ledger") === "1") {
            return;
          }
          var bb = g.getBBox();
          if (bb.width > 80 && bb.height < 8) {
            osmdHideSvgEl(g);
            g.setAttribute("data-osmd-spacer-ledger", "1");
          }
        }
      );
    }
  }

  function fixVoltaLabels(mount, xmlText) {
    var byNum = endingLabelByMeasureNumber(xmlText);
    var ids = Object.keys(byNum);
    if (!ids.length) {
      return;
    }
    Array.prototype.forEach.call(
      mount.querySelectorAll("g.vf-measure"),
      function (g) {
        var id = g.getAttribute("id");
        if (!id || !byNum[id]) {
          return;
        }
        var label = byNum[id];
        var first = label.split(",")[0].trim();
        Array.prototype.forEach.call(g.children, function (child) {
          var tag = child.tagName && String(child.tagName).toLowerCase();
          if (tag !== "text") {
            return;
          }
          var cur = String(child.textContent || "").trim();
          // Alleen bijknippen herstellen: OSMD toonde «1» i.p.v. «1,2».
          if (cur === first && cur !== label) {
            child.textContent = label;
          }
        });
      }
    );
  }

  function renderAndLayout(osmd, mount, xmlText) {
    osmd.render();
    fixVoltaLabels(mount, xmlText);
    layoutCues(mount, xmlText);
  }

  function finalizeOsmdPrint(mount, xmlText) {
    hideNoteheadNoneGraphics(mount, xmlText);
  }
  window.__vsaScoreOsmdFinalizePrint = finalizeOsmdPrint;

  async function renderHost(host) {
    var src = host.getAttribute("data-osmd-src");
    if (!src) {
      return;
    }
    var status = host.querySelector(".osmd-status");
    var mount = document.createElement("div");
    mount.className = "osmd-mount vsa-notation";
    host.appendChild(mount);
    try {
      await loadScoreFont();
      await loadScript(OSMD_SRC);
      var OSMD = window.opensheetmusicdisplay.OpenSheetMusicDisplay;
      var osmd = new OSMD(mount, {
        // Geen OSMD-autoResize: die hertekent zonder centreren en vecht
        // met onze handler → knipperen (links ↔ gecentreerd), vooral op
        // tablet bij adresbalk show/hide. Schalen: eigen resize hieronder.
        autoResize: false,
        backend: "svg",
        drawTitle: false,
        drawSubtitle: false,
        drawComposer: false,
        drawLyricist: false,
        drawPartNames: false,
        drawPartAbbreviations: false,
        drawMeasureNumbers: true,
        // schermpartituur §4.1 / besluit 3: voorkeur begin van elk systeem
        drawMeasureNumbersOnlyAtSystemStart: true,
        drawMetronomeMarks: false,
        drawTimeSignatures: false,
        drawCredits: false,
        defaultFontFamily: FONT_FAMILY,
        newSystemFromXML: true,
        drawingParameters: "default",
      });
      var rules = osmd.EngravingRules;
      if (rules) {
        rules.LyricsHeight = 2.55;
        rules.UnknownTextHeight = 2.35;
        rules.MinSkyBottomDistBetweenSystems = 5.0;
        rules.MinimumDistanceBetweenSystems = 15.0;
        // Geen vaste maatsoort (MusicXML senza-misura); OSMD toont anders 4/4.
        if (typeof rules.RenderTimeSignatures === "boolean") {
          rules.RenderTimeSignatures = false;
        }
        if (typeof rules.BetweenStaffDistance === "number") {
          rules.BetweenStaffDistance = Math.max(
            rules.BetweenStaffDistance || 0,
            10.0
          );
        }
        // Lettergrepen over de maatstreep: geen «wordtte-» (schermpartituur §4.3).
        // OSMD mag standaard ~3.4 eenheden overlappen in de volgende maat.
        if (typeof rules.LyricOverlapAllowedIntoNextMeasure === "number") {
          rules.LyricOverlapAllowedIntoNextMeasure = 0.4;
        }
        if (typeof rules.BetweenSyllableMinimumDistance === "number") {
          rules.BetweenSyllableMinimumDistance = Math.max(
            rules.BetweenSyllableMinimumDistance || 0,
            1.0
          );
        }
        if (typeof rules.HorizontalBetweenLyricsDistance === "number") {
          rules.HorizontalBetweenLyricsDistance = Math.max(
            rules.HorizontalBetweenLyricsDistance || 0,
            0.45
          );
        }
        if (typeof rules.LyricsUseXPaddingForLongLyrics === "boolean") {
          rules.LyricsUseXPaddingForLongLyrics = true;
        }
        if (typeof rules.LyricsXPaddingFactorForLongLyrics === "number") {
          rules.LyricsXPaddingFactorForLongLyrics = Math.max(
            rules.LyricsXPaddingFactorForLongLyrics || 0,
            1.2
          );
        }
        if (
          typeof rules.LyricsXPaddingReductionForLastNoteInMeasureCrossMeasureMidWord ===
          "number"
        ) {
          // Lager = meer ruimte vóór de maatstreep bij woordovergang.
          rules.LyricsXPaddingReductionForLastNoteInMeasureCrossMeasureMidWord = 0.4;
        }
      }
      await osmd.load(src);
      var xmlText = await fetchXml(src);
      var lastLayoutWidth = 0;
      var WIDTH_EPS = 16;

      function layoutWidth() {
        return host.clientWidth || mount.clientWidth || 0;
      }

      function fullLayout(allowRedistributePasses) {
        applyInitialWidthFactors(osmd, xmlText);
        renderAndLayout(osmd, mount, xmlText);
        var maxPass = allowRedistributePasses ? 3 : 1;
        for (var pass = 0; pass < maxPass; pass += 1) {
          if (!redistributeForOverflow(osmd, mount, xmlText)) {
            break;
          }
          renderAndLayout(osmd, mount, xmlText);
        }
        // Maatbreedtes staan vast → inklappen naar 1 regel alleen als het past.
        collapseWrappedCuesIfTheyFit(mount, xmlText);
        // Eerst centreren (lyrics + noten); daarna S8-spacers op finale x-posities.
        centerMeasureContents(mount);
        finalizeOsmdPrint(mount, xmlText);
        requestAnimationFrame(function () {
          finalizeOsmdPrint(mount, xmlText);
        });
        lastLayoutWidth = layoutWidth();
      }

      fullLayout(true);
      if (status) {
        status.remove();
      }
      var resizeTimer = null;
      function onViewportChange() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          // Alleen bij echte breedtewijziging. Hoogte-only (tablet-
          // adresbalk) opnieuw tekenen → zichtbaar knipperen links/centrum.
          var w = layoutWidth();
          if (Math.abs(w - lastLayoutWidth) < WIDTH_EPS) {
            return;
          }
          try {
            fullLayout(false);
          } catch (e) {
            console.warn("score-osmd: resize", e);
          }
        }, 200);
      }
      window.addEventListener("resize", onViewportChange);
      if (window.visualViewport) {
        window.visualViewport.addEventListener("resize", onViewportChange);
      }
    } catch (err) {
      console.error("score-osmd:", src, err);
      setStatus(
        host,
        "Partituur kon niet geladen worden. Controleer sibling .from-ir.musicxml."
      );
    }
  }

  function init() {
    var hosts = document.querySelectorAll("[data-osmd-src]");
    if (!hosts.length) {
      return;
    }
    hosts.forEach(function (host) {
      renderHost(host);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  window.__VSA_SCORE_OSMD_BUILD = "20261025-s8-a1-domrows";

  function diagnoseStaff(measures, byPart, mi, label) {
    var out = { label: label };
    if (!measures[mi] || !byPart[mi]) {
      out.missing = true;
      return out;
    }
    var id = measures[mi].getAttribute("id") || "1";
    var slots = byPart[mi][String(id)];
    if (!slots || !slots.length) {
      out.noFlags = true;
      return out;
    }
    var notes = measures[mi].querySelectorAll(".vf-stavenote");
    var rows = voiceNoteRowsFromDom(notes, slots.length);
    var keepVisible = 0;
    var spacerVisible = 0;
    var cadenceVisible = 0;
    var breveMarked = 0;
    var firstSpacer = -1;
    var k;
    for (k = 0; k < slots.length; k += 1) {
      if (slots[k].spacer) {
        firstSpacer = k;
        break;
      }
    }
    var ri;
    var si;
    for (ri = 0; ri < rows.length; ri += 1) {
      var row = rows[ri];
      for (si = 0; si < slots.length && si < row.length; si += 1) {
        if (!staveNoteHasVisibleNotehead(row[si])) {
          // Spacer mag onzichtbaar zijn; meet geen false keep.
          if (slots[si].spacer) {
            continue;
          }
          continue;
        }
        if (slots[si].spacer) {
          spacerVisible += 1;
        } else if (slots[si].breve) {
          keepVisible += 1;
          if (row[si].getAttribute("data-osmd-breve") === "1") {
            breveMarked += 1;
          }
        } else if (firstSpacer < 0 || si < firstSpacer) {
          keepVisible += 1;
        } else {
          cadenceVisible += 1;
        }
      }
    }
    var hideCols = 0;
    for (si = 0; si < slots.length; si += 1) {
      if (slots[si].spacer) {
        hideCols += 1;
      }
    }
    out.slotCount = slots.length;
    out.hideCols = hideCols;
    out.voiceRows = rows.length;
    out.noteCount = notes.length;
    out.keepVisibleHeads = keepVisible;
    out.spacerVisibleHeads = spacerVisible;
    out.cadenceVisibleHeads = cadenceVisible;
    out.breveMarked = breveMarked;
    out.warnings = [];
    out.hints = [];
    if (spacerVisible > 0) {
      out.warnings.push(
        label +
          ": recite-bolletjes in midden: " +
          spacerVisible +
          " (moet 0 zijn)"
      );
    }
    if (mi === 0 && keepVisible < 2) {
      out.warnings.push(
        label +
          ": bij begin (Al/breve) te weinig noten zichtbaar: " +
          keepVisible +
          " (minstens 2)"
      );
    }
    if (mi === 0 && breveMarked < 1) {
      out.warnings.push(
        label + ": breve «le» niet gemarkeerd (data-osmd-breve)"
      );
    }
    if (rows.length && rows[0].length < slots.length) {
      out.hints.push(
        label +
          ": DOM-stemrij korter (" +
          rows[0].length +
          ") dan MusicXML-slots (" +
          slots.length +
          ")"
      );
    }
    return out;
  }

  /**
   * Diagnose S8/OSMD op de getoonde partituur (zelfde grid-logica als hide).
   * @returns {{ ok: boolean, build: string, script: string, staven: object, warnings: string[] }}
   */
  window.__vsaScoreOsmdDiagnoseReport = function (mount, xmlText) {
    var scriptSrc = "";
    Array.prototype.forEach.call(
      document.querySelectorAll('script[src*="score-osmd.js"]'),
      function (s) {
        if (!scriptSrc) {
          scriptSrc = s.src || "";
        }
      }
    );
    var byPart = s8PrintSlotsByPartMeasure(xmlText);
    var measures = Array.prototype.slice
      .call(mount.querySelectorAll(".vf-measure"))
      .sort(function (a, b) {
        return a.getBBox().y - b.getBBox().y;
      });
    var boven = diagnoseStaff(measures, byPart, 0, "boven");
    var bas = diagnoseStaff(measures, byPart, 1, "bas");
    var warnings = []
      .concat(boven.warnings || [])
      .concat(bas.warnings || []);
    var hints = [].concat(boven.hints || []).concat(bas.hints || []);
    var ok =
      warnings.length === 0 &&
      (boven.spacerVisibleHeads || 0) === 0 &&
      (bas.spacerVisibleHeads || 0) === 0 &&
      (boven.keepVisibleHeads || 0) >= 2;
    return {
      ok: ok,
      build: window.__VSA_SCORE_OSMD_BUILD,
      script: scriptSrc,
      page: window.location.pathname,
      lyricTextGroups: mount.querySelectorAll("g.vf-text.lyrics").length,
      lyricDashGroups: mount.querySelectorAll("g.vf-text.dash").length,
      staven: { boven: boven, bas: bas },
      warnings: warnings,
      hints: hints,
    };
  };

  window.__vsaScoreOsmdPlainText = function (report) {
    var b = report.staven.boven || {};
    var s = report.staven.bas || {};
    var lines = [];
    lines.push("VSA-partituur check (plak dit in Cursor-chat)");
    lines.push("Pagina: " + (report.page || "?"));
    lines.push("Versie: " + (report.build || "?"));
    lines.push(
      "Automatisch: " +
        (report.ok ? "GOED" : "PROBLEEM") +
        " (alleen verborgen spacer-koppen in XML; echte noten tellen niet mee)"
    );
    lines.push(
      "Referentie: sibling .mvsa.svg op dezelfde pagina (Bronnen) — zelfde stuk, MuseScore/SVG."
    );
    lines.push(
      "Bovenstem — recite-bolletjes: " +
        (b.spacerVisibleHeads != null ? b.spacerVisibleHeads : "?") +
        " (0=goed); noten bij Al/breve: " +
        (b.keepVisibleHeads != null ? b.keepVisibleHeads : "?") +
        " (minstens 2=goed)"
    );
    lines.push(
      "Onderstem — recite-bolletjes: " +
        (s.spacerVisibleHeads != null ? s.spacerVisibleHeads : "?") +
        " (0=goed); noten cadens rechts: " +
        (s.cadenceVisibleHeads != null ? s.cadenceVisibleHeads : "?")
    );
    if (report.warnings && report.warnings.length) {
      lines.push("Probleem volgens meting: " + report.warnings.join(" | "));
    }
    if (report.hints && report.hints.length) {
      lines.push("Optioneel: " + report.hints.join(" | "));
    }
    lines.push("");
    lines.push(
      "Mijn ogen (typ hier 1 korte zin, bv. eerste Al ja/nee, bolletjesrij ja/nee, tekst scheef ja/nee):"
    );
    return lines.join("\n");
  };

  window.__vsaCountVisibleReciteHeads = function (mount, xmlText) {
    if (!xmlText) {
      return { boven: "?", bas: "?", hint: "fetch MusicXML meegeven" };
    }
    var byPart = s8PrintSlotsByPartMeasure(xmlText);
    var measures = Array.prototype.slice
      .call(mount.querySelectorAll(".vf-measure"))
      .sort(function (a, b) {
        return a.getBBox().y - b.getBBox().y;
      });
    function staff(mi) {
      if (!measures[mi] || !byPart[mi]) {
        return 0;
      }
      var id = measures[mi].getAttribute("id") || "1";
      var flags = byPart[mi][String(id)];
      if (!flags) {
        return 0;
      }
      var notes = measures[mi].querySelectorAll(".vf-stavenote");
      return countVisibleSpacerZoneHeads(notes, flags);
    }
    return { boven: staff(0), bas: staff(1) };
  };
})();
