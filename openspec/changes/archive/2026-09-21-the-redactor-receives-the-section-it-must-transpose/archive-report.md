# Archive Report: the-redactor-receives-the-section-it-must-transpose

**Date Archived**: 2026-09-21  
**Change Name**: the-redactor-receives-the-section-it-must-transpose  
**Artifact Store Mode**: hybrid  
**Final Verdict**: PASS

## Executive Summary

This change has been successfully planned, implemented, verified, and archived. All 38 tasks were completed in strict TDD discipline (RED → GREEN → REFACTOR). Both delta specs (`redactor-packet` and `evidence-bound-drafting`) were merged into their respective canonical specs via native composition. Full test suites (4518 Python tests, 646 npm tests) passed with zero failures. Zero new refusal codes were introduced. The change is fully archived and ready for delivery.

## Change Scope

**Domains Modified**:
- `redactor-packet`: Implemented packet source section resolution and guidance receipt mechanism
- `evidence-bound-drafting`: Extended evidence binding to include draft guidance navigation

**Specs Composition**: Both delta specs composed successfully into canonical specs using `gentle-ai sdd-archive-compose`:
- `openspec/specs/redactor-packet/spec.md` — 6352 bytes (merged)
- `openspec/specs/evidence-bound-drafting/spec.md` — 9453 bytes (merged)

## Task Completion

- **Total Tasks**: 38
- **Completed**: 38 (100%)
- **Incomplete**: 0
- **Status**: All implementation tasks ticked, independently cross-checked against running code

Per Task Completion Gate (SKILL.md §79): **PASS** — no unchecked implementation tasks remain in the persisted artifact.

## Verification Summary

Per `verify-report.md`, dated 2026-09-21:

### Builds & Tests
- **Python test suite** (`.venv/bin/python -m unittest discover`): **4518 tests PASS** (0 failures, 3 skipped)
- **npm test** (full build gate): **646/646 tests PASS** (0 failures)
- **Test time**: 662.4s (Python), 34.1s (npm), independent runs in verify session confirm no regressions

### Specifications
- **Requirement coverage**: 2/2 required specs implemented
- **Scenario coverage**: 11/11 scenarios covered by passing tests
- **Spec composition**: Both deltas composed cleanly, zero requirements lost or dropped

### Code Quality
- **Refusal code roster**: 161 (measured live, unchanged — zero new refusal codes)
- **Engine diff**: 163 insertions + 14 deletions = 177 lines against a 1600-line ceiling (Low risk)
- **File changes**: Zero deletions, `sections/` byte-identical to main, only implementation code touched
- **Generality scan**: ForgeVocabularyDerivedGuardTests 22/22 pass; no lineage pollution from prior work

### Coherence (Design Decisions Followed)
- D1: Missing/unreadable paper root handled as named state, never as refusal ✅
- D2: Corpus assembled only for transposition, never twice ✅
- D3: `source_sections` appended as fifth field, properly defaulted ✅
- D4: Fifth input mirrors `BlockContract.source_sections` exactly ✅
- D5: Only transposition resolves sections; argument mode gets not-applicable ✅
- D6: `SOURCE_RUN_BACKSTOP=16` unchanged; falsifier passes ✅

**Result**: PASS

## Spec Merges (Mechanical)

### Evidence-Bound-Drafting
**Delta source**: `openspec/changes/the-redactor-receives-the-section-it-must-transpose/specs/evidence-bound-drafting/spec.md`  
**Canonical target**: `openspec/specs/evidence-bound-drafting/spec.md`  
**Action**: Merge via native `sdd-archive-compose`  
**Status**: ✅ Succeeded (1712-byte delta composition)  
**Verbatim diff**: (empty — byte-identical verification passed)

### Redactor-Packet
**Delta source**: `openspec/changes/the-redactor-receives-the-section-it-must-transpose/specs/redactor-packet/spec.md`  
**Canonical target**: `openspec/specs/redactor-packet/spec.md`  
**Action**: Merge via native `sdd-archive-compose`  
**Status**: ✅ Succeeded (2843-byte delta composition)  
**Verbatim diff**: (empty — byte-identical verification passed)

Both compositions applied RENAMED requirements before MODIFIED, preserving all unmentioned requirements byte-for-byte.

## Archive Move (Mechanical)

**Source**: `openspec/changes/the-redactor-receives-the-section-it-must-transpose`  
**Destination**: `openspec/changes/archive/2026-09-21-the-redactor-receives-the-section-it-must-transpose`  
**Method**: git mv (tracked entry)  
**Status**: ✅ Succeeded  
**Verbatim diff readback**: (empty — byte-identical verification passed)

All artifacts preserved:
- `proposal.md` ✅
- `design.md` ✅
- `tasks.md` (38/38 tasks ticked) ✅
- `apply-progress.md` ✅
- `exploration.md` ✅
- `verify-report.md` ✅
- `specs/redactor-packet/spec.md` ✅
- `specs/evidence-bound-drafting/spec.md` ✅

## Critical Observations for Future Work

### 1. Pre-Existing Latent Defect: `paper_contract.resolve_section_path` Scan Order

**Finding** (out-of-scope suggestion from verify-report):  
`paper_contract.resolve_section_path` (lines 768–798, NOT modified by this change) globs `sections_dir.glob("*.md")` in sorted order and iterates EVERY file until finding the target section's header. If a corrupted sibling file sorts alphabetically BEFORE an unrelated target, the lookup raises `MALFORMED_HEADER` for work unrelated to the corruption.

**Impact**: Broader than this change's documented blast radius (D category). Affects `assemble_packet` for ALL block modes (not just transposition), and also blocks `write` and `place` operations through unrelated corrupted siblings.

**Evidence**: Direct reproduction with synthetic minimal fixture (two files, no reused test corpus). Confirmed output: `Refused MALFORMED_HEADER invalid JSON in header...`.

**Mitigation in this change**: `PacketCorpusContaminationTests::test_the_same_corrupted_sibling_does_not_block_an_argument_mode_packet` sidesteps the hazard by name-ordering its fixture (`00-c` before `02-b`) with an explicit comment. This is correct for this change's scope but does not fix the underlying defect.

**Recommendation**: Follow-up change scoped to `resolve_section_path` alone. Options: catch-and-skip malformed siblings, or resolve by filename-declared `section` field first and fall back to scan only if needed.

**Blocker Status**: No — `paper_contract.py` is explicitly read-only per design.md File Changes table. This change introduces neither the defect nor a new path reaching it beyond what already existed.

---

### 2. Archive-Time Defect: Delta RENAME Specification Requirement

**Finding**: During orchestrator's pre-archive dry-run, the `redactor-packet` delta initially failed composition because a renamed requirement was declared under the NEW heading in a MODIFIED section, but the delta had no `## RENAMED Requirements` section.

**Root Cause**: The composer matches MODIFIED blocks against canonical requirement names using the heading text. A requirement that is RENAMED must be explicitly declared in the delta's `## RENAMED Requirements` section with:
```
### Requirement: {Old} → {New}
(Reason: ...)
(Migration: ...)
```

When RENAMED is present, the composer applies it BEFORE MODIFIED, so a same-change MODIFIED block under the new name now resolves correctly.

**Fix Applied**: Orchestrator added the `## RENAMED Requirements` section per `~/.claude/skills/sdd-spec/SKILL.md:163-168`. Both compositions then succeeded cleanly.

**Lesson for Future Archives**: Every delta that renames a requirement MUST declare the rename with `(Reason: ...)` and `(Migration: ...)` notes. The composer's strict ordering (RENAMED → MODIFIED → REMOVED → ADDED) ensures that rename-then-modify patterns compose correctly. Verify does NOT exercise spec composition, so a stale delta can pass verify and still fail archive if the RENAMED section is missing.

---

### 3. Hard Ordering Seam: Sibling Change Dependency

**Sibling Change**: `the-block-asserts-only-what-its-section-carries`  
**Applies**: SECOND (after this change is delivered)  
**Blocking Gate**: Task 0.1 in the sibling change's task list re-measures `RedactorInput`'s field count and `assemble_packet`'s signature on disk

**Certificate**: This change satisfies that gate:
- `RedactorInput` (`paper_bindings.py:45-55`) has exactly 5 fields (confirmed by test `RedactorInputContractTests::test_the_shape_carries_exactly_five_fields` and direct source read)
- `assemble_packet` signature is `(sections_dir, guidance_dir, ...)` with corpus and paper_dir params (confirmed by source read `paper_cli.py:2147-2232` and test coverage)

The sibling change's gating assertion will find these values as measured.

---

### 4. Key Implementation Detail: Corpus Reuse and Heading Text

**From verify-report Key Learning #2** (independently confirmed):
- `resolve_bound_sections` returns markdown text that INCLUDES the heading line itself (regex match starts at the `#` character)
- `cmd_write` calls `resolve_bound_sections` twice against the SAME corpus object (once inside `assemble_packet`'s gate, once directly for `BlockContract.source_sections`) — this is read-only reuse, not re-assembly
- Test `PacketCorpusReuseTests::test_cmd_write_resolves_source_sections_consistently_with_assemble_packet` spies on both calls and confirms corpus object identity (`id()` equality)

**Implication for future work**: Any code that calls `resolve_bound_sections` should expect the heading line in the returned text, and should not assume corpus re-assembly when the same corpus object is used multiple times.

## Artifact Persistence

**Hybrid Mode**: Both filesystem and Engram persistence

### OpenSpec (Filesystem)
- Archive folder: `openspec/changes/archive/2026-09-21-the-redactor-receives-the-section-it-must-transpose/`
- Canonical spec updates:
  - `openspec/specs/redactor-packet/spec.md` (merged, verified with byte-identical diff)
  - `openspec/specs/evidence-bound-drafting/spec.md` (merged, verified with byte-identical diff)

### Engram (Topic Key)
- Observation ID for archive report: `sdd/the-redactor-receives-the-section-it-must-transpose/archive-report`
- Type: `architecture`
- Upsert: true (updates any prior snapshot)

## Final Checklist (Per SKILL.md §309-323)

**Task Completion Gate** (§79):
- [x] No unchecked implementation tasks in `tasks.md`
- [x] All 38 tasks ticked and independently verified

**Spec Merge** (§124-168):
- [x] Both canonical specs exist
- [x] Native `sdd-archive-compose` used (never Read/Edit)
- [x] Both compositions succeeded (zero exit)
- [x] Atomic mv applied after successful composition

**Archive Move** (§210-280):
- [x] Snapshot created before move
- [x] git mv attempted first (succeeded)
- [x] Fallback mv not needed
- [x] Source removed after move
- [x] Verbatim diff readback passed (empty output = pass)

**Artifact Verification** (§309-323, openspec/hybrid):
- [x] Main specs updated correctly
- [x] Change folder moved to archive
- [x] Archive contains all artifacts (proposal, specs, design, tasks, apply-progress, explore, verify-report)
- [x] Archived `tasks.md` has no unchecked implementation tasks
- [x] Active changes directory no longer has this change
- [x] Verbatim `diff -r` output is empty (no differences)

**Persistence** (§325-329):
- [x] Archive report written to filesystem (this file)
- [x] Archive report saved to Engram (via mem_save)

## Delivery State

**Status**: ✅ ARCHIVED  
**Ready for**: Ordinary repository policy (commit, push, merge) — SDD cycle complete

This archive closes the cycle. The change has been fully planned (proposal), specified (spec), designed (design), implemented (apply, 38 tasks), verified (verify, PASS), and archived (this report). No follow-up SDD phases are needed.

The orchestrator will now handle commit, PR, and merge decisions under ordinary repository policy.

---

**Archive closed**: 2026-09-21 03:44 UTC  
**Archived by**: sdd-archive executor (Claude Haiku 4.5)
