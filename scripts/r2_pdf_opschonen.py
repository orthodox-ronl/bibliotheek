"""Wis lokale blad-PDF's die inhoudelijk gelijk zijn aan R2 production/.

Vergelijkt SHA-256 met object-metadata ``sha256`` (gezet door r2-pdf-upload).
Zonder metadata: object downloaden en hashen (traag; liever opnieuw uploaden).

Default: --dry-run (alleen melden). Met --apply: wissen; tracked → git rm.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import r2_pdf_upload as r2

CONTENT = r2.CONTENT
ROOT = r2.ROOT


def _git_tracked(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=str(ROOT),
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def _r2_sha256(client, bucket: str, key: str) -> str | None:
    try:
        head = client.head_object(Bucket=bucket, Key=key)
    except Exception:
        return None
    meta = head.get("Metadata") or {}
    # S3/R2 normaliseert metadata-keys naar lowercase
    digest = (meta.get("sha256") or meta.get("Sha256") or "").strip()
    if digest:
        return digest.lower()
    # Fallback: body hashen
    try:
        obj = client.get_object(Bucket=bucket, Key=key)
        body = obj["Body"]
        import hashlib

        h = hashlib.sha256()
        for chunk in iter(lambda: body.read(1024 * 1024), b""):
            h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Verwijder lokale blad-PDF's die gelijk zijn aan R2 production/."
        )
    )
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Bestand of map (default: content-source)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Echt wissen (default: alleen tonen)",
    )
    ap.add_argument(
        "--fail-if-tracked-on-main",
        action="store_true",
        help="Exit 1 als getrackte blad-PDF's bestaan en branch main is",
    )
    args = ap.parse_args(argv)

    branch = ""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            branch = (proc.stdout or "").strip()
    except OSError:
        pass

    if args.fail_if_tracked_on_main:
        # Alleen git-index; geen R2-credentials nodig.
        proc = subprocess.run(
            [
                "git",
                "ls-files",
                "**/index.md.pdf",
                "**/index.md.translit*.pdf",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        tracked_paths = [
            ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()
        ]
        if branch == "main" and tracked_paths:
            print(
                f"FOUT: {len(tracked_paths)} getrackte blad-PDF(s) op branch main. "
                "Upload naar R2 en draai r2-pdf-opschonen --apply, "
                "of haal ze uit de index.",
                file=sys.stderr,
            )
            for p in tracked_paths[:15]:
                print(f"  {p}", file=sys.stderr)
            if len(tracked_paths) > 15:
                print(f"  … +{len(tracked_paths) - 15}", file=sys.stderr)
            return 1
        if branch == "main":
            print("OK: geen getrackte blad-PDF’s op main")
        else:
            print(f"OK: main-guard overgeslagen (branch={branch or '?'})")
        return 0

    roots = args.paths or [CONTENT]
    pdfs = r2._iter_pdfs(roots)

    if not pdfs:
        print("Geen lokale blad-PDF's gevonden.")
        return 0

    client, bucket, endpoint, _account = r2.r2_client()
    print(f"Bucket={bucket} Endpoint={endpoint}")
    print(f"{len(pdfs)} lokale PDF(s); mode={'APPLY' if args.apply else 'DRY-RUN'}")

    same = 0
    missing = 0
    differ = 0
    removed = 0

    for pdf in pdfs:
        key = r2.object_key(pdf)
        local_hash = r2.sha256_file(pdf)
        remote = _r2_sha256(client, bucket, key)
        rel = pdf.relative_to(ROOT).as_posix()
        if remote is None:
            print(f"SKIP  geen R2-object  {rel}")
            missing += 1
            continue
        if remote != local_hash:
            print(f"DIFF  {rel}")
            differ += 1
            continue
        same += 1
        tracked_flag = " tracked" if _git_tracked(pdf) else ""
        if not args.apply:
            print(f"SAME  zou wissen{tracked_flag}  {rel}")
            continue
        if _git_tracked(pdf):
            proc = subprocess.run(
                ["git", "rm", "-f", "--", str(pdf.relative_to(ROOT))],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                # Bestand al untracked in index maar nog op schijf
                pdf.unlink(missing_ok=True)
                print(f"DEL   (unlink na git-rm fail)  {rel}")
            else:
                print(f"DEL   git rm  {rel}")
        else:
            pdf.unlink(missing_ok=True)
            print(f"DEL   {rel}")
        removed += 1

    print(
        f"Klaar: same={same} differ={differ} missing_on_r2={missing} "
        f"removed={removed}"
    )
    if not args.apply and same:
        print("Voeg --apply toe om gelijke PDF's lokaal te wissen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
