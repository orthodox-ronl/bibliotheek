"""Sidecar ``*.products-meta.json`` naast bibliotheek-producten.

Zelfde schema als VSA-tooling ``vsa.products_meta`` (schema 2: bron- +
product-hashes). **Versheid** voor ``products`` / ``check`` komt uit meta.
In-file herkomststempels zijn alleen nog fallback als meta ontbreekt
(``no_meta``), tot de catalogus een keer via ``products`` is vernieuwd.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable


def write_products_meta(
    bron: Path,
    products: dict[str, Path],
    *,
    merge: bool = False,
) -> Path | None:
    """Schrijf meta voor bestaande productbestanden; None als niets te schrijven.

    ``merge=False`` (default): vervang ``products`` door precies deze keys
    (zoals tooling ``… products``). ``merge=True``: alleen de meegegeven
    keys bijwerken; overige keys behouden (bijv. MXL-hash na bron-id).
    """
    existing = {k: p for k, p in products.items() if p.is_file()}
    if not existing:
        return None
    from vsa.products_meta import write_meta

    dest = write_meta(bron, existing, merge=merge)
    print(f"  Meta {dest.name}", flush=True)
    return dest


def meta_status(
    bron: Path,
    *,
    required_keys: set[str] | None = None,
) -> tuple[str, str]:
    """``ok`` | ``missing`` | ``stale`` | ``no_meta`` + toelichting."""
    from vsa.products_meta import freshness

    return freshness(bron, required_keys=required_keys)


def meta_ok(
    bron: Path,
    *,
    required_keys: set[str] | None = None,
) -> bool:
    status, _ = meta_status(bron, required_keys=required_keys)
    return status == "ok"


def stamp_ok_or_meta(
    bron: Path,
    *,
    required_keys: set[str],
    stamp_ok: bool,
) -> bool:
    """True als sidecar-meta klopt; bij ``no_meta`` nog stamp-fallback."""
    status, _ = meta_status(bron, required_keys=required_keys)
    if status == "ok":
        return True
    if status == "no_meta":
        return stamp_ok
    return False


def issues_from_meta_or(
    bron: Path,
    *,
    required_keys: set[str],
    rel: Callable[[Path], str],
    stamp_issues: Callable[[], list],
    issue_cls: type,
) -> list:
    """Meta-versheid; bij ``no_meta`` fallback naar stamp-controle."""
    from vsa.products_meta import meta_path_for

    status, detail = meta_status(bron, required_keys=required_keys)
    if status == "ok":
        return []
    if status == "no_meta":
        return stamp_issues()
    kind = "meta_missing" if status == "missing" else "meta_stale"
    return [
        issue_cls(
            kind,
            rel(meta_path_for(bron)),
            detail,
        )
    ]


def assign_svg_keys(products: dict[str, Path], svg_paths: list[Path]) -> None:
    """Zelfde conventie als tooling: één ``svg`` of ``svg-1``…"""
    if not svg_paths:
        return
    if len(svg_paths) == 1:
        products["svg"] = svg_paths[0]
        return
    for i, path in enumerate(svg_paths, start=1):
        products[f"svg-{i}"] = path


def meta_has_svg_product(bron: Path) -> bool:
    """True als meta een ``svg`` of ``svg-N``-product vermeldt."""
    from vsa.products_meta import load_meta

    meta = load_meta(bron)
    if not meta:
        return False
    products = meta.get("products")
    if not isinstance(products, dict):
        return False
    return "svg" in products or any(
        isinstance(k, str) and k.startswith("svg-") for k in products
    )
