"""Herstelcommando's voor check/fix: altijd met bronpad.

Zonder pad zou ``products.cmd --kinds mvsa`` de héle catalogus
langs lopen (inclusief ``mxl validate``). Dat maakt ``fix --check``
onnodig traag bij een handvol wijzigingen.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def win_repo_rel(path: Path, *, repo_root: Path = REPO_ROOT) -> str:
    """Pad relatief aan de repo, met backslashes (voor cmd)."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path
    return rel.as_posix().replace("/", "\\")


def products_fix_cmd(
    kind: str,
    source: Path,
    *,
    repo_root: Path = REPO_ROOT,
    reasons: str = "missing,stale",
    skip_post: bool = True,
) -> str:
    """``products.cmd`` voor één bron; default zonder zoek/fingerprints."""
    parts = [
        r"scripts\products.cmd",
        "--kinds",
        kind,
    ]
    if reasons:
        parts.extend(["--reasons", reasons])
    if skip_post:
        parts.append("--skip-post")
    parts.append(win_repo_rel(source, repo_root=repo_root))
    return " ".join(parts)


def products_only_invalid_fix_cmd(
    source: Path,
    *,
    repo_root: Path = REPO_ROOT,
    skip_post: bool = True,
) -> str:
    """Alleen contract-ongeldige producten voor één bron herstellen."""
    name = source.name.lower()
    if name.endswith(".mvsa"):
        kind = "mvsa"
    elif name.endswith(".mscz"):
        kind = "mscz"
    elif name.endswith(".vsa"):
        kind = "vsa"
    else:
        kind = "mscz,mvsa,vsa"
    parts = [
        r"scripts\products.cmd",
        "--kinds",
        kind,
        "--only-invalid",
    ]
    if skip_post:
        parts.append("--skip-post")
    parts.append(win_repo_rel(source, repo_root=repo_root))
    return " ".join(parts)


def import_mvsa_fix_cmd(
    source: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> str:
    """``import-mvsa.cmd`` voor één basispartituur of import-``.mvsa``."""
    return rf"scripts\import-mvsa.cmd {win_repo_rel(source, repo_root=repo_root)}"


def coria_source_for_mxl(mxl: Path) -> Path | None:
    """Bron naast een Coria-``.mxl`` (``.mvsa`` / ``.mscz`` / ``.vsa``)."""
    name = mxl.name
    lower = name.lower()
    if lower.endswith(".mxl"):
        stem = name[: -len(".mxl")]
        candidate = mxl.with_name(stem)
        if candidate.suffix.lower() in {".mvsa", ".mscz", ".vsa"}:
            return candidate
    return None


def is_products_fix_cmd(fix_cmd: str) -> bool:
    text = (fix_cmd or "").replace("/", "\\").lower()
    return r"scripts\products.cmd" in text
