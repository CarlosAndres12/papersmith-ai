"""Synchronize framework-owned files into an existing workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..errors import SourceError, UserError
from ..generators import (
    UNSYNCHRONIZED,
    apply_generated,
    context_for_workspace,
    is_regular_file,
    render_files,
)
from ..kit import resolve_and_validate
from ..schema import validate_tools
from . import config, manifest

#: Dynamic rendered outputs — one file per discovered skill, so their membership
#: cannot be enumerated by a static list. Only paths under these prefixes that
#: were previously baselined are ever removed (see :func:`_orphaned`).
DYNAMIC_PREFIXES = (".opencode/commands/", ".claude/commands/")


def _contained(relpath: str) -> bool:
    """True when a stored key is a plain workspace-relative path.

    The manifest is data, so anything that is not a normal relative path — an
    absolute key, a ``..`` segment, or a NUL byte — is refused before it can be
    joined and unlinked. This check is lexical and total: it cannot itself raise.
    """
    if not relpath or relpath.startswith("/") or "\x00" in relpath:
        return False
    return ".." not in relpath.split("/")


def _orphaned(root: Path, previous_managed: set[str], current_render: set[str]) -> list[str]:
    """Baselined dynamic paths that are no longer derivable.

    The exact predicate: a path qualifies only when it is in ``previous_managed``
    (the stored manifest — it was this tool's own output), it starts with a
    declared dynamic prefix, it is absent from ``current_render``, and it is a
    contained relative path inside ``root``.

    A file under those prefixes that was never baselined is deliberately
    preserved: it is not this tool's output, so deleting it would lose user data.
    Static entrypoints never match a prefix and are never removable here.

    A stored-manifest key is data, not a trusted path. It is validated lexically
    first and only then resolved, so a crafted key is refused rather than
    resolved: a symlink loop, a NUL byte or an out-of-workspace target can never
    turn ``upgrade`` into a file-deletion primitive.
    """
    anchor = root.resolve()
    eligible: list[str] = []
    for path in previous_managed:
        if not path.startswith(DYNAMIC_PREFIXES) or path in current_render:
            continue
        if not _contained(path):
            continue
        try:
            inside = (root / path).resolve().is_relative_to(anchor)
        except (OSError, ValueError, RuntimeError):
            inside = False
        if inside:
            eligible.append(path)
    return sorted(eligible)


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
    context = context_for_workspace(root)
    unsynchronized: list[str] = []
    generated = apply_generated(root, context, active_tools, skipped=unsynchronized)
    for relpath in generated:
        if relpath not in changed:
            changed.append(relpath)

    # Remove previously-baselined dynamic outputs that stopped being derivable
    # (a workspace-local skill that was removed or renamed). The baseline is the
    # stored manifest loaded at the top of this run, before this run rewrites it
    # below — reading it afterwards would compare the new baseline with itself
    # and find nothing.
    current_render = set(render_files(root, context, active_tools))
    removed: list[str] = []
    stranded: list[str] = []
    for relpath in _orphaned(root, set(stored["files"]), current_render):
        target = root / relpath
        try:
            if not is_regular_file(target):
                stranded.append(relpath)
                continue
            target.unlink()
        except OSError:
            # A read-only parent or a refusing filesystem must not abort the run
            # after the workspace has already been synchronized; the path is
            # reported below instead, and a later run retries it.
            stranded.append(relpath)
            continue
        removed.append(relpath)

    version_path = root / ".papersmith" / "version"
    if not version_path.is_file() or version_path.read_text(encoding="utf-8").strip() != version:
        version_path.parent.mkdir(parents=True, exist_ok=True)
        version_path.write_text(version + "\n", encoding="utf-8")
        changed.append(".papersmith/version")

    framework_files = manifest.workspace_framework_files(root, kit_root)
    for relpath in stranded:
        # Keep an undeletable path in the baseline. It is not part of the current
        # framework set, so recording it makes ``status`` and ``audit`` report it
        # as drift and lets a later upgrade retry the removal; dropping it would
        # strand the file untracked forever.
        target = root / relpath
        framework_files[relpath] = (
            manifest.sha256_file(target) if is_regular_file(target) else UNSYNCHRONIZED
        )
    for relpath in current_render:
        # Every rendered path this run was responsible for must be accounted for
        # in the baseline. ``workspace_framework_files`` omits any path it cannot
        # hash — non-regular, never written, or written but still unreadable (a
        # write-only file) — and an omission on both sides of ``status``'s
        # comparison is a false "no drift". Sweeping the whole render set, rather
        # than only the paths reported as unsynchronized, is what makes this
        # total: a write can succeed and still leave the path unhashable.
        if relpath not in framework_files:
            framework_files[relpath] = UNSYNCHRONIZED
    manifest.write_manifest(root, version, framework_files, kind="workspace")
    return {
        "workspace": str(root),
        "version": version,
        "active_tools": active_tools,
        "changed_files": changed,
        "preserved_files": preserved,
        "removed": removed,
        "stranded": stranded,
        "unsynchronized": unsynchronized,
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
    for relpath in result["unsynchronized"]:
        print(f"Warning: could not write '{relpath}'; it stays reported as drift")
    return 0
