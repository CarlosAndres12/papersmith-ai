# Archive Report: Five Guards That Cannot Fire

**Change**: `five-guards-that-cannot-fire`
**Branch**: `experimental-deliberation` (HEAD `9233c50`)
**Archived To**: `openspec/changes/archive/2026-09-09-five-guards-that-cannot-fire/`
**Archive Date**: 2026-09-09
**Status**: ARCHIVED (PASS WITH WARNINGS)

## Artifact Traceability

All artifacts retrieved from hybrid storage (OpenSpec files + Engram observations):

| Artifact | Source | Observation ID | Retrieved |
|----------|--------|-----------------|-----------|
| Proposal | Engram + OpenSpec | #1573 | 2026-09-09 12:XX:XX |
| Specification | Engram + OpenSpec | #1574 | 2026-09-09 12:XX:XX |
| Design | Engram + OpenSpec | #1575 | 2026-09-09 12:XX:XX |
| Tasks | Engram + OpenSpec | #1576 | 2026-09-09 12:XX:XX |
| Verification Report | Engram + OpenSpec | #1579 | 2026-09-09 12:XX:XX |

## Specs Synced

| Domain | Action | Status | Details |
|--------|--------|--------|---------|
| `deliberation-guard-integrity` | Created | ✅ | New domain spec copied from delta. 6 requirements, 7 scenarios. Zero main spec existed previously. |

**Merge Summary**:
- Source: `openspec/changes/five-guards-that-cannot-fire/specs/deliberation-guard-integrity/spec.md`
- Target: `openspec/specs/deliberation-guard-integrity/spec.md`
- Verification: Mechanical copy via shell (`cp`), verified with `diff -r` — byte-identical

## Archive Contents

**Change folder moved to**: `openspec/changes/archive/2026-09-09-five-guards-that-cannot-fire/`

Files archived:
- ✅ `proposal.md` — SDD proposal, scope, approach
- ✅ `specs/deliberation-guard-integrity/spec.md` — 6 requirements, 7 scenarios
- ✅ `design.md` — Technical design, 6 decisions (A1–A6), measured findings
- ✅ `tasks.md` — All 23 tasks marked complete ([x])
- ✅ `verify-report.md` — Verification report, PASS WITH WARNINGS

**Task Completion Gate**: PASS
- 23 tasks marked [x], 0 tasks marked [ ]
- Per verify-report (Engram #1579): All requirements and scenarios verified independently

## Verification Summary (Per #1579)

**Verdict**: PASS WITH WARNINGS
- Requirements: 6/6 compliant
- Scenarios: 7/7 compliant (spec measured to have 7, not 8 as initially handed down)
- Critical Issues: 0
- Warnings: 1 (scenario count mismatch in initial handoff — now corrected via re-measure)
- Suggestions: 1 (informational; adapter-throw site explicitly out of scope)

**Key Verification Evidence** (independently re-measured per sdd-verify protocol):
- All 4 mutations (G1, G1b, G1c, G3) reproduced from scratch and verified to move assertions from pass to fail, then restored with byte-identity confirmation
- G3 critically required `rg -c -o` (occurrence count) not `rg -c` (line count) — plain `rg -c` reads 4→4 while occurrences actually go 6→5
- All 3 baselines independently re-run: `npm run typecheck` 0 errors, `npm test` 559/559, `.venv/bin/python -m unittest discover` 2782 OK (skipped=6)
- Byte-frozen files (`successor-composite-engine.ts`, `patch-compiler.ts`) confirmed empty diff
- Residue pins (EQUATION_RESIDUE=124, PROPOSAL_RESIDUE=192) unchanged; domain-profile-lock 12/12 passing

## Scope Resolution

### Delivered (3 defects closed)

1. **D1 — Smoke Stub Vocabulary + REVIEW Turn**
   - Fixed tutor stub to answer `'ACCEPT'` (valid member of `tutorDecisions`)
   - Fixed reviewer stub to answer `'APPROVE'` (valid member of `reviewerDecisions`)
   - Added REVIEW turn to smoke; both assertions now fire
   - Result: `npm run typecheck` 2→0 errors
   - Guard: G1, G1b, G1c (all fired; mutations shown to move assertions to fail)
   - Secondary fix: stale entry-id refetch in smoke-runner.ts (pre-existing ambiguity bug resolved)

2. **D5 — Guard Blocked Return plannerCalls Divergence**
   - New test `proposal-deliberation-blocked-return-counts.test.mjs` asserting `plannerCalls===1, modelCalls===2` on CANDIDATE_VALIDATION_FAILED return
   - Test covers diverging turn (tutor present, planner validation failure)
   - Guard: G3 (one occurrence of `plannerCalls:planned.plannerCalls` → `planned.modelCalls` at CANDIDATE_VALIDATION_FAILED site)
   - Result: New test passes; unmodified HEAD orchestrator.ts already contains the fix
   - Caveat: other 4 `publish()` blocked returns remain unguarded by design (reachability analysis in design.md)

3. **D2 — CLOSE_DELIBERATION Unreachable Throw Documentation**
   - Added 11-line comment above `if(params.operation==='CLOSE_DELIBERATION')` in proposal-workspace.ts
   - Comment explains why `resolveEffectiveOperationProfile`'s excluded-intent throw is unreachable here
   - Unguarded by design (A5): no test asserts comment text; behavioral guard remains `BudgetedIntent` + passing `status==='not_open'` assertions
   - Result: Specification requirement met via documentation only

### Out of Scope (Deferred, Raised Not Absorbed)

- **D3** — Single-term lexical tie (ambiguity gate with score margin <4). Rescaling `OWN_TERM` weight would require re-baseline of entire confidence distribution. Deferred.
- **D4** — Artifact marker literal in three files (only `draft-materialization.ts` half raised). `patch-compiler.ts` and `revision-lifecycle-store.ts` halves kept under edit authority restriction. Deferred.

## Key Findings Carried Forward

The following observations should be recorded so they do not die with this change:

1. **Entry IDs invalidate broadly**: Document-index.ts builds `sha256(parentType : ordinal : sha256(text))`. The ordinal is a document-wide paragraph position, so entry ID becomes invalid whenever ANY earlier paragraph is inserted/deleted/moved, not just when that entry's own text changes. Verification traced every captured ID in smoke-runner.ts against this fuller model and found only one pre-existing instance (gamma before DELIBERATE).

2. **Mutation occurrence anchors must be counted by occurrence, not by line**: Guard G3 has 6 occurrences on 4 lines. Plain `rg -c` reports 4→4 (misleading). Only `rg -c -o` correctly shows 6→5. Every mutation anchor in this repository must be measured by occurrence count, never line count.

3. **Entry IDs embed document-wide structural decisions**: A content-mutating turn that reorders paragraphs (e.g., "revisión conceptual") will invalidate IDs of untouched paragraphs that shift position. The stale-entry-id bug in the pre-fix smoke (gamma becoming ambiguous after conceptual-revision rewrites) was pre-existing and independent of the stub-vocabulary defect — both were true independently.

4. **Four blocked-return guards remain unguardable by design**: NO_MUTATION_PLAN (always 0/0), SOURCE_AUTHORITY_CONFLICT-refuse (unreachable under npm test profile), and two other sites are constrained such that no test can distinguish correct assignment from copy-pasted value. These are recorded as unguarded by design, not as oversights.

5. **Domain-profile lock pins embedding**: EQUATION_RESIDUE (124 `equation` substrings) and PROPOSAL_RESIDUE (192 `\bproposal\b` words) are checked by `proposal-deliberation-domain-profile-lock.test.mjs`. Production and documentation edits must stay inside these counts. This is an established decision: raise constraints, never re-baseline to fit new content.

6. **Scenario count was re-measured**: Initial handoff claimed 8 scenarios; verification re-measured via `rg -c '^#### Scenario:'` and found 7. This mismatch was corrected in the verification report and is now recorded as a WARNING (documentation-accuracy issue, not a code defect).

## Follow-Ups (Out of This Change's Scope)

Beyond this archive:

1. **Merge to main** — The user will decide. This branch (experimental-deliberation) is currently 9 commits ahead of main; merge is deliberately not performed by the archive phase.

2. **Experimental skill's required sources** — The experimental skill cannot yet be used because its required sources are absent from disk. This requires material from the user, not a fix within the codebase.

3. **SDD artifacts from earlier delegated-direct stretch** — One earlier delegated-direct stretch is missing its SDD artifacts. These are out of scope for this archive but should be recorded in future work.

4. **D3 and D4 deferred work** — Both are raised (noted as constraints), never absorbed. Future work may address these if the profile weight balance or edit-authority scope change.

## Mechanical Operations Verification

✅ **Spec merge**: Source spec copied to `openspec/specs/deliberation-guard-integrity/spec.md`
  - Diff check: byte-identical (empty diff output)

✅ **Archive move**: Change folder moved to `openspec/changes/archive/2026-09-09-five-guards-that-cannot-fire/`
  - Source no longer exists in `openspec/changes/`
  - Diff check: byte-identical to pre-move snapshot (empty diff output, excluding archive-report.md)

✅ **Task Completion Gate**: All 23 implementation tasks marked [x], zero unchecked

✅ **Native Review Receipt Gate**: No review was discovered for this candidate (kill switch off); archive proceeds under ordinary repository policy

## SDD Cycle Complete

This change has been:
- ✅ Planned (proposal, specification, design, tasks)
- ✅ Implemented (3 defects closed, 1 secondary fix, 1 unguarded documentation edit)
- ✅ Verified (PASS WITH WARNINGS; 0 CRITICAL, 1 WARNING, 1 SUGGESTION)
- ✅ Archived (specs merged, change folder moved with date prefix, all artifacts preserved)

Ready for the next change.

---

**Archive Created**: 2026-09-09
**Executed By**: sdd-archive executor
**Mode**: hybrid (OpenSpec files + Engram observations)
