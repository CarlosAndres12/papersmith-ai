#!/usr/bin/env python3
"""paper_cli.py — front door for the `paper-writing` skill.

Standard library only, keyless, offline, fail-closed — the shape of
`implementation_cli.py` and `remote_cli.py`. One JSON object on stdout per
invocation. Exit 0 means the command ran; exit 2 means a guard refused
before touching disk.

Wires nine verbs: `scaffold`, `open`, `status`, `substitute` (from
`only-the-block-changes`; `substitute` grew an optional `--contract <path>`
in Slice C1 of `the-paper-carries-its-own-decisions`, recording provenance
without changing what bytes get written); `contract`, `readiness`, `order`
(from `the-contract-is-data-not-code`); and `declare`, `plan` (from
`the-paper-carries-its-own-decisions`, Slices B and C2 — appended
afterwards, their entries disjoint from both prior changes' own, so any
landing order merges). Left extensible on purpose; nothing here assumes it
is the last verb this file will ever grow.
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


def compute_plan(paper_dir: Path, *, guidance_dir: Path) -> dict:
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

    status = paper_block.status(main_tex_bytes)
    provenance_report = []
    for block in status["blocks"]:
        block_id = block["id"]
        entry = next((e for e in provenance_entries if e["block"] == block_id), None)
        if entry is None:
            provenance_report.append({"block": block_id, "state": "unprovenanced"})
            continue
        drifted = paper_provenance.drift(main_tex_bytes, block_id, Path(entry["contract"]))
        provenance_report.append({
            "block": block_id,
            "state": "drifted" if drifted else "current",
        })

    return {
        "guidance": guidance_report,
        "declarations": declarations_body,
        "provenance": provenance_report,
    }


def cmd_plan(args: argparse.Namespace) -> dict:
    paper_dir = paper_scaffold.resolve_paper_dir(args.paper)
    guidance_dir = paper_guidance.resolve_guidance_dir(args.guidance)
    return compute_plan(paper_dir, guidance_dir=guidance_dir)


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

    return parser


COMMANDS = (
    "scaffold", "status", "open", "substitute", "contract", "readiness", "order", "declare", "plan",
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
