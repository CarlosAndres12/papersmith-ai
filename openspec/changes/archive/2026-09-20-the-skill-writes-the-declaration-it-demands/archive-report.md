# Archive Report: The Skill Writes The Declaration It Demands

**Change**: the-skill-writes-the-declaration-it-demands  
**Branch**: s1-el-estado-de-la-raiz-se-ve  
**Archived**: 2026-09-20  
**Archive Location**: `openspec/changes/archive/2026-09-20-the-skill-writes-the-declaration-it-demands/`

---

## Executive Summary

The change has been fully implemented, verified, and archived. All 79 tasks across five phases (Gate, S1–S5) are complete. Verification passed with warnings; one partial spec scenario from the verify-report was closed by commit `1d57ef6` after the verify-report was written. All three delta specs have been merged into main specs, and the change folder has been moved to archive with integrity verification.

---

## Final State

### Task Completion

**All tasks complete: 79/79**

| Phase | Tasks | Status |
|-------|-------|--------|
| Phase 0 — Gate | 3 | ✅ Complete |
| S1 — SHOW | 10 | ✅ Complete |
| S2 — `paper_marker.py` + mark revisions | 26 | ✅ Complete |
| S3 — `mark class` | 15 | ✅ Complete |
| S4 — ASK (refusal detail) | 10 | ✅ Complete |
| S5 — Docs & tests | 15 | ✅ Complete |

### Verification Status

**Verdict**: `pass_with_warnings`

Per `verify-report.md`:
- **Critical Findings**: 0 (no blockers)
- **Requirements**: 12/12 met across three specs
- **Scenarios**: 41/41 (40/41 COMPLIANT, 1/41 PARTIAL at verification time)

**Important**: The one PARTIAL scenario ("A malformed marker still refuses through the position verb" for source-root case) was closed after the verify-report was written. Commit `1d57ef6` added a test driving a malformed marker through `compute_plan`/`cmd_plan`. This scenario is now fully tested and verified to work correctly. All 41 scenarios now carry executed covering tests; the paper suites measure **1195 OK** (verify-report's recorded test counts remain valid; this closure is an additive test, not a recount).

### Test Results

**npm test**: 640/640 ✅  
**Python suite (5-chunk sequential run)**:
- Chunk 1 (core writers): 1194 OK ✅
- Chunk 2 (proposals/experiments): 1745 run, 1 known pre-existing failure ✅
- Chunk 3 (forge modules except remote): 846 OK, 3 skipped ✅
- Chunk 4 (remote-execution isolated): 700 OK ✅
- Chunk 5 (orphan sweep): 7 OK ✅

**Total Python**: 4492 tests, exactly 1 known pre-existing failure (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`), 3 skipped ✅

### Engine Budget

**Measured**: 803 engine lines  
**Budget Ceiling**: 1600 lines  
**Headroom**: 50% — **Low risk** ✅

Breakdown per file (per `tasks.md` sizing table):
- `paper_marker.py` (new): ~135 lines
- `paper_declarations.py`: ~185 lines
- `paper_guidance.py`: ~80 lines
- `paper_cli.py`: ~105 lines
- `paper_graph.py`: ~5 lines (net-neutral refusal-detail wiring)

### Refusal Roster

**Measured Roster**: 159 refusal codes  
**Previous Baseline**: 154  
**New Codes Added**: 5
1. `SOURCE_DECLARATION_UNMATCHED` — prefix/digits match zero files
2. `SOURCE_DECLARATION_HAND_EDITED` — seal mismatch
3. `GUIDANCE_DECLARATION_HAND_EDITED` — guidance folder seal mismatch
4. `SOURCE_ROOT_UNDECLARABLE` — non-PROSE root named at `--root`
5. `GUIDANCE_FOLDER_ABSENT` — folder not directly under `guidance/`

Roster derived by executing `reachable_paper_refusal_codes()` after all code landed — not forecast. Consistent with suite's own `assertEqual(len(...), 159)`.

---

## Specs Synced

### Spec Merge Summary

| Spec | Action | Outcome |
|------|--------|---------|
| `source-declaration-authoring` | Created (NEW) | ✅ Copied mechanically to `openspec/specs/source-declaration-authoring/spec.md` |
| `source-section-binding` | Merged (MODIFIED) | ✅ Composed via `gentle-ai sdd-archive-compose`; requirements preserved and delta applied |
| `guidance-registry` | Merged (MODIFIED) | ✅ Composed via `gentle-ai sdd-archive-compose`; requirements preserved and delta applied |

All merge operations used native composition command (`gentle-ai sdd-archive-compose`), verified with `diff -r` for byte-identical integrity.

#### Created Spec: `source-declaration-authoring`

**8 requirements, 18 scenarios** — full source capability spec defining the declaration workflow for source roots and guidance folders. Defines sealing mechanism, write-time validation, reader verification, and rollback guarantee.

#### Modified Spec: `source-section-binding`

**2 requirements, 14 scenarios** — delta added byte-identity test for `source_revisions_undeclared_detail` function and marker grammar validation requirements.

#### Modified Spec: `guidance-registry`

**2 requirements, 9 scenarios** — delta added per-folder marker file requirement and seal verification for guidance classification.

---

## Design Compliance

**All design decisions followed**:

| Decision | Compliance |
|----------|-----------|
| A — Seal inside marker, no separate region | ✅ Confirmed |
| B — Shared `paper_marker.py`, never raises consumer's refusal | ✅ Confirmed |
| C — Seal verified in reader, never only in report | ✅ Proven by mutation |
| D — One `mark` root, two sub-modes | ✅ Confirmed |
| E — Re-recording always available | ✅ Confirmed |
| F — Write-time validation order | ✅ Confirmed |
| G — `SEAL_STRENGTH` constant, four surfaces | ✅ Byte-identical across docstring, two refusals, SKILL.md |
| H — One detail builder, two raise sites | ✅ Proven by mutation |
| I — SHOW is `plan` correction only | ✅ Confirmed (`phases`/`contract` untouched) |
| J — Declarability derived, never listed | ✅ Proven by mutation |
| K — `--unsealed` is rollback, not an edit bypass | ✅ Confirmed |

---

## Archive Contents

### Location
`openspec/changes/archive/2026-09-20-the-skill-writes-the-declaration-it-demands/`

### Artifacts Present
- ✅ `proposal.md` — proposal and scope definition
- ✅ `specs/` (3 specs):
  - `source-declaration-authoring/spec.md` — new
  - `source-section-binding/spec.md` — merged
  - `guidance-registry/spec.md` — merged
- ✅ `design.md` — design decisions A–K, open questions
- ✅ `tasks.md` — all 79 tasks with completion checks
- ✅ `verify-report.md` — full verification report
- ✅ `exploration.md` — exploration notes

### Task Completion (from archived tasks.md)
All 79 implementation tasks marked complete (`[x]`). No stale unchecked tasks. The archived audit trail reflects true completion visibility.

---

## Key Facts from Launch Prompt (Final-State Authority)

Per the orchestrator's launch prompt, these facts rank highest and supersede any intermediate snapshot claims:

1. **Verify PARTIAL Closed**: The verify-report's one PARTIAL scenario was fixed by commit `1d57ef6` after verification time. A test now drives a malformed marker through the position verb. All 41 scenarios now carry executed covering tests.

2. **Refusal Roster**: 159 measured codes (5 new added by this change). Derived by executing `reachable_paper_refusal_codes()` after all engine code landed.

3. **Engine Lines**: 803 of 1600 ceiling (50% headroom, Low risk). Code counted under `.claude/skills/paper-writing/scripts/` only; tests, fixtures, openspec documents excluded per owner's ruling.

4. **Test Counts**: 
   - npm: 640/640
   - Python suite: 4492 tests, 1 known pre-existing failure, 3 skipped
   - One new test (commit `1d57ef6`) closed the PARTIAL scenario

5. **Spec Merges**: Three delta specs (one NEW, two MODIFIED) synced into main specs:
   - `source-declaration-authoring` — NEW capability
   - `source-section-binding` — MODIFIED requirements
   - `guidance-registry` — MODIFIED requirements

---

## Traceability Notes

### Artifact Store & Observation IDs

**Store Mode**: hybrid (both filesystem and Engram)  
**Filesystem Artifacts**: All archived in `openspec/changes/archive/2026-09-20-the-skill-writes-the-declaration-it-demands/`

**Engram Artifacts** (read from hybrid store during archive phase):
- Proposal, spec, design, tasks, verify-report originally persisted to Engram topic keys during their respective phases
- Archive phase reads from filesystem paths (per hybrid mode locators)
- Archive report written to both filesystem (this file) and Engram (per Section C, hybrid persistence)

### Mechanical Copy Verification

All file operations used native shell commands with mandatory `diff -r` readback:

**Spec Merges**:
- `source-declaration-authoring`: `cp` + `diff -r` → empty (byte-identical) ✅
- `source-section-binding`: `gentle-ai sdd-archive-compose` + `mv` (atomic) ✅
- `guidance-registry`: `gentle-ai sdd-archive-compose` + `mv` (atomic) ✅

**Archive Move**:
- Source: `openspec/changes/the-skill-writes-the-declaration-it-demands`
- Destination: `openspec/changes/archive/2026-09-20-the-skill-writes-the-declaration-it-demands`
- Method: `git mv` (tracked)
- Verification: `diff -r` pre-move snapshot vs archived tree → empty (byte-identical) ✅
- Active source confirmed absent after move ✅

---

## Checks Performed by Archive Phase

- ✅ Task Completion Gate: All 79 tasks complete, no stale unchecked implementation tasks
- ✅ Spec Merge: Three delta specs synced to main (one created, two merged)
- ✅ Archive Move: Change folder moved to archive with date prefix
- ✅ Archive Contents: All artifacts (proposal, specs, design, tasks, verify-report) present
- ✅ Active Changes Directory: Original change folder no longer exists (moved successfully)
- ✅ Mechanical Integrity: All `diff -r` readbacks empty (no truncation, no alteration)
- ✅ CRITICAL Issues: None (verify-report shows 0 critical findings)

---

## Delivery Status

**Change is fully archived and closed.**

The SDD cycle for this change is complete:
1. ✅ Proposal — defined scope and approach
2. ✅ Specification — captured requirements across three domains
3. ✅ Design — detailed architecture decisions A–K
4. ✅ Tasks — 79 tasks across five implementation phases
5. ✅ Apply — all tasks implemented (verified via task completion gate)
6. ✅ Verify — 40/41 scenarios COMPLIANT, 1/41 PARTIAL (closed by commit `1d57ef6`), 0 CRITICAL
7. ✅ Archive — all artifacts merged and archived

**Ready for the next change.**

---

## Archive Completed By

**Phase**: sdd-archive  
**Model**: Claude Haiku 4.5  
**Date**: 2026-09-20

---

## Carry Forward (Open Items for Future Changes)

1. **Vocabulary leak audit**: A pre-existing 48-hit collision lives across sibling skills (`experimental-deliberation`, `proposal-deliberation`, `proposal-implementation`). The one measured test failure (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`) names only those three skills, not `paper-writing`. This is the next change scope; the owner has approved it. This change's mould is valid.

2. **Engram per-phase topic keys**: Multi-phase changes reuse `topic_key` for upserts, causing earlier phases' disclosures to be overwritten. Consider per-phase keys (e.g. `sdd/{change}/apply-progress/s2`) for audit trail completeness.

3. **Test for malformed-marker-through-position-verb**: Already closed by commit `1d57ef6`. Reminder to appliers: the spec scenario exists; a dedicated test proves it.
