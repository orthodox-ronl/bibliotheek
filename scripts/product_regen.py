"""Gedeelde regeneratie-condities voor bibliotheek-producten.

Condities (default: alle drie):

- ``missing`` — productbestand ontbreekt
- ``stale`` — bestand bestaat, maar herkomststempel past niet bij de bron
- ``invalid`` — bestand bestaat, maar faalt een contractcheck (nu: ``mxl validate``)

``--force`` negeert condities en regenereert altijd.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REASON_MISSING = "missing"
REASON_STALE = "stale"
REASON_INVALID = "invalid"
ALL_REASONS = (REASON_MISSING, REASON_STALE, REASON_INVALID)


@dataclass(frozen=True)
class RegenPolicy:
    """Welke condities tot regeneratie leiden."""

    missing: bool = True
    stale: bool = True
    invalid: bool = True
    force: bool = False

    def active_reasons(self) -> tuple[str, ...]:
        if self.force:
            return ("force",)
        out: list[str] = []
        if self.missing:
            out.append(REASON_MISSING)
        if self.stale:
            out.append(REASON_STALE)
        if self.invalid:
            out.append(REASON_INVALID)
        return tuple(out)


def add_regen_arguments(parser: argparse.ArgumentParser) -> None:
    """Voeg --dry-run / --force / --only-* / --reasons toe."""
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenereer alle producten onder root (negeert missing/stale/invalid).",
    )
    only = parser.add_mutually_exclusive_group()
    only.add_argument(
        "--only-missing",
        action="store_true",
        help="Alleen als het productbestand ontbreekt.",
    )
    only.add_argument(
        "--only-stale",
        action="store_true",
        help="Alleen als het product bestaat maar de herkomststempel niet klopt.",
    )
    only.add_argument(
        "--only-invalid",
        action="store_true",
        help="Alleen als het product bestaat maar de contractcheck faalt.",
    )
    parser.add_argument(
        "--reasons",
        default=None,
        metavar="LIST",
        help=(
            "Komma-lijst: missing,stale,invalid (default: alle drie). "
            "Niet combineren met --only-*."
        ),
    )


def policy_from_args(args: argparse.Namespace) -> RegenPolicy:
    """Bouw RegenPolicy uit argparse-namespace (na add_regen_arguments)."""
    force = bool(getattr(args, "force", False))
    if force:
        return RegenPolicy(force=True)

    only_missing = bool(getattr(args, "only_missing", False))
    only_stale = bool(getattr(args, "only_stale", False))
    only_invalid = bool(getattr(args, "only_invalid", False))
    reasons_raw = getattr(args, "reasons", None)

    if sum([only_missing, only_stale, only_invalid]) > 1:
        raise SystemExit("Gebruik hoogstens één van --only-missing/--only-stale/--only-invalid")
    if reasons_raw and (only_missing or only_stale or only_invalid):
        raise SystemExit("--reasons niet combineren met --only-*")

    if only_missing:
        return RegenPolicy(missing=True, stale=False, invalid=False)
    if only_stale:
        return RegenPolicy(missing=False, stale=True, invalid=False)
    if only_invalid:
        return RegenPolicy(missing=False, stale=False, invalid=True)

    if reasons_raw is None or str(reasons_raw).strip() == "":
        return RegenPolicy()

    parts = [p.strip().lower() for p in str(reasons_raw).split(",") if p.strip()]
    unknown = [p for p in parts if p not in ALL_REASONS]
    if unknown:
        raise SystemExit(
            f"Onbekende --reasons: {', '.join(unknown)} "
            f"(verwacht: {', '.join(ALL_REASONS)})"
        )
    if not parts:
        raise SystemExit("--reasons mag niet leeg zijn")
    return RegenPolicy(
        missing=REASON_MISSING in parts,
        stale=REASON_STALE in parts,
        invalid=REASON_INVALID in parts,
    )


def need_regen(
    policy: RegenPolicy,
    *,
    exists: bool,
    stamp_ok: bool,
    contract_ok: bool | None = None,
) -> bool:
    """Of dit product opnieuw gegenereerd moet worden."""
    if policy.force:
        return True
    if not exists:
        return policy.missing
    # bestaat
    if policy.stale and not stamp_ok:
        return True
    if policy.invalid and contract_ok is False:
        return True
    return False


def mxl_contract_ok(path: Path, *, profile: str) -> bool | None:
    """``True``/``False`` na ``mxl validate``; ``None`` als CLI ontbreekt."""
    if not path.is_file():
        return None
    try:
        proc = subprocess.run(
            [
                "mxl",
                "validate",
                str(path),
                "--profile",
                profile,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        # Probeer python -m
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "vsa.cli_mxl",
                    "validate",
                    str(path),
                    "--profile",
                    profile,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            print(
                f"  WAARSCHUWING: mxl validate niet beschikbaar; "
                f"sla contract over voor {path.name}",
                flush=True,
            )
            return None
    return proc.returncode == 0


KIND_ORDER = (
    "vsa",
    "mscz",
    "tekstblad",
    "mvsa",
    "import",
    "audio",
    "lyrics",
)

KIND_HELP = {
    "vsa": "Coria-.vsa.mxl + .vsa.pdf",
    "mscz": ".mscz.pdf + .mscz.mxl",
    "tekstblad": ".tekstblad.pdf",
    "mvsa": ".mvsa.mxl + .mvsa.pdf",
    "import": "bestaande .mscz.mvsa-siblings",
    "audio": "preview-.mp3",
    "lyrics": ".lyrics.txt zoektekst",
}
