"""check_mvsa: sectie-producten ook als products-meta «ok» is."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import check_mvsa_products as check
from check_fixlist import collect_items


def test_check_one_reports_missing_sectie_when_meta_ok(tmp_path: Path) -> None:
    """Meta voor hele-stuk-producten mag sectie-SVG/from-ir niet verbergen."""
    leaf = tmp_path / "content-source" / "catalogus" / "z" / "v" / "u"
    leaf.mkdir(parents=True)
    mvsa = leaf / "lied.mvsa"
    mvsa.write_text("@sectie a\nL: x |\nS: do |\n", encoding="utf-8")

    def fake_meta_ok(bron, *, required_keys, rel, stamp_issues, issue_cls):
        return []

    with (
        mock.patch.object(check, "REPO_ROOT", tmp_path),
        mock.patch.object(check, "source_sha256", return_value="digest"),
        mock.patch.object(check, "issues_from_meta_or", side_effect=fake_meta_ok),
        mock.patch(
            "ensure_bibliotheek_id.id_from_catalogus_path",
            return_value="z/v/u",
        ),
    ):
        status = check.check_one(
            mvsa, sectie_refs={"z/v/u": {"a"}}
        )

    kinds = {i.kind for i in status.issues}
    assert "missing_sectie_svg" in kinds
    assert "missing_sectie_from_ir" in kinds
    assert not status.ok


def test_two_mvsa_in_one_leaf_both_stay_on_fixlist(tmp_path: Path) -> None:
    """Ok-bestand ná het falende mag de status-JSON niet wissen."""
    leaf = "catalogus/z/v/u"
    bad_src = f"{leaf}/ektinia-slot.mvsa"
    statuses = [
        check.FolderStatus(
            dir=leaf,
            source=bad_src,
            ok=False,
            issues=[
                check.Issue(
                    "meta_missing",
                    f"{bad_src}.products-meta.json",
                    "meta ontbreekt of incompleet",
                )
            ],
            fix_cmd=(
                r"scripts\products.cmd --kinds mvsa "
                r"--reasons missing,stale --skip-post ektinia-slot.mvsa"
            ),
        ),
        check.FolderStatus(
            dir=leaf,
            source=f"{leaf}/goed.mvsa",
            ok=True,
            issues=[],
            fix_cmd=r"scripts\products.cmd --kinds mvsa goed.mvsa",
        ),
    ]
    data = tmp_path / "data"
    data.mkdir()
    status_path = data / "mvsa-product-status.json"
    check.write_status_json(statuses, status_path)
    raw = json.loads(status_path.read_text(encoding="utf-8"))
    assert raw["folders"][bad_src]["ok"] is False
    assert raw["folders"][f"{leaf}/goed.mvsa"]["ok"] is True
    items = collect_items(data)
    assert len(items) == 1
    assert items[0].id == f"mvsa:{bad_src}"
    assert "ektinia-slot.mvsa" in items[0].fix_cmd
