"""OpenCDC CLI entry point.

Usage:
  python -m opencdc <yosys-json> [--report report.html]

This module provides a small command-line interface to the OpenCDC analyzer.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .checker import check_netlist_file


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="opencdc",
        description="OpenCDC: clock-domain crossing analysis for Yosys JSON netlists.",
    )
    parser.add_argument(
        "netlist",
        help="Path to a Yosys JSON netlist (produced by `yosys -p \"synth; write_json ...\"`).",
    )
    parser.add_argument(
        "--report",
        help="Optional path to write an HTML report (not yet implemented).",
        default=None,
    )
    return parser.parse_args(argv)


def _print_crossings(crossings: list[dict]) -> None:
    console = Console()

    if not crossings:
        console.print(":white_check_mark: [green]No cross-domain nets detected.[/green]")
        return

    table = Table(title="OpenCDC: cross-domain net crossings")
    table.add_column("Net", style="cyan", no_wrap=True)
    table.add_column("Driver FF", style="magenta")
    table.add_column("Driver domain", style="green")
    table.add_column("Sink FF", style="magenta")
    table.add_column("Sink domain", style="green")

    for c in crossings:
        table.add_row(
            c["net"],
            c["driver_ff"],
            c["driver_domain"],
            c["sink_ff"],
            c["sink_domain"],
        )

    console.print(table)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    path = Path(args.netlist)
    if not path.exists():
        Console().print(f":x: [red]Netlist file not found:[/red] {path}")
        return 2

    crossings = check_netlist_file(str(path))
    _print_crossings(crossings)

    # Simple exit policy for Tier 1: nonzero on any detected crossing.
    return 1 if crossings else 0


if __name__ == "__main__":
    raise SystemExit(main())
