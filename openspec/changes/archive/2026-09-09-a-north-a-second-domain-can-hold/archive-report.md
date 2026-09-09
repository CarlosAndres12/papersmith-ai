# Archive Report: a-north-a-second-domain-can-hold

## Change Status: ARCHIVED

**Change Name**: `a-north-a-second-domain-can-hold`  
**Archived To**: `openspec/changes/archive/2026-09-09-a-north-a-second-domain-can-hold/`  
**Archived Date**: 2026-09-09  
**Final Status**: COMPLETE — all phases 0–5 verified, all tasks [x]

## Observation IDs (Engram Artifacts)

| Artifact | ID | Type | Created |
|----------|-----|------|---------|
| Proposal | #1562 | architecture | 2026-09-09 00:57:51 |
| Spec (Delta) | #1563 | architecture | 2026-09-09 01:03:27 |
| Design | #1564 | architecture | 2026-09-09 01:09:57 |
| Tasks | #1565 | architecture | 2026-09-09 01:14:32 |
| Verify-Report | #1568 | architecture | 2026-09-09 02:43:59 |

## Specs Merged

| Domain | Action | Destination | Details |
|--------|--------|-------------|---------|
| deliberation-objective-flow | Created (NEW) | `openspec/specs/deliberation-objective-flow/spec.md` | Full spec, no existing spec to merge |
| deliberation-delegated-stretches | Created (NEW) | `openspec/specs/deliberation-delegated-stretches/spec.md` | Full spec, no existing spec to merge |

**Verification**: Both specs copied mechanically (shell `cp`) from change folder to main specs. Diff -r shows identical files (empty diff, status 0). ✅

## Archive Contents

- **proposal.md** ✅ (7.8 KB)
- **design.md** ✅ (16.4 KB)
- **tasks.md** ✅ (10.9 KB, all [x])
- **verify-report.md** ✅ (17.4 KB)
- **specs/** ✅
  - deliberation-objective-flow/spec.md (4.3 KB)
  - deliberation-delegated-stretches/spec.md (4.7 KB)

**Source Directory Removal**: Confirmed — original `openspec/changes/a-north-a-second-domain-can-hold/` no longer exists after `git mv` to archive.

## Task Completion Gate: PASS

All implementation tasks marked [x]:
- Phase 0 (Measurements): 0.1 ✅, 0.2 ✅
- Phase 1 (Parametrize/Unit 1): 1.1–1.8 ✅
- Phase 2 (Experimental North/Unit 2): 2.1–2.3 ✅
- Phase 3 (Guard Layers/Unit 3): 3.1–3.7 ✅
- Phase 4 (Agents + Seal/Unit 4): 4.1–4.9 ✅
- Phase 5 (Full-Suite Verification): 5.1–5.4 ✅

**Task Deviation Notes Recorded**: Yes. Task 3.1 implementation location corrected (placed in proposal-deliberation-objective-flow.test.mjs per design.md, not domain-profile-lock.test.mjs per literal task line). Task 4.3 scope corrected (2 agents received `stretch: terminal`, not 3, because skill-audit is northless). Measurements corrected task 3.6's occurrence count (124, not 126, after Phase 1 deleted legitimate OBJECTIVE_FLOW occurrences). Task 5.2 baseline recorded as +1 delta (new test method added, one rewritten in place).

## Verification State

**Source**: Verify-Report (obs #1568), timestamped 2026-09-09 02:43:59, with state re-measured at final verification run per preflight update.

**Verdict**: PASS WITH WARNINGS

**Measured Test Counts** (from preflight final state, not verify-report snapshot):
- `npm test`: **556 pass / 0 fail** (preflight update; verify-report showed 548)
- `.venv/bin/python -m unittest discover -s tests`: **Ran 2782, OK (skipped=6)** (preflight update; verify-report showed 2779)
- `npm run typecheck`: **exactly 2 known errors in smoke-runner.ts** (unchanged)

**3 CRITICAL Coverage Gaps** (from verify-report, now closed per preflight):
1. "The doctrine states the north's actual reach" (deliberation-objective-flow requirement) — zero covering test at verification time; **CLOSED by fb4b961**
2. "The deliberated stage is never delegated" (deliberation-delegated-stretches requirement) — zero covering test at verification time; **CLOSED by fb4b961**
3. "Domain-bound lines are adapted, not copied verbatim" — zero covering test at verification time; **CLOSED by fb4b961**

**2 Remaining WARNINGs** (from verify-report):
1. "A complete profile loads unchanged" (proposal-deliberation) has only static coverage, vs experimental-deliberation's live CLI end-to-end test. Behavior verified correct by direct execution.
2. Scenario-count discrepancy: spec claims 17 scenarios, measured 14 (`rg -c '^#### Scenario:'` across both domain specs = 7+7). Informational only; spec/code alignment verified correct.

**Byte-Identical Verification**:
- `successor-composite-engine.ts`: confirmed byte-identical to merge commit 31a7b71 via `git diff --quiet`
- `patch-compiler.ts`: confirmed byte-identical to merge commit 31a7b71 via `git diff --quiet`
- `proposal-deliberation/profile.ts` objective block: pure addition, pre-change OBJECTIVE_FLOW literal verified identical

## Carried-Forward Residues (Per Preflight)

### 1. PINNED_RESIDUE: Two Words

Both are pinned by exact occurrence count and sorted file list to detect loss:

**Word "equation"**: 124 occurrences across 10 core files (measured via `rg -o`, occurrence-accurate, not line-count).
- Files: artifact-naming.ts, cli.mjs (2 deleted by Phase 1), domain-profile.ts, edit-planner.ts, extraction-engine.ts, extraction-planner.ts, patch-compiler.ts, schema.ts, types.ts, witness-signature.ts
- Status: **PINNED** — Phase 1 legitimately deleted `OBJECTIVE_FLOW` occurrences in cli.mjs; count adjusted 126 → 124 per apply-progress
- One occurrence inside `patch-compiler.ts` is byte-frozen (type name `display_equation` + `CLEANUP_EQUATION_FORBIDDEN` + `equationLabel` + `SAFE_EQUATION_LABEL`)
- Layer C-3 (derived subject words) cannot fire on this residue (it is NOT a domain subject — it is a core TYPE NAME)

**Word "proposal"**: 192 occurrences across 24 files (measured via `rg -o`).
- Primary: subsystem is named after it (proposal-deliberation, proposal-implementation, proposal-workspace)
- Status: **PINNED** — guard layer C-3 cannot fire (word appears in BOTH profile objectives: proposal-deliberation's "carry the mathematics..." and experimental-deliberation's engagement with proposals as input)
- **Measured consequence**: C-3's vacuity self-check reports when ≥2 profiles exist and discover 0 subject words common to exactly 1 profile

### 2. Verify Report's Conditional PASS

The verify-report verdict (obs #1568) was PASS WITH WARNINGS when written at verification time (2026-09-09 02:43:59). Three CRITICAL coverage gaps existed at that point:
- All **three gaps are now CLOSED** as of commit fb4b961 (per preflight)
- Two WARNINGS remain (static-only coverage for proposal-deliberation, scenario count 17 vs 14 measured)
- These warnings do NOT block archive (archive rule: CRITICAL issues block, WARNINGs do not)

**Final traceability**: The CRITICAL findings were live at verify time and are now resolved. No other verification issues surfaced in final suite runs (5.1–5.4 all pass).

### 3. `sd` Tool Cost (Knowledge Record)

The `sd` stream-editor tool has cost work three separate ways in this repository:

1. **Default non-literal mode**: reads `${...}` as capture-group references, corrupting path construction (occurred twice in this session before mitigation)
2. **sd -s flag (literal) bug**: exits 0 while changing nothing when the pattern does not match across line breaks in hard-wrapped prose
3. **Mutation verification impact**: when a mutation's anchor count does not change, the mutation did not run — only occurrence-accurate counting (`rg -o`) reliably detects this

**Applied**: Use `rg` exclusively for counting (via `-o` flag), use plain `sed` for prose edits in deliberation documents, never use `sd` in this codebase.

## Eight Out-of-Scope Items (Recorded, Not Fixed)

These eight items were explicitly out of scope for this change and remain open:

1. **Unreachable `plannerCalls` budget**: `buildEditPlan` never returns a value, so the `maxPlannerCalls` budget can never fire — the most serious item
2. **Two `smoke-runner.ts` type errors**: pre-existing, known, outside scope
3. **`CLOSE_DELIBERATION` with no budget entry**: missing budget definition
4. **Single-term lexical query tie**: still binds inside the ambiguity margin
5. **`artifact.marker` still spelled in three core files**: should be profile-supplied like `objective`
6. **Experimental skill's required sources absent from disk**: cannot be used without manual setup
7. **Merge to `main`**: deliberately not merged; user decides timing
8. **Absent SDD artifacts from previous delegated-direct stretch**: prior work incomplete

## SDD Cycle Complete

✅ **Proposal** — defined scope, approach, rollback plan  
✅ **Spec** — two NEW domain specifications (deliberation-objective-flow, deliberation-delegated-stretches)  
✅ **Design** — detailed 17-item mutation plan, three guard layers (C-1/C-2/C-3), profile extension, generalized test, two new agents  
✅ **Apply** — all four work units (parametrize, experimental north, guard layers, agents + seal) implemented and verified  
✅ **Verify** — PASS WITH WARNINGS; 3 CRITICAL gaps now CLOSED by fb4b961  
✅ **Archive** — change folder moved, specs synced to main, final state recorded  

The change is complete and ready for merge to `main` (user decides timing).

---

**Archive Report Persisted**: Engram `sdd/a-north-a-second-domain-can-hold/archive-report` (observation recorded with all artifact IDs for traceability)

