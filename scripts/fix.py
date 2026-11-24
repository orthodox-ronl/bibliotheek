"""Afwerklijst uit check: tonen (--dry-run) of uitvoeren (fix_cmd per regel).

Met ``--check`` eerst ``check --strict`` (lijst vernieuwen); problemen
(exit 1) zijn verwacht. Harde check-fout (validate/tooling) stopt fix.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from batch_guard import add_yes_argument, confirm_batch
from check_fixlist import (
    FIXLIST_PATH,
    FixItem,
    load_fixlist,
    print_fixlist,
    save_fixlist,
    write_fixlist,
)
from cli_style import (
    add_verbose_argument,
    count,
    detail,
    error,
    hard,
    note,
    ok,
    refuse,
    run_quiet,
    section,
    set_verbose,
    work,
)
from fix_cmds import is_products_fix_cmd
from input_paths import rel_for_log

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_CMD = REPO_ROOT / "scripts" / "check.cmd"
FIX_LOG_PATH = REPO_ROOT / "data" / "fix-last.log"

# Regels die geen korte foutreden zijn (banners / meta van kind-scripts).
_NOISE_LINE_PREFIXES = (
    "===",
    ">>>",
    "VSA-tooling:",
    "Batch «",
    "Bevestiging:",
    "Geschatte duur:",
    "Root:",
    "Actie:",
    "Condities:",
    "Bestand:",
    "Elke regel",
    "FAILED exit=",
    "OK ",
    "OK:",
    "Oplossing:",
    "Werkvoorraad",
    "Werkbank",
    "Controle:",
    "Zie:",
    "fix:",
)


def _is_noise_line(line: str) -> bool:
    text = (line or "").strip()
    if not text:
        return True
    if any(text.startswith(p) for p in _NOISE_LINE_PREFIXES):
        return True
    if text.endswith(" items") and text[:1].isdigit():
        return True
    if "  items" in text and text.lstrip()[:1].isdigit():
        return True
    low = text.lower()
    if low.startswith("vsa:") and "bron" in low:
        return True
    if "mislukt-" in low and text.lstrip()[:1].isdigit():
        return True
    if "kinds-mislukt" in low:
        return True
    if "bijwerken (van" in low:
        return True
    return False


# ``catalogus/…/lied.vsa:29:28: hoogte-mismatch…`` (of Windows-pad).
_LOC_REASON_RE = re.compile(
    r"^(?P<loc>\S+\.\S+:\d+:\d+):\s+(?P<body>.+)$"
)


def _extract_child_failure_reason(text: str) -> str:
    """Haal één korte reden uit kind-script-uitvoer (geen hele banner-dump).

    Voorkeur: regel met ``bestand:regel:kolom:`` (VSA-tooling / explain).
    """
    lines = [ln.rstrip() for ln in (text or "").splitlines()]

    def _from_candidates(cands: list[str]) -> str | None:
        # 1) Locatieregel met inhoudelijke body (niet alleen een CODE).
        for s in cands:
            m = _LOC_REASON_RE.match(s)
            if not m:
                continue
            body = m.group("body").strip()
            if body.startswith("VSA-") and " " not in body and "-" in body:
                continue
            return s
        # 2) Locatie + volgende mismatch-regel samenvoegen.
        for i, s in enumerate(cands):
            m = _LOC_REASON_RE.match(s)
            if not m:
                continue
            body = m.group("body").strip()
            if body.startswith("VSA-"):
                for nxt in cands[i + 1 :]:
                    if _is_noise_line(nxt) or nxt.startswith("Oplossing:"):
                        continue
                    return f"{m.group('loc')}: {nxt}"
            return s
        markers = (
            "hoogte-mismatch",
            "meerdere templates",
            "template-slot",
            "ERROR:",
        )
        for s in cands:
            low = s.lower()
            if any(m in low for m in markers):
                return s
        return None

    after_mislukt: list[str] = []
    for i, ln in enumerate(lines):
        if not ln.strip().startswith("MISLUKT "):
            continue
        for nxt in lines[i + 1 :]:
            s = nxt.strip()
            if not s:
                continue
            if s.startswith("Oplossing:"):
                break
            if _is_noise_line(s):
                continue
            after_mislukt.append(s)
        hit = _from_candidates(after_mislukt)
        if hit:
            return hit
        if after_mislukt:
            return after_mislukt[0]

    all_cands = [
        ln.strip()
        for ln in lines
        if ln.strip() and not _is_noise_line(ln.strip())
    ]
    hit = _from_candidates(all_cands)
    if hit:
        return hit
    for ln in reversed(lines):
        s = ln.strip()
        if _is_noise_line(s):
            continue
        if s.startswith("MISLUKT "):
            continue
        return s
    return "herstel mislukt (geen korte reden; gebruik --verbose)"


def _failure_group(reason: str, kind: str = "") -> str:
    """Korte groepsnaam voor de eindsamenvatting."""
    low = (reason or "").lower()
    if "hoogte-mismatch" in low:
        return "hoogte-mismatch"
    if "meerdere templates" in low:
        return "meerdere templates"
    if "template-slot" in low:
        return "template-slots"
    if kind:
        from check_report import short_kind

        return short_kind(kind)
    head = (reason or "").strip()
    if not head:
        return "onbekend"
    if len(head) > 72:
        return head[:69] + "..."
    return head


def _item_path_label(item: FixItem) -> str:
    """Bronbestand of map: liever ``.vsa``/``.mvsa`` dan alleen de leaf-map."""
    for raw in (item.file, item.source):
        text = _rel_content_like(raw)
        if not text:
            continue
        # Meta-sidecar → onderliggende bron.
        for suf in (
            ".vsa.products-meta.json",
            ".mvsa.products-meta.json",
            ".mscz.products-meta.json",
            ".products-meta.json",
        ):
            if text.endswith(suf):
                text = text[: -len(suf)]
                break
        if text.endswith((".vsa", ".mvsa", ".mscz", ".md")):
            return text
    # fix_cmd eindigt vaak op het bronbestand.
    cmd = (item.fix_cmd or "").replace("/", "\\")
    for tok in reversed(cmd.split()):
        t = tok.strip('"').replace("\\", "/")
        low = t.lower()
        if low.endswith((".vsa", ".mvsa", ".mscz", ".md")):
            if "content-source/" in t:
                t = t.split("content-source/", 1)[1]
            return t
    text = (item.summary or "").strip()
    if "] " in text:
        return text.split("] ", 1)[1]
    return text or item.id


def _rel_content_like(path_str: str) -> str:
    text = (path_str or "").replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    prefix = "content-source/"
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def _print_failed_groups(failures: list[tuple[FixItem, str]]) -> None:
    """Restfouten gegroepeerd: telling + pad + één redenregel."""
    groups: dict[str, list[tuple[FixItem, str]]] = defaultdict(list)
    for item, reason in failures:
        groups[_failure_group(reason, item.kind)].append((item, reason))
    section("Rest (handwerk), gegroepeerd:")
    for group, rows in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        count(len(rows), group, role="hard")
        for item, reason in rows:
            hard(f"  {_item_path_label(item)}")
            note(f"    {reason}")


def _fixlist_mtime() -> float:
    try:
        return FIXLIST_PATH.stat().st_mtime
    except OSError:
        return 0.0


def _run_check_strict(*, verbose: bool) -> int:
    """Run check --strict. Return process exit code."""
    cmd = ["cmd", "/c", str(CHECK_CMD), "--strict"]
    section("=== fix: check --strict (fixlist vernieuwen) ===")
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        check=False,
    )
    if verbose:
        detail(f"check --strict exit={proc.returncode}")
    return int(proc.returncode)


def _check_failed_before_fixlist(code: int, *, mtime_before: float) -> bool:
    """True als check stopte vóór een verse fixlist (validate/tooling/…).

    Exit 0/1 mét nieuwere fixlist = ok (0 groen, 1 productproblemen).
    Exit ≥2, of fixlist niet vernieuwd → niet afwerken.
    """
    if code >= 2:
        return True
    return _fixlist_mtime() <= mtime_before


def _refresh_fixlist_from_status() -> list[FixItem]:
    items = write_fixlist()
    count(len(items), "fixlist-items", role="work" if items else "ok")
    detail(rel_for_log(FIXLIST_PATH, repo_root=REPO_ROOT))
    return items


def _ensure_yes_flag(fix_cmd: str) -> str:
    """Voeg ``-y`` toe zodat kind-scripts niet opnieuw om bevestiging vragen."""
    text = (fix_cmd or "").strip()
    if not text:
        return text
    tokens = text.split()
    if "-y" in tokens or "--yes" in tokens:
        return text
    return f"{text} -y"


def _open_fix_log(path: Path = FIX_LOG_PATH) -> Path:
    """Maak/leg `data/fix-last.log` leeg met kopregel; return pad."""
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    header = (
        f"# fix-last.log — {stamp}\n"
        f"# Scherm = samenvatting; dit bestand = volledige kind-uitvoer.\n"
        f"# Repo: {REPO_ROOT}\n\n"
    )
    path.write_text(header, encoding="utf-8", newline="\n")
    return path


def _append_fix_log(
    path: Path,
    *,
    summary: str,
    cmd: str,
    code: int,
    stdout: str,
    stderr: str,
    elapsed_s: float,
) -> None:
    """Voeg één fix_cmd-blok toe aan de verbose-log."""
    parts = [
        f"===== {summary} =====",
        f"cmd: {cmd}",
        f"exit: {code}",
        f"duur: {elapsed_s:.1f}s",
    ]
    out = (stdout or "").rstrip()
    err = (stderr or "").rstrip()
    if out:
        parts.append("--- stdout ---")
        parts.append(out)
    if err:
        parts.append("--- stderr ---")
        parts.append(err)
    if not out and not err:
        parts.append("(geen stdout/stderr)")
    parts.append("")
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts) + "\n")


def _run_fix_cmd(
    fix_cmd: str,
    *,
    summary: str = "",
    log_path: Path | None = None,
) -> tuple[int, str]:
    """Voer één fix_cmd uit. Return ``(exitcode, korte_reden)``.

    Scherm blijft kort. Met ``log_path`` gaat de volledige kind-uitvoer
    naar dat bestand (``--verbose``).
    """
    # Parent (fix) heeft al bevestigd: kind-batches stil door (-y).
    cmd = _ensure_yes_flag(fix_cmd)
    t0 = time.perf_counter()
    proc = subprocess.run(
        ["cmd", "/c", cmd],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    elapsed = time.perf_counter() - t0
    code = int(proc.returncode)
    out = proc.stdout or ""
    err = proc.stderr or ""
    if log_path is not None:
        _append_fix_log(
            log_path,
            summary=summary or cmd,
            cmd=cmd,
            code=code,
            stdout=out,
            stderr=err,
            elapsed_s=elapsed,
        )
    if code == 0:
        return 0, ""
    combined = "\n".join(p for p in (out, err) if p)
    return code, _extract_child_failure_reason(combined)


def _run_products_post(*, verbose: bool) -> int:
    """Zoekindex, gebreken-stempels + Coria-fingerprints, één keer na de fixes.

    De fix-commando’s lopen met ``--skip-post``; ``products`` zet dan ook de
    gebreken-stempels op de SVG’s niet. Die stap hoort hier (net als in
    ``products`` zelf), anders meldt check "SVG mist stempel".
    """
    section(">>> nabewerking (zoekindex, gebreken-stempels, Coria-fingerprints)")
    from build_zoek_index import main as build_zoek_main

    if run_quiet("zoekindex", build_zoek_main, [], verbose=verbose):
        return 1
    import gebreken as gebreken_mod

    def _stempels(_args: list[str]) -> int:
        _touched, changed, seen = gebreken_mod.sync_gebreken_stempels_under(
            gebreken_mod.CATALOGUS_ROOT
        )
        detail(f"gebreken-stempels: {changed} SVG gewijzigd ({seen} bekeken)")
        return 0

    if run_quiet("gebreken-stempels", _stempels, [], verbose=verbose):
        return 1
    import fingerprint_coria_mxl as fp_mod

    if run_quiet("fingerprints", lambda _a: fp_mod.main(), [], verbose=verbose):
        return 1
    import probe_coria_fetch as probe_mod

    if run_quiet(
        "coria-probe",
        lambda _a: probe_mod.apply_probe(warn_only=True),
        [],
        verbose=verbose,
    ):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Toon of werk de check-fixlist af (één fix_cmd per regel). "
            "Met --check eerst check --strict."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "voorbeelden:\n"
            "  python scripts/fix.py --dry-run\n"
            "  python scripts/fix.py --check --dry-run\n"
            "  python scripts/fix.py --strict --dry-run\n"
            "  python scripts/fix.py --check\n"
            "  python scripts/fix.py -y\n"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Toon de lijst; voer geen fix_cmd uit.",
    )
    parser.add_argument(
        "--check",
        "--strict",
        dest="check",
        action="store_true",
        help=(
            "Eerst check --strict (lijst opnieuw bouwen), daarna tonen/afwerken. "
            "--strict is hetzelfde als --check."
        ),
    )
    add_verbose_argument(parser)
    add_yes_argument(parser)
    args = parser.parse_args(argv)
    set_verbose(bool(args.verbose))

    if args.check:
        mtime_before = _fixlist_mtime()
        code = _run_check_strict(verbose=bool(args.verbose))
        if _check_failed_before_fixlist(code, mtime_before=mtime_before):
            error(
                f"check --strict leverde geen verse fixlist "
                f"(exit {code}). Geen afwerken. "
                "Herstel validate/tooling eerst, of draai check opnieuw."
            )
            return 2
        # check.cmd schreef al; opnieuw aggregaten dekt race/handmatige status.
        items = _refresh_fixlist_from_status()
    else:
        if not FIXLIST_PATH.is_file():
            error(
                "Geen fixlist gevonden (data\\check-fixlist.json). "
                "Oplossing: scripts\\check.cmd of scripts\\fix.cmd --check"
            )
            return 2
        items = load_fixlist()

    if args.dry_run:
        print_fixlist(items)
        ok("OK  dry-run (niets gefixt)")
        return 0

    if not items:
        ok("OK  fixlist leeg")
        return 0

    if not confirm_batch(
        "fix",
        n=len(items),
        headline=f"{len(items)} auto-fix(es) uit check-fixlist",
        details=[
            f"Bestand: {rel_for_log(FIXLIST_PATH, repo_root=REPO_ROOT)}",
            "Elke regel = één fix_cmd (zoals check voorstelt).",
        ],
        yes=bool(args.yes),
    ):
        refuse("WEIGERT  fix afgebroken (geen bevestiging)")
        return 2

    remaining = list(items)
    fixed = 0
    failed = 0
    done_cmds: set[str] = set()
    products_ok = 0
    failures: list[tuple[FixItem, str]] = []
    log_path: Path | None = None
    if args.verbose:
        log_path = _open_fix_log()
        note(
            f"Detail-log: {rel_for_log(log_path, repo_root=REPO_ROOT)} "
            "(scherm blijft samenvatting)"
        )

    for item in list(items):
        if item.fix_cmd in done_cmds:
            remaining = [x for x in remaining if x.fix_cmd != item.fix_cmd]
            save_fixlist(remaining)
            detail(f">>> {item.summary} (zelfde fix_cmd al ok)")
            continue
        work(f">>> {item.summary}")
        t0 = time.perf_counter()
        code, reason = _run_fix_cmd(
            item.fix_cmd,
            summary=item.summary,
            log_path=log_path,
        )
        elapsed = time.perf_counter() - t0
        if code == 0:
            fixed += 1
            done_cmds.add(item.fix_cmd)
            if is_products_fix_cmd(item.fix_cmd):
                products_ok += 1
            remaining = [x for x in remaining if x.fix_cmd != item.fix_cmd]
            save_fixlist(remaining)
            detail(f"    OK ({elapsed:.1f}s, {len(remaining)} rest)")
        else:
            failed += 1
            failures.append((item, reason or "herstel mislukt"))
            hard(f"    {reason or 'herstel mislukt'}")

    if products_ok and failed == 0:
        post = _run_products_post(verbose=bool(args.verbose))
        if post != 0:
            if log_path is not None:
                note(
                    f"Detail-log: {rel_for_log(log_path, repo_root=REPO_ROOT)}"
                )
            return 1

    section("=== Samenvatting fix ===")
    count(fixed, "ok", role="ok")
    count(failed, "mislukt", role="hard" if failed else "info")
    count(len(remaining), "rest", role="work" if remaining else "info")
    if log_path is not None:
        note(f"Detail-log: {rel_for_log(log_path, repo_root=REPO_ROOT)}")
    if failed:
        _print_failed_groups(failures)
        hard(
            "Oplossing: herstel de rest hierboven; daarna "
            "scripts\\fix.cmd opnieuw (of --dry-run)."
            + (
                f" Volledige kind-uitvoer: "
                f"{rel_for_log(log_path, repo_root=REPO_ROOT)}."
                if log_path is not None
                else " Volledige kind-uitvoer: --verbose → data\\fix-last.log."
            )
        )
        return 1
    ok("OK  fixlist leeg" if not remaining else "OK  fix afgerond")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
