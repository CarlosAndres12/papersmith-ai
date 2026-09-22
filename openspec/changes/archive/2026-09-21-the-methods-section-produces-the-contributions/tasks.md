# Tasks: The Methods Section Produces the Contributions

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~180-260 (8 section headers/prose + SKILL.md + spec + 3-4 tests) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | auto-chain |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Producer move + 6 retargets, 8 section files | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_contract` | `paper_cli.py order`/`phases` over `sections/` | Revert the 8 `sections/*.md` edits |
| 2 | Re-measure `phases`, update `SKILL.md`, add tests | PR 1 (same) | full suite below | `paper_cli.py phases` raw output | Revert `SKILL.md` + test hunks |

Single PR — not independently shippable; tests assert unit 1's header state.

## Phase 1: Producer Move (`01`, `06`)

- [x] 1.1 `sections/01-materials-and-methods.md`: `mm-proposal` header (58-93) gains `produces_facts: contributions`, quote `"This section defines the contributions."`
- [x] 1.2 `sections/01-materials-and-methods.md` (~356): Slot 3 step 3 gains mandate — ordered `\item` roster of contribution names, diagram order, right before the closing pointer. Structural mandate only, no real contribution named.
- [x] 1.3 `sections/01-materials-and-methods.md` (104-105, 182, 186-188, 217-218): invert naming-authority prose — Methods is source, not mirror.
- [x] 1.4 `sections/01-materials-and-methods.md`: state the Components Check compares its diagram to its own roster — intra-block drift, not cross-section corroboration.
- [x] 1.5 `sections/06-introduction.md` `block-4b` (129-157): drop `produces_facts`, add `requires_facts: contributions`, quote `"It is inherited, never a drafting target."` (459).
- [x] 1.6 `sections/06-introduction.md` `block-4b`: add `after: mm-proposal`, same quote.
- [x] 1.7 `sections/06-introduction.md`: add 8th chain row — `block-4b` depends on `mm-proposal`.
- [x] 1.8 `sections/06-introduction.md` (466-467): invert — `block-4b` receives the list, never drafts it.

## Phase 2: Retarget 6 Consumer Chains (`after` + row, `introduction.block-4b` → `materials-and-methods.mm-proposal`, quote unchanged)

| # | File | `after` line | Row line | Extra |
|---|------|-------------|----------|-------|
| 2.1 | `sections/06-introduction.md` (`block-2`) | 51 | 250 | — |
| 2.2 | `sections/02-experimental-setup.md` | 70 | 282 | — |
| 2.3 | `sections/03-results-and-discussion.md` | 56 | 268 | — |
| 2.4 | `sections/05-related-work.md` | 126 | 343 | state `components_from` referent moved intro→methods |
| 2.5 | `sections/07-conclusions.md` | 28 | 190 | — |
| 2.6 | `sections/08-abstract.md` | 58 | 219 | — |
| 2.7 | `sections/09-title-and-keywords.md` | none | 154 | row only — `_position_derived_edges` already orders M&M first |

- [x] 2.8 Apply rows 2.1-2.7 as checklist items.
- [x] 2.9 Grep `sections/` for leftover `introduction.block-4b` tied to `contributions`; only `block-4b`'s own requirer entry should remain.

## Phase 3: Re-measure and Update Doc Claims

- [x] 3.1 Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py phases` against the post-move corpus; quote the raw wave-shape output, dated 2026-09-21. Measured: **nine** waves shaped **21/3/6/10/2/2/1/1/1** (47 blocks total).
- [x] 3.2 Run `... order` against the post-move corpus; confirm acyclic, no `ORDER_CYCLE`. Confirmed: 47/47 blocks ordered, no cycle.
- [x] 3.3 `.claude/skills/paper-writing/SKILL.md:225-229`: replace `22/7/11/2/2/1/1/1` with the measured shape from 3.1, keep the dated, "measured directly" framing; do not pin a count test to this number (pattern 7).

## Phase 4: Tests (RED before GREEN, all in `tests/test_paper_writing.py`)

- [x] 4.1 Mutation: delete `block-4b`'s new row → `PRODUCER_CHAIN_ABSENT`. Confirm red pre-edit, green post-edit; anchor on a non-`def`, non-docstring line.
- [x] 4.2 Mutation: delete one of the 6 retargeted `after` edges → `CHAIN_ROW_UNBACKED` (per consumer or parametrized).
- [x] 4.3 Mutation: restore `block-4b`'s dropped `produces_facts: contributions` alongside `mm-proposal`'s → `FACT_PRODUCER_DUPLICATE`.
- [x] 4.4 Mutation (D2 falsifier): alter one roster `\item` in a rendered `mm-proposal`, re-run `render --section materials-and-methods --block mm-proposal` → Components Check refuses. (Implemented via direct `paper_cli._resolve_expected_components` + `paper_obligation.check_components` calls against a synthetic rendered `mm-proposal` body, since the real `paper/main.tex` carries it empty today — design.md's own measured note.)
- [x] 4.5 Property: every block's `after` dependency resolves to a strictly earlier wave (no count asserted).
- [x] 4.6 Integration: `assemble_corpus` + `derive_order` succeed, acyclic, `mm-proposal` sole `contributions` producer.
- [x] 4.7 Before anchoring any mutation on a `paper_*.py` line, grep `tests/` for that literal text first (three anchors broke this way in one session).

## Phase 5: Spec and Coverage Gap

- [x] 5.1 `openspec/specs/fact-production/spec.md:175-181`: confirm the delta already drafted by `sdd-spec` is applied, not duplicated. Confirmed applied as-is; no changes made.
- [x] 5.2 Note only, no code without operator approval: the leakage guard scans `.claude/skills/paper-writing/` only, not `sections/`. `forge_vocabulary.shipped_documents(root)` already accepts any root, so covering `sections/` costs one new assertion call, no new scanning logic. Ask before adding. (Not implemented — operator approval not sought this session, per note-only instruction.)

## Phase 6: Full Verification

- [x] 6.1 Run `.venv/bin/python -m unittest discover -s tests -p "test_*.py"`; baseline 4577 tests/0 failures/3 skips — expect same or better. See apply return summary for exact observed counts.
- [x] 6.2 Diff each edited `sections/*.md` against its own header `source.quote` list; confirm no quoted byte span changed. Confirmed structurally: `assemble_corpus`'s `_verify_after_transcription` / `_verify_requirement_transcription` (whitespace-collapsed, markdown-emphasis-stripped `SPAN_NOT_IN_SOURCE` checks) pass clean over the real shipped corpus for every `after`/`requires_facts`/`produces_facts` quote, reused or new.

## Key Learnings

1. `_resolve_expected_components` reads only `^\\item (.*)$` lines, so Methods must carry a literal roster rather than treat the move as a tautology.
2. `title-and-keywords.title` needs a new chain row but no `after` edge — `_position_derived_edges` already orders M&M before it.
3. `forge_vocabulary.shipped_documents(root)` is root-parametrized, so covering `sections/` for vocabulary leaks is a one-call extension.
4. All 6 retargeted chain entries reuse existing `source.quote` text verbatim, leaving `SPAN_NOT_IN_SOURCE` nothing new to break.
5. The `SKILL.md` wave-shape claim is unmeasured until `phases` runs post-edit; no test may pin the resulting count.
