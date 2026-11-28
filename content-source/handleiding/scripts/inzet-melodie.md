---
title: "inzet-melodie"
linkTitle: "inzet-melodie"
weight: 109
---

# NAME

`build_inzet_melodie.py` — zoekt de beginnoot voor de knop **Inzet** bij
stukken met alleen een melodie

# SYNOPSIS

```cmd
python scripts\build_inzet_melodie.py
```

Er is geen losse `.cmd`: `check`, `build`, `serve` en de GitHub
Pages-deploy draaien het script zelf. Normaal hoef je niets te doen.

# DESCRIPTION

De knop **Inzet** laat op de site de beginnoten van een zangstuk horen. Bij
vierstemmige muziek haalt de pagina de noten uit het bestand
`….from-ir.musicxml`. Sommige stukken hebben alleen een `.vsa`-bestand, dus
alleen de melodie. Voor die stukken zoekt het script de eerste noot en
schrijft die naar `data\inzet-melodie.json`. VSA-tooling rekent de
toonhoogte uit.

Het bestand `data\inzet-melodie.json` staat niet in git en wordt bij elke
bouw opnieuw gemaakt. `fix` en de productcontroles kijken er niet naar.

# MELDINGEN

Het script meldt hoeveel stukken een beginnoot kregen. Staat er een
`WAARSCHUWING` met de naam van een stuk, dan kon VSA-tooling de noot niet
bepalen. De site bouwt gewoon; dat ene stuk heeft dan geen knop **Inzet**.
Controleer de `.vsa` met `vsa validate`.
