---
title: "VSA plus template (SATB)"
linkTitle: "Template SATB"
weight: 20
---

# VSA plus template (SATB)

{{< cue >}}
Werkt nu concreet voor **tropaar toon 4** (corpus `T4-01` … `T4-12`). In `VSA-tooling`:
```cmd
cd /d C:\Git\orthodox-ronl\VSA-tooling
python scripts\render_tropaar_toon4_corpus.py --id T4-11 --pdf
```
Kopieer het resultaat naar de catalogus-site-bibliotheek als **print-vel** +
handmatige artefacten (zie stap 5), niet als automatische basispartituur.
{{< /cue >}}

**Wat je nu doet:** de eenstemmige tropaar-`.vsa` (sopraan plus tekst)
laten uitwerken tot een vierstemmig blad. Alt, tenor en bas komen uit de
formule `tropaar-toon-4`, niet uit extra VSA-regels.

**Wanneer:** tropaar op toon 4 die al een corpus-id heeft (zoals Nikolaas
`T4-11`). Een willekeurige antifoon of een andere toon: sla deze pagina
over; blijf bij [.vsa op de pagina](../1-vsa-schrijven/). Nieuw corpus-id
nodig? Vragen, niet zelf een code verzinnen.

Dit is **niet** de toekomstige meerstemmige VSA-syntax. Het is de keten
die vandaag werkt: tekst in VSA, stemmen in de template, MuseScore-bestand
als resultaat.

## Stap voor stap

1. De `.vsa` heeft bovenaan minstens:

```yaml
---
title: Nicolaas van Myra
do: F4
mode: major
tempo: 130
genre: tropaar
tone: 4
template: tropaar-toon-4
corpus_id: T4-11
---
```

   Bestandsnaam in de tooling-corpus:
   `T4-11-nicolaas-van-myra.vsa`
   (id, streepje, korte naam).

2. Open een **tweede** Windows-opdrachtvenster, nu in VSA-tooling:

```cmd
cd /d C:\Git\orthodox-ronl\VSA-tooling
```

3. Render alleen corpus-id `T4-11`, plus PDF via MuseScore:

```cmd
python scripts\render_tropaar_toon4_corpus.py --id T4-11 --pdf
```

   Zonder `--id` doet het script de hele corpus — dat hoeft niet.

4. Het resultaat landt in:

`VSA-tooling\docs\specification-vsa-templates\library\tropaar-toon-4\examples\corpus\`

   naast de `.vsa`: `.mscz`, `.mxl`, en met `--pdf` ook `.pdf`.

5. Kopieer naar de catalogus (voorbeeld Nikolaas:
   `catalogus\tropaar-nikolaas-van-myra\liturgikon\hemelum\`).
   Bestandsnamen **zonder spaties**. Voor dit soort template-blad:

   - laat het MuseScore-bestand `{stam}.mscz` heten (geen `.print.` in de naam);
   - houd PDF en Coria-`.mxl` zelf bij;
   - zet op catalogus-`index.md` `manueel: true`
     (gele beheerdersbanner; `products --kinds vsa` en de partituur-publicatiecontrole slaan de hele map over, ook een `.vsa` in diezelfde map);
   - wil je de eenstemmige notatie wél automatisch op het scherm, zet die `.vsa` dan niet in een map met `manueel` / `manual` — zie [.vsa schrijven](../1-vsa-schrijven/).

   Daarna koormap-slot via
   [Catalogus en koormap](../../publiceren/1-bladermap/). Print-details:
   [Print-.mscz](../../partituur/7-print-mscz/).

6. Fout `TemplateInstanceError`: de VSA-sopraan landt niet op de formule
   (verkeerde toon of een verplicht slot overgeslagen). De melding zegt
   welke noot. Pas de VSA aan en render opnieuw — begin niet met de
   `.mscz` met de hand “bijkleuren”.

De formule zelf (`template.yaml`) wijzig je als beheerder van *materiaal*
niet even tussendoor. Dat is een andere taak, in VSA-tooling.

## Klaar als

In de catalogus liggen `{stam}.mscz`, handmatige PDF/MXL en eventueel de
`.vsa`, met `manueel: true` op de `index.md`. MuseScore toont
SATB; de preview (koormap-slot) heeft PDF plus **Oefenen** / **Downloaden**
waar je die bestanden hebt neergezet.

{{< navbuttons "Volgende: catalogus en koormap|/handleiding/publiceren/1-bladermap/" >}}
