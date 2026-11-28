/**
 * Knop "Inzet": laat de beginnoten van S, A, T en B na elkaar klinken.
 * Het geluid maakt de browser zelf (Web Audio); er zijn geen audiobestanden.
 * Contract: docs/specs/schermpartituur.md §2.4.
 */
(function () {
  var Kern = window.__inzetKern;
  var AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!Kern || !AudioCtx) return;

  var context = null;
  var klinkt = []; /* oscillatoren van de lopende inzet */
  var knop = null; /* knop van de lopende inzet */
  var einde = 0;
  var beurt = 0; /* alleen de laatste klik mag nog gaan klinken */
  var cache = {};

  function stop() {
    klinkt.forEach(function (osc) {
      try {
        osc.stop();
      } catch (e) {
        /* al gestopt */
      }
    });
    klinkt = [];
    window.clearTimeout(einde);
    if (knop) knop.setAttribute("aria-pressed", "false");
    knop = null;
  }

  /* Boventonen: lage noten blijven zo hoorbaar op een telefoonluidspreker. */
  function orgelklank() {
    var sterkte = [0, 1, 0.5, 0.3, 0.15, 0.08];
    return context.createPeriodicWave(
      new Float32Array(sterkte.length),
      new Float32Array(sterkte)
    );
  }

  function speel(schema) {
    var klank = orgelklank();
    var nu = context.currentTime + 0.05;
    schema.forEach(function (toon) {
      var osc = context.createOscillator();
      var volume = context.createGain();
      var begin = nu + toon.start;
      var slot = begin + toon.duur;
      osc.setPeriodicWave(klank);
      osc.frequency.value = toon.frequentie;
      /* Zacht in en uit, anders hoor je klikken. */
      volume.gain.setValueAtTime(0, begin);
      volume.gain.linearRampToValueAtTime(0.5, begin + 0.02);
      volume.gain.setValueAtTime(0.5, slot - 0.05);
      volume.gain.linearRampToValueAtTime(0, slot);
      osc.connect(volume);
      volume.connect(context.destination);
      osc.start(begin);
      osc.stop(slot);
      klinkt.push(osc);
    });
    var laatste = schema[schema.length - 1];
    einde = window.setTimeout(stop, (laatste.start + laatste.duur) * 1000 + 100);
  }

  function noten(url) {
    if (!cache[url]) {
      cache[url] = fetch(url)
        .then(function (antwoord) {
          if (!antwoord.ok) throw new Error("HTTP " + antwoord.status);
          return antwoord.text();
        })
        .then(function (xml) {
          var gevonden = Kern.beginnoten(xml);
          if (!gevonden) throw new Error("geen vier beginnoten");
          return gevonden;
        });
      cache[url].catch(function () {
        delete cache[url];
      });
    }
    return cache[url];
  }

  function start(button) {
    var wasDeze = knop === button;
    stop();
    var mijnBeurt = ++beurt;
    if (wasDeze) return; /* tweede klik = stoppen */

    var voorbeeld = document.getElementById("score-audio-bar-element");
    if (voorbeeld && !voorbeeld.paused) voorbeeld.pause();

    /* iPhone: ook klinken met de stilschakelaar aan. */
    if (navigator.audioSession) navigator.audioSession.type = "playback";
    /* Aanmaken en hervatten moet direct in de klik gebeuren (iOS). */
    if (!context) context = new AudioCtx();
    var wakker = context.resume();

    knop = button;
    knop.setAttribute("aria-pressed", "true");
    Promise.all([noten(button.getAttribute("data-inzet-src")), wakker])
      .then(function (uit) {
        if (mijnBeurt !== beurt) return;
        speel(Kern.speelschema(uit[0]));
      })
      .catch(function (fout) {
        if (mijnBeurt !== beurt) return;
        stop();
        button.textContent = "Geen inzet";
        button.disabled = true;
        if (window.console) console.warn("Inzet:", fout);
      });
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-inzet-src]");
    if (button) start(button);
  });
  window.addEventListener("pagehide", stop);
})();
