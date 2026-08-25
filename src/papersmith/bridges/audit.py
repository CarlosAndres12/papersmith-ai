"""Workspace structural audit and generator-drift checks."""

from __future__ import annotations

from pathlib import Path

from ..core import manifest
from ..core.exit_codes import DRIFT_ERROR, SUCCESS
from ..errors import UserError
from ..generators import check_generated, context_for_workspace
from ..kit import resolve_and_validate
from .python import emit_result, run_script


def execute(workspace: str | Path, *, check_drift: bool = False) -> int:
    root = Path(workspace).expanduser().resolve()
    spec = root / "skills/skill-audit/references/probes/skill-audit.subcommands.json"
    if not spec.is_file():
        raise UserError(f"missing structural audit probe: {spec}")
    result = run_script(
        root,
        "skills/skill-audit/scripts/audit_cli.py",
        [
            "roster",
            "--subject", str(root / "skills/skill-audit"),
            "--probe-spec", str(spec),
            "--repo-root", str(root),
        ],
    )
    code = emit_result(result)
    if code != SUCCESS:
        return code
    if not check_drift:
        return SUCCESS
    drift = check_generated(root, context_for_workspace(root))
    stored = manifest.load_manifest(root)
    if stored is None:
        raise UserError(f"not a papersmith workspace: missing {root / '.papersmith/manifest.json'}")
    kit_root = resolve_and_validate()
    current = manifest.workspace_framework_files(root, kit_root)
    manifest_drift = sorted({
        path for path in set(current) | set(stored["files"])
        if current.get(path) != stored["files"].get(path)
    })
    if drift or manifest_drift:
        if drift:
            print("generator drift: " + ", ".join(drift))
        if manifest_drift:
            print("manifest drift: " + ", ".join(manifest_drift))
        return DRIFT_ERROR
    print("drift: clean")
    return SUCCESS


def register(subparsers) -> None:
    parser = subparsers.add_parser("audit", help="audit workspace structure and consistency")
    parser.add_argument("directory", nargs="?", default=".", metavar="<dir>")
    parser.add_argument("--check-drift", action="store_true")
    parser.set_defaults(handler=run_cli)


def run_cli(args) -> int:
    return execute(args.directory, check_drift=args.check_drift)
