#!/usr/bin/env python3
"""paper_cli.py — front door for the `paper-writing` skill.

Standard library only, keyless, offline, fail-closed — the shape of
`implementation_cli.py` and `remote_cli.py`. One JSON object on stdout per
invocation. Exit 0 means the command ran; exit 2 means a guard refused
before touching disk.

Wires twenty-four verbs: `scaffold`, `open`, `status`, `substitute` (from
`only-the-block-changes`; `substitute` grew an optional `--contract <path>`
in Slice C1 of `the-paper-carries-its-own-decisions`, recording provenance
without changing what bytes get written); `contract`, `readiness`, `order`
(from `the-contract-is-data-not-code` — the section-contract reader);
`declare`, `observe`, `plan` (from `the-paper-carries-its-own-decisions`,
Slices B and C2 — `observe` validates an `insumos-observer` report against
the observable-fact schema before a human runs `declare` against it);
`resolve`, `full_text`, `bib build`, `validate` (from `no-claim-without-a-
source-that-holds-it`, WU1/WU2/WU3, and `the-pdf-arrives-or-the-operator-
is-told` for `full_text` — `resolve` is the one path that makes this CLI
not offline end to end, keyless and behind a role `papersmith.yaml` can
empty; `full_text` fills the sibling `full-text` role the same way,
fetching an already-resolved record's own PDF from its cached metadata's
measured `full_text_url` and placing it loose under `guidance/<section-
id>/` for `paper-ingestion` to find; `bib build` rebuilds `refs.bib` whole
from cached resolved metadata only; `validate` is the single gate deciding
verdict, placement and the bounded search-round budget before any block
reaches disk, now counting each claim's DISTINCT source papers against a
configurable minimum (`paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM`,
`the-pdf-arrives-or-the-operator-is-told`, item 2), never bare record
count); `write` (from `the-
writer-may-assert-only-what-it-was-given` — a judge, never an invoker: it
reconciles an already-shuttled redactor draft and contract-auditor account
against one block's real contract, evidence set and mode, and either
substitutes the block or reports why not, with exactly one bounded
re-draft); `render`, `place` (from `a-diagram-that-compiles-or-says-why` —
a diagram that compiles standalone or says why, the repair-budget ledger,
and the data-figure boundary); `verify` (from `the-couplings-hold-or-they-
do-not` — a read-only report over five cross-section couplings, citation
integrity and contract currency; resolves the corpus's own optional-block
ids and threads them into `paper_verify.run`, so an unopened `optional:
true` block excuses a coupling as `unmeasured` rather than failing it); and
`phases`, `skeleton`, `packet` (from `the-phases-are-derived-not-
remembered` — `phases` reports each Kahn wave's own readiness basis and
gates `write` against it, `PHASE_NOT_READY`; `skeleton` infers Related Work
/ dataset-placement decisions straight from disk and opens every
non-excluded block id in derived order, once, never re-asking,
`SKELETON_ANSWER_REQUIRED`/`SKELETON_ALREADY_DECIDED`; `packet` assembles
one block's own contract prose plus, per `style-reference` guidance folder,
a heading OUTLINE only — offsets, never inlined span text — ahead of
`write`'s draft stage); and `reuse`, `exhaustion` (from
`a-leftover-paper-is-offered-before-it-is-lost` — two read-only reports
over the ingested-papers lifecycle: `reuse` names, for one block's own
still-open claims, which already-ingested `evidence`-classed papers carry
no verdict yet; `exhaustion` is the corpus-wide report of which papers now
carry a `does-not-hold` against every open claim in the whole corpus —
`paper_lifecycle.py` does every real read; this file only resolves paths
and threads `--min-sources` through. Neither verb ever deletes anything —
the operator deletes by hand, per the operator's own ruling). Left
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
import paper_couplings  # noqa: E402 -- the-skill-stops-trusting-memory, item 4: the producer `paper/couplings.json` never had; `couplings` verb
import paper_full_text  # noqa: E402 -- the-pdf-arrives-or-the-operator-is-told: fills the full-text role; `full_text` verb
import paper_lifecycle  # noqa: E402 -- a-leftover-paper-is-offered-before-it-is-lost: the reuse and exhaustion reports over the ingested-papers lifecycle; `reuse`/`exhaustion` verbs; raises no `Refused` of its own

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
    # --- the-phases-are-derived-not-remembered, unit 6: `readiness` gains a
    # basis (design.md D3) and `phases` owns "what can I write now" (this
    # file, `cmd_readiness`/`cmd_phases`) -----------------------------------
    "READINESS_BASIS_REQUIRED": INVOCATION_DEFECT,
    "PHASE_NOT_READY": WORK_STATE,
    # --- the-phases-are-derived-not-remembered, unit 7: `skeleton`'s two
    # blocking questions, asked exactly once, and the disk-inferred
    # dataset-placement conflict (design.md D4; this file's `cmd_skeleton`,
    # `paper_declarations.infer_dataset_placement`) -----------------------
    "SKELETON_ANSWER_REQUIRED": INVOCATION_DEFECT,
    "SKELETON_ALREADY_DECIDED": WORK_STATE,
    "DATASET_PLACEMENT_CONFLICT": WORK_STATE,
    # --- the-skill-stops-trusting-memory, item 1: dataset placement is
    # derived from the corpus's own `requires_facts`/`optional` shape,
    # never a literal id pair (paper_declarations.
    # dataset_placement_candidates) -------------------------------------
    "DATASET_PLACEMENT_CANDIDATE_ABSENT": WORK_STATE,
    "DATASET_PLACEMENT_CANDIDATE_AMBIGUOUS": WORK_STATE,
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
    # --- the-skill-stops-trusting-memory, item 2/3: the guidance registry's
    # own classification gates `validate --source-md` for the first time
    # (paper_cli._guard_source_md_classification) ---------------------------
    "SOURCE_STYLE_REFERENCE": WORK_STATE,
    "SOURCE_NOT_EVIDENCE": WORK_STATE,
    # --- the-phases-are-derived-not-remembered, unit 8: `packet`'s own
    # outline assembly over ingested guidance markdown (paper_guidance.
    # read_markdown_outline) -- reachable the instant that raise site
    # exists, `paper_guidance.py` already being an ahead-of-its-own-verb
    # import (design.md D5) --------------------------------------------
    "GUIDANCE_MARKDOWN_UNREADABLE": WORK_STATE,
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
    "DECLINE_REASON_REQUIRED": INVOCATION_DEFECT,
    "CONDITION_REQUIRED": INVOCATION_DEFECT,
    "CONDITION_MALFORMED": WORK_STATE,
    "UNKNOWN_CONDITION_TYPE": WORK_STATE,
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
    # --- the-skill-stops-trusting-memory, item 5: observe reconciles the
    # agent's own report against a real disk measurement this process takes
    # itself (paper_declarations.source_available/reconcile_observation_
    # report), gitignore-blind by construction -- never the agent's word
    # alone -------------------------------------------------------------
    "OBSERVATION_DISK_CONFLICT": WORK_STATE,
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
    # --- the-pdf-arrives-or-the-operator-is-told: fills the full-text role
    # (paper_full_text.py) -- `RESOLVER_ROLE_EMPTY`/`RESOLVER_UNREACHABLE`/
    # `IDENTIFIER_UNRESOLVED` above are reused verbatim, never a second code
    # for the same condition ---------------------------------------------
    "METADATA_NOT_CACHED": WORK_STATE,
    "FULL_TEXT_URL_ABSENT": WORK_STATE,
    "FULL_TEXT_NOT_A_PDF": WORK_STATE,
    "CITE_KEY_MALFORMED": INVOCATION_DEFECT,
    "FULL_TEXT_FILE_PRESENT": WORK_STATE,
    # --- the bibliography that cannot be typed (paper_bib.py; WU2) ------
    "ENTRY_UNSOURCED": WORK_STATE,
    "CITE_WITHOUT_ENTRY": WORK_STATE,
    "ENTRY_WITHOUT_CITE": WORK_STATE,
    # --- no-citation-before-its-paper-is-ingested, item 2: resolved is not
    # ingested (paper_bib._require_ingested) -------------------------------
    "ENTRY_NOT_INGESTED": WORK_STATE,
    # --- no-citation-before-its-paper-is-ingested, item 3: `write`'s own
    # citation-readiness gate (this file, `_guard_section_citations_ready`) -
    "CITATION_FOLDER_ABSENT": WORK_STATE,
    "CITATION_NOT_INGESTED": WORK_STATE,
    "CITATION_FOLDER_UNCLASSIFIED": WORK_STATE,
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
    # --- the-skill-stops-trusting-memory, item 4: `couplings` is the
    # producer `paper/couplings.json` never had (paper_couplings.py) -------
    "COUPLINGS_INPUT_UNREADABLE": INVOCATION_DEFECT,
    "COUPLINGS_RECORD_MALFORMED": WORK_STATE,
    # --- a-fact-is-declared-or-it-is-produced, unit 1: `produces_facts`
    # joins the header grammar (`paper_contract.py`) and three assemble-
    # time checks land in `paper_graph.py` -- self-reference, route
    # exclusivity against the declarable route
    # (`paper_declarations.OBSERVABLE_FACTS ∪ STRUCTURAL_FACTS`), and
    # duplicate-producer (corroborated pairs an existing
    # coupling-verification check names, e.g. `gap` / Coupling 3, are
    # legal; every other duplicate still refuses). Unit 2 adds
    # `FACT_PRODUCER_ABSENT` (consumption-relative totality: a fact some
    # block requires resolves via `FACT_SOURCE_ROOT` or a producer, else
    # refuses) and `PRODUCER_CHAIN_ABSENT` (every one of a fact's
    # producer(s) must reach the consumer in the `after`-edge graph). ----
    "FACT_SELF_REQUIRED": WORK_STATE,
    "FACT_ROUTE_AMBIGUOUS": WORK_STATE,
    "FACT_PRODUCER_DUPLICATE": WORK_STATE,
    "FACT_PRODUCER_ABSENT": WORK_STATE,
    "PRODUCER_CHAIN_ABSENT": WORK_STATE,
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


def compute_readiness_report(
    sections_dir: Path,
    *,
    paper_dir: Path | None = None,
    flag_facts: frozenset = frozenset(),
    flag_declarations: frozenset = frozenset(),
) -> dict:
    """The basis dispatch `readiness` reports, kept separate from `cmd_
    readiness`'s own `--paper`/`--sections` string resolution -- the same
    separation `compute_plan` already keeps from `cmd_plan`
    (`the-phases-are-derived-not-remembered`, design.md D3, tasks.md 6.4).

    `paper_dir` given -> basis `"declaration-backed"`: satisfied sets are
    read from the `declarations` region (`paper_declarations.read_
    satisfied`), merged with `flag_facts`/`flag_declarations` on top (any
    flag-given id not already recorded on disk is reported separately,
    under `"supposed"` -- design.md D3's own "each labelled `source:
    supposed`"), and `opened_blocks` is resolved from `main.tex` (`paper_
    block.read_status`) so `not-applicable` can fire for an optional,
    unopened block. This closes the regression where `cmd_readiness` never
    opened `main.tex`, so its answer never changed after `declare`.

    `paper_dir` omitted, with at least one flag given -> the hypothetical
    what-if preserved exactly as it behaved before this unit, basis
    `"supposed-only"`.

    Neither given -> refuses `READINESS_BASIS_REQUIRED`: the stale-number
    path (computing an answer from flags alone while silently ignoring an
    existing `declarations` region) is removed, never defaulted.
    """
    corpus = paper_graph.assemble_corpus(sections_dir)
    flag_facts = set(flag_facts)
    flag_declarations = set(flag_declarations)

    if paper_dir is not None:
        declared_facts, declared_declarations = paper_declarations.read_satisfied(paper_dir)
        declined_facts = paper_declarations.read_declined(paper_dir)
        opened_blocks = {block["id"] for block in paper_block.read_status(paper_dir)["blocks"]}
        satisfied_facts = declared_facts | flag_facts
        satisfied_declarations = declared_declarations | flag_declarations
        basis = "declaration-backed"
    elif flag_facts or flag_declarations:
        declared_facts = set()
        declared_declarations = set()
        declined_facts = {}
        opened_blocks = None
        satisfied_facts = flag_facts
        satisfied_declarations = flag_declarations
        basis = "supposed-only"
    else:
        raise Refused(
            "READINESS_BASIS_REQUIRED",
            "readiness needs either --paper <dir> (reads the declarations region) "
            "or at least one --fact/--declaration flag (a hypothetical what-if); "
            "a bare call with neither has no basis to compute an answer from.",
        )

    report = paper_readiness.compute_readiness(
        corpus,
        satisfied_facts=satisfied_facts,
        satisfied_declarations=satisfied_declarations,
        opened_blocks=opened_blocks,
        basis=basis,
        declined_facts=declined_facts,
    )
    result = {"basis": basis, "blocks": report}
    if basis == "declaration-backed":
        supposed = sorted((flag_facts | flag_declarations) - (declared_facts | declared_declarations))
        if supposed:
            result["supposed"] = supposed
    return result


def cmd_readiness(args: argparse.Namespace) -> dict:
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper) if args.paper else None
    return compute_readiness_report(
        sections_dir,
        paper_dir=paper_dir,
        flag_facts=frozenset(args.fact or []),
        flag_declarations=frozenset(args.declaration or []),
    )


def cmd_order(args: argparse.Namespace) -> dict:
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    corpus = paper_graph.assemble_corpus(sections_dir)
    edge_set = paper_graph.collect_edges(corpus)
    order = paper_graph.derive_order(corpus, edge_set)
    return {"order": order, "danglingEdges": sorted(set(edge_set.dangling))}


def _skeleton_excluded_ids(corpus, *, related_work: bool, dataset_in: str) -> set:
    """The block ids `skeleton` leaves unopened for the given answers
    (design.md D4; tasks.md 7.8): every `related-work` block when Related
    Work is "no", and every dataset-placement candidate
    (`paper_declarations.dataset_placement_candidates`) NOT sitting in the
    chosen section. Every other block id is opened unconditionally.

    Derives which candidate belongs to which section from the corpus
    itself -- never a literal `mm-dataset`/`es-dataset` id pair (the
    `a-fact-source-nobody-checks` corrective: those two ids used to be
    hardcoded here, via `paper_declarations.MM_DATASET_ID`/`ES_DATASET_ID`,
    a violation of this skill's own "block ids are shape only" invariant).
    """
    excluded: set = set()
    if not related_work:
        excluded |= set(corpus.order_by_section.get("related-work", ()))
    candidates = paper_declarations.dataset_placement_candidates(corpus)
    chosen_section = (
        "materials-and-methods" if dataset_in == "materials" else "experimental-setup"
    )
    excluded |= {qid for section, qid in candidates.items() if section != chosen_section}
    return excluded


def build_skeleton(
    paper_dir: Path, sections_dir: Path, *, related_work: str | None, dataset_in: str | None,
) -> dict:
    """`skeleton`'s own logic, taking `paper_dir`/`sections_dir` directly —
    the same separation `compute_phases`/`compute_readiness_report` keep
    from their own `cmd_*` wrappers — so a test can inject both without
    going through argparse's own resolution (design.md D4;
    `specs/skeleton-startup/spec.md`).

    Asks nothing itself — the orchestrator asks the two blocking questions
    exactly once — and opens every non-excluded block id through `paper_
    block.open_block` alone, in `derive_order` order: never a new writer,
    so the byte-identity invariant `open_block` already carries is
    untouched (tasks.md 7.13, Threat Matrix "Write amplification into
    `main.tex`").

    Refuses `SKELETON_ANSWER_REQUIRED` (invocation-defect) when either
    `related_work` or `dataset_in` is `None`. Once any corpus block is
    already opened, both decisions are re-derived straight from disk
    (`paper_declarations.infer_skeleton_decisions` — never a stored flag,
    design.md D4) and compared against the given answers: a contradiction
    refuses `SKELETON_ALREADY_DECIDED` (work-state) naming both what disk
    already records and what was requested. Already-opened ids are skipped
    — idempotent, never re-opened, never re-asked.
    """
    if related_work is None or dataset_in is None:
        missing = [
            flag for flag, value in (
                ("--related-work", related_work), ("--dataset-in", dataset_in),
            )
            if value is None
        ]
        raise Refused(
            "SKELETON_ANSWER_REQUIRED",
            "skeleton needs both --related-work yes|no and --dataset-in "
            f"materials|experimental-setup; missing {missing}",
        )

    corpus = paper_graph.assemble_corpus(sections_dir)

    related_work_flag = related_work == "yes"
    requested_placement = (
        "materials-and-methods" if dataset_in == "materials" else "experimental-setup"
    )

    status = paper_block.read_status(paper_dir)
    opened_ids = {block["id"] for block in status["blocks"]}

    if opened_ids:
        decided = paper_declarations.infer_skeleton_decisions(paper_dir, corpus)
        dataset_mismatch = (
            decided["datasetPlacement"] != "undecided"
            and decided["datasetPlacement"] != requested_placement
        )
        if decided["relatedWork"] != related_work_flag or dataset_mismatch:
            raise Refused(
                "SKELETON_ALREADY_DECIDED",
                f"disk already records relatedWork={decided['relatedWork']!r}, "
                f"datasetPlacement={decided['datasetPlacement']!r}; the given flags "
                f"(relatedWork={related_work_flag!r}, datasetPlacement={requested_placement!r}) "
                "contradict it",
            )

    excluded = _skeleton_excluded_ids(corpus, related_work=related_work_flag, dataset_in=dataset_in)
    edge_set = paper_graph.collect_edges(corpus)
    order = paper_graph.derive_order(corpus, edge_set)

    opened = []
    for qualified_id in order:
        if qualified_id in excluded or qualified_id in opened_ids:
            continue
        paper_block.open_block(paper_dir, qualified_id, at_end=True)
        opened_ids.add(qualified_id)
        opened.append(qualified_id)

    return {
        "relatedWork": related_work_flag,
        "datasetPlacement": requested_placement,
        "opened": opened,
    }


def cmd_skeleton(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    return build_skeleton(
        paper_dir, sections_dir, related_work=args.related_work, dataset_in=args.dataset_in,
    )


def cmd_declare(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    modes_given = [
        flag for flag in ("declaration", "fact", "reopen", "decline") if getattr(args, flag, None)
    ]
    if not modes_given:
        raise Refused(
            "DECLARE_MODE_REQUIRED",
            "exactly one of --declaration <id>, --fact <id>, --reopen <id>, --decline <id> is required.",
        )
    if len(modes_given) > 1:
        raise Refused(
            "DECLARE_MODE_CONFLICT",
            f"{modes_given} were given together; exactly one mode is required.",
        )
    if args.reopen:
        return paper_declarations.reopen(paper_dir, args.reopen)
    if args.decline:
        condition = None
        if args.condition is not None:
            try:
                condition = json.loads(args.condition)
            except json.JSONDecodeError as exc:
                raise Refused("CONDITION_MALFORMED", f"--condition is not valid JSON: {exc.msg}")
        return paper_declarations.decline_fact(paper_dir, args.decline, args.reason, condition)
    if args.value is None:
        raise Refused(
            "DECLARE_VALUE_REQUIRED",
            "--declaration/--fact requires --value <the recorded value or resolution>.",
        )
    if args.declaration:
        return paper_declarations.set_declaration(paper_dir, args.declaration, args.value)
    return paper_declarations.set_fact(paper_dir, args.fact, args.value)


def compute_observation(
    report_path: Path, *,
    proposals_dir: Path | None = None, experiments_dir: Path | None = None,
    implementation_dir: Path | None = None,
) -> dict:
    """`observe`'s own logic, taking already-resolved paths directly — the
    same separation `compute_plan`/`compute_readiness_report`/`build_
    skeleton` keep from their own `cmd_*` wrappers, so a test can inject
    every root without going through argparse's own defaulting.

    Validates an already-produced `insumos-observer` report against the
    observable-fact schema and the `implementation`/`results`
    evidence-conflation guard, THEN reconciles it against a real disk
    measurement THIS process takes itself
    (`paper_declarations.source_available`, gitignore-blind by construction
    — `the-skill-stops-trusting-memory`, item 5) for every root given.
    Read-only: never calls `declare`, never writes anything, regardless of
    outcome.

    Refuses `OBSERVATION_DISK_CONFLICT` (work-state) when the report claims
    a fact UNSATISFIED with no evidence while that fact's own source root
    is measurably non-empty right now (`paper_declarations.
    reconcile_observation_report`) — a disagreement is named, never
    averaged into a report that simply trusts the agent's word. A root not
    given here (most commonly `implementation_dir`, which has no fixed
    default) is never measured and never reconciled against — this refuses
    only what it can actually prove wrong, never what it merely suspects.
    """
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

    measured = {}
    for name, root in (
        ("proposals", proposals_dir), ("experiments", experiments_dir),
        ("implementation", implementation_dir),
    ):
        if root is not None:
            measured[name] = paper_declarations.source_available(root)

    disagreements = paper_declarations.reconcile_observation_report(report, measured)
    if disagreements:
        raise Refused(
            "OBSERVATION_DISK_CONFLICT",
            f"the report disagrees with what this process measured on disk: {disagreements}",
        )

    satisfied = sorted(
        fact for fact, entry in report.items() if isinstance(entry, dict) and entry.get("satisfied")
    )
    return {
        "validated": True, "facts": sorted(report.keys()), "satisfied": satisfied,
        "measured": measured,
    }


def cmd_observe(args: argparse.Namespace) -> dict:
    """`observe`: the CLI front door for `compute_observation` — resolves
    `--report` (required) and `--proposals`/`--experiments`/
    `--implementation` (each optional, none defaulted) against the real
    repository root before delegating.

    None of the three roots defaults to this repository's own top-level
    folder: `proposals/`/`experiments/` are long-lived, ongoing project
    directories in this repository's own real layout, routinely non-empty
    for reasons unrelated to any one paper's current facts, so silently
    defaulting to them would reconcile against content that says nothing
    about THIS observation and misfire (measured against this very
    repository, 2026-09-18: both are non-empty right now). Reconciliation
    only ever fires for a root the caller explicitly names, matching
    `--implementation`'s own always-optional treatment.
    """
    report_path = _resolve_repo_path(args.report)
    proposals_dir = _resolve_repo_path(args.proposals) if args.proposals else None
    experiments_dir = _resolve_repo_path(args.experiments) if args.experiments else None
    implementation_dir = _resolve_repo_path(args.implementation) if args.implementation else None
    return compute_observation(
        report_path, proposals_dir=proposals_dir, experiments_dir=experiments_dir,
        implementation_dir=implementation_dir,
    )


def cmd_resolve(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    config = paper_resolve.load_config()
    result = paper_resolve.resolve_identifier(
        args.identifier, resolver=args.resolver, role=args.role, config=config,
    )
    paper_resolve.cache_metadata(paper_dir, result)
    return result


def cmd_full_text(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    config = paper_resolve.load_config()
    return paper_full_text.fetch_full_text(
        paper_dir, guidance_dir, section_id=args.section, metadata_digest=args.metadata_digest,
        cite_key=args.cite_key, config=config,
    )


def cmd_bib(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    records = paper_evidence.read_all_records(paper_dir)
    result = paper_bib.build_refs_bib(paper_dir, records, guidance_dir=guidance_dir)
    tex_path = paper_block.resolve_main_tex(paper_dir)
    reciprocal = paper_bib.check_reciprocal(
        tex_path.read_bytes(), (paper_dir / "refs.bib").read_bytes(),
    )
    return {**result, "reciprocal": reciprocal}


def _round_for_new_record(existing_records: list[dict]) -> int:
    return max((record.get("round", 0) for record in existing_records), default=0) + 1


def _guard_source_md_classification(source_md: Path, guidance_dir: Path) -> None:
    """`the-skill-stops-trusting-memory`, item 2/3: `guidance/`'s per-folder
    classification (`paper_guidance.CLASSES`) is enforced here for the
    first time -- `plan` only ever echoed it back before this.

    Refuses `SOURCE_STYLE_REFERENCE` (work-state) when `source_md` resolves
    inside a folder the registry classes `style-reference`: that class
    feeds STYLE only, never content, and a quote lifted from one is not
    evidence no matter how well it locates (`style-channel` spec). Refuses
    `SOURCE_NOT_EVIDENCE` (work-state) when `source_md` resolves inside a
    guidance folder classed anything else (`unclassified`, or a future
    class outside `{"style-reference", "evidence"}`) -- `evidence` is the
    one class this gate accepts, its own real consequence rather than a
    label with nothing wired to it. A `source_md` that does not resolve
    under `guidance_dir` at all (`classify_source_md` returns `None`) is
    outside this gate's business and is never refused here.
    """
    source_class = paper_guidance.classify_source_md(source_md, guidance_dir)
    if source_class is None:
        return
    if source_class == "style-reference":
        raise Refused(
            "SOURCE_STYLE_REFERENCE",
            f"{source_md} resolves inside a guidance folder classed 'style-reference'; "
            "style-reference feeds style only, never a quote submitted as evidence",
        )
    if source_class != "evidence":
        raise Refused(
            "SOURCE_NOT_EVIDENCE",
            f"{source_md} resolves inside a guidance folder classed {source_class!r}, "
            "not 'evidence'; classify the folder before quoting it as evidence",
        )


def _build_evidence_record(
    args: argparse.Namespace, round_number: int, guidance_dir: Path,
) -> paper_evidence.EvidenceRecord:
    if args.quote and args.source_md:
        source_md_path = Path(args.source_md)
        _guard_source_md_classification(source_md_path, guidance_dir)
        span = paper_evidence.EvidenceSpan.locate(source_md_path, args.quote)
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
        guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
        record = _build_evidence_record(args, round_number, guidance_dir)
        paper_evidence.append_record(paper_dir, record, guidance_dir=guidance_dir)

    records = paper_evidence.read_records(paper_dir, args.block)
    claims = sorted({record["claim"] for record in records})
    body = None
    if args.body is not None:
        body = sys.stdin.buffer.read() if args.body == "-" else Path(args.body).read_bytes()
    explicit_min_sources = getattr(args, "min_sources", None)
    min_sources = (
        explicit_min_sources if explicit_min_sources is not None
        else paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM
    )
    return paper_validate.finalize_block(
        paper_dir, args.block, claims, records, body, min_sources=min_sources,
    )


def _compute_provenance_report(
    main_tex_bytes: bytes, status: dict, declarations_body: dict, corpus: "paper_graph.Corpus | None",
) -> list:
    """The `current`/`drifted`/`unprovenanced` per-block state, extracted
    from `compute_plan` (`the-phases-are-derived-not-remembered`, tasks.md
    6.9) so `phases` reads the SAME computation `plan` already proved end
    to end (`ReopenInvalidatesProvenanceEndToEndTests`), never a second one
    that could drift from it. Byte-identical to `compute_plan`'s own
    pre-extraction body; `corpus` is `None` exactly when `compute_plan`'s
    own `sections_dir` is omitted, preserving its two pre-existing callers
    that never built a section corpus.
    """
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
    if corpus is not None:
        for declaration_entry in declarations_body["records"]:
            record_generation = declaration_entry.get("generation", 0)
            if record_generation <= 0:
                continue
            for affected_id in paper_declarations.affected_blocks(
                corpus, declaration_entry["id"]
            ):
                if record_generation > stale_since_generation.get(affected_id, 0):
                    stale_since_generation[affected_id] = record_generation

    report = []
    for block in status["blocks"]:
        block_id = block["id"]
        entry = next((e for e in provenance_entries if e["block"] == block_id), None)
        if entry is None:
            report.append({"block": block_id, "state": "unprovenanced"})
            continue
        digest_drifted = paper_provenance.drift(main_tex_bytes, block_id, Path(entry["contract"]))
        generation_drifted = stale_since_generation.get(block_id, 0) > entry.get("generation", 0)
        report.append({
            "block": block_id,
            "state": "drifted" if (digest_drifted or generation_drifted) else "current",
        })
    return report


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

    status = paper_block.status(main_tex_bytes)
    corpus = paper_graph.assemble_corpus(sections_dir) if sections_dir is not None else None
    provenance_report = _compute_provenance_report(main_tex_bytes, status, declarations_body, corpus)

    result = {
        "guidance": guidance_report,
        "declarations": declarations_body,
        "provenance": provenance_report,
    }
    if corpus is not None:
        # item 1 (`no-citation-before-its-paper-is-ingested`): every
        # section-shaped guidance folder's own citation status, additive to
        # `guidance` above -- `corpus.sections` is the parsed corpus's own
        # set of section ids, never a hand-listed tuple.
        result["sectionGuidance"] = paper_guidance.section_citation_folders(
            guidance_dir, corpus.sections,
        )
    return result


def cmd_plan(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    return compute_plan(paper_dir, guidance_dir=guidance_dir, sections_dir=sections_dir)


def _unwritten_required_blocks(corpus, wave: list, opened_blocks: set) -> list:
    """Non-optional blocks in `wave` that are not yet opened -- unit 3's
    absence semantics: an unopened `optional` block never blocks a wave
    (tasks.md 6b.2). Extracted out of `compute_phases`'s own gate loop
    (unit 6) so `cmd_write`'s write-path gate (unit 6b) shares the exact
    same definition of "written" rather than a second one that could
    drift from it.
    """
    return sorted(
        qualified_id for qualified_id in wave
        if not corpus.blocks[qualified_id].optional and qualified_id not in opened_blocks
    )


def _refuse_on_incomplete_waves(
    waves: list, corpus, opened_blocks: set, up_to_index: int, *, blocked_label: str,
) -> None:
    """Raises `PHASE_NOT_READY` naming the first still-incomplete wave
    among `waves[:up_to_index]` and its unwritten non-optional blocks.
    `blocked_label` names what is being gated -- a phase number for
    `compute_phases`'s own `--phase N`, a qualified block id for
    `cmd_write`'s write-path gate -- in the refusal detail. ONE gate
    computation (tasks.md 6b.1's own instruction: "do not write a second
    one"), two callers below.
    """
    for index, wave in enumerate(waves[:up_to_index]):
        unwritten = _unwritten_required_blocks(corpus, wave, opened_blocks)
        if unwritten:
            raise Refused(
                "PHASE_NOT_READY",
                f"wave {index + 1} is not complete ({unwritten} still unwritten); "
                f"{blocked_label} cannot proceed until every wave before it is complete",
            )


def _resolve_write_gate(paper_dir: Path, sections_dir: Path, qualified_id: str) -> None:
    """`cmd_write`'s own phase gate (tasks.md 6b.1-6b.2; `specs/writing-
    phases/spec.md`, `Requirement: Phase N Is Gated On Phase N-1`, whose
    own scenarios name `write` -- the verb unit 6 left unwired). Runs
    BEFORE any draft/audit file is opened, before `paper_write.write_
    block`'s own attempt ledger is touched, and before any byte reaches
    `main.tex` -- a block must never burn a judge-cycle attempt on a
    refusal that has nothing to do with its draft.

    Resolves `qualified_id`'s own Kahn wave via `paper_graph.derive_
    waves` and calls `_refuse_on_incomplete_waves`, the SAME gate
    computation `compute_phases`'s own `--phase N` refusal uses -- so
    `phases` and `write` can never disagree about what "not ready" means
    (Unit 6's own Notes flagged exactly this drift; this closes it).

    A `qualified_id` the corpus's own waves do not contain (a typo'd
    `--section`/`--block`, or a block the section header does not
    declare) is left to `cmd_write`'s existing downstream lookup to
    refuse on its own terms -- this gate only ever narrows what CAN
    proceed, it never invents a refusal for a condition it was not asked
    to police.
    """
    corpus = paper_graph.assemble_corpus(sections_dir)
    edge_set = paper_graph.collect_edges(corpus)
    waves = paper_graph.derive_waves(corpus, edge_set)

    wave_index = next((index for index, wave in enumerate(waves) if qualified_id in wave), None)
    if wave_index is None:
        return

    tex_path = paper_block.resolve_main_tex(paper_dir)
    status = paper_block.status(tex_path.read_bytes())
    opened_blocks = {block["id"] for block in status["blocks"]}

    _refuse_on_incomplete_waves(
        waves, corpus, opened_blocks, wave_index,
        blocked_label=f"{qualified_id!r} (wave {wave_index + 1})",
    )


def compute_phases(paper_dir: Path, sections_dir: Path, *, phase: int | None = None) -> dict:
    """`phases`: the read-only "what can I write now" report `readiness`
    alone never answered -- `compute_readiness` had exactly one caller
    (`cmd_readiness`) before this unit (design.md D3). Takes `paper_dir`/
    `sections_dir` directly, the same separation `compute_plan` keeps from
    `cmd_plan`.

    Waves come from `paper_graph.derive_waves`; per-block readiness from
    `paper_readiness.compute_readiness` under basis `"declaration-backed"`;
    `opened` from `paper_block.status`; provenance state from the SAME
    computation `plan` already proved end to end
    (`_compute_provenance_report`, extracted from `compute_plan` this unit
    -- never a second one that could drift from it). The top-level
    `"declared"` key echoes exactly the two sets `paper_declarations.read_
    satisfied` returned -- direct, auditable proof that a `declare` write
    is seen, never inferred only from a block's own `missing_facts`
    shrinking.

    Open Question 2 (design.md), resolved here: an `unprovenanced` block
    still counts as WRITTEN for the wave gate below -- the gate reads
    `opened` (bare `main.tex` block presence) alone, never provenance
    state. Provenance currency (`drifted`/`unprovenanced`) is attached per
    block purely for the operator's own visibility and stays `plan`'s
    separately-reported concern; conflating it with wave-gating would
    block writing on a documentation gap, not a missing dependency
    (tasks.md 6.2).

    `phase` given -> refuses `PHASE_NOT_READY`, before any output is built,
    naming the first still-incomplete wave among waves `1..phase-1` and its
    unwritten non-optional blocks (via the shared `_refuse_on_incomplete_
    waves`, unit 6b: `cmd_write`'s own write-path gate below calls the
    identical function, so this read-only report and the real write path
    can never disagree about what "not ready" means); only waves `1..phase`
    are then reported. `phase` omitted -> every wave is reported -- the
    full plan the operator approves once, before writing starts
    (`specs/writing-phases/spec.md`, `Requirement: The Operator Approves
    The Phase Plan Before Writing Starts`; unit 9 wires this report into
    `SKILL.md`'s own approval prose).
    """
    corpus = paper_graph.assemble_corpus(sections_dir)
    edge_set = paper_graph.collect_edges(corpus)
    waves = paper_graph.derive_waves(corpus, edge_set)

    tex_path = paper_block.resolve_main_tex(paper_dir)
    main_tex_bytes = tex_path.read_bytes()
    status = paper_block.status(main_tex_bytes)
    opened_blocks = {block["id"] for block in status["blocks"]}

    declarations_record = paper_region.read_region(main_tex_bytes, "declarations")
    declarations_body = (
        declarations_record["body"] if declarations_record is not None
        else {"generation": 0, "records": []}
    )
    provenance_report = _compute_provenance_report(main_tex_bytes, status, declarations_body, corpus)
    provenance_by_block = {entry["block"]: entry["state"] for entry in provenance_report}

    declared_facts, declared_declarations = paper_declarations.read_satisfied(paper_dir)
    declined_facts = paper_declarations.read_declined(paper_dir)
    readiness_report = paper_readiness.compute_readiness(
        corpus, satisfied_facts=declared_facts, satisfied_declarations=declared_declarations,
        opened_blocks=opened_blocks, basis="declaration-backed", declined_facts=declined_facts,
    )
    readiness_by_block = {entry["block"]: entry for entry in readiness_report}

    if phase is not None:
        _refuse_on_incomplete_waves(
            waves, corpus, opened_blocks, phase - 1, blocked_label=f"phase {phase}",
        )

    selected_waves = waves if phase is None else waves[:phase]

    wave_reports = []
    previous_complete = True
    for index, wave in enumerate(selected_waves):
        wave_complete = not _unwritten_required_blocks(corpus, wave, opened_blocks)
        if not previous_complete:
            wave_status = "gated"
        elif wave_complete:
            wave_status = "complete"
        else:
            wave_status = "open"
        wave_reports.append({
            "wave": index + 1,
            "status": wave_status,
            "blocks": [
                {
                    "block": qualified_id,
                    "status": readiness_by_block[qualified_id]["status"],
                    "missing_facts": readiness_by_block[qualified_id]["missing_facts"],
                    "missing_declarations": readiness_by_block[qualified_id]["missing_declarations"],
                    "declined_facts": readiness_by_block[qualified_id].get("declined_facts", []),
                    "stale_declines": readiness_by_block[qualified_id].get("stale_declines", []),
                    "optional": readiness_by_block[qualified_id]["optional"],
                    "opened": qualified_id in opened_blocks,
                    "provenance": provenance_by_block.get(qualified_id),
                }
                for qualified_id in wave
            ],
        })
        previous_complete = previous_complete and wave_complete

    return {
        "declared": {
            "facts": sorted(declared_facts),
            "declarations": sorted(declared_declarations),
        },
        "waves": wave_reports,
    }


def cmd_phases(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    return compute_phases(paper_dir, sections_dir, phase=args.phase)


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


def assemble_packet(sections_dir: Path, guidance_dir: Path, section: str, block_id: str) -> dict:
    """The redactor packet (`redactor-packet` spec; design.md Decision D5):
    one block's own section contract prose, verbatim, plus -- per `style-
    reference`-classed `guidance/` root -- every ingested paper's heading
    OUTLINE (`paper_guidance.read_markdown_outline`: `{title, level,
    byte_start, byte_end}`, never the span text itself). Read-only: never
    opens a reference `.md` for anything beyond computing its own outline,
    and never writes anything under any input, including every refusal
    path (tasks.md 8.14).

    This is the structural half of the leak guard the operator raised
    twice: the packet is physically incapable of carrying reference
    prose, because outlines are all it ever carries (design.md: "Rejected
    alternative -- the packet inlines each extracted section's text --
    puts an unaudited copy of reference prose in a file the redactor can
    read without ever passing residency verification or the eight-token
    tripwire"). The style-sampler agent reads this outline, picks the
    heading it judges equivalent, reads THAT span itself from the real
    file, and reports it; `paper_style.resolve_style_set` residency-
    verifies that account into `R` exactly as before -- this function
    never resolves a span and never calls `resolve_style_set` itself, so
    there is exactly one resolution path, not a second one this function
    could drift from (tasks.md 8.9).

    A `style-reference` root with no ingested papers under it (`paper_
    guidance.ingested_papers`), and a root the registry classes anything
    other than `style-reference`, both contribute nothing to `references`
    -- never a refusal (`redactor-packet` spec, `Scenario: A reference
    with no equivalent block contributes nothing` is the sampler's own
    later degrade; this is the same "contributes nothing, never refuses"
    shape one step earlier, over roots rather than resolved spans).
    """
    section_path = sections_dir / f"{section}.md"
    header, body = paper_contract.parse(section_path.read_bytes())
    next(b for b in header.blocks if b["id"] == block_id)

    registry = paper_guidance.read_registry(guidance_dir)
    style_roots = sorted(name for name, cls in registry.items() if cls == "style-reference")
    ingested = paper_guidance.ingested_papers(guidance_dir)

    references = []
    for root in style_roots:
        for paper in ingested.get(root, []):
            outline = paper_guidance.read_markdown_outline(Path(paper["markdown"]))
            references.append({
                "root": root,
                "folder": paper["folder"],
                "markdown": paper["markdown"],
                **outline,
            })

    return {
        "block": block_id,
        "section": section,
        "contract": body.decode("utf-8"),
        "references": references,
    }


def cmd_packet(args: argparse.Namespace) -> dict:
    """`packet`: the CLI's own front door onto `assemble_packet` (tasks.md
    8.6) -- read-only, so an operator/orchestrator session can shuttle a
    block's contract prose plus every reference paper's heading outline
    to the redactor and style-sampler agents by hand without risking
    dropping one of the channels ("Why this verb exists at all": no
    script in this skill may import `subprocess`, so the skill can never
    invoke either agent itself)."""
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    return assemble_packet(sections_dir, guidance_dir, args.section, args.block)


def _guard_section_citations_ready(guidance_dir: Path, section_id: str, regime: str) -> None:
    """`no-citation-before-its-paper-is-ingested`, item 3: `write` refuses
    while a citing block's own section citation folder
    (`guidance/<section-id>/`) is not fully ready -- downloaded, ingested,
    and classified (`paper_guidance.section_citation_status`). A `none`-
    regime block cites nothing and is never gated here
    (`paper_vocabulary.CITATIONS_REGIMES`; a `none`-regime block has no
    citations to gate no matter what `guidance/<section-id>/` looks like).

    Checked in this fixed order, one refusal per call -- the same shape
    `_guard_source_md_classification` already uses for `validate
    --source-md`: the folder must exist at all (`CITATION_FOLDER_ABSENT`);
    every PDF already placed in it must be ingested
    (`CITATION_NOT_INGESTED`, naming every pending PDF by name); and the
    folder itself must carry a real classification
    (`CITATION_FOLDER_UNCLASSIFIED`) -- `plan`'s own `guidance`/
    `sectionGuidance` registries enforced here as a real gate on `write`'s
    own citing path for the first time, rather than a label nothing
    consequences until `validate --source-md` sees one real quote.
    """
    if regime == "none":
        return
    status = paper_guidance.section_citation_status(guidance_dir, section_id)
    if not status["exists"]:
        raise Refused(
            "CITATION_FOLDER_ABSENT",
            f"guidance/{section_id}/ does not exist yet; download this section's cited PDFs there "
            f"so the paper-ingestion skill can turn them into evidence before {section_id} is drafted",
        )
    if status["pending_pdfs"]:
        raise Refused(
            "CITATION_NOT_INGESTED",
            f"guidance/{section_id}/ still holds un-ingested PDF(s) {status['pending_pdfs']}; "
            "run the paper-ingestion skill over this folder before writing a citing block",
        )
    if status["classification"] == "unclassified":
        raise Refused(
            "CITATION_FOLDER_UNCLASSIFIED",
            f"guidance/{section_id}/ carries no .paper-writing.json marker; classify it "
            '(e.g. {"class": "evidence"}) before writing a citing block',
        )


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

    Before any of that -- before `--draft`/`--audit` are even read off
    disk -- `_resolve_write_gate` refuses `PHASE_NOT_READY` when this
    block's own wave has an earlier, still-incomplete wave (tasks.md
    6b.1-6b.5; `specs/writing-phases/spec.md`, `Requirement: Phase N Is
    Gated On Phase N-1`). Unit 6 wired this refusal onto the read-only
    `phases` verb alone; `cmd_write` never consulted `derive_waves`, so a
    later wave could be written before an earlier one existed. This gate
    closes that gap: it runs before `write_block`'s own attempt ledger is
    touched and before any byte reaches `main.tex`, so a block never
    burns a judge-cycle attempt on a refusal unrelated to its draft.

    Immediately after that gate -- still before `--draft`/`--audit` are
    read, and before `assemble_packet` even runs -- `_guard_section_
    citations_ready` refuses when this block's own section citation folder
    (`guidance/<section-id>/`) is not fully ready: downloaded, ingested,
    classified (`no-citation-before-its-paper-is-ingested`, item 3). A
    `none`-regime block cites nothing and is never gated by this.

    Then `assemble_packet` runs for this exact block (`writing-
    orchestration` spec, `Requirement: Packet Assembly Precedes Draft`).
    Its own return value is not otherwise consumed here (the redactor's
    draft and the style-sampler's account both already reached `write`
    through their own established channels, `--draft`/`--style`); running
    it is the gate: a `style-reference` root whose ingested markdown
    cannot be read refuses `GUIDANCE_MARKDOWN_UNREADABLE` here, before the
    draft/audit stage is ever reached, rather than surfacing only later
    and possibly after a judge-cycle attempt was already spent.
    """
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    _resolve_write_gate(paper_dir, sections_dir, f"{args.section}.{args.block}")

    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)

    section_path = sections_dir / f"{args.section}.md"
    header, body = paper_contract.parse(section_path.read_bytes())
    block = next(b for b in header.blocks if b["id"] == args.block)

    _guard_section_citations_ready(guidance_dir, header.section, block["citations"])

    assemble_packet(sections_dir, guidance_dir, args.section, args.block)

    draft_path = _resolve_repo_path(args.draft)
    audit_path = _resolve_repo_path(args.audit)
    if args.transcript:
        _resolve_repo_path(args.transcript)

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    audit_account = json.loads(audit_path.read_text(encoding="utf-8"))

    mode_obj = paper_contract.resolve_mode(header, block)
    mode = mode_obj["value"] if mode_obj is not None else None

    evidence_set = ()
    if args.evidence:
        evidence_set = tuple(json.loads(Path(args.evidence).read_text(encoding="utf-8")))

    style_set = ()
    if args.style:
        proposals = json.loads(Path(args.style).read_text(encoding="utf-8"))
        recorded, _no_equivalent = paper_style.resolve_style_set(guidance_dir, proposals)
        style_set = tuple(recorded)

    contract = paper_write.BlockContract(
        block_id=args.block,
        contract_prose=body.decode("utf-8"),
        contract_source=str(section_path),
        citations_regime=block["citations"],
        mode=mode,
        requires_facts=paper_contract.requirement_values(block["requires_facts"]),
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


def _resolve_optional_block_ids(sections_dir: Path) -> frozenset:
    """The raw (unqualified) block ids `paper_verify.run` treats as
    `optional`, derived from the same corpus `cmd_verify` already reads
    through `paper_coupling_evidence.gather` (`paper_graph.assemble_corpus`)
    -- never a second, independently-maintained classification.

    `paper_verify.py` cannot resolve this itself: its own AST-enforced
    import allowlist (`tests/test_paper_writing.py`,
    `_PAPER_VERIFY_ALLOWED_IMPORTS = {"re"}`) forbids it from ever reading
    `sections_dir`, by design (`the-couplings-hold-or-they-do-not`'s own
    diskless-checks guarantee). Work Unit 3 built and proved
    `optional_block_ids` end to end but left this exact resolution
    unwired, naming `paper_cli.py`/`cmd_verify` as the one place that
    already holds `sections_dir` and calls `paper_verify.run` (tasks.md,
    Work Unit 9b) -- this is that resolution, one level up from the module
    that cannot perform it.

    An unreadable corpus resolves to an empty set: `gather`'s own
    `_blocks_by_fact` already reports `SECTION_CONTRACTS_UNREADABLE` for
    every fact in that case, so this helper never needs to raise a second
    time for the same condition -- an empty `optional_block_ids` changes no
    check's verdict beyond what `SECTION_CONTRACTS_UNREADABLE` already
    reports.
    """
    try:
        corpus = paper_graph.assemble_corpus(sections_dir)
    except Refused:
        return frozenset()
    return frozenset(record.block_id for record in corpus.blocks.values() if record.optional)


def cmd_couplings(args: argparse.Namespace) -> dict:
    """`couplings`: the producer `verify` never had
    (`the-skill-stops-trusting-memory`, item 4). Reads a JSON object from
    `--file <path|->`, validates its shape
    (`paper_couplings.validate_couplings_shape`), and writes it WHOLE and
    atomically to `paper/couplings.json` -- the same "rebuild, never
    append" shape `bib build` already uses for its own sibling untracked
    file.

    Refuses `COUPLINGS_INPUT_UNREADABLE` (invocation-defect) when `--file`
    cannot be read or does not parse as JSON. Refuses `COUPLINGS_RECORD_
    MALFORMED` (work-state) when it parses but does not carry the shape
    `verify`'s own checks read (`paper_couplings.validate_couplings_shape`)
    -- checked BEFORE a single byte is written, so a malformed record never
    reaches disk half-applied.
    """
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    if args.file == "-":
        raw = sys.stdin.read()
        source = "<stdin>"
    else:
        file_path = _resolve_repo_path(args.file)
        try:
            raw = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise Refused("COUPLINGS_INPUT_UNREADABLE", f"{file_path}: {exc}")
        source = str(file_path)
    try:
        record = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Refused("COUPLINGS_INPUT_UNREADABLE", f"{source}: invalid JSON: {exc.msg}")
    return paper_couplings.write_couplings(paper_dir, record)


def cmd_verify(args: argparse.Namespace) -> dict:
    """`verify`: a pure, read-only report over the five cross-section
    couplings, citation integrity, and contract currency
    (`coupling-verification`/`citation-integrity`/`contract-currency`
    specs). Never writes a byte, under any input, including a refusal
    (`block-substitution` spec, `Requirement: verify Verb Is Registered
    And Read-Only`) -- `paper_coupling_evidence.gather` performs every
    disk read this needs; `paper_verify.run` is pure over the result.

    `optional_block_ids` (`_resolve_optional_block_ids`, tasks.md Work Unit
    9b) is resolved from the same `sections_dir` corpus and threaded
    through, so an unopened `optional: true` block excuses the couplings
    that depend on it alone as `unmeasured`/`OPTIONAL_BLOCK_ABSENT` rather
    than reporting a false `fail` or `BLOCK_NOT_DECLARED`.
    """
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    sections_dir = paper_contract.resolve_sections_dir(args.sections)
    evidence = paper_coupling_evidence.gather(paper_dir, sections_dir)
    optional_block_ids = _resolve_optional_block_ids(sections_dir)
    return paper_verify.run(evidence, optional_block_ids=optional_block_ids)


def cmd_reuse(args: argparse.Namespace) -> dict:
    """`reuse`: `SKILL.md` capability A, read-only. For `--block`'s own
    open claims, names which already-ingested, `evidence`-classed papers
    carry no verdict yet for each one -- what stops the operator
    re-downloading a paper already on disk (`paper_lifecycle.reuse_report`,
    which does every real read; this wrapper only resolves `--paper`/
    `--guidance` and threads `--min-sources` through, the same shape
    `cmd_validate` already uses for `min_sources`)."""
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    min_sources = (
        args.min_sources if args.min_sources is not None
        else paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM
    )
    return paper_lifecycle.reuse_report(paper_dir, guidance_dir, args.block, min_sources=min_sources)


def cmd_exhaustion(args: argparse.Namespace) -> dict:
    """`exhaustion`: `SKILL.md` capability B, read-only and corpus-wide --
    never scoped to one section, since a paper ingested under any
    `evidence`-classed root is already citable from any block
    (`paper_lifecycle.exhaustion_report`). Lists the exhausted set and,
    for every other paper, the corpus-wide open claims it still carries no
    verdict for. Builds NO deletion of any kind -- the operator deletes by
    hand, per the operator's own 2026-09-19 ruling."""
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    min_sources = (
        args.min_sources if args.min_sources is not None
        else paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM
    )
    return paper_lifecycle.exhaustion_report(paper_dir, guidance_dir, min_sources=min_sources)


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
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root -- reads the "
        "declarations region for its satisfied sets (basis \"declaration-backed\")",
    )
    p_readiness.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_readiness.add_argument(
        "--fact", action="append", default=None,
        help="a satisfied fact id; repeatable -- a hypothetical addition when --paper is "
        "given, or the whole basis (\"supposed-only\") when it is not",
    )
    p_readiness.add_argument(
        "--declaration", action="append", default=None,
        help="a satisfied declaration id; repeatable, same basis rules as --fact",
    )

    p_phases = sub.add_parser(
        "phases",
        help="read-only: what can I write now -- waves with per-block readiness, opened, provenance",
    )
    p_phases.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_phases.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_phases.add_argument(
        "--phase", type=int, default=None,
        help="report only waves 1..N; refuses PHASE_NOT_READY if any wave before N is "
        "incomplete. Omitted: report every wave, the full plan awaiting approval",
    )

    p_skeleton = sub.add_parser(
        "skeleton",
        help="open every section/block id the two structural answers imply, empty, via open_block only",
    )
    p_skeleton.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_skeleton.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_skeleton.add_argument(
        "--related-work", default=None, choices=("yes", "no"),
        help="whether the manuscript carries a dedicated Related Work section; asked once",
    )
    p_skeleton.add_argument(
        "--dataset-in", default=None, choices=("materials", "experimental-setup"),
        help="where the dataset is described; asked once",
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
    p_declare.add_argument(
        "--decline", default=None,
        help="a fact id to record as declined -- the operator has decided it does not enter the paper for now",
    )
    p_declare.add_argument(
        "--reason", default=None,
        help="mandatory with --decline: why this fact is declined",
    )
    p_declare.add_argument(
        "--condition", default=None,
        help=(
            "mandatory with --decline: a JSON object naming a disk condition the "
            "skill re-checks on every later read, e.g. "
            '\'{"type": "directory-empty-except", "path": "experiments", "ignore": [".gitkeep"]}\''
        ),
    )

    p_observe = sub.add_parser(
        "observe",
        help="validate an insumos-observer report against the observable-fact schema, then "
             "reconcile it against a real disk measurement this process takes itself, read-only",
    )
    p_observe.add_argument(
        "--report", required=True,
        help="path to the insumos-observer JSON report to validate; must resolve inside the repository root",
    )
    p_observe.add_argument(
        "--proposals", default=None,
        help="proposals/ location, for the disk-truth reconciliation; no default -- omit to "
             "skip reconciling formulation/dataset against disk; must resolve inside the "
             "repository root",
    )
    p_observe.add_argument(
        "--experiments", default=None,
        help="experiments/ location, for the disk-truth reconciliation; no default -- omit to "
             "skip reconciling experimental-design against disk; must resolve inside the "
             "repository root",
    )
    p_observe.add_argument(
        "--implementation", default=None,
        help="the target implementation repository's own path, for the disk-truth "
             "reconciliation; no default -- omit to skip reconciling implementation/results "
             "against disk; must resolve inside the repository root",
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

    p_full_text = sub.add_parser(
        "full_text",
        help="fetch one already-resolved identifier's own PDF, keyless, from its cached "
             "metadata's measured full_text_url, and place it loose under guidance/<section>/",
    )
    p_full_text.add_argument(
        "--paper", default=None,
        help="override paper/ location (where --metadata-digest's cache lives); "
             "must resolve inside the repository root",
    )
    p_full_text.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )
    p_full_text.add_argument(
        "--section", required=True,
        help="the guidance/<section-id>/ this PDF lands loose inside",
    )
    p_full_text.add_argument(
        "--metadata-digest", required=True,
        help="the digest of an already-cached `resolve` result to fetch this record's PDF for",
    )
    p_full_text.add_argument(
        "--cite-key", required=True,
        help="the \\cite{} key this PDF supports; becomes the output filename's stem",
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
    p_bib_build.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
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
        "--min-sources", type=int, default=None,
        help="override the minimum DISTINCT source papers required per claim "
             "(default: paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM)",
    )
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

    p_couplings = sub.add_parser(
        "couplings",
        help="validate and write paper/couplings.json whole -- the producer verify's own "
             "declaration record never had",
    )
    p_couplings.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_couplings.add_argument(
        "--file", required=True,
        help="path to the JSON couplings record to validate and write, or - for stdin; "
             "a file path must resolve inside the repository root",
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

    p_packet = sub.add_parser(
        "packet",
        help="read-only: this block's own contract prose plus every style-reference "
             "paper's heading outline (offsets only, never reference prose)",
    )
    p_packet.add_argument("--section", required=True, help="the sections/<id>.md stem this block belongs to")
    p_packet.add_argument("--block", required=True, help="block id to assemble the packet for")
    p_packet.add_argument(
        "--sections", default=None,
        help="override sections/ location; must resolve inside the repository root",
    )
    p_packet.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )

    p_reuse = sub.add_parser(
        "reuse",
        help="read-only: for one block's open claims, which already-ingested, "
             "evidence-classed papers carry no verdict yet",
    )
    p_reuse.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_reuse.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )
    p_reuse.add_argument("--block", required=True, help="the block id whose open claims to report")
    p_reuse.add_argument(
        "--min-sources", type=int, default=None, dest="min_sources",
        help="distinct holds sources a claim needs before it is no longer open "
             "(default paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM)",
    )

    p_exhaustion = sub.add_parser(
        "exhaustion",
        help="read-only, corpus-wide: every evidence-classed ingested paper's exhaustion "
             "state -- lists only, never deletes",
    )
    p_exhaustion.add_argument(
        "--paper", default=None,
        help="override paper/ location; must resolve inside the repository root",
    )
    p_exhaustion.add_argument(
        "--guidance", default=None,
        help="override guidance/ location; must resolve inside the repository root",
    )
    p_exhaustion.add_argument(
        "--min-sources", type=int, default=None, dest="min_sources",
        help="distinct holds sources a claim needs before it is no longer open "
             "(default paper_validate.DEFAULT_MIN_SOURCES_PER_CLAIM)",
    )

    return parser


COMMANDS = (
    "scaffold", "status", "open", "substitute", "contract", "readiness", "phases", "skeleton", "order",
    "declare", "observe", "plan", "resolve", "full_text", "bib", "validate", "write", "render", "place",
    "couplings", "verify", "packet", "reuse", "exhaustion",
)
_COMMANDS = {
    "scaffold": cmd_scaffold,
    "status": cmd_status,
    "open": cmd_open,
    "substitute": cmd_substitute,
    "contract": cmd_contract,
    "readiness": cmd_readiness,
    "phases": cmd_phases,
    "skeleton": cmd_skeleton,
    "order": cmd_order,
    "declare": cmd_declare,
    "observe": cmd_observe,
    "plan": cmd_plan,
    "resolve": cmd_resolve,
    "full_text": cmd_full_text,
    "bib": cmd_bib,
    "validate": cmd_validate,
    "write": cmd_write,
    "render": cmd_render,
    "place": cmd_place,
    "couplings": cmd_couplings,
    "verify": cmd_verify,
    "packet": cmd_packet,
    "reuse": cmd_reuse,
    "exhaustion": cmd_exhaustion,
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
