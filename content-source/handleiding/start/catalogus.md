---
title: "Catalogus"
linkTitle: "Catalogus"
weight: 17
---

# Catalogus

De **catalogus** is de lifecycle-fase waarin de uitvoeringsvorm een
**canonieke bron** heeft onder
`content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\`.
Afgeleide producten (PDF, Coria-`.mxl`, audio, …) horen bij die bron via
de bestaande productscripts en publicatiecontrole. Overzicht:
[Levenscyclus](levenscyclus/).

{{< cue >}}
1. Canonieke bron bewerken in de catalogusmap (niet opnieuw vanuit
   een ruwe dump “ernaast”).
2. Producten: `scripts\all-products.cmd` met pad naar die map (of het
   passende `*-products.cmd`).
3. `scripts\check.cmd --strict` groen vóór commit/push.
4. Optioneel: koormap-slot met shortcode `bieb` naar hetzelfde id.
{{< /cue >}}

## Waar bestanden liggen

| Pad | Rol |
| --- | --- |
| `catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>\index.md` | Pagina + shortcode `bieb`; `publicatiestatus` |
| Zelfde map: `{stam}.mscz` / `.vsa` / `.mvsa` / `.tekstblad.md` | **Canonieke bron** |
| Zelfde map: `{stam}.mscz.pdf`, `.vsa.mxl`, `.mp3`, … | **Afgeleiden** (siblings); vernieuwen via products |
| `koormappen\…\index.md` | View: verwijst met `bieb`, bevat geen partituurbestanden |

Namen: [Publicatiecontrole](publicatiecontrole/). Model:
[Catalogus en koormappen](catalogus-en-koormappen/). Taalvarianten
(NL / kerkslavisch): suffix `-nl` / `-ksl` op de uitvoeringsvorm —
[Taalvarianten](catalogus-en-koormappen/#taalvarianten-op-de-uitvoeringsvorm).

## Wat je mag wijzigen vs. regenereren

| Wel met de hand | Via regeneratie / script |
| --- | --- |
| Canonieke bron (`.mscz`, `.vsa`, `.mvsa`, `.tekstblad.md`) | `{stam}.….pdf` / `.mxl` / `.mp3` / `.lyrics.txt` |
| Frontmatter `publicatiestatus`, titel, `artefacten_handmatig` | SVG-plaatjes (`oefenhoek-index --svg`, via check/build) |
| Koormap-markdown en `bieb`-id | Coria-fingerprints (gegenereerd, niet committen) |

Bij `artefacten_handmatig: true` houd je PDF/MXL zelf bij; de
automatische productcontrole slaat die map over. Zie
[Print-vel](../werktrajecten/print-vel/).

## Pijplijnen en scripts in deze fase

| Stap | Commando | Wat het hier doet |
| --- | --- | --- |
| Producten (één map) | `scripts\all-products.cmd content-source\catalogus\…` | Alle ontbrekende/stale siblings voor die boom |
| Eén spoor | `vsa-products` / `mscz-products` / `mvsa-products` / `audio-products` / … | Alleen dat producttype |
| Validate | `scripts\validate.cmd` | Geldigheid `.vsa` / `.mvsa` in de catalogus |
| Preflight | `scripts\check.cmd --strict` | Publicatiecontrole + Hugo + … |
| Grenzen | `scripts\lifecycle-grenzen.cmd` | Geen ruwe formats / spaties in catalogusmappen |
| Opkuisen (licht) | `scripts\opkuisen.cmd` op de **canonieke** `.mscz`/`.mxl` | Gericht herstel — niet opnieuw de Capella-dump als bron |

### Zelfde naam, andere zwaarte: `opkuisen` / `layout`

In de **catalogus** is de canonieke `.mscz` (of `.vsa`) leidend. Opkuisen
of layout hier is onderhoud van die bron, niet “nog eens de hele
werkbank-keten”. Ruwe dumps blijven in `input\`; die overschrijf je niet
stil vanuit catalogus-werk.

## Relatie tot de koormap

De catalogus-map is de bron van oefenbestanden. Een **koormap-slot**
verwijst alleen:

```markdown
{{</* bieb id="zangstuk/variant/uitvoeringsvorm" */>}}
```

Zie [Catalogus en koormap](../publiceren/1-bladermap/). Een
uitvoeringsvorm mag in de catalogus staan zonder koormap (special page
[Ongerefereerd](/catalogus/speciaal/ongerefereerd/)).

## Publicatiestatus (los van lifecycle)

Op `index.md` (bibliotheek én koormap): `voorzien`, `concept`,
`reviewable`, `productie`. Na `bieb accepteer` staat meestal
`reviewable`. `productie` alleen bewust. Detail:
[Status en check](../publiceren/2-status-en-check/).

## Kopieerbaar blok (na bronwijziging)

```cmd
cd /d C:\Git\orthodox-ronl\bibliotheek
scripts\all-products.cmd content-source\catalogus\<zangstuk>\<variant>\<uitvoeringsvorm>
scripts\check.cmd --strict
```

## Klaar als

De canonieke bron ligt in de catalogusmap; siblings zijn vers volgens
`check --strict`; je weet of een koormap-slot nog moet.

{{< navbuttons "Werkbank|/handleiding/start/werkbank/" "Publicatiecontrole|/handleiding/start/publicatiecontrole/" >}}
