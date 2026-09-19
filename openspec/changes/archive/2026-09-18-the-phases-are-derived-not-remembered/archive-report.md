# Archive Report: The Phases Are Derived, Not Remembered

**Change**: `the-phases-are-derived-not-remembered`
**Archive Date**: 2026-09-18
**Repository**: papersmith-ai
**Branch**: unit9-the-docs-catch-up
**Status**: ARCHIVED — SDD cycle complete

---

## Executive Summary

The change successfully closed the readiness defect where `readiness` computed from CLI flags alone and never opened `main.tex`, remaining structurally blind to `declare`. The change also recovered from two significant corrections late in implementation:

1. **Unit 1 wrote eight false "None" assertions** into internal-chain contracts — six contradicted by prose already in the same file. Unit 1b replaced them with 14 quote-backed rows, turning a stale-reading defect into verified dependencies.
2. **Unit 6b wired gate logic into `cmd_write`**, because the `PHASE_NOT_READY` gate only reported but did not prevent writing an out-of-order wave.

The change introduced three new verbs (`phases`, `skeleton`, `packet`), raised the refusal roster to 107 codes, grew the corpus from 45 to 47 blocks, and established 111 verified internal-chain edges.

---

## Artifact Integration

### Specs Synced (11 domains)

| Domain | Type | Action |
|--------|------|--------|
| contract-input-partition | NEW | Copied to `openspec/specs/contract-input-partition/spec.md` |
| internal-chain-edges | NEW | Copied to `openspec/specs/internal-chain-edges/spec.md` |
| optional-block-semantics | NEW | Copied to `openspec/specs/optional-block-semantics/spec.md` |
| redactor-packet | NEW | Copied to `openspec/specs/redactor-packet/spec.md` |
| skeleton-startup | NEW | Copied to `openspec/specs/skeleton-startup/spec.md` |
| writing-phases | NEW | Copied to `openspec/specs/writing-phases/spec.md` |
| paper-declarations | DELTA | Merged via `sdd-archive-compose` |
| section-contract | DELTA | Merged via `sdd-archive-compose` (CRITICAL: false "exactly three" scenario removed) |
| style-channel | DELTA | Merged via `sdd-archive-compose` |
| writing-orchestration | DELTA | Merged via `sdd-archive-compose` |
| writing-readiness | DELTA | Merged via `sdd-archive-compose` |

### Verification

- **Section-Contract Critical Fix**: The false assertion "the shipped edge set is exactly three named edges" was removed. The merged spec now documents this invalidity and replaces it with verified scenarios (e.g., "Every shipped edge is quote-backed").
- **Test Suite**: All 358 tests pass across `test_paper_contract` and `test_paper_writing` (`OK`).
- **Archive Integrity**: Verified with empty `diff -r` between pre-move snapshot and archived folder.

---

## Work Unit Summary

| Unit | Status | Key Changes | Observations |
|------|--------|-------------|--------------|
| 1 | ✓ Complete | Added `_verify_input_partition` checker; normalized 10 section contracts; added `INPUT_PARTITION_ABSENT` refusal | Out-of-scope: one test in `test_paper_decisions` now requires a fixture edit (one-line addition of empty headers) |
| 1b | ✓ Complete | Replaced 6 false "None" rows with 14 quote-backed entries; rewrote 2 empty "None"s as checkable measurement sentences | Correction caught by read-only audit; positional denial is worse than omission |
| 2 | ✓ Complete | Added `es-dataset`, `rw-*` optional, `mm-proposal` facts | No new refusals registered |
| 4 | ✓ Complete | Transcribed internal-chain edges to `after` fields; added `CHAIN_ROW_UNRESOLVED` and `CHAIN_ROW_UNBACKED` refusals | ~560 LOC; largest unit; split split suggested if review flags it |
| 3 | ✓ Complete | Wired `optional` across readiness and verify paths | No new refusals; `OPTIONAL_BLOCK_ABSENT` remains unmeasured |
| 5 | ✓ Complete | Implemented `derive_waves` pure function; Kahn-sort extraction | Reuses `ORDER_CYCLE` refusal |
| 6 | ✓ Complete | Added readiness `basis` dispatch; introduced `phases` verb; added `READINESS_BASIS_REQUIRED` and `PHASE_NOT_READY` refusals | High complexity: basis + new verb in one unit |
| 6b | ✓ Complete | Wired `PHASE_NOT_READY` gate into `cmd_write` | Correction: gate was read-only in unit 6; now guards actual writes |
| 7 | ✓ Complete | Added `skeleton` verb with disk inference; introduced `ingested_papers`; added 3 new refusals | High complexity: multiple concerns |
| 8 | ✓ Complete | Implemented `packet` verb; added `segment_markdown`; added `GUIDANCE_MARKDOWN_UNREADABLE` refusal | Med–High complexity |
| 9 | ✓ Complete | Documentation, agent docstring updates; wired `optional` into real `verify` call (unit 9b) | No new refusals |

---

## Measured Final State

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Verbs | 17 | 20 | +3 (`phases`, `skeleton`, `packet`) |
| Refusal roster | 96 | 107 | +11 codes |
| Corpus blocks | 45 | 47 | +2 (block-4 split into 4a/4b) |
| Internal-chain edges | 3 | 111 | +108 verified edges |
| Kahn waves | 3 (35/8/2) | 5 (28/11/5/2/1) | Refined wave distribution |
| Test suite | ~290 | 358 | +68 tests (net after corrections) |

---

## Critical Fixes and Corrections

### Correction 1: False Internal-Chain Assertions (Unit 1b)

**What**: Unit 1 wrote eight "### Internal chain: None — nothing here depends on a sibling block" assertions. A read-only audit revealed six were false, each contradicted by prose in the same file (e.g., `01-materials.md` stated a dependency; its contract claimed none).

**Why**: The change required transcribing internal-chain edges from prose; a negative assertion must be verified, not assumed. Outputting a false denial is strictly worse than omitting the section — the validator certifies a false completeness.

**How Fixed**: Unit 1b replaced the six false rows with 14 quote-backed rows showing real dependencies, and rewrote the two genuinely empty cases as checkable measurement sentences.

**Impact**: Ensures every contract row is either quote-backed or explicitly measured as empty.

### Correction 2: Write Gate Never Wired (Unit 6b)

**What**: Unit 6 added `PHASE_NOT_READY` refusal and gated the read-only `phases` verb. However, `cmd_write` never consulted `derive_waves`, so nothing prevented writing an out-of-order wave before an earlier one existed.

**Why**: The gate reported on readiness but did not enforce it. Closing unit 6 left the write path unprotected.

**How Fixed**: Unit 6b wired the same gate computation into `cmd_write`'s wave-check path, using RED-first to validate against the real write verb.

**Impact**: Prevents out-of-order wave writes; enforcement now matches reporting.

---

## Out-of-Scope Items (Operator Decision)

These were identified but deferred per operator decision:

1. **Distributing `research-concept-r21.md` across blocks** — No machinery exists; needs its own design pass.
2. **Anchoring `requires_facts` with `source.quote`** — The field that decides writability is the only one without provenance. Recommended as next change; operator decision pending.
3. **`experimental-design` authorization** — Unauthorised by operator.
4. **`guidance/` classification** — Four folders unclassified; style-channel reports `unmeasured`. Operator's own pending action.

---

## Archive Contents Verification

- [x] proposal.md (retrieved)
- [x] design.md (retrieved)
- [x] tasks.md (all 11 units checked [x])
- [x] specs/ — 11 domains (6 NEW + 5 DELTA merged)
- [x] Archive path: `openspec/changes/archive/2026-09-18-the-phases-are-derived-not-remembered/`
- [x] Active change folder removed: `openspec/changes/the-phases-are-derived-not-remembered/` (gone)
- [x] Mechanical archive verified: empty `diff -r` output

---

## Test Results

**Command**: `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -q`

```
Ran 358 tests in 7.633s
OK
```

All tests pass, including the 68 new tests added across the change.

---

## Source of Truth Updated

The following specs now reflect the new behavior and are the canonical reference for:

- `openspec/specs/contract-input-partition/spec.md` — input partition requirements
- `openspec/specs/internal-chain-edges/spec.md` — internal-chain edge verification
- `openspec/specs/optional-block-semantics/spec.md` — optional-block behavior
- `openspec/specs/paper-declarations/spec.md` — updated declarations scope
- `openspec/specs/redactor-packet/spec.md` — packet-assembly behavior
- `openspec/specs/section-contract/spec.md` — (CRITICAL) edge-set cardinality invalidated; replaced with quote-backed verification
- `openspec/specs/skeleton-startup/spec.md` — skeleton inference and placement
- `openspec/specs/style-channel/spec.md` — updated style metadata
- `openspec/specs/writing-orchestration/spec.md` — updated orchestration flow
- `openspec/specs/writing-phases/spec.md` — wave-gating and readiness basis
- `openspec/specs/writing-readiness/spec.md` — readiness basis dispatch

---

## Key Learnings

1. False denials (negative assertions without proof) are worse than omissions — the validator certifies a false completeness.
2. A gate that reports on a read-only verb must also guard the write verb it affects, or the enforcement is incomplete.
3. Block-level structural splits (e.g., block-4a/4b) may be declared in prose long before they are recognized in the validator — prose carries intent.
4. Corrections caught late in implementation (units 1b and 6b) cost real work but are essential for audit trail integrity.
5. Corpus-wide refusal-roster drifts between parallel spec/design phases require task-level reconciliation per the tasks artifact.

