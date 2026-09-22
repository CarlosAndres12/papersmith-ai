# Exploration: the-methods-section-produces-the-contributions

Artifact store: hybrid. Engram twin: `sdd/the-methods-section-produces-the-contributions/explore`.
Written by the orchestrator because `sdd-explore` carries no Write tool; content is the
exploration phase's own returned report, not a summary of it.

## The operator's statement of the change

> "se materializa la matemática y ya con eso salen las contribuciones para el bloque
>  de la introducción que recibe y con eso redacta"

The mathematics is materialized in Materials and Methods first; the contribution list
falls out of that; the introduction's contribution block RECEIVES that list and drafts
from it. Today the graph says the opposite.

## Current state, measured

`contributions` is a PRODUCED fact (`paper_declarations.DERIVED_FACTS`) with exactly one
producer: `introduction.block-4b`, which requires `formulation` AND `results`.
`materials-and-methods.mm-proposal` requires only `formulation` and produces nothing.

Zero `after` edges exist from any `materials-and-methods.*` block to any `introduction.*`
block. `derive_order` yields introduction 1-6, related-work 7-11, `introduction.block-3`
at 12, materials-and-methods 13-16, then the rest.

**Seven** blocks across **seven different section files** directly require `contributions`
(verified by grep, not assumed): `introduction.block-2`, `related-work.rw-synthesis-artefact`,
`experimental-setup.es-assessment`, `results-and-discussion.rd-contribution-blocks`,
`abstract.slot-2`, `conclusions.concl-block-1`, `title-and-keywords.title`. Each of those
seven files' `### Internal chain` table carries a row naming `introduction.block-4b`,
backed by a real `after` edge, as `_verify_producer_chain_rows` / `PRODUCER_CHAIN_ABSENT`
require.

`materials-and-methods.mm-proposal`'s header declares `figure.components_from:
"contributions"`, so M&M's diagram is today cross-checked against `introduction.block-4b`'s
own written `\item` lines via `_resolve_expected_components`.

### Two pre-existing gaps found while measuring, both orthogonal to this change

1. `paper_verify.check_contribution_list` reads only the REQUIRES side (`blocks_by_fact`),
   never the producer — `introduction.block-4b` itself is never compared against
   `couplings.json`'s declared list by that check.
2. `_verify_producer_duplication`'s corroboration exception (two producers allowed when
   `fact_id in paper_verify.CHECKS`) works for `gap` only by string coincidence: the fact
   id `"gap"` happens to equal a `CHECKS` member. The corresponding entry for this fact is
   named `"contribution-list"`, not `"contributions"`, so the membership test is `False`.
   Any dual-producer design needs a code fix first.

## The contradiction the contracts already carry

`sections/06-introduction.md:458-466`:

> "**The number of items is the number of contributions the proposal has.** It is
>  inherited, never a drafting target. ... the list agree in count, order, and naming
>  with the components of the methods section."
>
> "Those names are the contract with the methods section, which uses the same ones in
>  the same order."

The prose says 4b INHERITS and must AGREE WITH methods; the header says 4b PRODUCES; the
methods diagram derives from what 4b produces. That is circular. Enforcement today is only
downstream: the contract-auditor's Disqualifier, and `verify`'s `contribution-list`
coupling — both after both blocks are written.

## Candidates

### 1. Move the sole producer to `materials-and-methods.mm-proposal` (RECOMMENDED)

`mm-proposal` produces `contributions`; `introduction.block-4b` newly requires it.

Matches the operator's literal statement and resolves the prose/header contradiction in
the prose's favour.

Costs: a full (legal, non-cyclic) writing-order inversion putting M&M ahead of nearly
everything; seven section files need new chain rows and `after` edges, each with a
literal, contract-verifiable quote; `mm-proposal`'s own Components Check becomes
self-referential unless explicitly redesigned. Effort: High.

### 2. Make `contributions` declared/inherited; both blocks require it

Rejected. There is no third "declared-derived" bucket: `_DECLARABLE_ROUTE_FACTS` is exactly
`OBSERVABLE_FACTS ∪ STRUCTURAL_FACTS`. Folding `contributions` into `OBSERVABLE_FACTS`
contradicts that class's own docstring (an outside observer measures external evidence,
never a derivation) and breaks the partition-consistency assert.

### 3. Corroborated dual producer, mirroring `gap`

Rejected, measured strictly worse than 1: reachability and chain-row checks require every
producer to reach every consumer, doubling the seven-file blast radius, plus the
`"contributions"` vs `"contribution-list"` code fix and a `check_contribution_list` rewrite
to read the producer side at all.

## Recommendation

Candidate 1, with two decisions the proposal must record explicitly:

- **D1 — order inversion.** Accept M&M being written before the introduction.
  *Confirmed by the operator's own statement above; this is the change being asked for.*
- **D2 — the self-referential Components Check.** `mm-proposal`'s diagram currently derives
  its expected components from a fact `introduction.block-4b` produces. If `mm-proposal`
  becomes the producer, that cross-section corroboration becomes a tautological self-check.
  Either accept the tautology (and say so, so it is not mistaken for a live guard) or
  redesign it to check against `block-4b`'s restated text. **Open; belongs to design.**

## Risks

- Every `sections/*.md` edit is contract-validated (`CHAIN_ROW_UNBACKED`,
  `PRODUCER_CHAIN_ABSENT`) — not a free-form doc edit.
- `SKILL.md`'s measured "eight waves 22/7/11/2/2/1/1/1" claim goes stale under Candidate 1
  unless re-measured in the same change.
- D2 left silent would create a guard that cannot fail — pattern 2 of
  `MANTENIMIENTO-siete-formas-de-fallar-en-verde.md`.
- `introduction.block-4b` already hard-requires `results` in its header despite prose
  describing a "partial form" writable before results. Pre-existing and orthogonal, but it
  interacts with this change.
- `tests/test_paper_writing.py` has 89 matching lines; none pin the shipped corpus's exact
  order by name.
