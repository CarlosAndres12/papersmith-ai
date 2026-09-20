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
    set_fact(paper_dir, id, resolution, *, clock=..., produced_by=()) -> dict
    decline_fact(paper_dir, id, reason, condition, *, clock=..., produced_by=()) -> dict
    bind_section(paper_dir, qualified_block_id, fact_id, lineage, sections, *, clock=...)
        -> dict  (the-requirement-names-the-section-that-feeds-it, U3e: a THIRD
        record kind, `binding`, keyed by (block, fact) -- the verb that RECORDS
        a `source-section-binding`, in `paper/`, never `sections/*.md`)
    reopen_binding(paper_dir, qualified_block_id, fact_id, *, clock=...) -> dict
    read_bindings(paper_dir) -> dict  (read-only; qualified_block_id ->
        {fact_id: {"lineage": str, "sections": tuple}}; {} before paper/ exists)
    describe_binding_candidates(status, root) -> dict  (pure disk read; every
        lineage a document-rooted or ingested-identity root carries RIGHT NOW,
        its own current revision/paper, and the section titles read from it --
        what `write`'s own SECTION_BINDING_ABSENT refusal shows an operator)
    read_fact(paper_dir, id) -> str | None  (read-only; None when unresolved)
    read_declined(paper_dir) -> dict[str, dict]  (read-only;
        {fact_id: {"reason", "condition", "holds", "detail"}}, condition
        re-evaluated fresh from disk on every call)
    read_satisfied(paper_dir) -> (set[str], set[str])  (read-only; fixed facts, fixed declarations)
    reopen(paper_dir, id, *, clock=...)                  -> dict
    affected_blocks(corpus, id)  -> set[str]  (pure; the reopen scan)
    infer_related_work(corpus, opened_ids) -> bool  (pure; skeleton inference)
    dataset_placement_candidates(corpus) -> dict  (pure; section -> qualified id;
        raises DATASET_PLACEMENT_CANDIDATE_ABSENT, DATASET_PLACEMENT_CANDIDATE_AMBIGUOUS)
    infer_dataset_placement(corpus, opened_ids) -> str  (pure; raises DATASET_PLACEMENT_CONFLICT
        and whatever dataset_placement_candidates raises)
    infer_skeleton_decisions(paper_dir, corpus) -> dict  (read-only; disk, never a stored flag)
    validate_observation_report(report) -> None  (raises NOT_AN_OBSERVABLE_FACT,
                                                     EVIDENCE_CONFLATED)
    FACT_SOURCE_ROOT -> dict[str, SourceRoot]  (fact id -> the root it is read from,
        AND that root's kind -- PROSE (a document revision, section-bindable),
        REPOSITORY (a target code repository, measured by running it), or
        INGESTED (a published paper under guidance/, identity-resolved))
    resolve_ingested_document(evidence_dir, lineage) -> Path  (pure disk read;
        the INGESTED-kind counterpart to resolve_lineage above)
    source_available(root) -> bool  (pure disk measurement; gitignore-blind, `Path.iterdir()`)
    reconcile_observation_report(report, measured) -> list[dict]  (pure; every
        disagreement between the agent's account and a real disk measurement)
"""
from __future__ import annotations

import enum
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_block  # noqa: E402
import paper_guidance  # noqa: E402
import paper_region  # noqa: E402
import paper_vocabulary  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402
import impl_layout  # noqa: E402

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
    extra: dict | None = None,
) -> dict:
    tex_path, pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    existing = _find_record(body, kind, id_)
    if existing is not None and existing.get("fixed"):
        if existing.get("declined"):
            raise Refused(
                "DECLARATION_FIXED",
                f"{id_!r} is declined (reason={existing.get('reason')!r}); "
                "use --reopen to clear it before resolving",
            )
        raise Refused(
            "DECLARATION_FIXED",
            f"{id_!r} is already fixed at {value_field}={existing.get(value_field)!r}; "
            "use --reopen to clear it first",
        )
    new_generation = body.get("generation", 0) + 1
    new_records = [
        entry for entry in body["records"] if not (entry["kind"] == kind and entry["id"] == id_)
    ]
    new_records.append(
        {
            "kind": kind, "id": id_, value_field: value, "fixed": True, "recorded": clock(),
            "generation": new_generation,
            **(extra or {}),
        }
    )
    new_body = {"generation": new_generation, "records": new_records}
    _write_declarations(paper_dir, pre, record, new_body)
    return {
        "id": id_, "kind": kind, value_field: value, "generation": new_body["generation"],
        **(extra or {}),
    }


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


def _refuse_if_produced(fact_id: str, produced_by: tuple) -> None:
    """Refuses `PRODUCED_FACT_UNDECLARABLE` (work-state) naming `fact_id`
    and its producing block(s), when `produced_by` is non-empty
    (`fact-production` spec: a fact whose producer is a block is never
    declared through this region — its satisfaction is read from that
    producer's own written status, never authored twice). Shared by
    `set_fact`/`decline_fact` so the refusal is enforced IN THE MODULE
    (design.md, Decision E) — the same precedent `decline_fact`'s own
    `DECLINE_REASON_REQUIRED` set, so no caller of either function can ever
    escape it by skipping a CLI-layer check."""
    if produced_by:
        raise Refused(
            "PRODUCED_FACT_UNDECLARABLE",
            f"{fact_id!r} is produced by {list(produced_by)!r}; its satisfaction is read "
            "from that producer's own written status, never declared",
        )


def set_fact(
    paper_dir: Path, fact_id: str, resolution: str, *, clock=paper_region.default_clock,
    produced_by: tuple = (),
) -> dict:
    """Records `fact_id` as a `fact` record, field `resolution`.

    Refuses `UNKNOWN_FACT` (Phase 2's own code, reused verbatim —
    `paper_vocabulary.validate_fact`) when `fact_id` is a declaration id
    rather than one of the ten declared facts. Refuses `DECLARATION_FIXED`
    when it was already recorded and `--reopen` was not run first.

    `produced_by` (`a-fact-is-declared-or-it-is-produced`, tasks.md Unit 3,
    3.2): a tuple of qualified block ids naming `fact_id`'s producer(s)
    (`paper_graph.producers_by_fact`, resolved by the caller — this module
    never assembles a corpus itself). Non-empty refuses
    `PRODUCED_FACT_UNDECLARABLE` via `_refuse_if_produced`, before the
    record is ever read or written. Defaults to `()`, so every existing
    caller — declaring one of the five externally-sourced observable facts
    — is unaffected.
    """
    paper_vocabulary.validate_fact(fact_id)
    _refuse_if_produced(fact_id, produced_by)
    return _set_record(
        paper_dir, kind="fact", id_=fact_id, value_field="resolution", value=resolution,
        clock=clock,
    )


def _validate_condition_shape(condition, root: Path) -> None:
    """Write-time structural validation only -- never evaluates whether the
    condition currently HOLDS (that is `_evaluate_condition`'s job, called
    only from `read_declined`, never from here)."""
    if not isinstance(condition, dict):
        raise Refused("CONDITION_MALFORMED", f"condition must be a JSON object, got {condition!r}")
    paper_vocabulary.validate_condition_type(condition.get("type"))
    if condition["type"] == "directory-empty-except":
        path = condition.get("path")
        if not isinstance(path, str) or not path:
            raise Refused(
                "CONDITION_MALFORMED",
                "'directory-empty-except' requires a non-empty string 'path'",
            )
        ignore = condition.get("ignore", [])
        if not isinstance(ignore, list) or not all(isinstance(x, str) for x in ignore):
            raise Refused("CONDITION_MALFORMED", "'ignore' must be a JSON array of strings")
        resolved = (root / path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            raise Refused(
                "CONDITION_MALFORMED", f"condition path {path!r} resolves outside {root}"
            )


def _evaluate_condition(root: Path, condition: dict) -> tuple:
    """Read-time truth check, fresh from disk every call -- never cached.
    Returns (holds, detail); `holds=False` is what `read_declined` reports
    as a lapsed (`stale`) decline."""
    paper_vocabulary.validate_condition_type(condition.get("type"))
    if condition["type"] == "directory-empty-except":
        path = root / condition["path"]
        ignore = set(condition.get("ignore", []))
        if not path.exists():
            return True, f"{condition['path']} does not exist"
        if not path.is_dir():
            return False, f"{condition['path']} exists and is not a directory"
        extra = sorted({p.name for p in path.iterdir()} - ignore)
        if extra:
            return False, f"{condition['path']} contains unexpected entries: {extra}"
        return True, f"{condition['path']} contains nothing beyond {sorted(ignore)}"
    raise AssertionError("unreachable: validate_condition_type already closed this")


def decline_fact(
    paper_dir: Path, fact_id: str, reason: str, condition: dict | None,
    *, clock=paper_region.default_clock, produced_by: tuple = (),
) -> dict:
    """Records `fact_id` as DECLINED — the operator has decided this fact does
    not enter the paper for now (e.g. no measurement protocol exists yet),
    as distinct from "not yet measured". A decline is a first-class record
    kind stored through the exact same `declarations` region and the exact
    same private readers/writers `set_fact`/`reopen` already use — never a
    second store. `readiness`/`phases` report a block whose only missing
    facts are declined ones as `declined`, not `blocked`, naming the fact
    and this reason.

    Refuses `UNKNOWN_FACT` when `fact_id` is not one of the ten declared
    facts (same code `set_fact` already raises — reused, not duplicated).
    Refuses `DECLARATION_FIXED` when the fact is already resolved OR already
    declined — `--reopen` clears either state identically before it can be
    re-declared or re-declined.
    Refuses `DECLINE_REASON_REQUIRED` (new; INVOCATION_DEFECT) when `reason`
    is empty or all whitespace: a decline with no reason is indistinguishable
    from an omission six months later, which is the defect this state exists
    to remove. Enforced here, in the module itself, not only at the CLI
    layer, so any caller — not just `declare --decline` — is held to it.

    `condition` is MANDATORY and is what makes a decline expire rather than
    stand forever on a human's memory. It is a JSON object of the shape
    `paper_vocabulary.CONDITION_TYPES` closes over, stored verbatim in the
    record and re-evaluated fresh from disk by `read_declined` on every
    call — never cached as a boolean, never evaluated here at write time
    (whether the condition currently holds is a `read_declined`/readiness
    concern, not a decline-time gate: you can decline for a condition that
    happens to already be false, and the very next `readiness`/`phases`
    call will correctly report it `stale` rather than `declined`).

    Refuses `CONDITION_REQUIRED` (invocation-defect) when `condition` is
    `None`. Refuses `CONDITION_MALFORMED` (work-state — same classification
    family as this skill's other MALFORMED_* codes) when it is not a JSON
    object, is missing a type-required field, or names a `path` that
    resolves outside `paper_dir`'s own parent directory. Refuses
    `UNKNOWN_CONDITION_TYPE` (work-state) when `condition["type"]` is
    outside the closed vocabulary.

    `produced_by` (`a-fact-is-declared-or-it-is-produced`, tasks.md Unit 3,
    3.2): the same producer tuple `set_fact` accepts, checked FIRST — a
    produced fact can never be declined either, regardless of whether
    `reason`/`condition` would otherwise be valid (`_refuse_if_produced`).
    Defaults to `()`, unaffecting every existing caller.

    No new `forge_root` parameter anywhere — `condition["path"]` is
    resolved relative to `paper_dir.parent`, which is the repository root
    under this skill's own default layout (`<repo>/paper`) and under every
    existing test fixture's own convention (`self.paper_dir = self.forge_root
    / "paper"`) — a deliberate, stated scope decision, not a hidden
    assumption: a fixture that wants an `experiments/` directory just
    creates `self.forge_root / "experiments"` and it is picked up with zero
    extra plumbing.
    """
    paper_vocabulary.validate_fact(fact_id)
    _refuse_if_produced(fact_id, produced_by)
    if not reason or not reason.strip():
        raise Refused(
            "DECLINE_REASON_REQUIRED",
            "declining a fact requires a non-empty --reason; an undocumented "
            "decline is indistinguishable from an omission later",
        )
    if condition is None:
        raise Refused(
            "CONDITION_REQUIRED",
            "declining a fact requires a --condition JSON object the skill can "
            "re-evaluate from disk on every later read; a decline with no "
            "re-checkable condition never expires",
        )
    _validate_condition_shape(condition, paper_dir.parent)
    return _set_record(
        paper_dir, kind="fact", id_=fact_id, value_field="reason", value=reason,
        clock=clock, extra={"declined": True, "condition": condition},
    )


def read_fact(paper_dir: Path, fact_id: str) -> str | None:
    """Read-only: the currently FIXED resolution string for `fact_id`, or
    `None` when it was never declared, or was reopened and not yet
    redeclared (`entry["fixed"]` false). Reuses the exact same private
    readers `set_fact`/`reopen` already call (`_read_declarations`,
    `_verify_not_hand_edited`, `_body_or_default`, `_find_record`) — the
    "existing declaration-record reader" every other reader of this region
    already goes through, never a second implementation of the same read.

    Added for `a-diagram-that-compiles-or-says-why`'s corrective amendment:
    `paper_cli._check_obligations` calls this to derive a Components
    Check's expected list from `components_from`'s named fact, rather than
    from an operator-supplied CLI flag. Raises no `Refused` of its own
    beyond `paper_vocabulary.validate_fact`'s `UNKNOWN_FACT` and
    `_verify_not_hand_edited`'s `DECLARATIONS_HAND_EDITED` — both already
    reachable through this module's other callers.
    """
    paper_vocabulary.validate_fact(fact_id)
    _tex_path, _pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    entry = _find_record(body, "fact", fact_id)
    if entry is None or not entry.get("fixed") or entry.get("declined"):
        return None
    return entry["resolution"]


def read_declined(paper_dir: Path) -> dict:
    """Read-only: every currently-declined fact id mapped to
    `{"reason": str, "condition": dict, "holds": bool, "detail": str}` --
    `condition` is re-evaluated fresh from disk on EVERY call via
    `_evaluate_condition`, never cached in the record itself and never
    memoized. `holds=True` means the decline's own justifying condition
    still holds (the readiness layer reports this fact `declined`);
    `holds=False` means it has LAPSED (the readiness layer reports this
    fact's block `stale`+`blocked`, never auto-satisfied and never
    silently ignored -- the operator decides what happens next, not this
    skill). A fact that was declined and then `reopen`ed is absent from
    this mapping entirely, matching `read_fact`/`read_satisfied`.

    The condition's own `path` is resolved relative to `paper_dir.parent`
    (the repository root under this skill's default layout) -- reused
    verbatim from what `decline_fact`/`_validate_condition_shape` already
    validated, never a second root.
    """
    _tex_path, _pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    root = paper_dir.parent
    result = {}
    for entry in body["records"]:
        if entry["kind"] == "fact" and entry.get("fixed") and entry.get("declined"):
            holds, detail = _evaluate_condition(root, entry["condition"])
            result[entry["id"]] = {
                "reason": entry["reason"], "condition": entry["condition"],
                "holds": holds, "detail": detail,
            }
    return result


def read_satisfied(paper_dir: Path) -> tuple[set, set]:
    """Read-only: every fact id and every declaration id currently FIXED in
    the `declarations` region, as two sets -- `(satisfied_facts,
    satisfied_declarations)`. This is the declaration-backed basis
    `cmd_readiness`/`phases` read (`the-phases-are-derived-not-remembered`,
    design.md D3, tasks.md 6.3): a bare `readiness` call used to compute its
    answer from CLI flags alone, never opening `main.tex`, so it never
    changed after `declare`.

    Reuses the exact same private readers `set_fact`/`reopen`/`read_fact`
    already go through (`_read_declarations`, `_verify_not_hand_edited`,
    `_body_or_default`) -- never a second region reader. Raises `PAPER_
    ABSENT` (via `_read_declarations` -> `paper_block.resolve_main_tex`)
    when `paper_dir` has no `main.tex`, and `DECLARATIONS_HAND_EDITED` (via
    `_verify_not_hand_edited`) when the region's own digest no longer
    matches -- both already reachable through this module's other callers,
    never a new code for either condition.
    """
    _tex_path, _pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    satisfied_facts = {
        entry["id"] for entry in body["records"]
        if entry["kind"] == "fact" and entry.get("fixed") and not entry.get("declined")
    }
    satisfied_declarations = {
        entry["id"] for entry in body["records"]
        if entry["kind"] == "declaration" and entry.get("fixed")
    }
    return satisfied_facts, satisfied_declarations


def _binding_record_id(qualified_block_id: str, fact_id: str) -> str:
    """The `binding` record's own composite id -- a (block, fact) PAIR,
    since one block may bind more than one fact and one fact may be bound
    by more than one block (the worked example this whole change exists
    for: `mm-borrowed-machinery` and `mm-proposal` both require
    `formulation` but bind different sections). Never a vocabulary member
    of `FACTS`/`DECLARATIONS` — `reopen`'s own dispatch is untouched by
    this; `reopen_binding` below is a dedicated function, not a widened
    `reopen`."""
    return f"{qualified_block_id}::{fact_id}"


def bind_section(
    paper_dir: Path, qualified_block_id: str, fact_id: str, lineage: str, sections,
    *, clock=paper_region.default_clock,
) -> dict:
    """Records ONE `binding` -- the `source-section-binding` half of a
    `requires_facts` entry, decided by USING the skill (`bind`), never by
    hand-editing `sections/*.md` (which ships with the forge and must stay
    byte-identical to `main`) and never by an agent reading conversation
    prose (`the-requirement-names-the-section-that-feeds-it`, U3e ruling,
    design.md Decision J). Stored in the SAME `declarations` region
    `set_fact`/`set_declaration` already write — `paper/`, never
    `sections/`: that region is gitignored except `.gitkeep`, and it
    already holds the paper's own decisions, protected by the SAME
    `DECLARATIONS_HAND_EDITED` guard, with no `--adopt` escape.

    A THIRD record kind, `binding` — deliberately not `fact`/`declaration`,
    so a binding can never silently satisfy a check meant for the other
    vocabulary (module docstring: "a shared field name invites a shared
    code path"). Keyed by `id={block}::{fact}` (`_binding_record_id`).
    `value_field="lineage"`; `sections` — a non-empty tuple of titles,
    normalized here so a single string is accepted exactly the way
    `paper_contract._validate_document_object`'s own `section` key already
    is — is carried in `extra`, alongside `block`/`fact` themselves, so
    `read_bindings` never has to re-derive them from the composite id.

    Refuses `UNKNOWN_FACT` (`paper_vocabulary.validate_fact`, reused
    verbatim) when `fact_id` is not one of the ten declared facts.
    Refuses `BINDING_FACT_NOT_BINDABLE` (new; work-state) when `fact_id`
    IS a declared fact but is not a key of `FACT_SOURCE_ROOT` (`is_
    bindable_fact`) — a produced or structural fact has no document-rooted
    source to bind at all (`source-section-binding` spec, `Requirement:
    Bindable Facts Are Derived, Never Listed`). Refuses `BINDING_LINEAGE_
    REQUIRED` / `BINDING_SECTIONS_REQUIRED` (new; invocation-defect) for an
    empty `lineage` / an empty `sections` — enforced HERE, in the module
    itself, not only at the CLI layer, the same precedent `decline_fact`'s
    own `DECLINE_REASON_REQUIRED` set. Refuses `DECLARATION_FIXED`
    (`_set_record`'s own guard, reused) when this exact (block, fact) pair
    is already recorded and `reopen_binding` was not run first.

    Raises nothing about `qualified_block_id`'s own shape or whether
    `fact_id` is really one of that block's `requires_facts` — that cross-
    check is the CALLER's concern (`paper_cli.cmd_bind`), which holds the
    real, assembled corpus this module never imports (`paper_graph`
    imports `paper_declarations`, so the reverse import would cycle); a
    binding naming a block or fact that turns out not to exist in the real
    corpus is simply orphaned data, harmless, the same tolerance `reopen`
    already extends to an id with no existing record.
    """
    paper_vocabulary.validate_fact(fact_id)
    if not is_bindable_fact(fact_id):
        raise Refused(
            "BINDING_FACT_NOT_BINDABLE",
            f"{fact_id!r} is not a key of FACT_SOURCE_ROOT; it has no document-rooted "
            "source to bind at all",
        )
    if not lineage:
        raise Refused(
            "BINDING_LINEAGE_REQUIRED", "recording a binding requires a non-empty lineage",
        )
    if isinstance(sections, str):
        sections = (sections,)
    sections = tuple(sections)
    if not sections:
        raise Refused(
            "BINDING_SECTIONS_REQUIRED", "recording a binding requires at least one section title",
        )
    binding_id = _binding_record_id(qualified_block_id, fact_id)
    return _set_record(
        paper_dir, kind="binding", id_=binding_id, value_field="lineage", value=lineage,
        clock=clock,
        extra={"block": qualified_block_id, "fact": fact_id, "sections": list(sections)},
    )


def reopen_binding(
    paper_dir: Path, qualified_block_id: str, fact_id: str, *, clock=paper_region.default_clock,
) -> dict:
    """Clears the `fixed` state for exactly the `binding` record naming
    `(qualified_block_id, fact_id)` — mirroring `reopen`'s own per-id
    clearing, as a DEDICATED function rather than a widened `reopen`,
    because a binding's own id is a (block, fact) PAIR, not a single
    vocabulary member `reopen`'s own `FACTS`/`DECLARATIONS` dispatch
    already closes over. Reopening a pair with no existing record is
    harmless, matching `reopen`'s own precedent — there is nothing to
    clear, and the region's own `generation` still bumps.
    """
    binding_id = _binding_record_id(qualified_block_id, fact_id)
    tex_path, pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    new_generation = body.get("generation", 0) + 1
    new_records = []
    for entry in body["records"]:
        if entry["kind"] == "binding" and entry["id"] == binding_id:
            entry = dict(entry)
            entry["fixed"] = False
            entry["generation"] = new_generation
        new_records.append(entry)
    new_body = {"generation": new_generation, "records": new_records}
    _write_declarations(paper_dir, pre, record, new_body)
    return {
        "id": binding_id, "kind": "binding", "block": qualified_block_id, "fact": fact_id,
        "generation": new_body["generation"],
    }


def read_bindings(paper_dir: Path) -> dict:
    """Read-only: every currently-FIXED `binding` record, as `qualified_
    block_id -> {fact_id: {"lineage": str, "sections": tuple}}` — the
    corpus's own read of what `bind` has recorded so far
    (`paper_graph.assemble_corpus`'s own merge, U3e).

    Returns `{}` when `paper_dir` (or `main.tex` under it) does not exist
    yet — a corpus is legitimately assemblable, read-only, before `paper/`
    is even scaffolded, the SAME tolerance `Corpus.undecided_bindings`
    already extends to every bindable fact carrying no binding at all;
    this is not `PAPER_ABSENT`'s concern, which is reserved for a verb
    that actually needs to WRITE `paper/` (`declare`, `bind` itself).
    Reuses the exact same private readers every other reader of this
    region already goes through (`_read_declarations`, `_verify_not_hand_
    edited`, `_body_or_default`) once `paper_dir` IS scaffolded — never a
    second reader, and `DECLARATIONS_HAND_EDITED` still refuses a
    tampered region exactly as it does for every other reader.
    """
    tex_path = paper_dir / "main.tex"
    if not paper_dir.is_dir() or not tex_path.is_file():
        return {}
    _tex_path, _pre, record = _read_declarations(paper_dir)
    _verify_not_hand_edited(record)
    body = _body_or_default(record)
    result: dict = {}
    for entry in body["records"]:
        if entry["kind"] == "binding" and entry.get("fixed"):
            result.setdefault(entry["block"], {})[entry["fact"]] = {
                "lineage": entry["lineage"], "sections": tuple(entry["sections"]),
            }
    return result


def _heading_titles(path: Path) -> list:
    """Every heading title `paper_guidance.segment_markdown` reads from
    `path` right now — the same read `_verify_source_section_bindings`
    already performs per resolved revision, reused here purely for
    reporting (`describe_binding_candidates`), never for resolution
    itself."""
    body = path.read_text(encoding="utf-8")
    outline = paper_guidance.segment_markdown(body)
    return [heading["title"] for heading in outline["headings"]]


def describe_binding_candidates(status: dict, root: SourceRoot) -> dict:
    """Every candidate an operator answering `write`'s own `SECTION_
    BINDING_ABSENT` refusal can see WITHOUT opening anything: `{lineage:
    {"revision": filename, "sections": [title, ...]}}`, read from disk at
    call time — nothing cached, nothing hand-listed (`the-requirement-
    names-the-section-that-feeds-it`, U3e ruling: "the refusal IS the
    question").

    `root.kind is INGESTED`: each ingested paper under `status['path']`
    (`paper_guidance.ingested_papers`, reused) is its own "lineage",
    identity-resolved — no ordinal to pick a "current" revision from.

    Otherwise (`PROSE`): `read_revisions_marker(status['path'])` — `None`
    (no marker yet; `SOURCE_REVISIONS_UNDECLARED` is a DIFFERENT check's
    concern, never raised here) falls back to reporting every `*.md` file
    under the root, ungrouped, by its own filename stem. A marker present
    derives the SAME per-root regex `resolve_lineage` composes, but
    matches every filename that fits it (never one literal lineage,
    generalizing `resolve_lineage`'s per-lineage regex into one that
    admits ANY lineage segment) and keeps only the highest-ordinal file
    per distinct lineage segment found — the current revision, per
    lineage, exactly as `resolve_lineage` would resolve it, for every
    lineage this root actually carries right now.
    """
    base_path = status["path"]
    if root.kind is SourceRootKind.INGESTED:
        papers = paper_guidance.ingested_papers(base_path.parent).get(base_path.name, [])
        return {
            entry["folder"]: {
                "revision": Path(entry["markdown"]).name,
                "sections": _heading_titles(Path(entry["markdown"])),
            }
            for entry in papers
        }

    marker = read_revisions_marker(base_path)
    if marker is None:
        return {
            doc_path.stem: {"revision": doc_path.name, "sections": _heading_titles(doc_path)}
            for doc_path in sorted(base_path.glob("*.md"))
        }

    marker_prefix = marker["revision_prefix"]
    marker_digits = marker["ordinal_digits"]
    pattern = re.compile(
        rf"^(?P<lineage>.+)-{re.escape(marker_prefix)}(?P<ordinal>\d{{{marker_digits},}})\.md$"
    )
    current_by_lineage: dict = {}
    for doc_path in sorted(base_path.glob("*.md")):
        match = pattern.match(doc_path.name)
        if not match:
            continue
        found_lineage = match.group("lineage")
        ordinal = int(match.group("ordinal"))
        current = current_by_lineage.get(found_lineage)
        if current is None or ordinal > current[0]:
            current_by_lineage[found_lineage] = (ordinal, doc_path)
    return {
        found_lineage: {"revision": doc_path.name, "sections": _heading_titles(doc_path)}
        for found_lineage, (_ordinal, doc_path) in sorted(current_by_lineage.items())
    }


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
    new_generation = body.get("generation", 0) + 1
    new_records = []
    for entry in body["records"]:
        if entry["kind"] == kind and entry["id"] == id_:
            entry = dict(entry)
            entry["fixed"] = False
            entry["generation"] = new_generation
        new_records.append(entry)
    new_body = {"generation": new_generation, "records": new_records}
    _write_declarations(paper_dir, pre, record, new_body)
    return {"id": id_, "kind": kind, "generation": new_body["generation"]}


def infer_related_work(corpus, opened_ids) -> bool:
    """Pure: Related Work is present iff any of `related-work`'s own block
    ids (`corpus.order_by_section["related-work"]`) is a member of
    `opened_ids` (design.md D4; `specs/skeleton-startup/spec.md`,
    `Requirement: Both Decisions Are Re-Derived From Disk, Never
    Recalled`). A corpus with no `related-work` section at all reports
    `False` -- there is nothing to have opened.
    """
    related_work_ids = corpus.order_by_section.get("related-work", ())
    return any(qualified_id in opened_ids for qualified_id in related_work_ids)


def dataset_placement_candidates(corpus) -> dict:
    """Pure: the dataset-placement candidate block, per section, DERIVED
    from the corpus itself rather than hardcoded (SKILL.md:154-158, "block
    ids are shape only ... never validates an id against a list of what
    should exist" -- WHICH ids exist is `sections/*.md`'s business, never
    this engine's). A candidate is any block whose own contract REQUIRES
    the `dataset` fact and is `optional` -- exactly the shape the real,
    shipped corpus already declares for both `materials-and-methods.
    mm-dataset` and `experimental-setup.es-dataset` (measured on disk, 2026
    -09-18, not assumed): renaming either block id in its own contract no
    longer desynchronizes this inference, because nothing here ever spells
    either id.

    Refuses `DATASET_PLACEMENT_CANDIDATE_ABSENT` (work-state) when NO block
    anywhere in the corpus matches -- a corpus that declares no such
    candidate at all is a shape this inference cannot silently read as
    `"undecided"`; an absence must be named, not swallowed. Refuses
    `DATASET_PLACEMENT_CANDIDATE_AMBIGUOUS` (work-state) when any ONE
    section offers more than one such candidate -- the "one per section"
    shape this inference requires does not hold for that corpus.
    """
    by_section: dict[str, list[str]] = {}
    for qualified_id, block in corpus.blocks.items():
        if block.optional and "dataset" in block.requires_facts:
            by_section.setdefault(block.section, []).append(qualified_id)

    if not by_section:
        raise Refused(
            "DATASET_PLACEMENT_CANDIDATE_ABSENT",
            "no block in this corpus requires the 'dataset' fact and is optional; "
            "dataset placement has no candidate to infer from",
        )
    ambiguous = {section: ids for section, ids in by_section.items() if len(ids) > 1}
    if ambiguous:
        raise Refused(
            "DATASET_PLACEMENT_CANDIDATE_AMBIGUOUS",
            f"more than one dataset-placement candidate in one section: {ambiguous}",
        )
    return {section: ids[0] for section, ids in by_section.items()}


def infer_dataset_placement(corpus, opened_ids) -> str:
    """Pure: the section name of whichever `dataset_placement_candidates`
    entry is opened, `"undecided"` if none is. Refuses `DATASET_PLACEMENT_
    CONFLICT` (work-state), naming every opened candidate, when more than
    one is opened at once -- the paper says two things and the skill will
    not pick one (design.md D4). Also raises whatever `dataset_placement_
    candidates` itself raises, unchanged.
    """
    candidates = dataset_placement_candidates(corpus)
    opened = {section: qid for section, qid in candidates.items() if qid in opened_ids}
    if len(opened) > 1:
        ids = ", ".join(repr(qid) for qid in sorted(opened.values()))
        raise Refused(
            "DATASET_PLACEMENT_CONFLICT",
            f"{ids} are opened; the paper names two placements and the skill will not pick one",
        )
    if not opened:
        return "undecided"
    (section,) = opened
    return section


def infer_skeleton_decisions(paper_dir: Path, corpus) -> dict:
    """Read-only: both skeleton decisions, re-derived from the block ids
    currently opened in `main.tex` (`paper_block.read_status`), intersected
    with the real corpus -- never from a separately stored flag and never
    from `read_fact(paper_dir, "skeleton")`, which is a DIFFERENT question
    (the gate `introduction.block-6` requires, "a skeleton exists") that
    design.md D4 deliberately keeps unused for this (`the-phases-are-
    derived-not-remembered`, "las decisiones no viven en ti, viven en el
    disco"). `tasks.md` 7.5's own mutation proof replaces the `read_status`
    call below with a `read_fact("skeleton")` read, over a fixture where
    the two disagree, to prove this reads disk and only disk.
    """
    status = paper_block.read_status(paper_dir)
    opened_ids = {block["id"] for block in status["blocks"]} & set(corpus.blocks)
    return {
        "relatedWork": infer_related_work(corpus, opened_ids),
        "datasetPlacement": infer_dataset_placement(corpus, opened_ids),
    }


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


class SourceRootKind(enum.Enum):
    """Whether a `FACT_SOURCE_ROOT` root is read as PROSE (a document
    revision with headings, resolvable for section binding), is a
    REPOSITORY (a target code repository, measured by running it -- never
    read as prose, regardless of what happens to exist on disk under its
    name), or is INGESTED (a published paper under `guidance/`, identified
    by that folder's own `evidence` classification -- never by a folder
    name literal). U2b correctness repair to `source-section-binding`
    spec's `Requirement: An Unmeasured Root Is Reported, Never Silently
    Passed`: a REPOSITORY-kind root is unmeasured BY KIND, not merely by
    the document-rooted predicate that requirement already names. U2c
    ruling (`the-requirement-names-the-section-that-feeds-it`): an
    INGESTED-kind root is not a revisioned lineage at all -- a published
    paper gets no `r22` -- so its resolution is IDENTITY (the lineage IS
    the document), never the PROSE branch's marker-driven max-ordinal
    search."""

    PROSE = "prose"
    REPOSITORY = "repository"
    INGESTED = "ingested"


class SourceRoot(NamedTuple):
    """One `FACT_SOURCE_ROOT` value: `name` (the root's own label -- for a
    `PROSE` root, the directory `source_root_status` resolves under the
    source base) and `kind` (`SourceRootKind`, above). `kind` carries NO
    default: a sixth fact/root pair that omits it fails immediately with
    `TypeError: missing ... argument`, rather than silently defaulting to
    `PROSE` and becoming spuriously section-bindable."""

    name: str
    kind: SourceRootKind


#: Which real-disk root each observable fact is read from, and that root's
#: KIND (`.claude/agents/insumos-observer.md`: "formulation, dataset (from
#: `proposals/` -- the managed mathematical proposal), experimental-design
#: (from `experiments/` -- the managed experiments document), implementation
#: (from the target implementation repository's own source) and results
#: (from that same repository's own run outputs)"). `implementation`/
#: `results` are `REPOSITORY`-kind: a target code repository, measured by
#: RUNNING it, never read as prose for section binding -- `impl_layout.
#: WORKSPACE` (the forge's own canonical target-repository workspace) is
#: the real path, never re-spelled here (U2b correctness repair, per
#: `source_root_status`'s own docstring below).
#:
#: `dataset` is `INGESTED`-kind (U2c ruling,
#: `the-requirement-names-the-section-that-feeds-it`): a proposal
#: lineage states the mathematics and need carry no dataset section at
#: all, so the fact is sourced from the ingested EVIDENCE
#: document under `guidance/` instead -- whichever folder that own
#: registry classes `'evidence'` (`paper_guidance.read_registry`,
#: DERIVED, never a folder name literal). `name="evidence"` here is a
#: generic vocabulary word already shared with `paper_guidance.CLASSES`,
#: never this paper's own guidance folder name -- `source_root_status`'s
#: INGESTED branch never resolves a directory from `root.name` at all,
#: the same "kind gates the check, name is not resolved" precedent
#: `REPOSITORY` already established.
#:
#: The `name` label is used only to RECONCILE an agent's report against a
#: measurement this process takes itself (`reconcile_observation_report`
#: below) -- never to resolve a directory for a REPOSITORY- or
#: INGESTED-kind root, and never to decide a fact's value. Every root
#: consumed by `assemble_corpus` (`paper_graph.Corpus.source_roots`, keyed
#: by `name` alone) MUST carry a name distinct from every other root
#: actually resolved on disk, or two different-kind roots would collide
#: on one dict key -- this is why `dataset` could not simply keep sharing
#: `formulation`'s `"proposals"` label once its KIND changed.
FACT_SOURCE_ROOT: dict = {
    "formulation": SourceRoot("proposals", SourceRootKind.PROSE),
    "dataset": SourceRoot("evidence", SourceRootKind.INGESTED),
    "experimental-design": SourceRoot("experiments", SourceRootKind.PROSE),
    "implementation": SourceRoot("implementation", SourceRootKind.REPOSITORY),
    "results": SourceRoot("implementation", SourceRootKind.REPOSITORY),
}


#: Per-root revision marker (`source-section-binding` spec, `Requirement:
#: The Marker Grammar Is Validated, And Disjoint From guidance/'s`; design.md
#: Decision A). Same filename `paper_guidance.py`'s own `guidance/` marker
#: uses (`_MARKER_NAME`) but a DISJOINT key set — `revisions` here,
#: `class` there — so a marker read by the wrong reader refuses loudly
#: rather than being silently half-understood.
_SOURCE_MARKER_NAME = ".paper-writing.json"
_SOURCE_MARKER_TOP_KEY = "revisions"
_SOURCE_MARKER_REQUIRED = ("revision_prefix", "ordinal_digits")


def read_revisions_marker(root: Path) -> dict | None:
    """`root / '.paper-writing.json'`'s own `{"revisions": {"revision_
    prefix": str, "ordinal_digits": int}}` declaration, or `None` when the
    marker file does not exist at all — an ABSENT marker is a distinct,
    legitimate state (`SOURCE_REVISIONS_UNDECLARED`, the caller's concern,
    never this reader's).

    Refuses `MALFORMED_SOURCE_MARKER` (work-state) naming the offending
    file and the missing, unknown, or wrong-typed key when the marker
    EXISTS but is not valid UTF-8, not valid JSON, not a JSON object, is
    missing the top-level `revisions` key, carries any other top-level key,
    is missing `revision_prefix`/`ordinal_digits`, carries an unknown
    nested key, or gives either required key the wrong type. A
    `guidance/`-shaped marker (`{"class": ...}`) refuses naming `revisions`
    as missing, rather than silently accepting `class` — the disjoint-key
    requirement, checked missing-before-unknown so the ABSENT key is always
    named first, the same ordering `paper_contract._validate_document_
    object` uses."""
    marker_path = root / _SOURCE_MARKER_NAME
    if not marker_path.is_file():
        return None
    try:
        raw_text = marker_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise Refused("MALFORMED_SOURCE_MARKER", f"{marker_path}: not valid utf-8: {exc}")
    try:
        obj = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise Refused("MALFORMED_SOURCE_MARKER", f"{marker_path}: invalid JSON: {exc.msg}")
    if not isinstance(obj, dict):
        raise Refused("MALFORMED_SOURCE_MARKER", f"{marker_path}: must be a JSON object")
    if _SOURCE_MARKER_TOP_KEY not in obj:
        raise Refused(
            "MALFORMED_SOURCE_MARKER",
            f"{marker_path}: missing required key {_SOURCE_MARKER_TOP_KEY!r}",
        )
    unknown = [key for key in obj if key != _SOURCE_MARKER_TOP_KEY]
    if unknown:
        raise Refused(
            "MALFORMED_SOURCE_MARKER", f"{marker_path}: carries unknown key {unknown[0]!r}"
        )
    revisions = obj[_SOURCE_MARKER_TOP_KEY]
    if not isinstance(revisions, dict):
        raise Refused(
            "MALFORMED_SOURCE_MARKER",
            f"{marker_path}: {_SOURCE_MARKER_TOP_KEY!r} must be an object",
        )
    missing = [key for key in _SOURCE_MARKER_REQUIRED if key not in revisions]
    if missing:
        raise Refused(
            "MALFORMED_SOURCE_MARKER",
            f"{marker_path}: {_SOURCE_MARKER_TOP_KEY!r} missing {missing[0]!r}",
        )
    unknown_nested = [key for key in revisions if key not in _SOURCE_MARKER_REQUIRED]
    if unknown_nested:
        raise Refused(
            "MALFORMED_SOURCE_MARKER",
            f"{marker_path}: {_SOURCE_MARKER_TOP_KEY!r} carries unknown key {unknown_nested[0]!r}",
        )
    revision_prefix = revisions["revision_prefix"]
    if not isinstance(revision_prefix, str):
        raise Refused(
            "MALFORMED_SOURCE_MARKER", f"{marker_path}: 'revision_prefix' must be a string"
        )
    ordinal_digits = revisions["ordinal_digits"]
    if not isinstance(ordinal_digits, int) or isinstance(ordinal_digits, bool):
        raise Refused(
            "MALFORMED_SOURCE_MARKER", f"{marker_path}: 'ordinal_digits' must be an integer"
        )
    return {"revision_prefix": revision_prefix, "ordinal_digits": ordinal_digits}


def source_root_status(base: Path, root: SourceRoot) -> dict:
    """`{"state": "document-rooted"|"unmeasured", "path": Path|None,
    "documents": int, "reason": str|None}` (design.md, Interfaces).

    A `SourceRootKind.REPOSITORY` root (`impl_layout.WORKSPACE` — the
    forge's own canonical target-repository workspace, never a name this
    skill re-spells) is ALWAYS `unmeasured`, regardless of whether that
    directory exists or holds `*.md` files: it is a target code
    repository, measured by RUNNING it, never read as prose for section
    binding. A U2b correctness repair to `source-section-binding` spec's
    `Requirement: An Unmeasured Root Is Reported, Never Silently Passed`
    — `implementation`/`results` were previously excluded only by an
    invented, never-existing directory name; here they are excluded by
    KIND, never by the document-rooted predicate below, so the outcome
    never depends on what a target repo's own `README.md`/`AGREED.md`
    happen to contain.

    A `SourceRootKind.INGESTED` root (U2c ruling) delegates to
    `_ingested_root_status` below — its path is DERIVED from `guidance/`'s
    own per-folder classification, never resolved from `root.name`.

    Otherwise (`SourceRootKind.PROSE`), document-rooted iff `base /
    root.name` is a directory holding at least one `*.md` file — a
    property computed on disk, never keyed by a fact id
    (`source-section-binding` spec, `Requirement: A Document-Rooted
    Source With No Marker Refuses`; design.md Decision B). An absent root
    and a root holding no `*.md` (e.g. only `.gitkeep`) both report
    `unmeasured` — the SAME report, never a refusal; only a document-rooted
    root missing its OWN marker refuses (`SOURCE_REVISIONS_UNDECLARED`,
    the caller's concern, checked one layer up)."""
    if root.kind is SourceRootKind.REPOSITORY:
        return {
            "state": "unmeasured", "path": impl_layout.WORKSPACE, "documents": 0,
            "reason": (
                f"{root.name!r} is a {root.kind.value} root ({impl_layout.WORKSPACE}), "
                "not read as prose for section binding"
            ),
        }
    if root.kind is SourceRootKind.INGESTED:
        return _ingested_root_status(base)
    path = base / root.name
    if not path.is_dir():
        return {
            "state": "unmeasured", "path": None, "documents": 0,
            "reason": f"{root.name!r} is not a directory under {base}",
        }
    documents = sorted(path.glob("*.md"))
    if not documents:
        return {
            "state": "unmeasured", "path": path, "documents": 0,
            "reason": f"{path} holds no '*.md' documents",
        }
    return {"state": "document-rooted", "path": path, "documents": len(documents), "reason": None}


def _ingested_root_status(base: Path) -> dict:
    """`source_root_status`'s `SourceRootKind.INGESTED` branch (U2c ruling,
    `the-requirement-names-the-section-that-feeds-it`): which `guidance/`
    folder feeds an ingested-kind fact is DERIVED from that folder's own
    `.paper-writing.json` classification — `paper_guidance.read_registry`,
    reused verbatim, the SAME reader every other `guidance/` consumer
    already goes through (`paper_cli._guard_source_md_classification`);
    this is its first SOURCE-ROOT consumer, never a second reader.

    An absent `guidance/` directory, or one carrying no folder classed
    `'evidence'` yet, reports `unmeasured` — a paper that has not
    classified (or ingested) its evidence document yet is a paper at an
    EARLIER STAGE, the same reading `experiments/` holding only
    `.gitkeep` already gets (`source-section-binding` spec, `Requirement:
    An Unmeasured Root Is Reported, Never Silently Passed`), never a
    fault. Exactly one folder classed `'evidence'` but holding zero
    ingested papers is ALSO `unmeasured`, for the identical reason.

    More than one folder classed `'evidence'` refuses
    `EVIDENCE_ROOT_AMBIGUOUS` naming every candidate — deciding WHICH
    folder is the root is this function's own job, and picking the first
    would be exactly the silent guess this change exists to rule out.
    """
    guidance_dir = paper_guidance.resolve_guidance_dir(None, forge_root=base)
    if not guidance_dir.is_dir():
        return {
            "state": "unmeasured", "path": None, "documents": 0,
            "reason": f"{guidance_dir} does not exist yet",
        }
    registry = paper_guidance.read_registry(guidance_dir)
    evidence_folders = sorted(name for name, klass in registry.items() if klass == "evidence")
    if not evidence_folders:
        return {
            "state": "unmeasured", "path": None, "documents": 0,
            "reason": f"no folder under {guidance_dir} is classed 'evidence' yet",
        }
    if len(evidence_folders) > 1:
        raise Refused(
            "EVIDENCE_ROOT_AMBIGUOUS",
            f"more than one folder under {guidance_dir} is classed 'evidence': "
            f"{evidence_folders}",
        )
    evidence_dir = guidance_dir / evidence_folders[0]
    papers = paper_guidance.ingested_papers(guidance_dir).get(evidence_folders[0], [])
    if not papers:
        return {
            "state": "unmeasured", "path": evidence_dir, "documents": 0,
            "reason": f"{evidence_dir} is classed 'evidence' but carries no ingested paper yet",
        }
    return {
        "state": "document-rooted", "path": evidence_dir, "documents": len(papers), "reason": None,
    }


def resolve_lineage(root: Path, lineage: str, marker: dict) -> Path:
    """The single highest-ordinal revision file under `root` matching
    `lineage`, per `marker`'s own declared `revision_prefix`/
    `ordinal_digits` — never a pattern literal (`source-section-binding`
    spec, `Requirement: Lineage Resolves To The Current Revision On Disk`;
    design.md Decision D). The regex is composed as
    `^{lineage}-{prefix}\\d{{digits,}}\\.md$`, so the ordinal capture group
    admits any digit COUNT at or above the declared minimum — two files
    whose ordinal-bearing suffix differs only in leading-zero padding
    (e.g. a two-digit and a three-digit spelling of the same prefix) parse
    to the SAME integer ordinal.

    Candidates are grouped by their PARSED integer ordinal; the winner is
    the highest one. Gaps between ordinals are irrelevant (an intermediate
    ordinal missing entirely never blocks resolving a later one). Refuses
    `SOURCE_LINEAGE_UNRESOLVED` naming the lineage and the root on ZERO
    candidates, and naming the lineage, the root, and every tied candidate
    when the highest ordinal is shared by more than one file (two
    spellings of the same ordinal) — covering both "did not resolve to
    exactly one revision" cases under this one code, never a seventh."""
    prefix = marker["revision_prefix"]
    digits = marker["ordinal_digits"]
    pattern = re.compile(rf"^{re.escape(lineage)}-{re.escape(prefix)}(\d{{{digits},}})\.md$")
    candidates = []
    for entry in sorted(root.glob("*.md")):
        match = pattern.match(entry.name)
        if match:
            candidates.append((int(match.group(1)), entry))
    if not candidates:
        raise Refused(
            "SOURCE_LINEAGE_UNRESOLVED",
            f"lineage {lineage!r} resolved to no file under {root} "
            f"(pattern {pattern.pattern!r})",
        )
    max_ordinal = max(ordinal for ordinal, _path in candidates)
    winners = sorted(path.name for ordinal, path in candidates if ordinal == max_ordinal)
    if len(winners) > 1:
        raise Refused(
            "SOURCE_LINEAGE_UNRESOLVED",
            f"lineage {lineage!r} under {root} ties at ordinal {max_ordinal}: {winners}",
        )
    return root / winners[0]


def resolve_ingested_document(evidence_dir: Path, lineage: str) -> Path:
    """The IDENTITY resolution route for a `SourceRootKind.INGESTED` root
    (U2c ruling, `the-requirement-names-the-section-that-feeds-it`,
    Structural consequence): an ingested paper is not a revisioned
    lineage — a published paper gets no `r22` — so `document.lineage`
    names the paper's own stable id directly, and resolution is PRESENCE
    of `evidence_dir/<lineage>/<lineage>.md`, never a marker-driven
    ordinal search.

    Reuses `paper_guidance.ingested_papers` verbatim (asked for
    `evidence_dir`'s own PARENT registry, filtered to `evidence_dir.
    name`'s own entries) rather than a second directory walk, then
    matches by exact folder-name equality against `lineage`. Refuses
    `SOURCE_LINEAGE_UNRESOLVED` — the SAME code a PROSE-kind root's
    `resolve_lineage` raises above, never a new one — when that filter
    yields anything other than exactly one candidate: zero (not yet
    ingested, or a different lineage named) and more than one
    (structurally unreachable on a real filesystem, where two
    directories cannot share one name, but checked explicitly rather
    than assumed) both refuse under this one shared code, covering "this
    lineage did not resolve to exactly one document" the same way
    `resolve_lineage`'s own docstring already generalizes its two cases.
    """
    papers = paper_guidance.ingested_papers(evidence_dir.parent).get(evidence_dir.name, [])
    candidates = [Path(entry["markdown"]) for entry in papers if entry["folder"] == lineage]
    if len(candidates) != 1:
        raise Refused(
            "SOURCE_LINEAGE_UNRESOLVED",
            f"lineage {lineage!r} resolved to {len(candidates)} ingested document(s) under "
            f"{evidence_dir} (expected exactly one)",
        )
    return candidates[0]


def is_bindable_fact(fact_id: str) -> bool:
    """`source-section-binding` spec, `Requirement: Bindable Facts Are
    Derived, Never Listed`: a fact is bindable **iff** it is a key of
    `FACT_SOURCE_ROOT` -- membership in this mapping is the sole and only
    test. The four PRODUCED facts and the structural `skeleton` fact are
    excluded by their absence from `FACT_SOURCE_ROOT`, not by a second,
    hand-maintained list naming them here or anywhere under `scripts/`.
    Extending `FACT_SOURCE_ROOT` with a new fact/root pair widens
    bindability with zero edit to this function (proven by
    `tests/test_paper_decisions.py::BindableFactDerivationTests
    .test_a_sixth_root_widens_bindability_with_zero_engine_edit`)."""
    return fact_id in FACT_SOURCE_ROOT


def source_available(root: Path) -> bool:
    """Gitignore-blind disk measurement of one source root's real
    availability, taken by THIS process -- `Path.iterdir()`, the same
    mechanism `paper_guidance.ingested_papers` already proved correct for
    `guidance/` (`the-skill-stops-trusting-memory`, item 5: `fd`/`rg` honor
    `.gitignore` by default and reported that whole tree empty four times
    in the session that produced this fix; `Path.iterdir()` is gitignore-
    blind by construction, never by instruction). A non-existent root and
    an existing-but-empty one both report `False` -- indistinguishable to
    a fact this root is supposed to ground either way.
    """
    return root.is_dir() and any(root.iterdir())


def reconcile_observation_report(report: dict, measured: dict) -> list:
    """Compares the agent's own per-fact `satisfied`/`evidence` account
    against `measured` (source-root-name -> `source_available` bool, taken
    by THIS process, never the agent's word) and returns every disagreement
    found -- never averages, never silently prefers one side.

    A disagreement is: the agent reports a fact UNSATISFIED with NO
    evidence at all, while the fact's own source root
    (`FACT_SOURCE_ROOT[fact_id]`) is measurably available RIGHT NOW. That is
    exactly the failure this exists to catch -- an agent claiming a source
    is absent/empty when it is not, because it used gitignore-respecting
    tooling this process never uses.

    `measured` need not name every root: a caller that does not know the
    implementation repository's path yet (there is no fixed default for
    it, unlike `proposals/`/`experiments/`) simply omits `"implementation"`
    and no fact mapped to it is reconciled -- reconciliation only ever
    fires for a root this call actually measured, never a guess about one
    it did not.
    """
    disagreements = []
    for fact_id, root in FACT_SOURCE_ROOT.items():
        root_name = root.name
        if root_name not in measured or not measured[root_name]:
            continue
        entry = report.get(fact_id) or {}
        satisfied = bool(entry.get("satisfied"))
        evidence = entry.get("evidence") or []
        if not satisfied and not evidence:
            disagreements.append({
                "fact": fact_id,
                "source": root_name,
                "reported": "unsatisfied, no evidence",
                "measured": f"{root_name!r} is non-empty on disk right now",
            })
    return disagreements


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
