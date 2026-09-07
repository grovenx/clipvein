"""Command-line entry point — the same engine the GUI uses, in the terminal.

    clipvein --streamer "Kai Cenat"
    clipvein --streamer N3on --source mock
    clipvein --list
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from .config import Settings, Source
from .engine import Engine
from .streamers import names


def _print_line(text: str, kind: str) -> None:
    try:
        from rich.console import Console

        console = Console()
        colors = {
            "code": "cyan",
            "found": "green",
            "ok": "bold green",
            "warn": "yellow",
            "error": "bold red",
            "result": "bold magenta",
            "info": "dim",
        }
        console.print(text, style=colors.get(kind, ""))
    except Exception:
        print(text)


async def _run(streamer: str, settings: Settings) -> int:
    engine = Engine(settings)
    async for line in engine.run(streamer):
        _print_line(line.text, line.kind)
        if line.result is not None:
            print()
            for i, link in enumerate(line.result.links, 1):
                print(f"{i}. {link}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clipvein",
        description="Mine the X feed for streamer clips worth posting.",
    )
    parser.add_argument("--streamer", "-s", help="Streamer name (see --list)")
    parser.add_argument(
        "--source",
        choices=[s.value for s in Source],
        help="Override the data source for this run.",
    )
    parser.add_argument("--min-views", type=int, help="Minimum views floor.")
    parser.add_argument("--list", action="store_true", help="List available streamers.")
    args = parser.parse_args(argv)

    if args.list:
        print("Available streamers:")
        for n in names():
            print(f"  - {n}")
        return 0

    if not args.streamer:
        parser.error("--streamer is required (or use --list)")

    settings = Settings.load()
    if args.source:
        settings.source = Source(args.source)
    if args.min_views is not None:
        settings.min_views = args.min_views

    return asyncio.run(_run(args.streamer, settings))


if __name__ == "__main__":
    sys.exit(main())
