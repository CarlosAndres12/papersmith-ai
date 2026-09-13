# SDD Archive Report — the-agreement-nothing-computes (Slice D)

**Change**: `the-agreement-nothing-computes`  
**Archived to**: `openspec/changes/archive/2026-09-12-the-agreement-nothing-computes/`  
**Archive Date**: 2026-09-12  
**Status**: Complete and Archived

## Verification Status

**Verify Verdict**: PASS WITH WARNINGS (0 CRITICAL, 4 WARNING, 2 SUGGESTION)  
**Requirements**: 19/19 ✓  
**Scenarios**: 46/46 ✓  
**Archive Authorization**: Operator-approved (explicit ruling: archive when verify passes)

## Change Deliverables

This change delivered the operator's final two of six requirements:

- **Item 3**: When the implementation contradicts the experiments document, publish a successor of it, with its tests.
- **Item 4**: Once everything agrees, reuse Flow B's paths to reach a test submission.

**Completion Status**: All six operator requirements are now delivered across the full change chain.

## Artifact Observation IDs (Engram)

- `proposal`: #1761
- `spec`: #1770
- `design`: #1771
- `tasks`: #1772
- `verify-report`: #1800

## Specs Synced

Two new full specs were copied mechanically to `openspec/specs/`:

| Domain | Action | Details |
|--------|--------|---------|
| `implementation-cross-document-agreement` | Created (new full spec) | 7,282 bytes |
| `implementation-block-locator` | Created (new full spec) | 5,257 bytes |

Four delta specs were merged into existing main specs:

| Domain | Action | Details |
|--------|--------|---------|
| `implementation-document-binding` | Modified | Enhanced "A Finding May Name Either Or Both Documents..." requirement with consumer details; added 4 new scenarios documenting `cmd_handoff` and `cmd_verify` behavior |
| `implementation-per-document-vocabulary` | Modified | Added two new requirements: "A Cross-Document Citation Leaf..." (5 scenarios) and "A Block Locator Is Required..." (3 scenarios) |
| `implementation-cli-seal` | Modified | Added three new requirements: "`compose`/`admit` Leave The Unsealed Set", "Every Digest That Moves When Locator Starts Matching", and "The Crossing Check's Refusals Are Added As Sealed Cases" |
| `experimental-implementation-skill` | Modified | Added three new requirements: "`SKILL.md` No Longer Lists `compose`/`admit`", "`SKILL.md` Carries A Tutor Bullet For Third Discrepancy Kind", and "`SKILL.md` Documents Flow B's Existing Path" |

## Mechanical Copy Verification

**Copy Method**: `cp -R` (shell-native, no model processing)  
**Verification**: `diff -r` (source vs. destination)  
**Result**: Empty diff (no differences detected) — PASS

All archived artifacts are byte-identical to source.

## Task Completion Audit

**Implementation Tasks**: 99 total  
**Task Status**: All 99 marked complete (0 unchecked) ✓  

**Note on Task Count Discrepancy** (documented in verify report WARNINGs):
- Proposal's frozen success criteria stated 78 tasks as authored count
- Design phase updated count to 100
- Final measured count: 99 (all checked and delivered)
- Discrepancy was caught and corrected in `5469c64` (verification report commit)

## Verify Report WARNINGs (Recorded at Final State)

Per the launch prompt, four WARNINGs were documented at verification time:

1. **Task Count Self-Correction**: `tasks.md` self-declared total was wrong twice (78 → 100); final count is 99, all checked. Completeness and count-accuracy are separate properties.

2. **Frozen Success Criteria Variance**: `proposal.md`'s frozen Success Criteria contain two items not literally true as worded:
   - No `proposal-implementation/` file was modified (authorized at design time, D9)
   - Not every new refusal code in the roster was explicitly authored (substituted by mutation proofs, authorized at M11)
   - Both were ruled and disclosed at design time, not silently violated — frozen checklist was simply never reconciled

3. **D1 Deviated from `strict_tdd`**: Commit `bc85ce9` is pure GREEN with no preceding dedicated RED for tasks 1.10/1.14/1.16. D2–D5 honored the contract.

4. **Boundary Proof Literal Criterion**: Of two "no-verdict" boundary proofs the proposal demands be mutation-proven, only **5.11 (Z11)** literally is; **3.11** is a construction-time absence assertion. The property holds; the literal criterion does not.

## Discoveries About This Change

The change discovered the following about itself:

- **Tasks 1.12/1.13 were never authored**: Substituted by Z2/Z3 real-subprocess mutation proofs (stronger evidence, different shape). Recorded as **substituted**, never as done.

- **Task 1.15's own claim was FALSE**: It claimed to add a test exercising `COMPOSE_AMBIGUOUS_DOCUMENT`; D5 found its own test was the first in the suite to fire it.

- **The refusal pin never moved from 116**: The design predicted 115 → 117 → 118 and was wrong three times. `COMPOSE_AMBIGUOUS_DOCUMENT` and `HANDOFF_DOCUMENT_UNREADABLE` are structurally unreachable from `GATING_COMMANDS` roots; classifying either **breaks the roster's reverse lock**.

- **M7 reversed a documented limitation**: `experimental-deliberation/SKILL.md`'s "the accept turn does not publish" diagnosis (dated 2026-09-08) blamed hardcoded `-r(\d+)\.md$` that is not in the file it named. The chain **publishes**; it is entirely profile-derived (`revisionPattern: "v"`).

- **A pre-existing bug was found by the seal**: `both-documents-citation` was wrongly classified `local`, moving three digests.

- **Nine inherited counts were measured false**: 52 → 44 → 46 scenarios; 78 → 100 → 99 tasks; 595 → 596 npm; 114 → 115 predicted → 116 pin.

## Operator's Structural Bar — Sister Skill Integrity

Per `proposal-deliberation/SKILL.md:301`, the final measured state:

- **`tests/seal/`**: 28 digests (29 keys), byte-identical across the entire change ✓
- **`.claude/skills/proposal-implementation/`**: Exactly 3 files (`impl_profile.py`, `SKILL.md`, `references/usage.md`), as required. No extra files. ✓
- **`.claude/skills/experimental-deliberation/SKILL.md`**: Exactly 1 file, prose-only, unchanged ✓
- **`.claude/skills/proposal-deliberation/`** (6 files): Byte-unchanged ✓
- **`.claude/skills/_core/deliberation/`** (56 files): Byte-unchanged ✓
- **`reference-experimental.ts`**: Byte-unchanged ✓

## Final Measured Bars

- `npm test`: **596/596** (unchanged) ✓
- Python Suite: **`Ran 3059`, `OK (skipped=6)`** — skipped count unmoved ✓
- `git diff --exit-code tests/seal/`: **0 (pass)** ✓
- `reachable_refusal_codes()`: **116** (unchanged) ✓
- `tests/experiments_seal/`: Exactly **4 movers** in the whole change, each cause named ✓

**Phase Line Counts**:
- D1: 1,080 lines
- D2: 702 lines
- D3: 574 lines
- D4: 197 lines
- D5: 884 lines
- **Total**: 3,437 lines (inside design's 2,750–4,350 floor) ✓

## Archive Contents Manifest

✓ `proposal.md` — SDD proposal for Slice D items 3 and 4  
✓ `design.md` — Five-phase design document  
✓ `tasks.md` — 99 implementation tasks (all complete, all checked)  
✓ `verify-report.md` — Verification report: PASS WITH WARNINGS  
✓ `specs/implementation-cross-document-agreement/spec.md` — Full spec (new)  
✓ `specs/implementation-block-locator/spec.md` — Full spec (new)  
✓ `specs/implementation-document-binding/spec.md` — Delta (merged)  
✓ `specs/implementation-per-document-vocabulary/spec.md` — Delta (merged)  
✓ `specs/implementation-cli-seal/spec.md` — Delta (merged)  
✓ `specs/experimental-implementation-skill/spec.md` — Delta (merged)  

## SDD Cycle Status

**Proposal**: ✓ Complete  
**Spec**: ✓ Complete  
**Design**: ✓ Complete  
**Apply**: ✓ Complete  
**Verify**: ✓ Complete (PASS WITH WARNINGS, operator-approved)  
**Archive**: ✓ Complete

The change has been fully planned, implemented, verified, and archived. All six operator requirements are now delivered. This is the tenth and final change in the Slice D chain.

