"""paper_guidance: per-folder `guidance/<folder>` class registry.

Classifies each folder under `guidance/` as `style-reference` or `evidence`
by reading a per-folder marker file, `guidance/<folder>/.paper-writing.json`
— never by reading the folder's name. A folder carrying no marker is
reported `unclassified`, including every folder on a fresh clone, where no
marker files exist yet. That is designed behavior, not a default and not a
fault (`specs/guidance-registry/spec.md`).

`guidance/` is not a fact source (`design.md`, `A fact the agent may
observe is a partition, not a guideline`); this registry feeds only the
style/evidence classification `plan` reports.

`ingested_papers(guidance_dir)` (`the-phases-are-derived-not-remembered`)
is a second, independent walk -- two levels deep, gitignore-blind by
`Path.iterdir()`'s own construction -- feeding `plan`/`packet`'s report of
which papers actually sit under `guidance/`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_scaffold  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: The closed two-value vocabulary a marker's `class` may hold
#: (`specs/guidance-registry/spec.md`, `Requirement: Per-Folder Marker
#: File`).
CLASSES: tuple[str, ...] = ("style-reference", "evidence")

_MARKER_NAME = ".paper-writing.json"
_MARKER_ALLOWED_KEYS = ("class",)


def resolve_guidance_dir(
    guidance_arg: str | None, *, forge_root: Path = paper_scaffold.FORGE_ROOT
) -> Path:
    """Resolve `--guidance <dir>` (or the default `<forge_root>/guidance`).

    Refuses `GUIDANCE_OUTSIDE_REPOSITORY` (invocation-defect) when the
    resolved path does not sit under `forge_root` — mirrors
    `paper_contract.resolve_sections_dir` exactly, at the same directory
    depth from this file.
    """
    root = forge_root.resolve()
    target = Path(guidance_arg).resolve() if guidance_arg else (root / "guidance")
    try:
        target.relative_to(root)
    except ValueError:
        raise Refused(
            "GUIDANCE_OUTSIDE_REPOSITORY",
            f"{target} does not resolve inside the repository root {root}",
        )
    return target


def _classify(folder: Path) -> str:
    """One folder's class, or `unclassified` when it carries no marker.

    Refuses `MALFORMED_GUIDANCE_MARKER` (work-state) when the marker file
    is not valid UTF-8, not valid JSON, not a JSON object, carries any key
    other than `class`, or omits `class`. Refuses `UNKNOWN_GUIDANCE_CLASS`
    (work-state) when `class` holds a value outside `CLASSES` — this never
    silently degrades to `unclassified`; only a genuinely absent marker
    file does that.
    """
    marker_path = folder / _MARKER_NAME
    if not marker_path.is_file():
        return "unclassified"
    try:
        raw_text = marker_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise Refused("MALFORMED_GUIDANCE_MARKER", f"{marker_path}: not valid utf-8: {exc}")
    try:
        obj = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise Refused("MALFORMED_GUIDANCE_MARKER", f"{marker_path}: invalid JSON: {exc.msg}")
    if not isinstance(obj, dict):
        raise Refused("MALFORMED_GUIDANCE_MARKER", f"{marker_path}: must be a JSON object")
    unknown = [key for key in obj if key not in _MARKER_ALLOWED_KEYS]
    if unknown:
        raise Refused(
            "MALFORMED_GUIDANCE_MARKER", f"{marker_path}: carries unknown key {unknown[0]!r}"
        )
    if "class" not in obj:
        raise Refused("MALFORMED_GUIDANCE_MARKER", f"{marker_path}: missing required key 'class'")
    value = obj["class"]
    if value not in CLASSES:
        raise Refused(
            "UNKNOWN_GUIDANCE_CLASS",
            f"{marker_path}: {value!r} is not one of the declared classes {CLASSES}",
        )
    return value


def ingested_papers(guidance_dir: Path) -> dict:
    """`{root: [{"folder": paper_folder_name, "markdown": str(path)}, ...]}`
    for every `guidance/<root>/<paper>/<paper>.md` two levels under
    `guidance_dir` (`the-phases-are-derived-not-remembered`, design.md D4).

    `read_registry` above enumerates ONE level (`guidance/<root>`), so the
    eight ingested papers actually sitting two levels down
    (`guidance/<root>/<paper>/<paper>.md`) are invisible to it -- and
    `guidance/*/*` is a `.gitignore` pattern, so `fd`/`rg` report the whole
    tree empty. `Path.iterdir()` is gitignore-blind BY CONSTRUCTION -- the
    mechanism, not an instruction (`specs/skeleton-startup/spec.md`,
    `Requirement: Disk Presence Checks Include Ignored Paths`) -- so this
    walks with it, never `fd`/`rg`/a shell call.

    A root directory holding no ingested papers reports an empty list, not
    an absence -- the point is exactly that a populated-but-ignored
    directory must never be reported as empty; an EMPTY root is a true,
    honestly reported empty list. A non-existent `guidance_dir` reports an
    empty registry, matching `read_registry`'s own precedent.
    """
    if not guidance_dir.is_dir():
        return {}
    registry: dict = {}
    for root_entry in sorted(guidance_dir.iterdir()):
        if not root_entry.is_dir():
            continue
        papers = []
        for paper_entry in sorted(root_entry.iterdir()):
            if not paper_entry.is_dir():
                continue
            markdown_path = paper_entry / f"{paper_entry.name}.md"
            if markdown_path.is_file():
                papers.append({"folder": paper_entry.name, "markdown": str(markdown_path)})
        registry[root_entry.name] = papers
    return registry


def read_registry(guidance_dir: Path) -> dict:
    """`{folder_name: class-or-"unclassified"}` for every directory
    directly under `guidance_dir`.

    Enumerated from disk (`sorted(guidance_dir.iterdir())`); no folder name
    is ever referenced as a constant anywhere in this module — the
    anti-pattern this registry exists to keep out
    (`_core/deliberation/engine/proposal-workspace.ts:49`'s hardcoded
    `GUIDE_DIRECTORY`, named as precedent, not repaired here). A
    non-existent `guidance_dir` reports an empty registry rather than
    refusing — a repository that has never created the folder has simply
    classified nothing yet.
    """
    if not guidance_dir.is_dir():
        return {}
    registry: dict = {}
    for entry in sorted(guidance_dir.iterdir()):
        if not entry.is_dir():
            continue
        registry[entry.name] = _classify(entry)
    return registry
