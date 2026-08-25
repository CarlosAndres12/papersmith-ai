"""Workspace and kit manifests: SHA-256 tracking, filtering, preservation.

Two manifests exist:

* ``kit-manifest.json`` at the kit root — hashes of every framework file the
  kit ships (written by ``scripts/build-kit.py``; computed on the fly when a
  development checkout has none).
* ``<workspace>/.papersmith/manifest.json`` — hashes of every
  framework-managed file as it exists in that workspace, plus the workspace
  version and update timestamp.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ..errors import UserError

MANIFEST_SCHEMA = 1

# The kit's top-level entries a workspace copies at init and re-syncs on
# upgrade. Everything else a workspace holds is either generated (rendered
# entrypoint docs) or preserved research state.
KIT_ENTRIES = (
    "skills",
    "guidance/paper-guide",
    ".claude/agents",
    "scripts/setup_env.py",
    "package.json",
    "requirements.txt",
)

# Framework-managed rendered files: generated deterministically, owned by the
# framework, and re-rendered on upgrade.
RENDERED_FILES = (
    "CLAUDE.md",
    "OPENCODE.md",
    "PI.md",
    ".pi/gentle-ai/persona.json",
    ".antigravity/rules.md",
    ".gitignore",
)

# Paths ``upgrade`` must never overwrite or delete. ``papersmith.yaml`` is
# user-edited compute configuration; the rest is research the user produces.
PRESERVE_PATTERNS = (
    "guidance/**",
    "proposals/**",
    "implementations/**",
    "kaggle-inbox/**",
    "journal/**",
    "DECISIONS.md",
    "papersmith.yaml",
    "README.md",
    ".env*",
)

_SKIP_DIRS = {".venv", "node_modules", "__pycache__", ".pytest_cache", ".micromamba", ".git"}
_SKIP_SUFFIXES = (".pyc", ".pyo")
_KEEP_HIDDEN = {".gitignore", ".gitkeep"}
_STORE_DIR = "skills/kaggle-accounts/store"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_preserved(relpath: str) -> bool:
    """True when ``upgrade`` must never overwrite or delete the path."""
    posix = relpath.replace("\\", "/")
    name = posix.rsplit("/", 1)[-1]
    for pattern in PRESERVE_PATTERNS:
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            if posix == prefix or posix.startswith(prefix + "/"):
                return True
        elif pattern.endswith("*") and pattern.startswith("."):
            if name.startswith(pattern[:-1]):
                return True
        elif posix == pattern:
            return True
    return False


def should_skip_file(path: Path) -> bool:
    name = path.name
    if name.startswith(".") and name not in _KEEP_HIDDEN:
        return True
    return path.suffix in _SKIP_SUFFIXES


def should_skip_dir(path: Path) -> bool:
    return path.name in _SKIP_DIRS


def _walk_dir(root: Path, kit_root: Path, files: dict[str, str]) -> None:
    for child in sorted(root.iterdir()):
        if child.is_dir():
            if should_skip_dir(child):
                continue
            if child.relative_to(kit_root).as_posix() == _STORE_DIR:
                # The credential store ships only its protective .gitignore —
                # a stored token committed is a token burned.
                for entry in sorted(child.iterdir()):
                    if entry.is_file() and entry.name == ".gitignore":
                        files[entry.relative_to(kit_root).as_posix()] = sha256_file(entry)
                continue
            _walk_dir(child, kit_root, files)
            continue
        if should_skip_file(child):
            continue
        files[child.relative_to(kit_root).as_posix()] = sha256_file(child)


def walk_kit_files(kit_root: Path) -> dict[str, str]:
    """relpath -> sha256 for every file the kit ships, filtered."""
    files: dict[str, str] = {}
    for entry in KIT_ENTRIES:
        path = kit_root / entry
        if not path.exists():
            continue
        if path.is_file():
            files[entry] = sha256_file(path)
        else:
            _walk_dir(path, kit_root, files)
    return files


def copy_kit_file(kit_root: Path, relpath: str, dest_root: Path) -> None:
    src = kit_root / relpath
    dst = dest_root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def load_manifest(workspace: Path) -> dict | None:
    path = workspace / ".papersmith" / "manifest.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UserError(f"corrupted manifest {path}: {exc}") from None
    if not isinstance(data, dict) or data.get("kind") != "workspace":
        raise UserError(f"corrupted manifest {path}: missing workspace envelope")
    if data.get("schema") != MANIFEST_SCHEMA or not isinstance(data.get("version"), str):
        raise UserError(f"corrupted manifest {path}: unsupported schema or version")
    files = data.get("files")
    if not isinstance(files, dict) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in files.items()
    ):
        raise UserError(f"corrupted manifest {path}: files must be a string-to-string map")
    return data


def write_manifest(dest_root: Path, version: str, files: dict[str, str], *, kind: str) -> None:
    payload = {
        "schema": MANIFEST_SCHEMA,
        "kind": kind,
        "version": version,
        "files": dict(sorted(files.items())),
    }
    if kind == "workspace":
        payload["updated_at"] = _timestamp()
        path = dest_root / ".papersmith" / "manifest.json"
    elif kind == "kit":
        payload["generated_at"] = _timestamp()
        path = dest_root / "kit-manifest.json"
    else:
        raise ValueError(f"unknown manifest kind {kind!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_kit_manifest(kit_root: Path) -> dict | None:
    path = kit_root / "kit-manifest.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UserError(f"corrupted kit manifest {path}: {exc}") from None
    if not isinstance(data, dict) or data.get("kind") != "kit":
        raise UserError(f"corrupted kit manifest {path}: missing kit envelope")
    if data.get("schema") != MANIFEST_SCHEMA or not isinstance(data.get("version"), str):
        raise UserError(f"corrupted kit manifest {path}: unsupported schema or version")
    return data


def kit_files(kit_root: Path) -> dict[str, str]:
    """relpath -> sha256 for the kit's framework files.

    A bundled kit answers from its manifest; a development checkout has none
    and is hashed live so ``upgrade`` always tracks the latest dev state.
    """
    cached = load_kit_manifest(kit_root)
    if cached is not None:
        files = cached.get("files")
        if isinstance(files, dict) and all(isinstance(v, str) for v in files.values()):
            return dict(files)
        raise UserError(f"corrupted kit manifest at {kit_root}: bad files map")
    return walk_kit_files(kit_root)


def kit_version(kit_root: Path) -> str:
    cached = load_kit_manifest(kit_root)
    if cached is not None and isinstance(cached.get("version"), str):
        return cached["version"]
    pkg = kit_root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, dict) and isinstance(data.get("version"), str):
            return data["version"]
    return "0.0.0"


def workspace_framework_files(workspace: Path, kit_root: Path) -> dict[str, str]:
    """Current hashes of every framework-managed file in a workspace."""
    files: dict[str, str] = {}
    for relpath in kit_files(kit_root):
        target = workspace / relpath
        if target.is_file():
            files[relpath] = sha256_file(target)
    for relpath in RENDERED_FILES:
        target = workspace / relpath
        if target.is_file():
            files[relpath] = sha256_file(target)
    version_file = workspace / ".papersmith" / "version"
    if version_file.is_file():
        files[".papersmith/version"] = sha256_file(version_file)
    return files
