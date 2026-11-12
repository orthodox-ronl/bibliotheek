"""Herschrijf zoektekst (frase per regel) op catalogus + input vanaf HEAD.

Laat overige working-tree-wijzigingen (soort/toon, docs, …) buiten deze run:
alleen tracked .vsa/.mvsa onder content-source/catalogus en content-source/input.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLING_SRC = REPO.parent / "VSA-tooling" / "src"
sys.path.insert(0, str(TOOLING_SRC))

from vsa.zoektekst import apply_zoektekst, kind_from_path  # noqa: E402

ROOTS = (
    Path("content-source/catalogus"),
    Path("content-source/input"),
)


def tracked_vsa_mvsa() -> list[Path]:
    out = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "content-source/catalogus", "content-source/input"],
        cwd=REPO,
    )
    paths: list[Path] = []
    for raw in out.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace").replace("/", "\\")
        p = Path(rel)
        if p.suffix.lower() in {".vsa", ".mvsa"}:
            paths.append(p)
    return sorted(paths)


def head_text(rel: Path) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"HEAD:{rel.as_posix()}"],
        cwd=REPO,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8")


def main() -> int:
    changed = 0
    skipped = 0
    errors: list[str] = []
    for rel in tracked_vsa_mvsa():
        text = head_text(rel)
        if text is None:
            skipped += 1
            continue
        try:
            kind = kind_from_path(rel)
            result = apply_zoektekst(text, kind=kind)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel}: {exc}")
            continue
        if not result.changed:
            # Schrijf HEAD terug als working tree vies was, zodat alleen
            # zoektekst-diff overblijft wanneer changed; anders HEAD.
            abs_path = REPO / rel
            if abs_path.read_text(encoding="utf-8") != text:
                abs_path.write_text(text, encoding="utf-8", newline="\n")
            skipped += 1
            continue
        abs_path = REPO / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(result.text, encoding="utf-8", newline="\n")
        changed += 1
        print(f"updated {rel}")
    print(f"\n{changed} updated, {skipped} unchanged/skip, {len(errors)} errors")
    for e in errors[:20]:
        print(f"  ERROR {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
