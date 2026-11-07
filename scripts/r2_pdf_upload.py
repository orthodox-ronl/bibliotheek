"""Upload blad-PDF's (index.md.pdf / translit) naar Cloudflare R2.

Padschema (docs/plans/pdf-r2.md):
  production/{relatief-pad-onder-content-source}/{bestandsnaam}

Alleen de map production/ (één set). Bij PUT: metadata sha256=<hex>.

Vereist (S3-compatibel API van R2):
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
Optioneel: R2_ENDPOINT of R2_JURISDICTION=eu.

Zonder credentials: --dry-run toont alleen de object-sleutels.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content-source"
R2_ENV = "production"
PDF_NAMES = (
    "index.md.pdf",
    "index.md.translit-nls.pdf",
    "index.md.translit-ksl.pdf",
    "index.md.translit-beide.pdf",
)

_R2_ENV_KEYS = (
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET",
    "R2_JURISDICTION",
    "R2_ENDPOINT",
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
    return sorted({f.resolve() for f in found})


def object_key(pdf: Path, env: str = R2_ENV) -> str:
    try:
        rel = pdf.relative_to(CONTENT).as_posix()
    except ValueError:
        _die(f"PDF ligt niet onder content-source: {pdf}")
    return f"{env}/{rel}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _r2_creds_present() -> bool:
    return all(os.environ.get(k, "").strip() for k in _R2_ENV_KEYS[:4])


def _apply_r2_env_lines(text: str) -> int:
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
    """Laad scripts/r2-env.cmd of .ps1 als credentials nog ontbreken."""
    if _r2_creds_present():
        return

    import subprocess

    cmd_env = ROOT / "scripts" / "r2-env.cmd"
    ps_env = ROOT / "scripts" / "r2-env.ps1"

    if cmd_env.is_file():
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


def r2_client():
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
            "Upload blad-PDF's naar Cloudflare R2 (alleen production/)."
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
        default=R2_ENV,
        help="Alleen 'production' (default). 'preview' is niet meer toegestaan.",
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
    ap.add_argument(
        "--purge-prefix",
        metavar="PREFIX",
        help="Wis alle objecten onder PREFIX/ in de bucket (bijv. preview). "
        "Vereist --apply-purge. Geen upload.",
    )
    ap.add_argument(
        "--apply-purge",
        action="store_true",
        help="Echt wissen bij --purge-prefix (anders alleen tonen).",
    )
    args = ap.parse_args(argv)

    if args.list_buckets:
        client, _bucket, endpoint, account = r2_client()
        print(f"Endpoint={endpoint}")
        print(f"Account ID (eerste 6)={account[:6]}…")
        try:
            resp = client.list_buckets()
        except Exception as exc:
            _die(
                f"list_buckets mislukt: {exc}\n"
                "Probeer bij EU-bucket: R2_JURISDICTION=eu"
            )
        names = [b.get("Name", "") for b in resp.get("Buckets", [])]
        if not names:
            print("Geen buckets zichtbaar voor dit token/account.")
            return 1
        print("Zichtbare buckets:")
        want = os.environ.get("R2_BUCKET", "").strip()
        for name in names:
            mark = " ← R2_BUCKET" if name == want else ""
            print(f"  - {name}{mark}")
        return 0

    if args.purge_prefix is not None:
        prefix = args.purge_prefix.strip().strip("/")
        if not prefix:
            _die("Geef een niet-lege --purge-prefix (bijv. preview).")
        prefix = prefix + "/"
        client, bucket, endpoint, account = r2_client()
        print(f"Bucket={bucket} Endpoint={endpoint}")
        print(f"Prefix={prefix}")
        token = None
        keys: list[str] = []
        while True:
            kw: dict = {"Bucket": bucket, "Prefix": prefix}
            if token:
                kw["ContinuationToken"] = token
            resp = client.list_objects_v2(**kw)
            for obj in resp.get("Contents") or []:
                keys.append(obj["Key"])
            if not resp.get("IsTruncated"):
                break
            token = resp.get("NextContinuationToken")
        print(f"{len(keys)} object(en) onder {prefix}")
        if not args.apply_purge:
            for k in keys[:20]:
                print(f"DRY  delete {k}")
            if len(keys) > 20:
                print(f"… +{len(keys) - 20} meer")
            print("Voeg --apply-purge toe om te wissen.")
            return 0
        # Batch delete (max 1000)
        deleted = 0
        for i in range(0, len(keys), 1000):
            chunk = keys[i : i + 1000]
            client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": k} for k in chunk], "Quiet": True},
            )
            deleted += len(chunk)
            print(f"DEL  {deleted}/{len(keys)}", flush=True)
        print(f"Klaar: {deleted} gewist")
        return 0

    env = (args.env or R2_ENV).strip().lower()
    if env != R2_ENV:
        _die(
            f"--env {args.env!r} mag niet. Alleen production/ "
            "(één R2-set; preview-map is afgeschaft)."
        )

    roots = args.paths or [CONTENT]
    pdfs = _iter_pdfs(roots)
    if not pdfs:
        print("Geen blad-PDF's gevonden.")
        return 0

    print(f"{len(pdfs)} PDF(s) → env={env}")
    client = bucket = None
    if not args.dry_run:
        client, bucket, endpoint, account = r2_client()
        print(f"Bucket={bucket}")
        print(f"Endpoint={endpoint}")
        print(f"Account ID (eerste 6)={account[:6]}…")
        try:
            client.head_bucket(Bucket=bucket)
        except Exception as exc:
            _die(
                "Bucket niet bereikbaar (NoSuchBucket / AccessDenied).\n"
                f"Detail: {exc}\n"
                "Zet R2_JURISDICTION=eu bij EU-bucket; "
                "diagnose: --list-buckets"
            )

    ok = 0
    for pdf in pdfs:
        key = object_key(pdf, env)
        digest = sha256_file(pdf)
        if args.dry_run:
            print(f"DRY  {key} sha256={digest[:12]}…")
            ok += 1
            continue
        assert client is not None and bucket is not None
        extra = {
            "ContentType": "application/pdf",
            "Metadata": {"sha256": digest},
        }
        try:
            client.upload_file(str(pdf), bucket, key, ExtraArgs=extra)
        except Exception as exc:
            _die(f"Upload mislukt voor {key}:\n{exc}")
        print(f"PUT  {key} sha256={digest[:12]}…", flush=True)
        ok += 1
        if ok % 25 == 0:
            print(f"… {ok}/{len(pdfs)}", flush=True)

    print(f"Klaar: {ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
