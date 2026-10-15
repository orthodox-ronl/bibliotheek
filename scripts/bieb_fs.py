"""Bestands-I/O voor ``bieb``: retries bij vergrendeling, nette fouten.

Geen traceback naar de gebruiker. Onverwachte fouten: zie ``run_handler`` /
``report_unexpected`` (optioneel ``BIEB_TRACE=1`` voor stacktrace).
"""

from __future__ import annotations

import os
import shutil
import sys
import time
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from catalogus import REPO_ROOT

T = TypeVar("T")

_RETRY_ATTEMPTS = 8


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def locked_oplossing() -> str:
    return (
        "Oplossing: sluit het programma dat het bestand open heeft "
        "(editor, viewer of MuseScore) en probeer opnieuw."
    )


def print_fail(
    message: str,
    *,
    oplossing: str,
    stream: object | None = None,
) -> None:
    """FAIL-regel + Oplossing (standaard stdout, zoals ``bieb accepteer``)."""
    out = sys.stdout if stream is None else stream
    print(f"FAIL: {message}", file=out, flush=True)
    text = oplossing if oplossing.startswith("Oplossing:") else f"Oplossing: {oplossing}"
    print(text, file=out, flush=True)


def format_locus(
    path: str | Path,
    line: int,
    *,
    col: int | None = None,
    snippet: str | None = None,
) -> str:
    """Locatie in tekstbron: ``pad:regel`` of ``pad:regel:kolom`` (+ optionele snippet)."""
    p = path if isinstance(path, str) else rel(path)
    loc = f"{p}:{line}" if col is None else f"{p}:{line}:{col}"
    if snippet is None or snippet == "":
        return loc
    return f"{loc}: {snippet}"


def needle_column(line: str, *needles: str) -> int | None:
    """1-based kolom van de vroegste naald in ``line``, of ``None``."""
    best: int | None = None
    for needle in needles:
        if not needle:
            continue
        i = line.find(needle)
        if i >= 0 and (best is None or i < best):
            best = i
    return None if best is None else best + 1


def _path_label(paths: list[Path]) -> str:
    if len(paths) == 1:
        return rel(paths[0])
    if len(paths) == 2:
        return f"{rel(paths[0])} → {rel(paths[1])}"
    return ", ".join(rel(p) for p in paths)


def die_os(action: str, *paths: Path, exc: BaseException | None = None) -> None:
    """``SystemExit`` met pad + Oplossing (geen exception-keten)."""
    label = _path_label(list(paths))
    if isinstance(exc, PermissionError) or (
        isinstance(exc, OSError) and getattr(exc, "winerror", None) == 32
    ):
        msg = (
            f"Kon niet {action}: {label}\n"
            "Het bestand is vergrendeld (bijvoorbeeld open in een editor, "
            "viewer of MuseScore).\n"
            f"{locked_oplossing()}"
        )
    elif isinstance(exc, FileNotFoundError):
        msg = (
            f"Kon niet {action}: {label}\n"
            "Bestand of map ontbreekt.\n"
            "Oplossing: controleer het pad en probeer opnieuw."
        )
    elif isinstance(exc, OSError):
        detail = exc.strerror or str(exc)
        msg = (
            f"Kon niet {action}: {label}\n"
            f"Systeemfout: {detail}\n"
            f"{locked_oplossing()}"
        )
    else:
        msg = (
            f"Kon niet {action}: {label}\n"
            f"{locked_oplossing()}"
        )
    raise SystemExit(msg)


def with_retry(fn: Callable[[], T], *, action: str, paths: list[Path]) -> T:
    """Voer ``fn`` uit; bij ``PermissionError`` opnieuw proberen, anders nette exit."""
    last: OSError | None = None
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            return fn()
        except PermissionError as exc:
            last = exc
            time.sleep(0.4 * (attempt + 1))
        except OSError as exc:
            die_os(action, *paths, exc=exc)
    assert last is not None
    die_os(action, *paths, exc=last)
    raise AssertionError("unreachable")  # pragma: no cover


def copy2(src: Path, dest: Path) -> None:
    with_retry(
        lambda: shutil.copy2(src, dest),
        action="kopiëren",
        paths=[src, dest],
    )


def move(src: Path, dest: Path) -> None:
    with_retry(
        lambda: shutil.move(str(src), str(dest)),
        action="verplaatsen",
        paths=[src, dest],
    )


def rename(src: Path, dest: Path) -> None:
    with_retry(
        lambda: src.rename(dest),
        action="hernoemen",
        paths=[src, dest],
    )


def unlink(path: Path) -> None:
    with_retry(
        lambda: path.unlink(),
        action="wissen",
        paths=[path],
    )


def rmtree(path: Path) -> None:
    with_retry(
        lambda: shutil.rmtree(path),
        action="wissen van map",
        paths=[path],
    )


def mkdir(path: Path) -> None:
    with_retry(
        lambda: path.mkdir(parents=True, exist_ok=True),
        action="aanmaken van map",
        paths=[path],
    )


def write_text(path: Path, text: str, *, encoding: str = "utf-8", newline: str = "\n") -> None:
    def _do() -> None:
        path.write_text(text, encoding=encoding, newline=newline)

    with_retry(_do, action="schrijven", paths=[path])


def report_unexpected(exc: BaseException, *, command: str | None = None) -> int:
    """Nette melding voor onverwachte fouten; return exitcode."""
    if os.environ.get("BIEB_TRACE", "").strip() in {"1", "true", "yes"}:
        traceback.print_exc()
    prefix = f"bieb {command}: " if command else "bieb: "
    if isinstance(exc, OSError):
        detail = exc.strerror or str(exc)
        filename = getattr(exc, "filename", None)
        where = f" ({filename})" if filename else ""
        print(
            f"{prefix}bestandfout{where}: {detail}\n"
            f"{locked_oplossing()}",
            file=sys.stderr,
        )
        return 1
    print(
        f"{prefix}onverwachte fout: {exc}\n"
        "Oplossing: controleer de argumenten en of bestanden niet open staan. "
        "Voor een technische stacktrace: zet BIEB_TRACE=1 en probeer opnieuw.",
        file=sys.stderr,
    )
    return 1


def run_handler(handler: Callable[[list[str]], int], argv: list[str], *, command: str) -> int:
    """Draai een subcommando-handler zonder traceback naar de gebruiker."""
    try:
        return int(handler(argv))
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(code, file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print(f"bieb {command}: gestopt.", file=sys.stderr)
        return 130 if isinstance(sys.exc_info()[1], KeyboardInterrupt) else 2
    except Exception as exc:  # noqa: BLE001 — CLI-vangnet
        return report_unexpected(exc, command=command)
