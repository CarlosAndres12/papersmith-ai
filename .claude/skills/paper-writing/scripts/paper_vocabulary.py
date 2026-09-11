"""paper_vocabulary: the three closed vocabularies a section contract's
header may draw from, and nothing else.

No I/O, no state — pure tuples plus a validator per tuple. A consumer that
only needs the vocabulary (a later phase, or a roster derivation) imports
this module alone and drags in no reader, no disk access
(design.md, `Internal layering`).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: `requires_facts` entries a block may declare — `specs/section-contract`,
#: `Requirement: Closed Fact Vocabulary`. Ten ids, exactly as spelled there.
FACTS: tuple[str, ...] = (
    "formulation",
    "contributions",
    "problem-statement",
    "gap",
    "dataset",
    "experimental-design",
    "implementation",
    "results",
    "limitations",
    "skeleton",
)

#: `requires_declarations` entries a block may declare — operator-supplied
#: inputs derived from no fact. `specs/section-contract`,
#: `Requirement: Closed Declaration Vocabulary`.
DECLARATIONS: tuple[str, ...] = (
    "author-roles",
    "grant-title",
    "grant-code",
    "repository-url",
    "keyword-bounds",
    "classification-line",
)

#: A block's `citations` value — exactly one of these three.
#: `specs/section-contract`, `Requirement: Closed Citations Regime`.
CITATIONS_REGIMES: tuple[str, ...] = ("discovery", "resolution", "none")


def validate_fact(fact_id: str) -> None:
    """Refuses `UNKNOWN_FACT` (work-state) when `fact_id` is not one of the
    ten declared facts."""
    if fact_id not in FACTS:
        raise Refused("UNKNOWN_FACT", f"{fact_id!r} is not one of the declared facts {FACTS}")


def validate_declaration(declaration_id: str) -> None:
    """Refuses `UNKNOWN_DECLARATION` (work-state) when `declaration_id` is
    not one of the six declared declarations."""
    if declaration_id not in DECLARATIONS:
        raise Refused(
            "UNKNOWN_DECLARATION",
            f"{declaration_id!r} is not one of the declared declarations {DECLARATIONS}",
        )


def validate_citations(value: str) -> None:
    """Refuses `UNKNOWN_CITATIONS_REGIME` (work-state) when `value` is not
    one of `discovery`, `resolution`, `none`."""
    if value not in CITATIONS_REGIMES:
        raise Refused(
            "UNKNOWN_CITATIONS_REGIME",
            f"{value!r} is not one of the declared citations regimes {CITATIONS_REGIMES}",
        )
