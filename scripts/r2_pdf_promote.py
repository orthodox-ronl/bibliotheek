"""Promoveer R2 development/-diff naar production/ en leeg development/.

Zie docs/plans/pdf-r2.md. Werkt metadata sha256 mee (kopie via get+put).
Schrijft data/pdf-r2-development.json leeg.
"""

from __future__ import annotations

import argparse
import hashlib
import sys

import r2_pdf_upload as r2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Kopieer R2 development/ → production/, wis development/, "
            "leeg het overrides-manifest."
        )
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Alleen tonen; niets kopiëren of wissen",
    )
    args = ap.parse_args(argv)

    client, bucket, endpoint, account = r2.r2_client()
    print(f"Bucket={bucket} Endpoint={endpoint}")
    print(f"Account ID (eerste 6)={account[:6]}…")

    prefix = f"{r2.R2_ENV_DEVELOPMENT}/"
    keys = [k for k in r2.list_keys(client, bucket, prefix) if k.endswith(".pdf")]
    print(f"{len(keys)} PDF(s) onder {prefix}")
    if not keys:
        if not args.dry_run:
            r2.write_development_manifest([])
        print("Niets te promoveren; manifest leeg.")
        return 0

    promoted = 0
    for key in keys:
        rel = key[len(prefix) :]
        dest = f"{r2.R2_ENV_PRODUCTION}/{rel}"
        if args.dry_run:
            print(f"DRY  {key} → {dest}")
            promoted += 1
            continue
        try:
            obj = client.get_object(Bucket=bucket, Key=key)
            body = obj["Body"].read()
            meta = obj.get("Metadata") or {}
            digest = (meta.get("sha256") or meta.get("Sha256") or "").strip()
            if not digest:
                digest = hashlib.sha256(body).hexdigest()
            ctype = obj.get("ContentType") or "application/pdf"
            client.put_object(
                Bucket=bucket,
                Key=dest,
                Body=body,
                ContentType=ctype,
                Metadata={"sha256": digest.lower()},
            )
        except Exception as exc:
            r2._die(f"Promote mislukt voor {key}:\n{exc}")
        print(f"PROM {key} → {dest}", flush=True)
        promoted += 1

    if args.dry_run:
        print(f"DRY  zou {len(keys)} development-object(en) wissen")
        print(f"Klaar (dry-run): promote={promoted}")
        return 0

    deleted = r2.delete_keys(client, bucket, keys)
    r2.write_development_manifest([])
    print(f"Klaar: promote={promoted} deleted-development={deleted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
