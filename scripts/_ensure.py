"""Install/check repo deps after scripts/_ensure.cmd has verified Python 3.14."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

HUGO_VERSION = "0.160.1"


def fail(message: str, *hints: str) -> None:
    print("ERROR: " + message)
    for hint in hints:
        print(hint)
    raise SystemExit(1)


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, text=True, **kwargs)


def check_hugo() -> None:
    hugo = shutil.which("hugo")
    if not hugo:
        fail(
            "hugo not found on PATH",
            "Install Hugo Extended 0.160.1 and add it to PATH.",
            "Reference folder: C:\\Git\\tools\\hugo",
        )
    proc = run([hugo, "version"], capture_output=True)
    text = (proc.stdout or "") + (proc.stderr or "")
    if HUGO_VERSION not in text:
        fail(
            f"hugo version is not {HUGO_VERSION}",
            text.strip() or "(no hugo version output)",
            f"Replace the binary with Hugo Extended {HUGO_VERSION}.",
            "Reference folder: C:\\Git\\tools\\hugo",
        )
    if "extended" not in text.lower():
        fail(
            "hugo is not the Extended build",
            text.strip(),
            f"Install Hugo Extended {HUGO_VERSION}.",
        )


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--hugo", action="store_true")
    args, _unknown = parser.parse_known_args()

    if args.hugo:
        check_hugo()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
