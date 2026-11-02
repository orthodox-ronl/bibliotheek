"""Kale kopie van de bibliotheek-repo naar een externe map (nieuwe repo-start).

Standaard: alleen kopiëren zonder gegenereerde catalogus-/koormap-producten.
Optioneel: site-identiteit herschrijven, git init, deps via _ensure.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from cli_style import add_verbose_argument, detail, info, set_verbose
from score_filenames import (
    is_chained_product_name,
    is_derived_mscz,
    is_tekstblad_md,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OLD_REPO_SLUG = "bibliotheek"
OLD_PAGES_ROOT = f"https://orthodox-ronl.github.io/{OLD_REPO_SLUG}"
DEFAULT_GITHUB_ORG = "orthodox-ronl"

EXCLUDE_DIR_NAMES = frozenset(
    {
        ".git",
        "generated",
        "public",
        "resources",
        ".venv",
        "vendor",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
    }
)

# Relatieve map-prefixen (posix) die altijd worden overgeslagen.
EXCLUDE_DIR_PREFIXES = (
    "static/mxl",
    "static/vsa/mxl",
    "static/coria",
    "static/vsa/bladermap",
    "content-source/input/_inbox",
)

EXCLUDE_ROOT_FILES = frozenset(
    {
        ".hugo_build.lock",
        ".ensure-stamp",
    }
)

EXCLUDE_DATA_FILES = frozenset(
    {
        "build.yaml",
        "coria-fp.json",
        "coria-public-base.json",
        "check-fixlist.json",
    }
)

_INDEX_MD_PDF = re.compile(r"(?i)^index\.md(?:\.translit-[a-z0-9_-]+)?\.pdf$")
_TEKSTBLAD_SCHERM = re.compile(r"(?i)\.tekstblad\.scherm\.html$")
_TEKSTBLAD_PDF = re.compile(r"(?i)\.tekstblad\.pdf$")
_TEKSTBLAD_BLOCK_SVG = re.compile(r"(?i)(?:tekstblad-)?block-\d+\.svg$")
_PRODUCTS_META = re.compile(r"(?i)\.products-meta\.json$")
_STATUS_JSON = re.compile(r"(?i)-status\.json$")
_HUGO_TITLE = re.compile(
    r'(?m)^(title\s*=\s*)(?P<q>["\'])(?P<val>.*?)(?P=q)\s*$'
)
_HUGO_LINKS_GITHUB = re.compile(
    r'(?m)^(  linksGithub\s*=\s*)(?P<q>["\'])(?P<val>.*?)(?P=q)\s*$'
)
_HUGO_FEEDBACK = re.compile(
    r'(?m)^(  feedback_email\s*=\s*)(?P<q>["\'])(?P<val>.*?)(?P=q)\s*$'
)
_PAGES_ROOT_ASSIGN = re.compile(
    r'(?m)^(PAGES_ROOT\s*=\s*)(?P<q>["\'])(?P<val>.*?)(?P=q)\s*$'
)
_RESERVED_SLUG_LINE = re.compile(
    r'(?m)^(?P<indent>\s*)"(?P<slug>[^"]+)",\s*$'
)

HELP_CONFIGURE = """
Site-identiteit voor de nieuwe map (Hugo + GitHub Pages).

Je vult de GitHub-reponaam (slug) en een sitenaam in. Org, Pages-URL,
GitHub-web-URL en feedback-e-mail krijgen defaults; Enter = default.

Typ ? bij een vraag voor deze uitleg.
""".strip()

HELP_REPO_NAME = """
Repo-naam (slug): alleen kleine letters, cijfers, streepjes.
Voorbeeld: parochie-demo → github.com/<org>/parochie-demo
en https://<org>.github.io/parochie-demo/
""".strip()

HELP_SITE_TITLE = """
Titel van de Hugo-site (hugo.toml title=…), zichtbaar in de browser-tab
en op de site. Voorbeeld: Parochie Demo.
""".strip()

HELP_REMOTE = """
Git remote-URL voor origin, of leeg laten voor geen remote.
Voorbeeld: https://github.com/orthodox-ronl/parochie-demo.git
""".strip()


def prompt_line(message: str) -> str:
    try:
        return input(message).strip()
    except EOFError:
        return ""


def _print_help_block(help_text: str) -> None:
    print(flush=True)
    print(help_text, flush=True)
    print(flush=True)


def prompt_until(
    message: str,
    help_text: str,
    *,
    allow_empty: bool = False,
) -> str | None:
    """Vraag tot er een waarde is. '?' toont help. Leeg + niet allow_empty = stop."""
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


def prompt_with_default(message: str, default: str, help_text: str) -> str | None:
    """Enter = default. '?' = help. Leeg na tweede Enter zonder default = None."""
    shown = f"{message} [{default}]: " if default else f"{message}: "
    while True:
        value = prompt_line(shown)
        if value == "?":
            _print_help_block(help_text)
            continue
        if not value:
            return default
        return value


def is_tty() -> bool:
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except Exception:  # noqa: BLE001
        return False


def posix_rel(path: Path) -> str:
    return path.as_posix()


def under_excluded_dir_prefix(rel_posix: str) -> bool:
    rel = rel_posix.strip("/")
    for prefix in EXCLUDE_DIR_PREFIXES:
        if rel == prefix or rel.startswith(prefix + "/"):
            return True
    return False


def is_tekstblad_product_name(name: str) -> bool:
    lower = name.lower()
    if _TEKSTBLAD_SCHERM.search(lower):
        return True
    if _TEKSTBLAD_PDF.search(lower):
        return True
    if lower.endswith(".svg") and _TEKSTBLAD_BLOCK_SVG.search(lower):
        return True
    return False


def is_notation_derived_product(name: str) -> bool:
    """True voor regenereerbare .vsa/.mvsa/.mscz-siblings (niet tekstblad, niet bron)."""
    if is_tekstblad_product_name(name):
        return False
    if is_tekstblad_md(name):
        return False
    lower = name.lower()
    if lower.endswith(".mscz.mvsa"):
        return False
    if is_chained_product_name(name):
        return True
    if is_derived_mscz(name):
        return True
    for marker in (".vsa.", ".mvsa.", ".mscz."):
        if marker in lower:
            return True
    return False


def should_copy_relative(rel: Path) -> bool:
    """Of een pad t.o.v. de bron-repo-root meegaat in de kale kopie."""
    parts = rel.parts
    if not parts:
        return False
    if any(p in EXCLUDE_DIR_NAMES for p in parts):
        return False
    rel_posix = posix_rel(rel)
    if under_excluded_dir_prefix(rel_posix):
        return False

    name = parts[-1]
    if len(parts) == 1 and name in EXCLUDE_ROOT_FILES:
        return False

    if parts[0] == "data" and len(parts) == 2:
        if name in EXCLUDE_DATA_FILES:
            return False
        if _STATUS_JSON.search(name):
            return False

    if _INDEX_MD_PDF.match(name):
        return False
    if _PRODUCTS_META.search(name):
        return False
    if is_notation_derived_product(name):
        return False
    return True


def read_feedback_email_default(hugo_toml: Path) -> str:
    text = hugo_toml.read_text(encoding="utf-8")
    m = _HUGO_FEEDBACK.search(text)
    if m:
        return m.group("val")
    return "orthodoxronl@duck.com"


def derive_pages_base_url(org: str, repo: str) -> str:
    return f"https://{org}.github.io/{repo}/"


def derive_github_web_url(org: str, repo: str) -> str:
    return f"https://github.com/{org}/{repo}"


def derive_remote_url(org: str, repo: str) -> str:
    return f"https://github.com/{org}/{repo}.git"


def pages_root_from_base_url(pages_base_url: str) -> str:
    return pages_base_url.rstrip("/")


def validate_repo_slug(slug: str) -> str | None:
    s = slug.strip().lower()
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?", s):
        return None
    return s


def identity_requested(args: argparse.Namespace) -> bool:
    if args.configure:
        return True
    return any(
        [
            args.repo_name,
            args.site_title,
            args.pages_base_url,
            args.github_web_url,
            args.feedback_email is not None and args.feedback_email != "",
            args.github_org is not None
            and args.github_org != DEFAULT_GITHUB_ORG
            and args.github_org != "",
        ]
    )


def resolve_identity(
    args: argparse.Namespace,
    *,
    source_root: Path,
    dry_run: bool,
) -> dict[str, str] | None:
    """Geeft identity-dict of None als geen herschrijven. Exit via SystemExit bij fout."""
    if not identity_requested(args):
        return None

    org = (args.github_org or DEFAULT_GITHUB_ORG).strip() or DEFAULT_GITHUB_ORG
    feedback_default = read_feedback_email_default(source_root / "hugo.toml")

    repo = (args.repo_name or "").strip()
    if not repo:
        if dry_run or not is_tty():
            raise SystemExit(
                "ERROR: --repo-name ontbreekt (of gebruik --configure op een TTY)."
            )
        print(HELP_CONFIGURE, flush=True)
        raw = prompt_until("Repo-naam (slug) (? voor uitleg): ", HELP_REPO_NAME)
        if raw is None:
            raise SystemExit("Afgebroken: geen repo-naam.")
        repo = raw
    validated = validate_repo_slug(repo)
    if not validated:
        raise SystemExit(
            f"ERROR: ongeldige repo-naam {repo!r} "
            "(gebruik [a-z0-9_-]+, begin/eindig niet met streepje)."
        )
    repo = validated

    title = (args.site_title or "").strip()
    if not title:
        if dry_run or not is_tty():
            raise SystemExit(
                "ERROR: --site-title ontbreekt (of gebruik --configure op een TTY)."
            )
        raw = prompt_until("Site-titel (? voor uitleg): ", HELP_SITE_TITLE)
        if raw is None:
            raise SystemExit("Afgebroken: geen site-titel.")
        title = raw

    if args.github_org is None and not dry_run and is_tty() and args.configure:
        org_in = prompt_with_default(
            "GitHub-org",
            org,
            "GitHub-organisatie of gebruikersnaam (default orthodox-ronl).",
        )
        if org_in is None:
            raise SystemExit("Afgebroken.")
        org = org_in.strip() or org

    pages = (args.pages_base_url or "").strip()
    github_web = (args.github_web_url or "").strip()
    if not pages:
        pages = derive_pages_base_url(org, repo)
        if args.configure and not dry_run and is_tty():
            pages = (
                prompt_with_default(
                    "Pages-base-URL",
                    pages,
                    "Productie-URL van GitHub Pages, eindigend op /.",
                )
                or pages
            )
    if not pages.endswith("/"):
        pages += "/"
    if not github_web:
        github_web = derive_github_web_url(org, repo)
        if args.configure and not dry_run and is_tty():
            github_web = (
                prompt_with_default(
                    "GitHub-web-URL",
                    github_web,
                    "URL van de GitHub-repo in de browser.",
                )
                or github_web
            )

    feedback = args.feedback_email
    if feedback is None:
        feedback = feedback_default
        if args.configure and not dry_run and is_tty():
            feedback = (
                prompt_with_default(
                    "Feedback-e-mail",
                    feedback_default,
                    "params.feedback_email in hugo.toml.",
                )
                or feedback_default
            )
    feedback = str(feedback).strip() or feedback_default

    return {
        "repo_name": repo,
        "github_org": org,
        "site_title": title,
        "pages_base_url": pages,
        "github_web_url": github_web,
        "feedback_email": feedback,
        "pages_root": pages_root_from_base_url(pages),
    }


def resolve_git_options(
    args: argparse.Namespace,
    identity: dict[str, str] | None,
    *,
    dry_run: bool,
) -> dict[str, object]:
    git_init = bool(args.git_init)
    initial_commit = bool(args.initial_commit)
    if initial_commit and not git_init:
        if dry_run or not is_tty():
            git_init = True
            info("--initial-commit: activeer ook git init.")
        else:
            ans = prompt_line(
                "--initial-commit zonder --git-init. Git init doen? [J/n]: "
            )
            if ans.lower() in ("", "j", "y", "ja", "yes"):
                git_init = True
            else:
                raise SystemExit("Afgebroken: --initial-commit vereist git init.")

    remote = (args.remote_url or "").strip()
    if args.remote_url is not None and not git_init:
        raise SystemExit("ERROR: --remote-url alleen samen met --git-init.")

    if git_init and not remote:
        if identity:
            remote = derive_remote_url(
                identity["github_org"], identity["repo_name"]
            )
            if args.configure and not dry_run and is_tty():
                remote = (
                    prompt_with_default(
                        "Git remote-URL (leeg = geen remote)",
                        remote,
                        HELP_REMOTE,
                    )
                    or ""
                )
        elif not dry_run and is_tty():
            raw = prompt_until(
                "Git remote-URL (Enter = geen remote, ? voor uitleg): ",
                HELP_REMOTE,
                allow_empty=True,
            )
            if raw is None:
                remote = ""
            else:
                remote = raw
        # dry-run / non-tty zonder identity: geen remote

    return {
        "git_init": git_init,
        "remote_url": remote,
        "initial_commit": initial_commit and git_init,
    }


def iter_source_files(source_root: Path) -> list[Path]:
    """Alle bestanden onder source_root die gekopieerd moeten worden."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(source_root):
        root = Path(dirpath)
        rel_dir = root.relative_to(source_root)
        # Prune
        keep_dirs: list[str] = []
        for d in sorted(dirnames):
            if d in EXCLUDE_DIR_NAMES:
                continue
            child_rel = rel_dir / d if rel_dir.parts else Path(d)
            if under_excluded_dir_prefix(posix_rel(child_rel)):
                continue
            keep_dirs.append(d)
        dirnames[:] = keep_dirs

        for name in filenames:
            rel = rel_dir / name if rel_dir.parts else Path(name)
            if should_copy_relative(rel):
                out.append(rel)
    return out


def copy_tree(
    source_root: Path,
    dest_root: Path,
    *,
    dry_run: bool,
) -> tuple[int, int]:
    files = iter_source_files(source_root)
    copied = 0
    for rel in files:
        src = source_root / rel
        dst = dest_root / rel
        detail(f"  copy {posix_rel(rel)}")
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied += 1
    return copied, len(files)


def _toml_basic_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def rewrite_hugo_toml(path: Path, identity: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    text, n1 = _HUGO_TITLE.subn(
        rf"\g<1>{_toml_basic_string(identity['site_title'])}", text, count=1
    )
    text, n2 = _HUGO_LINKS_GITHUB.subn(
        rf"\g<1>{_toml_basic_string(identity['github_web_url'])}",
        text,
        count=1,
    )
    text, n3 = _HUGO_FEEDBACK.subn(
        rf"\g<1>{_toml_basic_string(identity['feedback_email'])}",
        text,
        count=1,
    )
    if n1 + n2 + n3 == 0:
        raise SystemExit(f"ERROR: kon hugo.toml niet herschrijven: {path}")
    path.write_text(text, encoding="utf-8")


def rewrite_pages_yml(path: Path, identity: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    old = OLD_PAGES_ROOT
    new = identity["pages_root"]
    if old not in text:
        raise SystemExit(
            f"ERROR: verwachtte {old!r} in {path}, niets vervangen."
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def rewrite_fingerprint(path: Path, identity: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    new_root = identity["pages_root"]
    text, n = _PAGES_ROOT_ASSIGN.subn(
        rf'\g<1>"{new_root}"', text, count=1
    )
    if n != 1:
        raise SystemExit(f"ERROR: PAGES_ROOT niet gevonden in {path}")

    new_slug = identity["repo_name"]
    if new_slug != OLD_REPO_SLUG:

        def _swap_slug(m: re.Match[str]) -> str:
            slug = m.group("slug")
            if slug == OLD_REPO_SLUG:
                return f'{m.group("indent")}"{new_slug}",'
            return m.group(0)

        text = _RESERVED_SLUG_LINE.sub(_swap_slug, text)
    path.write_text(text, encoding="utf-8")


def apply_identity_rewrites(dest_root: Path, identity: dict[str, str]) -> None:
    rewrite_hugo_toml(dest_root / "hugo.toml", identity)
    rewrite_pages_yml(
        dest_root / ".github" / "workflows" / "pages.yml", identity
    )
    rewrite_fingerprint(
        dest_root / "scripts" / "fingerprint_coria_mxl.py", identity
    )


def run_git(
    dest_root: Path,
    *,
    remote_url: str,
    initial_commit: bool,
    dry_run: bool,
) -> None:
    if dry_run:
        info(f"[dry-run] git init in {dest_root}")
        if remote_url:
            info(f"[dry-run] git remote add origin {remote_url}")
        if initial_commit:
            info("[dry-run] git add -A && git commit")
        return

    def git(*git_args: str) -> None:
        proc = subprocess.run(
            ["git", *git_args],
            cwd=dest_root,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()
            raise SystemExit(f"ERROR: git {' '.join(git_args)} mislukt: {err}")

    git("init")
    if remote_url:
        git("remote", "add", "origin", remote_url)
    if initial_commit:
        git("add", "-A")
        proc = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "chore: seed from bibliotheek",
            ],
            cwd=dest_root,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()
            raise SystemExit(
                "ERROR: git commit mislukt "
                f"(zet user.name/user.email): {err}"
            )


def run_ensure(dest_root: Path, *, dry_run: bool) -> None:
    ensure_py = dest_root / "scripts" / "_ensure.py"
    if dry_run:
        info(f"[dry-run] python {ensure_py} --hugo --vsa-tool")
        return
    if not ensure_py.is_file():
        raise SystemExit(f"ERROR: ontbreekt {ensure_py}")
    proc = subprocess.run(
        [sys.executable, str(ensure_py), "--hugo", "--vsa-tool"],
        cwd=dest_root,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"ERROR: _ensure in doelmap mislukt (exit {proc.returncode})."
        )


def dest_is_inside_source(source: Path, dest: Path) -> bool:
    try:
        dest.resolve().relative_to(source.resolve())
        return True
    except ValueError:
        return False


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Kopieer de bibliotheek-repo kaal naar een externe map "
            "(zonder regenereerbare catalogus-/koormap-producten)."
        )
    )
    p.add_argument(
        "dest",
        type=Path,
        help="Doelmap buiten deze repo (wordt aangemaakt indien nodig).",
    )
    p.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Bron-repo (default: deze bibliotheek-root).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Alleen tonen wat er zou gebeuren; niets schrijven.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Sta toe dat de doelmap al bestanden bevat.",
    )
    add_verbose_argument(p)

    p.add_argument(
        "--configure",
        action="store_true",
        help="Herschrijf site-identiteit; vraag ontbrekende velden interactief.",
    )
    p.add_argument("--repo-name", default=None, help="GitHub-repo-slug.")
    p.add_argument(
        "--github-org",
        default=None,
        help=f"GitHub-org (default {DEFAULT_GITHUB_ORG}).",
    )
    p.add_argument("--site-title", default=None, help="Hugo title.")
    p.add_argument(
        "--pages-base-url",
        default=None,
        help="GitHub Pages-basis-URL (eindigend op /).",
    )
    p.add_argument(
        "--github-web-url",
        default=None,
        help="https://github.com/<org>/<repo>",
    )
    p.add_argument(
        "--feedback-email",
        default=None,
        help="params.feedback_email (default: huidige waarde uit bron-hugo.toml).",
    )

    p.add_argument(
        "--git-init",
        action="store_true",
        help="git init in de doelmap na kopiëren.",
    )
    p.add_argument(
        "--remote-url",
        default=None,
        help="git remote add origin URL (vereist --git-init).",
    )
    p.add_argument(
        "--initial-commit",
        action="store_true",
        help="Eerste commit na git init (geen push).",
    )
    p.add_argument(
        "--ensure",
        action="store_true",
        help="In de doelmap: python scripts/_ensure.py --hugo --vsa-tool",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    set_verbose(bool(args.verbose))

    source_root = (args.source or REPO_ROOT).resolve()
    dest_root = args.dest.expanduser().resolve()

    if not source_root.is_dir():
        info(f"ERROR: bron bestaat niet: {source_root}")
        return 2
    if not (source_root / "hugo.toml").is_file():
        info(f"ERROR: geen hugo.toml in bron: {source_root}")
        return 2
    if dest_root == source_root:
        info("ERROR: doelmap mag niet gelijk zijn aan de bron.")
        return 2
    if dest_is_inside_source(source_root, dest_root):
        info("ERROR: doelmap mag niet binnen de bron-repo liggen.")
        return 2

    if dest_root.exists():
        if any(dest_root.iterdir()) and not args.force:
            info(
                f"ERROR: doelmap is niet leeg: {dest_root}\n"
                "Gebruik --force om toch te schrijven."
            )
            return 2
    elif not args.dry_run:
        dest_root.mkdir(parents=True, exist_ok=True)

    def _exit_msg(exc: SystemExit) -> int:
        code = exc.code
        if code in (None, 0):
            return 0
        if isinstance(code, int):
            if exc.args:
                info(str(exc.args[0]))
            return code
        info(str(code))
        return 2

    try:
        identity = resolve_identity(
            args, source_root=source_root, dry_run=args.dry_run
        )
        git_opts = resolve_git_options(
            args, identity, dry_run=args.dry_run
        )
    except SystemExit as exc:
        return _exit_msg(exc)

    info(f"Bron:  {source_root}")
    info(f"Doel:  {dest_root}")
    if args.dry_run:
        info("Modus: dry-run (geen schrijfacties)")

    copied, _total = copy_tree(source_root, dest_root, dry_run=args.dry_run)
    info(f"{'Zou kopiëren' if args.dry_run else 'Gekopieerd'}: {copied} bestanden")

    if identity:
        info(
            "Identiteit: "
            f"{identity['site_title']} / {identity['github_web_url']} / "
            f"{identity['pages_base_url']}"
        )
        if args.dry_run:
            info(
                "[dry-run] herschrijf hugo.toml, pages.yml, "
                "fingerprint_coria_mxl.py"
            )
        else:
            try:
                apply_identity_rewrites(dest_root, identity)
            except SystemExit as exc:
                return _exit_msg(exc)
            info("Site-identiteit herschreven.")

    if git_opts["git_init"]:
        try:
            run_git(
                dest_root,
                remote_url=str(git_opts["remote_url"] or ""),
                initial_commit=bool(git_opts["initial_commit"]),
                dry_run=args.dry_run,
            )
        except SystemExit as exc:
            return _exit_msg(exc)
        info(
            "Git: init"
            + (
                f" + origin {git_opts['remote_url']}"
                if git_opts["remote_url"]
                else ""
            )
            + (" + initial commit" if git_opts["initial_commit"] else "")
        )

    if args.ensure:
        try:
            run_ensure(dest_root, dry_run=args.dry_run)
        except SystemExit as exc:
            return _exit_msg(exc)
        info(
            "Ensure in doelmap afgerond."
            if not args.dry_run
            else "Ensure (dry-run)."
        )

    info("")
    info("Volgende stappen:")
    info(f"  cd /d {dest_root}")
    if not args.ensure:
        info("  scripts\\_ensure.cmd --hugo --vsa-tool")
    info("  serve")
    info("  products")
    info("  pdf --all-koormappen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
