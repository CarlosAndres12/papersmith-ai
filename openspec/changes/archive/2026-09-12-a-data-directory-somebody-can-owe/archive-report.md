# SDD Archive Report — a-data-directory-somebody-can-owe (Slice B)

**Date**: 2026-09-12  
**Change**: `a-data-directory-somebody-can-owe`  
**Verdict**: PASS WITH WARNINGS  
**Mode**: hybrid (openspec + Engram)  

## Executive Summary

Slice B is archived with **PASS WITH WARNINGS**. The change enables `verify.structure.missingDirs` to contain a `Data/` entry for the first time, by deriving the `with_data` flag from per-`documents[N]` `dataset_marker` declarations instead of disk presence. The WARNING was a documentation-only inaccuracy in design.md's D3 prediction (claiming two registrations when there were three), corrected post-verify and closed in commit `01866cb`. Zero CRITICAL issues; 37/37 tasks completed.

## Change Scope

**Slice B (two work units)**:
- **B1** (Phases 1-7): Core mechanism — per-document leaf, detector, threading through three `build_plan` call sites, fixture profile proof
- **B2** (Phases 8-11): Shipped declaration — real marker landed, skill documentation, experiments seal axis

**Related changes**:
- **Slice A**: Single-document `experimental-implementation` skill (archived)
- **Slice C**: Cross-document agreement in `experimental-deliberation` (follow-on)
- **Slice D**: Experiments successor and Flow B (planning in progress, untracked)

## Verification Summary

**Verdict**: PASS WITH WARNINGS ✓  
**Evidence revision**: sha256:180dd983f2c4a1e35bf5be2e8276ffe3948da4d4d58f51011b75a97d5dfc0a3a  
**Measured at**: 2026-09-12 04:53:04 UTC

### Requirements & Scenarios

| Domain | Requirements | Scenarios | Status |
|--------|---|---|---|
| implementation-data-demandability (NEW) | 7 | 13 | ✓ All covered |
| implementation-document-binding (DELTA) | +2 | +6 | ✓ All covered |
| implementation-engine-neutrality (DELTA) | +2 | +5 | ✓ All covered |
| implementation-cli-seal (DELTA) | +3 | +9 | ✓ All covered |
| experimental-implementation-skill (DELTA) | +2 | +2 | ✓ All covered |
| **TOTAL** | **16** | **35** | **PASS** |

### Test Evidence

| Measurement | Result | Status |
|---|---|---|
| `npm test` | 595/595 pass, 0 fail | ✓ Unchanged |
| Python tests | `Ran 2998 tests ... OK (skipped=6)` | ✓ Unchanged |
| `tests/seal/` digests | sha256=011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75 | ✓ Byte-identical (28 cases) |
| `git diff --exit-code -- tests/seal/` | exit 0 | ✓ No changes |
| `reachable_refusal_codes()` | 114 | ✓ Unchanged |
| `tests/experiments_seal/` | 20 pre-existing unchanged, 4 new + fingerprint | ✓ Measured |

### The Core Acceptance Condition (Item 6, Operator Verdict)

**Before this change**: `verify.structure.missingDirs` structurally could NOT contain `Data/`.
- Pre-change (`fa04edc`): `cmd_verify`'s `with_data = (target / name / "Data").is_dir()`
- Real subprocess test: target with `Trial/` but no `Trial/Data/` → `missingDirs=['Trial/Notebooks', 'Trial/Results', 'Trial/Models', 'src/Trial', 'tests']` — `Trial/Data` absent from list despite disk absence

**At HEAD**: `verify.structure.missingDirs` now CAN contain `Data/`.
- Real subprocess execution: `verify-b-declared → missingDirs=['Trial/Data'], status=drift`
- Control: `verify-a-declared → missingDirs=[]` (document declares no dataset)
- Both halves proven by real execution, not assertions

## Issues & Resolutions

### CRITICAL
None. (0/0)

### WARNING
**1. Design.md D3 documentation inaccuracy** — Closed in commit `01866cb`
- **Claim**: "`--revision` registered at two sites (the eight-name set becomes nine)"
- **Fact**: Three sites — the eight-name set, `walk`'s own, and `plan`'s own third registration
- **Impact**: Functionally correct code, documentation-only error, no behavior change
- **Resolution**: Design.md corrected; shipped code correct; D3's binding (nine commands, per-product demand) stands untouched

### SUGGESTION
1. **apply-progress mid-session snapshot stale**: Reported 24/24 for test_implementation_domain_lock.py; final count 26/26. Not a defect, a normal growth pattern.

## The Three Things Worth This Archive

**1. Reaching configuration was not authored; real bytes matter**

The detector needs profile-supplied marker text, and the reflex is to write a fixture containing one. Instead, `tests/seal/corpus.py` **already carried** line-leading `## 1`/`## 2`/`## 3` (authored two changes earlier, unrelated). Mutating the sibling's `dataset_marker: None` to `"## 2"` makes the detector **real** against bytes nobody wrote to satisfy it, not a fixture artifact.

**2. The `None` branch is structural, proven by spy**

`test_a_none_marker_never_opens_the_document` uses a **call-counting spy** on `revision_source` and asserts zero calls. Verify confirmed the spy actually **registers when triggered** — a spy that cannot register is the same silent-guard defect one level over.

**3. A lock caught the literal in its own author's docstring**

The new detector's docstring spelled `**Dataset:**` as an example. `LockCDeclaredMarkerTests` caught it in the same session it was written, proving the lock reads rather than merely exists.

## Architecture Decisions

### D1–D10 Decisions (Design Phase)

- **D1**: Leaf is a line-leading marker, required key, nullable value
- **D2**: Every declared document consulted, or-folded via `document_revision_names`
- **D3**: `--revision` registered on `plan` ALONE (not `apply`/`materialize`); bound document read from approved plan's `boundTo` key
- **D4**: One conditional key `plan["boundTo"]`, emitted only when `--revision` given
- **D5**: `cmd_verify` moves three statements below revision resolution (all three have readers below)
- **D6**: F5 finished (bare `"Data"` literals → `PRODUCT_DATA`) + `ZeroBareDataLiteralTests`
- **D7**: `LockCDeclaredMarkerTests` in B2 (vacuous until shipped declaration)
- **D8**: B1 mutation is sibling's `None` → `"## 2"` (detector proven against real bytes)
- **D9**: B2 corpus adds two revisions differing in ONE line; zero of existing 20 cases move
- **D10**: B1 → B2 adopted; shipped declaration is last write

### M1–M7 Measured Counts (Verify Phase, Corrections Applied)

- **M1**: `--revision` reaches NINE commands through THREE registrations (not two)
- **M2**: `cmd_verify` computes `with_data` ~95 lines before revision; two readers for `missing_dirs`, one for `structure_ok`
- **M3**: `CoreNamesNoDomainTests` globs non-recursively; zero occurrences of all seven product names in flat core files
- **M4**: Lock phrase over declared marker VALUE (not generic "dataset" word); `classify` already returns `"dataset"` reason
- **M5**: F5 remainder is 3 sites/4 occurrences; 22 further bare literals, named follow-up
- **M6**: `tests/experiments_seal/` fingerprint moves mechanically when `corpus.py` edited at all
- **M7**: `tests/seal/corpus.py` carries real line-leading markers that made B1's mutation real

## Specs Synced to Main

| Domain | Action | Details |
|---|---|---|
| implementation-data-demandability | Created | 7 requirements, 13 scenarios (NEW spec) |
| implementation-document-binding | Updated | Added 2 requirements (6 scenarios) |
| implementation-engine-neutrality | Updated | Modified 1, Added 1 requirement (5 scenarios) |
| implementation-cli-seal | Updated | Modified 1, Added 2 requirements (9 scenarios) |
| experimental-implementation-skill | Updated | Added 2 requirements (2 scenarios) |

## Archive Contents

| Artifact | Status | Details |
|---|---|---|
| proposal.md | ✓ Archived | Includes appended "five questions, ruled" section |
| specs/ | ✓ Archived | Five domain specs, deltas ready for merge (completed) |
| design.md | ✓ Archived | Includes appended correction for D3 |
| tasks.md | ✓ Archived | 37/37 tasks completed, all [x] |
| verify-report.md | ✓ Archived | Full measurements, real subprocess verification |

**Archive location**: `openspec/changes/archive/2026-09-12-a-data-directory-somebody-can-owe/`

## Artifact Traceability (Engram Observation IDs)

| Artifact | ID | Retrieved | Status |
|---|---|---|---|
| sdd/a-data-directory-somebody-can-owe/proposal | 1760 | ✓ Retrieved | Proposal with ruled questions |
| sdd/a-data-directory-somebody-can-owe/spec | 1762 | ✓ Retrieved | Five delta specs concatenated |
| sdd/a-data-directory-somebody-can-owe/design | 1763 | ✓ Retrieved | Design with D1–D10, M1–M7 |
| sdd/a-data-directory-somebody-can-owe/tasks | 1764 | ✓ Retrieved | 37/37 complete, B1+B2 green |
| sdd/a-data-directory-somebody-can-owe/verify-report | 1766 | ✓ Retrieved | PASS WITH WARNINGS, real subprocess proof |

## Next Steps

**Slice C** (follow-on): Cross-document agreement in `experimental-deliberation`
- Requires Slice B complete (`dataset` atom needs declared markers to compare)
- Adds `**Dataset:**` enforcement at skill profile tier
- Approximately 200–300 lines, candidate for Q4 2026

**Slice D** (follow-on): Experiments successor and Flow B
- Requires Slice C complete (agreement rule enables flow)
- Planning in progress (untracked directory `openspec/changes/the-agreement-nothing-computes/`)
- Explicit open decision: cross-document citation key without which every document refuses day one

## Records

**Session ID**: Archive phase began 2026-09-12  
**Verify timestamp**: 2026-09-12 04:53:04 UTC (verify report ID 1766)  
**Archive timestamp**: 2026-09-12 (archive folder moved)  

**Key learnings from this change**:
1. Real bytes (not fixtures written to pass) prove detector correctness
2. Spy-based assertions distinguish guards that read from guards that merely exist
3. Inherited count assertions (apply-progress, design predictions) drift and must be re-measured, not inherited
