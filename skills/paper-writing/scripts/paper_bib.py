"""paper_bib: `paper/refs.bib` built exclusively from cached, resolved
metadata, so "never hand-typed" is a checked property rather than a claim
(`no-claim-without-a-source-that-holds-it`, `sourced-bibliography` spec).

`entry_from_record` is the SOLE entry producer -- no function or CLI flag
anywhere in this skill accepts caller-composed entry text. Handing this
module a finished entry would replace a human typing with a model typing
and degrade "never hand-typed" from a checked property to a claim
(`design.md`, Decision 4).

Public surface:

    entry_from_record(paper_dir, record) -> dict           (raises ENTRY_UNSOURCED)
    build_refs_bib(paper_dir, records)   -> dict            (rebuilds refs.bib whole, sorted)
    cited_keys(main_tex_bytes)           -> set[str]
    entry_keys(refs_bib_bytes)           -> set[str]
    check_reciprocal(main_tex_bytes, refs_bib_bytes) -> dict (raises CITE_WITHOUT_ENTRY / ENTRY_WITHOUT_CITE)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_resolve  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

_CITE_RE = re.compile(r"\\cite\{([^}]*)\}")
_BIB_ENTRY_RE = re.compile(r"@\w+\{([^,]+),")


def entry_from_record(paper_dir: Path, record: dict) -> dict:
    """The sole `refs.bib` entry producer. Reads the cached metadata blob
    keyed by `record['metadata_digest']` (`paper_resolve.read_cached_metadata`)
    and requires the cache's OWN recorded digest to agree with the lookup
    key -- a self-consistency check, not a network call, so this refuses
    correctly with the `OPENER` never installed.

    Refuses `ENTRY_UNSOURCED` (work-state) when `record` carries no
    `resolver`/`metadata_digest` at all (a hand-composed entry, or one from
    an `insufficient` verdict, never has both), when no cached blob exists
    for that digest, or when the cached blob's own digest field does not
    match the key it was looked up by.
    """
    cite_key = record.get("cite_key") or "<unknown>"
    digest = record.get("metadata_digest") or ""
    resolver = record.get("resolver") or ""
    if not digest or not resolver:
        raise Refused(
            "ENTRY_UNSOURCED",
            f"{cite_key!r}: no resolver/metadata_digest recorded -- this entry was never resolved",
        )
    cached = paper_resolve.read_cached_metadata(paper_dir, digest)
    if cached is None:
        raise Refused(
            "ENTRY_UNSOURCED", f"{cite_key!r}: no cached metadata found for digest {digest!r}"
        )
    if cached.get("metadata_digest") != digest:
        raise Refused(
            "ENTRY_UNSOURCED",
            f"{cite_key!r}: the cached blob's own digest does not match the digest it was looked up by",
        )
    return {
        "cite_key": cite_key,
        "title": cached.get("title"),
        "doi": cached.get("doi"),
        "year": cached.get("year"),
        "resolver": resolver,
        "metadata_digest": digest,
    }


def _entry_text(entry: dict) -> str:
    lines = [f"@misc{{{entry['cite_key']},"]
    if entry.get("title"):
        lines.append(f"  title = {{{entry['title']}}},")
    if entry.get("doi"):
        lines.append(f"  doi = {{{entry['doi']}}},")
    if entry.get("year") is not None:
        lines.append(f"  year = {{{entry['year']}}},")
    lines.append(f"  note = {{resolver={entry['resolver']}; metadata_digest={entry['metadata_digest']}}},")
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_refs_bib(paper_dir: Path, records: list[dict]) -> dict:
    """Rebuilds `paper/refs.bib` WHOLE, sorted by cite key -- never appended
    in place (`design.md`, Decision 4). One entry per distinct `cite_key`
    among `records` (last-write-wins per key, oldest to newest). Every
    entry is checked via `entry_from_record` BEFORE a single byte is
    written, so one unsourced record refuses the whole rebuild rather than
    leaving a partially-written file behind.
    """
    by_key: dict[str, dict] = {}
    for record in records:
        cite_key = record.get("cite_key")
        if cite_key:
            by_key[cite_key] = record
    entries = [entry_from_record(paper_dir, by_key[key]) for key in sorted(by_key)]
    text = "".join(_entry_text(entry) for entry in entries)
    refs_path = paper_dir / "refs.bib"
    refs_path.write_text(text, encoding="utf-8")
    return {"path": str(refs_path), "entries": [entry["cite_key"] for entry in entries]}


def cited_keys(main_tex_bytes: bytes) -> set[str]:
    text = main_tex_bytes.decode("utf-8", errors="replace")
    keys: set[str] = set()
    for match in _CITE_RE.finditer(text):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def entry_keys(refs_bib_bytes: bytes) -> set[str]:
    text = refs_bib_bytes.decode("utf-8", errors="replace")
    return {match.group(1).strip() for match in _BIB_ENTRY_RE.finditer(text)}


def check_reciprocal(main_tex_bytes: bytes, refs_bib_bytes: bytes) -> dict:
    """`sourced-bibliography`, Requirement: Reciprocal Citation/Entry
    Checks. Each direction fires independently: a `\\cite{}` with no
    matching entry refuses `CITE_WITHOUT_ENTRY` naming every missing key,
    checked first; an entry never cited refuses `ENTRY_WITHOUT_CITE` naming
    every unused key, checked only once the first direction is clean -- so
    a fixture exercising only one direction never sees the other's code."""
    cited = cited_keys(main_tex_bytes)
    entries = entry_keys(refs_bib_bytes)
    missing_entries = sorted(cited - entries)
    if missing_entries:
        raise Refused(
            "CITE_WITHOUT_ENTRY", f"cited but no matching refs.bib entry: {missing_entries}"
        )
    unused_entries = sorted(entries - cited)
    if unused_entries:
        raise Refused("ENTRY_WITHOUT_CITE", f"refs.bib entries never cited: {unused_entries}")
    return {"cited": sorted(cited), "entries": sorted(entries)}
