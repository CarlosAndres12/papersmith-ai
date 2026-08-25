"""papersmith command-line interface.

Subcommands register themselves here as they land; every handler returns the
process exit code and raises ``PapersmithError`` for typed failures.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .bridges import deliberation as deliberation_command
from .bridges import implementation as implementation_command
from .core import init as init_command
from .core import ingest as ingest_command
from .core import status as status_command
from .core import upgrade as upgrade_command
from .errors import PapersmithError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="papersmith",
        description="CLI workspace orchestrator for the papersmith-ai framework: "
        "initialize, upgrade, and run decoupled paper research workspaces.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    for register in _REGISTRY:
        register(sub)
    return parser


_REGISTRY: list = [
    init_command.register,
    upgrade_command.register,
    status_command.register,
    ingest_command.register,
    deliberation_command.register,
    implementation_command.register,
]


def command(register):
    """Decorator: register a subcommand's parser builder."""
    _REGISTRY.append(register)
    return register


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    try:
        return handler(args)
    except PapersmithError as exc:
        print(f"papersmith: error: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("papersmith: interrupted", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
