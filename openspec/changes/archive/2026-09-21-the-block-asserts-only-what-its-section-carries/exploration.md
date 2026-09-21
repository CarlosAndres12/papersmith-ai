# Exploration: the block asserts only what its section carries

Does `write` verify that a transposition draft asserts only what its bound
section carries?

> **Paths in this document.** Every `paper_*.py` citation is relative to
> `.claude/skills/paper-writing/scripts/`; every `tests/` and `openspec/`
> citation is relative to the repository root. The bare filenames below were
> written that way for brevity and caught as ambiguous by the proposal phase.

Engram counterpart: `sdd/the-block-asserts-only-what-its-section-carries/explore`
(observation #1963). Written here by the orchestrator: the explore executor has
no file-write tool, so the OpenSpec half of hybrid persistence is materialized
at this level rather than by the phase agent.

## Current state, measured

`cmd_write`'s own pipeline runs before `write_block` is reached at all
(`paper_cli.py:2172-2262`):

| order | stage | refuses |
| --- | --- | --- |
| 1 | `_resolve_write_gate` | `PHASE_NOT_READY` |
| 2 | `_guard_section_citations_ready` | the citation-folder codes |
| 3 | `assemble_packet` | `GUIDANCE_MARKDOWN_UNREADABLE` |

Then `write_block` (`paper_write.py:139-259`):

| order | stage | refuses |
| --- | --- | --- |
| 4 | `_stage_readiness` | `MODE_ABSENT`, `EVIDENCE_SET_REQUIRED` |
| 5 | `_stage_evidence_audit` | `UNBOUND_SENTENCE`, `BINDING_ORPHANED`, `EVIDENCE_ID_UNKNOWN`, `FACT_NOT_LICENSED`, `STRUCTURAL_CARRIES_CLAIM`, `MODE_VIOLATION` |
| 6 | `_stage_contract_audit` | `DISQUALIFIERS_ABSENT`, `VERDICT_MISSING`, `VERDICT_BULLET_UNKNOWN`, `AUDIT_EXHAUSTED` |
| 7 | style tripwire | `STYLE_OVERLAP` |
| 8 | source-section verbatim | `SOURCE_SECTION_VERBATIM` |
| 9 | `paper_block.substitute` | the substitution engine's own codes |

**`contract.source_sections` has exactly one real consumer.** Referenced at
`paper_write.py:236`, `:239` and `:249`; the only one that reads the section's
text is `paper_leak.check_source_section_verbatim`
(`paper_leak.py:215-273`), which computes the longest shared normalized-token
run and refuses when it exceeds `max(source_section_floor(...), 16)`.

That is a COPYING check. It is never a support check, and that is not an
oversight — `openspec/specs/transposition-fidelity/spec.md:1-17` states the
capability's purpose as proving content did not leak verbatim.

**The gap is real, not a suspicion.** A legitimate paraphrase deliberately
passes with near-zero overlap (the spec says so at lines 104-109). The further
a draft drifts from what the section actually says, the less it overlaps, and
the quieter the one check that reads the section becomes.

No test exercises "the draft states X but the section never says X". The
closest, `SourceSectionVerbatimTests` (`tests/test_paper_writing.py:5300-5432`),
asserts overlap-length behaviour throughout.

## Affected areas

| file | why |
| --- | --- |
| `paper_write.py:139-279` | pipeline order; `_stage_evidence_audit`'s discarded return value at `:159`; the `source_fidelity_report` envelope |
| `paper_leak.py:215-273` | where the sibling verbatim check lives — a grounding check must NOT extend it |
| `paper_audit.py` + `.claude/agents/contract-auditor.md` | the precedent shape: the agent proposes, the code reconciles against real bytes in both directions |
| `paper_bindings.py:88-137` | `segment_sentences` (reusable) and `resolve_bindings` (id-membership only, never content) |
| `paper_source_span.py:27-77`, `paper_graph.py:114`, `paper_contract.py:418-444` | the `fact_id` join tying a `fact:`-bound sentence to one bound section |
| `paper_cli.py:75-104` | the module-level import registry a new module must join "for the roster derivation" |
| `tests/test_paper_writing.py:7443-7534,7942` | roster derivation, classification, and the measured count literal (161 today) |
| `tests/paper_mutation.py` | the harness a new refusal must be proven reachable through |

## Approaches

**1. New sibling agent plus reconciliation, contract-audit shaped.** A new agent
judges whether each `fact:`-bound sentence is supported by its bound section;
`write` independently re-derives the sentences and the sections and reconciles
in both directions, span-grounded, downgrading any unfounded verdict to
`undecidable`. A new report key sits beside `sourceFidelity`.

- Reuses two already-shipped, already-tested shapes exactly; the `fact_id` join
  is real; refusal spans are per sentence.
- Covers only `fact:`-bound, `document`-bound sentences, which must be scoped
  explicitly — the same way `argument` mode was scoped out of
  `SOURCE_SECTION_VERBATIM`. Costs a new agent file, the full
  roster/classification/mutation-proof surface, and threading
  `_stage_evidence_audit`'s currently discarded bindings through.
- Effort: medium-high.

**2. Extend `contract-auditor` with a grounding section.** No new agent file,
but a real shape mismatch: the disqualifier bullets are a fixed, human-authored
list while the sentences are a dynamic, machine-segmented one. Conflating them
risks breaking `extract_disqualifiers`'s own "never special-cased" contract.

**3. Mechanical overlap widening, no agent.** Rejected in principle. This
repository's own shipped behaviour proves a legitimate paraphrase shares
near-zero overlap with its source, so no overlap signal can separate a faithful
paraphrase from an unsupported assertion.

## Recommendation

Approach 1, scoped explicitly to `fact:`-bound, `document`-bound sentences,
following `paper_audit.py`'s reconciliation shape and the "sibling, never
extension" precedent `SOURCE_SECTION_VERBATIM` itself already set.

## Risks

- No real `document` binding exists on disk today
  (`transposition-fidelity/spec.md:28-34`); every scenario stays synthetic until
  one does.
- Scope creep toward `evidence:`-bound sentences would conflate two separately
  shipped mechanisms.
- A design that lets the agent's verdict stand without byte-level reconciliation
  reproduces the "deciding instead of asking" failure this repository guards
  against by name.
- Omitting the module-level "for the roster derivation" import would leave a new
  refusal silently unreachable to the roster walk. This repository's own test
  docstring records that happening once already.

## Ready for proposal

Yes. Every claim above is grounded in `file:line` evidence; research is
optional.
