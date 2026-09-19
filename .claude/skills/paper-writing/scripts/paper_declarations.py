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
    decline_fact(paper_dir, id, reason, condition, *, clock=...) -> dict
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
    *, clock=paper_region.default_clock,
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
