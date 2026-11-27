"""Gebreken-markering op catalogus (scherm / SVG / PDF).

Bron: frontmatter ``gebreken: true`` (+ optioneel ``gebreken_toelichting``)
op catalogus-leaf ``index.md``, of op variant-/zangstuk-``_index.md``.
Overerving naar leaves: dichtstbijzijnde expliciete ``gebreken`` wint
(leaf → variant → zangstuk); ``gebreken: false`` op een lager niveau
zet de markering uit. Toelichting: dichtstbijzijnde niet-lege wint.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from catalogus import CATALOGUS_ROOT, REPO_ROOT, id_from_path, leaf_folders

# ASCII-koppelteken: Helvetica in PDF kan geen em-dash (—) betrouwbaar.
STEMPEL_TEKST = "Gebreken - niet als definitief gebruiken"
SVG_MARKER_ID = "bibliotheek-gebreken-stempel"
SVG_MARKER_ATTR = 'data-bibliotheek-gebreken="1"'

_BIEB_ID_RE = re.compile(r"""\bbieb\s+id=["']([^"']+)["']""", re.IGNORECASE)
_SVG_MARKER_GROUP_RE = re.compile(
    rf'<g\b[^>]*\bid=["\']{re.escape(SVG_MARKER_ID)}["\'][^>]*>.*?</g>\s*',
    re.IGNORECASE | re.DOTALL,
)
_VIEWBOX_RE = re.compile(
    r'\bviewBox\s*=\s*["\']\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*["\']',
    re.IGNORECASE,
)


def _truthy(value: object) -> bool:
    if value is True:
        return True
    if isinstance(value, (int, float)) and value == 1:
        return True
    if isinstance(value, str) and value.strip().lower() in {
        "true",
        "yes",
        "1",
        "ja",
    }:
        return True
    return False


def _falsey(value: object) -> bool:
    if value is False:
        return True
    if isinstance(value, (int, float)) and value == 0:
        return True
    if isinstance(value, str) and value.strip().lower() in {
        "false",
        "no",
        "0",
        "nee",
    }:
        return True
    return False


def parse_frontmatter_params(text: str) -> dict:
    """Zelfde subset als ``index_md_pdf._hugo_page_params`` (geen PyYAML)."""
    if not text.lstrip().startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    block = parts[1]
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if line.startswith("-") or ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        if not key:
            continue
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root
        rest = rest.strip()
        if rest == "" or rest in {"|", ">"}:
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            value = rest
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            parent[key] = value
    out: dict = {}
    nested = root.get("params")
    if isinstance(nested, dict):
        out.update(nested)
    for key, value in root.items():
        if key == "params":
            continue
        out[key] = value
    return out


def gebreken_actief(params: dict) -> bool:
    """True alleen bij expliciet truthy ``gebreken`` (geen overerving)."""
    return _truthy(params.get("gebreken"))


def gebreken_expliciet(params: dict) -> bool | None:
    """Expliciete ``gebreken``-waarde, of ``None`` als het veld ontbreekt."""
    if "gebreken" not in params:
        return None
    value = params.get("gebreken")
    if _falsey(value):
        return False
    if _truthy(value):
        return True
    return None


def gebreken_toelichting(params: dict) -> str | None:
    raw = params.get("gebreken_toelichting")
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def publicatiestatus(params: dict) -> str:
    return str(params.get("publicatiestatus") or "").strip().lower()


def bieb_ids_in_markdown(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for match in _BIEB_ID_RE.finditer(text):
        raw = match.group(1).strip()
        # sectie-suffix @… negeren voor leaf-lookup
        leaf = raw.split("@", 1)[0].strip().strip("/")
        if not leaf or leaf in seen:
            continue
        seen.add(leaf)
        found.append(leaf)
    return found


def read_md_params(md_path: Path) -> dict:
    if not md_path.is_file():
        return {}
    return parse_frontmatter_params(md_path.read_text(encoding="utf-8"))


def read_leaf_params(leaf_id: str) -> dict | None:
    index = CATALOGUS_ROOT.joinpath(*leaf_id.split("/")) / "index.md"
    if not index.is_file():
        return None
    return read_md_params(index)


def _catalogus_dir_chain(folder: Path) -> list[Path]:
    """Mapketen leaf → … → zangstuk (alleen onder catalogus)."""
    try:
        rel = folder.resolve().relative_to(CATALOGUS_ROOT.resolve())
    except ValueError:
        return []
    parts = rel.parts
    if not parts:
        return []
    chain: list[Path] = []
    # Van diep naar ondiep: leaf (3), variant (2), zangstuk (1)
    for depth in range(len(parts), 0, -1):
        chain.append(CATALOGUS_ROOT.joinpath(*parts[:depth]))
    return chain


def _params_chain_for_folder(folder: Path) -> list[dict]:
    """Frontmatter-keten dichtstbij → verst (leaf/index of _index per niveau)."""
    out: list[dict] = []
    for directory in _catalogus_dir_chain(folder):
        index = directory / "index.md"
        section = directory / "_index.md"
        if index.is_file():
            out.append(read_md_params(index))
        elif section.is_file():
            out.append(read_md_params(section))
        else:
            out.append({})
    return out


def effective_gebreken_for_folder(folder: Path) -> tuple[bool, str | None]:
    """Effectieve gebreken voor een catalogusmap (leaf, variant of zangstuk).

    Dichtstbijzijnde expliciete ``gebreken`` wint; daarna dichtstbijzijnde
    toelichting als de markering aan staat.
    """
    chain = _params_chain_for_folder(folder)
    actief: bool | None = None
    for params in chain:
        explicit = gebreken_expliciet(params)
        if explicit is not None:
            actief = explicit
            break
    if not actief:
        return False, None
    for params in chain:
        tip = gebreken_toelichting(params)
        if tip:
            return True, tip
    return True, None


def effective_gebreken_for_leaf_id(leaf_id: str) -> tuple[bool, str | None]:
    folder = CATALOGUS_ROOT.joinpath(*leaf_id.split("/"))
    return effective_gebreken_for_folder(folder)


def resolve_gebreken_for_md(md_path: Path) -> tuple[bool, str | None]:
    """Of deze pagina (catalogus of koormap) gebreken toont.

    Catalogus: overerving via zangstuk/variant/leaf. Koormap: via ``bieb``.
    """
    md_path = md_path.resolve()
    try:
        rel = md_path.relative_to(CATALOGUS_ROOT.resolve())
    except ValueError:
        rel = None
    if rel is not None and md_path.name in {"index.md", "_index.md"}:
        return effective_gebreken_for_folder(md_path.parent)

    text = md_path.read_text(encoding="utf-8")
    for leaf_id in bieb_ids_in_markdown(text):
        actief, tip = effective_gebreken_for_leaf_id(leaf_id)
        if actief:
            return True, tip
    return False, None


def leaf_index_md(leaf_dir: Path) -> Path:
    return leaf_dir / "index.md"


def product_svgs_in_leaf(leaf_dir: Path) -> list[Path]:
    """Sibling-SVG’s die op scherm/download meegaan (geen legacy bladermap)."""
    out: list[Path] = []
    if not leaf_dir.is_dir():
        return out
    for path in sorted(leaf_dir.iterdir()):
        if not path.is_file():
            continue
        name = path.name.lower()
        if not name.endswith(".svg"):
            continue
        if (
            name.endswith(".vsa.svg")
            or name.endswith(".mvsa.svg")
            or name.endswith(".mscz.svg")
            or ".vsa.mvsa.svg" in name
            or ".translit" in name
        ):
            out.append(path)
    return out


def svg_has_gebreken_stempel(svg_path: Path) -> bool:
    if not svg_path.is_file():
        return False
    return SVG_MARKER_ID in svg_path.read_text(encoding="utf-8")


def _svg_stempel_markup(width: float, y0: float) -> str:
    bar_h = max(28.0, width * 0.035)
    font_size = max(14.0, min(22.0, width * 0.028))
    text_y = y0 + bar_h * 0.68
    label = STEMPEL_TEKST.replace("&", "&amp;")
    return (
        f'<g id="{SVG_MARKER_ID}" {SVG_MARKER_ATTR}>'
        f'<rect x="0" y="{y0:.2f}" width="{width:.2f}" height="{bar_h:.2f}" '
        f'fill="#fde8eb" stroke="#b00020" stroke-width="2"/>'
        f'<text x="{width / 2:.2f}" y="{text_y:.2f}" '
        f'text-anchor="middle" font-family="Source Sans 3, sans-serif" '
        f'font-size="{font_size:.2f}" font-weight="700" fill="#3b0008">'
        f"{label}</text>"
        f"</g>"
    )


def ensure_svg_gebreken_stempel(svg_path: Path, *, actief: bool) -> bool:
    """Zet of verwijder de gebreken-groep. True als het bestand wijzigde."""
    raw = svg_path.read_text(encoding="utf-8")
    has = bool(_SVG_MARKER_GROUP_RE.search(raw)) or (SVG_MARKER_ID in raw)
    if actief and has:
        return False
    if not actief:
        if not has:
            return False
        cleaned = _SVG_MARKER_GROUP_RE.sub("", raw)
        if cleaned == raw and SVG_MARKER_ID in raw:
            # Fallback: marker zonder nette group-match
            cleaned = re.sub(
                rf"<!--?\s*{re.escape(SVG_MARKER_ID)}.*?-->",
                "",
                raw,
                flags=re.DOTALL,
            )
        if cleaned == raw:
            return False
        svg_path.write_text(cleaned, encoding="utf-8", newline="\n")
        return True

    vb = _VIEWBOX_RE.search(raw)
    if vb:
        x0 = float(vb.group(1))
        y0 = float(vb.group(2))
        width = float(vb.group(3))
    else:
        x0, y0, width = 0.0, 0.0, 800.0
    markup = _svg_stempel_markup(width, y0)
    # Na openingstag <svg …>
    m = re.search(r"<svg\b[^>]*>", raw, flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"geen <svg>-root in {svg_path}")
    insert_at = m.end()
    new = raw[:insert_at] + "\n" + markup + "\n" + raw[insert_at:]
    # x0 unused but viewBox may have non-zero origin — shift bar
    if x0 != 0.0:
        new = new.replace(
            f'<rect x="0" y="{y0:.2f}"',
            f'<rect x="{x0:.2f}" y="{y0:.2f}"',
            1,
        )
        new = new.replace(
            f'text x="{width / 2:.2f}"',
            f'text x="{x0 + width / 2:.2f}"',
            1,
        )
    svg_path.write_text(new, encoding="utf-8", newline="\n")
    return True


def pdf_has_gebreken_stempel(pdf_path: Path) -> bool:
    if not pdf_path.is_file():
        return False
    try:
        import pymupdf
    except ImportError:
        # Zonder pymupdf: tekstzoek in raw bytes (ruwe fallback)
        data = pdf_path.read_bytes()
        return b"Gebreken" in data and b"niet als definitief" in data
    doc = pymupdf.open(pdf_path)
    try:
        for page in doc:
            text = page.get_text()
            if "Gebreken" in text and "niet als definitief" in text:
                return True
    finally:
        doc.close()
    return False


def apply_pdf_gebreken_watermark(
    pdf_path: Path, *, toelichting: str | None = None
) -> None:
    """Kopstrook + diagonale watermark op elke pagina; toelichting alleen p.1."""
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "pymupdf ontbreekt; installeer met: python -m pip install pymupdf"
        ) from exc

    doc = pymupdf.open(pdf_path)
    try:
        for i, page in enumerate(doc):
            rect = page.rect
            # Kopstrook
            bar = pymupdf.Rect(0, 0, rect.width, 22)
            page.draw_rect(bar, color=(0.69, 0.0, 0.125), fill=(0.99, 0.91, 0.92))
            page.insert_textbox(
                pymupdf.Rect(8, 3, rect.width - 8, 20),
                STEMPEL_TEKST,
                fontsize=10,
                fontname="helv",
                align=pymupdf.TEXT_ALIGN_CENTER,
                color=(0.23, 0.0, 0.03),
            )
            # Diagonale watermark (morph; insert_text rotate alleen 90°)
            pivot = pymupdf.Point(rect.width * 0.2, rect.height * 0.55)
            morph = (pivot, pymupdf.Matrix(1, 0, 0, 1, 0, 0).prerotate(35))
            shape = page.new_shape()
            shape.insert_text(
                pivot,
                STEMPEL_TEKST,
                fontsize=28,
                fontname="helv",
                color=(0.85, 0.55, 0.58),
                morph=morph,
            )
            shape.commit(overlay=True)
            if i == 0 and toelichting:
                tip = toelichting.strip()
                if tip:
                    page.insert_textbox(
                        pymupdf.Rect(24, 26, rect.width - 24, 52),
                        tip,
                        fontsize=8,
                        fontname="helv",
                        align=pymupdf.TEXT_ALIGN_CENTER,
                        color=(0.35, 0.1, 0.12),
                    )
        tmp = pdf_path.with_suffix(pdf_path.suffix + ".gebreken.tmp")
        doc.save(tmp, deflate=True)
    finally:
        doc.close()
    from cli_style import atomic_replace

    atomic_replace(tmp, pdf_path)


def _ververs_meta_hash(leaf_dir: Path, svg: Path) -> None:
    """Zet de sha256 van ``svg`` in de products-meta opnieuw.

    Een (ont)stempeling wijzigt de SVG nadat ``products`` de meta schreef;
    zonder verversen meldt check ``meta foute sha256`` en maakt fix ze
    elke run opnieuw (en stempelt weer).
    """
    import json

    from street_meta import write_products_meta

    for meta in sorted(leaf_dir.glob("*.products-meta.json")):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        producten = data.get("products")
        bron_naam = data.get("bron")
        if not isinstance(producten, dict) or not isinstance(bron_naam, str):
            continue
        for key, info in producten.items():
            if isinstance(info, dict) and info.get("file") == svg.name:
                bron = leaf_dir / bron_naam
                if bron.is_file():
                    write_products_meta(bron, {key: svg}, merge=True)
                break


def sync_leaf_svg_stempels(leaf_dir: Path) -> tuple[int, int]:
    """Pas SVG-stempels aan volgens effectieve gebreken. Returns (gewijzigd, bekeken)."""
    index = leaf_index_md(leaf_dir)
    if not index.is_file():
        return 0, 0
    actief, _tip = effective_gebreken_for_folder(leaf_dir)
    changed = 0
    svgs = product_svgs_in_leaf(leaf_dir)
    for svg in svgs:
        if ensure_svg_gebreken_stempel(svg, actief=actief):
            changed += 1
            _ververs_meta_hash(leaf_dir, svg)
    return changed, len(svgs)


def _leaf_dirs_under(root: Path) -> list[Path]:
    root = root.resolve()
    if root.is_file():
        # Sectie-_index: alle leaves eronder; anders leaf van dit bestand.
        if root.name.lower() == "_index.md":
            return _leaf_dirs_under(root.parent)
        cur = root.parent
        for _ in range(5):
            if (cur / "index.md").is_file() and id_from_path(cur):
                return [cur]
            if cur == cur.parent:
                break
            cur = cur.parent
        return []
    if not root.is_dir():
        return []
    out: list[Path] = []
    for _ident, folder in leaf_folders():
        folder_r = folder.resolve()
        try:
            folder_r.relative_to(root)
        except ValueError:
            if folder_r != root:
                continue
        out.append(folder)
    return out


def sync_gebreken_stempels_under(root: Path) -> tuple[int, int, int]:
    """SVG-stempels onder ``root`` (map of bestand in catalogus).

    Returns (leaves_touched, svgs_changed, svgs_seen).
    """
    leaves = _leaf_dirs_under(root)
    touched = 0
    changed_total = 0
    seen_total = 0
    for leaf in leaves:
        changed, seen = sync_leaf_svg_stempels(leaf)
        if seen:
            touched += 1
        changed_total += changed
        seen_total += seen
    return touched, changed_total, seen_total


def find_gebreken_issues() -> tuple[list[str], list[str]]:
    """Hard errors en warnings voor check."""
    errors: list[str] = []
    warnings: list[str] = []
    from input_paths import rel_for_log

    for _ident, folder in leaf_folders():
        index = leaf_index_md(folder)
        params = read_md_params(index)
        actief, _tip = effective_gebreken_for_folder(folder)
        if not actief:
            # Orphan stempel op SVG zonder effectieve markering
            for svg in product_svgs_in_leaf(folder):
                if svg_has_gebreken_stempel(svg):
                    warnings.append(
                        f"{rel_for_log(svg, repo_root=REPO_ROOT)}: "
                        "heeft gebreken-stempel maar effectieve gebreken is uit "
                        "(products opnieuw of stempel strippen)"
                    )
            continue
        if publicatiestatus(params) == "productie":
            errors.append(
                f"{rel_for_log(index, repo_root=REPO_ROOT)}: "
                "publicatiestatus productie mag niet samen met effectieve "
                "gebreken (zet status op reviewable/concept, of haal gebreken "
                "weg op leaf/variant/zangstuk, of zet gebreken: false op de leaf)"
            )
        svgs = product_svgs_in_leaf(folder)
        if svgs:
            for svg in svgs:
                if not svg_has_gebreken_stempel(svg):
                    warnings.append(
                        f"{rel_for_log(svg, repo_root=REPO_ROOT)}: "
                        "effectieve gebreken aan maar SVG mist stempel "
                        "(draai products voor deze leaf / zangstukmap)"
                    )
        pdf = index.with_name("index.md.pdf")
        if pdf.is_file() and not pdf_has_gebreken_stempel(pdf):
            warnings.append(
                f"{rel_for_log(pdf, repo_root=REPO_ROOT)}: "
                "effectieve gebreken aan maar PDF mist watermark "
                "(draai scripts\\pdf.cmd voor deze leaf)"
            )
        for sibling in folder.glob("index.md.translit-*.pdf"):
            if sibling.is_file() and not pdf_has_gebreken_stempel(sibling):
                warnings.append(
                    f"{rel_for_log(sibling, repo_root=REPO_ROOT)}: "
                    "effectieve gebreken aan maar translit-PDF mist watermark "
                    "(draai scripts\\pdf.cmd voor deze leaf)"
                )
    return errors, warnings


STATUS_PATH = REPO_ROOT / "data" / "gebreken-status.json"


@dataclass(frozen=True)
class GebrekenIssue:
    kind: str
    file: str
    detail: str


@dataclass(frozen=True)
class GebrekenStatus:
    """Zelfde vorm als de andere status-JSON's (voor check_fixlist/fix)."""

    dir: str
    source: str
    ok: bool
    fix_cmd: str
    issues: list[GebrekenIssue]


def collect_gebreken_statuses() -> tuple[list[GebrekenStatus], int]:
    """Afwerkbare gebreken-problemen per leaf + aantal gecontroleerde leaves.

    * SVG-stempel ontbreekt (of staat er onterecht op) → ``gebreken.py <leaf>``.
    * PDF/translit-PDF mist watermark → ``scripts\\pdf.cmd <leaf>\\index.md --force``.

    Harde fouten (productie + gebreken) horen hier niet: die vragen handwerk
    en blijven in ``find_gebreken_issues``.
    """
    from input_paths import rel_for_log

    statuses: list[GebrekenStatus] = []
    n_leaves = 0
    for _ident, folder in leaf_folders():
        n_leaves += 1
        rel = rel_for_log(folder, repo_root=REPO_ROOT)
        rel_win = rel.replace("/", "\\")
        index = leaf_index_md(folder)
        actief, _tip = effective_gebreken_for_folder(folder)
        svg_issues: list[GebrekenIssue] = []
        pdf_issues: list[GebrekenIssue] = []
        for svg in product_svgs_in_leaf(folder):
            has = svg_has_gebreken_stempel(svg)
            if actief and not has:
                svg_issues.append(
                    GebrekenIssue(
                        "stempel_ontbreekt",
                        rel_for_log(svg, repo_root=REPO_ROOT),
                        "effectieve gebreken aan maar SVG mist stempel",
                    )
                )
            elif not actief and has:
                svg_issues.append(
                    GebrekenIssue(
                        "stempel_te_veel",
                        rel_for_log(svg, repo_root=REPO_ROOT),
                        "effectieve gebreken uit maar SVG heeft stempel",
                    )
                )
        if actief:
            pdfs = [index.with_name("index.md.pdf")]
            pdfs += sorted(folder.glob("index.md.translit-*.pdf"))
            for pdf in pdfs:
                if pdf.is_file() and not pdf_has_gebreken_stempel(pdf):
                    pdf_issues.append(
                        GebrekenIssue(
                            "watermark_ontbreekt",
                            rel_for_log(pdf, repo_root=REPO_ROOT),
                            "effectieve gebreken aan maar PDF mist watermark",
                        )
                    )
        source = rel_for_log(index, repo_root=REPO_ROOT)
        if svg_issues:
            statuses.append(
                GebrekenStatus(
                    dir=rel,
                    source=source,
                    ok=False,
                    fix_cmd=rf"python scripts\gebreken.py {rel_win}",
                    issues=svg_issues,
                )
            )
        if pdf_issues:
            statuses.append(
                GebrekenStatus(
                    dir=f"{rel} (pdf)",
                    source=source,
                    ok=False,
                    fix_cmd=rf"scripts\pdf.cmd {rel_win}\index.md --force",
                    issues=pdf_issues,
                )
            )
    return statuses, n_leaves


def write_gebreken_status_json(
    statuses: list[GebrekenStatus], path: Path = STATUS_PATH
) -> None:
    from dataclasses import asdict

    from cli_style import atomic_write_json

    atomic_write_json(
        path,
        {
            "folders": {
                s.dir: {
                    "source": s.source,
                    "ok": s.ok,
                    "fix_cmd": s.fix_cmd,
                    "issues": [asdict(i) for i in s.issues],
                }
                for s in statuses
            }
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Zet of verwijder gebreken-stempels op catalogus-SVG’s volgens "
            "effectieve gebreken (leaf/variant/zangstuk, met overerving)."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=CATALOGUS_ROOT,
        help="Catalogusmap of bestand (default: content-source/catalogus)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Alleen tellen; niets schrijven",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Accepteren (fix voegt -y toe aan elk fix_cmd); geen effect.",
    )
    args = parser.parse_args(argv)
    if args.dry_run:
        # Tel wat zou wijzigen zonder te schrijven: scan only
        errors, warnings = find_gebreken_issues()
        print(f"gebreken check: {len(errors)} fout(en), {len(warnings)} waarschuwing(en)")
        for line in errors + warnings:
            print(f"  {line}")
        return 1 if errors else 0

    from input_paths import InputPathError, resolve_user_path

    try:
        root = resolve_user_path(args.root, repo_root=REPO_ROOT)
    except InputPathError as exc:
        print(exc, file=sys.stderr)
        return 1
    touched, changed, seen = sync_gebreken_stempels_under(root)
    print(
        f"gebreken-stempels: {touched} leaf(s), {changed} SVG gewijzigd, "
        f"{seen} SVG bekeken"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
