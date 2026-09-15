# Archive Report: each-document-names-its-own-revision

**Date archived**: 2026-09-11  
**Change**: each-document-names-its-own-revision  
**Status**: PASS WITH WARNINGS  
**Archived to**: `openspec/changes/archive/2026-09-11-each-document-names-its-own-revision/`

## Why This Change Existed

Cut 3 (`a-revision-is-two-documents`) shipped a two-document binding capability but encoded an untested assumption: that a single revision NAME could resolve against N document roots. The engine's own `revision_source` docstring stated: "a revision is the pair of files that name shares across DOCUMENTS[0]'s and DOCUMENTS[1]'s roots, not two independently-named artifacts."

However, the two real publishers emit completely different filenames:
- `proposal-deliberation` emits `proposals/research-concept-rNN.md`
- `experimental-deliberation` emits `experiments/experiments-<slug>-vNN.md`

No filename exists that both would produce. This change amends Cut 3 by requiring each document to resolve its revision name independently, from its own directory, under its own naming convention.

### How The Defect Read Green

Three compounding factors masked the failure:

1. **`revision_discovery` took no index** — it only searched document 0's root, never checking document 1's directory for alternatives
2. **`_extra_document_revisions` answered `sha256: None` without refusing** — unreadable documents wrote null entries into carriers instead of raising an error
3. **Cut 3's own test fixture wrote ONE shared filename into BOTH document roots** — a fixture written specifically to satisfy the false guard

This is the exact shape the project has already measured: "a proof demanded and then not actually written down."

## Requirements and Scenarios — Verification Status

**8/8 requirements met, 14/14 scenarios verified compliant**

| ID | Requirement | Status |
|:---|:---|:---|
| R1 | Each Document's Revision Name Is Its Own, Never Shared | ✅ |
| R2 | An Unnamed Document's Revision Is Discovered In Its Own Root | ✅ |
| R3 | Revision Discovery And The Verify Fidelity Fold Run Per Document | ✅ |
| R4 | An Unreadable Declared Document Refuses At Every Binding-Write Site | ✅ |
| R5 | A Committed Record Written Under The Shared-Name Assumption Remains Valid, Unedited | ✅ |
| R6 | The Fixture Reshape Reddens The Existing Pair Tests Unassisted | ✅ |
| R7 | The New Refusal Is Reachable By Mutation, Not Only By Construction | ⚠️ WARNING |
| R8 | implementation-engine-neutrality text correction (unreached_mathematics → unreached_modules) | ✅ |

## Warnings and Findings

### WARNING: The RED Control's Proof Is Incomplete (R7)

The design's R7 success criterion asks for three independent predicted reds (failure mechanisms):

1. **Red #1: `_doc1_sha256()` comparison** — ✅ VERIFIED  
   Commit `bec4d12`'s test suite demonstrates this red by halting at the first `assertEqual` on the sha256 comparison.

2. **Red #2: `extra_entry["status"] == "unknown"` assertion** — ⚠️ ASSERTED, NOT DEMONSTRATED  
   When called directly against `bec4d12`, this mechanism holds (verified independently). However, the committed suite never reaches this assertion because the sha comparison fails first and `assertEqual` exits the test immediately.

3. **Red #3: `compatibility["status"] == "ok"` assertion** — ⚠️ NOT DEMONSTRATED AS PREDICTED  
   The real pipeline crashes in `remedy_compatibility` with an unhandled `TypeError` (`"\n".join(texts)` over a list containing `None`) **before** `fidelityByDocument` is computed. This is a genuine pre-existing defect (fixed in Phase 2), not the mechanism R7 predicted.

**Conclusion**: No functional defect ships — the fix is correct and mutation-tested in Phase 3. However, the committed RED artifact demonstrates only 1 of 3 predicted mechanisms. The design's own success criterion cannot fully verify R7 through the red test suite alone.

**Recommendation for future strict-TDD changes**: Use separate test methods or `subTest` to prove independent mechanisms, never sequential assertions in one method where fail-fast semantics halt at the first failure.

### Two Latent Defects Discovered and Closed

Both were unreachable before this change because every document used to share one filename. This change exposed them by wiring real multi-document paths:

1. **`remedy_compatibility` crashed on None** — `"\n".join(texts)` over a list containing `None` when a finding named a document whose source resolved to `None`. Fixed in Phase 2.

2. **`position_state` conflated "never recorded" with "recorded, mismatched"** — both read `block_sha256=None`. This caused `_bound_to` to return `"stale"` when a document appeared for the first time, which would have silently raised `POSITION_STALE` and **blocked a legitimate first-time launch**. Reproduced by verify and correctly fixed.

## Measurements

**Verification status: PASS WITH WARNINGS** (per `verify-report`, observation #1736)

- **npm test**: 595/595 (baseline 595/595, unchanged)
- **Python suite**: Ran 2923 (baseline 2913, +10 new tests), OK (skipped=6, unmoved)
- **`sha256(tests/seal/digests.json)`**: `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` (byte-identical, measured twice)
- **Size**: 865 lines (against design's ~870 floor — first change this session to land AT estimate rather than over it)
- **D5 mutation**: Reproduced independently, refusal-code assertion survives
- **Non-interference confirmed**: All four skill directories show 0 changed files:
  - `tests/seal/`
  - `.claude/skills/proposal-deliberation/`
  - `.claude/skills/experimental-deliberation/`
  - `.claude/skills/_core/deliberation/`
- **Tasks**: 33/33 complete (all ticked [x], measured evidence recorded)
- **Spec merge**: Both delta specs merged into main specs mechanically:
  - `implementation-document-binding/spec.md` — 7 new requirements added
  - `implementation-engine-neutrality/spec.md` — text correction applied

## Artifacts Merged to Main Specs

| Domain | Status | Changes |
|:---|:---|:---|
| `implementation-document-binding` | Modified | 7 ADDED requirements (each-document names its own, discovery per document, per-document fidelity, refusal on unreadable, shared-name backward compat, fixture reshape, mutation proof) |
| `implementation-engine-neutrality` | Modified | Text correction: `unreached_mathematics` → `unreached_modules` in existing requirement (Cut 2 rename not propagated) |

## Observation IDs for Traceability

These observations represent the full SDD cycle for this change:

- **Proposal**: observation #1730 (sdd/each-document-names-its-own-revision/proposal)
- **Spec (concatenated deltas)**: observation #1731 (sdd/each-document-names-its-own-revision/spec)
- **Design**: observation #1732 (sdd/each-document-names-its-own-revision/design)
- **Tasks**: observation #1734 (sdd/each-document-names-its-own-revision/tasks)
- **Verify Report**: observation #1736 (sdd/each-document-names-its-own-revision/verify-report)
- **Archive Report**: persisted separately via Engram

## Key Learnings

1. A fixture written to satisfy a guard proves nothing about the guard's real necessity — it survived a FAIL, two corrections, and an archive before being measured against reality.

2. A parameter passed by none of its nine call sites looks identical to working code — `position_state`'s `extra_sources` made every document beyond 0 permanently `"unknown"` while tests passed.

3. Two readers of one carrier can pair it by label and by position and agree by accident for exactly as long as the values are identical.

4. Wiring a dead parameter exposes latent defects one layer over — paths never walked before start being walked, causing crashes in downstream code.

5. A crash can mask a downstream assertion twice at once: within one test method (fail-fast), and within the real command path (earlier exception).

## Archive Contents

- ✅ proposal.md
- ✅ specs/ (two delta files)
- ✅ design.md
- ✅ tasks.md (33/33 tasks complete)
- ✅ verify-report.md
- ✅ archive-report.md (this file)

## SDD Cycle Complete

This change has been fully planned, implemented, verified, and archived. The delta specs have been merged into the main specs in `openspec/specs/`. The change is ready for the next phase or integration.

**Note on the WARNING**: The recorded defect in R7 proof is not a functional issue — the implementation is correct. It is a documentation issue about what the RED test artifact actually proves. The warning is open and recorded for future reference.
