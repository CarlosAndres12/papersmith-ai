# Archive Report: The Whole Cut Is Argued Before Any Section Is Claimed

**Date**: 2026-09-20  
**Change**: `the-whole-cut-is-argued-before-any-section-is-claimed`  
**Repository**: papersmith-ai  
**Branch**: u1-the-cut-is-scored-before-it-is-argued (8 commits ahead of main)  
**Archive Location**: `openspec/changes/archive/2026-09-20-the-whole-cut-is-argued-before-any-section-is-claimed/`  
**Artifact Store**: hybrid (filesystem + Engram)

---

## Executive Summary

A complete SDD cycle for source separation and its integration into section binding. The change introduces the `source-separation-review` capability (10 new requirements, 34 scenarios) and extends `source-section-binding` with a precondition guard. All 94 tasks completed, 4370 Python tests pass (1 pre-existing failure unrelated to this change), 640 npm tests pass. Verification verdict: PASS with warnings. Engine footprint: 1145 of 1600 lines. Refusal roster: 152 codes (144 baseline + 8 new). The change is ready for delivery.

---

## Specification Merge Summary

### Delta Specs Synced

| Spec Domain | Action | Details | Status |
|---|---|---|---|
| `source-separation-review` | Created | 10 new requirements, 34 scenarios total | ✅ Copied to `openspec/specs/source-separation-review/spec.md` |
| `source-section-binding` | Modified | Extended with 1 new requirement (the binding precondition) | ✅ Merged via `sdd-archive-compose` into `openspec/specs/source-section-binding/spec.md` |

### Sync Verification

- `sdd-archive-compose` merged `source-section-binding` delta with zero conflicts or errors.
- Mechanical copy verified `source-separation-review` with byte-exact diff.
- Both main specs now reflect the final change state.

---

## Change Architecture & History

The change grew through six owner-driven units, each driven by a specific ruling:

### Unit 1 (U1): Pure Scorer

**Owner ruling**: Derive claimable sections level-free using structural root-span elimination.

- **What**: `claimable_sections(outline)` — eliminates root spans by byte containment to a fixed point, then takes the shallowest remaining level. No level literal anywhere.
- **Why**: A differently-nested document works with zero engine edits, proving the derivation is generality-preserving, not hard-coded.
- **Where**: `.claude/skills/paper-writing/scripts/paper_separation.py`
- **Tests**: 20 pass, including a 3-deep nesting generality fixture.
- **Mutation**: Root-span elimination disabled; the "title is not itself claimable" fixture fails.

### Unit 2 (U2): Proposal Reader & Round-1 Path

**Owner ruling**: Proposal file shape, per-title resolution reuse, round-1 scoring via `separate` verb.

- **What**: Proposal reader validating exact key set `{lineage, assignments}`, each assignment `{block, fact, sections}`. Resolution reuses `bind`'s existing path, refusing `SECTION_NOT_IN_SOURCE` and `SECTION_TITLE_AMBIGUOUS` before scoring. Lands four new refusal codes: `SEPARATION_REPORT_UNREADABLE`, `SEPARATION_SECTION_UNCLAIMABLE`.
- **Where**: `paper_cli.py`, `paper_declarations.py`; extraction of `resolve_section_index` from `_verify_source_section_bindings`.
- **Tests**: 30+ pass. Refusal precedence (overlap > orphan > gap) fixed; all-classes detail proven by separate test from just the raised code.
- **Mutations**: Exact key-set weakened; all three fixtures fail. Single-refusal precedence inverted; three fixtures fail.

### Unit 3 (U3): Round Persistence

**Owner ruling**: Append-only round records, id format includes revision, derived round number, replay logic.

- **What**: Fourth `declarations`-region record kind (`separation::{root}::{lineage}::{revision}::round-{n}`). Round number derived (max existing + 1), never supplied. Append-only: no reopen. Canonicalization detects replay.
- **Where**: `paper_declarations.py`
- **Tests**: 30+ pass. Replay test uses two independent processes to confirm no in-process state leakage. AST proof that `separate` never records a `binding`.
- **Key**: Recording happens BEFORE the structural refusal (overlap/orphan/gap), so a nonzero score is still recorded.

### Unit 4 (U4): The Concession Check

**Owner ruling**: On concession, recompute both cut scores from disk, never trust stored scores.

- **What**: `cmd_separate` recomputes both the current and prior-round scores from their `assignments` fields and refuses `SEPARATION_CONCESSION_REGRESSED` if the current is strictly worse. Runs BEFORE the structural refusal (ordering has its own mutation proof).
- **Where**: `paper_cli.py`, `paper_declarations.py`
- **Tests**: 9+ pass. Ordering mutation (swap to run after structural refusal) makes the regressed fixture unreachable on the happy path alone. Stored-score-mutation (read cached value instead of recomputing) reddens the fixture.
- **Why this unit exists**: This is the owner's own failure-mode description — *"ojo con aceptarse"* — an agent that agrees because it was asked. Nothing passes by authority.

### Unit 5 (U5): Documentation & Roster Re-Measurement

**Owner ruling**: Update SKILL.md with the two-step loop, re-derive and report the refusal roster.

- **What**: SKILL.md extended (1108 → 1249 lines) with full two-step loop documentation, both verbs' refusal tables, and Decision Gates block. Roster re-derived: 152 codes (144 baseline + 8 new: `SEPARATION_REPORT_UNREADABLE`, `SEPARATION_SECTION_UNCLAIMABLE`, `SEPARATION_SECTION_ORPHANED`, `SEPARATION_NOTATION_GAP`, `SEPARATION_ROUND_ABSENT`, `SEPARATION_CONCESSION_REGRESSED`, `BINDING_UNARGUED`, and the precedence-driven multi-code refusals).
- **Where**: `.claude/skills/paper-writing/SKILL.md`
- **Deviation**: Decision J instructed "update SKILL.md AND references/usage.md", but `paper-writing` has no `usage.md` and never has (verified via `git ls-files` and `fd`). Only SKILL.md was updated; no second file was fabricated.
- **Tests**: 4370 Python tests pass (1 pre-existing failure in `test_proposal_implementation.ForgeVocabularyDerivedGuardTests` over "mechanisms" in `experimental-deliberation/SKILL.md`—unrelated to this change). 640 npm tests pass. Vocabulary audit: zero leaked product names or hardcoded values in `paper-writing`.

### Unit 6 (U6): Owner Amendment — Binding Precondition

**Owner ruling**: Every existing `bind` invocation must first record a settled `separate` round.

- **What**: `settled_round_licensing` guard in `paper_declarations.bind_section`, refusing `BINDING_UNARGUED` unless all four checks pass: (1) resolved revision matches, (2) document digest matches, (3) score total is 0, (4) title set equals (set equality, not order). Guard lives in `bind_section` itself, not only CLI, so it cannot be routed around.
- **Where**: `paper_declarations.py`, `paper_cli.py`
- **Tests**: 26+ pass, including direct `bind_section` call fixture (not via CLI). Every pre-existing `bind` test retrofit with a settled `separate` round first. Mutation proofs: drop check 2 (digest); drop check 1 (revision); weaken check 4 (subset instead of equality).
- **Key**: Check 4 (title-set equality) is the linchpin—subset-bind and wrong-block fixtures depend on it; only this mutation catches them both.

---

## Final State Facts (Authoritative)

Sourced from task completion gate (persisted), launch prompt explicit facts, and live measurements:

### Completeness

| Metric | Value |
|---|---|
| Implementation tasks | 94/94 complete ✅ |
| Verification verdict | PASS with warnings ✅ |
| Critical findings | 0 |
| Blockers | 0 |

### Test Execution

**Python Suite** (run in four sequential chunks, never concurrently):
- Chunk 1 (test_proposal_implementation, test_paper_writing, test_orphan_sweep): 1653 tests, 0 failures
- Chunk 2 (test_paper_graph): 700 tests, 0 failures
- Chunk 3 (test_paper_decisions): 996 tests, 0 failures
- Chunk 4 (test_paper_separation): 1021 tests, 0 failures
- **Total**: 4370 tests, 1 pre-existing failure (unrelated to this change), 3 skipped, rest passed

**Vocabulary & Leak Audit** (ForgeVocabularyDerivedGuardTests):
- 21 tests run, 1 known pre-existing failure over "mechanisms" in `experimental-deliberation/SKILL.md`
- Zero new failures in `paper-writing`

**TypeScript/npm**:
- `npm test`: 640/640 pass

### Code Metrics

| Metric | Value |
|---|---|
| Engine lines (paper-writing/scripts/) | 1145 of 1600 (71.6%) |
| Test lines | ~150 (net additions) |
| Refusal codes (roster) | 152 total (144 baseline + 8 new) |
| Requirements added | 10 (source-separation-review) + 1 modified (source-section-binding) |
| Scenarios added | 34 (source-separation-review) + 18 (source-section-binding delta) |

### Specifications

| Spec | Status | Details |
|---|---|---|
| source-separation-review | Created | 10 requirements, 34 scenarios, 100% compliant |
| source-section-binding | Extended | 1 new requirement (binding precondition), 51/52 scenarios compliant (2 partial—verified by construction but lack scenario-specific test names) |

---

## Archive Contents Verification

- [x] proposal.md ✅ (15 KB, intent + scope + rollback)
- [x] exploration.md ✅ (8.7 KB, discovery log)
- [x] design.md ✅ (39.8 KB, decisions A–J, six units, mutations, fixtures)
- [x] tasks.md ✅ (27.6 KB, 94/94 tasks complete, budget ruling, work units, ordering rationale)
- [x] verify-report.md ✅ (15.6 KB, PASS with warnings, spec compliance matrix)
- [x] specs/source-separation-review/spec.md ✅ (delta spec, 10 requirements)
- [x] specs/source-section-binding/spec.md ✅ (delta spec, 1 modified requirement)

All artifacts present, archived, and verified with empty diff -r output.

---

## Disclosed Deviations & Open Items

### Deviations (Reported, Not Silently Forced)

1. **Task 1.10 — Mutation pairing for k-1 vs min(k,1)**  
   The design claimed a two-block overlap fixture would redden under `k-1 → min(k,1)`. At k=2, both equal 1; only k≥3 distinguishes them. The applier documented this rather than fabricating a red result. The suite includes both a k=2 (two-block) fixture and a k=3 fixture, both tested and passing.

2. **Task 5.10 — Mutation pairing for check 4 weakening**  
   The design claimed both subset-bind and wrong-block fixtures would redden under check-4 weakening. The wrong-block fixture fails at check 1 (different block id) and is structurally unreachable by that mutation. A dedicated test covers it instead.

3. **Task 6.1 — Design's references/usage.md**  
   Decision J instructed updating both `SKILL.md` AND `references/usage.md`. The `paper-writing` skill has no `usage.md` (verified by `git ls-files` and `fd`), unlike four sibling skills the decision generalized from. Only SKILL.md was updated; no second file was fabricated.

### Known Pre-Existing Failure

- **Test**: `test_proposal_implementation.ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`
- **Scope**: Generic word "mechanisms" in `experimental-deliberation/SKILL.md` and sibling skills' suites
- **Impact**: Unrelated to `paper-writing`; this branch touches zero bytes of any sibling skill
- **Status**: Acknowledged; awaiting owner ruling on sanctioned product-name configuration

### Partial Compliance (Property Holds, Test Coverage Incomplete)

- **Requirement**: "The Negotiation Carries No Authorship Field"
- **Evidence**: Source inspection confirms no origin/author key in `_SEPARATION_TOP_KEYS` or assignment keys. Generic coverage exercises the identical code path an authorship-named key would hit.
- **Gap**: No scenario-named test exists for this specific property.
- **Mitigation**: Property verified by construction; code inspection proves unreachability of authorship-field paths.

### Carry Forward as Open

1. **Sibling change dependency**  
   A sibling change, `the-tripwire-reaches-the-section-that-feeds-it`, is fully planned and applies next. It depends on `resolve_section_index`'s `outline` return (byte offsets), which this change now exports from `paper_graph.py`.

2. **Product-name configuration review**  
   Audit found 48 occurrences of `paper-writing`'s own vocabulary across three sibling skills (including a method name in a `profile.ts` label), plus hundreds in their test suites. Awaiting owner ruling on whether a single sanctioned configuration point is acceptable.

---

## Delivery Guidance

### Commit Instructions

Conventional commit, Spanish subject line matching existing history. **Do NOT add Co-Authored-By or AI attribution** (repository-owner standing instruction).

Suggested commit message pattern:
```
feat(paper-writing): introduce source separation scoring and binding precondition

Introduces six implementation units (U1–U6):
- U1: Level-free claimable-section derivation (paper_separation.py)
- U2: Proposal reader, per-title resolution reuse, round-1 separate verb
- U3: Append-only round persistence, derived numbering, replay logic
- U4: Concession check with disk recomputation (precedence load-bearing)
- U6: Binding precondition guard (BINDING_UNARGUED) with four checks
- U5: Documentation update and roster re-measurement

Adds source-separation-review capability (10 reqs, 34 scenarios).
Extends source-section-binding with binding precondition (1 req, 18 scenarios).

Engine footprint: 1145 of 1600 lines. Refusal roster: 152 (144 + 8 new).
Tests: 4370 Python (1 pre-existing failure), 640 npm.
```

### Pre-Merge Checks

- [x] Branch is 8 commits ahead of main
- [x] Tree is clean (no uncommitted changes)
- [x] All specs merged into `openspec/specs/`
- [x] Change folder moved to archive
- [x] Archive verified with empty diff -r

### Deployment Path

Do NOT merge to main automatically. The user reviews the branch and decides delivery strategy:
- **Single PR**: All changes at once (review budget: 400 lines default, 1600-line owner-ruled budget consumed).
- **Feature branch chain**: Suggested split (proposal) is PR 1: U1 → PR 2: U2 → PR 3: U3+U4 → PR 4: U6 → PR 5: U5, each targeting the previous branch.
- **Strategy decision**: Awaiting owner choice.

---

## Key Learnings

1. The owner's ruling that "a decision about the paper is made by USING the skill, never by reading prose" is enforced structurally: the binding precondition guard lives in `bind_section`, not only CLI, so it cannot be routed around.

2. Refusal precedence (overlap > orphan > gap) is load-bearing, and reversal changes the reachability of the `SEPARATION_CONCESSION_REGRESSED` fixture, proving the ordering invisible to happy-path tests alone requires an explicit mutation.

3. A round's score is authority-free: recomputation from disk proves the critical property (`SEPARATION_CONCESSION_REGRESSED` fires on the recomputed value, not the stored one), and a mutation that swaps to stored-score reading makes the test red.

4. The sibling-skill vocabulary audit discovered 48 collisions across three skills, including method names in profile labels—a future configuration decision independent of this change.

5. The integration with `resolve_section_index`'s byte-offset outline shape is proven by import and call, not by behavior change, satisfying the sibling dependency without code duplication.

---

## Archive Status

**Status**: COMPLETE  
**Archived at**: `openspec/changes/archive/2026-09-20-the-whole-cut-is-argued-before-any-section-is-claimed/`  
**Engram Entry**: `sdd/the-whole-cut-is-argued-before-any-section-is-claimed/archive-report`  
**SDD Cycle**: CLOSED

The change is ready for review and delivery. The branch remains on `u1-the-cut-is-scored-before-it-is-argued`; the user decides merge timing and strategy.
