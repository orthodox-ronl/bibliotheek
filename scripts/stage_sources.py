"""Entry: stage gewijzigde bronnen (zelfde selectie als commit, zonder -m)."""

from __future__ import annotations

import sys

from commit_sources import main

if __name__ == "__main__":
    sys.exit(main(mode="stage"))
