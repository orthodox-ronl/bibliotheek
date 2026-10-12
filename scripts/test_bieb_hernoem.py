"""Tests voor bieb hernoem (id-resolutie + veilige rewrite)."""

from __future__ import annotations

from pathlib import Path

import bieb_hernoem as bh
import catalogus as cat


def test_resolve_existing_zangstuk() -> None:
    level, slash = cat.resolve_existing_ref("tropaar")
    assert level == "zangstuk"
    assert slash == "tropaar"


def test_resolve_existing_variant_slash_and_stem() -> None:
    level, slash = cat.resolve_existing_ref("tropaar/zondag-toon-1")
    assert level == "variant"
    assert slash == "tropaar/zondag-toon-1"
    level2, slash2 = cat.resolve_existing_ref("tropaar-zondag-toon-1")
    assert (level2, slash2) == (level, slash)


def test_resolve_existing_leaf_stem() -> None:
    level, slash = cat.resolve_existing_ref(
        "kondak-johannes-de-theoloog-toon-2-liturgikon"
    )
    assert level == "leaf"
    assert slash == "kondak/johannes-de-theoloog-toon-2/liturgikon"


def test_complete_new_leaf_short() -> None:
    level, slash = cat.complete_new_ref(
        "leaf",
        "kondak/johannes-de-theoloog-toon-2/liturgikon",
        "hemelum",
    )
    assert level == "leaf"
    assert slash == "kondak/johannes-de-theoloog-toon-2/hemelum"


def test_complete_new_variant_short() -> None:
    level, slash = cat.complete_new_ref(
        "variant",
        "tropaar/zondag-toon-1",
        "zondag-toon-9",
    )
    assert level == "variant"
    assert slash == "tropaar/zondag-toon-9"


def test_rewrite_skips_title_reports_doubt() -> None:
    text = (
        '---\ntitle: "tropaar/zondag-toon-1/hemelum"\n'
        'linkTitle: "Hemelum"\n---\n'
        '{{< bieb id="tropaar/zondag-toon-1/hemelum" >}}\n'
    )
    updated, doubt = bh._rewrite_text(
        text,
        "tropaar/zondag-toon-1/hemelum",
        "tropaar/zondag-toon-1/groningen",
        level="leaf",
    )
    assert 'bieb id="tropaar/zondag-toon-1/groningen"' in updated
    assert 'title: "tropaar/zondag-toon-1/hemelum"' in updated
    assert any("title:" in d for d in doubt)


def test_hernoem_leaf_dry_run(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    cat_root = root / "content-source" / "catalogus"
    leaf = cat_root / "demo" / "var" / "hemelum"
    leaf.mkdir(parents=True)
    (leaf / "index.md").write_text(
        '---\ntitle: "x"\nlinkTitle: "Hemelum"\n---\n'
        '{{< bieb id="demo/var/hemelum" >}}\n',
        encoding="utf-8",
    )
    (leaf / "demo-var-hemelum.vsa").write_text(
        "---\ntitel: Test\n---\n[/:] a [:]\n", encoding="utf-8"
    )
    koor = root / "content-source" / "koormappen" / "x" / "demo-var-hemelum"
    koor.mkdir(parents=True)
    (koor / "index.md").write_text("# slot\n", encoding="utf-8")

    monkeypatch.setattr(cat, "CATALOGUS_ROOT", cat_root)
    monkeypatch.setattr(cat, "REPO_ROOT", root)
    monkeypatch.setattr(bh, "REPO_ROOT", root)
    monkeypatch.setattr(bh, "KOORMAPPEN_ROOT", root / "content-source" / "koormappen")

    code = bh.hernoem("demo/var/hemelum", "groningen", dry_run=True)
    assert code == 0
    assert leaf.is_dir()
    assert (leaf / "demo-var-hemelum.vsa").is_file()
