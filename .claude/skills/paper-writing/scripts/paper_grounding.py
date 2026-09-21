"""paper_grounding: per-sentence support reconciliation for a transposition
block against its own bound source section's bytes (`transposition-
grounding` spec; `design.md`, "The block asserts only what its section
carries").

A fourth sibling in `write_block`'s judge chain, shaped on `paper_audit.py`'s
own account-versus-real-bytes reconciliation (`:56-101`), never extending it
(design.md D5). An agent proposes a per-sentence support verdict; this module
re-derives both the subject sentences (from the draft's own segmented
bindings) and the section bytes (from the block's own resolved bound
sections) and reconciles the account against those re-derived values, never
trusting either from the account's own copy. `supported` is the verdict that
lets a sentence reach substitution, so `supported` is the one this module
requires to be grounded (D1) -- the inversion of `contract-audit`'s own
asymmetry, where the *blocking* verdict is the one required to cite a span.

Public surface:

    subjects_for(bindings, source_sections) -> list[Binding]
    reconcile_support(subjects, account, source_sections, *, block_id) -> list[dict]
        (raises GROUNDING_ACCOUNT_ABSENT, GROUNDING_SENTENCE_UNKNOWN,
         GROUNDING_VERDICT_MISSING, SECTION_UNSUPPORTED_CLAIM)
    source_grounding_report(subjects, reconciled) -> dict
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402


def subjects_for(bindings: list, source_sections: tuple) -> list:
    """The subject set: the intersection of two independently produced sets
    -- the draft's own segmented bindings and the block's resolved bound
    sections -- computed fresh on every call (`transposition-grounding`
    spec, `Requirement: The Subject Set Is An Intersection Derived From
    Bytes, Never A List`; design.md D3). No block id, section title,
    document filename, or lineage literal decides membership -- only
    `Binding.kind == "fact"` and `Binding.ref` matching a `source_sections`
    entry's own `"fact"` key."""
    bound_facts = {section["fact"] for section in source_sections}
    return [binding for binding in bindings if binding.kind == "fact" and binding.ref in bound_facts]
