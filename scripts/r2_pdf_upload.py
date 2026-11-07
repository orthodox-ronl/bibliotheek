"""Upload blad-PDF's (index.md.pdf / translit) naar Cloudflare R2.

Padschema (docs/plans/pdf-r2.md):
  {env}/{relatief-pad-onder-content-source}/{bestandsnaam}

Vereist (S3-compatibel API van R2):
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
Optioneel: R2_ENDPOINT (default https://{account}.r2.cloudflarestorage.com).
EU-jurisdiction: https://{account}.eu.r2.cloudflarestorage.com
(of R2_JURISDICTION=eu → zelfde endpoint).

Zonder credentials: --dry-run toont alleen de object-sleutels.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content-source"
PDF_NAMES = (
    "index.md.pdf",
    "index.md.translit-nls.pdf",
    "index.md.translit-ksl.pdf",
    "index.md.translit-beide.pdf",
)


def _die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _iter_pdfs(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        p = p.resolve()
        if p.is_file():
            if p.name in PDF_NAMES:
                found.append(p)
            continue
        if not p.is_dir():
            _die(f"Geen bestand of map: {p}")
        for name in PDF_NAMES:
            found.extend(p.rglob(name))
    # Uniek, stabiele volgorde
    return sorted({f.resolve() for f in found})


def _object_key(env: str, pdf: Path) -> str:
    try:
        rel = pdf.relative_to(CONTENT).as_posix()
    except ValueError:
        _die(f"PDF ligt niet onder content-source: {pdf}")
    return f"{env}/{rel}"


_R2_ENV_KEYS = (
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET",
    "R2_JURISDICTION",
    "R2_ENDPOINT",
)


def _r2_creds_present() -> bool:
    return all(os.environ.get(k, "").strip() for k in _R2_ENV_KEYS[:4])


def _apply_r2_env_lines(text: str) -> int:
    """Zet R2_* uit 'set'- of 'Name=Value'-regels in os.environ. Retourneert aantal."""
    n = 0
    for raw in text.splitlines():
        line = raw.strip()
        if line.lower().startswith("set "):
            line = line[4:].strip()
        if "=" not in line:
            continue
        name, _, val = line.partition("=")
        name = name.strip()
        if name not in _R2_ENV_KEYS:
            continue
        val = val.strip().strip('"').strip("'")
        if val:
            os.environ[name] = val
            n += 1
    return n


def ensure_r2_env() -> None:
    """Laad scripts/r2-env.cmd of .ps1 als credentials nog ontbreken.

    Schrijvende Cloudflare-scripts roepen dit aan vóór de API-client.
    """
    if _r2_creds_present():
        return

    import subprocess

    cmd_env = ROOT / "scripts" / "r2-env.cmd"
    ps_env = ROOT / "scripts" / "r2-env.ps1"

    if cmd_env.is_file():
        # call + set: alleen R2_* teruggeven (secrets niet op stdout van dit script)
        proc = subprocess.run(
            ["cmd.exe", "/d", "/c", f'call "{cmd_env}" >nul && set R2_'],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if proc.returncode == 0 and _apply_r2_env_lines(proc.stdout):
            if _r2_creds_present():
                print("R2-env geladen uit scripts\\r2-env.cmd")
                return

    if ps_env.is_file():
        ps = (
            f'. "{ps_env}"; '
            "Get-ChildItem Env:R2_* | ForEach-Object { "
            '"{0}={1}" -f $_.Name, $_.Value }'
        )
        proc = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps,
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if proc.returncode == 0 and _apply_r2_env_lines(proc.stdout):
            if _r2_creds_present():
                print("R2-env geladen uit scripts\\r2-env.ps1")
                return


def _client():
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        _die(
            "Python-pakket boto3 ontbreekt. Installeer met:\n"
            "  pip install boto3\n"
            "Of gebruik eerst --dry-run (geen upload)."
        )

    ensure_r2_env()

    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key = os.environ.get("R2_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("R2_SECRET_ACCESS_KEY", "").strip()
    bucket = os.environ.get("R2_BUCKET", "").strip()
    if not all([account, key, secret, bucket]):
        _die(
            "R2-credentials ontbreken. Vul scripts\\r2-env.cmd of "
            "scripts\\r2-env.ps1 in (sjabloon: r2-env.*.example),\n"
            "of zet R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY "
            "en R2_BUCKET. Of gebruik --dry-run."
        )

    endpoint = os.environ.get("R2_ENDPOINT", "").strip()
    if not endpoint:
        juris = os.environ.get("R2_JURISDICTION", "").strip().lower()
        if juris in ("eu", "fedramp", "us"):
            endpoint = f"https://{account}.{juris}.r2.cloudflarestorage.com"
        else:
            endpoint = f"https://{account}.r2.cloudflarestorage.com"
    # pub-….r2.dev is de publieke host, géén Account ID.
    if account.lower().startswith("pub-") or "r2.dev" in account.lower():
        _die(
            "R2_ACCOUNT_ID lijkt op de publieke r2.dev-URL. Gebruik het "
            "Account ID uit het Cloudflare-dashboard (rechterzijde), niet "
            "pub-… uit de Public Bucket URL."
        )
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    return client, bucket, endpoint, account


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Upload blad-PDF's naar Cloudflare R2 "
            "(production/ of preview/ + pad onder content-source)."
        )
    )
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Bestand of map onder content-source (default: hele content-source)",
    )
    ap.add_argument(
        "--env",
        choices=("production", "preview"),
        help="R2-map: production of preview (strikt gescheiden; verplicht behalve bij --list-buckets)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Alleen sleutels tonen; niets uploaden",
    )
    ap.add_argument(
        "--list-buckets",
        action="store_true",
        help="Toon buckets zichtbaar voor deze credentials (diagnose); geen upload",
    )
    args = ap.parse_args(argv)

    if args.list_buckets:
        client, _bucket, endpoint, account = _client()
        print(f"Endpoint={endpoint}")
        print(f"Account ID (eerste 6)={account[:6]}…")
        try:
            resp = client.list_buckets()
        except Exception as exc:
            _die(
                f"list_buckets mislukt: {exc}\n"
                "Probeer bij EU-bucket:\n"
                "  $env:R2_ENDPOINT = "
                '"https://<ACCOUNT_ID>.eu.r2.cloudflarestorage.com"'
            )
        names = [b.get("Name", "") for b in resp.get("Buckets", [])]
        if not names:
            print("Geen buckets zichtbaar voor dit token/account.")
            print(
                "Tip: bucket staat misschien onder een ander account, "
                "of R2_ENDPOINT moet .eu. hebben (Location = European Union)."
            )
            return 1
        print("Zichtbare buckets:")
        want = os.environ.get("R2_BUCKET", "").strip()
        for name in names:
            mark = " ← R2_BUCKET" if name == want else ""
            print(f"  - {name}{mark}")
        return 0

    if not args.env:
        _die("Geef --env production of --env preview (of gebruik --list-buckets).")

    roots = args.paths or [CONTENT]
    pdfs = _iter_pdfs(roots)
    if not pdfs:
        print("Geen blad-PDF's gevonden.")
        return 0

    print(f"{len(pdfs)} PDF(s) → env={args.env}")
    client = bucket = None
    if not args.dry_run:
        client, bucket, endpoint, account = _client()
        print(f"Bucket={bucket}")
        print(f"Endpoint={endpoint}")
        print(f"Account ID (eerste 6)={account[:6]}…")
        try:
            client.head_bucket(Bucket=bucket)
        except Exception as exc:
            _die(
                "Bucket niet bereikbaar (NoSuchBucket / AccessDenied).\n"
                f"Detail: {exc}\n\n"
                "Controleer:\n"
                "  1. R2_ACCOUNT_ID = Account ID in het dashboard (rechts), "
                "NIET pub-… uit r2.dev\n"
                "  2. R2_BUCKET = exacte bucketnaam (hoofdletters tellen)\n"
                "  3. API-token hoort bij hetzelfde Cloudflare-account "
                "als die bucket\n"
                "  4. Bucket Location = European Union? Zet dan:\n"
                "       $env:R2_ENDPOINT = "
                f'"https://{account}.eu.r2.cloudflarestorage.com"\n'
                "  5. Diagnose: python scripts\\r2_pdf_upload.py "
                "--list-buckets --env preview"
            )

    ok = 0
    for pdf in pdfs:
        key = _object_key(args.env, pdf)
        if args.dry_run:
            print(f"DRY  {key}")
            ok += 1
            continue
        assert client is not None and bucket is not None
        extra = {"ContentType": "application/pdf"}
        try:
            client.upload_file(str(pdf), bucket, key, ExtraArgs=extra)
        except Exception as exc:
            _die(f"Upload mislukt voor {key}:\n{exc}")
        print(f"PUT  {key}", flush=True)
        ok += 1
        if ok % 25 == 0:
            print(f"… {ok}/{len(pdfs)}", flush=True)

    print(f"Klaar: {ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
