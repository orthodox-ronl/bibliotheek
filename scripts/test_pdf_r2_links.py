"""Templates voor de blad-PDF-links (docs/plans/pdf-r2.md).

Hugo maakt sleutels onder ``params`` klein (``isset`` is hoofdlettergevoelig)
en houdt de koppeltekens van een databestand. Beide fouten stuurden elke
download op de preview naar R2 ``production/`` (404).
"""

from __future__ import annotations

import re
from pathlib import Path

PARTIALS = Path(__file__).resolve().parents[1] / "layouts" / "partials"
NAMEN = ("pdf-asset-url.html", "pdf-r2-development-banner.html", "pagina-acties.html")


def test_isset_met_kleine_letters() -> None:
    for naam in NAMEN:
        tekst = (PARTIALS / naam).read_text(encoding="utf-8")
        for sleutel in re.findall(r'isset \$\w*[Cc]fg "(\w+)"', tekst):
            assert sleutel == sleutel.lower(), f"{naam}: isset {sleutel}"


def test_manifest_met_bestandsnaam() -> None:
    for naam in NAMEN[:2]:
        tekst = (PARTIALS / naam).read_text(encoding="utf-8")
        assert '"pdf-r2-development"' in tekst, naam
        assert "Data.pdf_r2_development" not in tekst, naam
