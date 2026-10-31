"""Console interface for the currently available project foundation."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from oscar_patterns import __version__


def build_parser() -> argparse.ArgumentParser:
    """Create the public CLI without advertising unimplemented commands."""
    parser = argparse.ArgumentParser(
        prog="oscar-data",
        description=(
            "Awards Patterns project tools. "
            "Data pipeline commands are not yet available."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Show project help, or process help/version arguments."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
