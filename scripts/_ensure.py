"""Install/check repo deps after scripts/_ensure.cmd has verified Python 3.14.

VSA-tooling-ref: zie docs/tooling-koppeling.md (float vs pin).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = ROOT / ".ensure-stamp"
PIN_FILE = ROOT / "vsa-tooling.pin"
HUGO_VERSION = "0.160.1"
VSA_TOOLING_GIT = "https://github.com/orthodox-ronl/VSA-tooling.git"


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


def check_vsa() -> None:
    vsa = shutil.which("vsa")
    if not vsa:
        fail(
            "vsa not found on PATH",
            "Run scripts\\_ensure.cmd --vsa-tool, or add the VSA-tooling",
            "venv Scripts folder to PATH after installing vsa-tool there.",
            "Reference: C:\\Git\\orthodox-ronl\\VSA-tooling\\.venv\\Scripts",
        )


def pip_install(args: list[str]) -> None:
    cmd = [sys.executable, "-m", "pip", "install", *args]
    proc = run(cmd)
    if proc.returncode != 0:
        fail("pip install failed: " + " ".join(args))


def module_ok(name: str) -> bool:
    proc = run(
        [sys.executable, "-c", f"import {name}"],
        capture_output=True,
    )
    return proc.returncode == 0


def stamp_payload(files: list[Path], extras: list[str]) -> str:
    h = hashlib.sha256()
    for path in files:
        h.update(path.read_bytes())
    for extra in extras:
        h.update(extra.encode("utf-8"))
    h.update(f"py{sys.version_info[:2]}".encode())
    return h.hexdigest()


def sibling_or_vendor(*relatives: str) -> Path | None:
    for rel in relatives:
        candidate = (ROOT / rel).resolve()
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return None


def read_pin() -> str:
    if not PIN_FILE.is_file():
        fail(
            f"pin file missing: {PIN_FILE.name}",
            "Create it with a VSA-tooling commit SHA or tag.",
            "See docs/tooling-koppeling.md",
        )
    ref = PIN_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    if not ref or ref.startswith("#"):
        fail(f"empty pin in {PIN_FILE.name}")
    return ref


def detect_tooling_mode() -> str:
    """Return 'pin' or 'float'."""
    explicit = os.environ.get("BIBLIOTHEEK_TOOLING_MODE", "").strip().lower()
    if explicit in {"pin", "float"}:
        return explicit
    ref = os.environ.get("GITHUB_REF", "").strip()
    if ref == "refs/heads/main":
        return "pin"
    return "float"


def resolve_tooling_ref() -> tuple[str, str]:
    """Return (ref, mode) for git install of vsa-tool."""
    override = os.environ.get("VSA_TOOLING_REF", "").strip()
    if override:
        return override, "override"
    mode = detect_tooling_mode()
    if mode == "pin":
        return read_pin(), "pin"
    return "main", "float"


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--hugo", action="store_true")
    parser.add_argument("--vsa", action="store_true")
    parser.add_argument("--vsa-tool", action="store_true")
    parser.add_argument("--import", dest="imports", action="append", default=[])
    parser.add_argument("--pip-r", action="append", default=[])
    parser.add_argument("--pip-e", action="append", default=[])
    args, _unknown = parser.parse_known_args()

    if args.hugo:
        check_hugo()
    if args.vsa:
        check_vsa()

    req_files = [ROOT / rel for rel in args.pip_r]
    for path in req_files:
        if not path.is_file():
            fail(f"requirements file not found: {path}")

    extras = list(args.pip_e)
    tooling_ref = ""
    tooling_mode = ""
    if args.vsa_tool:
        tooling_ref, tooling_mode = resolve_tooling_ref()
        extras.append(f"vsa-tool:{tooling_mode}:{tooling_ref}")
        print(f"VSA-tooling: mode={tooling_mode} ref={tooling_ref}", flush=True)

    payload = stamp_payload(req_files, extras + args.imports)
    if STAMP.is_file() and STAMP.read_text(encoding="utf-8").strip() == payload:
        missing = [name for name in args.imports if not module_ok(name)]
        if args.vsa_tool and not module_ok("vsa"):
            missing.append("vsa")
        if not missing:
            return 0

    for rel in args.pip_r:
        pip_install(["-r", str(ROOT / rel)])

    for spec in args.pip_e:
        pip_install(["-e", spec])

    if args.vsa_tool and not module_ok("vsa"):
        tooling = sibling_or_vendor(
            os.path.join("..", "VSA-tooling"),
            os.path.join("vendor", "VSA-tooling"),
        )
        if tooling is not None:
            print(f"VSA-tooling: editable install from {tooling}", flush=True)
            pip_install(["-e", f"{tooling}[rendering]"])
        else:
            spec = (
                f"vsa-tool[rendering] @ git+{VSA_TOOLING_GIT}@{tooling_ref}"
            )
            print(f"VSA-tooling: pip {spec}", flush=True)
            pip_install([spec])

    missing = [name for name in args.imports if not module_ok(name)]
    if args.vsa_tool and not module_ok("vsa"):
        missing.append("vsa")
    if missing:
        fail(
            "python imports still missing: " + ", ".join(missing),
            "pip install did not provide them in this Python 3.14 interpreter.",
        )

    STAMP.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
