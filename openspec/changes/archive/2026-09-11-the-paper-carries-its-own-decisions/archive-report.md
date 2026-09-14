# Archive Report: The Paper Carries Its Own Decisions

**Change**: `the-paper-carries-its-own-decisions`
**Phase**: 3 of the `paper-writing` build (third of seven archives closing this build)
**Archived**: 2026-09-11
**Archived to**: `openspec/changes/archive/2026-09-11-the-paper-carries-its-own-decisions/`
**Artifact store**: hybrid (filesystem canonical + Engram mirror)

## Observation IDs Read (traceability)

| Artifact | Engram ID | Notes |
|---|---|---|
| proposal | #1614 | |
| spec | #1622 | |
| design | #1625 | |
| tasks | #1635 | includes corrective-batch notes, commit `12ac0b7` |
| verify-report | #1648 | includes scoped re-verification appended 2026-09-11 |
| bugfix (reopen-drift falsification) | #1663 | independent re-falsification of the sole CRITICAL, ruling on second orphan |

## Final-State Authority — resolving the verify-report FAIL label

The verify-report's structured envelope reads `verdict: fail`, `blockers: 0`,
`critical_findings: 0`. Per the Final-State Authority hierarchy, the
substantive ranking is:

- **Native admission-tool rule, not a substantive defect**: `gentle-ai
  sdd-verify-validate` enforces `completed == total` for both `requirements`
  and `scenarios` before it will admit a `pass`/`pass_with_warnings` verdict,
  with no severity carve-out. One pre-existing, non-blocking UNTESTED
  scenario (`contract-provenance`'s "one edit flags every block of the
  section" — untested because `compute_plan` computes `drift()`
  independently per block with no shared/cached state, low-risk by
  construction) forces `requirements: 18/19` and `scenarios: 26/27`, and
  therefore `verdict: fail` at the envelope level, even with zero blockers
  and zero CRITICAL findings.
- **The sole CRITICAL** (`--reopen` never marked any written block stale in
  the provenance region, despite a passing but orphaned unit test for
  `affected_blocks`) was fixed in corrective commit `12ac0b7` and then
  **independently re-falsified** in a separate scoped re-verification pass
  (bugfix #1663 / verify-report #1648's "Re-Verification (scoped)" section):
  a 3-block corpus exercising narrowing, resubstitute-after-reopen,
  double-reopen, and an indirect fact-channel match, run twice across two
  separate commits (`0ea0e7c`, `f3b3fcf`) either side of a session reset,
  byte-identical results both times. RESOLVED, not merely claimed.
- **A second orphan** (`validate_observation_report`, zero production
  callers) was found by the corrective and ruled **accepted debt, not a
  second CRITICAL**, by direct reading of `specs/paper-declarations/spec.md`'s
  `Requirement: insumos-observer Reports Fact Satisfaction, Decides Nothing`
  — no MUST clause names it as a required runtime consumer, unlike the
  requirement that named `affected_blocks` explicitly.
- The verify report's own explicit call: **"Archivable: yes. Nothing
  blocking remains for this change."**

The task tool's launch prompt states verify status is "archivable" with the
verify report in the change folder — consistent with the above. No
contradiction found between the launch prompt and the ranked evidence; the
`fail` label is reported here as a strict-admission-tool artifact, not
echoed forward as an open defect.

**Substantive verdict carried into this archive**: PASS WITH WARNINGS.
Zero blockers, zero CRITICAL findings. One pre-existing, non-blocking
UNTESTED scenario remains open (see Known Follow-ups below).

## Task Completion Gate

`openspec/changes/the-paper-carries-its-own-decisions/tasks.md` (pre-move):
verified directly — `rg -c '^\- \[ \]'` found zero unchecked boxes;
`rg -c '^\- \[x\]'` found 37, matching the artifact's own "37/37 tasks
complete" status line. No stale-checkbox reconciliation was needed.

## Native Review Receipt Gate

No `reviewGate` was present in the launch context and no review artifacts
(`sdd/{change-name}/review/*`) were referenced by any upstream phase.
Receipt-driven development did not gate this candidate; archive proceeds
under ordinary repository policy per the gate's absent-key rule.

## Specs Synced

| Domain | Action | Details |
|---|---|---|
| `block-substitution` | **Merged (delta)** into existing `openspec/specs/block-substitution/spec.md` | 2 ADDED requirements appended (`substitute Accepts an Optional --contract Flag`, `--contract Is Additive to the Existing Refusal Roster`); Refusal Roster table grew from 20 to 21 data rows with `CONTRACT_UNREADABLE` (work-state) appended. Merged against the **current on-disk file** (20 rows, per the first archive's explicit warning), not any verify-report's stale description of it. Requirement count 12 → 14. This is a **delta merge**, not a create — `block-substitution` was created by the `only-the-block-changes` archive; a further sibling (`the-couplings-hold-or-they-do-not`) is expected to merge into it after this archive. The file remains fully able to absorb another additive delta: all requirements are independent `### Requirement:` sections and the Refusal Roster is a single append-only table. |
| `guidance-registry` | Created | full new spec, mechanical `cp` (main spec did not exist) |
| `paper-declarations` | Created | full new spec, mechanical `cp` (main spec did not exist) |
| `contract-provenance` | Created | full new spec, mechanical `cp` (main spec did not exist) |

### Mechanical copy verification (`diff -r`, empty = pass)

```
=== guidance-registry: diff -r (must be empty) ===
OK guidance-registry
=== paper-declarations: diff -r (must be empty) ===
OK paper-declarations
=== contract-provenance: diff -r (must be empty) ===
OK contract-provenance
```

### Archive folder move verification (`diff -r`, snapshot vs. archived, empty = pass)

```
=== diff -r snapshot vs archived (must be empty) ===
(no output)
DEST=openspec/changes/archive/2026-09-11-the-paper-carries-its-own-decisions
```

The `block-substitution` merge was a textual edit against existing content
(not a whole-file mechanical copy), per the skill's "If Main Spec Exists"
branch — verified structurally instead: Refusal Roster row count 20 → 21
(exactly +1, the one new code), Requirement count 12 → 14 (exactly +2, the
two new ADDED requirements), and a `tail` readback confirmed both new
sections landed with their scenarios intact and no existing content altered.

## Archive Contents

- `proposal.md` ✅
- `specs/block-substitution/spec.md` ✅ (delta, ADDED-only)
- `specs/contract-provenance/spec.md` ✅ (full, NEW)
- `specs/guidance-registry/spec.md` ✅ (full, NEW)
- `specs/paper-declarations/spec.md` ✅ (full, NEW)
- `design.md` ✅
- `tasks.md` ✅ (37/37 tasks complete)
- `verify-report.md` ✅ (original FAIL pass + scoped re-verification pass, both preserved verbatim)

## Source of Truth Updated

- `openspec/specs/block-substitution/spec.md` (merged)
- `openspec/specs/guidance-registry/spec.md` (created)
- `openspec/specs/paper-declarations/spec.md` (created)
- `openspec/specs/contract-provenance/spec.md` (created)

## Known Follow-ups (non-blocking, carried forward honestly, not re-litigated)

1. `contract-provenance`'s "one edit flags every block of the section"
   scenario (two blocks sharing one contract file) has no covering test.
   Low-risk by construction (`compute_plan` computes `drift()`
   independently per block, no shared/cached state) — this is the sole
   reason the structured verify envelope reads `fail`.
2. `paper_declarations.validate_observation_report` has zero production
   callers (accepted debt, not a defect — no spec MUST clause names it as a
   required runtime consumer). A future change wiring `insumos-observer`'s
   report into an automated consumer should route through this validator.
   A concrete recommendation on record: pin the current absence with a
   small static test rather than relying on a source comment alone.

## Note for the next sibling merging into `block-substitution`

`the-couplings-hold-or-they-do-not` is expected to merge into
`block-substitution` next. As of this archive, the main spec has:
- 14 `### Requirement:` sections
- 21 data rows in the Refusal Roster table (header + separator + 21 = 23
  lines matching `^\|`)

Merge against the current on-disk file at archive time, not against this
report's snapshot counts above, which will already be stale by then.

## Test Evidence (from the highest-ranked source covering it — scoped
re-verification, verify-report #1648)

- `npm test` → 559/559 passed, exit 0.
- `npm run typecheck` → exit 0 (clean; dev dependencies confirmed installed
  during the re-verification pass — this was not a stale `tsc: command not
  found` warning carried forward from an earlier point in this build).
- `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` → 3085
  ran, 0 failed, 6 skipped, exit 0.
- `tests.test_paper_decisions` (this change's own module) → 53/53 ok, run
  twice across two sessions.
- `tests/test_paper_writing.py::RefusalRosterTests` → 5/5 ok.
- All 7 mutation-proof tests (M1–M7 across region grammar, guidance
  registry, declarations ×3, provenance, observation report) → 7/7 ok.

Per the launch prompt's explicit note, the test suite was NOT re-run by this
archive phase (green at HEAD, other agents contending for CPU); the above
numbers are carried from the highest-ranked prior source (the scoped
re-verification, not the earlier original FAIL pass's numbers).

## SDD Cycle Complete

The change has been fully planned, implemented, verified (including one
corrective batch and one independent scoped re-verification), and archived.
Ready for the next change.
