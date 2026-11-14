"""Gedeelde argparse-help voor bibliotheek-scripts.

Doel: ``script -h`` en ``script sub -h`` even leesbaar; defaults zichtbaar.
"""

from __future__ import annotations

import argparse


class CliHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    """Ruwe description/epilog + defaults; geen ``(default: None)``-ruis."""

    def _get_help_string(self, action: argparse.Action) -> str:
        help_text = action.help or ""
        if "%(default)" in help_text:
            return help_text
        if action.default is argparse.SUPPRESS or action.default is None:
            return help_text
        # Flags: duidelijker dan ``(default: False)``.
        if action.option_strings and action.nargs == 0:
            if action.default is False:
                return f"{help_text} (standaard: uit)"
            if action.default is True:
                return f"{help_text} (standaard: aan)"
        return super()._get_help_string(action)


def make_parser(
    *,
    prog: str,
    description: str,
    epilog: str | None = None,
    **kwargs: object,
) -> argparse.ArgumentParser:
    """ArgumentParser met gedeelde help-formatter."""
    return argparse.ArgumentParser(
        prog=prog,
        description=description,
        epilog=epilog,
        formatter_class=CliHelpFormatter,
        **kwargs,  # type: ignore[arg-type]
    )
