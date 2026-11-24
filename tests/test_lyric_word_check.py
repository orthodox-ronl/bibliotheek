"""Woordcontrole voor de opkuisscripts (Capella/MusicXML en MuseScore)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lyric_word_check as w  # noqa: E402


def test_chain_rebuilds_word():
    items = [("he-", "begin"), ("mel", "middle"), ("se", "end")]
    assert w.words_from_syllables(items) == [("he-mel-se", True)]


def test_whole_word_is_not_chain():
    assert w.words_from_syllables([("hemelse", "single")]) == [("hemelse", False)]


def test_unknown_whole_word_blocks():
    w.ALLOW_UNKNOWN = False
    with pytest.raises(SystemExit) as exc:
        w.require_known_words([("Qwertyplonk", "single")], source="x.mscz")
    assert "Qwertyplonk" in str(exc.value)


def test_allow_unknown_words_continues(capsys):
    w.ALLOW_UNKNOWN = True
    try:
        w.require_known_words([("Qwertyplonk", "single")], source="x.mscz")
    finally:
        w.ALLOW_UNKNOWN = False
    assert "WAARSCHUWING" in capsys.readouterr().out


def test_chain_problem_is_advice_only(capsys):
    w.ALLOW_UNKNOWN = False
    w.require_known_words(
        [("qwer-", "begin"), ("ty", "middle"), ("plonk", "end")], source="x.mscz"
    )
    assert "niet blokkerend" in capsys.readouterr().out
