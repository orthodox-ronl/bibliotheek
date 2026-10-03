"""Controleer relatieve Markdown-links in koormappen naar bestaande mappen.

Na ``bieb hernoem`` worden inhoudsopgave-links herschreven naar het nieuwe
zangstuk-id. Als de slotmap niet meeverhuist, wijst ``](trisagion/)`` naar
een map die niet bestaat → 404. Deze check vangt dat vóór Hugo.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KOORMAPPEN_ROOT = REPO_ROOT / "content-source" / "koormappen"

# [tekst](doel/) of [tekst](doel) — geen http(s), geen anker-only, geen mailto
_MD_LINK = re.compile(
    r"\[[^\]]*\]\((?!https?:|mailto:|#)([^)\s#]+)\)",
    re.IGNORECASE,
)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _target_exists(from_md: Path, href: str) -> bool:
    """Of ``href`` (relatief t.o.v. de markdown) een bestaande Hugo-pagina is."""
    href = href.strip()
    if not href or href.startswith(("/", "http:", "https:", "mailto:")):
        return True
    # Query/anker strippen
    href = href.split("?", 1)[0].split("#", 1)[0]
    if not href:
        return True
    target = (from_md.parent / href).resolve()
    if target.is_dir():
        if (target / "_index.md").is_file() or (target / "index.md").is_file():
            return True
        # Sectie zonder index mag als map met children (zeldzaam)
        return any(target.iterdir())
    if target.is_file():
        return True
    # Hugo: link naar pagina zonder extensie → .md of map/index
    if target.suffix == "":
        if target.with_suffix(".md").is_file():
            return True
        if (target.parent / f"{target.name}.md").is_file():
            return True
    return False


def find_broken_links(root: Path = KOORMAPPEN_ROOT) -> list[tuple[Path, str, int]]:
    """Lijst van (bestand, href, regelnummer) voor ontbrekende doelen."""
    broken: list[tuple[Path, str, int]] = []
    if not root.is_dir():
        return broken
    for md in sorted(root.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for match in _MD_LINK.finditer(line):
                href = match.group(1)
                if not _target_exists(md, href):
                    broken.append((md, href, i))
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Controleer relatieve links in koormappen."
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 bij gebroken links (standaard: waarschuwen, exit 0)",
    )
    args = parser.parse_args(argv)
    broken = find_broken_links()
    if not broken:
        print("OK: koormap-slotlinks")
        return 0
    print(f"FOUT: {len(broken)} gebroken relatieve link(s) in koormappen:", flush=True)
    for path, href, line in broken:
        print(f"  {_rel(path)}:{line}: ]({href}) — doelmap/-pagina ontbreekt", flush=True)
    print(
        "Oplossing: hernoem de slotmap zodat die overeenkomt met de link "
        "(bieb hernoem doet dat voor 1:1 zangstuk-ids), of herstel de linktekst.",
        flush=True,
    )
    return 1 if args.fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
