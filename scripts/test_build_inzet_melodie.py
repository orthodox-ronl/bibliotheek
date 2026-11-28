from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("vsa")

from build_inzet_melodie import beginnoot, melodie_bron  # noqa: E402

VSA = "---\ndo: F4\nmode: major\n---\n\n[//:] Ik {zal_} [//:]\n"


def test_alleen_vsa_zonder_vier_stemmen(tmp_path: Path) -> None:
    bron = tmp_path / "stuk.vsa"
    bron.write_text(VSA, encoding="utf-8")
    assert melodie_bron(tmp_path) == bron
    # [//:] begint twee tonen boven do (F): A
    assert beginnoot(bron) == {"midi": 69, "do": "F"}


def test_geen_melodie_bij_vier_stemmen_of_andere_bron(tmp_path: Path) -> None:
    (tmp_path / "stuk.vsa").write_text(VSA, encoding="utf-8")
    ir = tmp_path / "stuk.vsa.mvsa.from-ir.musicxml"
    ir.write_text("<x/>", encoding="utf-8")
    assert melodie_bron(tmp_path) is None
    ir.unlink()
    (tmp_path / "stuk.mscz").write_bytes(b"")
    assert melodie_bron(tmp_path) is None
