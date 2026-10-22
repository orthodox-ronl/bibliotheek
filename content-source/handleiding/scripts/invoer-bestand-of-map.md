---
title: "Invoer: bestand of map"
linkTitle: "Bestand of map"
weight: 5
---

# NAME

Invoerconventie — één bronbestand of een map

# DESCRIPTION

Veel bibliotheek-commando’s die op bestanden werken volgen dezelfde
afspraak als in VSA-tooling: het pad-argument is

1. **één bronbestand** met de juiste extensie, of
2. **een map**, waarvan (standaard recursief) alle passende bestanden
   worden meegenomen.

Lege map (geen treffers) → duidelijke fout. Een enkelvoudig uitvoerpad
(`-o` / `--output`) mag alleen bij precies **één** bronbestand.

Dit geldt onder meer voor [layout](../layout/), [pagina-pdf](../pagina-pdf/),
[bieb accepteer](../bieb-accepteer/), [opkuisen](../opkuisen/) en
[products](../products/) / `*-products` (die dit al deden via
`list_source_paths`).

**Niet** voor id-commando’s: `bieb hernoem`, `bieb verwijder`,
`bieb kopieer` (die werken op catalogus-ids, niet op bestandsscans).

## Batch: preflight, duur-schatting, bevestiging

Bij meerdere bestanden (vanaf 2) tonen o.a. `layout`, `pagina-pdf`,
`bieb accepteer`, `opkuisen` en de `*-products` / `products` eerst een
**preflight**: hoeveel items, wat er gebeurt, en een **geschatte duur**.
Die schatting komt uit een running gemiddelde van de laatste metingen op
deze pc (per bewerkingstype, max. 20 samples), opgeslagen in
`generated\batch_timing.json` (niet in git). Zonder eerdere metingen staat
er expliciet „onbekend”.

Daarna: **Doorgaan? [j/N]**. Met `-y` / `--yes` sla je die gewone vraag
over (nodig in niet-interactieve runs). `products` (meerdere kinds) vraagt
één keer; de kind-sporen krijgen intern `-y`.

**Harde limiet (100+ items):** geen aparte switch onthouden. Het script
vraagt dan **Weet je het zeker?** en daarna **HEEL zeker?** (typ precies
`ja`). `-y` zet die dubbele vraag *niet* uit — handig na een grote
tooling-wijziging: alles opnieuw maken door twee keer bewust te
bevestigen in het opdrachtvenster. Zonder terminal stopt zo’n grote batch
met uitleg.

Tijdens de batch: doorgaan bij fouten, tussentijdse
resterende-tijd-schatting, eindlijst van mislukte paden.

Technische helpers: `scripts\input_paths.py`, `scripts\batch_guard.py`.

# EXAMPLES

```cmd
scripts\layout.cmd content-source\catalogus\ektinia\vrede\hemelum\lied.mscz
scripts\layout.cmd content-source\catalogus\ektinia\vrede
scripts\pagina-pdf.cmd content-source\koormappen\hemelum\liturgie-zondag
scripts\bieb.cmd accepteer input\_werk\batch --dry-run
```

Bij een map: eerst `--dry-run` waar dat bestaat; controleer of je niet per
ongeluk een te grote boom meegeeft.

{{< navbuttons "Script-referentie|/handleiding/scripts/" "layout|/handleiding/scripts/layout/" >}}
