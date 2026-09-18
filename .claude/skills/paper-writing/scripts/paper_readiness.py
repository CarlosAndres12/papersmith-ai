"""paper_readiness: per-block readiness given satisfied facts and
declarations.

Separable from `paper_graph.py` because readiness and order are two
different questions — back matter proves they differ: zero missing facts
(it requires none), every declaration missing (design.md, `Internal
layering`).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_graph  # noqa: E402


def _iter_blocks_in_declared_order(corpus: "paper_graph.Corpus"):
    """Sections by `position`, blocks within a section in declaration
    order — a stable, human-readable iteration order for a report. Never
    used for the writing order itself, which is `paper_graph.derive_order`'s
    job alone."""
    for section_id in sorted(corpus.sections, key=lambda sid: corpus.sections[sid].position):
        for qualified_id in corpus.order_by_section[section_id]:
            yield corpus.blocks[qualified_id]


def compute_block_readiness(
    block,
    satisfied_facts: set,
    satisfied_declarations: set,
    *,
    opened: bool | None = None,
    basis: str = "supposed-only",
) -> dict:
    """Given one `BlockRecord`, report `writable`/`blocked`/`not-applicable`
    naming each still-missing fact and declaration separately. A block whose
    facts are all satisfied but whose declarations are not reports
    `blocked`, never `writable` (`writing-readiness` spec, `Requirement:
    Per-Block Readiness`).

    `optional` is read verbatim off `block.optional`
    (`optional-block-semantics` spec, `Requirement: Readiness Reports The
    Optional Flag`).

    `opened` and `basis` are pure inputs, never a disk read performed here.
    `not-applicable` fires only when the block is `optional`, `opened is
    False` (a caller who does not know openness at all passes `opened=None`,
    which never triggers it), and `basis == "declaration-backed"` — the
    fork the paper chose not to take, not merely a fork this call happens
    not to have satisfied yet. Under `basis="supposed-only"` (the default,
    and `cmd_readiness`'s own flags-only call today), the status is always
    computed from `missing_facts`/`missing_declarations` exactly as before
    this function grew these two keyword-only parameters — `cmd_readiness`
    itself calls this with neither argument, so its behaviour is unchanged.

    `basis="declaration-backed"` and real `opened` values are not resolved
    anywhere yet — that resolution (reading `main.tex`'s opened block ids,
    behind a `readiness --paper` invocation) is Work Unit 6's job
    (`READINESS_BASIS_REQUIRED`, design.md D3). This function accepts the
    values so that caller can be wired later with no change to this
    function's shape (tasks.md, Work Unit 3, 3.2)."""
    missing_facts = [fact for fact in block.requires_facts if fact not in satisfied_facts]
    missing_declarations = [
        declaration for declaration in block.requires_declarations
        if declaration not in satisfied_declarations
    ]
    if block.optional and basis == "declaration-backed" and opened is False:
        status = "not-applicable"
    else:
        status = "writable" if not missing_facts and not missing_declarations else "blocked"
    return {
        "block": block.qualified_id,
        "status": status,
        "missing_facts": missing_facts,
        "missing_declarations": missing_declarations,
        "optional": block.optional,
    }


def compute_readiness(
    corpus: "paper_graph.Corpus",
    satisfied_facts: set,
    satisfied_declarations: set,
    *,
    opened_blocks: set | None = None,
    basis: str = "supposed-only",
) -> list:
    """Every block of every section, in a stable declared order (see
    `_iter_blocks_in_declared_order`).

    `opened_blocks`, when given, is the set of qualified block ids known to
    be opened in `main.tex` — a pure set the caller resolved, never read
    here. `opened_blocks=None` (the default) means openness is unknown for
    every block, which `compute_block_readiness` treats as `opened=None`
    and therefore never reports `not-applicable`, regardless of `basis`."""
    return [
        compute_block_readiness(
            block, satisfied_facts, satisfied_declarations,
            opened=(None if opened_blocks is None else block.qualified_id in opened_blocks),
            basis=basis,
        )
        for block in _iter_blocks_in_declared_order(corpus)
    ]
