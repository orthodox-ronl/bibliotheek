/**
 * Schermpartituur via OpenSheetMusicDisplay.
 * Bron: sibling ``*.from-ir.musicxml`` (Score-IR → MusicXML).
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
    var r = await fetch(src);
    if (!r.ok) {
      throw new Error("MusicXML HTTP " + r.status);
    }
    return r.text();
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

  function renderAndLayout(osmd, mount, xmlText) {
    osmd.render();
    layoutCues(mount, xmlText);
  }

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
        autoResize: true,
        backend: "svg",
        drawTitle: false,
        drawSubtitle: false,
        drawComposer: false,
        drawLyricist: false,
        drawPartNames: false,
        drawPartAbbreviations: false,
        drawMeasureNumbers: true,
        drawMeasureNumbersOnlyAtSystemStart: false,
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
      }
      await osmd.load(src);
      var xmlText = await fetchXml(src);
      applyInitialWidthFactors(osmd, xmlText);
      renderAndLayout(osmd, mount, xmlText);
      for (var pass = 0; pass < 3; pass += 1) {
        if (!redistributeForOverflow(osmd, mount, xmlText)) {
          break;
        }
        renderAndLayout(osmd, mount, xmlText);
      }
      // Maatbreedtes staan vast → inklappen naar 1 regel alleen als het past.
      collapseWrappedCuesIfTheyFit(mount, xmlText);
      // Daarna noten+lyrics centreren; cues niet opnieuw verplaatsen.
      centerMeasureContents(mount);
      if (status) {
        status.remove();
      }
      var resizeTimer = null;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          try {
            applyInitialWidthFactors(osmd, xmlText);
            renderAndLayout(osmd, mount, xmlText);
            if (redistributeForOverflow(osmd, mount, xmlText)) {
              renderAndLayout(osmd, mount, xmlText);
            }
            collapseWrappedCuesIfTheyFit(mount, xmlText);
            centerMeasureContents(mount);
          } catch (e) {
            console.warn("score-osmd: resize", e);
          }
        }, 200);
      });
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
})();
