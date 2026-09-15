# Archive Report — experimental-deliberation-layer

**Change**: `experimental-deliberation-layer`  
**Archived**: 2026-09-08  
**Status**: COMPLETE  
**Observation IDs**: proposal #1519 | spec #1521 | design #1523 | tasks #1525 | verify-report #1539

## Change Summary

Generalized `.claude/skills/_core/deliberation/engine/` to support a SECOND domain layer alongside `proposal-deliberation`, without altering `proposal-deliberation` behaviour by a byte. The change introduces seven new first-class capabilities to the deliberation-core specification:

1. **deliberation-artifact-namespace** — profile-driven artifact path configuration, replacing 14 hardcoded sites + 3 TypeScript literal types
2. **deliberation-structural-entries** — new `table` and `figure_placeholder` as first-class entry types
3. **deliberation-preservation-gate** — domain-neutral preservation logic extracted from math-specific code, with permanent `mathDelta`/`acknowledgedMathRemovals` aliases
4. **deliberation-reference-integrity** — profile-configurable reference vocabulary replacing hardwired LaTeX syntax
5. **deliberation-required-sources** — profile-gated source requirements with explicit `REQUIRED_SOURCE_MISSING` refusal
6. **deliberation-change-header** — successor composite change header as profile-gated resolved locus (design resolution option b)
7. **deliberation-source-authority** — ceiling source validation with optional `acknowledgedSourceConflicts` field

**Scope**: 10 implementation changes in approved order 1→2→3→6→4→5→7→8→9→10, plus domain lock extension. Delivered in 4 chained slices, stacked-to-main.

**Non-scope** (explicitly excluded):
- The experimental-deliberation skill itself (follows as separate change)
- Changes to `proposal-deliberation`'s SKILL.md or published bytes
- A unified `verify` notion across domains
- Any stage/pipeline orchestration (engine governs NO sequence)

## Verification Status

**VERDICT**: PASS (per `sdd-verify`, independent re-run on 2026-09-07)

### Test Evidence
- **npm test**: 453 pass / 0 fail (40.9s). Baseline 386 + new 67 per slice (32+13+8+14 counted from spec files directly).
- **.venv/bin/python -m unittest discover -s tests**: Ran 2718, OK (skipped=6) (475.8s). Must use `.venv/bin/python`, never bare `python3` (3.9 incompatible).

### Requirements & Scenarios
- **18 requirements** across 7 new capabilities
- **36 scenarios** total; 34/36 directly executing passing tests; 2/36 (change-header resolutions a/c) correctly N/A per design.md choosing resolution (b)
- **Zero UNCOVERED requirements**

### Quality Gates Passed
- **No CRITICAL issues** in verification report
- **No vacuous passes**: every new guard paired with genuine fixture (GFM tables, `\tag{1}/(Ec.1)` pairs, macro references, value conflicts)
- **Byte-identity for proposal-deliberation**: `REQUIRED` array in profile excludes `changeHeader`/`sourceAuthority` (both optional); every consuming site gates correctly; profile declares neither → confirmed no-op by code path
- **Mutation proof**: 4 independent mutations (M2a, M2b, M4a, M4b) tested with before/after `rg -c` anchor counts + full suite re-run + explicit assertion text validation
- **Scope discipline**: `successor-composite-engine.ts` and `patch-compiler.ts` completely untouched; `COMPOSITE_UNTOUCHED_INVARIANT` unmodified/unexempted

### One WARNING (Self-Disclosed, Non-Blocking)
**tests/fixtures/proposal-deliberation-artifact-naming-types.ts** is imported by nothing. This is a branded-string type fixture used for IDE affordance and documentation; TypeScript is not invoked in this codebase (jiti strips types at runtime). Recommendation: delete-or-wire-tsc as fast-follow, not a blocker for this archive. See Follow-Up #1 below.

## Specs Synced

| Capability | Action | Details |
|-----------|--------|---------|
| deliberation-artifact-namespace | Created | New spec defining nested artifact profile contract |
| deliberation-structural-entries | Created | New spec for table/figure_placeholder entry types |
| deliberation-preservation-gate | Created | New spec extracting domain-neutral preservation logic |
| deliberation-reference-integrity | Created | New spec for profile-gated reference vocabulary |
| deliberation-required-sources | Created | New spec for source requirement gating |
| deliberation-change-header | Created | New spec for successor change-header feature (profile-gated) |
| deliberation-source-authority | Created | New spec for ceiling source validation |

**Location**: `openspec/specs/{capability}/spec.md` (7 new capability specs)

## Archive Contents

- ✅ proposal.md (22.6 KB) — scope, acceptance criteria, coupling analysis
- ✅ specs/ (7 new capability specs, organized by domain)
- ✅ design.md (21.6 KB) — technical design decisions, mutation procedures, corrected claims
- ✅ tasks.md (43.7 KB) — 104 implementation tasks, all [x] complete
- ✅ verify-report.md (15.0 KB) — full verification with test evidence and quality gate status
- ✅ exploration.md (22.6 KB) — discovery work identifying the three coupling families
- ✅ archive-report.md (this file)

**Source of Truth**: `openspec/specs/` now contains the canonical deliberation-core capabilities.

## Task Completion

**104 / 104 tasks marked [x]**  
Breakdown by slice:
- Slice 1 (artifact namespace): ~35 tasks ✓
- Slice 2 (structure + preservation): ~30 tasks ✓
- Slice 3 (references + sources): ~25 tasks ✓
- Slice 4 (new mechanics + cleanup): ~14 tasks ✓

Verified independently in verify-report by fixture inspection, not trusted blindly. Every completed task confirmed either by direct test pass or explicit N/A status per design decision.

## SDD Cycle Complete

All four phases complete:
1. **sdd-proposal** (2026-09-06): Scope, approach, rollback plan, acceptance criteria
2. **sdd-spec** (2026-09-06): Seven new capabilities, requirements, scenarios, inherited verification
3. **sdd-design** (2026-09-06): Technical decisions, mutation proofs, corrections to claims, design resolutions for open questions 8 and 9
4. **sdd-apply** (completed per working tree): Four chained slices, 55 files, 4356+/350− lines, commit e903512
5. **sdd-verify** (2026-09-07): PASS — test evidence, requirements/scenarios traceability, quality gates, scope discipline
6. **sdd-archive** (2026-09-08): Specs synced to `openspec/specs/`, change folder moved to archive, this report persisted

The change is ready for merge to main (user's decision, held separate per preflight).

## Key Follow-Ups (Carry Forward)

These are documented residue from this change that require follow-up work in future changes or session tickets:

### Follow-Up #1: No TypeScript Checker in Repository

**What**: No `tsc`, no `tsconfig.json`, no `typescript` in `node_modules`. TypeScript runs through jiti, which strips types without checking. The branded string types introduced by this change are IDE affordance and documentation, NOT runtime guards.

**Evidence**: tests/fixtures/proposal-deliberation-artifact-naming-types.ts (imported by nothing, never executed); warning raised in verify-report.

**Impact**: A type-only fixture was written and then deleted during implementation (see tasks.md task 1.2.2, marked WITHDRAWN). Introducing `tsc --noEmit` over ~11k never-checked lines is its own change and will likely surface pre-existing errors unrelated to this work.

**Recommendation**: Defer to product decision on whether to enable tsc. If yes, coordinate as separate SDD change to avoid blame-shifting.

### Follow-Up #2: Table Queries Cannot Be Singled Out by Lexical Query

**What**: A table is now its own entry but cannot be selected independently by a query naming only its column headers. `target-resolver.ts` builds its match text as `own + neighbours + headingPath`, so a query naming a table's own column headers ties the table with its section and both adjacent paragraphs. `ambiguityGate` then blocks.

**Evidence**: Measured with live probe during design phase. Pre-existing scorer behaviour, not a regression from this change.

**Impact**: The experimental-deliberation skill writes documents that are mostly tables, so it will meet this on its most common locus.

**Recommendation**: Document as known limitation. If future skills need table-specific queries, escalate to orchestrator for a separate scope task on `target-resolver.ts` query semantics.

### Follow-Up #3: Ambient-Composite `CREATE_SUCCESSOR` Never Injects Change Header

**What**: When `changeSummary` is supplied, the change header is not injected into the document body under resolution (a) or (c), or when `profile.changeHeader` is undeclared. This is a documented scope limitation.

**Scope**: This change implements resolution (b) only (header as own resolved locus). Resolutions (a) and (c) remain unimplemented and may require future work depending on product direction.

**Recommendation**: If product chooses (a) or (c) in a future phase, file explicit SDD change to implement the alternate resolution and coordinate with any affected domains.

### Follow-Up #4: Verify-Report Correction Banner Must Be Preserved

**What**: The verify-report.md opens with a correction banner: the initial verification run destroyed the tree it was certifying (a `git checkout --` revert of a mutation) and its PASS was void when written. The damage was repaired and all four mutation proofs were then re-run independently with `cp`-based reverts.

**Evidence**: verify-report.md preamble; section "GUARD THAT CANNOT FIRE: CONFIRMED finding (WARNING, already self-disclosed by apply phase)".

**Impact**: This is the most valuable finding in the file — it documents a process failure that could silently corrupt future verification cycles.

**Recommendation**: Preserve this banner through any future re-verification. Use it to inform process improvements (e.g., mutation scripts should NEVER use in-place reverts; always snapshot-and-restore).

## Traceability

All change artifacts recorded in Engram with observation IDs:
- sdd/experimental-deliberation-layer/proposal (#1519)
- sdd/experimental-deliberation-layer/spec (#1521)
- sdd/experimental-deliberation-layer/design (#1523)
- sdd/experimental-deliberation-layer/tasks (#1525)
- sdd/experimental-deliberation-layer/verify-report (#1539)
- sdd/experimental-deliberation-layer/archive-report (this report, persisted at phase close)

Archive persisted on 2026-09-08 to `openspec/changes/archive/2026-09-08-experimental-deliberation-layer/` following existing archive layout and file conventions.

---

**Archive Report**: Complete  
**Ready for**: Merge decision (user's choice, held separate per preflight)  
**Date**: 2026-09-08  
**Executor**: sdd-archive phase agent
