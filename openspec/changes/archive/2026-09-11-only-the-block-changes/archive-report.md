# Archive Report: only-the-block-changes

**Archived**: 2026-09-11
**Artifact store mode**: hybrid (filesystem canonical, Engram mirrored)
**Sequence position**: 1 of 7 (`only-the-block-changes` archives first; two siblings later merge deltas into `block-substitution`)

## Sources Read (traceability)

| Artifact | Engram observation ID | Filesystem path (canonical) |
|---|---|---|
| proposal | #1600 | `openspec/changes/only-the-block-changes/proposal.md` (now archived) |
| spec | #1603 | `openspec/changes/only-the-block-changes/specs/{paper-scaffold,block-substitution}/spec.md` (now archived) |
| design | #1604 | `openspec/changes/only-the-block-changes/design.md` (now archived) |
| tasks | #1606 | `openspec/changes/only-the-block-changes/tasks.md` (now archived) |
| verify-report | #1649 | `openspec/changes/only-the-block-changes/verify-report.md` (now archived) |

## Final-State Authority Applied

The launch prompt supplied one explicit final-state fact that outranks the verify-report snapshot: the orchestrator closed this change's documented spec debt at commit `20b3e0c` (2026-09-11), adding the eight refusal codes that shipped, were tested, and were classified but were missing from `specs/block-substitution/spec.md`'s Refusal Roster table at verify time — `BLOCK_ID_MALFORMED`, `OPEN_POSITION_REQUIRED`, `OPEN_POSITION_CONFLICT`, `SUBSTITUTE_MODE_REQUIRED`, `ADOPT_BODY_CONFLICT`, `NOTHING_TO_ADOPT`, `SUBSTITUTION_NOT_LOCAL`, `TEX_MOVED`.

- `verify-report` (#1649, written 2026-09-11 00:16, before the correction) records this as an open WARNING: "specs/block-substitution/spec.md's Refusal Roster table lists only 12 codes; 8 more ... are missing." That claim was true at verify time and is stale now.
- Verified directly against the delta spec on disk before merge: all 8 codes are present in the Refusal Roster table (`specs/block-substitution/spec.md` lines 212-219, invocation-defect/work-state classified), confirmed by `rg` against the tracked file and by `git show 20b3e0c --stat` showing the 8-line addition to that exact file.
- The merged main spec (`openspec/specs/block-substitution/spec.md`) carries the corrected 20-row roster (12 original + 8 added), not the 12-row table verify-report described.

No other contradictions between sources were found. No unrankable contradiction exists.

## Native Review Receipt Gate

No `reviewGate` key was present in any structured status supplied for this candidate, and no `sdd/only-the-block-changes/review/*` topics exist in Engram. Per the gate contract this is the ordinary-policy case (kill switch off or never started for this candidate) — archive proceeds without a review receipt requirement.

## Task Completion Gate

Inspected `openspec/changes/only-the-block-changes/tasks.md` before any merge or move: 28/28 items checked (`- [x]`), 0 unchecked (`- [ ]`) — confirmed by direct `rg` count on the tracked file. Matches verify-report's "28/28 tasks.md items [x] across Phases 1-7." No reconciliation needed.

## Verify Status

PASS WITH WARNINGS (#1649). 0 blockers, 0 CRITICAL findings, 17/17 requirements, 28/28 scenarios. Two WARNINGs recorded at verify time:
1. Refusal Roster gap — RESOLVED post-verify at `20b3e0c` (see Final-State Authority above).
2. Transient `test_skill_audit.py` failure on first full-suite run, confirmed non-reproducible on immediate re-run, unrelated to this change's scope — informational only, no action required.

No CRITICAL issues existed at any point; nothing blocked archive.

## Specs Synced

Neither `block-substitution` nor `paper-scaffold` existed under `openspec/specs/` before this archive (only `deliberation-*` capabilities were present). Both delta specs ARE full specs (first capability version), so both were mechanically copied — never Read→Write — via `cp` + `diff -r` + `mv`, per the Mechanical Copy Contract.

| Domain | Action | Details |
|---|---|---|
| `block-substitution` | Created | New capability. 20 requirements incl. Refusal Roster (20 codes, corrected per 20b3e0c). |
| `paper-scaffold` | Created | New capability. 5 requirements. |

**Left open for absorption**: `block-substitution` is the shared capability across this change and two later siblings (`the-paper-carries-its-own-decisions`, then `the-couplings-hold-or-they-do-not`, in that order). This main spec is left as a plain, non-final requirements document — no closing/freeze language was added — so each sibling's delta can append/modify/rename requirements using the standard delta merge procedure without needing to first undo a false "final" framing.

## Mechanical Copy Verification (MANDATORY, verbatim)

### Step 2 — spec sync to `openspec/specs/`

```
diff block-substitution (should be empty):
diff paper-scaffold (should be empty):
--- final diff readback vs source ---
ALL DIFFS EMPTY (mechanical copy verified)
```

### Step 3 — archive folder move

```
--- diff -r snapshot vs archived (should be empty) ---
DIFF EMPTY — move verified byte-identical
```

Both diffs are empty (no output between the labeled lines above), which is the only passing evidence per the Mechanical Copy Contract. This `archive-report.md` file itself is additive to the archived folder and was correctly excluded from both comparisons (it did not exist in the pre-move snapshot).

## Archive Contents

- `proposal.md` ✅
- `specs/paper-scaffold/spec.md` ✅
- `specs/block-substitution/spec.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (28/28 tasks complete)
- `verify-report.md` ✅
- `archive-report.md` ✅ (this file, additive)

## Source of Truth Updated

- `openspec/specs/block-substitution/spec.md` (created)
- `openspec/specs/paper-scaffold/spec.md` (created)

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived. Archived to `openspec/changes/archive/2026-09-11-only-the-block-changes/`.
