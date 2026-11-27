"""Unit tests for check_fixlist + fix dry-run (geen MuseScore/Hugo)."""

from __future__ import annotations

import json
from pathlib import Path

import fix as fix_mod
from check_fixlist import (
    FixItem,
    _rel_content_source,
    fix_sort_key,
    collect_items,
    load_fixlist,
    save_fixlist,
    write_fixlist,
)


def test_ensure_yes_flag_appends_once() -> None:
    cmd = r"scripts\pdf.cmd catalogus\a\index.md"
    assert fix_mod._ensure_yes_flag(cmd) == cmd + " -y"
    assert fix_mod._ensure_yes_flag(cmd + " -y") == cmd + " -y"
    assert fix_mod._ensure_yes_flag(cmd + " --yes") == cmd + " --yes"


def test_extract_child_failure_reason_from_mislukt_block() -> None:
    text = """
=== products: kinds=vsa ===
Batch «products»: products: 1 kind(s)
Bevestiging: overgeslagen (-y/--yes).
>>> vsa
  1  bijwerken (van 1)
  1  mislukt-vsa
=== Samenvatting products ===
  1  kinds-mislukt
MISLUKT catalogus/tropaar/uw-heilig-kruis/groningen/x.vsa
  hoogte-mismatch op lettergreep 'Uw' (klinkend E4).
  Oplossing: herstel de fout hierboven en draai opnieuw.
"""
    assert (
        fix_mod._extract_child_failure_reason(text)
        == "hoogte-mismatch op lettergreep 'Uw' (klinkend E4)."
    )


def test_extract_child_failure_reason_keeps_file_line_col() -> None:
    text = """
MISLUKT catalogus/tropaar/x/y/lied.vsa
  catalogus/tropaar/x/y/lied.vsa:29:28: hoogte-mismatch op lettergreep 'door' (klinkend G4).
  Oplossing: Zet ** op de regel ervoor.
"""
    reason = fix_mod._extract_child_failure_reason(text)
    assert reason.startswith("catalogus/tropaar/x/y/lied.vsa:29:28:")
    assert "door" in reason


def test_item_path_label_prefers_vsa_from_fix_cmd() -> None:
    item = FixItem(
        id="vsa:a",
        checker="vsa",
        summary="[meta-missing] catalogus/tropaar/x/y",
        fix_cmd=(
            r"scripts\products.cmd --kinds vsa --skip-post "
            r"catalogus\tropaar\x\y\lied.vsa"
        ),
        kind="meta_missing",
        file="catalogus/tropaar/x/y/lied.vsa.products-meta.json",
        source="catalogus/tropaar/x/y",
    )
    assert (
        fix_mod._item_path_label(item)
        == "catalogus/tropaar/x/y/lied.vsa"
    )


def test_extract_child_failure_reason_meerdere_templates() -> None:
    text = """
VSA-tooling: mode=float ref=main
MISLUKT catalogus/kondak/silouan/asten/x.vsa
  meerdere templates voor soort='kondak' toon=8: a, b. Geef --template.
  Oplossing: herstel de fout hierboven.
"""
    reason = fix_mod._extract_child_failure_reason(text)
    assert reason.startswith("meerdere templates")
    assert fix_mod._failure_group(reason) == "meerdere templates"


def test_failure_group_template_slots() -> None:
    reason = "verplicht(e) template-slot(s) niet aangedaan in frase '1': ti-1."
    assert fix_mod._failure_group(reason) == "template-slots"


def test_item_path_label_from_summary() -> None:
    item = FixItem(
        id="vsa:a",
        checker="vsa",
        summary="[meta-missing] catalogus/tropaar/x/y",
        fix_cmd="products x",
        kind="meta_missing",
    )
    assert fix_mod._item_path_label(item) == "catalogus/tropaar/x/y"


def _write_pdf_status(data_dir: Path, *, stale: bool) -> None:
    folders = {
        "catalogus/x/ok": {
            "source": "content-source/catalogus/x/ok/index.md",
            "ok": True,
            "fix_cmd": r"scripts\pdf.cmd content-source\catalogus\x\ok\index.md",
            "issues": [],
        },
    }
    if stale:
        folders["catalogus/x/stale"] = {
            "source": "content-source/catalogus/x/stale/index.md",
            "ok": False,
            "fix_cmd": (
                r"scripts\pdf.cmd content-source\catalogus\x\stale\index.md"
            ),
            "issues": [
                {
                    "kind": "stale_pdf",
                    "file": "content-source/catalogus/x/stale/index.md.pdf",
                    "detail": "ouder dan bron",
                }
            ],
        }
    (data_dir / "pdf-status.json").write_text(
        json.dumps({"folders": folders}, indent=2) + "\n",
        encoding="utf-8",
    )


def test_rel_content_source():
    assert (
        _rel_content_source(
            "content-source/catalogus/x/index.md.pdf"
        )
        == "catalogus/x/index.md.pdf"
    )
    assert _rel_content_source(r"content-source\koormappen\a\index.md") == (
        "koormappen/a/index.md"
    )


def test_collect_only_not_ok(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    _write_pdf_status(data, stale=True)
    items = collect_items(data)
    assert len(items) == 1
    assert items[0].checker == "pdf"
    assert items[0].kind == "stale_pdf"
    assert items[0].summary == "[stale-pdf] catalogus/x/stale"
    assert "pdf.cmd" in items[0].fix_cmd


def test_write_and_load_roundtrip(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    _write_pdf_status(data, stale=True)
    out = tmp_path / "check-fixlist.json"
    items = write_fixlist(path=out, data_dir=data)
    assert len(items) == 1
    loaded = load_fixlist(out)
    assert loaded[0].id == items[0].id
    assert loaded[0].fix_cmd == items[0].fix_cmd


def test_save_removes_item(tmp_path: Path):
    path = tmp_path / "check-fixlist.json"
    items = [
        FixItem(
            id="pdf:a",
            checker="pdf",
            summary="a",
            fix_cmd=r"scripts\pdf.cmd a\index.md",
        ),
        FixItem(
            id="pdf:b",
            checker="pdf",
            summary="b",
            fix_cmd=r"scripts\pdf.cmd b\index.md",
        ),
    ]
    save_fixlist(items, path=path)
    save_fixlist(items[1:], path=path)
    left = load_fixlist(path)
    assert [x.id for x in left] == ["pdf:b"]


def test_fix_dry_run_prints(tmp_path: Path, monkeypatch, capsys):
    path = tmp_path / "check-fixlist.json"
    save_fixlist(
        [
            FixItem(
                id="pdf:a",
                checker="pdf",
                summary="[stale_pdf] x",
                fix_cmd=r"scripts\pdf.cmd x\index.md",
            )
        ],
        path=path,
    )
    monkeypatch.setattr(fix_mod, "FIXLIST_PATH", path)
    monkeypatch.setattr(
        "check_fixlist.FIXLIST_PATH",
        path,
    )
    # load_fixlist uses FIXLIST_PATH from check_fixlist at call time
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    code = fix_mod.main(["--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert "pdf.cmd" in out
    assert "dry-run" in out.lower()


def test_fix_check_dry_run_refreshes(tmp_path: Path, monkeypatch, capsys):
    data = tmp_path / "data"
    data.mkdir()
    _write_pdf_status(data, stale=True)
    out = tmp_path / "check-fixlist.json"

    times = {"n": 0}

    def fake_mtime() -> float:
        times["n"] += 1
        # vóór check: 1.0; ná check: 2.0 (verse lijst)
        return 1.0 if times["n"] == 1 else 2.0

    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 1)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", fake_mtime)
    monkeypatch.setattr(
        fix_mod,
        "_refresh_fixlist_from_status",
        lambda: write_fixlist(path=out, data_dir=data),
    )
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(out))

    code = fix_mod.main(["--check", "--dry-run"])
    assert code == 0
    assert out.is_file()
    assert len(load_fixlist(out)) == 1
    assert "stale-pdf" in capsys.readouterr().out


def test_fix_check_hard_fail_exit2(monkeypatch):
    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 2)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", lambda: 1.0)
    assert fix_mod.main(["--check", "--dry-run"]) == 2


def test_fix_strict_alias_runs_check(monkeypatch):
    """--strict is hetzelfde als --check."""
    called = {"n": 0}
    times = {"n": 0}

    def _fake_check(**_k):
        called["n"] += 1
        return 0

    def fake_mtime() -> float:
        times["n"] += 1
        return 1.0 if times["n"] == 1 else 2.0

    monkeypatch.setattr(fix_mod, "_run_check_strict", _fake_check)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", fake_mtime)
    monkeypatch.setattr(fix_mod, "_refresh_fixlist_from_status", lambda: [])
    assert fix_mod.main(["--strict", "--dry-run"]) == 0
    assert called["n"] == 1


def test_fix_check_hard_fail_stale_list(monkeypatch):
    """Exit 1 maar fixlist niet vernieuwd (bijv. validate-stop) → stop."""
    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 1)
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", lambda: 10.0)
    assert fix_mod.main(["--check", "--dry-run"]) == 2


def test_fix_run_removes_success(tmp_path: Path, monkeypatch):
    path = tmp_path / "check-fixlist.json"
    save_fixlist(
        [
            FixItem(
                id="pdf:a",
                checker="pdf",
                summary="a",
                fix_cmd=r"scripts\pdf.cmd a\index.md",
            ),
            FixItem(
                id="pdf:b",
                checker="pdf",
                summary="b",
                fix_cmd=r"scripts\pdf.cmd b\index.md",
            ),
        ],
        path=path,
    )
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    monkeypatch.setattr(
        fix_mod,
        "save_fixlist",
        lambda items: save_fixlist(items, path=path),
    )
    monkeypatch.setattr(
        fix_mod, "_run_fix_cmd", lambda *_a, **_k: (0, "")
    )
    monkeypatch.setattr(
        fix_mod,
        "confirm_batch",
        lambda *_a, **_k: True,
    )
    assert fix_mod.main(["-y"]) == 0
    assert load_fixlist(path) == []


def test_fix_skips_duplicate_fix_cmd(tmp_path: Path, monkeypatch):
    """Zelfde fix_cmd op meerdere regels: één keer uitvoeren."""
    path = tmp_path / "check-fixlist.json"
    shared = r"scripts\products.cmd --kinds mvsa --skip-post a.mvsa"
    save_fixlist(
        [
            FixItem(
                id="mvsa:a",
                checker="mvsa",
                summary="a",
                fix_cmd=shared,
            ),
            FixItem(
                id="mvsa:a2",
                checker="mvsa",
                summary="a2",
                fix_cmd=shared,
            ),
        ],
        path=path,
    )
    calls: list[str] = []

    def _run(cmd: str, **_k) -> tuple[int, str]:
        calls.append(cmd)
        return 0, ""

    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    monkeypatch.setattr(
        fix_mod,
        "save_fixlist",
        lambda items: save_fixlist(items, path=path),
    )
    monkeypatch.setattr(fix_mod, "_run_fix_cmd", _run)
    monkeypatch.setattr(fix_mod, "_run_products_post", lambda **_k: 0)
    monkeypatch.setattr(fix_mod, "confirm_batch", lambda *_a, **_k: True)
    assert fix_mod.main(["-y"]) == 0
    assert calls == [shared]
    assert load_fixlist(path) == []


def test_fix_failure_summary_is_grouped(tmp_path: Path, monkeypatch, capsys):
    """Mislukte fixes: geen dump; eindsamenvatting gegroepeerd."""
    path = tmp_path / "check-fixlist.json"
    save_fixlist(
        [
            FixItem(
                id="vsa:a",
                checker="vsa",
                summary="[meta-missing] catalogus/tropaar/a/x",
                fix_cmd=r"scripts\products.cmd --kinds vsa a.vsa",
                kind="meta_missing",
            ),
            FixItem(
                id="vsa:b",
                checker="vsa",
                summary="[meta-missing] catalogus/tropaar/b/y",
                fix_cmd=r"scripts\products.cmd --kinds vsa b.vsa",
                kind="meta_missing",
            ),
        ],
        path=path,
    )

    def _run(cmd: str, **_k) -> tuple[int, str]:
        if "a.vsa" in cmd:
            return 1, "hoogte-mismatch op lettergreep 'Uw' (klinkend E4)."
        return 1, "meerdere templates voor soort='tropaar' toon=4: a, b."

    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    monkeypatch.setattr(
        fix_mod,
        "save_fixlist",
        lambda items: save_fixlist(items, path=path),
    )
    monkeypatch.setattr(fix_mod, "_run_fix_cmd", _run)
    monkeypatch.setattr(fix_mod, "confirm_batch", lambda *_a, **_k: True)
    assert fix_mod.main(["-y"]) == 1
    out = capsys.readouterr().out
    assert "Rest (handwerk), gegroepeerd:" in out
    assert "hoogte-mismatch" in out
    assert "meerdere templates" in out
    assert "catalogus/tropaar/a/x" in out
    assert "Batch «products»" not in out


def test_fix_verbose_writes_detail_log(tmp_path: Path, monkeypatch, capsys):
    """--verbose: scherm kort; details in data/fix-last.log."""
    path = tmp_path / "check-fixlist.json"
    log = tmp_path / "fix-last.log"
    save_fixlist(
        [
            FixItem(
                id="pdf:a",
                checker="pdf",
                summary="[stale-pdf] catalogus/x/a",
                fix_cmd=r"scripts\pdf.cmd a\index.md",
                kind="stale_pdf",
            ),
        ],
        path=path,
    )

    def _run(cmd: str, **kwargs) -> tuple[int, str]:
        log_path = kwargs.get("log_path")
        assert log_path is not None
        fix_mod._append_fix_log(
            log_path,
            summary=kwargs.get("summary") or "x",
            cmd=cmd,
            code=1,
            stdout=(
                "=== products banner ===\n"
                "MISLUKT a\n"
                "  hoogte-mismatch op 'Uw'.\n"
            ),
            stderr="",
            elapsed_s=0.1,
        )
        return 1, "hoogte-mismatch op 'Uw'."

    open_orig = fix_mod._open_fix_log
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    monkeypatch.setattr(
        fix_mod,
        "save_fixlist",
        lambda items: save_fixlist(items, path=path),
    )
    monkeypatch.setattr(fix_mod, "_open_fix_log", lambda: open_orig(log))
    monkeypatch.setattr(fix_mod, "_run_fix_cmd", _run)
    monkeypatch.setattr(fix_mod, "confirm_batch", lambda *_a, **_k: True)

    assert fix_mod.main(["-y", "--verbose"]) == 1
    out = capsys.readouterr().out
    assert "Detail-log:" in out
    assert "=== products banner ===" not in out
    text = log.read_text(encoding="utf-8")
    assert "=== products banner ===" in text
    assert "hoogte-mismatch" in text


def test_fix_volgorde_pdf_na_producten() -> None:
    """pdf moet ná de producten (anders is de pdf direct weer stale)."""
    mk = lambda c: FixItem(id=f"{c}:x", checker=c, summary="s", fix_cmd="c")
    items = [mk("pdf"), mk("audio"), mk("mvsa"), mk("vsa"), mk("mxl-contract")]
    assert [i.checker for i in sorted(items, key=fix_sort_key)] == [
        "vsa",
        "mvsa",
        "audio",
        "mxl-contract",
        "pdf",
    ]


def test_products_post_zet_gebreken_stempels(monkeypatch) -> None:
    """De fix-nabewerking moet de gebreken-stempels op SVG's zetten.

    De fix-commando's lopen met ``--skip-post``; zonder deze stap meldt
    check daarna "SVG mist stempel".
    """
    import sys
    import types

    import gebreken

    calls: list[object] = []
    monkeypatch.setattr(
        gebreken,
        "sync_gebreken_stempels_under",
        lambda root: (calls.append(root), (1, 2, 3))[1],
    )
    zoek = types.ModuleType("build_zoek_index")
    zoek.main = lambda _argv=None: 0
    fp = types.ModuleType("fingerprint_coria_mxl")
    fp.main = lambda: 0
    probe = types.ModuleType("probe_coria_fetch")
    probe.apply_probe = lambda warn_only=True: 0
    monkeypatch.setitem(sys.modules, "build_zoek_index", zoek)
    monkeypatch.setitem(sys.modules, "fingerprint_coria_mxl", fp)
    monkeypatch.setitem(sys.modules, "probe_coria_fetch", probe)

    assert fix_mod._run_products_post(verbose=True) == 0
    assert calls == [gebreken.CATALOGUS_ROOT]


def test_gebreken_status_komt_in_fixlist_voor_pdf(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "gebreken-status.json").write_text(
        json.dumps(
            {
                "folders": {
                    "catalogus/x/y": {
                        "source": "catalogus/x/y/index.md",
                        "ok": False,
                        "fix_cmd": r"python scripts\gebreken.py catalogus\x\y",
                        "issues": [
                            {
                                "kind": "stempel_ontbreekt",
                                "file": "catalogus/x/y/a.vsa.svg",
                                "detail": "mist stempel",
                            }
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    _write_pdf_status(data, stale=True)
    items = sorted(collect_items(data), key=fix_sort_key)
    assert [i.checker for i in items] == ["gebreken", "pdf"]
    assert items[0].fix_cmd.startswith("python scripts\\gebreken.py ")
    assert items[0].summary == "[stempel-ontbreekt] catalogus/x/y"


def test_collect_gebreken_statuses(monkeypatch, tmp_path: Path) -> None:
    import gebreken

    leaf = tmp_path / "content-source" / "catalogus" / "x" / "y"
    leaf.mkdir(parents=True)
    (leaf / "index.md").write_text("x", encoding="utf-8")
    svg = leaf / "a.vsa.svg"
    svg.write_text("<svg/>", encoding="utf-8")
    pdf = leaf / "index.md.pdf"
    pdf.write_bytes(b"%PDF")
    monkeypatch.setattr(gebreken, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gebreken, "leaf_folders", lambda: [("x/y", leaf)])
    monkeypatch.setattr(
        gebreken, "effective_gebreken_for_folder", lambda _f: (True, None)
    )
    monkeypatch.setattr(gebreken, "svg_has_gebreken_stempel", lambda _s: False)
    monkeypatch.setattr(gebreken, "pdf_has_gebreken_stempel", lambda _p: False)

    statuses, n = gebreken.collect_gebreken_statuses()
    assert n == 1
    assert [s.dir for s in statuses] == ["catalogus/x/y", "catalogus/x/y (pdf)"]
    assert statuses[0].fix_cmd == r"python scripts\gebreken.py catalogus\x\y"
    assert statuses[0].issues[0].kind == "stempel_ontbreekt"
    assert statuses[1].fix_cmd == r"scripts\pdf.cmd catalogus\x\y\index.md --force"

    # Stempels aanwezig → niets te doen.
    monkeypatch.setattr(gebreken, "svg_has_gebreken_stempel", lambda _s: True)
    monkeypatch.setattr(gebreken, "pdf_has_gebreken_stempel", lambda _p: True)
    assert gebreken.collect_gebreken_statuses() == ([], 1)


def _fix_ronde_setup(monkeypatch, tmp_path, na_check):
    """Gemeenschappelijke stubs voor de meerrondes-tests; geeft de uitgevoerde cmds."""
    path = tmp_path / "check-fixlist.json"
    save_fixlist(
        [
            FixItem(
                id="mvsa:a",
                checker="mvsa",
                summary="a",
                fix_cmd=r"scripts\products.cmd --kinds mvsa --skip-post a.mvsa",
            )
        ],
        path=path,
    )
    uitgevoerd: list[str] = []
    checks = iter(na_check)
    monkeypatch.setattr(fix_mod, "FIXLIST_PATH", path)
    monkeypatch.setattr(fix_mod, "load_fixlist", lambda: load_fixlist(path))
    monkeypatch.setattr(
        fix_mod, "save_fixlist", lambda items: save_fixlist(items, path=path)
    )
    mt = iter(range(1, 100))
    monkeypatch.setattr(fix_mod, "_fixlist_mtime", lambda: next(mt))
    monkeypatch.setattr(fix_mod, "_run_check_strict", lambda **_k: 1)
    first = [True]

    def _refresh():
        if first[0]:
            first[0] = False
            return load_fixlist(path)
        return next(checks)

    monkeypatch.setattr(fix_mod, "_refresh_fixlist_from_status", _refresh)
    monkeypatch.setattr(fix_mod, "_sync_stempels", lambda **_k: 0)
    monkeypatch.setattr(fix_mod, "_run_products_post", lambda **_k: 0)

    def _run(cmd, **_k):
        uitgevoerd.append(cmd)
        return 0, ""

    monkeypatch.setattr(fix_mod, "_run_fix_cmd", _run)
    monkeypatch.setattr(fix_mod, "confirm_batch", lambda *_a, **_k: True)
    return uitgevoerd


def test_fix_tweede_ronde_pakt_nieuw_verouderde_pdfs(tmp_path, monkeypatch):
    """Na producten zijn andere PDF's verouderd: dezelfde run maakt ze af."""
    pdf = FixItem(
        id="pdf:x", checker="pdf", summary="x", fix_cmd=r"scripts\pdf.cmd x\index.md"
    )
    uitgevoerd = _fix_ronde_setup(monkeypatch, tmp_path, [[pdf], []])
    assert fix_mod.main(["--strict", "-y"]) == 0
    assert len(uitgevoerd) == 2
    assert "pdf.cmd" in uitgevoerd[1]


def test_fix_stopt_bij_niet_convergeren(tmp_path, monkeypatch):
    """Dezelfde fix_cmd blijft terugkomen: niet eindeloos herhalen, exit 1."""
    prod = FixItem(
        id="mvsa:a",
        checker="mvsa",
        summary="a",
        fix_cmd=r"scripts\products.cmd --kinds mvsa --skip-post a.mvsa",
    )
    uitgevoerd = _fix_ronde_setup(monkeypatch, tmp_path, [[prod], [prod], [prod]])
    assert fix_mod.main(["--strict", "-y"]) == 1
    assert len(uitgevoerd) == 1
