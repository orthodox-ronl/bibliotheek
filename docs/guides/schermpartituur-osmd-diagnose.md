# OSMD — partituur check (1 plakblok voor Cursor)

Antwoord eerst: je hoeft **geen** console-objecten te knippen. Eén
console-commando → tekst op het **klembord** → **Ctrl+V** in de chat, plus
**één zin** wat jij ziet.

Look-regels: [schermpartituur.md](../specs/schermpartituur.md).

## Stappen

1. Bibliotheek-site draait (`serve` in repo **bibliotheek**).
2. Open een blad met OSMD-partituur (bijv. Alleluia Groningen).
3. Wacht tot de partituur getoond is.
4. **Ctrl+F5** (verversen).
5. **F12** → tab **Console**.
6. Plak het blok hieronder, druk **Enter**.

```javascript
(async function () {
  if (!window.__vsaRunScoreOsmdDiagnose) {
    await new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = "/js/score-osmd-diagnose.js?v=20261024-2";
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  return await window.__vsaRunScoreOsmdDiagnose();
})();
```

7. In Cursor-chat: **Ctrl+V**.
8. Onder de geplakte tekst: vul de regel **«Mijn ogen …»** in (of typ er
   direct onder één korte zin).

## Wat de regels betekenen (kort)

| Tekst in plakblok | Betekenis |
| --- | --- |
| **recite-bolletjes** | Zwarte koppen in het lange middenstuk (moet **0** zijn). |
| **noten bij Al/breve** | Kwart + breve aan het begin bovenstem (minstens **2**). |
| **Automatisch GOED/PROBLEEM** | Rekentool; **jouw zin** blijft leidend als het beeld afwijkt. |

## Bestanden

- `static/js/score-osmd.js` — weergave + meting
- `static/js/score-osmd-diagnose.js` — klembord-plakblok
