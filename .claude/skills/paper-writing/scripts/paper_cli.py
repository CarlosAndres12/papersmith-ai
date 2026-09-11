#!/usr/bin/env python3
"""paper_cli.py — front door for the `paper-writing` skill.

Standard library only, keyless, offline, fail-closed — the shape of
`implementation_cli.py` and `remote_cli.py`. One JSON object on stdout per
invocation. Exit 0 means the command ran; exit 2 means a guard refused
before touching disk.

Wires eleven verbs: `scaffold`, `open`, `status`, `substitute` (from
`only-the-block-changes`; `substitute` grew an optional `--contract <path>`
in Slice C1 of `the-paper-carries-its-own-decisions`, recording provenance
without changing what bytes get written); `contract`, `readiness`, `order`
(from `the-contract-is-data-not-code`); `declare`, `plan` (from
`the-paper-carries-its-own-decisions`, Slices B and C2); and `resolve`,
`bib build` (from `no-claim-without-a-source-that-holds-it`, WU1/WU2 —
`resolve` is the one path that makes this CLI not offline end to end,
keyless and behind a role `papersmith.yaml` can empty; `bib build` rebuilds
`refs.bib` whole from cached resolved metadata only). Left extensible on
purpose; nothing here assumes it is the last verb this file will ever grow.
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
    # --- header schema and insertion (paper_contract.py) ------------------
    "MALFORMED_HEADER": WORK_STATE,
    "HEADER_PRESENT": WORK_STATE,
    "BODY_MUTATED": WORK_STATE,
    "SECTIONS_OUTSIDE_REPOSITORY": INVOCATION_DEFECT,
    # --- corpus assembly and order (paper_graph.py) -----------------------
    "ID_COLLISION": WORK_STATE,
    "ORDER_CYCLE": WORK_STATE,
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
    # --- observation report validation (paper_declarations.py; consumed by
    # a human reading `insumos-observer`'s report, never called from a
    # cmd_* root here, but reachable through the whole-module scan the
    # roster derivation already performs on every imported module) ------
    "NOT_AN_OBSERVABLE_FACT": INVOCATION_DEFECT,
    "EVIDENCE_CONFLATED": INVOCATION_DEFECT,
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

    return parser


COMMANDS = (
    "scaffold", "status", "open", "substitute", "contract", "readiness", "order", "declare", "plan",
    "resolve", "bib",
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
    "plan": cmd_plan,
    "resolve": cmd_resolve,
    "bib": cmd_bib,
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
