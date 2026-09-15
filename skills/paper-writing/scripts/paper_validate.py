"""paper_validate: verdict accounting, regime-dispatched placement, and the
bounded three-round search loop that never lets a half-cited block reach
disk (`no-claim-without-a-source-that-holds-it`, `citation-validation` and
`citation-placement` specs).

Public surface:

    HOLDS, MAX_ROUNDS
    satisfied_claims(records)                 -> set[str]
    finalize_block(paper_dir, block_id, claims, records, new_body=None) -> dict  (raises EVIDENCE_EXHAUSTED)
    Citation, Sentence
    validate_placement(regime, sentence)       -> dict   (raises placement codes)
    read_citations_regime(section_path, block_id) -> str  (raises CONTRACT_HEADER_ABSENT)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_block  # noqa: E402
import paper_contract  # noqa: E402
import paper_vocabulary  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: `citation-validation`, Requirement: Three Verdicts, `insufficient` Is Not
#: Lenient. Only this exact string satisfies a claim -- `does-not-hold` and
#: `insufficient` are identical to the accounting below, one derivation,
#: never a per-verdict branch (`design.md`, Decision 5).
HOLDS = "holds"

#: `citation-validation`, Requirement: Three Search Rounds Per Block, Then
#: Exhaustion.
MAX_ROUNDS = 3


def satisfied_claims(records: list[dict]) -> set[str]:
    """`satisfied = {r.claim for r in records if r.verdict == HOLDS}`
    (`design.md`, Decision 5) -- the whole leniency-proof surface is this
    one derivation; there is no second code path that could special-case
    `does-not-hold` or `insufficient` into passing."""
    return {record["claim"] for record in records if record["verdict"] == HOLDS}


def finalize_block(
    paper_dir: Path, block_id: str, claims: list[str], records: list[dict],
    new_body: bytes | None = None,
) -> dict:
    """The single gate: given every claim a block needs support for and
    every evidence record gathered so far, decide `pending` (rounds
    remain), refuse `EVIDENCE_EXHAUSTED` naming every unsupported claim
    (round budget spent), or -- only when every claim is satisfied --
    write the block via `paper_block.substitute`.

    The write sits strictly inside the all-satisfied branch: `substitute`
    is never even reached while `unsupported` is non-empty, so "the block
    is not written" on exhaustion is control flow, not a policy this
    function merely promises (`citation-validation`, Requirement: Three
    Search Rounds Per Block, Then Exhaustion).
    """
    satisfied = satisfied_claims(records)
    unsupported = sorted(claim for claim in claims if claim not in satisfied)
    max_round = max((record.get("round", 0) for record in records), default=0)

    if unsupported:
        if max_round >= MAX_ROUNDS:
            raise Refused(
                "EVIDENCE_EXHAUSTED",
                f"block {block_id!r}: unsupported after {MAX_ROUNDS} rounds: {unsupported}",
            )
        return {"status": "pending", "block": block_id, "unsupported": unsupported, "round": max_round}

    if new_body is None:
        return {"status": "satisfied", "block": block_id, "unsupported": [], "round": max_round}

    result = paper_block.substitute(paper_dir, block_id, new_body=new_body)
    return {"status": "written", **result}


@dataclass(frozen=True)
class Citation:
    """One citation occurrence inside a `Sentence` (`citation-placement`
    spec). `position` is `"sentence-end"` or `"mid-sentence"`;
    `attached_to_object` is true when the citation sits immediately beside
    the object it credits; `is_noun_phrase` is true when the citation
    itself functions as the sentence's subject (e.g. "the work in [N] does
    X")."""

    text: str
    position: str
    attached_to_object: bool
    is_noun_phrase: bool


@dataclass(frozen=True)
class Sentence:
    text: str
    citations: tuple[Citation, ...]


def _validate_discovery(sentence: Sentence) -> dict:
    if len(sentence.citations) > 1:
        raise Refused(
            "CITATION_MULTI_CLAIM_SENTENCE",
            f"{sentence.text!r}: two citations in one discovery sentence; split into two sentences",
        )
    for citation in sentence.citations:
        if citation.is_noun_phrase:
            raise Refused(
                "CITATION_NOUN_PHRASE",
                f"{sentence.text!r}: {citation.text!r} is a noun-phrase citation, prohibited under discovery",
            )
        if citation.position != "sentence-end":
            raise Refused(
                "CITATION_NOT_AT_SENTENCE_END",
                f"{sentence.text!r}: {citation.text!r} must sit at the end of the sentence it supports",
            )
    return {"regime": "discovery", "sentence": sentence.text, "result": "pass"}


def _validate_resolution(sentence: Sentence) -> dict:
    for citation in sentence.citations:
        if not citation.attached_to_object:
            raise Refused(
                "CITATION_DETACHED_FROM_OBJECT",
                f"{sentence.text!r}: {citation.text!r} is not attached to the object it credits",
            )
    return {"regime": "resolution", "sentence": sentence.text, "result": "pass"}


def _validate_none(sentence: Sentence) -> dict:
    if sentence.citations:
        raise Refused(
            "CITATION_UNDER_NONE_REGIME",
            f"{sentence.text!r}: a citations:none block cites {[c.text for c in sentence.citations]}",
        )
    return {"regime": "none", "sentence": sentence.text, "result": "pass"}


#: `citation-placement`, Requirement: Placement Dispatches On Regime -- a
#: table, never one universal rule (`proposal.md`, "The governing rule").
_PLACEMENT_RULES = {
    "discovery": _validate_discovery,
    "resolution": _validate_resolution,
    "none": _validate_none,
}


def validate_placement(regime: str, sentence: Sentence) -> dict:
    paper_vocabulary.validate_citations(regime)
    return _PLACEMENT_RULES[regime](sentence)


def read_citations_regime(section_path: Path, block_id: str) -> str:
    """Reads one block's `citations` regime from an already-headered
    `sections/*.md` file. Refuses `CONTRACT_HEADER_ABSENT` (work-state) when
    the file carries no front-matter fence at all -- never a defaulted
    regime (`design.md`, `What Breaks`: none of the ten shipped
    `sections/*.md` carry front matter yet, so every real block refuses
    this until `the-contract-is-data-not-code` lands; tests build their own
    headered fixtures). Reuses `BLOCK_ABSENT` (already classified,
    `paper_block.py`) for a block id the header simply does not declare --
    the same "requested id does not exist" condition, not a second code for
    it.
    """
    data = section_path.read_bytes()
    if not (data.startswith(b"---\n") or data.startswith(b"---\r\n")):
        raise Refused(
            "CONTRACT_HEADER_ABSENT",
            f"{section_path} carries no front-matter header; the citations regime cannot be read",
        )
    header, _body = paper_contract.parse(data)
    for block in header.blocks:
        if block["id"] == block_id:
            return block["citations"]
    raise Refused("BLOCK_ABSENT", f"{block_id!r} is not declared in {section_path}'s header")
