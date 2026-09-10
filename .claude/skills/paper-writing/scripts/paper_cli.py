#!/usr/bin/env python3
"""paper_cli.py — front door for the `paper-writing` skill.

Standard library only, keyless, offline, fail-closed — the shape of
`implementation_cli.py` and `remote_cli.py`. One JSON object on stdout per
invocation. Exit 0 means the command ran; exit 2 means a guard refused
before touching disk.

This first slice wires only `scaffold`. `open`, `status` and `substitute`
land once `paper_block.py`'s engine has its own CLI wiring — a later,
separate work unit; importing it here before then would wire commands this
slice's own tests do not cover.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_scaffold  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: This script's own absolute path, resolved once — printed by no command
#: yet, kept for the same reason `implementation_cli.py`'s `CLI_PATH` is:
#: whatever prints a runnable command later reaches for this rather than a
#: bare relative name.
CLI_PATH = Path(__file__).resolve()


def cmd_scaffold(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    return paper_scaffold.scaffold(paper_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scaffold = sub.add_parser("scaffold", help="create/re-enter paper/ idempotently")
    p_scaffold.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )

    return parser


_COMMANDS = {"scaffold": cmd_scaffold}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = _COMMANDS[args.command](args)
    except Refused as exc:
        print(json.dumps({"status": "refused", "code": exc.code, "detail": exc.detail}))
        return 2
    print(json.dumps({"status": "ok", "command": args.command, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
