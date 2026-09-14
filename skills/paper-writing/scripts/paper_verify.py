"""paper_verify: seven pure checks over a `paper_coupling_evidence.Evidence`,
and the report they assemble into (`the-couplings-hold-or-they-do-not`).

Every function below is a pure function of an already-built `Evidence`
object — no `Path`, no `open`, no disk read anywhere in this module
(`tests/test_paper_writing.py`, `ReadOnlyTests`'s AST lock holds this file
to exactly that). `skill-audit`'s shape throughout: derive both sides where
a side can be derived, publish the provenance of every side that cannot,
report, never repair.

`CHECKS` is one closed roster (contribution-list, chain, gap, artefacts,
future-work, citations, contract-currency); `run()` is held to producing
exactly one report object per member, in both directions
(`ReportShapeTests`). `UNMEASURED_REASONS` is a second closed roster; every
member is proven reachable by a fixture elsewhere in the suite.

Verdict vocabulary is `pass` | `fail` | `unmeasured` — deliberately NOT
`paper_vocabulary.VERDICTS` (`holds`/`does-not-hold`/`insufficient`), which
belongs to a different domain entirely (WU1's claim<->source citation
verdicts). Reusing that vocabulary here would conflate two unrelated
judgments that happen to both be three-valued; `specs/coupling-
verification/spec.md`'s own `Requirement: Verdict Vocabulary And
Classification Field` names `pass|fail|unmeasured` explicitly, and this
module follows the spec's normative wording over design.md's one
illustrative JSON snippet (which used `holds|fails` loosely) — noted as a
documentation inconsistency in this change's own apply report, not silently
carried forward into a second live vocabulary.

Public surface:

    CHECKS               -> the seven check ids, in report order
    UNMEASURED_REASONS   -> every reason a check can report `unmeasured` for
    run(evidence) -> dict  {"checks": [...], "clean": bool,
                             "holds": int, "fails": int, "unmeasured": int}
"""
from __future__ import annotations

import re

CHECKS: tuple[str, ...] = (
    "contribution-list",
    "chain",
    "gap",
    "artefacts",
    "future-work",
    "citations",
    "contract-currency",
)

#: Every reason a check's `unmeasured_reason` may carry. Closed: a check
#: returning a reason outside this tuple is a programming error in this
#: module, caught by `_entry`'s own assertion rather than shipped silently.
UNMEASURED_REASONS: tuple[str, ...] = (
    "SECTION_CONTRACTS_UNREADABLE",
    "NO_BLOCK_REQUIRES_FACT",
    "BLOCK_NOT_DECLARED",
    "ASSISTED_READING_REQUIRED",
    "CONTRACT_RECORD_ABSENT",
)

_VERDICTS = ("pass", "fail", "unmeasured")

_CITE_RE = re.compile(rb"\\cite\{([^}]*)\}")
_BIB_ENTRY_RE = re.compile(rb"@[A-Za-z]+\{\s*([^,\s]+)\s*,")
_ITEM_RE = re.compile(r"^\\item (.*)$", re.MULTILINE)
_CLOSING_RE = re.compile(r"^Closing: (.*)$", re.MULTILINE)
_CHAIN_ROLES: tuple[str, ...] = ("Problem", "Contribution", "Property", "Instrument", "Evidence")
_CHAIN_ROLE_RE = {
    role: re.compile(rf"^{role}: (.*)$".encode("ascii"), re.MULTILINE) for role in _CHAIN_ROLES
}


def _entry(check: str, *, classification: str, verdict: str, sides: list,
           evidence: dict, limits: list, unmeasured_reason: str | None) -> dict:
    if verdict not in _VERDICTS:
        raise AssertionError(f"{verdict!r} is not one of {_VERDICTS}")
    if verdict == "unmeasured":
        if unmeasured_reason not in UNMEASURED_REASONS:
            raise AssertionError(f"{unmeasured_reason!r} is not a declared unmeasured reason")
    elif unmeasured_reason is not None:
        raise AssertionError("unmeasured_reason set on a non-unmeasured verdict")

    limits = list(limits)
    if sides and all(side["source"] == "declared" for side in sides):
        if "TWO_DECLARED_SIDES" not in limits:
            limits.append("TWO_DECLARED_SIDES")

    return {
        "check": check,
        "classification": classification,
        "verdict": verdict,
        "sides": sides,
        "evidence": evidence,
        "limits": limits,
        "unmeasured_reason": unmeasured_reason,
    }


def _unmeasured(check: str, classification: str, reason: str, *, evidence: dict | None = None) -> dict:
    return _entry(
        check, classification=classification, verdict="unmeasured",
        sides=[], evidence=evidence or {}, limits=[], unmeasured_reason=reason,
    )


def _cite_keys(body: bytes) -> set:
    keys = set()
    for match in _CITE_RE.finditer(body):
        for raw in match.group(1).split(b","):
            key = raw.strip()
            if key:
                keys.add(key.decode("utf-8", errors="replace"))
    return keys


def _bib_keys(body: bytes) -> set:
    return {match.group(1).decode("utf-8", errors="replace") for match in _BIB_ENTRY_RE.finditer(body)}


def _first_occurrence_order(body: bytes, names: list) -> list:
    text = body.decode("utf-8", errors="replace")
    positions = []
    for name in names:
        idx = text.find(name)
        if idx != -1:
            positions.append((idx, name))
    positions.sort(key=lambda pair: pair[0])
    return [name for _, name in positions]


def _parse_chain_roles(body: bytes) -> dict:
    roles = {}
    for role, pattern in _CHAIN_ROLE_RE.items():
        match = pattern.search(body)
        roles[role.lower()] = match.group(1).decode("utf-8", errors="replace") if match else ""
    return roles


def _gap_shape(body: bytes) -> dict:
    text = body.decode("utf-8", errors="replace")
    items = [match.group(1).strip() for match in _ITEM_RE.finditer(text)]
    closing_match = _CLOSING_RE.search(text)
    closing = closing_match.group(1).strip() if closing_match else None
    offset = closing_match.start(1) if closing_match else None
    return {"front": items, "closing": closing, "closing_offset": offset}


def check_contribution_list(evidence) -> dict:
    """Coupling 1 (`coupling-verification` spec, `Requirement: Coupling 1
    — Contribution List Identity`). Declared: `record["facts"]
    ["contributions"]`, ordered. Derived, per block requiring the
    `contributions` fact: the order each declared name FIRST occurs in that
    block's own bytes. A name absent from a block's bytes fails the
    declared-name literal-presence limit distinctly from an order mismatch
    (`Requirement: Declared-Name Literal Presence Limit`) — both are
    reported, either alone flips the verdict to `fail`.
    """
    block_ids, reason = evidence.blocks_by_fact.get("contributions", ((), "SECTION_CONTRACTS_UNREADABLE"))
    if reason is not None:
        return _unmeasured("contribution-list", "mechanical", reason)

    declared_blocks = evidence.record.get("blocks", {})
    undeclared = [bid for bid in block_ids if bid not in declared_blocks]
    declared = evidence.record.get("facts", {}).get("contributions") or []
    if undeclared or not declared:
        return _unmeasured("contribution-list", "mechanical", "BLOCK_NOT_DECLARED",
                            evidence={"undeclared_blocks": undeclared})

    sides = [{"name": "facts.contributions", "source": "declared", "origin": "couplings.json"}]
    per_block_order = {}
    mismatched = []
    absent_from_bytes = []
    for block_id in block_ids:
        body = evidence.block_bodies.get(block_id, b"")
        order = _first_occurrence_order(body, list(declared))
        per_block_order[block_id] = order
        sides.append({
            "name": f"{block_id}:first-occurrence-order", "source": "derived",
            "origin": "main.tex block bytes",
        })
        for name in declared:
            if name not in order:
                absent_from_bytes.append({"block": block_id, "name": name})
        if order != list(declared):
            mismatched.append(block_id)

    verdict = "fail" if (mismatched or absent_from_bytes) else "pass"
    return _entry(
        "contribution-list", classification="mechanical", verdict=verdict, sides=sides,
        evidence={
            "declared": list(declared), "per_block_order": per_block_order,
            "mismatched_blocks": mismatched, "absent_from_bytes": absent_from_bytes,
        },
        limits=["ORDER_FROM_FIRST_OCCURRENCE"], unmeasured_reason=None,
    )


def check_chain(evidence) -> dict:
    """Coupling 2 (`Requirement: Coupling 2 — Chain Word Identity`).
    Declared: one word per link (`record["chain"]["links"][i]["word"]`).
    Derived, per block requiring the `problem-statement` fact: the literal
    text found at each of the chain's five role-labeled lines
    (`Problem:`/`Contribution:`/`Property:`/`Instrument:`/`Evidence:`).
    Fails when the declared word is not literally present at every role
    (identity, never synonymy — M2), or when it is not itself a member of
    the declared contribution set (set closure against coupling 1's own
    declared list).
    """
    block_ids, reason = evidence.blocks_by_fact.get("problem-statement", ((), "SECTION_CONTRACTS_UNREADABLE"))
    if reason is not None:
        return _unmeasured("chain", "mechanical", reason)

    declared_blocks = evidence.record.get("blocks", {})
    undeclared = [bid for bid in block_ids if bid not in declared_blocks]
    links = evidence.record.get("chain", {}).get("links") or []
    if undeclared or not links:
        return _unmeasured("chain", "mechanical", "BLOCK_NOT_DECLARED",
                            evidence={"undeclared_blocks": undeclared})

    declared_contributions = set(evidence.record.get("facts", {}).get("contributions") or [])
    sides = [{"name": "chain.links", "source": "declared", "origin": "couplings.json"}]
    per_link = []
    failed = False
    for block_id, link in zip(block_ids, links):
        body = evidence.block_bodies.get(block_id, b"")
        roles = _parse_chain_roles(body)
        sides.append({"name": f"{block_id}:roles", "source": "derived", "origin": "main.tex block bytes"})
        word = link.get("word", "")
        role_present = {role: (word in text) for role, text in roles.items()}
        closure_ok = word in declared_contributions
        link_ok = all(role_present.values()) and closure_ok
        if not link_ok:
            failed = True
        per_link.append({
            "block": block_id, "word": word, "roles_present": role_present, "closure": closure_ok,
        })

    verdict = "fail" if failed else "pass"
    return _entry(
        "chain", classification="mechanical", verdict=verdict, sides=sides,
        evidence={"links": per_link}, limits=["LITERAL_IDENTITY_ONLY"], unmeasured_reason=None,
    )


def check_gap(evidence) -> dict:
    """Coupling 3 (`Requirement: Coupling 3 — The Gap Is Assisted`). Both
    sides are derived, sliced from the two `gap`-fact blocks' own bytes;
    nothing is declared. Mechanical sub-checks (both closings present,
    fronts equal, front counts equal) are published as named booleans; the
    "same thing at different depths" reading is never computed. The check's
    own top-level verdict is unconditionally `unmeasured`,
    `ASSISTED_READING_REQUIRED` — `holds`/`pass` is structurally absent from
    this check's own vocabulary (design.md, `the assisted payload publishes
    evidence, and its only verdict is unmeasured`): no mechanical
    sub-result, however clean, ever promotes it.
    """
    block_ids, reason = evidence.blocks_by_fact.get("gap", ((), "SECTION_CONTRACTS_UNREADABLE"))
    if reason is not None:
        return _unmeasured("gap", "assisted", reason)
    if len(block_ids) != 2:
        return _unmeasured(
            "gap", "assisted", "BLOCK_NOT_DECLARED", evidence={"block_ids": list(block_ids)},
        )

    first_id, second_id = block_ids
    first_shape = _gap_shape(evidence.block_bodies.get(first_id, b""))
    second_shape = _gap_shape(evidence.block_bodies.get(second_id, b""))

    both_closings_present = first_shape["closing"] is not None and second_shape["closing"] is not None
    fronts_equal = first_shape["front"] == second_shape["front"]
    front_counts_equal = len(first_shape["front"]) == len(second_shape["front"])

    sides = [
        {"name": f"{first_id}:closing", "source": "derived", "origin": "main.tex block bytes"},
        {"name": f"{second_id}:closing", "source": "derived", "origin": "main.tex block bytes"},
        {"name": f"{first_id}:front", "source": "derived", "origin": "main.tex block bytes"},
        {"name": f"{second_id}:front", "source": "derived", "origin": "main.tex block bytes"},
    ]
    return _entry(
        "gap", classification="assisted", verdict="unmeasured", sides=sides,
        evidence={
            "closings": {first_id: first_shape["closing"], second_id: second_shape["closing"]},
            "closing_offsets": {
                first_id: first_shape["closing_offset"], second_id: second_shape["closing_offset"],
            },
            "fronts": {first_id: first_shape["front"], second_id: second_shape["front"]},
            "mechanical": {
                "both_closings_present": both_closings_present,
                "fronts_equal": fronts_equal,
                "front_counts_equal": front_counts_equal,
            },
            "depth_reading": "unmeasured",
        },
        limits=[], unmeasured_reason="ASSISTED_READING_REQUIRED",
    )


def check_artefacts(evidence) -> dict:
    """Coupling 4 (`Requirement: Coupling 4 — Diagram Cell Disjointness`).
    Declared: `record["artefacts"]["setup_cells"]` / `["results_
    artefacts"]`. The methods-diagram side is never separately declared —
    it IS coupling 1's own declared contribution set, reused
    (design.md: "the list check 1 already bound to the document, never
    declared twice"). Fails on a results cell absent from the declared
    setup cells (M4a), or a non-empty intersection between the setup cells
    and the contribution set (M4b).
    """
    contribution_check = check_contribution_list(evidence)
    if contribution_check["verdict"] == "unmeasured":
        return _unmeasured("artefacts", "mechanical", contribution_check["unmeasured_reason"])

    artefacts = evidence.record.get("artefacts")
    if not artefacts:
        return _unmeasured("artefacts", "mechanical", "BLOCK_NOT_DECLARED")

    setup_cells = list(artefacts.get("setup_cells") or [])
    results_artefacts = list(artefacts.get("results_artefacts") or [])
    methods_cells = set(evidence.record.get("facts", {}).get("contributions") or [])

    undeclared_results = sorted(set(results_artefacts) - set(setup_cells))
    shared_with_methods = sorted(set(setup_cells) & methods_cells)

    verdict = "fail" if (undeclared_results or shared_with_methods) else "pass"
    return _entry(
        "artefacts", classification="mechanical", verdict=verdict,
        sides=[
            {"name": "artefacts.setup_cells", "source": "declared", "origin": "couplings.json"},
            {"name": "artefacts.results_artefacts", "source": "declared", "origin": "couplings.json"},
            {
                "name": "methods-diagram (== contribution-list)", "source": "derived",
                "origin": "check contribution-list",
            },
        ],
        evidence={
            "setup_cells": setup_cells, "results_artefacts": results_artefacts,
            "undeclared_results": undeclared_results, "shared_with_methods": shared_with_methods,
        },
        limits=[], unmeasured_reason=None,
    )


def check_future_work(evidence) -> dict:
    """Coupling 5 (`Requirement: Coupling 5 — Future Work ⊆ Limitations`).
    Declared, both sides: `record["facts"]["limitations"]` and
    `record["future_work"]["directions"]`. Totality fails on a direction
    answering no declared limitation (M5). The shared citation key is
    checked against the union of `\\cite` keys across every block requiring
    the `limitations` fact, and against `refs.bib` — both derived.
    "Relevant subset" and "specific enough to be a paper" are published as
    `out-of-reach`, never attempted (`Requirement: Classification`).
    """
    block_ids, reason = evidence.blocks_by_fact.get("limitations", ((), "SECTION_CONTRACTS_UNREADABLE"))
    if reason is not None:
        return _unmeasured("future-work", "mechanical", reason)

    declared_blocks = evidence.record.get("blocks", {})
    undeclared = [bid for bid in block_ids if bid not in declared_blocks]
    future_work = evidence.record.get("future_work") or {}
    directions = future_work.get("directions") or []
    declared_limitations = evidence.record.get("facts", {}).get("limitations") or []
    if undeclared or not directions or not declared_limitations:
        return _unmeasured("future-work", "mechanical", "BLOCK_NOT_DECLARED",
                            evidence={"undeclared_blocks": undeclared})

    unanswered = [d["id"] for d in directions if d.get("limitation") not in declared_limitations]

    block_cite_keys: set = set()
    for block_id in block_ids:
        block_cite_keys |= _cite_keys(evidence.block_bodies.get(block_id, b""))
    bib_keys = _bib_keys(evidence.refs_bib_bytes)
    missing_cite = [
        d["id"] for d in directions
        if d.get("cite_key") not in block_cite_keys or d.get("cite_key") not in bib_keys
    ]

    verdict = "fail" if (unanswered or missing_cite) else "pass"
    return _entry(
        "future-work", classification="mechanical", verdict=verdict,
        sides=[
            {"name": "facts.limitations", "source": "declared", "origin": "couplings.json"},
            {"name": "future_work.directions", "source": "declared", "origin": "couplings.json"},
            {"name": "cite-keys", "source": "derived", "origin": "main.tex/refs.bib"},
        ],
        evidence={
            "declared_limitations": list(declared_limitations), "directions": list(directions),
            "unanswered": unanswered, "missing_cite": missing_cite,
            "relevance": "out-of-reach", "specificity": "out-of-reach",
        },
        limits=[], unmeasured_reason=None,
    )


def check_citations(evidence) -> dict:
    """Check A (`citation-integrity` spec). Both sides derived from the
    document itself — no declaration anywhere. A dangling `\\cite` fails
    (M3a); an orphan `refs.bib` entry is reported, never failed (M3b) —
    exercised as two independent mutations, neither reading as proof of the
    other.
    """
    cite_keys = sorted(_cite_keys(evidence.main_tex_bytes))
    bib_keys = sorted(_bib_keys(evidence.refs_bib_bytes))
    dangling = sorted(set(cite_keys) - set(bib_keys))
    orphans = sorted(set(bib_keys) - set(cite_keys))
    verdict = "fail" if dangling else "pass"
    return _entry(
        "citations", classification="mechanical", verdict=verdict,
        sides=[
            {"name": "cite-keys", "source": "derived", "origin": "main.tex \\cite{...}"},
            {"name": "bib-entries", "source": "derived", "origin": "refs.bib @type{key,"},
        ],
        evidence={
            "cite_keys": cite_keys, "bib_keys": bib_keys, "dangling": dangling, "orphans": orphans,
        },
        limits=[], unmeasured_reason=None,
    )


def check_contract_currency(evidence) -> dict:
    """Check B (`contract-currency` spec). `classification` is the literal
    two-word value the spec's own scenario states — `"out-of-reach today"`,
    distinct from the plain `"out-of-reach"` `coupling-verification`'s own
    enum otherwise uses for coupling 5's sub-parts (each spec's own literal
    wording, followed exactly).

    An absent OR empty `provenance` region reports `unmeasured`,
    `CONTRACT_RECORD_ABSENT` (M7) — never zero stale blocks, which would be
    indistinguishable from a genuinely current paper. When present, per-
    block staleness is `evidence.contract_drift`, already computed by
    `paper_coupling_evidence.gather` via `paper_provenance.drift` — this
    function never re-derives it, and never opens the contract file itself.
    """
    if evidence.provenance is None or not evidence.provenance["body"]["records"]:
        return _unmeasured("contract-currency", "out-of-reach today", "CONTRACT_RECORD_ABSENT")

    per_block = dict(evidence.contract_drift)
    stale = sorted(block_id for block_id, drifted in per_block.items() if drifted)
    verdict = "fail" if stale else "pass"
    return _entry(
        "contract-currency", classification="out-of-reach today", verdict=verdict,
        sides=[
            {
                "name": "provenance.records[*].contract_sha256", "source": "declared",
                "origin": "provenance region",
            },
            {
                "name": "contract file sha256", "source": "derived",
                "origin": "section contract file bytes",
            },
        ],
        evidence={"per_block_stale": per_block, "stale_blocks": stale},
        limits=[], unmeasured_reason=None,
    )


_CHECK_FUNCTIONS = {
    "contribution-list": check_contribution_list,
    "chain": check_chain,
    "gap": check_gap,
    "artefacts": check_artefacts,
    "future-work": check_future_work,
    "citations": check_citations,
    "contract-currency": check_contract_currency,
}
assert set(_CHECK_FUNCTIONS) == set(CHECKS), "every CHECKS member needs exactly one function, and the reverse"


def run(evidence) -> dict:
    """Assemble the full report: one object per `CHECKS` member, in both
    directions (`ReportShapeTests`). `holds + fails + unmeasured ==
    len(CHECKS)` always; `unmeasured` is never counted in `holds` — held by
    the arithmetic below, not by prose.
    """
    entries = [_CHECK_FUNCTIONS[check](evidence) for check in CHECKS]
    holds = sum(1 for entry in entries if entry["verdict"] == "pass")
    fails = sum(1 for entry in entries if entry["verdict"] == "fail")
    unmeasured = sum(1 for entry in entries if entry["verdict"] == "unmeasured")
    assert holds + fails + unmeasured == len(CHECKS)
    return {
        "checks": entries, "clean": (fails == 0 and unmeasured == 0),
        "holds": holds, "fails": fails, "unmeasured": unmeasured,
    }
