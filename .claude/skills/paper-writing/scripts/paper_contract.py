"""paper_contract: front-matter grammar, schema validation, header insertion.

The only module in this skill that touches disk bytes for `sections/*.md`
(design.md, `Internal layering`). The header is JSON inside a `---` … `---`
front-matter fence; `json.loads` is all-or-nothing by construction, so
"never parses partially" is structural rather than a rule someone has to
maintain. Everything below the closing fence is prose — read as bytes and
handed back unread, never decoded for meaning.

Public surface:

    parse(data)                    -> (ContractHeader, body_bytes)
    resolve_sections_dir(arg, ...) -> Path   (raises SECTIONS_OUTSIDE_REPOSITORY)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_scaffold  # noqa: E402
import paper_vocabulary  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: The exact fence line. JSON is a YAML 1.2 subset, so this is also valid
#: YAML front matter and editors highlight it (design.md, `the header is
#: JSON inside a --- front-matter fence`).
_FENCE_LINE = b"---"

_TOP_LEVEL_REQUIRED = ("section", "position", "blocks")
_TOP_LEVEL_OPTIONAL = ("after",)
_TOP_LEVEL_ALLOWED = _TOP_LEVEL_REQUIRED + _TOP_LEVEL_OPTIONAL

_BLOCK_REQUIRED = ("id", "requires_facts", "requires_declarations", "citations")
_BLOCK_OPTIONAL = ("optional", "after")
_BLOCK_ALLOWED = _BLOCK_REQUIRED + _BLOCK_OPTIONAL

_AFTER_REQUIRED = ("target", "source")
_SOURCE_REQUIRED = ("file", "quote")


@dataclass(frozen=True)
class ContractHeader:
    """One parsed header. `blocks` is a list of validated dicts, each
    carrying exactly `id`, `requires_facts`, `requires_declarations`,
    `citations`, `optional`, `after` — defaults filled in, nothing extra."""

    section: str
    position: int
    after: list
    blocks: list


def _split_front_matter(data: bytes) -> tuple[str, bytes]:
    """Returns `(json_text, body_bytes)`. Refuses `MALFORMED_HEADER` when
    the file does not open with a `---` fence, the fence is never closed, or
    the header bytes are not valid UTF-8.
    """
    if not (data.startswith(b"---\n") or data.startswith(b"---\r\n")):
        raise Refused(
            "MALFORMED_HEADER",
            "file does not open with a '---' front-matter fence",
        )
    first_newline = data.index(b"\n")
    rest = data[first_newline + 1:]
    lines = rest.split(b"\n")
    close_idx = None
    for i, line in enumerate(lines):
        if line.rstrip(b"\r") == _FENCE_LINE:
            close_idx = i
            break
    if close_idx is None:
        raise Refused(
            "MALFORMED_HEADER",
            "front-matter fence opened but never closed with a line reading '---'",
        )
    json_bytes = b"\n".join(lines[:close_idx])
    body = b"\n".join(lines[close_idx + 1:])
    try:
        json_text = json_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refused("MALFORMED_HEADER", f"header bytes are not valid utf-8: {exc}")
    return json_text, body


def _validate_after_list(value, owner: str) -> list:
    if not isinstance(value, list):
        raise Refused("MALFORMED_HEADER", f"{owner}: 'after' must be a list")
    for entry in value:
        if not isinstance(entry, dict):
            raise Refused("MALFORMED_HEADER", f"{owner}: each 'after' entry must be an object")
        missing = [key for key in _AFTER_REQUIRED if key not in entry]
        if missing:
            raise Refused("MALFORMED_HEADER", f"{owner}: 'after' entry missing {missing[0]!r}")
        unknown = [key for key in entry if key not in _AFTER_REQUIRED]
        if unknown:
            raise Refused("MALFORMED_HEADER", f"{owner}: 'after' entry carries unknown key {unknown[0]!r}")
        source = entry["source"]
        if not isinstance(source, dict):
            raise Refused("MALFORMED_HEADER", f"{owner}: 'source' must be an object")
        missing_source = [key for key in _SOURCE_REQUIRED if key not in source]
        if missing_source:
            raise Refused("MALFORMED_HEADER", f"{owner}: 'source' missing {missing_source[0]!r}")
        unknown_source = [key for key in source if key not in _SOURCE_REQUIRED]
        if unknown_source:
            raise Refused(
                "MALFORMED_HEADER", f"{owner}: 'source' carries unknown key {unknown_source[0]!r}"
            )
    return value


def _parse_block(raw, section: str) -> dict:
    if not isinstance(raw, dict):
        raise Refused("MALFORMED_HEADER", f"{section}: each block must be an object")
    missing = [key for key in _BLOCK_REQUIRED if key not in raw]
    if missing:
        raise Refused("MALFORMED_HEADER", f"{section}: block missing {missing[0]!r}")
    unknown = [key for key in raw if key not in _BLOCK_ALLOWED]
    if unknown:
        raise Refused("MALFORMED_HEADER", f"{section}: block carries unknown key {unknown[0]!r}")

    block_id = raw["id"]
    if not isinstance(block_id, str) or not block_id:
        raise Refused("MALFORMED_HEADER", f"{section}: block 'id' must be a non-empty string")

    facts = raw["requires_facts"]
    if not isinstance(facts, list):
        raise Refused("MALFORMED_HEADER", f"{section}.{block_id}: 'requires_facts' must be a list")
    for fact in facts:
        paper_vocabulary.validate_fact(fact)

    declarations = raw["requires_declarations"]
    if not isinstance(declarations, list):
        raise Refused(
            "MALFORMED_HEADER", f"{section}.{block_id}: 'requires_declarations' must be a list"
        )
    for declaration in declarations:
        paper_vocabulary.validate_declaration(declaration)

    citations = raw["citations"]
    if not isinstance(citations, str):
        raise Refused("MALFORMED_HEADER", f"{section}.{block_id}: 'citations' must be a string")
    paper_vocabulary.validate_citations(citations)

    optional = raw.get("optional", False)
    if not isinstance(optional, bool):
        raise Refused("MALFORMED_HEADER", f"{section}.{block_id}: 'optional' must be a boolean")

    block_after = _validate_after_list(raw.get("after", []), f"{section}.{block_id}")

    return {
        "id": block_id,
        "requires_facts": list(facts),
        "requires_declarations": list(declarations),
        "citations": citations,
        "optional": optional,
        "after": block_after,
    }


def parse_header(header) -> ContractHeader:
    """Validates an already-`json.loads`-ed header object against the
    schema and the three vocabularies. Refuses `MALFORMED_HEADER` naming the
    missing or unknown key; refuses `UNKNOWN_FACT` / `UNKNOWN_DECLARATION` /
    `UNKNOWN_CITATIONS_REGIME` from `paper_vocabulary` for a value outside
    the closed vocabularies."""
    if not isinstance(header, dict):
        raise Refused("MALFORMED_HEADER", "header is not a JSON object")

    missing = [key for key in _TOP_LEVEL_REQUIRED if key not in header]
    if missing:
        raise Refused("MALFORMED_HEADER", f"missing required key {missing[0]!r}")
    unknown = [key for key in header if key not in _TOP_LEVEL_ALLOWED]
    if unknown:
        raise Refused("MALFORMED_HEADER", f"unknown key {unknown[0]!r}")

    section = header["section"]
    if not isinstance(section, str) or not section:
        raise Refused("MALFORMED_HEADER", "'section' must be a non-empty string")

    position = header["position"]
    if not isinstance(position, int) or isinstance(position, bool):
        raise Refused("MALFORMED_HEADER", "'position' must be an integer")

    blocks_raw = header["blocks"]
    if not isinstance(blocks_raw, list) or not blocks_raw:
        raise Refused("MALFORMED_HEADER", "'blocks' must be a non-empty list")

    after = _validate_after_list(header.get("after", []), section)
    blocks = [_parse_block(raw, section) for raw in blocks_raw]

    return ContractHeader(section=section, position=position, after=after, blocks=blocks)


def parse(data: bytes) -> tuple[ContractHeader, bytes]:
    """The whole-file entry point: split the fence, `json.loads` the
    middle, validate the result. `json.loads` is all-or-nothing, so a
    malformed body never produces a partial header -- the caller gets a
    `Refused` and nothing else (`MALFORMED_HEADER`, carrying the
    `JSONDecodeError`'s own line/column rather than a bare "invalid")."""
    json_text, body = _split_front_matter(data)
    try:
        raw_header = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise Refused(
            "MALFORMED_HEADER",
            f"invalid JSON in header at line {exc.lineno} column {exc.colno}: {exc.msg}",
        )
    header = parse_header(raw_header)
    return header, body


def resolve_sections_dir(sections_arg: str | None, *, forge_root: Path = paper_scaffold.FORGE_ROOT) -> Path:
    """Resolve `--sections <dir>` (or the default `<forge_root>/sections`).

    Refuses `SECTIONS_OUTSIDE_REPOSITORY` (invocation-defect) when the
    resolved path does not sit under `forge_root`. Reuses
    `paper_scaffold.FORGE_ROOT` rather than re-deriving a second root
    constant — the same `parents[4]` resolution `paper_scaffold.py` already
    proved, at the same directory depth from this file.
    """
    root = forge_root.resolve()
    target = Path(sections_arg).resolve() if sections_arg else (root / "sections")
    try:
        target.relative_to(root)
    except ValueError:
        raise Refused(
            "SECTIONS_OUTSIDE_REPOSITORY",
            f"{target} does not resolve inside the repository root {root}",
        )
    return target
