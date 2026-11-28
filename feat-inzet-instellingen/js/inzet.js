/**
 * Knop "Inzet": laat de beginnoten van S, A, T en B (of van de enige stem) na
 * elkaar klinken. Het knopje ernaast opent de keuzes van de koorleider; die
 * blijven in localStorage op dit apparaat.
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
  var OPSLAG = "bibliotheek-inzet";
  var stand = lees();
  var paneel = null; /* open paneel */

  function lees() {
    try {
      return Kern.instellingen(JSON.parse(window.localStorage.getItem(OPSLAG)));
    } catch (e) {
      return Kern.instellingen(null);
    }
  }

  function bewaar() {
    try {
      window.localStorage.setItem(OPSLAG, JSON.stringify(stand));
    } catch (e) {
      /* privemodus: de keuze geldt dan alleen zolang de pagina open is */
    }
  }

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

  /* {noten, doKlasse} van een stuk, zoals genoteerd. */
  function gegevens(vak) {
    var url = vak.getAttribute("data-inzet-src");
    if (!url) {
      var doNaam = vak.getAttribute("data-inzet-do") || "";
      var letter = "C D EF G A B".indexOf(doNaam.charAt(0));
      var teken = doNaam.charAt(1) === "b" ? -1 : doNaam.charAt(1) === "#" ? 1 : 0;
      return Promise.resolve({
        noten: [{ stem: "", midi: parseInt(vak.getAttribute("data-inzet-midi"), 10) }],
        doKlasse: letter < 0 ? null : (letter + teken + 12) % 12,
      });
    }
    if (!cache[url]) {
      cache[url] = fetch(url)
        .then(function (antwoord) {
          if (!antwoord.ok) throw new Error("HTTP " + antwoord.status);
          return antwoord.text();
        })
        .then(function (xml) {
          var gevonden = Kern.beginnoten(xml);
          if (!gevonden) throw new Error("geen vier beginnoten");
          return { noten: gevonden, doKlasse: Kern.doUitKruizen(xml) };
        });
      cache[url].catch(function () {
        delete cache[url];
      });
    }
    return cache[url];
  }

  function klinkend(vak, uit) {
    var id = vak.getAttribute("data-inzet-id");
    return Kern.verschuif(uit.noten, Kern.geldend(stand, id), stand.tbHoger);
  }

  function start(button) {
    var vak = button.closest("[data-inzet]");
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
    Promise.all([gegevens(vak), wakker])
      .then(function (uit) {
        if (mijnBeurt !== beurt) return;
        speel(Kern.speelschema(klinkend(vak, uit[0])));
      })
      .catch(function (fout) {
        if (mijnBeurt !== beurt) return;
        stop();
        button.textContent = "Geen inzet";
        button.disabled = true;
        if (window.console) console.warn("Inzet:", fout);
      });
  }

  /* Knopje naast Inzet: toont de verschuiving; oranje = eigen instelling. */
  function werkKnoppenBij() {
    document.querySelectorAll("[data-inzet]").forEach(function (vak) {
      var id = vak.getAttribute("data-inzet-id");
      var eigen = Kern.heeftEigen(stand, id);
      var n = Kern.geldend(stand, id);
      var kies = vak.querySelector("[data-inzet-kies]");
      vak.classList.toggle("score-inzet--eigen", eigen);
      kies.textContent = eigen ? "eigen " + Kern.kortTeken(n) : n ? Kern.kortTeken(n) : "\u00b1";
      kies.setAttribute(
        "aria-label",
        "Inzet instellen. Nu " +
          Kern.verschuivingTekst(n) +
          (eigen ? ", eigen instelling voor dit stuk" : ", algemene instelling")
      );
    });
  }

  function element(tag, klasse, tekst) {
    var el = document.createElement(tag);
    if (klasse) el.className = klasse;
    if (tekst) el.textContent = tekst;
    return el;
  }

  function keuzeknop(tekst, actie, ingedrukt) {
    var b = element("button", "", tekst);
    b.type = "button";
    b.setAttribute("data-inzet-actie", actie);
    if (ingedrukt !== undefined) b.setAttribute("aria-pressed", String(ingedrukt));
    return b;
  }

  function tekenPaneel() {
    var vak = paneel.parentNode;
    var id = vak.getAttribute("data-inzet-id");
    var eigen = Kern.heeftEigen(stand, id);
    var n = Kern.geldend(stand, id);
    var vierstemmig = !!vak.getAttribute("data-inzet-src");
    var focus = paneel.contains(document.activeElement)
      ? document.activeElement.getAttribute("data-inzet-actie")
      : null;
    paneel.textContent = "";

    if (!vierstemmig) {
      paneel.appendChild(
        element("p", "inzet-let-op", "Alleen de melodie is bekend: je hoort \u00e9\u00e9n toon.")
      );
    }

    var regime = element("div", "inzet-regime");
    regime.setAttribute("role", "group");
    regime.setAttribute("aria-label", "Welke instelling geldt voor dit stuk");
    regime.appendChild(keuzeknop("Algemeen", "algemeen", !eigen));
    regime.appendChild(keuzeknop("Eigen voor dit stuk", "eigen", eigen));
    paneel.appendChild(regime);

    var stapper = element("div", "inzet-stapper");
    var lager = keuzeknop("\u2212", "lager");
    lager.setAttribute("aria-label", "Halve toon lager");
    var hoger = keuzeknop("+", "hoger");
    hoger.setAttribute("aria-label", "Halve toon hoger");
    var waarde = element("output", "", Kern.verschuivingTekst(n));
    waarde.setAttribute("aria-live", "polite");
    stapper.appendChild(lager);
    stapper.appendChild(waarde);
    stapper.appendChild(hoger);
    paneel.appendChild(stapper);

    paneel.appendChild(
      element(
        "p",
        "inzet-uitleg",
        eigen
          ? "Alleen dit stuk. Algemeen staat op: " + Kern.verschuivingTekst(stand.algemeen) + "."
          : "Geldt voor alle stukken op Algemeen."
      )
    );

    var tonen = element("p", "inzet-tonen", "\u00a0");
    paneel.appendChild(tonen);
    var dit = paneel;
    gegevens(vak).then(
      function (uit) {
        if (paneel !== dit) return;
        var noten = klinkend(vak, uit)
          .map(function (noot) {
            return (noot.stem ? noot.stem + ": " : "Toon: ") + Kern.nootnaam(noot.midi);
          })
          .join(" \u00b7 ");
        var doTekst =
          uit.doKlasse === null
            ? ""
            : "do klinkt als " + Kern.nootnaam(uit.doKlasse + Kern.geldend(stand, id) + 120) + "\n";
        tonen.textContent = doTekst + noten;
      },
      function () {
        tonen.textContent = "De beginnoten konden niet worden geladen.";
      }
    );

    if (vierstemmig) {
      var label = element("label", "inzet-tb");
      var vink = element("input");
      vink.type = "checkbox";
      vink.checked = stand.tbHoger;
      vink.setAttribute("data-inzet-actie", "tb");
      label.appendChild(vink);
      label.appendChild(
        document.createTextNode(" Tenor en bas een octaaf hoger (bij alle stukken)")
      );
      paneel.appendChild(label);
    }

    if (focus) {
      var terug = paneel.querySelector('[data-inzet-actie="' + focus + '"]');
      if (terug) terug.focus();
    }
  }

  function sluitPaneel() {
    if (!paneel) return;
    var vak = paneel.parentNode;
    vak.querySelector("[data-inzet-kies]").setAttribute("aria-expanded", "false");
    vak.removeChild(paneel);
    paneel = null;
  }

  function openPaneel(kies) {
    var vak = kies.closest("[data-inzet]");
    var wasDit = paneel && paneel.parentNode === vak;
    sluitPaneel();
    if (wasDit) return;
    paneel = element("div", "inzet-paneel");
    paneel.setAttribute("role", "dialog");
    paneel.setAttribute("aria-label", "Inzet instellen");
    vak.appendChild(paneel);
    kies.setAttribute("aria-expanded", "true");
    tekenPaneel();
  }

  function doe(actie) {
    var id = paneel.parentNode.getAttribute("data-inzet-id");
    stop();
    beurt++;
    if (actie === "algemeen") Kern.zetEigen(stand, id, false);
    else if (actie === "eigen") Kern.zetEigen(stand, id, true);
    else if (actie === "lager") Kern.stap(stand, id, -1);
    else if (actie === "hoger") Kern.stap(stand, id, 1);
    else if (actie === "tb") stand.tbHoger = !stand.tbHoger;
    bewaar();
    werkKnoppenBij();
    tekenPaneel();
  }

  document.addEventListener("click", function (event) {
    var doel = event.target;
    if (paneel && paneel.contains(doel)) {
      var actie = doel.closest("[data-inzet-actie]");
      if (actie) doe(actie.getAttribute("data-inzet-actie"));
      return;
    }
    var speelknop = doel.closest("[data-inzet-speel]");
    if (speelknop) {
      start(speelknop);
      return;
    }
    var kies = doel.closest("[data-inzet-kies]");
    if (kies) openPaneel(kies);
    else sluitPaneel();
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape" || !paneel) return;
    var kies = paneel.parentNode.querySelector("[data-inzet-kies]");
    sluitPaneel();
    kies.focus();
  });
  window.addEventListener("pagehide", stop);
  /* Ander tabblad of terug-knop: opnieuw uit de opslag lezen. */
  function ververs() {
    stand = lees();
    werkKnoppenBij();
    if (paneel) tekenPaneel();
  }
  window.addEventListener("storage", ververs);
  window.addEventListener("pageshow", ververs);
  werkKnoppenBij();
})();
