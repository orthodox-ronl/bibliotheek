"""Unit tests for product_regen policy helpers."""

from __future__ import annotations

import argparse

from product_regen import (
    RegenPolicy,
    need_regen,
    policy_from_args,
)


def _ns(**kwargs):
    defaults = {
        "force": False,
        "only_missing": False,
        "only_stale": False,
        "only_invalid": False,
        "reasons": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_default_policy_all_three():
    p = policy_from_args(_ns())
    assert p == RegenPolicy(missing=True, stale=True, invalid=True)


def test_only_missing():
    p = policy_from_args(_ns(only_missing=True))
    assert need_regen(p, exists=False, stamp_ok=False) is True
    assert need_regen(p, exists=True, stamp_ok=False) is False
    assert need_regen(p, exists=True, stamp_ok=True, contract_ok=False) is False


def test_only_stale():
    p = policy_from_args(_ns(only_stale=True))
    assert need_regen(p, exists=False, stamp_ok=False) is False
    assert need_regen(p, exists=True, stamp_ok=False) is True
    assert need_regen(p, exists=True, stamp_ok=True, contract_ok=False) is False


def test_only_invalid():
    p = policy_from_args(_ns(only_invalid=True))
    assert need_regen(p, exists=True, stamp_ok=True, contract_ok=False) is True
    assert need_regen(p, exists=True, stamp_ok=False, contract_ok=True) is False
    assert need_regen(p, exists=False, stamp_ok=False) is False


def test_force():
    p = policy_from_args(_ns(force=True))
    assert need_regen(p, exists=True, stamp_ok=True, contract_ok=True) is True


def test_reasons_subset():
    p = policy_from_args(_ns(reasons="missing,invalid"))
    assert p.missing and p.invalid and not p.stale
    assert need_regen(p, exists=True, stamp_ok=False, contract_ok=True) is False
    assert need_regen(p, exists=True, stamp_ok=True, contract_ok=False) is True
