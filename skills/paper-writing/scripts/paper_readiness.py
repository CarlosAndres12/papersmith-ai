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


def compute_block_readiness(block, satisfied_facts: set, satisfied_declarations: set) -> dict:
    """Given one `BlockRecord`, report `writable` or `blocked` naming each
    still-missing fact and declaration separately. A block whose facts are
    all satisfied but whose declarations are not reports `blocked`, never
    `writable` (`writing-readiness` spec, `Requirement: Per-Block
    Readiness`)."""
    missing_facts = [fact for fact in block.requires_facts if fact not in satisfied_facts]
    missing_declarations = [
        declaration for declaration in block.requires_declarations
        if declaration not in satisfied_declarations
    ]
    status = "writable" if not missing_facts and not missing_declarations else "blocked"
    return {
        "block": block.qualified_id,
        "status": status,
        "missing_facts": missing_facts,
        "missing_declarations": missing_declarations,
    }


def compute_readiness(corpus: "paper_graph.Corpus", satisfied_facts: set, satisfied_declarations: set) -> list:
    """Every block of every section, in a stable declared order (see
    `_iter_blocks_in_declared_order`)."""
    return [
        compute_block_readiness(block, satisfied_facts, satisfied_declarations)
        for block in _iter_blocks_in_declared_order(corpus)
    ]
