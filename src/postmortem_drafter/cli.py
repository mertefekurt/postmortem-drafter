from __future__ import annotations

import argparse
import sys
from pathlib import Path

from postmortem_drafter import __version__
from postmortem_drafter.drafter import draft_postmortem
from postmortem_drafter.io import read_events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="postmortem-drafter",
        description="Draft a Markdown incident postmortem from timeline CSV or JSONL.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", nargs="?", type=Path, help="timeline CSV or JSONL file")
    parser.add_argument("--format", choices=("auto", "csv", "jsonl"), default="auto")
    parser.add_argument("--title", default="Incident postmortem")
    parser.add_argument("--out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input is None:
        parser.print_help()
        return 0
    try:
        events = read_events(args.input, args.format)
        draft = draft_postmortem(events, args.title)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(draft.markdown, encoding="utf-8")
        else:
            print(draft.markdown, end="")
    except (OSError, ValueError) as exc:
        print(f"postmortem-drafter: error: {exc}", file=sys.stderr)
        return 1
    return 0

