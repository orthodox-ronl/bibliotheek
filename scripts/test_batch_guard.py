"""Unit tests voor batch_guard (timing + schatting)."""

from __future__ import annotations

from pathlib import Path

import batch_guard as bg


def test_format_duration() -> None:
    assert "seconden" in bg.format_duration(12)
    assert "minuten" in bg.format_duration(120)
    assert "uur" in bg.format_duration(7200)


def test_record_and_estimate(tmp_path: Path, monkeypatch) -> None:
    store = tmp_path / "batch_timing.json"
    monkeypatch.setattr(bg, "STORE_PATH", store)
    assert bg.mean_seconds("layout") is None
    assert "onbekend" in bg.estimate_line("layout", 10)

    for s in (2.0, 4.0, 6.0):
        bg.record_sample("layout", s)
    mean, k = bg.mean_seconds("layout")  # type: ignore[misc]
    assert k == 3
    assert abs(mean - 4.0) < 1e-9
    line = bg.estimate_line("layout", 10)
    assert "Geschatte duur" in line
    assert "3 metingen" in line


def test_window_caps_at_20(tmp_path: Path, monkeypatch) -> None:
    store = tmp_path / "batch_timing.json"
    monkeypatch.setattr(bg, "STORE_PATH", store)
    for i in range(25):
        bg.record_sample("pagina_pdf", float(i + 1))
    mean, k = bg.mean_seconds("pagina_pdf")  # type: ignore[misc]
    assert k == 20
    # laatste 20: 6..25 → mean 15.5
    assert abs(mean - 15.5) < 1e-9


def test_confirm_skips_when_small(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    assert bg.confirm_batch(
        "layout",
        n=1,
        headline="1 bestand",
        yes=False,
    )
    out = capsys.readouterr().out
    assert "Batch «layout»" in out
    assert "Doorgaan?" not in out


def test_confirm_skips_under_hard_limit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Default: onder HARD_LIMIT geen soft-vraag (korte run op aantal)."""
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: True)

    def _boom(_p: str) -> str:
        raise AssertionError("geen Doorgaan? onder harde limiet")

    monkeypatch.setattr(bg, "_read_answer", _boom)
    assert bg.confirm_batch(
        "product_vsa",
        n=bg.HARD_LIMIT - 1,
        headline="99 bestanden",
        yes=False,
    )
    assert "Doorgaan?" not in capsys.readouterr().out


def test_confirm_skips_when_short_estimate(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Bekende schatting ≤ SOFT_SECONDS: geen soft-vraag ondanks lagere drempel."""
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    for _ in range(5):
        bg.record_sample("layout", 0.4)  # 20 × 0,4 s = 8 s
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: True)

    def _boom(_p: str) -> str:
        raise AssertionError("geen Doorgaan? bij korte schatting")

    monkeypatch.setattr(bg, "_read_answer", _boom)
    assert bg.confirm_batch(
        "layout",
        n=20,
        headline="20 bestanden",
        yes=False,
        confirm_from=5,
        hard_limit=100,
        soft_seconds=30,
    )
    out = capsys.readouterr().out
    assert "Doorgaan?" not in out
    assert "geschat" in out.lower() or "overgeslagen" in out


def test_confirm_asks_when_long_estimate(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Lange schatting + n ≥ confirm_from (< hard): soft Doorgaan?."""
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    for _ in range(5):
        bg.record_sample("layout", 10.0)  # 5 × 10 s = 50 s > 30
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: True)
    prompts: list[str] = []

    def _answer(p: str) -> str:
        prompts.append(p)
        return "j"

    monkeypatch.setattr(bg, "_read_answer", _answer)
    assert bg.confirm_batch(
        "layout",
        n=5,
        headline="5 bestanden",
        yes=False,
        confirm_from=2,
        hard_limit=100,
        soft_seconds=30,
    )
    assert prompts == ["Doorgaan? [j/N] "]
    _ = capsys.readouterr()


def test_confirm_yes_flag(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    # Soft-pad forceren: confirm_from laag + lange schatting
    for _ in range(3):
        bg.record_sample("layout", 20.0)
    assert bg.confirm_batch(
        "layout",
        n=5,
        headline="5 bestanden",
        yes=True,
        confirm_from=2,
        hard_limit=100,
        soft_seconds=30,
    )
    assert "-y/--yes" in capsys.readouterr().out


def test_hard_limit_rejects_yes_without_tty(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: False)
    assert not bg.confirm_batch(
        "products",
        n=bg.HARD_LIMIT,
        headline="alles",
        yes=True,
    )
    out = capsys.readouterr().out
    assert "dubbele bevestiging" in out or "HEEL zeker" in out or "grote batch" in out


def test_already_confirmed_skips_hard_limit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: True)

    def _boom(_p: str) -> str:
        raise AssertionError("geen input bij already_confirmed")

    monkeypatch.setattr(bg, "_read_answer", _boom)
    assert bg.confirm_batch(
        "product_vsa",
        n=bg.HARD_LIMIT + 1,
        headline="rebuild",
        yes=True,
        already_confirmed=True,
    )
    out = capsys.readouterr().out
    assert "aanroepende batch" in out


def test_hard_limit_double_confirm(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: True)
    answers = iter(["j", "ja"])
    monkeypatch.setattr(bg, "_read_answer", lambda _p: next(answers))
    assert bg.confirm_batch(
        "product_vsa",
        n=bg.HARD_LIMIT + 1,
        headline="rebuild",
        yes=True,  # moet genegeerd worden
    )
    out = capsys.readouterr().out
    assert "genegeerd" in out
    assert "Dubbele bevestiging ok" in out


def test_hard_limit_abort_on_second(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")
    monkeypatch.setattr(bg.sys.stdin, "isatty", lambda: True)
    answers = iter(["j", "nee"])
    monkeypatch.setattr(bg, "_read_answer", lambda _p: next(answers))
    assert not bg.confirm_batch(
        "layout",
        n=150,
        headline="te groot",
    )


def test_run_timed_batch_records(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(bg, "STORE_PATH", tmp_path / "t.json")

    def work(x: int) -> int:
        return 0 if x >= 0 else 1

    ok, failed, skipped = bg.run_timed_batch(
        "layout", [1, 2, -1], work, label=str
    )
    assert ok == 2
    assert failed == 1
    assert skipped == 0
    mean, k = bg.mean_seconds("layout")  # type: ignore[misc]
    assert k == 3
    assert mean >= 0

    def work_skip(x: int) -> int:
        return bg.SKIP if x == 0 else 0

    ok2, failed2, skipped2 = bg.run_timed_batch(
        "layout", [0, 1], work_skip, label=str
    )
    assert (ok2, failed2, skipped2) == (1, 0, 1)
    # skip mag het gemiddelde niet verdunnen
    _, k2 = bg.mean_seconds("layout")  # type: ignore[misc]
    assert k2 == 4
