---
title: ".vsa schrijven en op de pagina"
linkTitle: ".vsa schrijven"
weight: 10
---

# .vsa schrijven en op de pagina

{{< cue >}}
1. Kopieer een bestaand `.vsa` in de catalogus (bijvoorbeeld eerste antifoon weekdagen Hemelum).
2. Zet het bestand in de catalogus-map; bestandsnaam zonder spaties (publicatiestam).
3. Zet bovenaan YAML met minstens `do`, `mode` en `tempo: 130`.
4. `vsa validate pad\naar\bestand.vsa`
5. Catalogus-`index.md` + slot-pagina (of compositieblad): shortcode `bieb` met de catalogus-id
6. `scripts\vsa-products.cmd` op die map, daarna `scripts\check.cmd --strict`. Commit `.vsa`, `.vsa.svg`, `.vsa.pdf` en `.vsa.mxl` samen.
{{< /cue >}}

**Wat je nu doet:** de gezongen tekst in VSA-notatie zetten en via de
catalogus op de site tonen, inclusief oefenen in Coria. Nog geen
vierstemmig blad — daarvoor is de [volgende pagina](../2-template-satb/),
alleen voor tropaar toon 4.

**Wanneer:** je hebt tekst (en een bekende melodie) in plaats van een
Capella-partituur. Voorbeeld-catalogus-id:
`eerste-antifoon/weekdagen/hemelum`.

## Wat de site van je `.vsa` maakt

Op een gewone eenstemmige catalogus-pagina (geen basispartituur-`.mscz` ernaast)
doet de build twee aparte dingen met hetzelfde `.vsa`-bestand:

| Afgeleide | Rol op de pagina | Hoe maak je die |
| --- | --- | --- |
| `{stam}.vsa.svg` naast de `.vsa` | Het **plaatje** dat shortcode `bieb` toont | `scripts\vsa-products.cmd` (samen met PDF en Coria-`.mxl`) |
| `{stam}.vsa.pdf` naast de `.vsa` | **Downloaden** / **Printen** | Zelfde commando |
| `{stam}.vsa.mxl` naast de `.vsa` | Knop **Oefenen** (Coria) | Zelfde commando; export syllabificeert woorden tijdelijk, zonder je `.vsa` te wijzigen |

`scripts\opkuisen.cmd` past **geen** Capella-/MusicXML-heuristieken toe op een
`.vsa`. Met `--analyze` of `--dry-run` kan `opkuisen` wél `vsa validate`
rapporteren; automatische inhoudsfix op `.vsa` bestaat in v1 niet — zie
[opkuisen](/handleiding/scripts/opkuisen/).

Volledig overzicht van de pijplijnen: [Werktrajecten](/handleiding/werktrajecten/)
(VSA-werktraject: [VSA → SVG en Coria](/handleiding/werktrajecten/vsa/)).
HOW op deze pagina; de werktrajectpagina beschrijft waartoe, CI en commando’s.

Een basispartituur-`.mscz` in dezelfde map toont de PDF van dat spoor
op het scherm, niet de VSA-SVG. Een oud `.print.mscz` blokkeert de
VSA-SVG niet.

Het plaatje vernieuwen:

```cmd
scripts\vsa-products.cmd content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>
```

Zolang `{stam}.vsa.svg` ontbreekt, zoekt de site nog een legacy-plaatje
onder `static\vsa\bladermap\`. Dat vult `oefenhoek-index --svg` (ook in
`check` / `build` / `serve`). Dat is de fallback, niet het product dat
je commit.

## Stap voor stap

1. Maak of kies de catalogus-map ([publiceren](../../publiceren/1-bladermap/)).
2. Open een **bestaand** `.vsa` dat op het nieuwe stuk lijkt. Verzin de
   tekens niet vanaf nul. Antifoon-voorbeeld:

`content-source\catalogus\eerste-antifoon\weekdagen\hemelum\eerste-antifoon-weekdagen.vsa`

3. Kopieer dat bestand naar jouw catalogus-map, hernoem naar de
   publicatiestam (geen spaties), plak jouw tekst in dezelfde notatie. Een
   `.vsa` is **geen** Markdown-pagina: zet geen `#`-koppen in de notatie
   zelf. Zet wél YAML bovenaan tussen `---` met minstens `do`, `mode` en
   `tempo` (default in de toolchain is **120** BPM):

```yaml
---
do: F4
mode: major
tempo: 130
---
```

4. In het Windows-opdrachtvenster:

```cmd
vsa validate content-source\catalogus\eerste-antifoon\weekdagen\hemelum\eerste-antifoon-weekdagen.vsa
```

   Foutmelding: de markering zit in de **gezongen tekst**, niet in het
   programma. Verbeter de notatie. “Even stil krijgen” door tekens weg te
   halen is geen oplossing.

5. In catalogus-`index.md` (kopieer een bestaand voorbeeld):

```markdown
---
title: "…"
publicatiestatus: reviewable
automatische_inhoud: false
---

# …

{{</* bieb id="eerste-antifoon/weekdagen/hemelum" */>}}
```

6. Hetzelfde id in de **slot-pagina** van de koormap (bijv.
   `koormappen/hemelum/liturgie-weekdagen\eerste-antifoon\weekdagen\index.md`). Meerdere
   VSA’s op één liturgische plek? Sectie met kindpagina’s, of één
   compositieblad — zie
   [Catalogus en koormappen](../../start/catalogus-en-koormappen/).

7. Draai `scripts\vsa-products.cmd` op de catalogusmap, daarna
   `scripts\check.cmd --strict`. `vsa-products` schrijft
   `{stam}.vsa.svg`, `{stam}.vsa.pdf` en `{stam}.vsa.mxl`. `check`
   controleert die siblings en bouwt de site; `check` maakt ze niet.

   Commit **`.vsa`, `.vsa.svg`, `.vsa.pdf` en `.vsa.mxl` samen**. Op de
   preview verschijnt het plaatje én de knop **Oefenen**.

Catalogus-includes horen **niet** in de oefenhoek (geen verwijzing naar
`content-source/lokaal/`). Kondaken en troparen: catalogus-leaf + `bieb`.
Zie [Catalogus en koormap](../../publiceren/1-bladermap/).

Uitleg van de VSA-tekens (`{/`, `{_`, `*`, …): de pagina’s onder
[Tooling Demo](../../../demo/), niet deze handleiding. Hier gaat het over
waar het `.vsa`-bestand hoort en hoe het op de catalogus-site komt.

### Handmatige artefacten

Zet je op de catalogus-`index.md` `artefacten_handmatig: true`, dan
slaat `vsa-products` die map over: geen `.vsa.svg`, geen `.vsa.pdf` en
geen `.vsa.mxl`. Dat hoort bij een MuseScore-blad dat je zelf bijhoudt
— zie [Print-vel](../../werktrajecten/print-vel/) en de gele banner op
die cataloguspagina. Afspraak over namen en sporen:
[Publicatiecontrole](/handleiding/start/publicatiecontrole/).

Een basispartituur-`.mscz` in dezelfde map toont op het scherm de PDF
van dat spoor, niet de VSA-SVG.

### Banner of check over `.vsa.mxl`

Rode banner “VSA-afgeleiden niet in orde”, of `check` rood op `main`: de
`.vsa.mxl`, `.vsa.pdf` of `.vsa.svg` ontbreekt, is ouder dan de `.vsa`,
of mist de herkomststempel. Oplossing: `scripts\vsa-products.cmd`,
daarna opnieuw `check`, en bron plus siblings committen. Zie ook
[Als het misgaat](../../publiceren/3-als-het-misgaat/).

### Hugo-waarschuwing “SVG ontbreekt”

Shortcode `bieb` verwacht `{stam}.vsa.svg` naast de `.vsa`. Ontbreekt
die sibling, dan meldt Hugo ook het legacy-pad
`static\vsa\bladermap\…`. Oplossing:

```cmd
scripts\vsa-products.cmd content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>
```

Daarna opnieuw previewen. `check` alleen vult de sibling niet aan.

## Klaar als

`vsa validate` is stil, catalogus en koormap verwijzen met hetzelfde id,
na `vsa-products` en `check` zie je het plaatje op de lokale preview,
en er liggen verse `{stam}.vsa.svg`, `{stam}.vsa.pdf` en `{stam}.vsa.mxl`
naast de `.vsa` (scherm, download en **Oefenen**), tenzij
`artefacten_handmatig: true` op die cataloguspagina staat (dan houd jij
de afgeleiden zelf bij).

{{< navbuttons "Volgende: template SATB|/handleiding/vsa/2-template-satb/" >}}
