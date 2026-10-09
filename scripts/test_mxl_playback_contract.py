"""Unit tests for check_mxl_playback_contract helpers."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from check_mxl_playback_contract import (
    collect_coria_mxl,
    has_coria_source_encoding_clash,
    profile_for_coria_mxl,
)


def test_profile_for_coria_mxl():
    assert profile_for_coria_mxl(Path("a.vsa.mxl")) == "mono"
    assert profile_for_coria_mxl(Path("a.mscz.mxl")) == "satb"
    assert profile_for_coria_mxl(Path("a.mvsa.mxl")) == "satb"
    assert profile_for_coria_mxl(Path("legacy.mxl")) is None
    assert profile_for_coria_mxl(Path("a.mscz.mvsa")) is None


def _mxl_bytes(score_xml: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?><container><rootfiles>'
            '<rootfile full-path="score.xml"/></rootfiles></container>',
        )
        z.writestr("score.xml", score_xml.encode("utf-8"))
    return buf.getvalue()


def test_has_coria_source_encoding_clash(tmp_path: Path):
    bad = tmp_path / "bad.vsa.mxl"
    bad.write_bytes(
        _mxl_bytes(
            """<?xml version="1.0"?>
<score-partwise version="3.1">
  <identification>
    <source>X</source>
    <encoding><software>t</software></encoding>
  </identification>
  <part-list><score-part id="P1"><part-name>V</part-name></score-part></part-list>
  <part id="P1"><measure number="1"/></part>
</score-partwise>
"""
        )
    )
    good = tmp_path / "good.vsa.mxl"
    good.write_bytes(
        _mxl_bytes(
            """<?xml version="1.0"?>
<score-partwise version="3.1">
  <identification>
    <encoding><software>t</software></encoding>
    <miscellaneous>
      <miscellaneous-field name="bron">X</miscellaneous-field>
    </miscellaneous>
  </identification>
  <part-list><score-part id="P1"><part-name>V</part-name></score-part></part-list>
  <part id="P1"><measure number="1"/></part>
</score-partwise>
"""
        )
    )
    assert has_coria_source_encoding_clash(bad) is True
    assert has_coria_source_encoding_clash(good) is False


def test_collect_skips_input_and_handmatig(tmp_path: Path):
    root = tmp_path / "bibliotheek"
    good = root / "lied" / "koor"
    good.mkdir(parents=True)
    (good / "index.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")
    (good / "lied.vsa.mxl").write_bytes(b"PK")
    (good / "lied.mscz.mxl").write_bytes(b"PK")

    manual = root / "hand"
    manual.mkdir(parents=True)
    (manual / "index.md").write_text(
        "---\nartefacten_handmatig: true\n---\n", encoding="utf-8"
    )
    (manual / "oud.vsa.mxl").write_bytes(b"PK")

    inp = root / "input" / "raw"
    inp.mkdir(parents=True)
    (inp / "x.vsa.mxl").write_bytes(b"PK")

    found = collect_coria_mxl(root)
    names = sorted(p.name for p, _ in found)
    assert names == ["lied.mscz.mxl", "lied.vsa.mxl"]
    by_name = {p.name: profile for p, profile in found}
    assert by_name["lied.vsa.mxl"] == "mono"
    assert by_name["lied.mscz.mxl"] == "satb"
