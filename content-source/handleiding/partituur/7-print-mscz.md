---
title: "Print-.mscz (koormap-vel)"
linkTitle: "Print-.mscz"
weight: 70
---

# Print-`.mscz` (koormap-vel)

**Werktraject** (waartoe, criteria, CI):
[Print-vel](/handleiding/werktrajecten/print-vel/).
Deze pagina is de HOW.

{{< cue >}}
Bestandsnaam eindigt op **`.print.mscz`**. Geen `scripts\layout.cmd`, geen
`products --kinds mscz`, geen Coria-eis uit dit MuseScore-bestand. PDF maak je zelf in
MuseScore 4 (Bestand → Exporteren → PDF) en commit je naast het print-bestand
**in de catalogus**. Zet op de catalogus-`index.md`
`manueel: true` (gele beheerdersbanner).
{{< /cue >}}

**Wat je nu doet:** een MuseScore-bestand in de **catalogus** zetten dat de
basispartituur-pijplijn **niet** mag aanpassen — typisch één A4-vel voor de koormap met
layout of tekstregels die de basispartituur-normalisatie zou vernielen, of een
template-SATB-blad dat jij handmatig bijhoudt. Het koormap-slot verwijst met
`bieb`.

**Wanneer:** als je bewust **buiten** de basispartituur-spoor werkt. Voor gewoon
oefenmateriaal (één tekst, automatische Coria, standaardlayout) gebruik je een
gewone basispartituur-`.mscz` via [standaard-.mscz](../3-standaard-mscz/) en
[PDF en Coria](../5-pdf-en-coria/), of een eenstemmige `.vsa` via
[.vsa schrijven](../../vsa/1-vsa-schrijven/).

Voorbeelden in de catalogus:

- `kleine-intocht/zo-wk-mg/hemelum` — gecombineerd printvel;
- `tropaar/nikolaas-van-myra-toon-4/hemelum` — template-SATB + handmatige
  PDF/MXL + `.vsa`;
- `moeder-godslied/ontslapen-moeder-gods/hemelum` — idem print + handmatig.

## Wat het is

| In Verkenner (catalogus) | Rol |
| --- | --- |
| `{stam}.print.mscz` | MuseScore-bron voor een printvel; scripts laten dit met rust |
| `{stam}.pdf` | Handmatige A4-export |
| Optioneel: Coria-`.mxl` | Alleen als jij die zelf neerzet en bijhoudt (geen `products --kinds mscz`) |
| Optioneel: `.vsa` | Notatie naast het printvel; `products --kinds vsa` slaat de map over bij `manueel: true` |

Catalogus-id voorbeeld: `kleine-intocht/zo-wk-mg/hemelum`.

Frontmatter op catalogus-`index.md`:

```yaml
manueel: true
```

Die regel betekent: PDF, Coria-`.mxl` en andere afgeleiden in **deze** map
worden niet automatisch bijgewerkt. De cataloguspagina toont een gele
beheerdersmelding. Afspraak over bestandsnamen per spoor:
[Publicatiecontrole](/handleiding/start/publicatiecontrole/).

## Wat je niet doet

- Geen `scripts\layout.cmd` op `.print.mscz`.
- Geen `products.cmd --kinds mscz` voor dit bestand.
- Geen hernoemen naar gewone `.mscz` “even snel” — dan eist `check` basispartituur-producten.
- Geen verwachting dat `products --kinds vsa` de Coria-`.mxl` vernieuwt zolang
  `manueel: true` staat.

## Stap voor stap

1. Bewerk in MuseScore 4. Neem het bestand op met
   [bieb accepteer](/handleiding/publiceren/1-opnemen-in-catalogus/)
   (bestandsnaam eindigend op `.print.mscz`), of sla handmatig op als
   `{stam}.print.mscz` in de catalogus (geen spaties; stam uit
   catalogus-id).
2. Exporteer PDF handmatig naar `{stam}.pdf` in dezelfde catalogus-map.
   Eventuele Coria-`.mxl` eveneens handmatig (of uit de template-render)
   ernaast zetten en bij elke bronwijziging meenemen.
3. Catalogus-`index.md` met `manueel: true` (bieb accepteer
   zet dat automatisch bij `.print.mscz`) + koormap-slot met `bieb`
   (bestaand id: [Zoeken](/overzichten/zoeken/); Hemelum-naslag:
   [Id-register](/overzichten/id-register/)).
4. `scripts\check.cmd --strict` — partituur- en VSA-publicatiecontrole slaan deze map over.

## Klaar als

De catalogusmap bevat `*.print.mscz` en PDF (plus eventueel handmatige `.mxl` /
`.vsa`); `manueel: true` staat op de `index.md`; koormap-slot
verwijst ernaar; check klaagt niet over ontbrekende automatische Coria voor
dit printvel.

{{< navbuttons "Terug: afgeleiden|/handleiding/partituur/6-afgeleiden/" "Handleiding|/handleiding/" >}}
