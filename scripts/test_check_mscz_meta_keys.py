"""check_mscz: alleen mxl/svg in meta-required_keys (geen verplichte pdf)."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import check_mscz_products as check


def test_mscz_meta_keys_single_svg() -> None:
    mscz = Path("a/lied.mscz")
    with mock.patch.object(check, "mscz_svg_outputs", return_value=[Path("a/lied.mscz.svg")]):
        assert check._mscz_meta_keys(mscz) == {"mxl", "svg"}


def test_mscz_meta_keys_multi_svg() -> None:
    mscz = Path("a/lied.mscz")
    outs = [Path("a/lied.mscz-1.svg"), Path("a/lied.mscz-2.svg")]
    with mock.patch.object(check, "mscz_svg_outputs", return_value=outs):
        assert check._mscz_meta_keys(mscz) == {"mxl", "svg-1"}


def test_check_one_passes_mxl_svg_required_keys(tmp_path: Path) -> None:
    mscz = tmp_path / "lied.mscz"
    mscz.write_bytes(b"PK")
    captured: dict = {}

    def fake_issues(bron, *, required_keys, rel, stamp_issues, issue_cls):
        captured["keys"] = set(required_keys)
        return []

    with (
        mock.patch.object(check, "partituur_sha256", return_value="d"),
        mock.patch.object(check, "issues_from_meta_or", side_effect=fake_issues),
        mock.patch.object(check, "REPO_ROOT", tmp_path),
        mock.patch.object(
            check, "mscz_svg_outputs", return_value=[tmp_path / "lied.mscz.svg"]
        ),
    ):
        status = check.check_one(mscz)

    assert status.ok
    assert captured["keys"] == {"mxl", "svg"}
    assert "pdf" not in captured["keys"]


def test_write_products_meta_forwards_drop_keys(tmp_path: Path) -> None:
    import street_meta as sm

    bron = tmp_path / "lied.mscz"
    bron.write_bytes(b"PK")
    mxl = tmp_path / "lied.mscz.mxl"
    mxl.write_bytes(b"PK")
    with mock.patch("vsa.products_meta.write_meta") as write_meta:
        write_meta.return_value = tmp_path / "lied.mscz.products-meta.json"
        sm.write_products_meta(
            bron, {"mxl": mxl}, merge=True, drop_keys={"pdf"}
        )
    write_meta.assert_called_once()
    assert write_meta.call_args.kwargs.get("drop_keys") == {"pdf"}
