---
title: "bump-vsa-tooling-pin"
linkTitle: "bump-vsa-tooling-pin"
weight: 125
---

# NAME

`scripts\bump-vsa-tooling-pin.cmd` — productie-pin naar VSA-tooling bijwerken

# SYNOPSIS

```cmd
scripts\bump-vsa-tooling-pin.cmd
scripts\bump-vsa-tooling-pin.cmd --dry-run
scripts\bump-vsa-tooling-pin.cmd 0.2.0
scripts\bump-vsa-tooling-pin.cmd --ref main
```

# DESCRIPTION

Productie-CI op bibliotheek-`main` installeert `vsa-tool` vanaf de commit in
[`vsa-tooling.pin`](https://github.com/orthodox-ronl/bibliotheek/blob/main/vsa-tooling.pin).
Dit script haalt via `gh` de SHA van `orthodox-ronl/VSA-tooling` op (standaard
de tip van `main`) en schrijft die naar het pin-bestand.

Het script **commit niet**. Na een bump: commit + PR naar bibliotheek-`main`.

Branch **`development`** floatt al op tooling-`main`; daar hoef je de pin niet
te zetten voor preview.

Vereist: [GitHub CLI](https://cli.github.com/) (`gh`), ingelogd.

# OPTIONS

| Optie       | Betekenis                                              |
| ----------- | ------------------------------------------------------ |
| `ref`       | Branch, tag of SHA op VSA-tooling (default: `main`)    |
| `--ref REF` | Zelfde als positionele `ref`                           |
| `--dry-run` | Toon oud/nieuw; schrijf `vsa-tooling.pin` niet         |

# WHEN

Nadat gewenste wijzigingen op VSA-tooling-`main` staan (of een release-tag)
en productie die tooling mag gebruiken.

# SEE ALSO

- [Tooling-koppeling](https://github.com/orthodox-ronl/bibliotheek/blob/main/docs/tooling-koppeling.md)
- [VSA-tooling — Releases en pinnen](https://orthodox-ronl.github.io/VSA-tooling/manuals/releases/)
