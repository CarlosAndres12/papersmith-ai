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
#: `mode` widened in `the-writer-may-assert-only-what-it-was-given`
#: (`section-contract` spec, `Requirement: Front Matter Schema`, MODIFIED):
#: the section-level drafting-mode default, optional, overridden per block.
_TOP_LEVEL_OPTIONAL = ("after", "mode")
_TOP_LEVEL_ALLOWED = _TOP_LEVEL_REQUIRED + _TOP_LEVEL_OPTIONAL

_BLOCK_REQUIRED = ("id", "requires_facts", "requires_declarations", "citations")
#: `mode` widened the same way at block level — a block's own `mode`
#: overrides the section-level default when present (`resolve_mode` below).
#: `figure` widened in `a-diagram-that-compiles-or-says-why`
#: (`section-contract` spec, `Requirement: Front Matter Schema`, MODIFIED):
#: a per-block diagram obligation, read by `paper_obligation.py` and never
#: hardcoded against a section or block id.
_BLOCK_OPTIONAL = ("optional", "after", "mode", "figure")
_BLOCK_ALLOWED = _BLOCK_REQUIRED + _BLOCK_OPTIONAL

#: A `figure` object's own six subkeys. Five are required, nothing else
#: admitted (`diagram-obligation` spec, `Requirement: Obligations Read From
#: Contract Front Matter`; `section-contract` spec, `Requirement: Front
#: Matter Schema`). `caption_decodes` is deliberately a boolean, not a list
#: of encodings — WHICH encodings exist is a property of the diagram itself
#: and lives in `<id>.diagram.json`, never duplicated into the contract.
#:
#: `components_from` is OPTIONAL (corrective amendment, `a-diagram-that-
#: compiles-or-says-why`'s own verify FAIL, CRITICAL finding): it names the
#: one fact whose value IS the diagram's full expected component list, and
#: that equality only holds when the diagram truly is one fact's own list
#: by contract (section 01: the methods diagram is the contribution list).
#: A block whose diagram is a composite crossing over several categories of
#: content, none of which alone is the full list (section 02's closing
#: diagram), declares no `components_from` at all — the Components Check
#: then does not run for that block, honestly, rather than being wired to
#: one fact's partial value and silently inverting (measured directly: a
#: prose-compliant diagram refused, a degenerate one passed). Same
#: `raw.get(...) is not None` round-trip convention `mode` already uses
#: below, so a re-serialized header's explicit `null` means the same as the
#: key being absent.
_FIGURE_REQUIRED = (
    "ordered", "excludes",
    "caption_enumerates", "caption_decodes", "mandatory",
)
_FIGURE_OPTIONAL = ("components_from",)
_FIGURE_ALLOWED = _FIGURE_REQUIRED + _FIGURE_OPTIONAL

_AFTER_REQUIRED = ("target", "source")
_SOURCE_REQUIRED = ("file", "quote")
#: Same shape as an `after` entry's own `source` — `{value, source}`, where
#: `source` is `{file, quote}` (`section-contract` spec, `Requirement:
#: Closed Mode Vocabulary And Transcription`). Reuses `_validate_source`
#: below rather than a second copy of the same three checks.
_MODE_REQUIRED = ("value", "source")


@dataclass(frozen=True)
class ContractHeader:
    """One parsed header. `blocks` is a list of validated dicts, each
    carrying exactly `id`, `requires_facts`, `requires_declarations`,
    `citations`, `optional`, `after`, `mode` — defaults filled in, nothing
    extra. `mode` is the section-level default (`None` when the header
    declares none); a block's own `mode` entry, also `None` when absent,
    wins over it (`resolve_mode` below)."""

    section: str
    position: int
    after: list
    blocks: list
    mode: dict | None = None


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


def _validate_source(source, owner: str) -> dict:
    """The `{file, quote}` shape an `after` entry's own `source` carries,
    and — since `the-writer-may-assert-only-what-it-was-given` — a `mode`
    declaration's `source` too (`section-contract` spec, `Requirement:
    Closed Mode Vocabulary And Transcription`: "the same shape
    `_validate_after_list` already enforces for `after` edges"). Factored
    out here so one validator serves both rather than two copies drifting
    (`design.md`, Decision D4)."""
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
    return source


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
        _validate_source(entry["source"], owner)
    return value


def _validate_mode_object(raw, owner: str) -> dict:
    """`mode` MUST be `{value, source}` — `value` one of
    `paper_vocabulary.MODES`, `source` the same `{file, quote}` shape
    `_validate_source` already enforces for `after` edges. Refuses
    `UNKNOWN_MODE` (via `paper_vocabulary.validate_mode`) for a `value`
    outside the pair (`section-contract` spec, `Requirement: Closed Mode
    Vocabulary And Transcription`)."""
    if not isinstance(raw, dict):
        raise Refused("MALFORMED_HEADER", f"{owner}: 'mode' must be an object")
    missing = [key for key in _MODE_REQUIRED if key not in raw]
    if missing:
        raise Refused("MALFORMED_HEADER", f"{owner}: 'mode' missing {missing[0]!r}")
    unknown = [key for key in raw if key not in _MODE_REQUIRED]
    if unknown:
        raise Refused("MALFORMED_HEADER", f"{owner}: 'mode' carries unknown key {unknown[0]!r}")
    value = raw["value"]
    if not isinstance(value, str):
        raise Refused("MALFORMED_HEADER", f"{owner}: 'mode.value' must be a string")
    paper_vocabulary.validate_mode(value)
    source = _validate_source(raw["source"], f"{owner}.mode")
    return {"value": value, "source": dict(source)}


def _parse_figure(raw, owner: str) -> dict:
    """`diagram-obligation` spec, `Requirement: Obligations Read From
    Contract Front Matter`; `section-contract` spec, `Requirement: Front
    Matter Schema`. Refuses `MALFORMED_FIGURE_OBLIGATION` naming the
    missing or unknown key, or a wrong-typed value. `components_from`,
    when present, is validated through `paper_vocabulary.validate_fact` —
    an invented fact refuses `UNKNOWN_FACT`, reused verbatim rather than a
    second vocabulary (design.md, "Refusal codes and their classification").
    Absent (or explicit JSON `null`, matching `mode`'s own round-trip
    convention), it resolves to `None` and admits no Components Check for
    that block — see `_FIGURE_REQUIRED`'s own comment for why this is
    optional rather than the original six-required schema."""
    if not isinstance(raw, dict):
        raise Refused("MALFORMED_FIGURE_OBLIGATION", f"{owner}: 'figure' must be an object")
    missing = [key for key in _FIGURE_REQUIRED if key not in raw]
    if missing:
        raise Refused("MALFORMED_FIGURE_OBLIGATION", f"{owner}: 'figure' missing {missing[0]!r}")
    unknown = [key for key in raw if key not in _FIGURE_ALLOWED]
    if unknown:
        raise Refused(
            "MALFORMED_FIGURE_OBLIGATION", f"{owner}: 'figure' carries unknown key {unknown[0]!r}"
        )

    components_from = raw.get("components_from")
    if components_from is not None:
        if not isinstance(components_from, str):
            raise Refused(
                "MALFORMED_FIGURE_OBLIGATION", f"{owner}: 'figure.components_from' must be a string"
            )
        paper_vocabulary.validate_fact(components_from)

    for bool_key in ("ordered", "caption_enumerates", "caption_decodes", "mandatory"):
        if not isinstance(raw[bool_key], bool):
            raise Refused(
                "MALFORMED_FIGURE_OBLIGATION", f"{owner}: 'figure.{bool_key}' must be a boolean"
            )

    excludes = raw["excludes"]
    if not isinstance(excludes, list) or not all(isinstance(item, str) for item in excludes):
        raise Refused(
            "MALFORMED_FIGURE_OBLIGATION", f"{owner}: 'figure.excludes' must be a list of strings"
        )

    return {
        "components_from": components_from,
        "ordered": raw["ordered"],
        "excludes": list(excludes),
        "caption_enumerates": raw["caption_enumerates"],
        "caption_decodes": raw["caption_decodes"],
        "mandatory": raw["mandatory"],
    }


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

    # `raw.get("mode") is not None` rather than `"mode" in raw`: this
    # function's own OWN output round-trips through re-serialization in
    # `paper_graph.py`'s corpus assembly and this suite's own fixtures
    # (`header.blocks` already carries a `"mode": None` key for every block
    # that declared none), so an explicit JSON `null` MUST mean the same
    # thing as the key being absent -- never a `MALFORMED_HEADER` a
    # round-trip would otherwise manufacture out of this parser's own
    # output shape.
    block_mode = None
    if raw.get("mode") is not None:
        block_mode = _validate_mode_object(raw["mode"], f"{section}.{block_id}")

    # Same `raw.get(...) is not None` convention as `mode` above: this
    # function's own output round-trips through re-serialization elsewhere
    # (`paper_graph.py`'s corpus assembly), so an explicit JSON `null` MUST
    # mean the same thing as the key being absent.
    block_figure = None
    if raw.get("figure") is not None:
        block_figure = _parse_figure(raw["figure"], f"{section}.{block_id}")

    return {
        "id": block_id,
        "requires_facts": list(facts),
        "requires_declarations": list(declarations),
        "citations": citations,
        "optional": optional,
        "after": block_after,
        "mode": block_mode,
        "figure": block_figure,
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

    section_mode = None
    if header.get("mode") is not None:
        section_mode = _validate_mode_object(header["mode"], section)

    return ContractHeader(
        section=section, position=position, after=after, blocks=blocks, mode=section_mode
    )


def resolve_mode(header: ContractHeader, block: dict) -> dict | None:
    """A block's own `mode` wins; the section-level `mode` is the default;
    `None` when neither declares one (`section-contract` spec, `Requirement:
    Front Matter Schema`, scenarios "A block inherits the section-level
    mode" / "A block's own mode overrides the section-level default";
    `Requirement: Headers Written Before mode Existed` for the `None` case —
    `write`'s own readiness stage is what refuses on `None`, never this
    reader)."""
    block_mode = block.get("mode")
    if block_mode is not None:
        return block_mode
    return header.mode


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


def _atomic_replace(path: Path, data: bytes) -> None:
    """Write `data` to `path` via a same-directory temp file + `os.replace`
    (the same shape `paper_block.py`'s own `_atomic_replace` uses): a
    process interrupted mid-write never leaves `path` torn.
    """
    directory = path.parent
    fd, tmp_name = tempfile.mkstemp(dir=str(directory), prefix=path.name + ".")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def install_header(path: Path, header: dict) -> dict:
    """Insert `header` as a `---`-fenced JSON front matter above `path`'s
    existing bytes, one-shot and idempotent (design.md, `Header insertion
    into the ten shipped files`).

    Refuses `HEADER_PRESENT` (work-state) when `path` already opens with a
    `---` fence -- this is what makes a second run refuse rather than
    double-write. Refuses `BODY_MUTATED` (work-state) when the post-write
    re-read does not carry the pre-write bytes, byte-for-byte, below the new
    header -- and restores the original bytes first, by inverse patch
    confirmed by content digest, never `git checkout --` (sdd-apply's own
    hard rule: undo a mutation by proving the restore, not by trusting a
    tool that cannot tell this write from any other).
    """
    # Validated BEFORE anything is read from or written to `path`: a
    # malformed header must never reach disk, not even the disk of a file
    # that turns out to already carry one. `parse_header`'s own refusals
    # (`MALFORMED_HEADER`, `UNKNOWN_FACT`, `UNKNOWN_DECLARATION`,
    # `UNKNOWN_CITATIONS_REGIME`) propagate unchanged.
    parse_header(header)

    pre = path.read_bytes()
    if pre.startswith(b"---\n") or pre.startswith(b"---\r\n"):
        raise Refused("HEADER_PRESENT", f"{path} already opens with a '---' front-matter fence")
    pre_digest = hashlib.sha256(pre).hexdigest()

    header_bytes = b"---\n" + json.dumps(header, indent=2).encode("utf-8") + b"\n---\n"
    candidate = header_bytes + pre

    _atomic_replace(path, candidate)
    post = path.read_bytes()

    body = post[len(header_bytes):]
    body_ok = post[:len(header_bytes)] == header_bytes
    post_body_digest = hashlib.sha256(body).hexdigest() if body_ok else None

    if not body_ok or post_body_digest != pre_digest:
        _atomic_replace(path, pre)
        restored = path.read_bytes()
        if restored != pre:
            raise Refused(
                "BODY_MUTATED",
                f"{path}: body below the inserted header did not match the pre-write digest, "
                "AND the restore itself did not reproduce the original bytes -- manual recovery required",
            )
        raise Refused(
            "BODY_MUTATED",
            f"{path}: body below the inserted header did not match the pre-write digest "
            f"(expected sha256={pre_digest}); original bytes restored",
        )

    return {"path": str(path), "header_bytes": len(header_bytes), "body_digest": pre_digest}


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
