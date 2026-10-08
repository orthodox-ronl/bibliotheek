"""Neem een partituur op in de Oefenhoek-bibliotheek.

Maakt (indien nodig) zangstuk/variant-_index.md en leaf-index.md met bieb,
kopieert of verplaatst bestanden naar de publicatiestam, en weigert formats
die niet in de bibliotheek horen.

Niet in check. Geen volledige muzikale opkuis; wel poorten (id, formaat,
vsa validate). Zie scripts/h.cmd bieb-accepteer en de handleiding
publiceren/1-opnemen-in-catalogus.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogus import (  # noqa: E402
    CATALOGUS_ROOT,
    REPO_ROOT,
    folder,
    id_from_publication_stem,
    is_generic_leaf_title,
    parse_id,
    publication_stem_from_filename,
    stem,
    under_alias_variant,
    uitvoeringsvorm_link_title,
)
from score_filenames import is_print_mscz, is_tekstblad_md  # noqa: E402

ALLOWED_STATUS = frozenset({"voorzien", "concept", "reviewable", "productie"})
SCORE_SUFFIXES = frozenset({".mscz", ".vsa", ".mvsa"})
COMPANION_SUFFIXES = frozenset({".pdf", ".mxl"})

TEKSTBLAD_BUILD_FM = (
    "build:\n"
    "  render: never\n"
    "  list: never\n"
)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _write(path: Path, text: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"  would write {_rel(path)}", flush=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _fm_value(text: str, key: str) -> str | None:
    in_fm = False
    prefix = f"{key.lower()}:"
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def _words_title(slug: str) -> str:
    """``johannes-de-theoloog`` → ``Johannes De Theoloog`` (leesbare default)."""
    parts = []
    for w in slug.replace("-", " ").split():
        if not w:
            continue
        parts.append(w[:1].upper() + w[1:])
    return " ".join(parts)


def default_title(ident: str) -> str:
    """Volledige leaf-titel uit id: ``Kondak Johannes … (Liturgikon)``."""
    zangstuk, variant, uv = parse_id(ident)
    return (
        f"{_words_title(zangstuk)} {_words_title(variant)} "
        f"({uitvoeringsvorm_link_title(uv)})"
    )


def default_link_title(ident: str) -> str:
    _z, _v, uv = parse_id(ident)
    return uitvoeringsvorm_link_title(uv)


def title_hint_from_source(path: Path) -> str | None:
    """Optionele paginatitel uit VSA/mvsa-frontmatter (``titel:`` / ``soort:``)."""
    if path.suffix.lower() not in {".vsa", ".mvsa"}:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.lstrip().startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = parts[1]
    titel = None
    soort = None
    for line in fm.splitlines():
        stripped = line.strip()
        low = stripped.lower()
        if low.startswith("titel:"):
            titel = stripped.split(":", 1)[1].strip().strip("\"'")
        elif low.startswith("soort:") and soort is None:
            soort = stripped.split(":", 1)[1].strip().strip("\"'")
    if not titel:
        return None
    if soort:
        s = soort.replace("-", " ")
        s = s[:1].upper() + s[1:] if s else s
        if not titel.lower().startswith(s.lower()):
            return f"{s} — {titel}"
    return titel


def classify_source(path: Path) -> str:
    """Geef soort: partituur_mscz | print_mscz | vsa | mvsa | tekstblad | pdf | mxl | refuse:..."""
    if not path.is_file():
        return f"refuse:bestaat niet ({path})"
    name = path.name.lower()
    if is_print_mscz(path):
        return "print_mscz"
    if is_tekstblad_md(path):
        return "tekstblad"
    suffix = path.suffix.lower()
    if suffix == ".mscz":
        return "partituur_mscz"
    if suffix == ".vsa":
        return "vsa"
    if suffix == ".mvsa":
        return "mvsa"
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".mxl":
        # Ruwe Capella-MXL hoort via opkuisen; alleen siblings (producten) ok.
        return "mxl"
    if suffix == ".md":
        return (
            "refuse:gewone .md hoort niet als bibliotheek-bron; "
            "gebruik {stam}.tekstblad.md voor het tekstblad-spoor"
        )
    if suffix in {".musicxml", ".xml", ".cap", ".capx"}:
        return (
            "refuse:dit formaat hoort niet rechtstreeks in de bibliotheek "
            "(eerst opkuisen / normaliseren; zie handleiding partituur)"
        )
    return f"refuse:onbekende extensie {path.suffix!r}"


def target_name(
    kind: str,
    ident: str,
    *,
    with_vsa: bool,
    with_mscz: bool = False,
    with_tekstblad: bool = False,
) -> str:
    stam = stem(ident)
    if kind == "partituur_mscz":
        return f"{stam}.mscz"
    if kind == "print_mscz":
        # Legacy; nieuwe bladen: {stam}.mscz + artefacten_handmatig.
        return f"{stam}.print.mscz"
    if kind == "vsa":
        return f"{stam}.vsa"
    if kind == "mvsa":
        return f"{stam}.mvsa"
    if kind == "tekstblad":
        return f"{stam}.tekstblad.md"
    if kind == "pdf":
        if with_tekstblad:
            return f"{stam}.tekstblad.pdf"
        if with_mscz:
            return f"{stam}.mscz.pdf"
        return f"{stam}.pdf"
    if kind == "mxl":
        if with_vsa:
            return f"{stam}.vsa.mxl"
        if with_mscz:
            return f"{stam}.mscz.mxl"
        return f"{stam}.mxl"
    raise ValueError(kind)


def ensure_tekstblad_frontmatter(text: str, *, title: str) -> str:
    """Zorg voor ``build: render/list: never``; behoud bestaande frontmatter/body."""
    import re

    build_block = "build:\n  render: never\n  list: never\n"
    if not text.lstrip().startswith("---"):
        return f'---\ntitle: "{title}"\n{build_block}---\n\n{text.lstrip()}'
    parts = text.split("---", 2)
    if len(parts) < 3:
        return f'---\ntitle: "{title}"\n{build_block}---\n\n{text.lstrip()}'
    fm = parts[1]
    body = parts[2]
    if not re.search(r"(?m)^title\s*:", fm):
        fm = f'\ntitle: "{title}"' + fm
    if "render: never" not in fm:
        fm = fm.rstrip("\n") + "\n" + build_block
    return f"---{fm}---{body}"


def write_tekstblad_source(
    dest: Path,
    src: Path,
    *,
    title: str,
    move: bool,
    force: bool,
    dry_run: bool,
) -> None:
    raw = src.read_text(encoding="utf-8")
    text = ensure_tekstblad_frontmatter(raw, title=title)
    if dry_run:
        print(f"  would write {_rel(dest)} (tekstblad + frontmatter)", flush=True)
        return
    if dest.exists() and not force:
        print(f"FAIL: bestaat al: {_rel(dest)} (gebruik --force)", flush=True)
        raise SystemExit(1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8", newline="\n")
    print(f"  wrote {_rel(dest)}", flush=True)
    if move and src.resolve() != dest.resolve():
        src.unlink()
        print(f"  removed source {_rel(src)}", flush=True)


def section_index_text(title: str) -> str:
    return (
        f"---\ntitle: \"{title}\"\nlinkTitle: \"{title}\"\n"
        "nav_sort: weight\npublicatiestatus: concept\n"
        "automatische_inhoud: true\n---\n"
    )


def leaf_index_text(
    ident: str,
    title: str,
    status: str,
    *,
    artefacten_handmatig: bool,
    link_title: str | None = None,
) -> str:
    handmatig = "artefacten_handmatig: true\n" if artefacten_handmatig else ""
    link = link_title or default_link_title(ident)
    return (
        f"---\ntitle: \"{title}\"\nlinkTitle: \"{link}\"\n"
        f"publicatiestatus: {status}\n"
        f"{handmatig}"
        "automatische_inhoud: false\n---\n\n"
        f"# {title}\n\n"
        f"{{{{< bieb id=\"{ident}\" >}}}}\n"
    )


def ensure_sections(ident: str, *, dry_run: bool) -> None:
    zangstuk, variant, _uv = parse_id(ident)
    zdir = CATALOGUS_ROOT / zangstuk
    zindex = zdir / "_index.md"
    if not zindex.is_file():
        _write(zindex, section_index_text(zangstuk.replace("-", " ")), dry_run=dry_run)
        print(f"  section {_rel(zindex)}", flush=True)
    vdir = zdir / variant
    vindex = vdir / "_index.md"
    if not vindex.is_file():
        _write(vindex, section_index_text(variant.replace("-", " ")), dry_run=dry_run)
        print(f"  section {_rel(vindex)}", flush=True)


def validate_vsa(path: Path) -> list[str]:
    """Lege lijst = ok; anders foutregels."""
    try:
        proc = subprocess.run(
            ["vsa", "validate", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return [
            "vsa staat niet op PATH; installeer vsa-tool of draai scripts\\check.cmd "
            "eerst (bootstrap)"
        ]
    if proc.returncode == 0:
        return []
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    detail = out or err or f"exit {proc.returncode}"
    return [f"vsa validate faalde voor {path.name}: {detail}"]


def validate_mvsa(path: Path) -> list[str]:
    """Lege lijst = ok; anders foutregels."""
    try:
        proc = subprocess.run(
            ["mvsa", "validate", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return [
            "mvsa staat niet op PATH; installeer vsa-tool of draai scripts\\check.cmd "
            "eerst (bootstrap)"
        ]
    if proc.returncode == 0:
        return []
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    detail = out or err or f"exit {proc.returncode}"
    return [f"mvsa validate faalde voor {path.name}: {detail}"]


def place_file(
    src: Path,
    dest: Path,
    *,
    move: bool,
    force: bool,
    dry_run: bool,
) -> None:
    if dest.exists() and not force:
        raise SystemExit(
            f"doel bestaat al: {_rel(dest)}\n"
            "Oplossing: gebruik --force om te overschrijven, of kies een ander id."
        )
    if dry_run:
        action = "move" if move else "copy"
        print(f"  would {action} {_rel(src)} -> {_rel(dest)}", flush=True)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if move:
        if dest.exists():
            dest.unlink()
        shutil.move(str(src), str(dest))
    else:
        shutil.copy2(src, dest)
    print(f"  {'moved' if move else 'copied'} {_rel(dest)}", flush=True)


def accept(
    ident: str,
    sources: list[Path],
    *,
    title: str | None,
    status: str | None,
    stub: bool,
    move: bool,
    force: bool,
    dry_run: bool,
    skip_vsa_validate: bool,
    artefacten_handmatig: bool,
) -> int:
    try:
        parse_id(ident)
    except ValueError as exc:
        print(f"FAIL: ongeldig catalogus-id ({exc})", flush=True)
        print(
            "Oplossing: gebruik zangstuk/variant/uitvoeringsvorm "
            "(alleen a-z, 0-9, -, _). Zie Id-register.",
            flush=True,
        )
        return 1

    dest_dir = folder(ident)
    if under_alias_variant(dest_dir):
        print(
            f"FAIL: {ident} valt onder een alias-variant "
            "(daar horen geen partituren)",
            flush=True,
        )
        print(
            "Oplossing: plaats op de canonieke variant, of maak alleen "
            "alias_van op de variant-_index.",
            flush=True,
        )
        return 1

    if stub and sources:
        print("FAIL: --stub samen met bestanden mag niet", flush=True)
        return 1
    if not stub and not sources:
        print(
            "FAIL: geef minstens een bestand, of --stub voor een lege leaf",
            flush=True,
        )
        return 1

    classified: list[tuple[Path, str]] = []
    errors: list[str] = []
    for raw in sources:
        src = raw.expanduser().resolve()
        kind = classify_source(src)
        if kind.startswith("refuse:"):
            errors.append(f"{src.name}: {kind.removeprefix('refuse:')}")
            continue
        classified.append((src, kind))

    kinds = {k for _, k in classified}
    if "mxl" in kinds and "partituur_mscz" not in kinds and "vsa" not in kinds and "mvsa" not in kinds:
        errors.append(
            "alleen een .mxl: dat is meestal een Capella- of productbestand. "
            "Accepteer eerst een .mscz, .vsa of .mvsa, of leg de .mxl ernaast als "
            "sibling. Ruwe Capella: zie handleiding opkuisen."
        )

    has_score = (
        bool(kinds & {"partituur_mscz", "print_mscz", "vsa", "mvsa", "tekstblad"})
        or stub
    )
    if not has_score and classified:
        errors.append(
            "geen basispartituur-.mscz, .print.mscz, .vsa, .mvsa of .tekstblad.md: "
            "de bibliotheek-leaf heeft dan niets oefenbaars. "
            "Gebruik --stub voor een lege placeholder."
        )

    if not skip_vsa_validate:
        for src, kind in classified:
            if kind == "vsa":
                errors.extend(validate_vsa(src))
            elif kind == "mvsa":
                errors.extend(validate_mvsa(src))

    # Publicatiestam ↔ bestandsnaam (typo-vangnet).
    expect = stem(ident)
    for src, kind in classified:
        if kind not in {
            "partituur_mscz",
            "print_mscz",
            "vsa",
            "mvsa",
            "tekstblad",
        }:
            continue
        got = publication_stem_from_filename(src.name)
        if got != expect:
            msg = (
                f"{src.name}: bestandsstam {got!r} hoort "
                f"{expect!r} te zijn (id {ident})"
            )
            if force:
                print(f"WARN: {msg} (--force: toch door)", flush=True)
            else:
                errors.append(
                    msg
                    + ". Hernoem het bestand, corrigeer het id, of gebruik --force."
                )

    if errors:
        for line in errors:
            print(f"FAIL: {line}", flush=True)
        return 1

    resolved_title = title
    if not resolved_title:
        for src, kind in classified:
            if kind in {"vsa", "mvsa"}:
                hint = title_hint_from_source(src)
                if hint:
                    _z, _v, uv = parse_id(ident)
                    uv_label = uitvoeringsvorm_link_title(uv)
                    if uv_label.lower() not in hint.lower():
                        resolved_title = f"{hint} ({uv_label})"
                    else:
                        resolved_title = hint
                    break
    if not resolved_title:
        resolved_title = default_title(ident)
    resolved_link_title = default_link_title(ident)
    if is_generic_leaf_title(resolved_title, parse_id(ident)[0]):
        print(
            f"WARN: leaf-titel {resolved_title!r} is te generiek voor zoeken; "
            f"gebruik --title of verbeter de bron-frontmatter.",
            flush=True,
        )
    if status is None:
        resolved_status = "voorzien" if stub else "reviewable"
    else:
        resolved_status = status
    if resolved_status not in ALLOWED_STATUS:
        print(
            f"FAIL: onbekende publicatiestatus {resolved_status!r} "
            f"(verwacht: {', '.join(sorted(ALLOWED_STATUS))})",
            flush=True,
        )
        return 1
    if resolved_status == "productie" and not force:
        print(
            "FAIL: publicatiestatus productie niet automatisch zetten",
            flush=True,
        )
        print(
            "Oplossing: kies reviewable/concept/voorzien, of --force als "
            "een beheerder productie bewust wil.",
            flush=True,
        )
        return 1

    with_vsa = "vsa" in kinds
    with_mscz = "partituur_mscz" in kinds or "print_mscz" in kinds
    with_tekstblad = "tekstblad" in kinds
    handmatig = artefacten_handmatig or ("print_mscz" in kinds)

    print(f"Catalogus-id: {ident}", flush=True)
    print(f"Doelmap: {_rel(dest_dir)}", flush=True)
    if dry_run:
        print("(dry-run: niets geschreven)", flush=True)

    ensure_sections(ident, dry_run=dry_run)

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    for src, kind in classified:
        name = target_name(
            kind,
            ident,
            with_vsa=with_vsa,
            with_mscz=with_mscz,
            with_tekstblad=with_tekstblad,
        )
        if " " in name:
            print(f"FAIL: doelnaam mag geen spaties hebben: {name}", flush=True)
            return 1
        dest = dest_dir / name
        if kind == "tekstblad":
            try:
                write_tekstblad_source(
                    dest,
                    src,
                    title=resolved_title,
                    move=move,
                    force=force,
                    dry_run=dry_run,
                )
            except SystemExit as exc:
                return int(exc.code) if isinstance(exc.code, int) else 1
            continue
        place_file(
            src,
            dest,
            move=move,
            force=force,
            dry_run=dry_run,
        )

    index_path = dest_dir / "index.md"
    if index_path.is_file() and not force and not dry_run:
        existing = index_path.read_text(encoding="utf-8")
        bieb_ok = f'bieb id="{ident}"' in existing or f"bieb id='{ident}'" in existing
        if not bieb_ok:
            print(
                f"FAIL: bestaande {_rel(index_path)} heeft geen matching bieb id",
                flush=True,
            )
            print(
                "Oplossing: corrigeer de shortcode, of --force om index.md "
                "opnieuw te schrijven.",
                flush=True,
            )
            return 1
        print(f"  kept {_rel(index_path)}", flush=True)
    else:
        _write(
            index_path,
            leaf_index_text(
                ident,
                resolved_title,
                resolved_status,
                artefacten_handmatig=handmatig,
                link_title=resolved_link_title,
            ),
            dry_run=dry_run,
        )
        print(f"  index {_rel(index_path)} ({resolved_status})", flush=True)

    print("OK: opgenomen in de catalogus", flush=True)
    if dry_run:
        print("(dry-run: herhaal zonder --dry-run om echt te schrijven)", flush=True)
    if not stub and "partituur_mscz" in kinds:
        print(
            "Volgende (basispartituur): normaliseren/layouten indien nog niet gedaan, "
            "daarna scripts\\mscz-products.cmd",
            flush=True,
        )
    if "vsa" in kinds:
        print(
            "Volgende (VSA): scripts\\vsa-products.cmd of check "
            "(Coria-.vsa.mxl)",
            flush=True,
        )
    if "tekstblad" in kinds:
        print(
            "Volgende (tekstblad): scripts\\tekstblad-products.cmd "
            "({stam}.tekstblad.pdf), daarna commit bron + PDF",
            flush=True,
        )
    print(
        "Daarna: koormap-slot met bieb (handleiding publiceren) en "
        "scripts\\check.cmd --strict",
        flush=True,
    )
    return 0


HELP_IDENT = """\
Catalogus-id = drie delen met schuine streep, bijvoorbeeld:
  eniggeboren-zoon/default/hemelum
  zangstuk / variant / uitvoeringsvorm

Alleen kleine letters, cijfers, - en _. Geen spaties.
Lijst: content-source\\catalogus\\ID-REGISTER.md
  (op de site: Bibliotheek > Id-register)

Geef je bronbestand bij voorkeur al de publicatiestam-naam
  (zangstuk-variant-uitvoeringsvorm.ext); dan leidt accepteer het id af
  en controleert of de stam bij het id past.

Ken je het id niet? Verzin het niet - vraag na bij een beheerder.
Typ daarna het id opnieuw (of Enter om te stoppen).
"""

HELP_BESTAND = """\
Geef eerst het bronbestand (pad). Geef het bij voorkeur al de naam die het
in de catalogus moet krijgen, bijvoorbeeld:

  kondak-johannes-de-theoloog-toon-2-liturgikon.vsa

Daaruit leidt accepteer het catalogus-id af en controleert of de stam klopt.
Het bestand wordt meteen gevalideerd (.vsa / .mvsa), zodat je niet eerst
een id typt voor een ongeldige bron.

Toegestaan:
  - basispartituur-.mscz (MuseScore, genormaliseerd)
  - .vsa / .mvsa
  - bestandsnaam eindigend op .print.mscz (legacy; liever --artefacten-handmatig)
  - bestandsnaam eindigend op .tekstblad.md (liturgische tekst / dialoog)
  - optioneel daarna nog .pdf of .mxl in een volgende vraag

Niet toegestaan hier: ruwe Capella (.capx / alleen .mxl) - eerst opkuisen.
Gewone .md zonder .tekstblad. in de naam: hernoem naar {stam}.tekstblad.md.

Geen partituur, alleen een lege pagina reserveren? Typ: stub
Typ daarna het pad opnieuw (of Enter om te stoppen).
"""

_PUBLICATION_PATH_HINTS = (
    ".tekstblad.md",
    ".print.mscz",
    ".mscz",
    ".mvsa",
    ".vsa",
    ".pdf",
    ".mxl",
)


def _looks_like_catalogus_id(value: str) -> bool:
    try:
        parse_id(value)
    except ValueError:
        return False
    return True


def _looks_like_source_path(value: str) -> bool:
    """True als CLI-token eerder een bestandspad is dan een catalogus-id."""
    if not value or value in {"?", "stub"}:
        return False
    if _looks_like_catalogus_id(value):
        return False
    path = Path(value).expanduser()
    if path.is_file():
        return True
    name = path.name.lower()
    return any(name.endswith(suf) for suf in _PUBLICATION_PATH_HINTS)


def early_validate_sources(
    sources: list[Path],
    *,
    skip_vsa_validate: bool,
) -> list[str]:
    """Format + VSA-validate vóór id-invoer. Lege lijst = ok."""
    errors: list[str] = []
    classified: list[tuple[Path, str]] = []
    for raw in sources:
        src = raw.expanduser().resolve()
        kind = classify_source(src)
        if kind.startswith("refuse:"):
            errors.append(f"{src.name}: {kind.removeprefix('refuse:')}")
            continue
        classified.append((src, kind))
    kinds = {k for _, k in classified}
    if "mxl" in kinds and not (kinds & {"partituur_mscz", "vsa", "mvsa"}):
        errors.append(
            "alleen een .mxl: accepteer eerst .mscz / .vsa / .mvsa, "
            "of leg .mxl ernaast als sibling."
        )
    if not skip_vsa_validate:
        for src, kind in classified:
            if kind == "vsa":
                errors.extend(validate_vsa(src))
            elif kind == "mvsa":
                errors.extend(validate_mvsa(src))
    return errors


def primary_score_source(sources: list[Path]) -> Path | None:
    for raw in sources:
        src = raw.expanduser().resolve()
        kind = classify_source(src)
        if kind in {
            "partituur_mscz",
            "print_mscz",
            "vsa",
            "mvsa",
            "tekstblad",
        }:
            return src
    return None


def _print_help_block(text: str) -> None:
    print(flush=True)
    print(text.rstrip(), flush=True)
    print(flush=True)


def prompt_line(message: str) -> str:
    """Lees een regel van de gebruiker; EOF/leeg na strip = ''."""
    try:
        return input(message).strip()
    except EOFError:
        return ""


def prompt_until(
    message: str,
    help_text: str,
    *,
    allow_empty: bool = False,
) -> str | None:
    """Vraag tot er een waarde is. '?' toont help. Leeg + niet allow_empty = stop (None)."""
    while True:
        value = prompt_line(message)
        if value == "?":
            _print_help_block(help_text)
            continue
        if not value:
            if allow_empty:
                return ""
            print(
                "Niets ingevuld. Typ een waarde, of ? voor uitleg, "
                "of Enter opnieuw om te stoppen.",
                flush=True,
            )
            again = prompt_line(message)
            if again == "?":
                _print_help_block(help_text)
                continue
            if not again:
                return None
            return again
        return value


def resolve_ident(
    raw: str | None,
    *,
    suggested: str | None = None,
) -> str | None:
    """CLI-waarde, voorgesteld id uit bestandsstam, of interactieve vraag."""
    if raw is not None and raw.strip() and raw.strip() != "?":
        return raw.strip()
    if raw is not None and raw.strip() == "?":
        _print_help_block(HELP_IDENT)
    if suggested:
        try:
            parse_id(suggested)
        except ValueError:
            suggested = None
    if suggested:
        print(
            f"Afgeleid catalogus-id uit bestandsnaam: {suggested}",
            flush=True,
        )
        print(
            "Enter = bevestigen, of typ een ander id (? voor uitleg).",
            flush=True,
        )
        while True:
            value = prompt_until(
                f"Catalogus-id [{suggested}]: ",
                HELP_IDENT,
                allow_empty=True,
            )
            if value is None:
                return None
            if value == "":
                return suggested
            try:
                parse_id(value)
            except ValueError as exc:
                print(f"Dat id klopt niet ({exc}).", flush=True)
                continue
            return value
    print(
        "Catalogus-id ontbreekt. Typ het id, of ? voor uitleg.",
        flush=True,
    )
    while True:
        value = prompt_until(
            "Catalogus-id (zangstuk/variant/uitvoeringsvorm): ",
            HELP_IDENT,
        )
        if value is None:
            return None
        try:
            parse_id(value)
        except ValueError as exc:
            print(f"Dat id klopt niet ({exc}).", flush=True)
            print("Typ ? voor uitleg, of probeer opnieuw.", flush=True)
            continue
        return value


def _collect_extra_paths(first: Path) -> list[Path]:
    paths = [first]
    extra = prompt_until(
        "Nog een bestand (pad), of Enter om door te gaan: ",
        HELP_BESTAND,
        allow_empty=True,
    )
    while extra:
        if extra.lower() == "stub":
            print("stub kan niet samen met bestanden; genegeerd.", flush=True)
            break
        more = Path(extra).expanduser()
        if not more.is_file():
            print(f"Bestand niet gevonden: {more}", flush=True)
        else:
            paths.append(more)
        extra = prompt_until(
            "Nog een bestand (pad), of Enter om door te gaan: ",
            HELP_BESTAND,
            allow_empty=True,
        )
        if extra is None:
            break
    return paths


def resolve_bestanden_en_stub(
    bestanden: list[Path],
    *,
    stub: bool,
) -> tuple[list[Path], bool] | None:
    """Vul bestanden of stub aan (bestand eerst). None = gebruiker stopt."""
    if stub:
        return [], True
    cleaned: list[Path] = []
    for path in bestanden:
        name = str(path).strip()
        if not name or name == "?":
            continue
        cleaned.append(Path(name))
    if cleaned:
        return cleaned, False

    if any(str(p).strip() == "?" for p in bestanden):
        _print_help_block(HELP_BESTAND)
    print(
        "Bestand eerst. Typ het pad naar .mscz / .vsa / .mvsa / .tekstblad.md,",
        flush=True,
    )
    print(
        "of typ stub voor een lege leaf, of ? voor uitleg.",
        flush=True,
    )
    while True:
        value = prompt_until(
            "Bestand (pad) of stub: ",
            HELP_BESTAND,
        )
        if value is None:
            return None
        if value.lower() == "stub":
            return [], True
        path = Path(value).expanduser()
        if not path.is_file():
            print(f"Bestand niet gevonden: {path}", flush=True)
            print("Typ ? voor uitleg, of een ander pad.", flush=True)
            continue
        return _collect_extra_paths(path), False


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Neem .mscz / .vsa / .mvsa / .tekstblad.md (en optioneel PDF/MXL) op in "
            "content-source/catalogus onder een catalogus-id. "
            "Zonder argumenten: eerst bestand (validatie + id uit stam), daarna id. "
            "Typ ? voor uitleg."
        )
    )
    p.add_argument(
        "ident",
        nargs="?",
        default=None,
        help="catalogus-id óf bronbestand (bestand mag als eerste argument)",
    )
    p.add_argument(
        "bestanden",
        nargs="*",
        type=Path,
        help="bronbestanden (of catalogus-id als tweede als het eerste een bestand is)",
    )
    p.add_argument(
        "--title",
        help=(
            "paginatitel (default: uit VSA-titel of "
            "'Zangstuk variant (Uitvoeringsvorm)')"
        ),
    )
    p.add_argument(
        "--status",
        choices=sorted(ALLOWED_STATUS),
        help="publicatiestatus (default: reviewable, of voorzien bij --stub)",
    )
    p.add_argument(
        "--stub",
        action="store_true",
        help="alleen leaf + index.md, zonder partituurbestand",
    )
    p.add_argument(
        "--move",
        action="store_true",
        help="verplaats bronbestanden (default: kopieer)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="overschrijf bestaande doelen / herschrijf index.md",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="toon acties zonder te schrijven",
    )
    p.add_argument(
        "--skip-vsa-validate",
        action="store_true",
        help="sla vsa validate over (niet aanbevolen)",
    )
    p.add_argument(
        "--artefacten-handmatig",
        action="store_true",
        help="zet artefacten_handmatig: true (ook auto bij .print.mscz)",
    )
    return p


def _normalize_cli_positionals(
    ident_arg: str | None,
    bestanden: list[Path],
) -> tuple[str | None, list[Path]]:
    """Accepteer ``id bestand`` of ``bestand`` (of ``bestand id``)."""
    files = list(bestanden)
    ident = ident_arg.strip() if ident_arg and ident_arg.strip() else None
    if ident == "?":
        return "?", files
    if ident and _looks_like_source_path(ident):
        files = [Path(ident)] + files
        ident = None
        # Optioneel: tweede positioneel is id i.p.v. extra bestand
        if files and len(files) >= 2:
            second = str(files[1]).strip()
            if _looks_like_catalogus_id(second):
                ident = second
                files = [files[0]] + files[2:]
    elif ident and _looks_like_catalogus_id(ident):
        pass
    elif ident and not files:
        # Ambigu token: noch bestaand pad noch id → laat resolve later falen
        pass
    return ident, files


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ident_arg, file_args = _normalize_cli_positionals(
        args.ident, list(args.bestanden)
    )

    # 1) Bestand (of stub) eerst — dan vroege validatie.
    resolved = resolve_bestanden_en_stub(file_args, stub=args.stub)
    if resolved is None:
        print("Gestopt: geen bestand en geen stub.", flush=True)
        return 2
    bestanden, stub = resolved

    if bestanden and not stub:
        early = early_validate_sources(
            bestanden, skip_vsa_validate=args.skip_vsa_validate
        )
        if early:
            for line in early:
                print(f"FAIL: {line}", flush=True)
            print(
                "Bron eerst herstellen; daarna opnieuw accepteer "
                "(geen catalogus-id nodig tot de bron klopt).",
                flush=True,
            )
            return 1

    suggested: str | None = None
    primary = primary_score_source(bestanden) if bestanden else None
    if primary is not None:
        stam = publication_stem_from_filename(primary.name)
        suggested = id_from_publication_stem(stam)
        if suggested is None:
            print(
                f"Kon geen catalogus-id afleiden uit bestandsnaam {primary.name!r}.",
                flush=True,
            )
        elif ident_arg and _looks_like_catalogus_id(ident_arg):
            if stem(ident_arg) != stam:
                print(
                    f"FAIL: id {ident_arg} hoort bij stam {stem(ident_arg)!r}, "
                    f"maar bestand heet {stam!r}.",
                    flush=True,
                )
                print(
                    "Oplossing: hernoem het bestand, corrigeer het id, "
                    "of laat het id weg zodat accepteer het voorstelt.",
                    flush=True,
                )
                return 1

    # 2) Id (bevestigen voorgesteld, of typen bij stub / onbekende stam).
    ident = resolve_ident(
        ident_arg,
        suggested=None if stub else suggested,
    )
    if ident is None:
        print("Gestopt: geen catalogus-id.", flush=True)
        return 2

    return accept(
        ident,
        bestanden,
        title=args.title,
        status=args.status,
        stub=stub,
        move=args.move,
        force=args.force,
        dry_run=args.dry_run,
        skip_vsa_validate=args.skip_vsa_validate,
        artefacten_handmatig=args.artefacten_handmatig,
    )


if __name__ == "__main__":
    raise SystemExit(main())
