#!/usr/bin/env python3
"""paper_cli.py — front door for the `paper-writing` skill.

Standard library only, keyless, offline, fail-closed — the shape of
`implementation_cli.py` and `remote_cli.py`. One JSON object on stdout per
invocation. Exit 0 means the command ran; exit 2 means a guard refused
before touching disk.

Wires thirteen verbs: `scaffold`, `open`, `status`, `substitute` (from
`only-the-block-changes`; `substitute` grew an optional `--contract <path>`
in Slice C1 of `the-paper-carries-its-own-decisions`, recording provenance
without changing what bytes get written); `contract`, `readiness`, `order`
(from `the-contract-is-data-not-code`); `declare`, `plan` (from
`the-paper-carries-its-own-decisions`, Slices B and C2); `resolve`,
`bib build`, `validate` (from `no-claim-without-a-source-that-holds-it`,
WU1/WU2/WU3 — `resolve` is the one path that makes this CLI not offline end
to end, keyless and behind a role `papersmith.yaml` can empty; `bib build`
rebuilds `refs.bib` whole from cached resolved metadata only; `validate` is
the single gate deciding verdict, placement and the bounded search-round
budget before any block reaches disk); and `write` (from `the-writer-may-
assert-only-what-it-was-given` — a judge, never an invoker: it reconciles an
already-shuttled redactor draft and contract-auditor account against one
block's real contract, evidence set and mode, and either substitutes the
block or reports why not, with exactly one bounded re-draft). Left
extensible on purpose; nothing here assumes it is the last verb this file
will ever grow.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_block  # noqa: E402
import paper_scaffold  # noqa: E402
import paper_vocabulary  # noqa: E402
import paper_contract  # noqa: E402
import paper_graph  # noqa: E402
import paper_readiness  # noqa: E402
import paper_region  # noqa: E402,F401 -- registered for the roster derivation
import paper_guidance  # noqa: E402
import paper_declarations  # noqa: E402
import paper_provenance  # noqa: E402,F401 -- for the roster derivation; substitute's own --contract wiring calls paper_block, which calls this module in turn
import paper_objective  # noqa: E402,F401 -- this skill's own declared north (tests/test_agents.py); raises no Refused of its own
import paper_evidence  # noqa: E402 -- no-claim-without-a-source-that-holds-it, WU1: the claim<->source record
import paper_resolve  # noqa: E402 -- no-claim-without-a-source-that-holds-it, WU1: the urllib resolution client
import paper_bib  # noqa: E402 -- no-claim-without-a-source-that-holds-it, WU2: refs.bib from cached metadata
import paper_validate  # noqa: E402 -- no-claim-without-a-source-that-holds-it, WU3: verdicts, placement, the bounded loop
import paper_bindings  # noqa: E402 -- the-writer-may-assert-only-what-it-was-given, WU1: binding map reconciliation/resolution/typing/mode
import paper_audit  # noqa: E402 -- the-writer-may-assert-only-what-it-was-given, WU1: verbatim Disqualifiers reconciliation
import paper_write  # noqa: E402 -- the-writer-may-assert-only-what-it-was-given, WU1: the write pipeline and its attempt ledger
import paper_style  # noqa: E402,F401 -- the-writer-may-assert-only-what-it-was-given, WU2: style-reference resolution and R; for the roster derivation
import paper_leak  # noqa: E402,F401 -- the-writer-may-assert-only-what-it-was-given, WU2: register/overlap proof and the eight-token tripwire; for the roster derivation
import paper_latex  # noqa: E402,F401 -- a-diagram-that-compiles-or-says-why: the sole subprocess seam (latexmk), invocation, log parse, verdict; for the roster derivation
import paper_figure  # noqa: E402 -- a-diagram-that-compiles-or-says-why: source/manifest layout, stop A, the compile pipeline, the repair-budget ledger; `render`/`place` verbs
import paper_obligation  # noqa: E402,F401 -- a-diagram-that-compiles-or-says-why: components/separation/caption/mandatory checks over the contract's `figure:` declaration; imported ahead of any verb calling it directly (the same shape `paper_region.py`/`paper_guidance.py` already established) so its refusals are reachable the moment the import lands
import paper_coupling_evidence  # noqa: E402 -- the-couplings-hold-or-they-do-not: every disk read `verify` needs (named to avoid colliding with `paper_evidence.py`, WU1's own claim<->source module)
import paper_verify  # noqa: E402 -- the-couplings-hold-or-they-do-not: the seven pure coupling checks and the report they assemble; raises no `Refused` of its own (every refusal a `verify` run can report is `DECLARATION_RECORD_ABSENT`, from `paper_coupling_evidence.py`)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: This script's own absolute path, resolved once — printed by no command
#: yet, kept for the same reason `implementation_cli.py`'s `CLI_PATH` is:
#: whatever prints a runnable command later reaches for this rather than a
#: bare relative name.
CLI_PATH = Path(__file__).resolve()

#: The two classes every refusal below is sorted into, matching
#: `implementation_cli.py`'s own vocabulary: can the caller clear this by
#: changing the invocation alone (`INVOCATION_DEFECT`), or does clearing it
#: require acting on the repository (`WORK_STATE`)?
INVOCATION_DEFECT = "invocation-defect"
WORK_STATE = "work-state"

#: Every refusal code reachable from a command below, classified. Derived
#: against and held to `reachable_paper_refusal_codes()`
#: (`tests/test_paper_writing.py`) in both directions: nothing reachable is
#: unclassified, and nothing classified here is unreachable. Never a code
#: this file merely documents — every entry is a code some command really
#: raises, directly or through a module this file imports
#: (`paper_block.py`, `paper_scaffold.py`, `paper_vocabulary.py`,
#: `paper_contract.py`, `paper_graph.py`, `paper_region.py`,
#: `paper_guidance.py`; `paper_readiness.py` raises none of its own).
#: `paper_region.py` and `paper_guidance.py` are imported ahead of their own
#: verb wiring (`the-paper-carries-its-own-decisions`, Slice A) -- their
#: refusals are reachable the moment the import lands, so they are
#: classified here immediately rather than left dangling until `declare`/
#: `plan` exist.
REFUSAL_CLASSIFICATION: dict[str, str] = {
    # --- scaffold ------------------------------------------------------
    "PAPER_OUTSIDE_REPOSITORY": INVOCATION_DEFECT,
    "PAPER_NOT_A_DIRECTORY": WORK_STATE,
    "SCAFFOLD_ENTRY_WRONG_TYPE": WORK_STATE,
    # --- shared block resolution (open, status, substitute) ------------
    "PAPER_ABSENT": WORK_STATE,
    "TEX_UNDECODABLE": WORK_STATE,
    "BLOCK_ID_MALFORMED": INVOCATION_DEFECT,
    # --- marker grammar --------------------------------------------------
    "MARKER_MALFORMED": WORK_STATE,
    "BLOCK_DUPLICATED": WORK_STATE,
    "BLOCK_UNPAIRED": WORK_STATE,
    "BLOCK_NESTED": WORK_STATE,
    # --- open ------------------------------------------------------------
    "ANCHOR_ABSENT": INVOCATION_DEFECT,
    "OPEN_POSITION_REQUIRED": INVOCATION_DEFECT,
    "OPEN_POSITION_CONFLICT": INVOCATION_DEFECT,
    # --- substitute --------------------------------------------------------
    "BLOCK_ABSENT": WORK_STATE,
    "BLOCK_HAND_EDITED": WORK_STATE,
    "CONTENT_CARRIES_MARKER": INVOCATION_DEFECT,
    "NOTHING_TO_ADOPT": INVOCATION_DEFECT,
    "SUBSTITUTE_MODE_REQUIRED": INVOCATION_DEFECT,
    "ADOPT_BODY_CONFLICT": INVOCATION_DEFECT,
    "SUBSTITUTION_NOT_LOCAL": WORK_STATE,
    "TEX_MOVED": WORK_STATE,
    # --- closed vocabularies (paper_vocabulary.py) ----------------------
    "UNKNOWN_FACT": WORK_STATE,
    "UNKNOWN_DECLARATION": WORK_STATE,
    "UNKNOWN_CITATIONS_REGIME": WORK_STATE,
    # --- header schema (paper_contract.py; `install_header` -- and its own
    # HEADER_PRESENT/BODY_MUTATED -- deleted in the zero-production-caller
    # corrective: its one-shot migration already ran and nothing promises
    # an ongoing "create a new section contract" workflow) ----------------
    "MALFORMED_HEADER": WORK_STATE,
    "SECTIONS_OUTSIDE_REPOSITORY": INVOCATION_DEFECT,
    #: K4 corrective: `resolve_sections_dir` now also refuses when the
    #: resolved path does not exist as a directory, reusing the exact code
    #: `UNMEASURED_REASONS` (`paper_verify.py`) and `_blocks_by_fact`
    #: (`paper_coupling_evidence.py`) already use to name "the corpus
    #: itself could not be read" — never a second code for the same
    #: condition.
    "SECTION_CONTRACTS_UNREADABLE": WORK_STATE,
    # --- corpus assembly and order (paper_graph.py) -----------------------
    "ID_COLLISION": WORK_STATE,
    "ORDER_CYCLE": WORK_STATE,
    # --- the-phases-are-derived-not-remembered, unit 1: the two-heading
    # partition every contract's prose must carry (paper_graph.py,
    # `_verify_input_partition`, called from `assemble_corpus`) ------------
    "INPUT_PARTITION_ABSENT": WORK_STATE,
    # --- the-phases-are-derived-not-remembered, unit 4: every `### Internal
    # chain` row transcribes to a real, backed `after` edge
    # (paper_graph.py, `_verify_internal_chain`) ---------------------------
    "CHAIN_ROW_UNRESOLVED": WORK_STATE,
    "CHAIN_ROW_UNBACKED": WORK_STATE,
    # --- the-phases-are-derived-not-remembered, unit 4 (tasks 4.8b-4.8i):
    # the PROSE -> HEADER direction no other check covers -- a numbered
    # heading (parent or `###` child) naming a sub-unit the front matter
    # never declared, or naming several without an explicit grouping
    # (paper_graph.py, `_verify_block_subunits`) ---------------------------
    "BLOCK_SUBUNIT_UNDECLARED": WORK_STATE,
    "UNIT_HEADING_AMBIGUOUS": WORK_STATE,
    # --- region grammar (paper_region.py) -- twins of Phase 1's marker
    # codes, reachable ahead of their own verb wiring because paper_cli.py
    # imports paper_region.py at module level (Slice A, `the-paper-carries-
    # its-own-decisions`) -----------------------------------------------
    "REGION_MALFORMED": WORK_STATE,
    "REGION_DUPLICATED": WORK_STATE,
    "REGION_UNPAIRED": WORK_STATE,
    # --- guidance registry (paper_guidance.py) -- same reason -----------
    "GUIDANCE_OUTSIDE_REPOSITORY": INVOCATION_DEFECT,
    "UNKNOWN_GUIDANCE_CLASS": WORK_STATE,
    "MALFORMED_GUIDANCE_MARKER": WORK_STATE,
    # --- declare (paper_declarations.py; UNKNOWN_FACT/UNKNOWN_DECLARATION
    # already classified above -- reused verbatim, never a second code for
    # the same condition, design.md's own decision) ---------------------
    "DECLARATION_FIXED": WORK_STATE,
    "DECLARATIONS_HAND_EDITED": WORK_STATE,
    # --- declare's own mode selection (this file; the same shape
    # SUBSTITUTE_MODE_REQUIRED/ADOPT_BODY_CONFLICT and
    # OPEN_POSITION_REQUIRED/OPEN_POSITION_CONFLICT already establish for
    # `substitute`/`open` -- not named in design.md's refusal table, which
    # only enumerates the region/vocabulary-level codes, so this is a
    # deliberate small extension of an existing convention) --------------
    "DECLARE_MODE_REQUIRED": INVOCATION_DEFECT,
    "DECLARE_MODE_CONFLICT": INVOCATION_DEFECT,
    "DECLARE_VALUE_REQUIRED": INVOCATION_DEFECT,
    # --- substitute --contract (paper_block.py's own new step; provenance
    # write itself is paper_provenance.py) -------------------------------
    "CONTRACT_UNREADABLE": WORK_STATE,
    "PROVENANCE_HAND_EDITED": WORK_STATE,
    # --- observation report validation (paper_declarations.py, wired to a
    # real caller via cmd_observe; formerly reachable only through the
    # whole-module scan, with no cmd_* root calling it -- closed by
    # wiring `observe`, the shuttle verb for `insumos-observer`'s report) -
    "NOT_AN_OBSERVABLE_FACT": INVOCATION_DEFECT,
    "EVIDENCE_CONFLATED": INVOCATION_DEFECT,
    # --- observe's own file/JSON read (this file; same shape
    # CONTRACT_UNREADABLE already establishes for a shuttled file) --------
    "OBSERVATION_REPORT_UNREADABLE": WORK_STATE,
    # --- verdict vocabulary (paper_vocabulary.py; no-claim-without-a-
    # source-that-holds-it Phase 1) --------------------------------------
    "UNKNOWN_VERDICT": WORK_STATE,
    # --- the claim<->source record and its span (paper_evidence.py; WU1) -
    "SPAN_NOT_IN_SOURCE": WORK_STATE,
    "VERDICT_SPAN_REQUIRED": WORK_STATE,
    # --- the urllib resolution client (paper_resolve.py; WU1) -----------
    "PAPERSMITH_CONFIG_UNREADABLE": WORK_STATE,
    "UNKNOWN_ROLE": INVOCATION_DEFECT,
    "DISCOVERY_UNAVAILABLE": WORK_STATE,
    "RESOLVER_ROLE_EMPTY": WORK_STATE,
    "RESOLVER_UNREACHABLE": WORK_STATE,
    "IDENTIFIER_UNRESOLVED": WORK_STATE,
    # --- the bibliography that cannot be typed (paper_bib.py; WU2) ------
    "ENTRY_UNSOURCED": WORK_STATE,
    "CITE_WITHOUT_ENTRY": WORK_STATE,
    "ENTRY_WITHOUT_CITE": WORK_STATE,
    # --- the validator and the bounded loop (paper_validate.py; WU3) -----
    "EVIDENCE_EXHAUSTED": WORK_STATE,
    "CITATION_MULTI_CLAIM_SENTENCE": WORK_STATE,
    "CITATION_NOUN_PHRASE": WORK_STATE,
    "CITATION_NOT_AT_SENTENCE_END": WORK_STATE,
    "CITATION_DETACHED_FROM_OBJECT": WORK_STATE,
    "CITATION_UNDER_NONE_REGIME": WORK_STATE,
    "CONTRACT_HEADER_ABSENT": WORK_STATE,
    # --- validate's own mode selection (this file; the same shape as
    # SUBSTITUTE_MODE_REQUIRED/DECLARE_MODE_REQUIRED) --------------------
    "VALIDATE_VERDICT_REQUIRED": INVOCATION_DEFECT,
    # --- mode widening (paper_vocabulary.py/paper_contract.py; the-writer-
    # may-assert-only-what-it-was-given, section-contract delta) ----------
    "UNKNOWN_MODE": WORK_STATE,
    # --- the binding map: reconciliation, resolution, structural typing,
    # mode admissibility (paper_bindings.py; WU1) -------------------------
    "UNBOUND_SENTENCE": WORK_STATE,
    "BINDING_ORPHANED": WORK_STATE,
    "EVIDENCE_ID_UNKNOWN": WORK_STATE,
    "FACT_NOT_LICENSED": WORK_STATE,
    "STRUCTURAL_CARRIES_CLAIM": WORK_STATE,
    "MODE_VIOLATION": WORK_STATE,
    # --- the contract audit: verbatim Disqualifiers, verdict reconciliation
    # (paper_audit.py; WU1) ------------------------------------------------
    "DISQUALIFIERS_ABSENT": WORK_STATE,
    "VERDICT_MISSING": WORK_STATE,
    "VERDICT_BULLET_UNKNOWN": WORK_STATE,
    # --- the write pipeline: readiness/gate and exhaustion (paper_write.py;
    # WU1) ------------------------------------------------------------------
    "MODE_ABSENT": WORK_STATE,
    "EVIDENCE_SET_REQUIRED": WORK_STATE,
    "AUDIT_EXHAUSTED": WORK_STATE,
    # --- the eight-token tripwire (paper_leak.py; WU2) ---------------------
    "STYLE_OVERLAP": WORK_STATE,
    # --- a-diagram-that-compiles-or-says-why: `render`/`place`, the sole
    # subprocess seam (paper_latex.py), source/manifest layout and the
    # repair ledger (paper_figure.py), and the obligation checks
    # (paper_obligation.py, imported ahead of any verb calling it directly
    # -- reachable the moment the import lands, the same shape
    # paper_region.py/paper_guidance.py already established). Twelve codes
    # from `authored-diagram`/`diagram-obligation`, plus two this skill's
    # own design introduces for behaviour the spec described without
    # naming a code (`LATEX_LOG_ABSENT`, `LATEX_OUTCOME_UNEXPLAINED`) -----
    "DIAGRAM_SOURCE_ABSENT": WORK_STATE,
    "LATEX_TOOLCHAIN_ABSENT": WORK_STATE,
    "LATEX_PACKAGE_ABSENT": WORK_STATE,
    "REPAIR_BUDGET_SPENT": WORK_STATE,
    "DIAGRAM_PLOTS_DATA": WORK_STATE,
    "MALFORMED_FIGURE_OBLIGATION": WORK_STATE,
    "COMPONENT_MISMATCH": WORK_STATE,
    # `components_from`'s Components Check is derived, never operator-
    # supplied (corrective amendment, `_resolve_expected_components`) -----
    "COMPONENTS_FACT_UNRESOLVED": WORK_STATE,
    "COMPONENTS_FACT_NOT_A_LIST": WORK_STATE,
    "MANIFEST_SOURCE_MISMATCH": WORK_STATE,
    "EXCLUDED_COMPONENT": WORK_STATE,
    "SHARED_COMPONENT": WORK_STATE,
    "CAPTION_INCOMPLETE": WORK_STATE,
    "MANDATORY_DIAGRAM_ABSENT": WORK_STATE,
    "LATEX_LOG_ABSENT": WORK_STATE,
    "LATEX_OUTCOME_UNEXPLAINED": WORK_STATE,
    # --- the-couplings-hold-or-they-do-not: verify's own declaration
    # record (`paper_coupling_evidence.py`; imported ahead of `verify`'s
    # own wiring, same shape as `paper_region.py`/`paper_obligation.py`
    # above). Every other tier of inability `verify` reports (an absent
    # provenance region, an undeclared block, an unreadable section
    # corpus) is an `unmeasured_reason` string in the report payload, never
    # a `Refused` -- only the whole-record-absent tier refuses the run -----
    "DECLARATION_RECORD_ABSENT": WORK_STATE,
}


def cmd_scaffold(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    return paper_scaffold.scaffold(paper_dir)


def cmd_status(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    return paper_block.read_status(paper_dir)


def cmd_open(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    positions_given = [flag for flag in ("after", "at_end") if getattr(args, flag, None)]
    if not positions_given:
        raise Refused(
            "OPEN_POSITION_REQUIRED",
            "--after <id> or --at-end is required.",
        )
    if len(positions_given) > 1:
        raise Refused(
            "OPEN_POSITION_CONFLICT",
            "--after and --at-end were given together; exactly one position is required.",
        )
    return paper_block.open_block(paper_dir, args.block, after=args.after, at_end=bool(args.at_end))


def cmd_substitute(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    modes_given = [flag for flag in ("body", "adopt") if getattr(args, flag, None)]
    if not modes_given:
        raise Refused(
            "SUBSTITUTE_MODE_REQUIRED",
            "--body <path|-> or --adopt is required.",
        )
    if len(modes_given) > 1:
        raise Refused(
            "ADOPT_BODY_CONFLICT",
            "--body and --adopt were given together; --adopt takes no body.",
        )
    contract = Path(args.contract) if args.contract else None
    if args.adopt:
        return paper_block.substitute(paper_dir, args.block, adopt=True, contract=contract)
    raw = sys.stdin.buffer.read() if args.body == "-" else Path(args.body).read_bytes()
    return paper_block.substitute(paper_dir, args.block, new_body=raw, contract=contract)


def cmd_contract(args: argparse.Namespace) -> dict:
    if args.file:
        header, _body = paper_contract.parse(Path(args.file).read_bytes())
        return {
            "section": header.section,
            "position": header.position,
            "after": header.after,
            "blocks": header.blocks,
        }
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    corpus = paper_graph.assemble_corpus(sections_dir)
    edge_set = paper_graph.collect_edges(corpus)
    return {
        "sections": sorted(corpus.sections),
        "blocks": sorted(corpus.blocks),
        "danglingEdges": sorted(set(edge_set.dangling)),
    }


def cmd_readiness(args: argparse.Namespace) -> dict:
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    corpus = paper_graph.assemble_corpus(sections_dir)
    report = paper_readiness.compute_readiness(
        corpus,
        satisfied_facts=set(args.fact or []),
        satisfied_declarations=set(args.declaration or []),
    )
    return {"blocks": report}


def cmd_order(args: argparse.Namespace) -> dict:
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    corpus = paper_graph.assemble_corpus(sections_dir)
    edge_set = paper_graph.collect_edges(corpus)
    order = paper_graph.derive_order(corpus, edge_set)
    return {"order": order, "danglingEdges": sorted(set(edge_set.dangling))}


def cmd_declare(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    modes_given = [flag for flag in ("declaration", "fact", "reopen") if getattr(args, flag, None)]
    if not modes_given:
        raise Refused(
            "DECLARE_MODE_REQUIRED",
            "exactly one of --declaration <id>, --fact <id>, --reopen <id> is required.",
        )
    if len(modes_given) > 1:
        raise Refused(
            "DECLARE_MODE_CONFLICT",
            f"{modes_given} were given together; exactly one mode is required.",
        )
    if args.reopen:
        return paper_declarations.reopen(paper_dir, args.reopen)
    if args.value is None:
        raise Refused(
            "DECLARE_VALUE_REQUIRED",
            "--declaration/--fact requires --value <the recorded value or resolution>.",
        )
    if args.declaration:
        return paper_declarations.set_declaration(paper_dir, args.declaration, args.value)
    return paper_declarations.set_fact(paper_dir, args.fact, args.value)


def cmd_observe(args: argparse.Namespace) -> dict:
    """`observe`: validates an already-produced `insumos-observer` report
    against the observable-fact schema and the `implementation`/`results`
    evidence-conflation guard, read-only — the Schema enforcement layer
    `design.md`'s "`insumos-observer` cannot decide, by schema and by
    capability" names, wired to a real caller. `insumos-observer` itself has
    no `Write`/`Edit`/`Bash` and never runs `declare`; its JSON account is
    shuttled to a file exactly like the redactor/contract-auditor/
    style-sampler accounts `write` already consumes, and this verb is what
    reads it back before a human runs `declare` against it themselves. Never
    calls `declare`, never writes anything.
    """
    report_path = _resolve_repo_path(args.report)
    try:
        raw = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Refused("OBSERVATION_REPORT_UNREADABLE", f"{report_path}: {exc}")
    try:
        report = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Refused("OBSERVATION_REPORT_UNREADABLE", f"{report_path}: invalid JSON: {exc.msg}")
    if not isinstance(report, dict):
        raise Refused("OBSERVATION_REPORT_UNREADABLE", f"{report_path}: must be a JSON object")
    paper_declarations.validate_observation_report(report)
    satisfied = sorted(
        fact for fact, entry in report.items() if isinstance(entry, dict) and entry.get("satisfied")
    )
    return {"validated": True, "facts": sorted(report.keys()), "satisfied": satisfied}


def cmd_resolve(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    config = paper_resolve.load_config()
    result = paper_resolve.resolve_identifier(
        args.identifier, resolver=args.resolver, role=args.role, config=config,
    )
    paper_resolve.cache_metadata(paper_dir, result)
    return result


def cmd_bib(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    records = paper_evidence.read_all_records(paper_dir)
    result = paper_bib.build_refs_bib(paper_dir, records)
    tex_path = paper_block.resolve_main_tex(paper_dir)
    reciprocal = paper_bib.check_reciprocal(
        tex_path.read_bytes(), (paper_dir / "refs.bib").read_bytes(),
    )
    return {**result, "reciprocal": reciprocal}


def _round_for_new_record(existing_records: list[dict]) -> int:
    return max((record.get("round", 0) for record in existing_records), default=0) + 1


def _build_evidence_record(args: argparse.Namespace, round_number: int) -> paper_evidence.EvidenceRecord:
    if args.quote and args.source_md:
        span = paper_evidence.EvidenceSpan.locate(Path(args.source_md), args.quote)
        if args.verdict == "holds":
            verdict = paper_evidence.Verdict.holds(span)
        elif args.verdict == "does-not-hold":
            verdict = paper_evidence.Verdict.does_not_hold(span)
        else:
            raise Refused(
                "VALIDATE_VERDICT_REQUIRED",
                "a located --quote/--source-md requires --verdict holds|does-not-hold",
            )
    else:
        verdict = paper_evidence.Verdict.insufficient(args.reason or "no --quote/--source-md given")
    return paper_evidence.EvidenceRecord.from_verdict(
        block_id=args.block, regime=_resolve_regime(args, "none"), claim=args.claim,
        cite_key=args.cite_key or "", identifier=args.identifier or "",
        resolver=args.resolver or "", metadata_digest=args.metadata_digest or "",
        verdict=verdict, round=round_number,
    )


def _resolve_regime(args: argparse.Namespace, fallback: str | None) -> str | None:
    """`--regime` wins when given explicitly; otherwise, when `--section-md`
    names an already-headered `sections/*.md` fixture, the regime is READ
    from that file's own contract for `--block` (`paper_validate.
    read_citations_regime` — real caller, not only the unit tests that
    exercise it directly). `fallback` (a `--sentence` JSON's own embedded
    `"regime"`, if any) is used only when neither of the above is given.
    """
    if args.regime:
        return args.regime
    if args.section_md:
        return paper_validate.read_citations_regime(Path(args.section_md), args.block)
    return fallback


def cmd_validate(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)

    if args.sentence:
        sentence_obj = json.loads(Path(args.sentence).read_text(encoding="utf-8"))
        citations = tuple(
            paper_validate.Citation(
                text=entry["text"], position=entry["position"],
                attached_to_object=bool(entry.get("attached_to_object", False)),
                is_noun_phrase=bool(entry.get("is_noun_phrase", False)),
            )
            for entry in sentence_obj.get("citations", [])
        )
        sentence = paper_validate.Sentence(text=sentence_obj["text"], citations=citations)
        regime = _resolve_regime(args, sentence_obj.get("regime"))
        paper_validate.validate_placement(regime, sentence)

    if args.claim:
        existing = paper_evidence.read_records(paper_dir, args.block)
        round_number = args.round if args.round is not None else _round_for_new_record(existing)
        record = _build_evidence_record(args, round_number)
        guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
        paper_evidence.append_record(paper_dir, record, guidance_dir=guidance_dir)

    records = paper_evidence.read_records(paper_dir, args.block)
    claims = sorted({record["claim"] for record in records})
    body = None
    if args.body is not None:
        body = sys.stdin.buffer.read() if args.body == "-" else Path(args.body).read_bytes()
    return paper_validate.finalize_block(paper_dir, args.block, claims, records, body)


def compute_plan(paper_dir: Path, *, guidance_dir: Path, sections_dir: Path | None = None) -> dict:
    """The pure aggregation `plan` reports: every `guidance/` folder's
    class or `unclassified`; the whole `declarations` region body (fill
    and fixed state, per record); and every written block's provenance
    state — `current`, `drifted`, or `unprovenanced` (design.md, `plan
    Aggregates Registry, Declarations, and Provenance`).

    Never writes — `read_registry`, `read_region` and `status` are all
    read-only, and `drift` only compares digests. Takes `paper_dir` and
    `guidance_dir` directly (not `--paper`/`--guidance` strings) so a test
    can inject both without going through argparse's own resolution, the
    same separation `paper_readiness.compute_readiness` already keeps from
    its own `cmd_readiness` wrapper.

    `sections_dir` (corrective batch, `the-paper-carries-its-own-decisions`
    verify FAIL, CRITICAL): reopening a fact/declaration a written block
    depends on used to leave `plan` reporting that block `current` forever
    — `paper_declarations.affected_blocks`, the pure function the spec's
    own "Reopening Invalidates Exactly the Blocks That Named It"
    requirement names as the reopen scan, had exactly one caller in the
    whole repository: its own isolated test. Optional and defaulted to
    `None` so the two pre-existing `PlanTests` that never built a section
    corpus keep passing unchanged; every real invocation (`cmd_plan` below)
    always resolves and passes one. When given, a block is ALSO reported
    `drifted` (never a new state name — `plan`'s three-state vocabulary is
    unchanged) when `affected_blocks(corpus, id)` names it for some
    declarations-region record whose own `generation` — bumped by both
    `declare` and `--reopen` — is newer than the generation this block's
    provenance was written against. This is a strict superset of "reopened
    since": a reopen-then-redeclare with a new value also invalidates a
    dependent block's provenance, correctly, since the block was written
    against a value that no longer holds; `plan` never rewrites `main.tex`
    or either region under any of this, unchanged from before.
    """
    guidance_report = paper_guidance.read_registry(guidance_dir)

    tex_path = paper_block.resolve_main_tex(paper_dir)
    main_tex_bytes = tex_path.read_bytes()

    declarations_record = paper_region.read_region(main_tex_bytes, "declarations")
    declarations_body = (
        declarations_record["body"] if declarations_record is not None
        else {"generation": 0, "records": []}
    )

    provenance_record = paper_region.read_region(main_tex_bytes, "provenance")
    provenance_entries = (
        provenance_record["body"]["records"] if provenance_record is not None else []
    )

    # The generation, per block id, above which that block's own recorded
    # provenance generation is stale -- 0 (never stale) unless some record
    # this block's contract names was touched at a strictly later
    # generation. Computed once, up front, from every declarations record
    # in one pass over `affected_blocks`, rather than re-deriving the
    # corpus per block below.
    stale_since_generation: dict[str, int] = {}
    if sections_dir is not None:
        corpus = paper_graph.assemble_corpus(sections_dir)
        for declaration_entry in declarations_body["records"]:
            record_generation = declaration_entry.get("generation", 0)
            if record_generation <= 0:
                continue
            for affected_id in paper_declarations.affected_blocks(
                corpus, declaration_entry["id"]
            ):
                if record_generation > stale_since_generation.get(affected_id, 0):
                    stale_since_generation[affected_id] = record_generation

    status = paper_block.status(main_tex_bytes)
    provenance_report = []
    for block in status["blocks"]:
        block_id = block["id"]
        entry = next((e for e in provenance_entries if e["block"] == block_id), None)
        if entry is None:
            provenance_report.append({"block": block_id, "state": "unprovenanced"})
            continue
        digest_drifted = paper_provenance.drift(main_tex_bytes, block_id, Path(entry["contract"]))
        generation_drifted = stale_since_generation.get(block_id, 0) > entry.get("generation", 0)
        provenance_report.append({
            "block": block_id,
            "state": "drifted" if (digest_drifted or generation_drifted) else "current",
        })

    return {
        "guidance": guidance_report,
        "declarations": declarations_body,
        "provenance": provenance_report,
    }


def cmd_plan(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    return compute_plan(paper_dir, guidance_dir=guidance_dir, sections_dir=sections_dir)


def _resolve_repo_path(raw: str) -> Path:
    """Resolves a caller-supplied `--draft`/`--audit`/`--transcript` operand
    against the real repository root, reusing `paper_scaffold.FORGE_ROOT`
    containment and its `PAPER_OUTSIDE_REPOSITORY` refusal (`design.md`,
    Threat Matrix: Path containment) — never a second, freshly-invented code
    for the same condition."""
    root = paper_scaffold.FORGE_ROOT.resolve()
    target = Path(raw).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise Refused(
            "PAPER_OUTSIDE_REPOSITORY", f"{target} does not resolve inside the repository root {root}"
        )
    return target


def cmd_write(args: argparse.Namespace) -> dict:
    """`write`: reconciles an already-shuttled redactor draft and
    contract-auditor account against one block's real contract, evidence
    set and mode, and either substitutes the block or reports why not
    (`writing-orchestration` spec). Never drafts, never audits, never
    spawns anything (`design.md`, Decision D2) — `--draft`/`--audit` are
    JSON envelopes an agent already produced; `--transcript`, when given,
    is only containment-checked and recorded, never parsed for judgment.
    `--style`, when given, is the style-sampler's JSON account; it is
    residency-verified and recorded as `R` here, then the eight-token
    tripwire (`paper_leak.check_tripwire`) runs against the styled draft
    inside `write_block` before `substitute`, never only importable and
    unreachable (`style-leak-detection` spec, `Requirement: The
    Eight-Token Tripwire`).
    """
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    draft_path = _resolve_repo_path(args.draft)
    audit_path = _resolve_repo_path(args.audit)
    if args.transcript:
        _resolve_repo_path(args.transcript)

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    audit_account = json.loads(audit_path.read_text(encoding="utf-8"))

    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    section_path = sections_dir / f"{args.section}.md"
    header, body = paper_contract.parse(section_path.read_bytes())
    block = next(b for b in header.blocks if b["id"] == args.block)
    mode_obj = paper_contract.resolve_mode(header, block)
    mode = mode_obj["value"] if mode_obj is not None else None

    evidence_set = ()
    if args.evidence:
        evidence_set = tuple(json.loads(Path(args.evidence).read_text(encoding="utf-8")))

    style_set = ()
    if args.style:
        proposals = json.loads(Path(args.style).read_text(encoding="utf-8"))
        guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
        recorded, _no_equivalent = paper_style.resolve_style_set(guidance_dir, proposals)
        style_set = tuple(recorded)

    contract = paper_write.BlockContract(
        block_id=args.block,
        contract_prose=body.decode("utf-8"),
        contract_source=str(section_path),
        citations_regime=block["citations"],
        mode=mode,
        requires_facts=tuple(block["requires_facts"]),
        evidence_set=evidence_set,
        style_set=style_set,
    )
    return paper_write.write_block(paper_dir, contract, draft, audit_account)


def cmd_render(args: argparse.Namespace) -> dict:
    """`render`: compiles `paper/Figures/<id>.tex` standalone, exactly once
    per call (`authored-diagram` spec, `Requirement: Standalone Compile`).
    `--latexmk-path` is injectable ONLY for tests (`paper_latex.compile`'s
    own `path` kwarg); omitted, `shutil.which` searches the real `PATH`.

    `--acknowledge-reset` takes the OTHER branch entirely: the explicit
    operator acknowledgement that clears a spent ledger (`authored-diagram`
    spec, `Scenario: Acknowledgement clears the ledger`) — never combined
    with a compile in the same call, so a reset is always its own,
    unambiguous act.
    """
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    if args.acknowledge_reset:
        paths = paper_figure.figure_paths(paper_dir, args.figure_id)
        return paper_figure.acknowledge_reset(paths, args.figure_id)

    result = paper_figure.render(paper_dir, args.figure_id, path=args.latexmk_path)
    if args.section and args.block:
        result["obligations"] = _check_obligations(paper_dir, args)
    return result


def _resolve_expected_components(paper_dir: Path, fact_id: str) -> list:
    """Derives the Components Check's expected list from `components_from`'s
    named fact's own declared resolution — never an operator-supplied CLI
    flag (corrective amendment, `a-diagram-that-compiles-or-says-why`'s own
    verify FAIL: `--expected-components` let a wrong list be supplied for a
    block whose diagram was never that one fact's own list, silently
    inverting the check; removed rather than left reachable). Reads through
    `paper_declarations.read_fact` — the SAME `declarations` region
    `declare --fact` writes.

    Refuses `COMPONENTS_FACT_UNRESOLVED` (work-state) when the fact was
    never declared, or was reopened and not yet redeclared.  Refuses
    `COMPONENTS_FACT_NOT_A_LIST` (work-state) when its resolution does not
    parse as a JSON array of strings — the declared resolution for a fact
    a `figure:` object names via `components_from` MUST be exactly that
    array, in the order the diagram must show it when `ordered: true`.
    """
    resolution = paper_declarations.read_fact(paper_dir, fact_id)
    if resolution is None:
        raise Refused(
            "COMPONENTS_FACT_UNRESOLVED",
            f"figure.components_from names {fact_id!r}, which has not been declared — "
            f"run `declare --fact {fact_id} --value '[\"...\"]'` first",
        )
    try:
        parsed = json.loads(resolution)
    except json.JSONDecodeError as exc:
        raise Refused(
            "COMPONENTS_FACT_NOT_A_LIST",
            f"{fact_id!r}'s declared resolution is not valid JSON: {exc}",
        )
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise Refused(
            "COMPONENTS_FACT_NOT_A_LIST",
            f"{fact_id!r}'s declared resolution must be a JSON array of strings, got {parsed!r}",
        )
    return parsed


def _check_obligations(paper_dir: Path, args: argparse.Namespace) -> dict:
    """Optional, real caller of `paper_obligation.py`'s checks — run only
    when `--section`/`--block` are given alongside `render`
    (`diagram-obligation` spec: obligations are read off the contract's own
    `figure:` declaration, never known).

    The Components Check runs ONLY when the block's `figure.components_from`
    names a fact — `_parse_figure` made this subkey optional precisely
    because it is a claim that one fact's own value IS the diagram's full
    expected component list, and that claim only holds when the diagram
    truly is one fact's own list by contract (section 01: the methods
    diagram's components are the contribution list). For a block whose
    diagram is a composite crossing over several categories of content
    (section 02's closing diagram: data, methods, axes, metrics,
    qualitative instruments, the repetition unit), no single fact is that
    list — such a block declares NO `components_from` at all, and no
    Components Check runs for it; `check_excluded`/`check_caption`/
    `check_mandatory`/separation still do.

    Also checks separation against every SIBLING `<other_id>.diagram.json`
    already under `paper/Figures/` — the cross-diagram intersection
    `check_shared_components` exists for, with no second CLI argument
    needed: every other diagram this figure could collide with is already
    on disk.
    """
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    section_path = sections_dir / f"{args.section}.md"
    header, _body = paper_contract.parse(section_path.read_bytes())
    block = next(b for b in header.blocks if b["id"] == args.block)
    figure = block["figure"]
    if figure is None:
        return {"checked": False, "reason": f"{args.block!r} declares no figure: obligation"}

    paths = paper_figure.figure_paths(paper_dir, args.figure_id)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    manifest_components = manifest.get("components", [])

    if figure["components_from"] is not None:
        expected = _resolve_expected_components(paper_dir, figure["components_from"])
        paper_obligation.check_components(figure, manifest_components, expected)
    paper_obligation.check_excluded(figure, manifest_components)
    paper_obligation.check_caption(
        figure, manifest_components, manifest.get("encodings", []), manifest.get("caption", ""),
    )
    paper_obligation.check_mandatory(figure, paths["pdf"].is_file(), args.block, manifest_components)

    sibling_components = {args.figure_id: manifest_components}
    for sibling_manifest_path in sorted(paths["tex"].parent.glob("*.diagram.json")):
        sibling_id = sibling_manifest_path.name[: -len(".diagram.json")]
        if sibling_id == args.figure_id:
            continue
        sibling_manifest = json.loads(sibling_manifest_path.read_text(encoding="utf-8"))
        sibling_components[sibling_id] = sibling_manifest.get("components", [])
    paper_obligation.check_shared_components(sibling_components)

    return {"checked": True}


def cmd_verify(args: argparse.Namespace) -> dict:
    """`verify`: a pure, read-only report over the five cross-section
    couplings, citation integrity, and contract currency
    (`coupling-verification`/`citation-integrity`/`contract-currency`
    specs). Never writes a byte, under any input, including a refusal
    (`block-substitution` spec, `Requirement: verify Verb Is Registered
    And Read-Only`) -- `paper_coupling_evidence.gather` performs every
    disk read this needs; `paper_verify.run` is pure over the result.
    """
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    evidence = paper_coupling_evidence.gather(paper_dir, sections_dir)
    return paper_verify.run(evidence)


def cmd_place(args: argparse.Namespace) -> dict:
    """`place`: places an already-measured figure's PDF — compiles nothing,
    requires provenance naming the run (`authored-diagram` spec,
    `Requirement: Data-Figure Boundary`)."""
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    return paper_figure.place_figure(
        paper_dir, args.figure_id, Path(args.pdf), Path(args.provenance),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scaffold = sub.add_parser("scaffold", help="create/re-enter paper/ idempotently")
    p_scaffold.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )

    p_status = sub.add_parser("status", help="report the block table, read-only")
    p_status.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )

    p_open = sub.add_parser("open", help="insert an empty block pair, never content")
    p_open.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_open.add_argument("--block", required=True, help="block id to open")
    p_open.add_argument("--after", default=None, help="insert immediately after this block's end marker")
    p_open.add_argument("--at-end", action="store_true", help="insert at the end of the document")

    p_substitute = sub.add_parser("substitute", help="replace one block's body, or adopt a hand edit")
    p_substitute.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_substitute.add_argument("--block", required=True, help="block id to substitute")
    p_substitute.add_argument("--body", default=None, help="path to the new body, or - for stdin")
    p_substitute.add_argument(
        "--adopt", action="store_true",
        help="accept the on-disk body as the new baseline; rewrites the digest, never the body",
    )
    p_substitute.add_argument(
        "--contract", default=None,
        help="record this substitution's provenance against this contract file's current digest",
    )

    p_contract = sub.add_parser(
        "contract", help="validate the section corpus, or show one file's parsed header",
    )
    p_contract.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_contract.add_argument(
        "--file", default=None,
        help="show this one file's parsed header instead of validating the whole corpus",
    )

    p_readiness = sub.add_parser(
        "readiness", help="per-block writable/blocked given satisfied facts and declarations",
    )
    p_readiness.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_readiness.add_argument(
        "--fact", action="append", default=None,
        help="a satisfied fact id; repeatable",
    )
    p_readiness.add_argument(
        "--declaration", action="append", default=None,
        help="a satisfied declaration id; repeatable",
    )

    p_order = sub.add_parser("order", help="derive the writing order from the block graph")
    p_order.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )

    p_declare = sub.add_parser(
        "declare",
        help="record a declaration or fact resolution, or reopen a fixed one",
    )
    p_declare.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_declare.add_argument("--declaration", default=None, help="a declaration id to record")
    p_declare.add_argument("--fact", default=None, help="a fact id to record a resolution for")
    p_declare.add_argument("--reopen", default=None, help="an id to clear the fixed state of")
    p_declare.add_argument(
        "--value", default=None,
        help="the value (--declaration) or resolution (--fact) to record",
    )

    p_observe = sub.add_parser(
        "observe",
        help="validate an insumos-observer report against the observable-fact schema, read-only",
    )
    p_observe.add_argument(
        "--report", required=True,
        help="path to the insumos-observer JSON report to validate; must resolve inside the repository root",
    )

    p_resolve = sub.add_parser(
        "resolve",
        help="resolve one identifier's metadata through a named connector, keyless",
    )
    p_resolve.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_resolve.add_argument("--identifier", required=True, help="DOI or arXiv id to resolve")
    p_resolve.add_argument(
        "--resolver", required=True, choices=paper_resolve.RESOLVERS,
        help="which connector to resolve through",
    )
    p_resolve.add_argument(
        "--role", default="resolution", choices=paper_resolve.ROLES,
        help="which papersmith.yaml connector role this call is validated against",
    )

    p_bib = sub.add_parser("bib", help="paper/refs.bib management -- never hand-typed")
    bib_sub = p_bib.add_subparsers(dest="bib_command", required=True)
    p_bib_build = bib_sub.add_parser(
        "build", help="rebuild refs.bib whole, sorted, from cached resolved metadata only",
    )
    p_bib_build.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )

    p_validate = sub.add_parser(
        "validate",
        help="the single gate: submit one judged verdict, check round-bounded satisfaction, write on success",
    )
    p_validate.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_validate.add_argument("--block", required=True, help="block id this evidence/write targets")
    p_validate.add_argument("--claim", default=None, help="claim text this call submits evidence for")
    p_validate.add_argument("--quote", default=None, help="the verbatim quote to locate in --source-md")
    p_validate.add_argument("--source-md", default=None, help="the ingested .md the quote is located in")
    p_validate.add_argument(
        "--verdict", default=None, choices=("holds", "does-not-hold"),
        help="the agent's own judgment for a located --quote; omit --quote/--source-md for insufficient",
    )
    p_validate.add_argument("--reason", default=None, help="why the record is insufficient")
    p_validate.add_argument("--cite-key", default=None, help="the \\cite{} key this record supports")
    p_validate.add_argument("--identifier", default=None, help="the resolved DOI/arXiv id")
    p_validate.add_argument("--resolver", default=None, help="which connector resolved --identifier")
    p_validate.add_argument("--metadata-digest", default=None, help="the cached resolution's own digest")
    p_validate.add_argument("--regime", default=None, choices=paper_vocabulary.CITATIONS_REGIMES)
    p_validate.add_argument(
        "--section-md", default=None,
        help="an already-headered sections/*.md path to read --block's citations regime from",
    )
    p_validate.add_argument("--round", type=int, default=None, help="override the auto-derived round number")
    p_validate.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )
    p_validate.add_argument("--body", default=None, help="path to the candidate body, or - for stdin")
    p_validate.add_argument(
        "--sentence", default=None,
        help="path to a JSON {text, regime, citations:[...]} object; checked before any evidence step",
    )

    p_plan = sub.add_parser(
        "plan", help="read-only: guidance classes, declaration/fact fill state, provenance state",
    )
    p_plan.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_plan.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )
    p_plan.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )

    p_write = sub.add_parser(
        "write",
        help="judge an already-drafted, already-audited block: reconcile, then substitute or report why not",
    )
    p_write.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_write.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_write.add_argument("--section", required=True, help="the sections/<id>.md stem this block belongs to")
    p_write.add_argument("--block", required=True, help="block id to write")
    p_write.add_argument(
        "--draft", required=True,
        help="path to the redactor's JSON envelope: {latex, bindings}; must resolve inside the repository root",
    )
    p_write.add_argument(
        "--audit", required=True,
        help="path to the contract-auditor's JSON envelope: {verdicts}; must resolve inside the repository root",
    )
    p_write.add_argument(
        "--evidence", default=None,
        help="path to a JSON array of {id, regime, ...} evidence records this block may bind against",
    )
    p_write.add_argument(
        "--style", default=None,
        help="path to a JSON array of the style-sampler's {reference, source_md, span} proposals; "
             "residency-verified and recorded as R before the tripwire runs against the styled draft",
    )
    p_write.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )
    p_write.add_argument(
        "--transcript", default=None,
        help="path to a recorded agent transcript; containment-checked, never parsed for judgment",
    )

    p_render = sub.add_parser(
        "render", help="compile one diagram id standalone, exactly once, via latexmk",
    )
    p_render.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_render.add_argument("--figure-id", required=True, help="the diagram id under paper/Figures/")
    p_render.add_argument(
        "--latexmk-path", default=None,
        help="test-only: override the PATH shutil.which searches for latexmk",
    )
    p_render.add_argument(
        "--acknowledge-reset", action="store_true",
        help="explicit operator acknowledgement: clears this id's spent repair-budget ledger, compiles nothing",
    )
    p_render.add_argument(
        "--section", default=None,
        help="run obligation checks after compiling: the sections/<id>.md stem --block belongs to",
    )
    p_render.add_argument(
        "--block", default=None, help="the block id whose figure: obligation to check after compiling",
    )
    p_render.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )

    p_verify = sub.add_parser(
        "verify",
        help="read-only report over the couplings, citation integrity and contract currency",
    )
    p_verify.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_verify.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )

    p_place = sub.add_parser(
        "place", help="place an already-measured figure's PDF; compiles nothing, needs provenance",
    )
    p_place.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_place.add_argument("--figure-id", required=True, help="the diagram id under paper/Figures/")
    p_place.add_argument("--pdf", required=True, help="path to the already-produced PDF")
    p_place.add_argument(
        "--provenance", required=True,
        help="path to a JSON record naming the run this figure was measured from",
    )

    return parser


COMMANDS = (
    "scaffold", "status", "open", "substitute", "contract", "readiness", "order", "declare", "observe",
    "plan", "resolve", "bib", "validate", "write", "render", "place", "verify",
)
_COMMANDS = {
    "scaffold": cmd_scaffold,
    "status": cmd_status,
    "open": cmd_open,
    "substitute": cmd_substitute,
    "contract": cmd_contract,
    "readiness": cmd_readiness,
    "order": cmd_order,
    "declare": cmd_declare,
    "observe": cmd_observe,
    "plan": cmd_plan,
    "resolve": cmd_resolve,
    "bib": cmd_bib,
    "validate": cmd_validate,
    "write": cmd_write,
    "render": cmd_render,
    "place": cmd_place,
    "verify": cmd_verify,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = _COMMANDS[args.command](args)
    except Refused as exc:
        print(json.dumps({"status": "refused", "code": exc.code, "detail": exc.detail}))
        return 2
    print(json.dumps({"status": "ok", "command": args.command, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
