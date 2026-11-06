---
title: "Invoer: bestand of map"
linkTitle: "Bestand of map"
weight: 5
---

# NAME

Invoerconventie — pad zoeken, bestand of map, en korte logregels

# DESCRIPTION

Veel bibliotheek-commando’s die op bestanden werken volgen dezelfde
afspraak als in VSA-tooling: het pad-argument is

1. **één bronbestand** met de juiste extensie, of
2. **een map**, waarvan (standaard recursief) alle passende bestanden
   worden meegenomen.

Lege map (geen treffers) → duidelijke fout. Een enkelvoudig uitvoerpad
(`-o` / `--output`) mag alleen bij precies **één** bronbestand.

Dit geldt onder meer voor [layout](../layout/), [pdf](../pdf/),
[bieb accepteer](../bieb-accepteer/), [opkuisen](../opkuisen/) en
[products](../products/) / `*-products` (via `list_source_paths`).

**Niet** voor id-commando’s: `bieb hernoem`, `bieb verwijder`,
`bieb kopieer` (die werken op catalogus-ids, niet op bestandsscans).

## Korte paden (waar het CLI dat ondersteunt)

Bij [products](../products/) (en elk product-kind), [pdf](../pdf/),
[layout](../layout/), [opkuisen](../opkuisen/),
[cleanup-chained-products](../cleanup-chained-products/),
[ensure-bibliotheek-id](../ensure-bibliotheek-id/),
[bieb accepteer](../bieb-accepteer/) en [validate](../validate/)
zoekt het script een ontbrekend pad in deze volgorde:

1. precies zoals je het typt (absoluut, of relatief t.o.v. de map waarin
   je het opdrachtvenster hebt openstaan; relatief ook t.o.v. de
   repository-map);
2. onder `content-source\`;
3. onder `content-source\catalogus\`;
4. onder `content-source\koormappen\`.

Het eerste bestaande bestand of de eerste bestaande map wint. Bestaat
dezelfde relatieve naam onder catalogus én koormappen, dan wint
**catalogus**.

Voorbeelden die hetzelfde blad bedoelen:

```cmd
scripts\products.cmd content-source\catalogus\tweede-antifoon\weekdagen\hemelum
scripts\products.cmd catalogus\tweede-antifoon\weekdagen\hemelum
scripts\products.cmd tweede-antifoon\weekdagen\hemelum
```

```cmd
scripts\pdf.cmd content-source\koormappen\hemelum\liturgie-zondag
scripts\pdf.cmd koormappen\hemelum\liturgie-zondag
scripts\pdf.cmd hemelum\liturgie-zondag
```

Andere script-man-pages kunnen nog een volledig `content-source\…`-pad
in de voorbeelden tonen; korte vormen werken op de CLI’s hierboven.
`validate` lost het pad op via `scripts\resolve_cli_path.py` en geeft
het absolute pad door aan de `vsa`-/`mvsa`-CLI.

## Logging: korte bestandsnamen

In de uitvoer (OK-regels, fouten, fix-suggesties) schrijft het script
paden als volgt:

- onder `content-source\` → relatief t.o.v. die map
  (`catalogus\…`, `koormappen\…`, `handleiding\…`);
- anders onder de repository → relatief t.o.v. de repo-root
  (`scripts\…`, `data\…`);
- buiten de repository → absoluut pad.

Zo zie je in logs `catalogus\trisagion\…` in plaats van
`content-source\catalogus\trisagion\…`.

Technische helpers: `scripts\input_paths.py` (`resolve_user_path`,
`rel_for_log`), `scripts\batch_guard.py`.

## Batch: preflight, duur-schatting, bevestiging

Bij een batch tonen o.a. `layout`, `pdf.cmd`, `bieb accepteer`,
`opkuisen` en de `*-products` / `products` eerst een **preflight**:
hoeveel items, wat er gebeurt, en een **geschatte duur**. Die schatting
komt uit een running gemiddelde van de laatste metingen op deze pc (per
bewerkingstype, max. 20 samples), opgeslagen in
`generated\batch_timing.json` (niet in git). Zonder eerdere metingen staat
er expliciet „onbekend”.

**Korte runs** (minder dan 100 items, of geschat klaar binnen ongeveer
een halve minuut) starten daarna meteen — geen **Doorgaan?**. Met `-y` /
`--yes` sla je elke bevestigingsvraag over (nodig zonder interactieve
terminal). `products` vraagt hooguit **één keer** voor de hele run;
daarna geen tweede vraag per kind.

**Harde limiet (100+ items):** zonder `-y` vraagt het script
**Weet je het zeker?** en daarna **HEEL zeker?** (typ precies `ja`).
Met `-y` / `--yes` gaat die batch stil door. Zonder terminal en zonder
`-y` stopt zo’n grote batch met uitleg.

Tijdens de batch: doorgaan bij fouten, tussentijdse
resterende-tijd-schatting, eindlijst van mislukte paden. Tijdelijke
Windows-vergrendeling (bestand even vast door MuseScore, viewer of
Defender) wordt uitgesteld en later in dezelfde run opnieuw geprobeerd;
pas daarna telt het als mislukt.

# EXAMPLES

```cmd
scripts\products.cmd tweede-antifoon\weekdagen\hemelum --kinds vsa
scripts\pdf.cmd hemelum\liturgie-zondag\vredeslitanie
scripts\layout.cmd content-source\catalogus\ektinia\vrede\hemelum\lied.mscz
scripts\layout.cmd content-source\catalogus\ektinia\vrede
scripts\bieb.cmd accepteer input\_werk\batch --dry-run
```

Bij een map: eerst `--dry-run` waar dat bestaat; controleer of je niet per
ongeluk een te grote boom meegeeft.

{{< navbuttons "Script-referentie|/handleiding/scripts/" "layout|/handleiding/scripts/layout/" >}}
