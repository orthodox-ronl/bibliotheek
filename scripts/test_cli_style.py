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
    assert "WinError 32" in explained.reason or "vergrendeld" in explained.reason.lower()
    assert explained.solution.startswith("Oplossing:")
    assert "MuseScore" in explained.solution or "viewer" in explained.solution.lower()
    assert cs.is_transient_lock_error(exc)


def test_explain_winerror_5() -> None:
    exc = RuntimeError(
        "x.mscz: ERROR: [WinError 5] Toegang geweigerd: "
        "'C:\\\\tmp\\\\x.mscz.products-meta.json.tmp'"
    )
    explained = cs.explain_sync_failure(exc)
    assert "WinError 5" in explained.reason or "vergrendeld" in explained.reason.lower()
    assert explained.solution.startswith("Oplossing:")
    assert cs.is_transient_lock_error(exc)


def test_explain_errno_22() -> None:
    exc = OSError(22, "Invalid argument", r"C:\tmp\lied.vsa.mxl")
    explained = cs.explain_sync_failure(exc)
    assert "22" in explained.reason or "overschrijven" in explained.reason.lower()
    assert explained.solution.startswith("Oplossing:")


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
