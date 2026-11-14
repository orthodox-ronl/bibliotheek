"""Tests voor cli_style (foutuitleg + verbose-gate)."""

from __future__ import annotations

from pathlib import Path

import cli_style as cs


def test_explain_winerror_32() -> None:
    exc = RuntimeError(
        "x.mscz: ERROR: [WinError 32] Het proces heeft geen toegang tot het "
        "bestand omdat het door een ander proces wordt gebruikt: 'x-1.svg'"
    )
    explained = cs.explain_sync_failure(exc)
    assert "open" in explained.reason.lower()
    assert "WinError" not in explained.reason
    assert explained.solution.startswith("Oplossing:")
    assert "MuseScore" in explained.solution or "viewer" in explained.solution.lower()
    assert cs.is_transient_lock_error(exc)


def test_explain_winerror_5() -> None:
    exc = RuntimeError(
        "x.mscz: ERROR: [WinError 5] Toegang geweigerd: "
        "'C:\\\\tmp\\\\x.mscz.products-meta.json.tmp'"
    )
    explained = cs.explain_sync_failure(exc)
    assert "open" in explained.reason.lower()
    assert "WinError" not in explained.reason
    assert explained.solution.startswith("Oplossing:")
    assert cs.is_transient_lock_error(exc)


def test_explain_winerror_1224_dutch() -> None:
    exc = OSError(
        1224,
        "Kan de aangevraagde bewerking niet uitvoeren op een bestand met "
        "een open door de gebruiker toegewezen sectie",
        r"C:\tmp\index.md.pdf",
    )
    exc.winerror = 1224  # type: ignore[attr-defined]
    explained = cs.explain_sync_failure(exc)
    assert "PDF" in explained.reason or "open" in explained.reason.lower()
    assert "toegewezen sectie" not in explained.reason.lower()
    assert "WinError" not in explained.reason
    assert explained.solution.startswith("Oplossing:")
    assert cs.is_transient_lock_error(exc)


def test_atomic_replace_lock_message(tmp_path: Path, monkeypatch) -> None:
    dest = tmp_path / "blad.pdf"
    dest.write_bytes(b"old")
    src = tmp_path / "blad.pdf.tmp"
    src.write_bytes(b"new")

    def _boom(_a, _b):
        err = OSError(
            1224,
            "Kan de aangevraagde bewerking niet uitvoeren op een bestand met "
            "een open door de gebruiker toegewezen sectie",
        )
        err.winerror = 1224
        raise err

    monkeypatch.setattr(cs.os, "replace", _boom)
    monkeypatch.setattr(cs.time, "sleep", lambda _s: None)
    try:
        cs.atomic_replace(src, dest, retries=2)
    except RuntimeError as exc:
        msg = str(exc)
        assert "blad.pdf" in msg
        assert "toegewezen sectie" not in msg.lower()
        assert "Oplossing:" in msg
    else:
        raise AssertionError("verwacht RuntimeError bij vergrendeling")


def test_explain_errno_22() -> None:
    exc = OSError(22, "Invalid argument", r"C:\tmp\lied.vsa.mxl")
    explained = cs.explain_sync_failure(exc)
    assert "22" in explained.reason or "overschrijven" in explained.reason.lower()
    assert explained.solution.startswith("Oplossing:")


def test_paint_source_locations_splits_dir_file_linecol(monkeypatch) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    loc = (
        "catalogus/tropaar/heer-red-uw-volk/rode-gebedenboek/"
        "tropaar-heer-red-uw-volk-rode-gebedenboek.vsa:30:1"
    )
    painted = cs.paint_source_locations(f"{loc}: hoogte-mismatch")
    assert cs._CYAN in painted
    assert cs._YELLOW in painted
    assert cs._DIM in painted
    assert "rode-gebedenboek.vsa" in painted
    assert ":30:1" in painted
    assert "hoogte-mismatch" in painted
    # Zonder kleur: platte tekst (logs / extractie blijven schoon).
    monkeypatch.setenv("NO_COLOR", "1")
    plain = cs.paint_source_locations(f"{loc}: hoogte-mismatch")
    assert plain == f"{loc}: hoogte-mismatch"
    assert "\033[" not in plain


def test_paint_source_locations_windows_path(monkeypatch) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    loc = r"C:\Git\orthodox-ronl\bibliotheek\content-source\x.vsa:31:1"
    painted = cs.paint_source_locations(loc)
    assert "x.vsa" in painted
    assert ":31:1" in painted
    assert cs._CYAN in painted


def test_hard_colors_location_parts(capsys, monkeypatch) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    cs.hard("  catalogus/a/b.vsa:4:2: fouttekst")
    out = capsys.readouterr().out
    assert "b.vsa" in out
    assert ":4:2" in out
    assert "fouttekst" in out
    assert "\033[" in out


def test_explain_template_instance_includes_location() -> None:
    """VSA-template-fout: reden met pad:regel:kolom + hint als Oplossing."""

    class FakeTemplateErr(Exception):
        def __init__(self) -> None:
            self.message_nl = (
                "hoogte-mismatch op lettergreep 'door' (klinkend G4).\n"
                "Geen passend slot meer (verwacht o.a. fa, mi)."
            )
            self.hint_nl = (
                "Waarschijnlijk ontbreekt een frasescheiding.\n"
                "  de over{/win_}{/ning_} … {den_} **\n"
                "Zet `**` aan het eind van die regel."
            )
            self.source = (
                "catalogus/tropaar/heer-red-uw-volk/rode-gebedenboek/"
                "tropaar-heer-red-uw-volk-rode-gebedenboek.vsa"
            )
            self.line = 30
            self.column = 1
            self.code = "VSA-TEMPLATE-PITCH-MISMATCH"

    cs.set_verbose(False)
    explained = cs.explain_sync_failure(FakeTemplateErr())
    assert "rode-gebedenboek" in explained.reason
    assert ":30:1:" in explained.reason
    assert "hoogte-mismatch" in explained.reason
    assert "Geen passend slot" not in explained.reason  # alleen bij --verbose
    assert explained.solution.startswith("Oplossing:")
    assert "**" in explained.solution

    cs.set_verbose(True)
    verbose = cs.explain_sync_failure(FakeTemplateErr())
    assert "Geen passend slot" in verbose.reason
    assert "frasescheiding" in verbose.solution
    cs.set_verbose(False)


def test_safe_print_replaces_unencodable() -> None:
    class BoomStream:
        encoding = "cp1252"

        def __init__(self) -> None:
            self.chunks: list[bytes] = []

        def write(self, s: str) -> int:
            s.encode("cp1252")  # raise op →
            return len(s)

        def flush(self) -> None:
            return None

        @property
        def buffer(self):
            class Buf:
                def __init__(self, outer: "BoomStream") -> None:
                    self._outer = outer

                def write(self, raw: bytes) -> int:
                    self._outer.chunks.append(raw)
                    return len(raw)

                def flush(self) -> None:
                    return None

            return Buf(self)

    stream = BoomStream()
    cs.safe_print("index.md → pdf", file=stream, flush=True)
    assert stream.chunks
    assert b"index.md" in stream.chunks[0]


def test_detail_silent_by_default(capsys) -> None:
    cs.set_verbose(False)
    cs.detail("geheim")
    assert capsys.readouterr().out == ""


def test_detail_when_verbose(capsys) -> None:
    cs.set_verbose(True)
    try:
        cs.detail("zichtbaar")
        assert "zichtbaar" in capsys.readouterr().out
    finally:
        cs.set_verbose(False)


def test_format_count_aligns() -> None:
    assert cs.format_count(12, "stale-mxl") == " 12  stale-mxl"
    assert cs.format_count(3, "missing-pdf") == "  3  missing-pdf"
    assert cs.format_count(0, "hard", width=3) == "  0  hard"


def test_count_work_and_refuse(capsys, monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    cs.count(12, "stale-mxl", role="work")
    cs.refuse("WEIGERT  doelmap bestaat al")
    out = capsys.readouterr().out
    assert " 12  stale-mxl" in out
    assert "WEIGERT  doelmap bestaat al" in out


def test_count_rejects_unknown_role() -> None:
    try:
        cs.count(1, "x", role="paars")
    except ValueError as exc:
        assert "paars" in str(exc)
    else:
        raise AssertionError("verwacht ValueError")


def test_atomic_write_text(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    cs.atomic_write_text(dest, '{"ok": true}\n')
    assert dest.read_text(encoding="utf-8") == '{"ok": true}\n'
    assert not (tmp_path / "out.json.tmp").exists()
    cs.atomic_write_text(dest, '{"ok": false}\n')
    assert dest.read_text(encoding="utf-8") == '{"ok": false}\n'


def test_atomic_write_json_and_bytes(tmp_path: Path) -> None:
    js = tmp_path / "a.json"
    cs.atomic_write_json(js, {"n": 1}, ensure_ascii=False)
    assert '"n": 1' in js.read_text(encoding="utf-8")
    blob = tmp_path / "a.bin"
    cs.atomic_write_bytes(blob, b"abc")
    assert blob.read_bytes() == b"abc"
    cs.atomic_write_bytes(blob, b"xyz")
    assert blob.read_bytes() == b"xyz"
    assert not (tmp_path / "a.bin.tmp").exists()


def test_atomic_replace(tmp_path: Path) -> None:
    dest = tmp_path / "page.pdf"
    dest.write_bytes(b"old")
    src = tmp_path / "page.pdf.tmp"
    src.write_bytes(b"new-pdf")
    cs.atomic_replace(src, dest)
    assert dest.read_bytes() == b"new-pdf"
    assert not src.exists()
