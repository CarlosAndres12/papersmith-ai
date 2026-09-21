# Exploration: the redactor receives the section it must transpose

> **Paths in this document.** Every `paper_*.py` citation is relative to
> `.claude/skills/paper-writing/scripts/`; every `tests/` and `openspec/`
> citation is relative to the repository root. The bare filenames below were
> written that way for brevity and caught as ambiguous by the proposal phase.

Engram counterpart:
`sdd/the-redactor-receives-the-section-it-must-transpose/explore`
(observation #1962). Written here by the orchestrator: the explore executor has
no file-write tool, so the OpenSpec half of hybrid persistence is materialized
at this level rather than by the phase agent.

## The demand and the missing key

A block whose contract declares `mode: transposition` is bound to a source
section of an upstream managed document, and
`openspec/specs/transposition-fidelity/spec.md:5-8` requires it to "carry its
bound source section into the paper's own style — never copy it."

Nothing hands the redactor that section.

| where | what it says |
| --- | --- |
| `.claude/agents/redactor.md:15-24` | names exactly four inputs, then: "You never open a file yourself to find a fifth input — if the contract prose does not license a claim, you have no back door to it." No bound section anywhere. |
| `paper_cli.py:2052-2113` (`assemble_packet`) | returns `{block, section, contract, references}`. `references` are heading OUTLINES per ingested style-reference paper, never span text. The bound section never enters the function. |
| `paper_cli.py:2217` | `write` DOES resolve the section's bytes into `BlockContract.source_sections` — after the draft exists, and only to run the verbatim-overlap check. |

The only time the machine opens that section is to distrust the draft. Never to
supply it.

## The six questions, settled

**1. D5 is scoped to reference material only.** Its own text
(`openspec/changes/archive/2026-09-18-the-phases-are-derived-not-remembered/design.md:65-69`):
"the packet is physically incapable of carrying reference prose… puts an
unaudited copy of reference prose in a file the redactor can read without ever
passing residency verification or the eight-token tripwire." Every clause names
third-party style material. D5 never mentions `source_bindings` or a bound
document, and does not extend to one.

**2. `assemble_packet` does not assemble a corpus today** and takes no
`--paper`/`paper_dir` at all. `resolve_bound_sections` (`paper_source_span.py:27-77`)
requires a full `Corpus`, obtainable only from `assemble_corpus`'s whole-
`sections_dir` glob (`paper_graph.py:291`) — there is no narrower entry point.
Assembling one makes 16 further refusal codes reachable from `packet`
(`ID_COLLISION`, `SOURCE_BINDING_CONFLICT`, `INPUT_PARTITION_ABSENT`,
`SPAN_NOT_IN_SOURCE`, `FACT_ROUTE_AMBIGUOUS`, `FACT_PRODUCER_DUPLICATE`,
`FACT_SELF_REQUIRED`, `FACT_PRODUCER_ABSENT`, `PRODUCER_CHAIN_ABSENT`,
`CHAIN_ROW_UNRESOLVED`, `CHAIN_ROW_UNBACKED`, `BLOCK_SUBUNIT_UNDECLARED`,
`UNIT_HEADING_AMBIGUOUS`, plus `SOURCE_REVISIONS_UNDECLARED`,
`SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`).

Precedent exists: `compute_phases` (`paper_cli.py:1923`) already pays exactly
this cost on a read-only verb. `resolve_bound_sections` does not need
`enforce_bindings=True`, so `SECTION_BINDING_ABSENT` need not become reachable
from `packet`.

**3. The shipped requirements this modifies**, and the real structural blocker:

- `openspec/specs/redactor-packet/spec.md:15-23` —
  `Requirement: The Packet Carries Contract Prose Plus Same-Section Style Extracts`
- `openspec/specs/evidence-bound-drafting/spec.md:19-25` —
  `Requirement: Redactor Input Contract`, whose text is literally "The redactor
  MUST receive exactly four inputs for one block".

That requirement is backed by code, not only prose: `paper_bindings.RedactorInput`
(`paper_bindings.py:39-44`) is a `@dataclass(frozen=True)` with exactly four
fields, documented at `:36-38` as "a shape contract, not a validator with its
own refusal — a caller building a fixture for the redactor simply cannot omit a
field."

**4. The redactor's contract must gain a fifth DECLARED input** while keeping
"you never open a file yourself" intact in spirit: the point is to add a door,
not to remove the prohibition on the back door. No test gates `redactor.md`'s
frontmatter or its stated inputs; `RedactorInputContractTests`
(`tests/test_paper_writing.py:4611-4620`) exercises the dataclass shape but does
not assert a field count.

**5. The verbatim check's arithmetic is unaffected** —
`threshold = max(overlap_against_set(contract_prose, [S_i]), 16)` is computed
from contract prose and section text alone. Its practical load changes sharply:
today verbatim copying is near-structurally impossible because the redactor
never saw the bytes. Once it does, `SOURCE_SECTION_VERBATIM` becomes the primary
real-world safeguard rather than a backstop.

**6. No real binding exists on disk** (`paper/.paper-writing/` holds none;
`transposition-fidelity/spec.md:28-34` says so itself). A fixture must invent a
synthetic source document and a `bind` round, following this repository's own
invented-name convention.

## Recommendation

Widen `assemble_packet` — add `paper_dir`, assemble the corpus with the default
`enforce_bindings=False`, and call the already-shipped `resolve_bound_sections`
— and widen `RedactorInput` with a fifth `source_sections` field, mirroring
`BlockContract.source_sections`'s existing shape.

Rejected: a second separate verb (same machinery cost, worse process shape), and
leaving the redactor blind while only hardening the post-hoc check (does not
address the stated defect at all).

## Risks

- **Corpus-wide refusal contamination on `packet`**: an unrelated section's
  defect can now block one block's packet. This must be an explicitly accepted
  tradeoff, never a silent one.
- `RedactorInput` field-order and positional-argument risk when widening a
  frozen dataclass.
- No real binding exists to validate any of this end to end; everything stays
  synthetic.
- **Faithfulness of the transposition remains unchecked after this change.** The
  prior change's own Open Questions
  (`openspec/changes/archive/2026-09-20-the-tripwire-reaches-the-section-that-feeds-it/design.md:316-319`)
  already deferred it. It must be scoped out explicitly here, never implied
  closed — it is the sibling change
  `the-block-asserts-only-what-its-section-carries`.

## Ready for proposal

Yes.
