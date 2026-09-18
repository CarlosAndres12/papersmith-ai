# Tasks: The Phases Are Derived, Not Remembered

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~3,100–3,900 across 9 chained units |
| 1200-line budget risk | Low — no unit exceeds the ceiling; largest is unit 1 at ~780 |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 4 → PR 3 → PR 5 → PR 6 → PR 7 → PR 8 → PR 9 |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch chain — each unit branches off the previous, matching this repository's own precedent (b493151 → 432da9f → 45eae9d → cb965c4 → d1a13b5). Ceiling raised to 1200 by the operator; `size:exception` is not needed |

Decision needed before apply: No — settled
Chained PRs recommended: Yes
Chain strategy: feature-branch chain
1200-line budget risk: Low

## Refusal-Roster Reconciliation Ledger

`sdd-spec` and `sdd-design` ran in parallel and drifted on which refusal codes
actually exist. Every drift is closed by a task below — none is left
unmentioned.

| Code | Drift | Closed by |
|---|---|---|
| `INPUT_PARTITION_ABSENT` | Required by `contract-input-partition` spec; **absent from design** (no refusal-table row, no File Changes entry) | 1.1 (add to design.md), 1.2–1.5 (implement + test + classify) |
| `GUIDANCE_MARKDOWN_UNREADABLE` | Named in design D5; **no `redactor-packet` spec requirement** | 8.1 (add spec Requirement + scenario), 8.5 (implement + test) |
| `READINESS_BASIS_REQUIRED` | Named in design D3; **no `writing-readiness` spec requirement** | 6.1 (add spec Requirement + scenario), 6.4/6.7 (implement + test) |
| `SKELETON_ALREADY_DECIDED` | Named in design D4; **no `skeleton-startup` spec scenario** | 7.1 (add spec scenario), 7.8/7.11 (implement + test) |
| `SKELETON_ANSWER_REQUIRED` | Named in design D4; **no `skeleton-startup` spec scenario** | 7.1 (add spec scenario), 7.8/7.12 (implement + test) |
| `INPUT_PARTITION_ABSENT`'s knock-on | Design's own roster forecast (96 → 104, 8 codes) **omits this 9th code** | 1.1 notes the correction; roster target is **96 → 107** (`BLOCK_SUBUNIT_UNDECLARED` at 4.8f, `UNIT_HEADING_AMBIGUOUS` at 4.8h), tracked incrementally at 1.5 / 4.10 / 6.15 / 7.15 / 8.13 / confirmed at 9.5 |

## Open Questions Resolved At Task Time

- **Block-level vs section-level `optional`** (design Open Question 1): DECIDED block-level `optional: true` on every `rw-*` block — no schema change, no `_TOP_LEVEL_ALLOWED` widening. Task 2.2.
- **Does an `unprovenanced` block hold the `phases` wave gate?** (design Open Question 2): DECIDED an `unprovenanced` block counts as **written** for gating — provenance currency (`drifted`/`unprovenanced`) stays `plan`'s own separately-reported concern; conflating it with wave-gating would block writing on a documentation gap, not a missing dependency. Task 6.2.

## Work Unit Table

| # | Unit | Touches | New refusals | Est. lines | Budget risk | Depends on | Status |
|---|------|---------|---------------|------------|--------------|------------|--------|
| 1 | Normalize all ten contracts (`External inputs` / `Internal chain`) + shared `_verify_input_partition` checker + `06` backtick row-id gap | all ten `sections/*.md`, `paper_graph.py`, `paper_cli.py`, `design.md`, `tests/test_paper_contract.py`, `tests/test_paper_writing.py` | `INPUT_PARTITION_ABSENT` | ~780 | Low (ceiling 1200) | — | [x] |
| 1b | **Correction to unit 1.** Six of the eight `### Internal chain` "None" assertions unit 1 wrote were false, each contradicted by prose already in the same file — a read-only audit denies a real dependency, worse than the pre-unit-1 defect of merely not transcribing one. Replace the six false "None"s with real, quote-backed rows; rewrite the two genuinely-empty "None"s (`04`, `07`) into a checkable measurement sentence | `sections/01,02,03,04,05,07,09,10.md`, `tests/test_paper_contract.py` | none | ~90 | Low | 1 | [x] |
| 2 | `es-dataset` + `rw-*` optional + `mm-proposal` facts | `sections/01,02,05-*.md`, `tests/test_paper_contract.py` | none | ~110 | Low | 1 | [x] |
| 4 | Internal-chain → `after` transcription + both refusals | `paper_graph.py`, all ten `sections/*.md`, `paper_cli.py`, `specs/section-contract/spec.md` (verify only), `tests/test_paper_writing.py` | `CHAIN_ROW_UNRESOLVED`, `CHAIN_ROW_UNBACKED` | ~560 | High — consider a 4a(code+tests)/4b(edges) split if review flags it | 1, 2 | [x] |
| 3 | `optional` across readiness/verify | `paper_readiness.py`, `paper_verify.py`, `tests/test_paper_writing.py` | none (`OPTIONAL_BLOCK_ABSENT` is `UNMEASURED_REASONS`, not `Refused`) | ~230 | Med | 2 | [x] |
| 5 | `derive_waves` | `paper_graph.py`, `tests/test_paper_writing.py` | none (reuses `ORDER_CYCLE`) | ~260 | Med | 4, 3 | [ ] |
| 6 | `readiness` basis + `phases` verb | `paper_readiness.py`, `paper_declarations.py`, `paper_cli.py`, `specs/writing-readiness/spec.md`, `tests/test_paper_writing.py` | `READINESS_BASIS_REQUIRED`, `PHASE_NOT_READY` | ~500 | High (raised from design's Med — basis + a whole new verb in one unit) | 5 | [ ] |
| 7 | `skeleton` + disk inference + `ingested_papers` | `paper_declarations.py`, `paper_guidance.py`, `paper_cli.py`, `specs/skeleton-startup/spec.md`, `tests/test_paper_writing.py`, `tests/test_paper_decisions.py` | `SKELETON_ANSWER_REQUIRED`, `SKELETON_ALREADY_DECIDED`, `DATASET_PLACEMENT_CONFLICT` | ~520 | High | 2, 3, 6 | [ ] |
| 8 | `packet` + `segment_markdown` | `paper_guidance.py`, `paper_style.py`, `paper_leak.py`, `paper_cli.py`, `specs/redactor-packet/spec.md`, `tests/test_paper_writing.py` | `GUIDANCE_MARKDOWN_UNREADABLE` | ~390 | Med–High | 7 | [ ] |
| 9 | Docs / agent / docstring corrections | `SKILL.md`, `paper_cli.py` (docstring), `.claude/agents/insumos-observer.md`, `.claude/agents/style-sampler.md`, `tests/test_paper_writing.py` | none | ~120 | Low | all | [ ] |

## Work-Unit Evidence

| Unit | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|
| 1 | `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v` | `paper_cli.py contract` over the whole shipped corpus | Revert the ten `sections/*.md` edits + `_verify_input_partition`; text-only plus one pure function, no persisted state |
| 1b | `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v` | `paper_cli.py contract` and `paper_cli.py order` over the whole shipped corpus | Revert the eight `### Internal chain` prose edits + the eight recaptured `PRE_MIGRATION_BODY_DIGESTS` entries; text-only, no persisted state, no `after` edges wired |
| 4 | `.venv/bin/python -m unittest tests.test_paper_writing -v -k Chain` | `paper_cli.py contract` (zero refusals on the real corpus) | Revert `_verify_internal_chain` + the ten header `after` additions; `_verify_after_transcription` still guards edges added |
| 3 | `.venv/bin/python -m unittest tests.test_paper_writing -v -k Optional` | `paper_cli.py readiness --paper paper/` and `paper_cli.py verify` | Revert the two consumer diffs independently of unit 4/5 |
| 5 | `.venv/bin/python -m unittest tests.test_paper_writing -v -k Wave` | N/A — pure function, no CLI verb of its own yet (exercised via unit 6's `phases`) | Revert `derive_waves` + `_build_graph` extraction; `derive_order` restored to its pre-extraction body |
| 6 | `.venv/bin/python -m unittest tests.test_paper_writing -v -k Readiness` | `paper_cli.py readiness --paper paper/` then `paper_cli.py phases` against a scaffolded `paper/` | Revert `phases` verb + basis dispatch independently; `readiness`'s flag-only path is preserved as a fallback |
| 7 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions -v -k Skeleton` | `paper_cli.py skeleton --related-work yes --dataset-in experimental-setup` against a fresh scaffolded `paper/` | Revert `skeleton` verb + inference helpers; no writer added beyond `open_block`, so `main.tex` byte-identity is unaffected by rollback |
| 8 | `.venv/bin/python -m unittest tests.test_paper_writing -v -k Packet` | `paper_cli.py packet --section 06-introduction --block block-1` against the shipped `guidance/` tree | Revert `packet` verb + `segment_markdown`; `write`'s pipeline wiring reverts to no packet-assembly step |
| 9 | `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | full skill walkthrough per `SKILL.md`'s own verb tables | Revert docs/docstrings only — zero behavior change |

---

## Unit 1 — Notes / Deviations

- **Out-of-scope regression, not fixed (scope boundary honored).**
  `tests/test_paper_decisions.py::ReopenInvalidatesProvenanceEndToEndTests::
  test_reopen_then_plan_stops_reporting_current` builds a synthetic
  `reopen-e2e.md` contract whose body is a single sentence with no
  `### External inputs` / `### Internal chain` partition. Once
  `_verify_input_partition` is wired into `assemble_corpus`, `plan` on that
  fixture now refuses `INPUT_PARTITION_ABSENT` (exit 2) instead of
  succeeding, failing that one test. `tests/test_paper_decisions.py` is
  outside this unit's allowed edit roots, so it was left untouched rather
  than silently widened. The fix is a one-line fixture-body addition (the
  same two empty headings added to every other synthetic fixture in
  `tests/test_paper_contract.py` and `tests/test_paper_writing.py` this
  unit); it needs either a scope exception for that one file or a follow-up
  task. Confirmed as the ONLY failure across `test_paper_decisions`,
  `test_paper_citation`, `test_paper_evidence`, `test_paper_figure` (203
  tests, 1 failure).
- **Rows without a resolvable block id moved to `### Structural decisions`,
  never force-fitted with an invented id** (D1's own provision, extended
  from "subject is not a block" to "dependency is not a block"): in
  `01-materials-and-methods.md` ("the correct reading of an ambiguous
  equation"), `02-experimental-setup.md` ("how many blocks Assessment has",
  "the closing diagram"), `03-results-and-discussion.md` ("each artefact",
  "the third beat", "limitations"), `04-limitations.md` ("each item's
  citation"), `07-conclusions.md` (block 3's audience choice), and
  `09-title-and-keywords.md` ("whether the acronym appears").
- **`06-introduction.md`'s six original Internal Chain rows reduce to two
  genuine cross-block edges** once each row is checked against its
  header's own `requires_facts` (block-3/-4/-5 declare `problem-statement`/
  `formulation`/`results` as FACTS, not block ids) and against composite
  parts (4a/4b-partial/4b-complete/5-partial/5-complete are glosses on the
  SAME two qualified ids, so a row naming two glosses of the same block is
  intra-node sequencing, never a graph edge): `introduction.block-2` ←
  `introduction.block-4` (unchanged), and a new row making
  `introduction.block-4` ← `introduction.block-2` explicit (previously
  buried in the "three distinct sources" prose gloss). The other four
  rows' content is preserved verbatim under the new `### Structural
  decisions` heading — no information dropped, only relocated. This
  surfaces a real tension for unit 4: those two edges name the SAME pair of
  blocks in both directions, which would be `ORDER_CYCLE` if both became
  literal `after` edges — flagged here for unit 4's implementer to resolve
  (likely: only one direction is a real gating edge; the other is drafting
  guidance), not resolved in this unit, which wires no `after` edges at
  all.

---

## Unit 1b — Notes / Deviations

- **The defect this unit closes.** Unit 1 wrote a positive assertion of
  absence — "None — `x`, `y` and `z` depend only on the external inputs
  above; nothing here is derived from a sibling block's own prose" — into
  eight of the ten contracts' `### Internal chain` headings. Six of those
  eight were false, each contradicted by prose sitting in the same file.
  This is strictly worse than the pre-unit-1 defect (an untranscribed
  dependency): the contract now actively denies a dependency exists, and
  `assemble_corpus` validates the file as complete. A read-only audit
  established the six false files and the sentence deciding each verdict;
  this unit acts on that audit without re-deriving it.
- **`01-materials-and-methods.md`** — two rows: `mm-proposal` after
  `mm-borrowed-machinery` ("state the proposal as a delta on the borrowed
  machinery, with an explicit reference to the previous equation by
  number") and `mm-proposal` after `mm-dataset` ("The proposal is always
  the last subsection. Without exception."). `mm-preamble`'s own "It names
  the subsections that follow and their order" is not a third row: it
  needs to know which subsections exist, which is the dataset-placement
  structural decision already recorded in "Subsection order", never a
  dependency on a sibling block's own written prose.
- **`02-experimental-setup.md`** — one row: `es-assessment` after
  `es-dataset` (the closing diagram's "which data enter" panel needs
  `es-dataset`'s identity once that block exists as its own id).
- **`03-results-and-discussion.md`** — two rows chaining
  `rd-general-task` → `rd-contribution-blocks` → `rd-cost`, both backed by
  the same sentence: "It chains between blocks. A mechanism block opens by
  naming the previous block's result as the question it comes to answer."
- **`05-related-work.md`** — one row: `rw-closing` after
  `rw-problem-blocks` ("Name the fronts left open — as many as there are
  blocks. Two blocks, two fronts."). **Flagged, not force-fitted:** the
  file's own "Each block opens by naming its problem... and starts from
  the close of the previous block... The blocks are a chain, not parallel
  islands" describes the repeated specific-problem sub-blocks that all
  share the single id `rw-problem-blocks` (the schema has no `-1`/`-2`
  split the way `introduction.block-4a`/`4b` does). A row naming
  `rw-problem-blocks` as depending on itself would be a self-loop —
  `ORDER_CYCLE` in unit 4 — so this is intra-node sequencing under design
  D1's composite-parts / union rule, not a second cross-id row. Reported
  here rather than invented.
- **`09-title-and-keywords.md`** — one row: `keywords` after `title`
  ("The title carries the adjective; the keyword carries the noun.").
- **`10-back-matter.md`** — one row: `bm-acknowledgments` after
  `bm-funding` ("Present only when there is a project or institution to
  thank that is not already named under funding.").
- **`04-limitations.md` and `07-conclusions.md` (verdict TRUE, left as
  "None").** Both rewritten from a bare claim into a checkable measurement:
  naming exactly which block ids and which `requires_facts` were checked
  against the file's own prose body, and that no sibling-block prose
  reference was found. `07`'s block 3 placement option ("its own paragraph
  or the closing sentences of block 2") is called out explicitly as a
  placement choice, not a content derivation from block 2's own prose.
- **No `after` edges wired.** This unit only corrects the `### Internal
  chain` prose tables; transcribing them into quote-anchored `after`
  entries in the JSON header is unit 4's job (task 4.7 already covers all
  ten contracts). Every new row here was hand-traced against the others in
  its own file for cycles before landing — all are linear, acyclic,
  same-section chains.
- **`sections/02-experimental-setup.md`'s pre-existing `### Structural
  decisions` bullet** ("The closing diagram is... an internal composition
  rule within `es-assessment` itself, not a dependency on a sibling
  block") was left untouched per the no-rewording rule, even though it
  reads in tension with the new `es-assessment` ← `es-dataset` row: that
  bullet is about the diagram's compositional shape (what the "crossing"
  is made of), the new row is about one specific panel's content (`which
  data enter`) needing `es-dataset`'s identity. Left for a future
  operator/spec decision if that tension needs closing further; not
  invented or reworded here.
- **Digests recaptured, never deleted.** All eight touched contracts'
  `PRE_MIGRATION_BODY_DIGESTS` entries in `tests/test_paper_contract.py`
  were recomputed via `paper_contract.parse` over the edited files and
  replaced; `06-introduction.md` and `08-abstract.md` are untouched by
  this unit and their digests are unchanged (confirmed by recomputing
  both — identical to unit 1's captured value).

---

## Unit 2 — Notes / Deviations

- **Digest recapture.** `02-experimental-setup.md` and `05-related-work.md`
  both gained a prose-body row/comment (the new `es-dataset` External-inputs
  row; the Open Question 1 HTML comment), so their `PRE_MIGRATION_BODY_DIGESTS`
  entries in `tests/test_paper_contract.py` were recomputed and replaced.
  `01-materials-and-methods.md` only lost a JSON array entry
  (`mm-proposal.requires_facts`), which sits inside the header, never the
  body — its digest is unchanged, confirmed by recomputing it too.
- **`es-assessment`'s own `requires_facts` left untouched.** It still lists
  `"dataset"` directly, unconditionally, alongside the three facts
  `es-dataset` and `es-assessment` both partly answer to. Task 2.1 asked
  only to add the new `es-dataset` block and its table row, mirroring
  `mm-dataset` — not to rewire `es-assessment`'s own dependency list. That
  rewiring, if wanted, is a separate decision outside this unit's scope.
- **The "comment referencing design.md's Open Questions" lives in the
  prose body, not the JSON header.** The front-matter schema is closed
  (`_BLOCK_ALLOWED`/`_TOP_LEVEL_ALLOWED` reject unknown keys), so an
  arbitrary `_comment` key would refuse `MALFORMED_HEADER`. The decision
  is recorded as an HTML comment (`<!-- -->`, invisible in rendered
  markdown) directly above `05-related-work.md`'s "Whether the section
  exists" heading.

---

## Unit 4 — Notes / Deviations

- **Execution order deviated from this file's own listed order, on
  purpose.** Tasks 4.8g/4.8h/4.8i are listed in the file BEFORE 4.8b/4.8c/
  4.8d/4.8e/4.8f, which is backwards from their dependency order (4.8g
  fixes a residue that 4.8h's own extended check would flag, and 4.8h
  extends a check 4.8c hasn't been implemented yet at that point in the
  file). Implemented in dependency order instead:
  4.1–4.7 → 4.8b → 4.8c → 4.8d → 4.8e → 4.8f → 4.8g → 4.8h → 4.8i → 4.8 →
  4.9 → 4.10 → 4.11 → 4.12 → 4.13. All twenty-one subtasks are ticked; none
  were skipped.
- **The fourteen rows, mapped to holder/dependency/quote.** `01`
  (3: `mm-proposal`←`mm-borrowed-machinery`, `mm-proposal`←`mm-dataset`,
  `mm-preamble`←`mm-proposal`), `02` (1: `es-assessment`←`es-dataset`),
  `03` (2: `rd-contribution-blocks`←`rd-general-task`,
  `rd-cost`←`rd-contribution-blocks`), `05` (1: `rw-closing`←
  `rw-problem-blocks`), `06` (3: `block-2`←`block-4b`, `block-4a`←
  `block-2`, `block-4a`←`block-4b`), `08` (2: `slot-2`←`slot-4`, `slot-3`←
  `slot-2`), `09` (1: `keywords`←`title`), `10` (1: `bm-acknowledgments`←
  `bm-funding`). `04` and `07` stay at zero, untouched. Every quote is a
  literal, hand-traced substring of the named prose body — several wrap
  across source lines (`mm-preamble`'s own "It names the\nsubsections that
  follow and their order." is the exact case the launch brief warned
  about); `quote_in_body`'s whitespace collapse accepts all of them.
- **08's two rows were not in the launch brief's own count table and were
  found by re-reading the file in full**, not by trusting the earlier
  per-file summary. `abstract.slot-3`←`abstract.slot-2` is backed by
  `08`'s own sentence ("The purpose clause mirrors the deficiencies of
  slot 2, in the same order."). `abstract.slot-2`←`abstract.slot-4` has NO
  matching sentence anywhere in `08-abstract.md` itself — the file states
  its own graph "is the same one that governs the introduction" (line
  129–130), so this edge's `source.file` points at
  `sections/06-introduction.md`, reusing the exact quote backing
  `introduction.block-2`←`introduction.block-4b` ("this block is derived
  from the contributions, read backwards"). This is the same
  cross-file-source pattern the pre-existing `abstract`→`conclusions` edge
  already established (sourced in `07-conclusions.md`, not `08` itself) —
  never a new pattern, and never an invented quote.
- **4.8g's fix, and what it actually triggers.** `06`'s `## Block 4 —
  Proposal and contributions` heading is rewritten to `` ## Block 4 —
  Proposal and contributions (`block-4a`, `block-4b`) ``, naming both
  resolved ids explicitly. Measured: under `_verify_block_subunits`'s own
  loose suffix matching, this heading resolves to TWO ids (`block-4a`,
  `block-4b`), which is the `UNIT_HEADING_AMBIGUOUS` branch, not
  `BLOCK_SUBUNIT_UNDECLARED` as 4.8g's own prose loosely describes ("no
  declared id") — `BLOCK_SUBUNIT_UNDECLARED` fires only when a numbered
  heading matches ZERO ids under loose matching (a number nothing carries
  at all), which is a materially different fixture from a composite
  `Na`/`Nb` split. Both refusal shapes are covered by dedicated fixture
  tests (`BlockSubunitTests`); the discrepancy is reported here rather
  than silently reworded into the task text.
- **4.8i's own stated gate (heading-pattern presence) is refined, measured
  against the real corpus.** `01`, `02` and `05` all use the
  `## Slot|Subsection|Block N` HEADING convention 4.8i names, but their
  declared ids are content-named (`mm-dataset`, `es-assessment`,
  `rw-closing`, never `slot-1`/`subsection-1`/`block-1`). A gate keyed
  only on "does this section use numbered headings" would misfire
  `BLOCK_SUBUNIT_UNDECLARED` on `01`'s own `## Slot 1 — The dataset` (zero
  ids match "1" numerically). `_section_uses_numbered_ids` gates instead
  on whether the section's OWN declared ids carry a numeric suffix at
  all — true for `06`/`07`/`08` only among the six heading-numbered
  sections, false for `01`/`02`/`05` alongside the four content-named
  ones. `BlockSubunitTests.test_semantically_named_numbered_headings_
  never_misfire` asserts this measurement directly. This is a correction
  to 4.8i's own criterion, not a new capability — the real corpus was
  never at risk (`_verify_block_subunits` was written with this gate from
  the start), but the task's own stated gate would have been wrong had it
  been implemented literally.
- **Roster count moved 97 → 101 in one step, not the three separate moves
  (4.8f, then 4.10, then an implied third) the tasks artifact forecast in
  isolation.** All four new codes (`CHAIN_ROW_UNRESOLVED`,
  `CHAIN_ROW_UNBACKED`, `BLOCK_SUBUNIT_UNDECLARED`,
  `UNIT_HEADING_AMBIGUOUS`) live in `paper_graph.py`, already imported by
  `paper_cli.py` at module level — `reachable_paper_refusal_codes()`'s own
  whole-module scan makes all four reachable the instant their raise
  sites exist, regardless of implementation order. 4.8f's own "roster
  target rises to 106" is not the measured number; 101 is what
  `test_the_derivation_finds_the_measured_count` actually derives from
  source once every raise site and every classification entry landed —
  reported here rather than forcing the assertion to a number the
  derivation does not produce.
- **`test_back_matter_renders_last_...`'s own "back matter carries no
  `after` edge anywhere" assertion is now false** (Unit 4 wires
  `bm-acknowledgments` after `bm-funding`, intra-section) and was
  narrowed to "no CROSS-section edge", preserving the test's real intent
  (back matter's render position is not driven by any transcribed edge)
  without asserting a now-false absolute.
- **`06-introduction.md`'s digest moved again** (its third recapture in
  this change): the `## Block 4` heading rewrite is a genuine prose edit,
  unlike the fourteen `after` entries, which live entirely in the header
  and move no body digest.

---

## Phase 1: Normalize all ten contracts + `_verify_input_partition`

**Merged from 1a/1b/1c under the 1200-line ceiling.** Splitting them left the corpus half-normalized between PRs: `_verify_input_partition` runs inside `assemble_corpus`, so every un-normalized contract would refuse `INPUT_PARTITION_ABSENT` and take `contract`, `order`, `plan`, `readiness`, `verify` and `write` down with it until the last split landed.

- [x] 1.1 Edit `design.md`: add `INPUT_PARTITION_ABSENT | work-state` to the New Refusal Codes table, add `_verify_input_partition` to `paper_graph.py`'s File Changes row, and correct the roster forecast comment from "96 → 104" to "96 → 105" (see Reconciliation Ledger).
- [x] 1.2 Add `_verify_input_partition(corpus, bodies) -> None` to `paper_graph.py`, called from `assemble_corpus` before `_verify_internal_chain`; refuses `INPUT_PARTITION_ABSENT` naming whichever of `### External inputs` / `### Internal chain` is missing from a contract's prose body.
- [x] 1.3 RED test (write first): a fixture contract with a flat `## Inputs` table and no `### Internal chain` heading refuses `INPUT_PARTITION_ABSENT` naming that heading. `.venv/bin/python -m unittest tests.test_paper_contract -v -k InputPartition`
- [x] 1.4 RED test — mutation: delete `### Internal chain` from a previously-normalized fixture; confirm the guard fires live, not from a cached parse.
- [x] 1.5 Register `INPUT_PARTITION_ABSENT: WORK_STATE` in `paper_cli.REFUSAL_CLASSIFICATION`; move the assertion at `tests/test_paper_writing.py:3614` from 96 to 97.
- [x] 1.6 Normalize `sections/01-materials-and-methods.md`: `## Inputs` → `### External inputs` / `### Internal chain` (present-but-empty where no internal deps); rows lead with backticked `<section>.<block-id>` per design D1; move non-block-subject rows to `### Structural decisions`.
- [x] 1.7 Normalize `sections/02-experimental-setup.md` the same way.
- [x] 1.8 Normalize `sections/05-related-work.md` the same way.
- [x] 1.9 Regression scenario: `contract --file sections/06-introduction.md` still parses with no refusal (already-normalized file unaffected).
- [x] 1.10 Run `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v`.


- [x] 1.11 Normalize `sections/03-results-and-discussion.md`.
- [x] 1.12 Normalize `sections/04-limitations.md`.
- [x] 1.13 Normalize `sections/07-conclusions.md`, preserving the pre-existing `abstract`-after-`conclusions` quote transcribed in ITS OWN body (per `paper_graph.py`'s docstring — the edge is declared on `08-abstract.md` but sourced here).
- [x] 1.14 Verify the pre-existing literal edge survives heading normalization: `contract` reports no `SPAN_NOT_IN_SOURCE`.
- [x] 1.15 Run `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v`.


- [x] 1.16 Normalize `sections/08-abstract.md`.
- [x] 1.17 Normalize `sections/09-title-and-keywords.md` — text only; the position-derived edge (`_KEYWORD_BODY_*` constants) needs no code change.
- [x] 1.18 Normalize `sections/10-back-matter.md`.
- [x] 1.19 Rewrite `sections/06-introduction.md`'s existing `### Internal chain` rows to lead each cell with a backticked qualified id (e.g. `` `introduction.block-4` — 4b partial ``) — design's migration table marks `06` "already normalized" for the heading partition only; its rows are still bold-prose labels with no id, which would fail `CHAIN_ROW_UNRESOLVED` parsing in unit 4 on the one file assumed done.
- [x] 1.20 **REVISED after unit 1 closed, operator-settled:** `introduction.block-4` is SPLIT into `block-4a` / `block-4b`. The contract already declared it — "Two physical paragraphs, 120-180 words in total", `Paragraph 4a - the prose`, `Paragraph 4b - the list`, and a draftability line naming "1, 2, 3, 4a, 4b in partial form, and 6". Collapsing them produced a real `ORDER_CYCLE`: `block-2` depends on 4b while 4a depends on `block-2`. Decision 5's union rule is unchanged and still governs `block-5`, whose parts depend only on external facts; it simply has no answer when a block's parts straddle a sibling. Tests: `test_introduction_block_4_is_two_blocks_not_one_composite`, `test_the_internal_chain_of_the_introduction_is_acyclic`.
- [x] 1.21 Corpus-wide content smoke check: `paper_cli.py contract` over all ten files reports zero `INPUT_PARTITION_ABSENT` (chain-row backing itself is unit 4's concern, not this unit's).
- [x] 1.22 Run `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v`.

## Phase 1b: Correction — the false "None" internal-chain assertions

**A correction to unit 1, not a new capability.** Unit 1 wrote a positive
assertion of absence into every contract's `### Internal chain` heading; a
read-only audit found six of the eight non-`06`/`08` files' assertions
false, each contradicted by prose already in that same file. This phase
replaces the false claims with real, quote-backed rows and makes the two
genuinely-empty claims checkable, without wiring any `after` edge (unit
4's job) and without reformulating any existing sentence.

- [x] 1b.1 Read the audit table (parent-supplied); confirm each cited
  quote is still present, verbatim, in its file before acting on it.
- [x] 1b.2 `sections/01-materials-and-methods.md`: replace the "None" under
  `### Internal chain` with two rows — `mm-proposal` after
  `mm-borrowed-machinery`, and `mm-proposal` after `mm-dataset`.
- [x] 1b.3 `sections/02-experimental-setup.md`: replace "None" with one
  row — `es-assessment` after `es-dataset`.
- [x] 1b.4 `sections/03-results-and-discussion.md`: replace "None" with two
  rows chaining `rd-general-task` → `rd-contribution-blocks` → `rd-cost`.
- [x] 1b.5 `sections/05-related-work.md`: replace "None" with one row —
  `rw-closing` after `rw-problem-blocks`. Confirm the repeated
  specific-problem sub-blocks' own "chain, not parallel islands" language
  stays intra-node (same id, design D1's union rule) rather than being
  force-fitted into a self-referential row (would be `ORDER_CYCLE`).
- [x] 1b.6 `sections/09-title-and-keywords.md`: replace "None" with one
  row — `keywords` after `title`.
- [x] 1b.7 `sections/10-back-matter.md`: replace "None" with one row —
  `bm-acknowledgments` after `bm-funding`.
- [x] 1b.8 `sections/04-limitations.md` and `sections/07-conclusions.md`
  (verdict TRUE): rewrite the bare "None" claim into a checkable
  measurement sentence naming which block ids and which `requires_facts`
  were checked against the file's own prose body, and that no
  sibling-block prose reference was found — the assertion stays "None"
  but stops being a bare, unfalsifiable claim.
- [x] 1b.9 Hand-trace every new row against the others in its own file for
  cycles; confirm each file's chain is linear and acyclic (no `after`
  edges are wired yet, so this is a manual check, not a run of
  `derive_order`).
- [x] 1b.10 Recompute the eight affected `PRE_MIGRATION_BODY_DIGESTS`
  entries in `tests/test_paper_contract.py` via `paper_contract.parse`
  over the edited files; confirm `06-introduction.md` and
  `08-abstract.md` recompute to their unchanged, already-recorded digest.
- [x] 1b.11 Run `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v` (265 tests, green), `paper_cli.py contract` and `paper_cli.py order` (exit 0, 46 blocks in `order`), and `.venv/bin/python -m unittest tests.test_paper_decisions tests.test_paper_citation tests.test_paper_evidence tests.test_paper_figure -q` (203 tests, green).

## Phase 2: `es-dataset` + `rw-*` optional + `mm-proposal` facts

- [x] 2.1 Add `es-dataset` to `sections/02-experimental-setup.md`'s JSON header (`optional: true`, `requires_facts: ["dataset"]`, mirroring `mm-dataset`) and to its normalized tables.
- [x] 2.2 Resolve Open Question 1: set `optional: true` on every `rw-*` block id in `sections/05-related-work.md` (block-level, no schema change); record the decision as a comment referencing `design.md`'s Open Questions.
- [x] 2.3 Drop `implementation` from `mm-proposal.requires_facts` in `sections/01-materials-and-methods.md`, leaving `["formulation"]`.
- [x] 2.4 Scenario test: `contract --file sections/02-experimental-setup.md` shows `es-dataset` with `optional: true`, `requires_facts: ["dataset"]`.
- [x] 2.5 Scenario test: `mm-proposal.requires_facts` contains `formulation`, not `implementation`.
- [x] 2.6 Run `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -v`.

## Phase 4: Internal-chain → `after` transcription + both refusals

- [x] 4.1 Add `_verify_internal_chain(corpus, bodies)` to `paper_graph.py`, called from `assemble_corpus` right after `_verify_after_transcription` (same `bodies` dict, zero extra disk pass). Raises `CHAIN_ROW_UNRESOLVED` when a row's leading token is not a key of `corpus.blocks`; `CHAIN_ROW_UNBACKED` when it is a key but no `after` edge backs `(holder, dependency)`.
- [x] 4.2 RED test: a row naming only a paraphrase refuses `CHAIN_ROW_UNRESOLVED` naming the row's text.
- [x] 4.3 RED test — mutation: edit a mapping row to drop its qualified id; `CHAIN_ROW_UNRESOLVED` fires rather than reusing a stale mapping.
- [x] 4.4 RED test: a row naming a real block id with no backing edge refuses `CHAIN_ROW_UNBACKED` naming holder + dependency.
- [x] 4.5 RED test — mutation: remove the backing `after` entry, leave the row unchanged; `CHAIN_ROW_UNBACKED` fires (live edge-set read, not row-presence cache).
- [x] 4.6 RED test: corpus-wide, nine of ten named dependencies backed, one not — the run refuses on the one gap; no order/readiness/waves output is produced from the incomplete graph.
- [x] 4.7 For each of the ten contracts, add the block-level `after` entries backing every Internal-chain row from units 1, each `{target, source:{file, quote}}` with a verified literal quote (`paper_contract.quote_in_body`) — never an invented quote.
- [x] 4.8g **Residue left by the block-4 split, found by sweeping the class.** `sections/06-introduction.md` still carries `## Block 4 — Proposal and contributions`, a unit heading that now resolves to NO declared id (the two ids are `block-4a`/`block-4b`, named by its `###` children). Decide and apply: either the heading becomes an explicit grouping of the two, or it is rewritten. Prose that outlived its mechanism is the defect this change exists to close — leaving our own instance would be the worst kind.
- [x] 4.8h **The inverse guard, and the honest limit on it.** `BLOCK_SUBUNIT_UNDECLARED` catches a heading naming a sub-unit with no id. It does NOT catch a unit heading resolving to ZERO ids (4.8g's residue) or to SEVERAL. The several-case ships today and is correct: `04-limitations.md`'s `## Two sweeps, two kinds of gap` covers both `lim-proposal-items` and `lim-validation-items`. It is correct only because both ids exist — delete one and the heading keeps promising it, silently. Extend the check to "every unit heading resolves to exactly one declared id", refusing `BLOCK_SUBUNIT_UNDECLARED` for zero and a new `UNIT_HEADING_AMBIGUOUS` for several.
- [x] 4.8i **Scope the inverse guard to where the convention holds — measured, not assumed.** Only SIX of ten contracts use `## Block|Slot|Subsection N` headings. `03`, `04`, `09` and `10` name their blocks by content (`## Funding`, `## The closing`, `## Keywords`), so a count or resolve rule fires false positives on four of ten. The check must apply per-section, gated on that section actually using the numbered convention, and a test must assert it stays SILENT on all four content-named contracts. Measured 2026-09-18 across the full corpus: no hidden sub-unit remains anywhere; `block-4` was the only one, and `02`'s apparent mismatch was a false positive from a regex that missed `## Preamble` (no unit word).
- [x] 4.8b **`BLOCK_SUBUNIT_UNDECLARED` — the guard the block-4 split proved missing.** Every refusal this change ships checks TABLE -> GRAPH (a chain row naming a block). Nothing checks PROSE -> HEADER: the contract announced block 4's split in three places (its `**Extent. Two physical paragraphs**` line, the `### Paragraph 4a` / `### Paragraph 4b` headings, and a draftability line reading "1, 2, 3, 4a, 4b in partial form, and 6") and no guard fired, because none of the three is a chain row. A human reading found it.
- [x] 4.8c Add `_verify_block_subunits(corpus, bodies)` to `paper_graph.py`, called from `assemble_corpus`: a `###` heading whose text begins with a unit word (`Paragraph`, `Block`, `Slot`, `Subsection`, `Part`) followed by an identifier, sitting under a `## Block|Slot|Subsection N` parent, names a sub-unit the header must declare as its own block id. Refuses `BLOCK_SUBUNIT_UNDECLARED` naming the heading and its parent.
- [x] 4.8d MEASURED, zero false positives on today's corpus: six unit-headings carry `###` children, and five of those children are prose notes with no unit word (`What is cited here`, `The summary diagram`, `Two ways to walk a block...`, `Figures are permitted here...`). Only `06`'s two `### Paragraph 4a/4b` match, and both now resolve to declared ids. Assert BOTH directions in the test: the real corpus passes, and a fixture reintroducing a `### Paragraph 5a` under `## Block 5` without a matching id refuses.
- [x] 4.8e RED-first mutation: collapse `block-4a`/`block-4b` back to one `block-4` id in a fixture and confirm `BLOCK_SUBUNIT_UNDECLARED` fires — the guard must catch the exact anomaly that shipped unnoticed, not merely pass alongside it.
- [x] 4.8f Register `BLOCK_SUBUNIT_UNDECLARED: WORK_STATE` in `paper_cli.REFUSAL_CLASSIFICATION`; roster target rises to 106 (97 landed in unit 1, not the design's 96 baseline).
- [x] 4.8 Confirm the introduction's three chain rows become three `after` edges (`block-2` ← `block-4b`; `block-4a` ← `block-2`; `block-4a` ← `block-4b`) with no cycle, and that `block-5`'s glosses still union onto one node.
- [x] 4.9 Transcribe `mm-preamble`'s internal chain into a real edge (proposal Risks: it sits in the same wave as blocks it must name today); assert only edge existence here — placement is unit 5's test.
- [x] 4.10 Register `CHAIN_ROW_UNRESOLVED: WORK_STATE`, `CHAIN_ROW_UNBACKED: WORK_STATE`; move the roster assertion from 97 to 99.
- [x] 4.11 Confirm `specs/section-contract/spec.md`'s shipped scenarios ("every edge quote-backed", "no row left unmapped") hold against the real corpus: `paper_cli.py contract` reports zero refusals.
- [x] 4.12 Record the measured `collect_edges` size and a wave-shape estimate in a scratch note for unit 5 — waves must be measured, never assumed (proposal Risk: "only three edges exist today; waves collapse to 35/8/2").
- [x] 4.13 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_contract -v`.

## Phase 3: `optional` semantics — readiness and verify

- [x] 3.1 `paper_readiness.compute_block_readiness`: add `"optional"`, read verbatim from `BlockRecord.optional`, to every entry.
- [x] 3.2 Add the `"not-applicable"` status: optional AND unopened, under declaration-backed (`--paper`) basis only; unchanged under `supposed-only`. **Basis-independent half only — see Notes below.**
- [x] 3.3 RED test: `mm-dataset` reports `optional: true`; a non-optional block reports `optional: false`, over the shipped corpus.
- [x] 3.4 RED test: an optional unopened block reports `not-applicable` under `--paper` basis; the same block under flags-only reports `writable`/`blocked`. **Exercised via direct calls with explicit `opened`/`basis`, never an invented `--paper` flag — see Notes.**
- [x] 3.5 `paper_verify.py`: add `OPTIONAL_BLOCK_ABSENT` to `UNMEASURED_REASONS`; a check whose derived block set is entirely optional-and-unopened reports `unmeasured` with that reason, never `fail`. **Pure mechanism only — production wiring deferred, see Notes.**
- [x] 3.6 RED test: a coupling depending solely on an unopened optional block reports `unmeasured`/`OPTIONAL_BLOCK_ABSENT`.
- [x] 3.7 RED test: the same block declared optional but OPENED is checked exactly like a non-optional opened block — never `unmeasured` for being optional alone.
- [x] 3.8 Confirm `OPTIONAL_BLOCK_ABSENT` needs no `REFUSAL_CLASSIFICATION` entry and does not move the roster count; add a one-line comment at its definition recording that.
- [x] 3.9 Run `.venv/bin/python -m unittest tests.test_paper_writing -v`.

---

## Unit 3 — Notes / Deviations

- **3.2/3.4's own flagged seam, closed exactly as instructed.**
  `compute_block_readiness`/`compute_readiness` grew two keyword-only
  parameters, `opened` and `basis` (`opened_blocks` at the `compute_
  readiness` layer). `not-applicable` fires only when `block.optional`,
  `basis == "declaration-backed"`, and `opened is False`. Both default to
  values that make `not-applicable` unreachable (`opened=None`,
  `basis="supposed-only"`), so `cmd_readiness`'s own existing call — no
  keyword arguments — is byte-identical in behaviour to before this unit.
  **Deferred to Work Unit 6:** resolving `basis="declaration-backed"` and
  real per-block `opened` values from `--paper`'s disk read
  (`paper_declarations.read_satisfied`, `paper_block.read_status`) and
  wiring them into `cmd_readiness`. Neither `--paper` nor a basis field was
  invented on the CLI, per the launch brief.

- **A second, previously-unflagged dependency inversion, found while
  implementing 3.5-3.8 — reported, not silently worked around.** The
  literal spec scenario ("verify runs a coupling depending on `mm-dataset`'s
  content") implies `paper_verify.py`'s checks can tell whether a block is
  `optional`. They cannot: `Evidence` (`paper_coupling_evidence.py`) has no
  field carrying `BlockRecord.optional` — `blocks_by_fact` returns bare raw
  block ids with no optional annotation, and this module's own AST-enforced
  import allowlist (`_PAPER_VERIFY_ALLOWED_IMPORTS = {"re"}`) forbids it
  from ever calling `paper_graph.assemble_corpus` itself to find out.
  Threading `optional` from the corpus into something `paper_verify.py` can
  read requires editing `paper_coupling_evidence.py` (a new `Evidence`
  field) and/or `paper_cli.py` (`cmd_verify`, the only place that holds both
  `sections_dir` and calls `paper_verify.run`) — **neither file is in this
  unit's allowed edit roots.**

  Resolved the same way the launch brief modeled for 3.2/3.4: implemented
  the basis-independent half in full. `_optional_block_absence_reason`
  (new) and a new `optional_block_ids: frozenset = frozenset()`
  keyword-only parameter, threaded through all seven check functions and
  `run()`, decide `OPTIONAL_BLOCK_ABSENT` purely from `block_ids` +
  `optional_block_ids` + `evidence.block_bodies` membership (the last one
  already-available Evidence data — no new field needed for "opened").
  Checked ahead of the existing `BLOCK_NOT_DECLARED`/length-mismatch
  branches in `check_contribution_list`, `check_chain`, `check_gap`,
  `check_future_work` (and transitively `check_artefacts`, which calls
  `check_contribution_list`) — a block absent because its optional branch
  was never taken is a more precise explanation than "not declared", not a
  competing one. `check_citations`/`check_contract_currency` accept the
  same parameter, unused, only for `run()`'s uniform dispatch — their
  required evidence is never derived from `blocks_by_fact`, so no block's
  `optional` flag is ever relevant to either. The default `frozenset()`
  makes the branch unreachable for every caller that does not pass real
  ids, so `run(evidence)` — the only real call today — is behaviourally
  unchanged (proven directly, `test_run_default_optional_block_ids_never_
  changes_behavior`).

  Tests 3.6/3.7 build a real, on-disk fixture and pass a real
  `optional_block_ids` set (computed from a genuine `paper_graph.assemble_
  corpus` read) directly into `check_contribution_list` — proving the
  mechanism end to end, never through an invented CLI wiring.
  **Deferred, outside this unit's scope:** production wiring — `cmd_verify`
  resolving the corpus's optional block ids and passing them into
  `paper_verify.run`, which needs either a new `Evidence` field
  (`paper_coupling_evidence.py`) or a direct corpus read inside `cmd_verify`
  (`paper_cli.py`). Flagged here for the parent to route to a follow-up
  task/unit; not half-built in either of those two files.

- **RED-first discipline, verified by mutation on the test suite itself,
  not merely narrated.** For every RED task (3.3, 3.4, 3.6, 3.7), the
  implementation was stashed via `git stash` and the new tests were run
  first to confirm they failed (`TypeError`/`KeyError`, not a vacuous
  pass), then the stash was restored and the same tests re-run green. No
  test in `OptionalReadinessTests`/`OptionalVerifyTests` passed before its
  corresponding production change existed.

- **`test_mutation_8_a_write_in_paper_verify_fails_the_manifest_guard`'s
  anchor string updated.** This pre-existing mutation test's anchor was the
  literal source line `"def run(evidence) -> dict:"`; `run()`'s new
  `optional_block_ids` keyword-only parameter changed that line, so the
  anchor was updated to match exactly (`_run_against_mutant` asserts the
  anchor matches exactly once) — the mutation itself, and everything it
  proves, is unchanged.

- **Roster count, corpus, and waves confirmed undisturbed.** `reachable_
  paper_refusal_codes()` stays at 101 (`RefusalRosterTests`, unaffected —
  `OPTIONAL_BLOCK_ABSENT` is an `UNMEASURED_REASONS` member, never a
  `Refused`). `contract`/`order` both exit 0 over the real 47-block corpus,
  zero dangling edges. The Kahn frontier decomposition, recomputed
  directly from `collect_edges`, stays 28/11/5/2/1.

## Phase 5: `derive_waves`

- [ ] 5.1 Extract `_build_graph(corpus, edge_set) -> (successors, indegree)` from `derive_order`; `derive_order`'s own behavior and tests stay green, unmodified.
- [ ] 5.2 Add `derive_waves(corpus, edge_set) -> list[list[str]]`, reusing `_build_graph`, `_sort_key`, `_extract_minimal_cycle` + `ORDER_CYCLE` — no second cycle extractor, no new refusal.
- [ ] 5.3 RED test invariant 1: `set(chain(*waves)) == set(corpus.blocks) == set(derive_order(...))` over the real post-unit-4 corpus.
- [ ] 5.4 RED test invariant 2: for every edge `(before, after)`, `wave_of(before) < wave_of(after)`.
- [ ] 5.5 RED test invariant 3: waves sorted by `_sort_key`; membership identical when dict-iteration order is artificially perturbed.
- [ ] 5.6 RED test invariant 4: a fixture cycle refuses `ORDER_CYCLE` with the identical detail string `derive_order` produces.
- [ ] 5.7 RED test invariant 5 (negative): flattened waves are NOT asserted equal to `derive_order`'s sequence on a multi-frontier fixture — documents the rejected false lock.
- [ ] 5.8 Fixture tests: zero-edge corpus → one wave; a pure chain → N waves matching chain length.
- [ ] 5.9 Measure and record the real wave count/shape against the shipped corpus; compare against 4.12's scratch note — confirms waves are measured, not assumed.
- [ ] 5.10 Run `.venv/bin/python -m unittest tests.test_paper_writing -v`.

## Phase 6: `readiness` basis + `phases` verb

- [ ] 6.1 Edit `specs/writing-readiness/spec.md`: add a Requirement + scenario for `readiness` invoked with neither `--paper` nor any `--fact`/`--declaration` refusing `READINESS_BASIS_REQUIRED`.
- [ ] 6.2 Resolve Open Question 2: an `unprovenanced` block counts as WRITTEN for `phases`' gate; provenance currency stays `plan`'s own separate concern. Record as a code comment in the gating function and in `design.md`.
- [ ] 6.3 `paper_declarations`: expose a `read_satisfied(paper_dir)` reader reusing `_read_declarations`/`_verify_not_hand_edited`/`_body_or_default` — no second region reader.
- [ ] 6.4 `cmd_readiness`: `--paper` resolves → merge `read_satisfied`'s sets with any `--fact`/`--declaration` flags (flag-only additions labelled `"source": "supposed"`); flags with no `--paper` → preserve the hypothetical path, `"basis": "supposed-only"`; neither → refuse `READINESS_BASIS_REQUIRED`.
- [ ] 6.5 RED test: `declarations` region records `formulation` satisfied, no `--fact` flags → blocks whose only gap was `formulation` report `writable`.
- [ ] 6.6 RED test: `readiness --fact dataset` on the same paper (formulation recorded, dataset not) → a block requiring both reports `writable`.
- [ ] 6.7 RED test: `readiness` with neither `--paper` nor any flag refuses `READINESS_BASIS_REQUIRED`.
- [ ] 6.8 Integration test: real `declare` write, then `readiness --paper` re-read shows the changed answer with no flags repeated.
- [ ] 6.9 Add `phases [--phase N]` to `paper_cli.py`: waves 1..N with per-block readiness, `opened`, provenance state, per-wave `complete|open|gated`; `--phase N` refuses `PHASE_NOT_READY` naming the unwritten wave-(N-1) non-optional block, honoring unit 3's optional-excuses-absence semantics.
- [ ] 6.10 RED test: wave 1's non-optional block unwritten → `write` on a wave-2 block refuses `PHASE_NOT_READY` naming it.
- [ ] 6.11 RED test: wave 1 complete → the same wave-2 `write` proceeds with no refusal.
- [ ] 6.12 RED test: wave 1 holds one written non-optional + one unwritten optional block → wave-2 `write` raises no refusal.
- [ ] 6.13 Implement the read-only "plan awaiting approval" report shape — the skill must present the full wave plan and not begin writing until it is explicitly approved (unit 9 wires `SKILL.md` prose to this).
- [ ] 6.14 Read-only proof: before/after content-manifest over `paper_dir` for `phases` and `readiness` — writes nothing under every input, including refusal paths.
- [ ] 6.15 Register `READINESS_BASIS_REQUIRED: INVOCATION_DEFECT`, `PHASE_NOT_READY: WORK_STATE`; move the roster assertion from 99 to 101.
- [ ] 6.16 Run `.venv/bin/python -m unittest tests.test_paper_writing -v`.

## Phase 7: `skeleton` + disk inference + `ingested_papers`

- [ ] 7.1 Edit `specs/skeleton-startup/spec.md`: add scenarios for `skeleton` refusing `SKELETON_ALREADY_DECIDED` (flags contradict disk) and `SKELETON_ANSWER_REQUIRED` (a required flag missing).
- [ ] 7.2 Pure inference over `paper_block.read_status(paper_dir)["blocks"]` intersected with the corpus: `relatedWork` (any opened id under `related-work`); `datasetPlacement` (`materials-and-methods` / `experimental-setup` / `undecided` / conflict when both `mm-dataset` and `es-dataset` are opened).
- [ ] 7.3 RED test: `es-dataset` opened alone → placement reports "Experimental Setup" from opened ids alone.
- [ ] 7.4 RED test: both dataset blocks opened → refuses `DATASET_PLACEMENT_CONFLICT` naming both ids.
- [ ] 7.5 RED test — mutation: inference reads `read_fact("skeleton")` instead of `read_status`; a fixture where the two disagree goes red.
- [ ] 7.6 `paper_guidance.ingested_papers(guidance_dir)`: pure `Path.iterdir()` walk (gitignore-blind by construction) over `guidance/<root>/<paper>/<paper>.md`; `plan`/`packet` report `{root: [{folder, markdown}]}`.
- [ ] 7.7 RED test: a `guidance/` tree matching a `.gitignore` pattern and holding files reports as populated, not empty — assert against the measured baseline (3 roots, 8 `.md`).
- [ ] 7.8 `skeleton --related-work yes|no --dataset-in materials|experimental-setup`: opens every non-excluded block id via `paper_block.open_block` in `derive_order` order (never a new writer); idempotent; refuses `SKELETON_ALREADY_DECIDED` on contradiction, `SKELETON_ANSWER_REQUIRED` on a missing flag.
- [ ] 7.9 RED test: fresh `main.tex`, both flags given → both blocking questions asked before the skeleton opens; the chosen dataset block only is opened (the other left unopened).
- [ ] 7.10 RED test: existing skeleton, fresh process → neither question asked again.
- [ ] 7.11 RED test: flags contradicting disk state → `SKELETON_ALREADY_DECIDED`.
- [ ] 7.12 RED test: a missing flag → `SKELETON_ANSWER_REQUIRED`.
- [ ] 7.13 Threat-matrix RED test (write amplification): mutate `skeleton` to write `main.tex` directly, bypassing `open_block` — the byte-identity mutation harness fails.
- [ ] 7.14 Threat-matrix RED test (path containment): `skeleton --paper ../x` / `--sections ../y` refuse `PAPER_OUTSIDE_REPOSITORY` / `SECTIONS_OUTSIDE_REPOSITORY` (existing codes, reused verbatim via `paper_scaffold.resolve_paper_dir`/`paper_contract.resolve_sections_dir`, no roster move) and write nothing.
- [ ] 7.15 Register `SKELETON_ANSWER_REQUIRED: INVOCATION_DEFECT`, `SKELETON_ALREADY_DECIDED: WORK_STATE`, `DATASET_PLACEMENT_CONFLICT: WORK_STATE`; move the roster assertion from 101 to 104.
- [ ] 7.16 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions -v`.

## Phase 8: `packet` + `segment_markdown`

- [ ] 8.1 Edit `specs/redactor-packet/spec.md`: add a Requirement + scenario for an unreadable `guidance/*.md` refusing `GUIDANCE_MARKDOWN_UNREADABLE` during outline assembly.
- [ ] 8.2 `segment_markdown(body)`: end a section at the next heading of level ≤ its own (never same-level-only); EOF only when no such heading follows; a headingless paper reports `{"headings": [], "reason": "NO_HEADINGS"}`.
- [ ] 8.3 RED test (must go red before the fix): a fixture whose last section is a deeper-level appendix is swallowed under the same-level-only rule; confirm the fix keeps it.
- [ ] 8.4 RED test: `NO_HEADINGS` reported for a headingless guidance `.md`, never a silent empty list.
- [ ] 8.5 RED test: an unreadable `.md` refuses `GUIDANCE_MARKDOWN_UNREADABLE`.
- [ ] 8.6 `packet --section <stem> --block <id>` (read-only): emits the block's own contract prose verbatim plus, per `style-reference`-classed entry, a heading OUTLINE (`{title, level, byte_start, byte_end}`) only — never inlined span text.
- [ ] 8.7 RED test (leak proof): a mutated `packet` that inlines span text instead of offsets — assert "no reference byte in the payload" goes red without the offsets-only fix.
- [ ] 8.8 RED test: a `noEquivalent` style-reference entry contributes nothing; assembly does not refuse on its account.
- [ ] 8.9 Wire packet's style extracts through the existing `paper_style.resolve_style_set` call path only — no second resolution path; extracts land in the same recorded `R`.
- [ ] 8.10 RED test: `R` read back after assembly contains exactly the two extracts a two-reference packet resolved.
- [ ] 8.11 Leak-tripwire proof: run the existing `STYLE_OVERLAP` tripwire, register-distance and relative-overlap proofs against a packet's own extracts using exactly `R`; confirm no violation attributable to material outside `R`, and confirm material not in `R` is refused before assembly.
- [ ] 8.12 `writing-orchestration`: wire packet assembly ahead of `write`'s `draft` stage — a draft stage invoked without an assembled packet must not proceed; shuttle through files only (`NoSubprocessScanTests` coverage).
- [ ] 8.13 Register `GUIDANCE_MARKDOWN_UNREADABLE: WORK_STATE`; move the roster assertion from 104 to 105 (final target — all nine reconciled codes accounted for).
- [ ] 8.14 Read-only proof: before/after content-manifest for `packet` — writes nothing under every input, including refusal paths.
- [ ] 8.15 Run `.venv/bin/python -m unittest tests.test_paper_writing -v`.

## Phase 9: Docs / agent / docstring corrections

- [ ] 9.1 `SKILL.md`: 17 → 20 verbs; add `phases`, `skeleton`, `packet` to the verb tables and Refuses columns; fix the stale `readiness` row to document the `--paper`/basis behavior.
- [ ] 9.2 `paper_cli.py` module docstring: "thirteen verbs" → "twenty verbs" (also corrects the pre-existing 13-vs-17 drift, not only the three new verbs).
- [ ] 9.3 Fix `.claude/agents/insumos-observer.md`'s write-tool/shuttle mismatch; confirm its declared tool list matches the shuttle-file contract `observe` actually reads.
- [ ] 9.4 Confirm `.claude/agents/style-sampler.md`'s frontmatter/tool list matches consuming the packet's outline (offsets), not inline reference text.
- [ ] 9.5 Confirm the final `reachable_paper_refusal_codes()` count is exactly **105** (96 baseline + `INPUT_PARTITION_ABSENT`, `CHAIN_ROW_UNRESOLVED`, `CHAIN_ROW_UNBACKED`, `READINESS_BASIS_REQUIRED`, `PHASE_NOT_READY`, `SKELETON_ANSWER_REQUIRED`, `SKELETON_ALREADY_DECIDED`, `DATASET_PLACEMENT_CONFLICT`, `GUIDANCE_MARKDOWN_UNREADABLE`) — not design's own 104 forecast, which omitted `INPUT_PARTITION_ABSENT`.
- [ ] 9.6 Full-suite run: `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` green.
- [ ] 9.7 Walk `proposal.md`'s Success Criteria checklist and tick every box against what actually shipped; note any item that did not close and why.
