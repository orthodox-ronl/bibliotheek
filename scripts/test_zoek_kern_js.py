"""Draait de Node-tests voor ``static/js/catalogus-zoek-kern.js``.

Wordt overgeslagen als ``node`` ontbreekt (Node is alleen voor deze tests nodig).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="node niet geïnstalleerd")
def test_zoek_kern_node_tests() -> None:
    proc = subprocess.run(
        ["node", "--test", str(REPO_ROOT / "tests" / "zoek-kern.test.mjs")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
