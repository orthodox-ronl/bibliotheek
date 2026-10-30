"""Unit tests voor product_kind.run_kind (geen MuseScore)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from product_kind import KindFailure, ProductSlot, collect_failures, run_kind
from product_regen import RegenPolicy


@dataclass
class FakeKind:
    id: str = "fake"
    label: str = "Fake-producten"
    source_noun: str = " bronnen"
    fix_cmd: str = r"scripts\fake-products.cmd"
    sources: list[Path] = field(default_factory=list)
    slots: dict[Path, list[ProductSlot]] = field(default_factory=dict)
    synced: list[tuple[Path, tuple[bool, ...]]] = field(default_factory=list)

    def collect(self, root: Path) -> list[Path]:
        if root.is_file():
            return [p for p in self.sources if p.resolve() == root.resolve()]
        return list(self.sources)

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]:
        return list(self.slots.get(source, []))

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None:
        self.synced.append((source, tuple(need)))


def test_skip_when_file_has_no_sources(tmp_path: Path) -> None:
    other = tmp_path / "x.mvsa"
    other.write_text("x", encoding="utf-8")
    kind = FakeKind(sources=[])
    assert run_kind(kind, other, RegenPolicy(), dry_run=True) == 0
    assert kind.synced == []


def test_empty_dir_up_to_date(tmp_path: Path) -> None:
    kind = FakeKind(sources=[])
    assert run_kind(kind, tmp_path, RegenPolicy(), dry_run=True) == 0


def test_up_to_date_when_stamp_ok(tmp_path: Path) -> None:
    src = tmp_path / "a.vsa"
    src.write_text("a", encoding="utf-8")
    prod = tmp_path / "a.vsa.pdf"
    prod.write_bytes(b"%PDF")
    kind = FakeKind(
        sources=[src],
        slots={
            src: [
                ProductSlot(
                    path=prod, exists=True, stamp_ok=True, contract_ok=None
                )
            ]
        },
    )
    assert run_kind(kind, tmp_path, RegenPolicy(), dry_run=True) == 0
    assert kind.synced == []


def test_sync_when_missing(tmp_path: Path) -> None:
    src = tmp_path / "a.vsa"
    src.write_text("a", encoding="utf-8")
    prod = tmp_path / "a.vsa.pdf"
    kind = FakeKind(
        sources=[src],
        slots={
            src: [
                ProductSlot(
                    path=prod, exists=False, stamp_ok=False, contract_ok=None
                )
            ]
        },
    )
    assert run_kind(kind, tmp_path, RegenPolicy(), dry_run=True) == 0
    assert kind.synced == [(src, (True,))]


def test_musescore_gate_drops_ms_slots_ci(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CI", "true")
    src = tmp_path / "a.mscz"
    src.write_bytes(b"PK")
    pdf = tmp_path / "a.mscz.pdf"
    mxl = tmp_path / "a.mscz.mxl"
    kind = FakeKind(
        sources=[src],
        slots={
            src: [
                ProductSlot(
                    path=pdf,
                    exists=False,
                    stamp_ok=False,
                    needs_musescore=True,
                ),
                ProductSlot(
                    path=mxl,
                    exists=False,
                    stamp_ok=False,
                    needs_musescore=False,
                ),
            ]
        },
    )
    code = run_kind(
        kind,
        tmp_path,
        RegenPolicy(),
        dry_run=True,
        find_musescore=lambda: None,
    )
    assert code == 0
    assert kind.synced == [(src, (False, True))]


def test_musescore_gate_fails_locally_when_only_ms(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.delenv("CI", raising=False)
    src = tmp_path / "a.mscz"
    src.write_bytes(b"PK")
    pdf = tmp_path / "a.mscz.pdf"
    kind = FakeKind(
        sources=[src],
        slots={
            src: [
                ProductSlot(
                    path=pdf,
                    exists=False,
                    stamp_ok=False,
                    needs_musescore=True,
                )
            ]
        },
    )
    code = run_kind(
        kind,
        tmp_path,
        RegenPolicy(),
        dry_run=True,
        find_musescore=lambda: None,
    )
    assert code == 1
    assert kind.synced == []


def test_sync_failure_explained_and_collected(tmp_path: Path) -> None:
    src = tmp_path / "a.mscz"
    src.write_bytes(b"PK")
    prod = tmp_path / "a.mscz.mxl"

    class BoomKind(FakeKind):
        def sync(self, source, *, need, dry_run):  # noqa: ANN001
            raise RuntimeError(
                "a.mscz: ERROR: [WinError 32] door een ander proces wordt gebruikt"
            )

    kind = BoomKind(
        id="mscz",
        sources=[src],
        slots={
            src: [
                ProductSlot(
                    path=prod, exists=False, stamp_ok=False, contract_ok=None
                )
            ]
        },
    )
    rows: list[KindFailure] = []
    with collect_failures(rows):
        code = run_kind(
            kind,
            tmp_path,
            RegenPolicy(),
            dry_run=True,
            yes=True,
            already_confirmed=True,
            repo_root=tmp_path,
        )
    assert code == 1
    assert len(rows) == 1
    assert "a.mscz" in rows[0].path.replace("\\", "/")
    assert rows[0].solution.startswith("Oplossing:")
