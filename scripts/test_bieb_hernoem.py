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


def test_normalize_backslash_and_repo_prefix() -> None:
    assert (
        cat.normalize_ref_input(
            r"cherubijnenhymne\15c-kastorski\hemelum-ksl-trlat"
        )
        == "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat"
    )
    assert (
        cat.normalize_ref_input(
            r"content-source\catalogus\cherubijnenhymne\15c-kastorski\hemelum-ksl-trlat"
        )
        == "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat"
    )


def test_resolve_existing_backslash_path() -> None:
    level, slash = cat.resolve_existing_ref(
        r"cherubijnenhymne\15c-kastorski\hemelum-ksl-trlat"
    )
    assert level == "leaf"
    assert slash == "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat"


def test_resolve_existing_repo_relative_path() -> None:
    level, slash = cat.resolve_existing_ref(
        r"content-source\catalogus\cherubijnenhymne\15c-kastorski\hemelum-ksl-trlat"
    )
    assert (level, slash) == (
        "leaf",
        "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat",
    )


def test_resolve_existing_unique_variant_uv_suffix() -> None:
    level, slash = cat.resolve_existing_ref(
        r"15c-kastorski\hemelum-ksl-trlat"
    )
    assert level == "leaf"
    assert slash == "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat"
    level2, slash2 = cat.resolve_existing_ref(
        "15c-kastorski-hemelum-ksl-trlat"
    )
    assert (level2, slash2) == (level, slash)


def test_resolve_existing_ambiguous_uv_only() -> None:
    try:
        cat.resolve_existing_ref("hemelum")
    except cat.AmbiguousRefError as exc:
        assert len(exc.options) > 1
    else:
        raise AssertionError("verwacht AmbiguousRefError voor hemelum")


def test_complete_new_leaf_short() -> None:
    level, slash = cat.complete_new_ref(
        "leaf",
        "kondak/johannes-de-theoloog-toon-2/liturgikon",
        "hemelum",
    )
    assert level == "leaf"
    assert slash == "kondak/johannes-de-theoloog-toon-2/hemelum"


def test_complete_new_leaf_short_with_dashes() -> None:
    level, slash = cat.complete_new_ref(
        "leaf",
        "ektinia/vredes/hemelum",
        "hemelum-ksl-trlat",
    )
    assert (level, slash) == ("leaf", "ektinia/vredes/hemelum-ksl-trlat")


def test_complete_new_leaf_variant_uv_slash() -> None:
    level, slash = cat.complete_new_ref(
        "leaf",
        "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat",
        r"15c-kastorski\groningen",
    )
    assert (level, slash) == (
        "leaf",
        "cherubijnenhymne/15c-kastorski/groningen",
    )


def test_complete_new_leaf_variant_uv_dash() -> None:
    level, slash = cat.complete_new_ref(
        "leaf",
        "cherubijnenhymne/15c-kastorski/hemelum-ksl-trlat",
        "15c-kastorski-groningen",
    )
    assert (level, slash) == (
        "leaf",
        "cherubijnenhymne/15c-kastorski/groningen",
    )


def test_complete_new_leaf_repo_path() -> None:
    level, slash = cat.complete_new_ref(
        "leaf",
        "ektinia/vredes/hemelum",
        r"content-source\catalogus\ektinia\vredes\groningen",
    )
    assert (level, slash) == ("leaf", "ektinia/vredes/groningen")


def test_complete_new_variant_short() -> None:
    level, slash = cat.complete_new_ref(
        "variant",
        "tropaar/zondag-toon-1",
        "zondag-toon-9",
    )
    assert level == "variant"
    assert slash == "tropaar/zondag-toon-9"


def test_interactive_disambiguate_enter_picks_first(monkeypatch) -> None:
    exc = cat.AmbiguousRefError(
        "hemelum",
        [("leaf", "a/b/hemelum"), ("leaf", "c/d/hemelum")],
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": "")
    assert cat.interactive_disambiguate(exc, help_text="help") == (
        "leaf",
        "a/b/hemelum",
    )


def test_interactive_disambiguate_number(monkeypatch) -> None:
    exc = cat.AmbiguousRefError(
        "hemelum",
        [("leaf", "a/b/hemelum"), ("leaf", "c/d/hemelum")],
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": "2")
    assert cat.interactive_disambiguate(exc, help_text="help") == (
        "leaf",
        "c/d/hemelum",
    )


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
