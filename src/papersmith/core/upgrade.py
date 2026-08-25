"""Synchronize framework-owned files into an existing workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..errors import SourceError, UserError
from ..generators import ALL_TOOLS, apply_generated, context_for_workspace
from ..kit import resolve_and_validate
from ..schema import validate_tools
from . import config, manifest


def _copy_if_needed(workspace: Path, kit_root: Path, relpath: str, *, force: bool) -> bool:
    source = kit_root / relpath
    destination = workspace / relpath
    if not source.is_file():
        raise SourceError(f"kit manifest names a missing source file: {source}")
    if manifest.is_preserved(relpath):
        return False
    if not force and destination.is_file() and (
        manifest.sha256_file(destination) == manifest.sha256_file(source)
    ):
        return False
    manifest.copy_kit_file(kit_root, relpath, workspace)
    return True


def upgrade(workspace: str | Path = ".", *, tools: Sequence[str] | None = None,
            force: bool = False) -> dict:
    root = Path(workspace).expanduser().resolve()
    stored = manifest.load_manifest(root)
    if stored is None:
        raise UserError(f"not a papersmith workspace: missing {root / '.papersmith/manifest.json'}")

    kit_root = resolve_and_validate()
    kit_files = manifest.kit_files(kit_root)
    version = manifest.kit_version(kit_root)
    workspace_config = config.load_workspace_config(root)
    active_tools = validate_tools(list(tools) if tools is not None else workspace_config["active_tools"])
    changed: list[str] = []
    preserved: list[str] = []

    for relpath in sorted(kit_files):
        if manifest.is_preserved(relpath):
            preserved.append(relpath)
            continue
        if _copy_if_needed(root, kit_root, relpath, force=force):
            changed.append(relpath)

    if tools is not None:
        workspace_config["active_tools"] = active_tools
    workspace_config["updated_at"] = config.utc_timestamp()
    config.write_json(root / ".papersmith" / "config.json", workspace_config)

    # Rendered files are framework-owned projections. Context is read after
    # raw agent/config files have been synchronized so the new roster appears.
    generated = apply_generated(root, context_for_workspace(root), active_tools)
    for relpath in generated:
        if relpath not in changed:
            changed.append(relpath)

    version_path = root / ".papersmith" / "version"
    if not version_path.is_file() or version_path.read_text(encoding="utf-8").strip() != version:
        version_path.parent.mkdir(parents=True, exist_ok=True)
        version_path.write_text(version + "\n", encoding="utf-8")
        changed.append(".papersmith/version")

    framework_files = manifest.workspace_framework_files(root, kit_root)
    manifest.write_manifest(root, version, framework_files, kind="workspace")
    return {
        "workspace": str(root),
        "version": version,
        "active_tools": active_tools,
        "changed_files": changed,
        "preserved_files": preserved,
        "warnings": [
            "package.json changed; run npm install in the workspace"
            if "package.json" in changed else ""
        ],
    }


def register(subparsers) -> None:
    parser = subparsers.add_parser("upgrade", help="synchronize framework files in a workspace")
    parser.add_argument("directory", nargs="?", default=".", metavar="<dir>")
    parser.add_argument("--tools", default=None, help="replace active runtime generators")
    parser.add_argument("--force", action="store_true", help="force framework-file writes")
    parser.set_defaults(handler=run_cli)


def run_cli(args) -> int:
    tools = None
    if args.tools is not None:
        tools = [item.strip() for item in args.tools.split(",") if item.strip()]
    result = upgrade(args.directory, tools=tools, force=args.force)
    print(f"Upgraded papersmith workspace: {result['workspace']}")
    print(f"Framework version: {result['version']}; changed files: {len(result['changed_files'])}")
    for warning in result["warnings"]:
        if warning:
            print(f"Warning: {warning}")
    return 0
