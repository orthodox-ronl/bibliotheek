"""Upload blad-PDF's (index.md.pdf / translit) naar Cloudflare R2.

Padschema (docs/plans/pdf-r2.md):
  production/{relatief-pad-onder-content-source}/{bestandsnaam}
  development/… — alleen diff t.o.v. production/ (+ manifest)

Bij PUT: metadata sha256=<hex>.

Vereist (S3-compatibel API van R2):
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
Optioneel: R2_ENDPOINT of R2_JURISDICTION=eu.

Zonder credentials: --dry-run toont alleen de object-sleutels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content-source"
MANIFEST_PATH = ROOT / "data" / "pdf-r2-development.json"
R2_ENV_PRODUCTION = "production"
R2_ENV_DEVELOPMENT = "development"
ALLOWED_ENVS = frozenset({R2_ENV_PRODUCTION, R2_ENV_DEVELOPMENT})
PDF_NAMES = (
    "index.md.pdf",
    "index.md.translit-nls.pdf",
    "index.md.translit-ksl.pdf",
    "index.md.translit-beide.pdf",
)
# Andere weergave-keuzes (incl. translit): index.md.weergave-vp[.translit-nls].pdf
PDF_VARIANT_GLOB = "index.md.weergave-*.pdf"

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
            if p.name in PDF_NAMES or p.match(PDF_VARIANT_GLOB):
                found.append(p)
            continue
        if not p.is_dir():
            _die(f"Geen bestand of map: {p}")
        for name in (*PDF_NAMES, PDF_VARIANT_GLOB):
            found.extend(p.rglob(name))
    return sorted({f.resolve() for f in found})


def content_rel(pdf: Path) -> str:
    try:
        return pdf.relative_to(CONTENT).as_posix()
    except ValueError:
        _die(f"PDF ligt niet onder content-source: {pdf}")
        raise  # unreachable


def object_key(pdf: Path, env: str = R2_ENV_PRODUCTION) -> str:
    return f"{env}/{content_rel(pdf)}"


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


def r2_object_sha256(client, bucket: str, key: str) -> str | None:
    try:
        head = client.head_object(Bucket=bucket, Key=key)
    except Exception:
        return None
    meta = head.get("Metadata") or {}
    digest = (meta.get("sha256") or meta.get("Sha256") or "").strip()
    if digest:
        return digest.lower()
    try:
        obj = client.get_object(Bucket=bucket, Key=key)
        body = obj["Body"]
        h = hashlib.sha256()
        for chunk in iter(lambda: body.read(1024 * 1024), b""):
            h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def list_keys(client, bucket: str, prefix: str) -> list[str]:
    if not prefix.endswith("/"):
        prefix = prefix + "/"
    keys: list[str] = []
    token = None
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
    return keys


def delete_keys(client, bucket: str, keys: list[str]) -> int:
    deleted = 0
    for i in range(0, len(keys), 1000):
        chunk = keys[i : i + 1000]
        if not chunk:
            continue
        client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": k} for k in chunk], "Quiet": True},
        )
        deleted += len(chunk)
    return deleted


def write_development_manifest(rels: list[str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"overrides": sorted(set(rels))}
    MANIFEST_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Manifest {MANIFEST_PATH.relative_to(ROOT).as_posix()} "
          f"({len(payload['overrides'])} overrides)")


def manifest_rels_from_keys(keys: list[str]) -> list[str]:
    out: list[str] = []
    prefix = f"{R2_ENV_DEVELOPMENT}/"
    for key in keys:
        if not key.startswith(prefix) or not key.endswith(".pdf"):
            continue
        out.append(key[len(prefix) :])
    return sorted(set(out))


def _upload_file(client, bucket: str, pdf: Path, key: str, digest: str) -> None:
    client.upload_file(
        str(pdf),
        bucket,
        key,
        ExtraArgs={
            "ContentType": "application/pdf",
            "Metadata": {"sha256": digest},
        },
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Upload blad-PDF's naar Cloudflare R2 "
            "(production/ of development/-diff)."
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
        default=R2_ENV_PRODUCTION,
        help="production (default) of development (alleen diff t.o.v. production)",
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
        help="Wis alle objecten onder PREFIX/ in de bucket "
        "(bijv. development of oude preview). Vereist --apply-purge.",
    )
    ap.add_argument(
        "--apply-purge",
        action="store_true",
        help="Echt wissen bij --purge-prefix (anders alleen tonen).",
    )
    ap.add_argument(
        "--restamp-metadata",
        action="store_true",
        help="Zet sha256-metadata op bestaande objecten onder production/ "
        "(download+hash+put; geen lokale PDF's nodig).",
    )
    ap.add_argument(
        "--only-missing-sha",
        action="store_true",
        help="Bij --restamp-metadata: sla objecten over die al sha256 hebben.",
    )
    ap.add_argument(
        "--write-manifest-from-r2",
        action="store_true",
        help="Schrijf data/pdf-r2-development.json uit R2 development/ "
        "(geen upload).",
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
            _die("Geef een niet-lege --purge-prefix (bijv. development).")
        prefix = prefix + "/"
        client, bucket, endpoint, account = r2_client()
        print(f"Bucket={bucket} Endpoint={endpoint}")
        print(f"Prefix={prefix}")
        keys = list_keys(client, bucket, prefix)
        print(f"{len(keys)} object(en) onder {prefix}")
        if not args.apply_purge:
            for k in keys[:20]:
                print(f"DRY  delete {k}")
            if len(keys) > 20:
                print(f"… +{len(keys) - 20} meer")
            print("Voeg --apply-purge toe om te wissen.")
            return 0
        deleted = delete_keys(client, bucket, keys)
        print(f"Klaar: {deleted} gewist")
        if prefix.rstrip("/") == R2_ENV_DEVELOPMENT:
            write_development_manifest([])
        return 0

    if args.write_manifest_from_r2:
        client, bucket, endpoint, account = r2_client()
        print(f"Bucket={bucket} Endpoint={endpoint}")
        keys = list_keys(client, bucket, f"{R2_ENV_DEVELOPMENT}/")
        rels = manifest_rels_from_keys(keys)
        write_development_manifest(rels)
        return 0

    if args.restamp_metadata:
        prefix = f"{R2_ENV_PRODUCTION}/"
        client, bucket, endpoint, account = r2_client()
        print(f"Bucket={bucket} Endpoint={endpoint}")
        print(f"Restamp sha256 onder {prefix}")
        keys = [k for k in list_keys(client, bucket, prefix) if k.endswith(".pdf")]
        print(f"{len(keys)} PDF-object(en)")
        done = 0
        skipped = 0
        for key in keys:
            if args.only_missing_sha:
                try:
                    head = client.head_object(Bucket=bucket, Key=key)
                    meta = head.get("Metadata") or {}
                    if (meta.get("sha256") or "").strip():
                        skipped += 1
                        continue
                except Exception:
                    pass
            if args.dry_run:
                print(f"DRY  restamp {key}")
                done += 1
                continue
            try:
                obj = client.get_object(Bucket=bucket, Key=key)
                body = obj["Body"].read()
                digest = hashlib.sha256(body).hexdigest()
                ctype = obj.get("ContentType") or "application/pdf"
                client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=body,
                    ContentType=ctype,
                    Metadata={"sha256": digest},
                )
            except Exception as exc:
                _die(f"Restamp mislukt voor {key}:\n{exc}")
            done += 1
            print(f"META {key} sha256={digest[:12]}…", flush=True)
            if done % 25 == 0:
                print(f"… {done}/{len(keys)} (skip={skipped})", flush=True)
        print(f"Klaar: restamped={done} skipped={skipped}")
        return 0

    env = (args.env or R2_ENV_PRODUCTION).strip().lower()
    if env == "preview":
        _die(
            "--env preview is vervangen door --env development "
            "(alleen de diff t.o.v. production/). Zie docs/plans/pdf-r2.md."
        )
    if env not in ALLOWED_ENVS:
        _die(
            f"--env {args.env!r} mag niet. Gebruik production of development."
        )

    roots = args.paths or [CONTENT]
    pdfs = _iter_pdfs(roots)
    if not pdfs:
        print("Geen blad-PDF's gevonden.")
        return 0

    print(f"{len(pdfs)} lokale PDF(s) → env={env}")
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
    skipped_same = 0
    unchanged_dev = 0
    removed_dev = 0

    if env == R2_ENV_PRODUCTION:
        for pdf in pdfs:
            key = object_key(pdf, env)
            digest = sha256_file(pdf)
            if args.dry_run:
                print(f"DRY  {key} sha256={digest[:12]}…")
                ok += 1
                continue
            assert client is not None and bucket is not None
            if r2_object_sha256(client, bucket, key) == digest:
                skipped_same += 1
                continue
            try:
                _upload_file(client, bucket, pdf, key, digest)
            except Exception as exc:
                _die(f"Upload mislukt voor {key}:\n{exc}")
            print(f"PUT  {key} sha256={digest[:12]}…", flush=True)
            ok += 1
            if ok % 25 == 0:
                print(f"… {ok}/{len(pdfs)}", flush=True)
        print(f"Klaar: put={ok} ongewijzigd={skipped_same}")
        return 0

    # development: alleen diff t.o.v. production/
    if args.dry_run and client is None:
        # Diff-vergelijking zonder credentials kan niet; toon voorgenomen keys.
        print(
            "DRY development zonder credentials: toont alle lokale PDF’s "
            "als kandidaat (geen SHA-vergelijking met production/)."
        )
        for pdf in pdfs:
            key = object_key(pdf, R2_ENV_DEVELOPMENT)
            digest = sha256_file(pdf)
            print(f"DRY? {key} sha256={digest[:12]}…")
            ok += 1
        print(f"Klaar: kandidaten={ok} (geen echte diff zonder R2)")
        return 0

    assert client is not None and bucket is not None
    for pdf in pdfs:
        rel = content_rel(pdf)
        digest = sha256_file(pdf)
        prod_key = f"{R2_ENV_PRODUCTION}/{rel}"
        dev_key = f"{R2_ENV_DEVELOPMENT}/{rel}"
        prod_sha = r2_object_sha256(client, bucket, prod_key)
        if prod_sha == digest:
            skipped_same += 1
            # Geen override meer: development-key weg als die er nog staat.
            try:
                client.head_object(Bucket=bucket, Key=dev_key)
            except Exception:
                continue
            if args.dry_run:
                print(f"DRY  delete {dev_key} (gelijk aan production)")
            else:
                client.delete_object(Bucket=bucket, Key=dev_key)
                print(f"DEL  {dev_key} (gelijk aan production)", flush=True)
            removed_dev += 1
            continue
        if args.dry_run:
            why = "missing-on-production" if prod_sha is None else "diff"
            print(f"DRY  {dev_key} ({why}) sha256={digest[:12]}…")
            ok += 1
            continue
        # Al zo op development/ (CI bouwt elke keer alles opnieuw): overslaan.
        if r2_object_sha256(client, bucket, dev_key) == digest:
            unchanged_dev += 1
            continue
        try:
            _upload_file(client, bucket, pdf, dev_key, digest)
        except Exception as exc:
            _die(f"Upload mislukt voor {dev_key}:\n{exc}")
        print(f"PUT  {dev_key} sha256={digest[:12]}…", flush=True)
        ok += 1
        if ok % 25 == 0:
            print(f"… put={ok} skip={skipped_same}", flush=True)

    if not args.dry_run:
        keys = list_keys(client, bucket, f"{R2_ENV_DEVELOPMENT}/")
        write_development_manifest(manifest_rels_from_keys(keys))
    print(
        f"Klaar: put={ok} ongewijzigd-op-development={unchanged_dev} "
        f"gelijk-aan-production={skipped_same} "
        f"dev-opgeruimd={removed_dev}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
