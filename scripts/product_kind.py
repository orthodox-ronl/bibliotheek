"""Gedeelde product-schil: collect → need_regen → MuseScore-gate → sync.

Per kind blijven bron-selectie en generatie in ``sync_*``; deze module
doet de herhaalde orchestration. Zie docs/publicatiecontrole.md.
"""

from __future__ import annotations

import argparse
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, Protocol, Sequence

from cli_style import (
    add_verbose_argument,
    count,
    detail,
    error,
    error_block,
    explain_sync_failure,
    info,
    is_transient_lock_error,
    ok,
    section,
    set_verbose,
    work,
)


# Na de eerste ronde: vergrendelde items nog zo vaak proberen.
LOCK_RETRY_PASSES = 2
LOCK_RETRY_PAUSE_S = 1.5
from product_regen import (
    RegenPolicy,
    add_regen_arguments,
    need_regen,
    policy_from_args,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "content-source" / "catalogus"


@dataclass(frozen=True)
class ProductSlot:
    """Eén afgeleid bestand bij een bron."""

    path: Path
    exists: bool
    stamp_ok: bool
    contract_ok: bool | None = None  # None = geen contract voor dit slot
    needs_musescore: bool = False


@dataclass(frozen=True)
class KindFailure:
    """Eén mislukte bron in een product-spoor."""

    path: str
    reason: str
    solution: str


_FAILURES_OUT: list[KindFailure] | None = None


@contextmanager
def collect_failures(out: list[KindFailure]) -> Iterator[None]:
    """Laat ``run_kind`` failures in ``out`` zetten (o.a. vanuit ``products``)."""
    global _FAILURES_OUT
    prev = _FAILURES_OUT
    _FAILURES_OUT = out
    try:
        yield
    finally:
        _FAILURES_OUT = prev


class ProductKind(Protocol):
    """Contract voor één product-spoor."""

    id: str
    label: str  # logregel: "Tekstblad-producten", "MSCZ-producten", …
    source_noun: str  # " .tekstblad.md", " .mscz", " bronnen", …
    fix_cmd: str  # hint als MuseScore ontbreekt

    def collect(self, root: Path) -> list[Path]: ...

    def slots_for(self, source: Path, policy: RegenPolicy) -> list[ProductSlot]: ...

    def sync(self, source: Path, *, need: Sequence[bool], dry_run: bool) -> None: ...


def running_in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def catalog_eligible(path: Path, *, folder_is_handmatig: Callable[[Path], bool]) -> bool:
    """Gemeenschappelijke uitsluitingen: ``input/`` en ``manueel/manual``."""
    if "input" in path.parts:
        return False
    if folder_is_handmatig(path.parent):
        return False
    return True


def require_no_spaces_name(path: Path) -> None:
    if " " in path.name:
        raise SystemExit(f"bestandsnaam mag geen spaties hebben: {path.name}")


def resolve_root(raw: Path | str, *, repo_root: Path = REPO_ROOT) -> Path:
    """CLI-root: as-is → content-source → catalogus → koormappen.

    Zie :func:`input_paths.resolve_user_path`. Ontbreekt het pad →
    :exc:`input_paths.InputPathError`.
    """
    from input_paths import resolve_user_path

    return resolve_user_path(raw, repo_root=repo_root)


def parse_product_args(
    argv: list[str] | None,
    *,
    description: str,
    default_root: Path = DEFAULT_ROOT,
    add_extra: Callable[[argparse.ArgumentParser], None] | None = None,
) -> argparse.Namespace:
    from batch_guard import add_already_confirmed_argument, add_yes_argument

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=default_root,
        help=(
            "Catalogusmap of één bronbestand (default: "
            "content-source/catalogus). Korte paden: t.o.v. "
            "content-source, catalogus of koormappen."
        ),
    )
    add_regen_arguments(parser)
    add_verbose_argument(parser)
    add_yes_argument(parser)
    add_already_confirmed_argument(parser)
    if add_extra is not None:
        add_extra(parser)
    return parser.parse_args(argv)


def _print_kind_failure_summary(kind_id: str, failures: Sequence[KindFailure]) -> None:
    if not failures:
        return
    count(len(failures), f"mislukt-{kind_id}", role="hard")
    for fail in failures:
        error(f"  {fail.path}")
        error(f"    {fail.reason}")
        error(f"    {fail.solution}")


def run_kind(
    kind: ProductKind,
    root: Path,
    policy: RegenPolicy,
    *,
    dry_run: bool = False,
    yes: bool = False,
    already_confirmed: bool = False,
    verbose: bool = False,
    repo_root: Path = REPO_ROOT,
    find_musescore: Callable[[], Path | None] | None = None,
    failures_out: list[KindFailure] | None = None,
) -> int:
    """Draai één product-spoor. Geen passende bron = skip (exit 0), geen fout."""
    set_verbose(verbose)
    if not root.exists():
        error(f"FAIL: pad bestaat niet: {root}")
        error(
            "Oplossing: geef een bestaande catalogusmap of één bronbestand "
            "onder content-source\\catalogus."
        )
        return 1

    sources = kind.collect(root)
    if not sources:
        if root.is_file():
            detail(
                f"{kind.id}: geen passende bron op {root.name}; overgeslagen",
            )
        else:
            detail(
                f"{kind.label}: 0 bronnen onder {root}",
            )
        return 0

    todo: list[tuple[Path, list[bool], list[ProductSlot]]] = []
    for source in sources:
        slots = kind.slots_for(source, policy)
        need = [
            need_regen(
                policy,
                exists=slot.exists,
                stamp_ok=slot.stamp_ok,
                contract_ok=slot.contract_ok,
            )
            for slot in slots
        ]
        if any(need):
            todo.append((source, need, slots))

    if not todo:
        detail(
            f"{kind.label} up-to-date ({len(sources)}{kind.source_noun})",
        )
        return 0

    # MuseScore-gate: slots met needs_musescore uitzetten als MuseScore ontbreekt.
    needs_ms = any(
        flag and slot.needs_musescore
        for _, need_flags, slots in todo
        for flag, slot in zip(need_flags, slots, strict=True)
    )
    if needs_ms:
        if find_musescore is None:
            from vsa.musescore_cli import find_musescore as _find

            find_musescore = _find
        if find_musescore() is None:
            pending: list[str] = []
            trimmed: list[tuple[Path, list[bool], list[ProductSlot]]] = []
            for source, need_flags, slots in todo:
                new_need = list(need_flags)
                for i, slot in enumerate(slots):
                    if new_need[i] and slot.needs_musescore:
                        pending.append(f"{source.name} -> {slot.path.name}")
                        new_need[i] = False
                if any(new_need):
                    trimmed.append((source, new_need, slots))
            count(len(pending), f"wacht-op-musescore-{kind.id}", role="work")
            if running_in_ci():
                work(
                    f"CI: sla MuseScore-stappen over voor {kind.id}; "
                    "overige slots wel bijwerken.",
                )
                todo = trimmed
                if not todo:
                    return 0
            else:
                error(f"Installeer MuseScore 4 of: {kind.fix_cmd}")
                error(
                    "Oplossing: installeer MuseScore 4, of genereer later "
                    f"met {kind.fix_cmd} zodra MuseScore beschikbaar is."
                )
                for line in pending:
                    detail(f"  - {line}")
                todo = trimmed
                if not todo:
                    return 1

    section(f">>> {kind.id}")
    count(len(todo), f"bijwerken (van {len(sources)})", role="work")
    from batch_guard import confirm_batch, run_timed_batch
    from input_paths import rel_for_log

    timing_kind = f"product_{kind.id}"
    actie = "dry-run (geen schrijven)" if dry_run else "producten schrijven/vernieuwen"
    if not confirm_batch(
        timing_kind,
        n=len(todo),
        headline=f"{kind.label}: {len(todo)} van {len(sources)}{kind.source_noun}",
        details=[
            f"Root: {rel_for_log(root, repo_root=repo_root)}",
            f"Actie: {actie}",
            f"Condities: {', '.join(policy.active_reasons())}",
        ],
        yes=yes,
        already_confirmed=already_confirmed,
    ):
        return 2

    failed_rows: list[KindFailure] = []
    deferred: list[tuple[Path, list[bool], list[ProductSlot]]] = []
    deferred_exc: dict[Path, BaseException] = {}

    def _record_failure(rel: str, exc: BaseException) -> None:
        explained = explain_sync_failure(exc)
        fail = KindFailure(
            path=rel,
            reason=explained.reason,
            solution=explained.solution,
        )
        failed_rows.append(fail)
        error_block(
            [
                f"MISLUKT {rel}",
                f"  {fail.reason}",
                f"  {fail.solution}",
            ]
        )

    def _one(item: tuple[Path, list[bool], list[ProductSlot]]) -> int:
        from batch_guard import SKIP

        source, need_flags, _slots = item
        rel = rel_for_log(source, repo_root=repo_root)
        detail(f"== {rel}")
        try:
            kind.sync(source, need=need_flags, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001
            if is_transient_lock_error(exc):
                work(f"  Uitgesteld (vergrendeld): {rel}")
                deferred.append(item)
                deferred_exc[source] = exc
                return SKIP
            _record_failure(rel, exc)
            return 1
        return 0

    _ok, failed, _skipped = run_timed_batch(
        timing_kind,
        todo,
        _one,
        label=lambda it: str(it[0]),
    )

    for pass_i in range(1, LOCK_RETRY_PASSES + 1):
        if not deferred:
            break
        time.sleep(LOCK_RETRY_PAUSE_S * pass_i)
        count(
            len(deferred),
            f"retry-vergrendeling ({pass_i}/{LOCK_RETRY_PASSES})",
            role="work",
        )
        still: list[tuple[Path, list[bool], list[ProductSlot]]] = []
        for item in deferred:
            source, need_flags, _slots = item
            rel = rel_for_log(source, repo_root=repo_root)
            detail(f"== retry {rel}")
            try:
                kind.sync(source, need=need_flags, dry_run=dry_run)
            except Exception as exc:  # noqa: BLE001
                if is_transient_lock_error(exc):
                    still.append(item)
                    deferred_exc[source] = exc
                    work(f"  Nog vergrendeld: {rel}")
                else:
                    _record_failure(rel, exc)
                    failed += 1
            else:
                ok(f"  OK na herhaling: {rel}")
        deferred = still

    for item in deferred:
        source, need_flags, _slots = item
        rel = rel_for_log(source, repo_root=repo_root)
        exc = deferred_exc.get(source) or RuntimeError(
            "Bestand bleef vergrendeld na herhaalpogingen."
        )
        _record_failure(rel, exc)
        failed += 1

    sink = failures_out if failures_out is not None else _FAILURES_OUT
    if sink is not None:
        sink.extend(failed_rows)
    else:
        # Alleen bij losse kind-CLI: volledige samenvatting hier.
        _print_kind_failure_summary(kind.id, failed_rows)
    if failed:
        count(failed, f"mislukt-{kind.id}", role="hard")
        return 1
    ok(f"OK  {kind.id}")
    return 0


def main_for_kind(
    kind: ProductKind,
    argv: list[str] | None = None,
    *,
    description: str,
    default_root: Path = DEFAULT_ROOT,
    add_extra: Callable[[argparse.ArgumentParser], None] | None = None,
    after_parse: Callable[[argparse.Namespace], None] | None = None,
    repo_root: Path = REPO_ROOT,
) -> int:
    """Standaard CLI-entry voor een sync_*-module."""
    args = parse_product_args(
        argv,
        description=description,
        default_root=default_root,
        add_extra=add_extra,
    )
    if after_parse is not None:
        after_parse(args)
    policy = policy_from_args(args)
    from input_paths import InputPathError

    try:
        root = resolve_root(args.root, repo_root=repo_root)
    except InputPathError as exc:
        error(f"FAIL: {exc}")
        error(
            "Oplossing: geef een bestaande catalogusmap of één bronbestand "
            "(kort: t.o.v. content-source, catalogus of koormappen)."
        )
        return 1
    return run_kind(
        kind,
        root,
        policy,
        dry_run=bool(args.dry_run),
        yes=bool(getattr(args, "yes", False)),
        already_confirmed=bool(getattr(args, "already_confirmed", False)),
        verbose=bool(getattr(args, "verbose", False)),
        repo_root=repo_root,
    )
