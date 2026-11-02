"""Terminal-output voor bibliotheek-scripts: kleur, stilte, leesbare fouten."""

from __future__ import annotations

import errno
import os
import re
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Callable, Sequence

_VERBOSE = False

_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def configure_stdio() -> None:
    """Forceer UTF-8 op stdout/stderr (Windows cp1252 crasht op →/←/…)."""
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if not callable(reconf):
            continue
        try:
            reconf(encoding="utf-8", errors="replace")
        except (OSError, ValueError, AttributeError):
            pass


def safe_print(*args: object, sep: str = " ", end: str = "\n", file=None, flush: bool = False) -> None:
    """``print`` die bij codec-fouten tekens vervangt i.p.v. te crashen."""
    stream = sys.stdout if file is None else file
    text = sep.join(str(a) for a in args) + end
    try:
        stream.write(text)
        if flush:
            stream.flush()
        return
    except UnicodeEncodeError:
        pass
    enc = getattr(stream, "encoding", None) or "utf-8"
    raw = text.encode(enc, errors="replace")
    buf = getattr(stream, "buffer", None)
    if buf is not None:
        buf.write(raw)
        if flush:
            buf.flush()
        return
    stream.write(raw.decode(enc, errors="replace"))
    if flush:
        stream.flush()


configure_stdio()


def paint(msg: str, *codes: str, stream=None) -> str:
    """ANSI om msg heen als de stream kleuren mag; anders msg ongewijzigd."""
    target = sys.stdout if stream is None else stream
    if not codes or not _use_color(target):
        return msg
    return f"{''.join(codes)}{msg}{_RESET}"


def section(msg: str) -> None:
    """Start van een controle/stap (cyaan)."""
    print(paint(msg, _BOLD, _CYAN), flush=True)


def ok(msg: str) -> None:
    """Alles in orde (groen)."""
    print(paint(msg, _GREEN), flush=True)


def work(msg: str) -> None:
    """Er is afwerkbaar werk / bevinding (geel)."""
    print(paint(msg, _YELLOW), flush=True)


def note(msg: str) -> None:
    """Neutrale toelichting (dim)."""
    print(paint(msg, _DIM), flush=True)


def hard(msg: str) -> None:
    """Echte fout / onverwacht probleem (rood vet), op stdout."""
    print(paint(msg, _BOLD, _RED), flush=True)


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


def atomic_write_text(
    path: Path,
    text: str,
    *,
    encoding: str = "utf-8",
    newline: str | None = None,
    retries: int = 8,
) -> None:
    """Schrijf via temp+replace; retry bij Windows-vergrendeling (Errno 22)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    write_kw: dict = {"encoding": encoding}
    if newline is not None:
        write_kw["newline"] = newline

    def _write_direct(target: Path) -> None:
        target.write_text(text, **write_kw)

    _write_direct(tmp)
    last: OSError | None = None
    for attempt in range(max(1, retries)):
        try:
            os.replace(tmp, path)
            return
        except OSError as exc:
            last = exc
            # WinError 5/32 / Errno 22: bestand even vast (editor, AV, …)
            time.sleep(0.05 * (attempt + 1))
    try:
        _write_direct(path)
    except OSError:
        if last is not None:
            raise last
        raise
    finally:
        tmp.unlink(missing_ok=True)


def atomic_write_json(
    path: Path,
    payload: object,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None:
    """JSON + newline via ``atomic_write_text`` (data/status/static indexen)."""
    import json

    atomic_write_text(
        path,
        json.dumps(
            payload,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
        )
        + "\n",
        newline="\n",
    )


def atomic_write_bytes(
    path: Path,
    data: bytes,
    *,
    retries: int = 8,
) -> None:
    """Bytes via temp+replace; zelfde Windows-retry als ``atomic_write_text``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    last: OSError | None = None
    for attempt in range(max(1, retries)):
        try:
            os.replace(tmp, path)
            return
        except OSError as exc:
            last = exc
            time.sleep(0.05 * (attempt + 1))
    try:
        path.write_bytes(data)
    except OSError:
        if last is not None:
            raise last
        raise
    finally:
        tmp.unlink(missing_ok=True)


def run_quiet(
    label: str,
    fn: Callable[[list[str]], int | None],
    argv: list[str] | None = None,
    *,
    verbose: bool | None = None,
) -> int:
    """Kind-aanroep: stil tenzij verbose of mislukking (dan wél de log)."""
    args = list(argv or [])
    show = is_verbose() if verbose is None else bool(verbose)
    if show:
        code = fn(args)
        return 0 if code in (0, None) else int(code)
    buf = StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        code = fn(args)
    rc = 0 if code in (0, None) else int(code)
    if rc != 0:
        text = buf.getvalue().rstrip()
        error(f"FAILED {label}")
        if text:
            error(text)
    return rc


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


def _exception_text(exc: BaseException) -> str:
    """Stdout/stderr + str(exc) voor lock-detectie en foutuitleg."""
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
    return "\n".join(p for p in parts if p)


def is_transient_lock_error(exc: BaseException) -> bool:
    """True bij tijdelijke Windows-vergrendeling (Access Denied / sharing).

    Die fouten horen in de products-batch in een herhaal-wachtrij, niet
    meteen als definitieve MISLUKT.
    """
    if isinstance(exc, PermissionError):
        return True
    if isinstance(exc, OSError):
        win = getattr(exc, "winerror", None)
        if win in {5, 32, 1224}:
            return True
        if exc.errno in {errno.EACCES, errno.EPERM, errno.EINVAL}:
            return True
    low = _exception_text(exc).lower()
    markers = (
        "winerror 5",
        "winerror 32",
        "winerror 1224",
        "toegang geweigerd",
        "access is denied",
        "door een ander proces wordt gebruikt",
        "errno 22",
        "lokale sessie",
    )
    return any(m in low for m in markers)


def explain_sync_failure(exc: BaseException) -> FailureExplain:
    """Vertaal ruwe uitzondering naar reden + Oplossing."""
    combined = _exception_text(exc)

    error_line = ""
    for line in combined.splitlines():
        if "ERROR:" in line:
            error_line = line.strip()
            break

    low = combined.lower()
    if (
        "winerror 5" in low
        or "winerror 32" in low
        or "toegang geweigerd" in low
        or "access is denied" in low
        or "door een ander proces wordt gebruikt" in low
    ):
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
