# Archive Report: The Tripwire Reaches The Section That Feeds It

**Date Archived**: 2026-09-20  
**Change**: the-tripwire-reaches-the-section-that-feeds-it  
**Branch**: wu0-the-math-fence-stops-leaking (5 commits ahead of main)  
**Archive Destination**: `openspec/changes/archive/2026-09-20-the-tripwire-reaches-the-section-that-feeds-it/`  
**Artifact Store Mode**: hybrid (filesystem + Engram)  
**Status**: CLOSED — All tasks complete, verification passed, specs merged, change archived.

---

## Final State Summary

This change introduces a sibling guard (`SOURCE_SECTION_VERBATIM` refusal) that prevents a `transposition`-mode block from reproducing its bound source section verbatim. It also fixes two live implementations of `strip_math` (in both `paper_style.py` and `paper_bindings.py`) that failed to exclude `$$...$$` display math fences, and wires the binding machinery from `_resolve_write_gate` into `BlockContract.source_sections` so the new check has concrete data to work with.

**Authority Hierarchy Applied**:
1. **Persisted tasks artifact**: All 53 tasks marked complete (`[x]`)
2. **Explicit final-state facts in launch prompt**: Verify PASS with 0 critical findings; 153 refusals measured; 289 engine lines; 4406 tests (1 pre-existing failure)
3. **Verify-report and apply-progress**: intermediate snapshots, valid at their time

---

## Tasks Completion Status

**Total**: 53  
**Complete**: 53 (every task `[x]`)  
**Incomplete**: 0  

All four work units (WU0–WU3) are closed:
- **WU0**: `$$` fence fix + blast radius measurement — 16 tasks, all complete
- **WU1**: Wiring gap (`_resolve_write_gate` → `Corpus` → `BlockContract.source_sections`) — 12 tasks, all complete
- **WU2**: Threshold, sibling check, wiring into `write_block` — 21 tasks, all complete
- **WU3**: Neutrality gate, roster re-measure, both suites, falsification obligation — 4 tasks, all complete

**Gate Passed**: Task Completion Gate validates all 53 are complete.

---

## Specs Merged (OpenSpec Mode)

Three delta specs have been merged into main specs using native `gentle-ai sdd-archive-compose`:

### New Capability
- **`transposition-fidelity`**: Mechanical copy (no main spec existed)
  - 6 requirements, 18 scenarios
  - Guards against verbatim reproduction of bound source sections inside transposition-mode blocks
  - Refusal code: `SOURCE_SECTION_VERBATIM`
  - Threshold is self-calibrated per contract prose, with `SOURCE_RUN_BACKSTOP = 16` as floor
  - Guard fires inside `write`, before `substitute`, never in read-only verbs
  - Per-section floor, threshold, and longest run reported whether check refused or passed

### Modified Capabilities
- **`style-leak-detection`** (composed)
  - 2 requirements, 7 scenarios
  - Added: `$$...$$` display fence exclusion to `_MATH_DISPLAY_RE` in both implementations
  - Preserved: all existing overlap and tripwire machinery untouched
  - Derived sweep test (introspects every `strip_math`/`_strip_math` under `scripts/`, never hand-listed pair) catches any new normalizer that omits the fence pattern

- **`evidence-bound-drafting`** (composed)
  - "Structural Sentences Are Typed" requirement now correctly excludes `$$...$$` fences in `paper_bindings._strip_math`
  - Same fence pattern added to its own `_MATH_DISPLAY_RE`, mirror of the fix in `paper_style.py`

---

## Verification Report Outcome

**Verdict**: `pass_with_warnings` (0 critical findings, 0 blockers)

### Build & Tests Summary
- **TypeScript**: `npx tsc -p tsconfig.json` — exit 0, empty output ✓
- **JavaScript**: `npm test` — 640/640 tests pass ✓
- **Python Suite** (run in 6 sequential chunks per documented `implementations/` race discipline):
  - `test_paper_writing`: 526/526 ✓
  - `test_paper_*` (7 modules): 582/582 ✓
  - `test_agents`, `test_experimental_*`, `test_extract_pdf`, `test_forge_*`, `test_implementation_*`: 485/485 ✓
  - `test_kaggle_accounts`: 63/63 ✓
  - `PYTHONPATH=tests test_orphan_sweep`: 7/7 ✓
  - `test_proposal_implementation`, `test_remote_execution`, `test_skill_audit`, `test_suite_collects`: 2743 tests, **exactly 1 known pre-existing failure** (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`, unrelated to this change — generic word "mechanisms" in `experimental-deliberation/SKILL.md`), 3 skipped ✓

**Total**: 4,406 tests across all suites, exactly 1 pre-existing failure, 0 new failures ✓

**Note**: A spurious failure in an earlier attempt (`test_the_toy_targets_left_nothing_behind`) was caused by a stray `implementations/` scratch directory from a killed verifier subprocess — a live instance of the documented cross-chunk race. Removed and re-ran clean. This is a methodology artifact, not a defect in the change's code.

### Spec Compliance
All 9 requirements / 29 scenarios across three delta specs are compliant. Key verifications:
- Fence fix confirmed in both `paper_style.py` and `paper_bindings.py`
- Derived cross-module sweep (introspecting `SKILL_SCRIPTS.glob("*.py")`) validates generality
- `check_source_section_verbatim` is a pure addition to `paper_leak.py` — `check_tripwire` bytes untouched
- New refusal fires inside `write_block` before `substitute`, after `check_tripwire`, guarded on `contract.mode == MODE_TRANSPOSITION`
- Mode derivation uses named constants (`MODE_TRANSPOSITION`, `MODE_ARGUMENT`, `MODES`) instead of bare string literals
- All mutations (8 across WU2, 2 across WU1) confirmed green before and red after changes, proving guard reachability

---

## Engine Lines and Code Metrics

**Engine Code** (lines under `.claude/skills/paper-writing/scripts/`):
- Current total: **289 lines**
- Budget: 1600 (owner-raised twice, 2026-09-20)
- Risk: Low-Medium

**Breakdown by Work Unit** (measured):
| Unit | Engine (est.) | Test/Fixture (est.) | Docs (est.) | Total (est.) | Status |
|---|---|---|---|---|---|
| WU0 | ~50 | ~185 | ~15 | ~250 | Complete |
| WU1 | ~120 | ~175 | 0 | ~295 | Complete |
| WU2 | ~110 | ~230 | ~15 | ~355 | Complete |
| WU3 | ~0 | ~140 | ~10 | ~150 | Complete |
| **Running Total** | | | | ~1050 | **Complete** |

**Refusal Roster** (measured live):
- Pre-change baseline: 144 refusal codes
- Post-change measured: **153 refusal codes**
- New codes this change: 1 (`SOURCE_SECTION_VERBATIM`)
- Newly-reachable existing codes: 8 (via wired-in imports from WU1's `paper_source_span.py` and its dependencies)

---

## Archive Contents Checklist

- [x] proposal.md — scope, capabilities, approach
- [x] specs/ — three delta specs (transposition-fidelity, style-leak-detection, evidence-bound-drafting)
- [x] design.md — full design with decisions, data flow, refusal codes, measurement specs
- [x] tasks.md — 53 complete tasks (WU0–WU3)
- [x] verify-report.md — verification outcome, test breakdown, spec compliance
- [x] exploration.md — exploration work and findings
- [x] math-fence-blast-radius.md — before/after measurement of the `$$` fence fix blast radius

**Source of Truth Updated**:
- `openspec/specs/transposition-fidelity/spec.md` ✓ (created)
- `openspec/specs/style-leak-detection/spec.md` ✓ (merged)
- `openspec/specs/evidence-bound-drafting/spec.md` ✓ (merged)

---

## Key Decisions & Design Notes

### Decision A: The `$$` Fence Fix (WU0)
Two independent implementations of `strip_math` both failed to exclude `$$...$$` display equation fences. The inline pattern `$...$` matched the first two adjacent delimiters as an empty span, leaving the body as prose. Fixed by adding `\$\$.*?\$\$|` ahead of existing alternatives, with before/after measurement:

**Blast Radius (measured on single real document)**:
- Normalized token count: **−1,108 tokens (−14.8%)**
- The style tripwire had been counting ~1,108 equation tokens as prose
- Before-table captured on unmodified tree; after-table after both fixes landed

**Generality**: Derived cross-module sweep (introspects `SKILL_SCRIPTS.glob("*.py")`) ensures any new `strip_math` callable is caught by test, never a hand-maintained list.

### Decision B–D: The Sibling Check (WU2)
`check_source_section_verbatim` is a new function in `paper_leak.py`, sibling to `check_tripwire`:
- Reuses `overlap_against_set` and `tripwire_spans` verbatim (no new overlap logic)
- Per-section threshold: `max(source_section_floor(...), SOURCE_RUN_BACKSTOP)` where `SOURCE_RUN_BACKSTOP = 16`
- Refuses `SOURCE_SECTION_VERBATIM` on first run STRICTLY exceeding threshold
- Reports per-section `{"floor", "threshold", "longest_run"}` on every path, not silently inferred
- Guarded on `contract.mode == MODE_TRANSPOSITION` (argument-mode blocks are exempt)
- Fires inside `write_block` after `check_tripwire`, before `substitute`

**Threshold Rationale**: 8 tokens (the original tripwire floor) is tuned for style references where reuse is forbidden. A source document is the same author's earlier text about the same work — reuse is legitimate far higher. 16 tokens is calibrated against independent published prose norms; the design records what would falsify it.

### Decision E: Wiring (WU1)
`_resolve_write_gate` already assembled `Corpus` with `enforce_bindings=True` but returned `None`. Now:
1. Returns the `Corpus` instead
2. `cmd_write` calls `paper_source_span.resolve_bound_sections(corpus, qualified_id)`
3. Result fills `BlockContract.source_sections` (new field, defaulted to `()`)
4. `write_block` receives plain text/tuples, never touching disk

**Note**: This also made true a claim the previous change's archived design shipped but the code never honored — `paper_graph.py`'s memo was widened by concurrent change to include outline shape, which `paper_source_span.py` now uses to slice sections.

---

## Open Items & Future Work

### Carried Forward (Recorded, Not Silently Dropped)

1. **Where the transposition block's redactor obtains its prose is unresolved.** Today it arrives by hand, so the skill cannot know what the redactor was shown — only judge what came back. This is a shuttle gap, not a guard gap. Belongs to whoever widens `packet`.

2. **Nothing verifies that a transposition block asserts only what its bound section carries.** Content verification against a located span exists today only for citations. This is a separate, real gap — named in proposal, not folded into this change.

3. **Threshold falsification is unexecutable today.** Per design.md Decision C: when three real `document` bindings exist on disk, execute two falsifiers:
   - A transposed draft (same claim, the paper's own register) whose longest shared run with its bound section reaches 16 → 16 is too low
   - A sentence pasted verbatim from the bound section whose normalized run is under 16 and passes → 16 is too high
   
   Either observation moves ONE named constant in `paper_leak.py`, nothing else. **This obligation is unexecutable today** because no real `document` binding exists on disk (every bindable requirement is `undecided` per `transposition-fidelity`'s own spec preamble). It is stated as a live, open obligation on the next real `bind`, not silently waived.

### Disclosed Pre-Existing Gaps

1. **Widening to `argument`-mode blocks.** The spec exists; the guard does not check them. Explicit design decision, not an oversight.

2. **Generalist vocabulary collisions across three sibling skills.** `ForgeVocabularyDerivedGuardTests` reports one known failure: `experimental-deliberation/SKILL.md` uses "mechanisms" (a generic English word). An audit counted 48 occurrences of "mechanisms" across the three skills, including in `profile.ts` labels. Awaiting owner's ruling on whether a single sanctioned configuration point for product names is acceptable at all. `paper-writing` itself is clean.

3. **One per-field refusal detail test is missing.** No dedicated test names all five fields of `SOURCE_SECTION_VERBATIM`'s detail message as its own scenario.

4. **Engram's `apply-progress` topic upserts per unit.** Intermediate work-unit evidence is not retrievable once superseded by a later commit. This is architectural, not a defect in this change.

5. **All end-to-end paths are synthetic.** No real `document` binding exists on disk, so all paths run on `bind`-recorded fixtures. State the limit; do not imply it away.

---

## Mechanical Archive Operations

All archive operations used shell commands with mandatory `diff -r` verification:

### Spec Merge Operations
1. **style-leak-detection**: `gentle-ai sdd-archive-compose` (main spec exists) — exit 0 ✓
2. **evidence-bound-drafting**: `gentle-ai sdd-archive-compose` (main spec exists) — exit 0 ✓
3. **transposition-fidelity**: Mechanical copy with `cp -R` and diff verification (new spec) — exit 0, empty diff ✓

### Folder Move Operation
- **Source**: `openspec/changes/the-tripwire-reaches-the-section-that-feeds-it`
- **Destination**: `openspec/changes/archive/2026-09-20-the-tripwire-reaches-the-section-that-feeds-it`
- **Method**: `git mv` (tracked folder)
- **Verification**: Pre-move snapshot + post-move `diff -r` (empty) ✓
- **Exit Status**: 0 ✓

---

## SDD Cycle Complete

**Proposal**: ✓ Defined scope, capabilities, and approach  
**Spec**: ✓ Three delta specs (1 new, 2 modified) authored  
**Design**: ✓ Full design with decisions A–E, data flow, refusal codes, measurement specs  
**Tasks**: ✓ 53 tasks defined, all executed and complete  
**Apply**: ✓ 4 work units implemented, all code present  
**Verify**: ✓ Passed with 0 critical findings, 4406 tests green (1 pre-existing failure)  
**Archive**: ✓ Specs merged, change folder moved, archive report written  

The change is ready for review and delivery. No follow-up SDD cycles recommended.

---

## Artifact Store Metadata

**Artifact Store Mode**: hybrid  
**Filesystem Archive Location**: `openspec/changes/archive/2026-09-20-the-tripwire-reaches-the-section-that-feeds-it/`  
**Engram Topic Key**: `sdd/the-tripwire-reaches-the-section-that-feeds-it/archive-report`  
**Project**: papersmith-ai  

Both filesystem and Engram copies written at close.
