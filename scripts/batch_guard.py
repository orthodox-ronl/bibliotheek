"""Preflight + bevestiging + duur-schatting voor batch (bestand-of-map).

Houdt per bewerkingstype een **running window** van de laatste N gemeten
bestanden bij (lokaal in ``generated/batch_timing.json``). Zo kan de
preflight niet alleen „47 bestanden” zeggen, maar ook „ongeveer 8 minuten”
op basis van eerdere runs op deze machine.

- Bevestiging vanaf ``confirm_from`` items (default 2), tenzij ``--yes`` / ``-y``.
- Vanaf ``HARD_LIMIT`` items: dubbele vraag («weet je het zeker?» /
  «HEEL zeker?») — ``-y`` zet die **niet** uit (geen stille mega-batch).
- Zonder TTY: zachte batch → hint ``-y``; mega-batch → draai interactief.
- Na elke gemeten item: sample opslaan (window = 20).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TypeVar

REPO_ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = REPO_ROOT / "generated" / "batch_timing.json"
WINDOW = 20
CONFIRM_FROM = 2
# Boven deze grens: twee expliciete vragen; geen switch-naam onthouden.
HARD_LIMIT = 100

T = TypeVar("T")


def _load_store() -> dict[str, list[float]]:
    if not STORE_PATH.is_file():
        return {}
    try:
        raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    out: dict[str, list[float]] = {}
    for key, samples in raw.items():
        if not isinstance(key, str) or not isinstance(samples, list):
            continue
        cleaned = [float(x) for x in samples if isinstance(x, (int, float)) and x >= 0]
        if cleaned:
            out[key] = cleaned[-WINDOW:]
    return out


def _save_store(store: dict[str, list[float]]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v[-WINDOW:] for k, v in store.items() if v}
    STORE_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def record_sample(kind: str, seconds: float) -> None:
    """Voeg één gemeten duur toe (seconden) voor dit bewerkingstype."""
    if seconds < 0:
        return
    store = _load_store()
    samples = store.get(kind, [])
    samples.append(float(seconds))
    store[kind] = samples[-WINDOW:]
    _save_store(store)


def mean_seconds(kind: str) -> tuple[float, int] | None:
    """Gemiddelde duur en aantal samples, of None als er nog geen metingen zijn."""
    samples = _load_store().get(kind) or []
    if not samples:
        return None
    return sum(samples) / len(samples), len(samples)


def format_duration(seconds: float) -> str:
    """Leesbare duur voor beheerders (Nederlands)."""
    if seconds < 1.5:
        return "minder dan 2 seconden"
    if seconds < 60:
        return f"ongeveer {int(round(seconds))} seconden"
    minutes = seconds / 60.0
    if minutes < 90:
        # één decimaal onder 10 min, anders afronden
        if minutes < 10:
            return f"ongeveer {minutes:.1f} minuten".replace(".", ",")
        return f"ongeveer {int(round(minutes))} minuten"
    hours = minutes / 60.0
    if hours < 10:
        return f"ongeveer {hours:.1f} uur".replace(".", ",")
    return f"ongeveer {int(round(hours))} uur"


def estimate_line(kind: str, n: int) -> str:
    """Eén regel over geschatte totale duur voor *n* items."""
    if n <= 0:
        return "Geschatte duur: —"
    stats = mean_seconds(kind)
    if stats is None:
        return (
            "Geschatte duur: onbekend "
            f"(nog geen eerdere metingen voor «{kind}» op deze pc; "
            "na deze run wel)"
        )
    mean, k = stats
    total = mean * n
    return (
        f"Geschatte duur: {format_duration(total)} "
        f"(gemiddelde {format_duration(mean)}/bestand over laatste {k} metingen)"
    )


def add_yes_argument(parser) -> None:
    """Voeg ``-y`` / ``--yes`` toe (batch zonder zachte vraag)."""
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help=(
            "Batch zonder gewone bevestigingsvraag (nodig zonder TTY). "
            f"Bij {HARD_LIMIT}+ items blijft de dubbele zekerheidsvraag verplicht."
        ),
    )


def add_already_confirmed_argument(parser) -> None:
    """Intern: parent-batch heeft al bevestigd (ook harde limiet overslaan)."""
    parser.add_argument(
        "--already-confirmed",
        action="store_true",
        help=argparse.SUPPRESS,
    )


def _read_answer(prompt: str) -> str:
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""


def _confirm_hard_limit(n: int) -> bool:
    """Dubbele bevestiging boven HARD_LIMIT — geen speciale CLI-switch."""
    print(
        f"  Let op: {n} items (harde limiet {HARD_LIMIT}). "
        "Dit is een grote batch (bijv. alle producten opnieuw).",
        flush=True,
    )
    if not sys.stdin.isatty():
        print(
            "  Gestopt: zo’n grote batch kan niet met -y of zonder terminal.\n"
            "  Oplossing: draai in een opdrachtvenster en beantwoord "
            "«weet je het zeker?» en daarna «HEEL zeker?».",
            flush=True,
        )
        print(flush=True)
        return False

    a1 = _read_answer("Weet je het zeker? [j/N] ")
    if a1 not in {"j", "ja", "y", "yes"}:
        print("Afgebroken.", flush=True)
        print(flush=True)
        return False
    a2 = _read_answer('HEEL zeker? Typ precies "ja" om door te gaan: ')
    if a2 != "ja":
        print("Afgebroken (tweede bevestiging niet «ja»).", flush=True)
        print(flush=True)
        return False
    print("  Dubbele bevestiging ok — grote batch start.", flush=True)
    print(flush=True)
    return True


def confirm_batch(
    kind: str,
    *,
    n: int,
    headline: str,
    details: Sequence[str] = (),
    yes: bool = False,
    already_confirmed: bool = False,
    confirm_from: int = CONFIRM_FROM,
    hard_limit: int = HARD_LIMIT,
) -> bool:
    """Toon preflight; vraag bevestiging als ``n >= confirm_from``.

    Bij ``n >= hard_limit``: altijd dubbele zekerheidsvraag; ``-y`` helpt
    daar niet (bewust: na tooling-wijziging alles opnieuw maken zonder
    switch-naam te onthouden, wél met twee bewuste antwoorden).

    ``already_confirmed=True`` (alleen via parent zoals ``products``):
    geen enkele vraag meer, ook niet boven de harde limiet — de
    orchestrator heeft al bevestigd voor de hele run.

    Returns
    -------
    bool
        True = doorgaan, False = afbreken (caller → exit 2).
    """
    print(flush=True)
    print(f"Batch «{kind}»: {headline}", flush=True)
    for line in details:
        print(f"  {line}", flush=True)
    print(f"  Aantal items: {n}", flush=True)
    print(f"  {estimate_line(kind, n)}", flush=True)

    if already_confirmed:
        print("  Bevestiging: al gedaan (aanroepende batch).", flush=True)
        print(flush=True)
        return True

    if n < confirm_from:
        print(flush=True)
        return True

    large = n >= hard_limit

    if large:
        if yes:
            print(
                "  -y/--yes genegeerd: bij "
                f"{hard_limit}+ items is dubbele bevestiging verplicht.",
                flush=True,
            )
        return _confirm_hard_limit(n)

    if yes:
        print("  Bevestiging: overgeslagen (-y/--yes).", flush=True)
        print(flush=True)
        return True

    if not sys.stdin.isatty():
        print(
            "  Gestopt: dit is een batch zonder interactieve terminal.\n"
            "  Oplossing: voeg -y/--yes toe als je bewust wilt doorgaan, "
            "of draai in een opdrachtvenster.",
            flush=True,
        )
        print(flush=True)
        return False

    answer = _read_answer("Doorgaan? [j/N] ")
    if answer in {"j", "ja", "y", "yes"}:
        print(flush=True)
        return True
    print("Afgebroken.", flush=True)
    print(flush=True)
    return False


@contextmanager
def timed_sample(kind: str) -> Iterator[None]:
    """Meet duur van één item en sla op in het running window."""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        record_sample(kind, time.perf_counter() - t0)


# fn-return: 0 = ok, <0 = overgeslagen (niet meten), >0 = mislukt
SKIP = -1


def run_timed_batch(
    kind: str,
    items: Sequence[T],
    fn: Callable[[T], int],
    *,
    label: Callable[[T], str] | None = None,
) -> tuple[int, int, int]:
    """Voer ``fn`` per item uit, meet duur, print tussentijdse ETA.

    ``fn`` returnt ``0`` = ok, ``SKIP`` (−1) = overgeslagen (geen timing-sample),
    anders mislukt. Returns ``(ok, failed, skipped)``.
    """
    ok = 0
    failed = 0
    skipped = 0
    remaining = len(items)
    for i, item in enumerate(items, start=1):
        name = label(item) if label else str(item)
        t0 = time.perf_counter()
        try:
            code = fn(item)
        except SystemExit as exc:
            code = int(exc.code) if isinstance(exc.code, int) else 1
        except Exception as exc:  # noqa: BLE001 — batch mag niet sterven
            print(f"FOUT ({name}): {exc}", file=sys.stderr, flush=True)
            code = 1
        elapsed = time.perf_counter() - t0
        remaining -= 1
        if code == SKIP or code < 0:
            skipped += 1
        elif code == 0:
            record_sample(kind, elapsed)
            ok += 1
        else:
            record_sample(kind, elapsed)
            failed += 1
        stats = mean_seconds(kind)
        if remaining > 0 and stats is not None and code >= 0:
            mean, _ = stats
            print(
                f"  … {i}/{len(items)} klaar; "
                f"nog ~{format_duration(mean * remaining)} "
                f"({remaining} bestanden)",
                flush=True,
            )
    return ok, failed, skipped
