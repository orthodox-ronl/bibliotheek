"""Leesbare check-rapportage voor beheerders (korte labels, geen pad-herhaling)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Sequence

from cli_style import count, is_verbose, note, ok, section, work

# Interne kind → korte label in de log
KIND_LABELS: dict[str, str] = {
    "meta_stale": "meta",
    "meta_missing": "meta-missing",
    "stale_pdf": "stale-pdf",
    "missing_pdf": "missing-pdf",
    "stale_mxl": "stale-mxl",
    "missing_mxl": "missing-mxl",
    "stale_svg": "stale-svg",
    "missing_svg": "missing-svg",
    "stale_mp3": "stale-mp3",
    "missing_mp3": "missing-mp3",
    "stale_lyrics": "stale-lyrics",
    "missing_lyrics": "missing-lyrics",
    "parse_error": "parse",
}

# Korte hint zonder --verbose (leeg = soort-label volstaat)
KIND_HINT: dict[str, str] = {
    "meta_stale": "foute sha256",
    "meta_missing": "meta ontbreekt of incompleet",
}

# Soorten die eerder “echt fout” zijn dan “afwerken met products/pdf”
_HARD_KINDS = frozenset({"parse_error", "parse"})


def short_kind(kind: str) -> str:
    raw = (kind or "").strip()
    if not raw:
        return "probleem"
    if raw in KIND_LABELS:
        return KIND_LABELS[raw]
    return raw.replace("_", "-")


def short_hint(kind: str, detail: str = "", *, verbose: bool = False) -> str:
    if verbose:
        return (detail or "").strip()
    if kind in KIND_HINT:
        return KIND_HINT[kind]
    if kind.startswith("stale") or kind.startswith("missing"):
        return ""
    text = (detail or "").lower()
    if "sha256" in text or "wijkt af" in text:
        return "foute sha256"
    return ""


def template_fix_cmd(fix_cmd: str) -> str:
    """Laatste pad-argument → ``{file}``; ``scripts\\products.cmd`` → ``products``."""
    text = (fix_cmd or "").strip()
    if not text:
        return text
    parts = text.split()
    for i in range(len(parts) - 1, -1, -1):
        part = parts[i].strip('"')
        lower = part.lower()
        if (
            "\\" in part
            or "/" in part
            or lower.endswith(
                (
                    ".mvsa",
                    ".vsa",
                    ".mscz",
                    ".md",
                    ".mxl",
                    ".mp3",
                    ".svg",
                    ".json",
                )
            )
        ):
            parts[i] = "{file}"
            break
    out = " ".join(parts)
    out = out.replace(r"scripts\products.cmd", "products")
    out = out.replace("scripts/products.cmd", "products")
    return out


def status_dir_label(status: Any) -> str:
    for attr in ("dir", "product", "source", "file"):
        value = getattr(status, attr, None)
        if value:
            text = str(value).replace("\\", "/").strip()
            prefix = "content-source/"
            if text.startswith(prefix):
                text = text[len(prefix) :]
            return text
    return "?"


def _primary_kind(status: Any) -> str:
    issues = getattr(status, "issues", None) or []
    if issues:
        first = issues[0]
        kind = getattr(first, "kind", None)
        if kind:
            return str(kind)
        if isinstance(first, dict) and first.get("kind"):
            return str(first["kind"])
    return "probleem"


def _primary_detail(status: Any) -> str:
    issues = getattr(status, "issues", None) or []
    if not issues:
        return ""
    first = issues[0]
    detail = getattr(first, "detail", None)
    if detail is not None:
        return str(detail)
    if isinstance(first, dict):
        return str(first.get("detail") or "")
    return ""


def _is_hard_kind(kind: str) -> bool:
    return short_kind(kind) in _HARD_KINDS or kind in _HARD_KINDS


def print_check_findings(
    *,
    headline: str,
    what: str,
    bad: Sequence[Any],
    fix_page: str | None = None,
    verbose: bool | None = None,
    max_dirs: int = 40,
) -> None:
    """Headline + wat er getest wordt + paden per soort + één fix-sjabloon."""
    show = is_verbose() if verbose is None else bool(verbose)
    if bad:
        work(headline)
        section(what)
        count(len(bad), "niet-in-orde", role="work")
    else:
        ok(headline)
        return

    groups: dict[str, list[Any]] = defaultdict(list)
    for status in bad:
        groups[_primary_kind(status)].append(status)

    for kind, items in groups.items():
        label = short_kind(kind)
        hint = short_hint(kind, _primary_detail(items[0]), verbose=False)
        tag = f"{label}  {hint}" if hint else label
        role = "hard" if _is_hard_kind(kind) else "work"
        count(len(items), tag, role=role)
        shown = items[:max_dirs]
        for status in shown:
            print(f"  {status_dir_label(status)}", flush=True)
            if show:
                for issue in getattr(status, "issues", None) or []:
                    kind_i = getattr(issue, "kind", "") or ""
                    file_i = getattr(issue, "file", "") or ""
                    detail_i = getattr(issue, "detail", "") or ""
                    print(
                        f"    - [{kind_i}] {file_i}: {detail_i}",
                        flush=True,
                    )
                fix = getattr(status, "fix_cmd", "") or ""
                if fix:
                    note(f"    fix: {fix}")
        if len(items) > max_dirs:
            note(f"  … en {len(items) - max_dirs} meer")
        if not show:
            fix = getattr(items[0], "fix_cmd", "") or ""
            if fix:
                note(f"  fix: `{template_fix_cmd(fix)}`")

    if fix_page:
        page = str(fix_page).lstrip("/").replace("/", "\\")
        if not page.lower().startswith("handleiding"):
            page = str(fix_page).lstrip("/")
        note(f"Zie: {page}")


def print_path_problems(
    *,
    headline: str,
    what: str,
    bad_rows: Sequence[tuple[str, str, str]],
    fix_template: str,
    fix_page: str | None = None,
    max_dirs: int = 40,
) -> None:
    """Voor checks zonder Status-object (pad, soort, detail)."""
    if bad_rows:
        work(headline)
        section(what)
        count(len(bad_rows), "niet-in-orde", role="work")
    else:
        ok(headline)
        return
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for row in bad_rows:
        groups[row[1]].append(row)
    for kind, rows in groups.items():
        label = short_kind(kind)
        hint = short_hint(kind, rows[0][2], verbose=False)
        tag = f"{label}  {hint}" if hint else label
        role = "hard" if _is_hard_kind(kind) else "work"
        count(len(rows), tag, role=role)
        for path, _k, _d in rows[:max_dirs]:
            print(f"  {path}", flush=True)
        if len(rows) > max_dirs:
            note(f"  … en {len(rows) - max_dirs} meer")
        note(f"  fix: `{fix_template}`")
    if fix_page:
        note(f"Zie: {str(fix_page).lstrip('/')}")
