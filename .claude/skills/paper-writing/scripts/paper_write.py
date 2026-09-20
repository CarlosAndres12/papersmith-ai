"""paper_write: the `write` pipeline — readiness, gate, draft, evidence-
audit, contract-audit, `substitute --contract` — with exactly one bounded
re-draft, enforced through an on-disk attempt ledger rather than counted
in-process (`writing-orchestration` spec; `design.md`, Decision D7).

The CLI is a judge, never an invoker (`design.md`, Decision D2): `draft` and
`audit_account` below are JSON envelopes an agent already produced and
handed back through `--draft`/`--audit`. This module never drafts, never
audits, never spawns anything — it reconciles what it is given against
`main.tex` and either writes or refuses.

Public surface:

    BlockContract                    -> the pipeline's one immutable input shape
    write_block(paper_dir, contract, draft, audit_account) -> dict
        (raises MODE_ABSENT, EVIDENCE_SET_REQUIRED, AUDIT_EXHAUSTED,
         plus every code `paper_bindings`/`paper_audit` themselves raise)
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_audit  # noqa: E402
import paper_bindings  # noqa: E402
import paper_block  # noqa: E402
import paper_vocabulary  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402


@dataclass(frozen=True)
class BlockContract:
    """One block's real inputs, already resolved from `sections/*.md` and
    `paper/.paper-writing/evidence/`. Never touches disk itself — every
    field is a plain value a caller (the CLI, or a test fixture) hands in."""

    block_id: str
    contract_prose: str
    contract_source: str
    citations_regime: str
    mode: str | None
    requires_facts: tuple
    evidence_set: tuple = ()
    style_set: tuple = ()
    #: `transposition-fidelity` spec's own prerequisite plumbing (design.md
    #: Decision E). One entry per bound source section
    #: (`paper_source_span.resolve_bound_sections`'s own return shape:
    #: `{"fact", "lineage", "title", "path", "byte_start", "byte_end",
    #: "text"}`), already resolved from disk by the CLI -- this dataclass
    #: never touches disk itself. Defaulted, the same `produces_facts`/
    #: `source_bindings` precedent, so every construction site that
    #: predates this field stays green unchanged.
    source_sections: tuple = ()


def _attempt_key(contract: BlockContract) -> str:
    payload = json.dumps(
        {
            "contract": contract.contract_prose,
            "evidence": [dict(entry) for entry in contract.evidence_set],
            "mode": contract.mode,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _ledger_path(paper_dir: Path, block_id: str) -> Path:
    return paper_dir / ".paper-writing" / "attempts" / f"{block_id}.json"


def _read_ledger(paper_dir: Path, block_id: str) -> dict | None:
    path = _ledger_path(paper_dir, block_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_ledger(paper_dir: Path, block_id: str, entry: dict) -> None:
    path = _ledger_path(paper_dir, block_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry), encoding="utf-8")


def _stage_readiness(contract: BlockContract) -> None:
    """`readiness`/`gate`, combined: the pipeline's own preconditions before
    any draft is even read. Refuses `MODE_ABSENT` (`section-contract` spec,
    `Requirement: Headers Written Before mode Existed`) when no mode
    resolved at either level — `write` never assumes a default. Refuses
    `EVIDENCE_SET_REQUIRED` (Ruling 3: a block whose `citations` regime is
    not `none` and carries no evidence set is refused, never reported
    `unvalidated` — every claim it would make is unbound, not merely
    unchecked) when `citations_regime != "none"` and `evidence_set` is
    empty. The pre-existing facts/declarations writability gate
    (`paper_readiness.compute_block_readiness`) is a separately-wired
    capability this pipeline does not duplicate; a caller (the CLI) is
    expected to have already confirmed the block is writable before
    invoking `write_block` at all.
    """
    if contract.mode is None:
        raise Refused(
            "MODE_ABSENT",
            f"{contract.block_id}: no mode resolves at section or block level; "
            "write refuses rather than assuming one",
        )
    paper_vocabulary.validate_mode(contract.mode)
    if contract.citations_regime != "none" and not contract.evidence_set:
        raise Refused(
            "EVIDENCE_SET_REQUIRED",
            f"{contract.block_id}: citations={contract.citations_regime!r} requires "
            "a non-empty evidence set; every claim this block would make is unbound",
        )


def _stage_evidence_audit(contract: BlockContract, draft: dict) -> list:
    bindings = paper_bindings.reconcile(draft["latex"], draft["bindings"])
    evidence_ids = {entry["id"] for entry in contract.evidence_set}
    facts = set(contract.requires_facts)
    paper_bindings.resolve_bindings(bindings, evidence_ids, facts)
    paper_bindings.type_structural(bindings, contract.contract_prose)
    evidence_by_id = {entry["id"]: entry for entry in contract.evidence_set}
    paper_bindings.check_mode_admissibility(bindings, contract.mode, evidence_by_id)
    return bindings


def _stage_contract_audit(contract: BlockContract, draft: dict, audit_account: dict) -> dict:
    return paper_audit.audit(
        contract.contract_prose, draft["latex"], audit_account["verdicts"],
        source_name=contract.contract_source,
    )


def write_block(paper_dir: Path, contract: BlockContract, draft: dict, audit_account: dict) -> dict:
    """One `write` invocation for one block (`writing-orchestration` spec,
    `Requirement: Pipeline Stage Order`). Stages run in order: readiness,
    gate (both `_stage_readiness` above), draft (`draft`/`audit_account`
    already handed in), evidence-audit, contract-audit, `substitute
    --contract`. A stage never starts until every earlier one clears —
    `_stage_evidence_audit` running before `_stage_contract_audit` is what
    makes "a failing evidence-audit stops the pipeline before contract-audit
    runs" true by construction, not by a check somewhere else.

    Contract-audit firing does not itself refuse: it records the attempt in
    the on-disk ledger and reports the fired bullets as feedback for exactly
    one re-draft (`Requirement: One Bounded Re-Draft`). A second consecutive
    attempt under the same `(contract, evidence, mode)` key that still fires
    refuses `AUDIT_EXHAUSTED` naming every bullet that fired on that attempt
    (`Requirement: Exhaustion Leaves The Block Unwritten`) — `substitute` is
    never reached on that path, so `main.tex` stays byte-identical to its
    pre-`write` state.
    """
    _stage_readiness(contract)
    _stage_evidence_audit(contract, draft)

    key = _attempt_key(contract)
    ledger = _read_ledger(paper_dir, contract.block_id)
    attempt = 1
    if ledger is not None and ledger.get("key") == key:
        attempt = ledger.get("attempts", 0) + 1

    audit_result = _stage_contract_audit(contract, draft, audit_account)

    if audit_result["blocks"]:
        fired = [{"bullet": entry["bullet"], "span": entry["span"]} for entry in audit_result["fired"]]
        if attempt >= 2:
            raise Refused(
                "AUDIT_EXHAUSTED",
                f"{contract.block_id}: contract-audit still fires on attempt {attempt}: "
                f"{[entry['bullet'] for entry in fired]}",
            )
        _write_ledger(paper_dir, contract.block_id, {"key": key, "attempts": attempt, "fired": fired})
        return {
            "status": "audit-fired",
            "block": contract.block_id,
            "attempt": attempt,
            "fired": fired,
            "verdicts": audit_result["verdicts"],
        }

    if contract.style_set:
        # Local import, not module-level: `paper_write.py` is a Work Unit 1
        # file and must stay importable (and `write_block` callable with an
        # empty style set, the only value WU1 itself ever populates) even
        # when `paper_leak.py` is absent -- WU2's own rollback boundary
        # ("Unit 1 stands alone with an empty style channel"). Only a
        # non-empty `style_set` -- which only the WU2-wired CLI path
        # (`cmd_write`'s `--style`) ever produces -- reaches this branch.
        # `design.md`'s own Data Flow: "paper_leak.tripwire (styled only)
        # -> paper_write ledger" runs here, after contract-audit clears and
        # before `substitute`, independent of the A/B/S register/overlap
        # proof (`paper_leak.register_distance_holds`/
        # `relative_overlap_holds`), which is a Unit-level proof of the
        # mechanism itself (`design.md`, Testing Strategy table), not a
        # per-write runtime check -- the same role `_run_against_mutant`
        # plays for the byte-identity guards, exercised by
        # `StyleLeakDetectionTests`, never by a real `write` call.
        import paper_leak  # noqa: PLC0415
        paper_leak.check_tripwire(draft["latex"], contract.style_set)

    # Ruling 2's real caller: every real `write` that reaches this point
    # (contract-audit cleared) reports the style channel's own status in
    # the returned envelope, never only through a standalone unit test.
    # `register_result`/`overlap_result` stay `None` here -- that pair is
    # the proof harness's own measurement over recorded A/B/S transcripts
    # (`design.md`, Decision D6; `StyleLeakDetectionTests`), never computed
    # for a single real `write` call, which only ever runs the tripwire
    # above. An empty `style_set` still reaches this call, which is what
    # makes "unmeasured" a real reported status rather than an omitted key.
    style_report = style_channel_report(contract.style_set, None, None)

    # `transposition-fidelity` spec, `Requirement: A Block With No Measured
    # Bound Section Reports Unmeasured, Never Refused` (WU1's own scope,
    # design.md Decision E). `source_fidelity_report` below adds no
    # comparison and no refusal -- that is `check_source_section_
    # verbatim`'s own sibling stage, wired in by WU2 -- this call only
    # reports whether a bound section reached the pipeline at all,
    # mirroring `style_channel_report`'s shipped shape rather than
    # inventing a second reporting convention.
    source_fidelity = source_fidelity_report(contract.source_sections)

    result = paper_block.substitute(paper_dir, contract.block_id, new_body=draft["latex"].encode("utf-8"))
    return {
        "status": "written",
        "block": contract.block_id,
        "verdicts": audit_result["verdicts"],
        "styleChannel": style_report,
        "sourceFidelity": source_fidelity,
        **result,
    }


def source_fidelity_report(source_sections: tuple) -> dict:
    """`transposition-fidelity` spec, `Requirement: A Block With No
    Measured Bound Section Reports Unmeasured, Never Refused` -- WU1's own
    scope only (design.md Decision E; tasks.md 1.9). Mirrors `style_
    channel_report`'s own shape: no bound section resolved for this block
    -> `unmeasured`, never a silent pass and never inferred only from the
    absence of a refusal.

    A non-empty `source_sections` reports `measured` with no per-section
    detail yet -- the floor/threshold/longest_run report per section
    (`{"lineage", "title", "floor", "threshold", "longest_run"}`) is
    `check_source_section_verbatim`'s own computation, WU2's scope, not
    this phase's: this function adds no comparison and no refusal of its
    own, only whether a bound section reached the pipeline at all.
    """
    if not source_sections:
        return {"status": "unmeasured"}
    return {"status": "measured", "sections": []}


def style_channel_report(recorded_samples: list, register_result: dict | None, overlap_result: dict | None) -> dict:
    """Ruling 2 (orchestrator, this change): an empty `R` — every
    style-reference resolved `noEquivalent` — means register distance
    measures nothing and overlap is vacuously satisfied, so the style
    channel reports `unmeasured` rather than a silent pass. Joins
    `unprovenanced`/`unclassified`/`ambiguous` in this skill's own
    uncertainty vocabulary (`design.md`, Decision D8's sibling for the style
    channel)."""
    if not recorded_samples:
        return {"status": "unmeasured"}
    return {"status": "measured", "register": register_result, "overlap": overlap_result}
