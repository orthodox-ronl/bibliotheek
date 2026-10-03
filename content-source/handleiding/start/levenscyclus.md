---
title: "Levenscyclus van een uitvoeringsvorm"
linkTitle: "Levenscyclus"
weight: 15
---

# Levenscyclus van een uitvoeringsvorm

Elke **uitvoeringsvorm** (catalogus-id
`zangstuk/variant/uitvoeringsvorm`) is een *case*: je weet in welke
**lifecycle-fase** die zit, welke scripts en bestanden bij die fase
horen, en wanneer je naar de volgende fase mag.

Dit is **niet** hetzelfde als `publicatiestatus` op de site
(`voorzien` / `reviewable` / …). Die status is voor koorleden. De
lifecycle is voor beheerders die het materiaal maken.

{{< cue >}}
- **Werkbank** — reserveren, materiaal binnenhalen, opkuisen, editen,
  proefdraaien. Bestanden in `input\` en `_werk\`.
- **Catalogus** — canonieke bron in
  `content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\`;
  producten via `*-products`; `check --strict` groen.
- Overgang Werkbank → Catalogus: `bieb accepteer` als de
  [overgangscriteria](werkbank/#overgangscriteria) kloppen.
- Overzicht open werk: `scripts\werkbank-status.cmd` en special page
  [Werkbank](/catalogus/speciaal/werkbank/).
{{< /cue >}}

## Twee fases (nu)

| Fase | Waar bestanden horen | Kernvraag |
| --- | --- | --- |
| [Werkbank](werkbank/) | `input\<herkomst>\`, `_inbox\`, `_werk\<stam>\`; optioneel stub in de catalogus | “Waar werk ik dit stuk af?” |
| [Catalogus](catalogus/) | `catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\` | “Wat is de canonieke bron, en zijn de producten vers?” |

Later kunnen er fases bij (bijvoorbeeld review of archief). Het model
blijft hetzelfde: status per uitvoeringsvorm, fase-eigen pijplijnen,
overgangscriteria.

## Case-management in het kort

```text
(doel-)id bekend?
    |
    v
Werkbank: input + _werk + opkuisen/layout/proef
    |
    |  overgangscriterium + bieb accepteer
    v
Catalogus: canonieke bron + producten + check --strict
    |
    v
Koormap-slot (optioneel) met shortcode bieb
```

**Eén leidend authoring-spoor** per uitvoeringsvorm: als er meerdere
inputs (Capella én VOW) zijn, kies je één spoor dat naar de canonieke
bron leidt. Andere inputs blijven herkomst in `input\`, niet een tweede
“waarheid”.

## Commando’s op één plek

| Situatie | Commando |
| --- | --- |
| Wat hangt in de werkbank? | `scripts\werkbank-status.cmd` |
| Grenzen werkbank/catalogus checken | `scripts\lifecycle-grenzen.cmd` |
| Werkvoorraad-tabel bijwerken | `scripts\update-werkvoorraad.cmd` |
| Opnemen in de catalogus | `bieb accepteer` |
| Producten voor één map | `scripts\all-products.cmd content-source\catalogus\…` |
| Alles controleren | `scripts\check.cmd --strict` |

Detail per fase: [Werkbank](werkbank/), [Catalogus](catalogus/).
Productsporen: [Werktrajecten](../werktrajecten/). Mappen:
[Waar ligt wat](waar-ligt-wat/).

## Special pages

Automatische overzichten onder [Bibliotheek → Speciaal](/catalogus/speciaal/):

| Pagina | Rol t.o.v. lifecycle |
| --- | --- |
| [Werkbank](/catalogus/speciaal/werkbank/) | Onder handen: open werkvoorraad + stubs |
| [Voorzien](/catalogus/speciaal/voorzien/) | Zangstukken zonder oefenbare inhoud (`publicatiestatus`) |
| [Ongerefereerd](/catalogus/speciaal/ongerefereerd/) | In catalogus, nog geen koormap-`bieb` |
| [Oefenbaar](/catalogus/speciaal/oefenbaar/) | Platte lijst oefenbare uitvoeringsvormen |
| [Handmatig](/catalogus/speciaal/handmatig/) | Uitvoeringsvormen met `artefacten_handmatig: true` |

## Klaar als

Je kunt van elk stuk zeggen: werkbank of catalogus; welk script je nu
draait; en of de case al mag overgaan met `bieb accepteer`.

{{< navbuttons "Waar ligt wat|/handleiding/start/waar-ligt-wat/" "Werkbank|/handleiding/start/werkbank/" >}}
