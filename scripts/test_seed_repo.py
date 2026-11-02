"""Tests voor seed-repo (filter, defaults, rewrite)."""

from __future__ import annotations

from pathlib import Path

import seed_repo as sr


def test_should_copy_keeps_sources_and_tekstblad_products() -> None:
    keep = [
        Path("content-source/catalogus/x/y/z/index.md"),
        Path("content-source/catalogus/x/y/z/foo.vsa"),
        Path("content-source/catalogus/x/y/z/foo.mvsa"),
        Path("content-source/catalogus/x/y/z/foo.mscz"),
        Path("content-source/catalogus/x/y/z/foo.mscz.mvsa"),
        Path("content-source/catalogus/x/y/z/foo.tekstblad.md"),
        Path("content-source/catalogus/x/y/z/foo.tekstblad.scherm.html"),
        Path("content-source/catalogus/x/y/z/foo.tekstblad.pdf"),
        Path(
            "content-source/catalogus/x/y/z/"
            "foo-tekstblad-block-1.svg"
        ),
        Path("content-source/koormappen/a/b/index.md"),
        Path("content-source/handleiding/scripts/check.md"),
        Path("content-source/_index.md"),
        Path("content-source/input/_werk/case/a.mscz"),
        Path("docs/publicatiecontrole.md"),
        Path("scripts/seed_repo.py"),
        Path("layouts/index.html"),
        Path("static/js/catalogus-zoek.js"),
        Path("hugo.toml"),
        Path("data/bronnen.yaml"),
    ]
    for rel in keep:
        assert sr.should_copy_relative(rel), rel


def test_should_copy_excludes_generated_products() -> None:
    drop = [
        Path("content-source/catalogus/x/y/z/foo.vsa.svg"),
        Path("content-source/catalogus/x/y/z/foo.vsa.mxl"),
        Path("content-source/catalogus/x/y/z/foo.vsa.mp3"),
        Path("content-source/catalogus/x/y/z/foo.vsa.lyrics.txt"),
        Path("content-source/catalogus/x/y/z/foo.mvsa.svg"),
        Path("content-source/catalogus/x/y/z/foo.mvsa.score-ir.json"),
        Path("content-source/catalogus/x/y/z/foo.mvsa.from-ir.musicxml"),
        Path("content-source/catalogus/x/y/z/foo.mscz.svg"),
        Path("content-source/catalogus/x/y/z/foo.vsa.mscz"),
        Path("content-source/catalogus/x/y/z/foo.mvsa.mscz"),
        Path("content-source/catalogus/x/y/z/foo.mvsa.mscz.mp3"),
        Path("content-source/catalogus/x/y/z/foo.products-meta.json"),
        Path("content-source/koormappen/a/b/index.md.pdf"),
        Path("content-source/koormappen/a/b/index.md.translit-nls.pdf"),
        Path("content-source/catalogus/x/y/z/index.md.pdf"),
        Path("content-source/input/_inbox/dump.mscz"),
        Path("generated/site/index.html"),
        Path(".git/config"),
        Path("static/mxl/foo.mxl"),
        Path("static/vsa/bladermap/x.svg"),
        Path("data/build.yaml"),
        Path("data/coria-fp.json"),
        Path("data/check-status.json"),
        Path("data/check-fixlist.json"),
        Path(".venv/pyvenv.cfg"),
    ]
    for rel in drop:
        assert not sr.should_copy_relative(rel), rel


def test_feedback_email_default_from_hugo(tmp_path: Path) -> None:
    hugo = tmp_path / "hugo.toml"
    hugo.write_text(
        'title = "X"\n\n[params]\n  feedback_email = "orthodoxronl@duck.com"\n',
        encoding="utf-8",
    )
    assert sr.read_feedback_email_default(hugo) == "orthodoxronl@duck.com"


def test_derive_urls() -> None:
    assert (
        sr.derive_pages_base_url("orthodox-ronl", "parochie-demo")
        == "https://orthodox-ronl.github.io/parochie-demo/"
    )
    assert (
        sr.derive_github_web_url("orthodox-ronl", "parochie-demo")
        == "https://github.com/orthodox-ronl/parochie-demo"
    )
    assert (
        sr.pages_root_from_base_url(
            "https://orthodox-ronl.github.io/parochie-demo/"
        )
        == "https://orthodox-ronl.github.io/parochie-demo"
    )


def test_rewrite_hugo_and_pages(tmp_path: Path) -> None:
    hugo = tmp_path / "hugo.toml"
    hugo.write_text(
        'baseURL = "/"\n'
        'title = "Bibliotheek"\n'
        "\n[params]\n"
        '  linksGithub = "https://github.com/orthodox-ronl/bibliotheek"\n'
        '  feedback_email = "orthodoxronl@duck.com"\n',
        encoding="utf-8",
    )
    pages = tmp_path / "pages.yml"
    pages.write_text(
        "# URL prod:        https://orthodox-ronl.github.io/bibliotheek/\n"
        'echo "base_url=https://orthodox-ronl.github.io/bibliotheek/"\n'
        'echo "base_url=https://orthodox-ronl.github.io/bibliotheek/preview/"\n',
        encoding="utf-8",
    )
    fp = tmp_path / "fingerprint_coria_mxl.py"
    fp.write_text(
        'PAGES_ROOT = "https://orthodox-ronl.github.io/bibliotheek"\n'
        "RESERVED_SLUGS = frozenset(\n"
        "    {\n"
        '        "preview",\n'
        '        "bibliotheek",\n'
        '        "catalogus",\n'
        "    }\n"
        ")\n",
        encoding="utf-8",
    )

    identity = {
        "repo_name": "parochie-demo",
        "github_org": "orthodox-ronl",
        "site_title": 'Parochie "Demo"',
        "pages_base_url": "https://orthodox-ronl.github.io/parochie-demo/",
        "github_web_url": "https://github.com/orthodox-ronl/parochie-demo",
        "feedback_email": "orthodoxronl@duck.com",
        "pages_root": "https://orthodox-ronl.github.io/parochie-demo",
    }
    sr.rewrite_hugo_toml(hugo, identity)
    sr.rewrite_pages_yml(pages, identity)
    sr.rewrite_fingerprint(fp, identity)

    hugo_text = hugo.read_text(encoding="utf-8")
    assert 'title = "Parochie \\"Demo\\""' in hugo_text
    assert "parochie-demo" in hugo_text
    assert "orthodoxronl@duck.com" in hugo_text

    pages_text = pages.read_text(encoding="utf-8")
    assert "bibliotheek" not in pages_text
    assert "parochie-demo" in pages_text

    fp_text = fp.read_text(encoding="utf-8")
    assert (
        'PAGES_ROOT = "https://orthodox-ronl.github.io/parochie-demo"'
        in fp_text
    )
    assert '"parochie-demo"' in fp_text
    assert '"bibliotheek"' not in fp_text


def test_copy_tree_dry_run_and_real(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    leaf = src / "content-source" / "catalogus" / "a" / "b" / "c"
    leaf.mkdir(parents=True)
    (leaf / "index.md").write_text("x\n", encoding="utf-8")
    (leaf / "song.vsa").write_text("vsa\n", encoding="utf-8")
    (leaf / "song.vsa.svg").write_text("<svg/>\n", encoding="utf-8")
    (leaf / "song.tekstblad.scherm.html").write_text("<html/>\n", encoding="utf-8")
    (src / "hugo.toml").write_text('title = "T"\n', encoding="utf-8")
    (src / "generated" / "site").mkdir(parents=True)
    (src / "generated" / "site" / "x.html").write_text("g\n", encoding="utf-8")

    n, _ = sr.copy_tree(src, dst, dry_run=True)
    assert n >= 3
    assert not dst.exists() or not any(dst.rglob("*"))

    dst.mkdir()
    sr.copy_tree(src, dst, dry_run=False)
    assert (dst / "content-source/catalogus/a/b/c/index.md").is_file()
    assert (dst / "content-source/catalogus/a/b/c/song.vsa").is_file()
    assert (
        dst / "content-source/catalogus/a/b/c/song.tekstblad.scherm.html"
    ).is_file()
    assert not (dst / "content-source/catalogus/a/b/c/song.vsa.svg").exists()
    assert not (dst / "generated/site/x.html").exists()


def test_main_rejects_dest_inside_source(tmp_path: Path) -> None:
    src = tmp_path / "repo"
    src.mkdir()
    (src / "hugo.toml").write_text('title = "T"\n', encoding="utf-8")
    dest = src / "out"
    assert sr.main(["--source", str(src), str(dest), "--dry-run"]) == 2


def test_main_dry_run_configure_needs_args(tmp_path: Path) -> None:
    src = tmp_path / "repo"
    src.mkdir()
    (src / "hugo.toml").write_text(
        'title = "Bibliotheek"\n\n[params]\n'
        '  feedback_email = "orthodoxronl@duck.com"\n',
        encoding="utf-8",
    )
    dest = tmp_path / "out"
    rc = sr.main(
        [
            "--source",
            str(src),
            str(dest),
            "--dry-run",
            "--configure",
        ]
    )
    assert rc == 2


def test_main_dry_run_with_identity(tmp_path: Path) -> None:
    src = tmp_path / "repo"
    (src / "content-source").mkdir(parents=True)
    (src / "content-source" / "_index.md").write_text("home\n", encoding="utf-8")
    (src / "hugo.toml").write_text(
        'title = "Bibliotheek"\n\n[params]\n'
        '  linksGithub = "https://github.com/orthodox-ronl/bibliotheek"\n'
        '  feedback_email = "orthodoxronl@duck.com"\n',
        encoding="utf-8",
    )
    dest = tmp_path / "out"
    rc = sr.main(
        [
            "--source",
            str(src),
            str(dest),
            "--dry-run",
            "--force",
            "--repo-name",
            "parochie-demo",
            "--site-title",
            "Parochie Demo",
        ]
    )
    assert rc == 0
    assert not dest.exists() or not any(dest.rglob("*"))
