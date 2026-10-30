"""Terminal-output voor bibliotheek-scripts: kleur, stilte, leesbare fouten."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence

_VERBOSE = False

_RED = "\033[31m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def set_verbose(enabled: bool) -> None:
    global _VERBOSE
    _VERBOSE = bool(enabled)


def is_verbose() -> bool:
    if _VERBOSE:
        return True
    return os.environ.get("BIBLIOTHEEK_VERBOSE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def add_verbose_argument(parser) -> None:
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Uitgebreide logging (per stap / subprocess-uitvoer). Standaard uit.",
    )


def _use_color(stream) -> bool:
    if os.environ.get("NO_COLOR", "").strip():
        return False
    if os.environ.get("FORCE_COLOR", "").strip():
        return True
    try:
        return bool(stream.isatty())
    except Exception:  # noqa: BLE001
        return False


def detail(msg: str) -> None:
    """Alleen bij --verbose / BIBLIOTHEEK_VERBOSE."""
    if is_verbose():
        print(msg, flush=True)


def info(msg: str) -> None:
    print(msg, flush=True)


def error(msg: str) -> None:
    """Foutregel (rood op een kleuren-terminal)."""
    stream = sys.stderr
    if _use_color(stream):
        print(f"{_RED}{msg}{_RESET}", file=stream, flush=True)
    else:
        print(msg, file=stream, flush=True)


def error_block(lines: Sequence[str]) -> None:
    for line in lines:
        error(line)


@dataclass(frozen=True)
class FailureExplain:
    """Korte reden + beheerder-oplossing (kwaliteitsstijl)."""

    reason: str
    solution: str


def explain_sync_failure(exc: BaseException) -> FailureExplain:
    """Vertaal ruwe uitzondering naar reden + Oplossing."""
    parts: list[str] = [str(exc).strip()]
    stderr = getattr(exc, "stderr", None)
    stdout = getattr(exc, "stdout", None)
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, str) and stderr.strip():
        parts.insert(0, stderr.strip())
    if isinstance(stdout, str) and stdout.strip():
        parts.append(stdout.strip())
    combined = "\n".join(p for p in parts if p)

    error_line = ""
    for line in combined.splitlines():
        if "ERROR:" in line:
            error_line = line.strip()
            break

    low = combined.lower()
    if "winerror 32" in low or "door een ander proces wordt gebruikt" in low:
        return FailureExplain(
            reason=(
                error_line
                or "Bestand was vergrendeld (in gebruik door een ander programma)."
            ),
            solution=(
                "Oplossing: sluit MuseScore, een PDF-/SVG-viewer of het "
                "voorbeeldvenster in Verkenner dat dit bestand open heeft, "
                "en draai het commando opnieuw."
            ),
        )
    if "winerror 1224" in low or "lokale sessie" in low:
        return FailureExplain(
            reason=error_line or "Bestand was tijdelijk vergrendeld (WinError 1224).",
            solution=(
                "Oplossing: sluit het bestand in MuseScore of een viewer en "
                "draai opnieuw; soms helpt een paar seconden wachten."
            ),
        )
    if "errno 22" in low or "invalid argument" in low:
        return FailureExplain(
            reason=error_line
            or "Windows weigerde het bestaande productbestand te overschrijven (Errno 22).",
            solution=(
                "Oplossing: sluit MuseScore/viewer die het bestand open heeft; "
                "wis desnoods het genoemde sibling-bestand en draai opnieuw. "
                "Recente tooling schrijft via een tijdelijk bestand (minder "
                "gevoelig voor dit Windows-probleem)."
            ),
        )
    if "musescore" in low and (
        "not found" in low or "niet gevonden" in low or "niet op path" in low
    ):
        return FailureExplain(
            reason=error_line or "MuseScore ontbreekt of staat niet op PATH.",
            solution=(
                "Oplossing: installeer MuseScore 4 en zorg dat het op PATH "
                "staat, of draai scripts\\_ensure.cmd."
            ),
        )

    if error_line:
        short = error_line
        if len(short) > 240:
            short = short[:237] + "..."
    else:
        short = combined.splitlines()[0] if combined else type(exc).__name__
        if len(short) > 240:
            short = short[:237] + "..."

    return FailureExplain(
        reason=short,
        solution=(
            "Oplossing: herstel de fout hierboven (bronbestand of tools) "
            "en draai het commando opnieuw. Voor meer detail: zelfde "
            "commando met --verbose."
        ),
    )


_CMD_RE = re.compile(r"^Command\s+'\[", re.I)


def street_products_quiet_flags() -> list[str]:
    """``--quiet`` voor vsa/mvsa/mscz products tenzij bibliotheek-verbose."""
    if is_verbose():
        return []
    return ["--quiet"]


def check_call(cmd: Sequence[str], *, cwd: str | None = None) -> None:
    """subprocess.check_call; dempt stdout/stderr tenzij verbose.

    Bij falen: RuntimeError met CLI-tekst (zodat explain_sync_failure werkt).
    """
    if is_verbose():
        subprocess.check_call(list(cmd), cwd=cwd)
        return
    proc = subprocess.run(
        list(cmd),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return
    blob = "\n".join(
        p for p in ((proc.stderr or "").strip(), (proc.stdout or "").strip()) if p
    )
    if not blob:
        blob = f"commando mislukt (exit {proc.returncode})"
    raise RuntimeError(blob)


def run_checked(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Zoals subprocess.run(..., check=False) met optioneel stille streams."""
    if is_verbose():
        return subprocess.run(list(cmd), cwd=cwd, text=True, check=False)
    return subprocess.run(
        list(cmd),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
