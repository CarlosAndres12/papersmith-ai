# Archive Report: The Block Asserts Only What Its Section Carries

**Change**: `the-block-asserts-only-what-its-section-carries`  
**Status**: ✅ PASS WITH WARNINGS  
**Archived**: 2026-09-21  
**Branch**: 5 commits ahead of `main`  

---

## Final State Authority

This archive report reflects the state of the change AT CLOSE per the archive phase's Final-State Authority hierarchy. Work continued after intermediate artifacts (`apply-progress`, `verify-report`) were persisted; those are intermediate snapshots and do not represent final state. All facts below are authoritative as of this archive date.

**Verdict Determination**: 
- `verify-report` (observation ID N/A, persisted to filesystem): PASS WITH WARNINGS
- Final-state facts in launch prompt: all 47/47 tasks ticked, seam confirmed as landed
- No later commits changed the verdict

---

## Completeness Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Tasks** | 47/47 complete | ✅ All ticked |
| **Requirements** | 9/9 satisfied | ✅ All compliant |
| **Scenarios** | 24/24 passing | ✅ All green |
| **Build** | `npm test` | ✅ 646/646 passed, 0 failed |
| **Tests (Python)** | Full discover suite | ✅ 4559/4559 passed, 3 pre-existing skips, 0 failures |
| **Refusal codes added** | 4 new, all `WORK_STATE` | ✅ All reachable (mutation-proven) |
| **Engine lines (`.claude/skills/`)** | 235 lines added | ✅ Well under 1600 ceiling |

---

## What This Change Delivers

**New Capability**: `transposition-grounding` — a fourth sibling judge inside `write_block` that verifies a block's assertions are grounded in its bound source sections.

**Core Responsibility**: 
- Derives the subject set as a byte-derived intersection of draft bindings and bound sections
- Reconciles per-sentence verdicts from an optional grounding account against independently re-derived bytes
- Inverts the burden of proof: `supported` requires byte-present span; `unsupported` needs none

**New Refusal Codes**:
1. `GROUNDING_ACCOUNT_ABSENT` — subjects exist but no account was supplied
2. `GROUNDING_SENTENCE_UNKNOWN` — account entry names a sentence the guard didn't segment
3. `GROUNDING_VERDICT_MISSING` — subject sentence has no account entry
4. `SECTION_UNSUPPORTED_CLAIM` — agent marked sentence as unsupported

**Wiring**: Fires inside `write_block` after `check_source_section_verbatim` clears, before `substitute`.

---

## Known Issues Recorded

### WARNING: Untested Degenerate Span Acceptance

**Description**: The byte-presence check does not exclude the section's own markdown heading line from the "grounded" text. A `supported` verdict citing only the heading title (e.g., `"3. Calibration Regime"`) passes reconciliation unchanged, with no downgrade and no refusal.

**Root Cause**: `resolve_bound_sections`' `"text"` field is sliced from `heading["byte_start"]` (`paper_source_span.py:66-67`), and `segment_markdown` sets that `byte_start` to the ATX heading match's start (`paper_guidance.py:422`). The heading line itself is thus part of the byte-derived text the spec's own `Requirement: The Permissive Verdict Carries The Burden Of Proof` defines as the comparison target. The byte-presence check technically complies with the spec as written — the heading line genuinely is part of "the section's own bytes" — but it is a real, untested gap in the property this change exists to make load-bearing (D1: inverted burden of proof).

**Impact**: None to the 24 scenarios (the shared `_bound_section` fixture never includes a heading line in its `text` field, unlike real `resolve_bound_sections` output). The property is intact for tested cases.

**Why Not Fixed Here**: Fixing it correctly (stripping the heading line from comparison text or requiring minimum span length) would mean changing `resolve_bound_sections`' shared semantics in `paper_source_span.py`, which also backs the already-shipped `transposition-fidelity`/`SOURCE_SECTION_VERBATIM` check — outside this change's stated scope (design.md D5: "`paper_leak.py` is touched by this change not at all"; no file change here touches `paper_source_span.py`). Reported here explicitly so the gap is never silently waived; a future session should address it before `transposition-grounding` is used against real documents.

**Verification Evidence**: Reproduced directly by execution in the verify phase (not by reading); recorded in `verify-report.md` lines 142-169.

---

## Open Obligations Recorded

### Unexecuted D2 Falsifier (Task 3.10)

**What**: The ruling that `downgraded > 0` or `subjects > 0` with `decided == 0` NEVER block (design.md D2) carries no ratio threshold. This is a deliberate JUDGEMENT CALL, not a measurement, backed by a falsifier rather than invented numbers.

**Falsifier (exact text from spec)**:
> Over ten or more recorded real `write` runs against genuine `document`-rooted bindings, if any block reaches `written` with `downgraded > 0`, or with `subjects > 0` and `decided == 0`, this ruling is wrong and a blocking rule over these counts must be added.

**Executability**: UNEXECUTABLE as of archive date (2026-09-21). No real `document`-rooted binding exists on disk in this repository (`transposition-fidelity/spec.md:28-34`). Every scenario this change proves uses a `bind`-recorded fixture with invented names. There is no corpus of ten real `write` runs against document-rooted bindings yet.

**Status**: NOT closed, NOT satisfied, NOT waived — open, dated, and waiting on precondition (real document-rooted bindings). A future session accumulating ten or more real `write` runs must check this falsifier against actual `sourceGrounding` reported counts.

**Recorded In**: `SKILL.md` (verbatim) and `tasks.md` (this archive, closing section) — the ruling stays arguable in both places a reader might land.

---

## Disclosed Deviations (Benign)

### Deviation 1: Import Row Timing

**What**: The import row for `paper_grounding` (task 2.5) landed in WU1's commit rather than WU3's as planned.

**Why**: `ModuleCompletenessTests` forces the import row the instant a new script file exists on disk. `paper_grounding.py` was created in WU1 (phase 0.6), so the import row appeared then.

**Impact**: None — the change's logic, scope, and rollback remain identical. The import row is still in `paper_cli.py:75-107`, correctly positioned, and carries its own comment anchor.

### Deviation 2: And-Operand Reordering

**What**: Two `and`-operands in `paper_grounding.py` were reordered (commutative, behaviour-preserving) to break a literal mutation-anchor collision.

**Why**: The mutation harness (`tests/paper_mutation.py:64-68`) requires each anchor string to occur exactly once. Two distinct refusal conditions had anchors that could collide if operands weren't ordered distinctly.

**Impact**: None — the logic is unchanged; the conditions are commutative and produce identical results. The reordering exists purely to satisfy the mutation harness' uniqueness requirement.

**Verification**: Both suites green; logic unchanged.

---

## Seams and Dependencies

### Seam with Sibling: `the-redactor-receives-the-section-it-must-transpose`

This change assumes its sibling has landed. The ordering gate (task 0.1) verifies:

**At Archive Time** (2026-09-21): ✅ CONFIRMED LANDED
- `RedactorInput` carries 5 fields including `source_sections: tuple = ()` (verified `paper_bindings.py:40-44`)
- `assemble_packet` accepts keyword params `corpus=None, paper_dir=None` (verified `paper_cli.py:2052`)

This change closes the seam by verifying the draft did not invent what the section does not say. The ordering gate (task 0.1) was satisfied by the sibling landing first.

---

## Governing Property (Load-Bearing)

**The Permissive Verdict Carries The Burden Of Proof (D1)**:

The PERMISSIVE verdict (`supported`) carries the burden of proof. Only a `supported` whose cited span is byte-present in the bound section's sliced text survives. This inverts `contract-audit`'s shipped asymmetry, where the BLOCKING verdict quotes the span. If that asymmetry were copied here naively, the guard would be green and worthless — any ungrounded `supported` would wave everything past.

**Proof**: Task 1.1 plants this as a failing test first (RED), then `reconcile_support` enforces it. Mutation proof 3 (task 3.3) removes the byte-presence check and confirms the test goes red — the guard is reachable, not ceremonial.

---

## Roster and Metrics

**Refusal Code Roster**: `reachable_paper_refusal_codes()` was re-derived at archive time (task 3.7). The pinned literal at `tests/test_paper_writing.py:7975` now asserts **165** (was 161 before this change).

**Code Addition**: 235 engine lines under `.claude/skills/` across three files:
- `paper_write.py`: +30/-2 (bindings wiring, grounding check position)
- `paper_cli.py`: +33/-1 (CLI wiring, import row, refusal codes)
- `paper_grounding.py`: +172/-0 (new file, subject derivation, reconciliation, reporting)

**Test Coverage**: 39 new grounding-specific tests, all green, exercising every requirement scenario.

**Zero Deletions**: Confirmed by `git diff main --diff-filter=D` (empty).

**Sibling Module Untouched**: `paper_leak.py` byte-identical to `main` (confirmed task 3.8).

---

## Verification Evidence

All facts verified in `verify-report.md` by independent execution (not by reading):

- ✅ All 47 tasks reproduced against actual diff and running code
- ✅ All RED-first guard tasks (0.2, 0.5, 0.7, 0.9, 1.1, 1.6, 1.7, 1.9, 1.10, 1.11, 1.13, 1.14, 2.8) independently reproduced
- ✅ All four mutation proofs (3.1-3.4) re-run and confirmed red-under-mutation
- ✅ Generality sweeps (0.10, 1.15, 3.6) confirmed zero leakage
- ✅ Roster re-measured live (3.7)
- ✅ Both full suites run (3.9): npm test 646/646, Python discover 4559/4559

---

## Artifact Locations

**Archived Change Folder**:  
`openspec/changes/archive/2026-09-21-the-block-asserts-only-what-its-section-carries/`

**Contents**:
- `proposal.md` — change rationale and scope
- `design.md` — architecture decisions (D1–D9)
- `tasks.md` — 47 implementation tasks with RED-first discipline
- `specs/transposition-grounding/spec.md` — 9 requirements, 24 scenarios
- `verify-report.md` — full verification evidence
- `apply-progress.md` — WU-by-WU apply log
- `exploration.md` — research phase

**Canonical Spec**:  
`openspec/specs/transposition-grounding/spec.md` — created at archive time by copying from delta (CREATE, not COMPOSE, per SUGGESTION in verify-report.md).

---

## Key Learnings

1. The burden-of-proof inversion (D1) is the load-bearing property; removing the byte-presence check makes the guard ceremonial and green without meaning.

2. A degenerate span edge case (heading line only) was not fixed here because correcting it requires widening `paper_source_span.py`, which backs another already-shipped guard, outside this change's stated scope.

3. Mutation proofs must anchor on distinct lines; two operand-reordering collisions were benign but required reordering to satisfy the uniqueness requirement of the mutation harness.

4. The ordering gate (task 0.1) is a stop-and-report instruction; the sibling's landing was verified at archive time, not assumed.

5. An open D2 falsifier was deliberately shipped without a ratio threshold because no real document-rooted bindings exist on disk yet; the falsifier waits for future real data.
