"""paper_declarations: the `declarations` region — operator-supplied
declarations and fact resolutions, collected progressively, fixed once
recorded, reopened only by name.

Two record kinds, `declaration` (six operator-input ids, field `value`) and
`fact` (ten fact ids, field `resolution`) — deliberately different field
names, so the two vocabularies can never share a code path by accident
(design.md, `JSON region bodies, comment-prefixed, canonically serialized`:
"a shared field name invites a shared code path, and a shared code path is
exactly how a closed vocabulary gets opened by accident").

Neither `NOT_A_DECLARATION` nor `NOT_A_FACT` exists as a code of its own:
`paper_vocabulary.validate_declaration` / `validate_fact` are called
directly, so the SAME `UNKNOWN_DECLARATION` / `UNKNOWN_FACT` codes Phase 2
already raises for a header value fire here too (design.md, `Refusal codes
and their classification`: "two codes for one condition is the drift this
repository's roster exists to prevent").

Public surface:

    OBSERVABLE_FACTS / DERIVED_FACTS / STRUCTURAL_FACTS  -> the ten facts,
        partitioned (design.md, `A fact the agent may observe is a
        partition, not a guideline`)
    set_declaration(paper_dir, id, value, *, clock=...) -> dict
    set_fact(paper_dir, id, resolution, *, clock=...)    -> dict
    reopen(paper_dir, id, *, clock=...)                  -> dict
    affected_blocks(corpus, id)  -> set[str]  (pure; the reopen scan)
    validate_observation_report(report) -> None  (raises NOT_AN_OBSERVABLE_FACT,
                                                     EVIDENCE_CONFLATED)
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_block  # noqa: E402
import paper_region  # noqa: E402
import paper_vocabulary  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: The five facts an outside observer (`insumos-observer`) may report on —
#: read from `proposals/`, `experiments/`, or the target implementation
#: repository. Held by exact equality against `paper_vocabulary.FACTS`
#: below, so a fact Phase 2 ever adds goes red here until somebody
#: classifies it (design.md, `A fact the agent may observe is a partition,
#: not a guideline`).
OBSERVABLE_FACTS: tuple[str, ...] = (
    "formulation",
    "dataset",
    "experimental-design",
    "implementation",
    "results",
)

#: Facts the agent reports the MATERIAL for, never the derivation itself.
DERIVED_FACTS: tuple[str, ...] = (
    "contributions",
    "problem-statement",
    "gap",
    "limitations",
)

#: A decision, not an observation.
STRUCTURAL_FACTS: tuple[str, ...] = ("skeleton",)

assert set(OBSERVABLE_FACTS) | set(DERIVED_FACTS) | set(STRUCTURAL_FACTS) == set(
    paper_vocabulary.FACTS
), "the partition drifted from paper_vocabulary.FACTS"
assert (
    set(OBSERVABLE_FACTS).isdisjoint(DERIVED_FACTS)
    and set(OBSERVABLE_FACTS).isdisjoint(STRUCTURAL_FACTS)
    and set(DERIVED_FACTS).isdisjoint(STRUCTURAL_FACTS)
), "the three fact classes must be pairwise disjoint"

_DEFAULT_BODY = {"generation": 0, "records": []}


def _atomic_replace(path: Path, data: bytes) -> None:
    """Same shape `paper_block.py`'s and `paper_contract.py`'s own
    `_atomic_replace` use: a same-directory temp file + `os.replace`, so a
    process interrupted mid-write never leaves `path` torn."""
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


def _read_declarations(paper_dir: Path) -> tuple[Path, bytes, dict | None]:
    tex_path = paper_block.resolve_main_tex(paper_dir)
    pre = tex_path.read_bytes()
    record = paper_region.read_region(pre, "declarations")
    return tex_path, pre, record


def _verify_not_hand_edited(record: dict | None) -> None:
    """Refuses `DECLARATIONS_HAND_EDITED` (work-state) when the region's
    on-disk body no longer matches the digest its own begin marker
    recorded. There is no `--adopt` path for this region — a declarations
    record is a decision the machine reads back as authority, and adopting
    a hand edit would launder an unreviewed change into "what was decided"
    (design.md, `The digest covers the region body, and a mismatch never
    heals itself`).
    """
    if record is None:
        return
    actual = paper_region.current_digest(record["body_bytes"])
    if actual != record["digest"]:
        raise Refused(
            "DECLARATIONS_HAND_EDITED",
            f"expected sha256={record['digest']}, found sha256={actual}",
        )


def _body_or_default(record: dict | None) -> dict:
    if record is None:
        return {"generation": 0, "records": []}
    return record["body"]


def _find_record(body: dict, kind: str, id_: str) -> dict | None:
    for entry in body["records"]:
        if entry["kind"] == kind and entry["id"] == id_:
            return entry
    return None


def _write_declarations(paper_dir: Path, pre: bytes, record: dict | None, new_body: dict) -> None:
    region_bytes, _digest = paper_region.build_region_bytes("declarations", new_body)
    existing_span = (
        {"begin_start": record["begin_start"], "end_end": record["end_end"]}
        if record is not None
        else None
    )
    candidate = paper_region.replace_or_append(pre, "declarations", region_bytes, existing_span)
    tex_path = paper_block.resolve_main_tex(paper_dir)
    _atomic_replace(tex_path, candidate)


def _set_record(
    paper_dir: Path, *, kind: str, id_: str, value_field: str, value: str, clock,
) -> dict:
    tex_path, pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    existing = _find_record(body, kind, id_)
    if existing is not None and existing.get("fixed"):
        raise Refused(
            "DECLARATION_FIXED",
            f"{id_!r} is already fixed at {value_field}={existing.get(value_field)!r}; "
            "use --reopen to clear it first",
        )
    new_records = [
        entry for entry in body["records"] if not (entry["kind"] == kind and entry["id"] == id_)
    ]
    new_records.append(
        {"kind": kind, "id": id_, value_field: value, "fixed": True, "recorded": clock()}
    )
    new_body = {"generation": body.get("generation", 0) + 1, "records": new_records}
    _write_declarations(paper_dir, pre, record, new_body)
    return {"id": id_, "kind": kind, value_field: value, "generation": new_body["generation"]}


def set_declaration(
    paper_dir: Path, declaration_id: str, value: str, *, clock=paper_region.default_clock,
) -> dict:
    """Records `declaration_id` as a `declaration` record, field `value`.

    Refuses `UNKNOWN_DECLARATION` (Phase 2's own code, reused verbatim —
    `paper_vocabulary.validate_declaration`) when `declaration_id` is a fact
    id rather than one of the six declared declarations. Refuses
    `DECLARATION_FIXED` when it was already recorded and `--reopen` was not
    run first.
    """
    paper_vocabulary.validate_declaration(declaration_id)
    return _set_record(
        paper_dir, kind="declaration", id_=declaration_id, value_field="value", value=value,
        clock=clock,
    )


def set_fact(
    paper_dir: Path, fact_id: str, resolution: str, *, clock=paper_region.default_clock,
) -> dict:
    """Records `fact_id` as a `fact` record, field `resolution`.

    Refuses `UNKNOWN_FACT` (Phase 2's own code, reused verbatim —
    `paper_vocabulary.validate_fact`) when `fact_id` is a declaration id
    rather than one of the ten declared facts. Refuses `DECLARATION_FIXED`
    when it was already recorded and `--reopen` was not run first.
    """
    paper_vocabulary.validate_fact(fact_id)
    return _set_record(
        paper_dir, kind="fact", id_=fact_id, value_field="resolution", value=resolution,
        clock=clock,
    )


def reopen(paper_dir: Path, id_: str, *, clock=paper_region.default_clock) -> dict:
    """Clears the `fixed` state for exactly the record named `id_`, and no
    other, then bumps the region's own `generation` counter.

    Refuses `UNKNOWN_DECLARATION` when `id_` is neither a declared fact nor
    a declared declaration id. Reopening an id with no existing record is
    harmless — there is nothing to clear, and the generation still bumps,
    matching `declare`'s own "every write bumps generation" rule.
    """
    if id_ in paper_vocabulary.FACTS:
        kind = "fact"
    elif id_ in paper_vocabulary.DECLARATIONS:
        kind = "declaration"
    else:
        raise Refused(
            "UNKNOWN_DECLARATION", f"{id_!r} is not one of the declared facts or declarations"
        )

    tex_path, pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    new_records = []
    for entry in body["records"]:
        if entry["kind"] == kind and entry["id"] == id_:
            entry = dict(entry)
            entry["fixed"] = False
        new_records.append(entry)
    new_body = {"generation": body.get("generation", 0) + 1, "records": new_records}
    _write_declarations(paper_dir, pre, record, new_body)
    return {"id": id_, "kind": kind, "generation": new_body["generation"]}


def affected_blocks(corpus, target_id: str) -> set:
    """Every qualified block id (`paper_graph.Corpus.blocks` key) whose
    parsed contract's `requires_facts` or `requires_declarations` names
    `target_id`. Pure — touches no region, no disk; this is the whole
    "reopen scan" (design.md, `Reopening Invalidates Exactly the Blocks
    That Named It`), reused by `plan` (Slice C2) to report staleness and by
    `declare --reopen` to report what it just invalidated.
    """
    return {
        qualified_id
        for qualified_id, block in corpus.blocks.items()
        if target_id in block.requires_facts or target_id in block.requires_declarations
    }


def validate_observation_report(report: dict) -> None:
    """Validates an `insumos-observer` fact-satisfaction report:
    `{fact_id: {"satisfied": bool, "evidence": [[path, quote], ...]}}`.

    Refuses `NOT_AN_OBSERVABLE_FACT` (invocation-defect) for any key
    outside `OBSERVABLE_FACTS` — detectable even if the agent invents an
    id, since it was never handed the other five. Refuses
    `EVIDENCE_CONFLATED` (invocation-defect) when `implementation` and
    `results` are both satisfied by evidence citing the exact same file
    path: a source file can prove code exists, never that it ran, so
    requiring distinct evidence is what makes the conflation visible
    rather than merely asked-against (design.md, `A fact the agent may
    observe is a partition, not a guideline`).
    """
    for fact_id in report:
        if fact_id not in OBSERVABLE_FACTS:
            raise Refused(
                "NOT_AN_OBSERVABLE_FACT",
                f"{fact_id!r} is not one of the observable facts {OBSERVABLE_FACTS}",
            )

    def _paths(fact_id: str) -> set:
        entry = report.get(fact_id) or {}
        if not entry.get("satisfied"):
            return set()
        return {path for path, _quote in entry.get("evidence", [])}

    implementation_paths = _paths("implementation")
    results_paths = _paths("results")
    overlap = implementation_paths & results_paths
    if overlap:
        raise Refused(
            "EVIDENCE_CONFLATED",
            f"'implementation' and 'results' are both satisfied by the same "
            f"evidence path(s) {sorted(overlap)}; a source file can prove code "
            "exists, never that it ran",
        )
