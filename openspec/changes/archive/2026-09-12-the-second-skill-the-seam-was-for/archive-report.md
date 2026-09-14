# Archive Report: the-second-skill-the-seam-was-for (Slice A)

**Status**: ARCHIVED — Complete and closed
**Change**: the-second-skill-the-seam-was-for (Slice A)
**Archived to**: `openspec/changes/archive/2026-09-12-the-second-skill-the-seam-was-for/`
**Date**: 2026-09-12
**HEAD**: 587399e

## Verdict Summary

**PASS** — 10 requirements, 24 scenarios across 3 spec files, 33/33 tasks complete, 0 CRITICAL, 2 WARNING, 1 SUGGESTION.

- JavaScript: `npm test` 595/595 ✓
- Python: `Ran 2956, OK (skipped=6)` ✓
- `sha256(tests/seal/digests.json)` unchanged ✓
- Zero engine bytes changed ✓

## Traceability — Engram Observation IDs

All artifacts persisted and retrievable via Engram with these topic keys:

| Artifact | Observation ID | Retrieved |
|----------|---|---|
| proposal | 1727 | ✓ |
| spec | 1741 | ✓ |
| design | 1743 | ✓ |
| tasks | 1745 | ✓ |
| verify-report | 1751 | ✓ |
| archive-report | (this file) | — |

## What This Change Delivers

**`experimental-implementation` now exists as a second skill on the shared implementation engine seam, with:**

- Own `impl_profile.py` in `.claude/skills/experimental-implementation/`
- Byte-identical launcher (24 lines, copied from `proposal-implementation`)
- Own `SKILL.md` (2,854 lines, full doctrine)
- Two thin agents: `experiments-build.md` and `experiments-walk.md` (~70 lines each, no logic)
- Own sealed corpus at `tests/experiments_seal/` (beside, never inside `tests/seal/`)
- Single declared document (experiments) — Slice A governance only
- **Zero changes to the shared `_core/implementation/` engine**
- **All 28 existing `proposal-implementation` seal digests untouched**

This is Slice A of a four-change series (A, B, C, D) recommended in the proposal. B (Data/ per product) and C/D (claim vocabulary, cross-document agreement) are separate follow-on changes.

## Specs Merged Into Main Specs

### New: experimental-implementation-skill

**Action**: Created new full spec (not a delta)
**Location**: `openspec/specs/experimental-implementation-skill/spec.md`
**Requirements**: 5 (The Skill Declares Its Own Domain Profile, One Skill One North, The North Belongs To This Skill Alone, The Two Agents Carry No Logic, A Single Document Reproduces Byte-Identical Guarantee)
**Scenarios**: 10

Mechanical copy verified with diff — no truncation.

### Modified: implementation-engine-neutrality

**Action**: Merged delta into existing spec
**Location**: `openspec/specs/implementation-engine-neutrality/spec.md`
**Changes**:
1. MODIFIED: "The Kit Template's Provenance Keys Agree With The Profile" — now globs via `discover_profiles()` instead of hardcoding `proposal-implementation`; each skill's check independent via `subTest`/separate methods
2. ADDED: "The Derived-Denylist Lock Becomes Satisfiable, Not A Permanent Skip" — M5 buildDenylist mirror runs as real test once second profile exists; `skipped=6` invariant held
3. ADDED: "A Namespace Word's Self-Check Is Not The Leak Proof" — Lock A self-check passes trivially for namespace words; whole-engine scan is sole mutation-provable guard

### Modified: implementation-cli-seal

**Action**: Merged delta into existing spec
**Location**: `openspec/specs/implementation-cli-seal/spec.md`
**Changes**:
1. MODIFIED: "Non-Interference With Sibling Suites" — added scenario: shipping `experimental-implementation` must not move any of the existing 28 sealed digests
2. ADDED: "The Second Skill Ships Its Own Seal, Added Beside The Existing One" — `experimental-implementation` gets its own committed stdout-characterization seal (single-document corpus), added beside `tests/seal/`; `git diff --exit-code tests/seal/` stays 0

## Key Findings (from verify-report #1751)

### Headline Finding: M1 Guard Can Now Fail

**`test_every_declared_name_really_is_that_domain_speaking` was vacuous for every profile, now provably fixed.**

The test searches `entry["source"]` (the entire profile file text), which contains the `names` list literal. Any declared name trivially finds itself in its own declaration. Verified by:
1. Planting `"zzz-nothing-anywhere"` into the real shipped `.claude/skills/experimental-implementation/impl_profile.py`'s `vocabulary.names`
2. Confirming test fails with `AssertionError`
3. Byte-identical revert via backup/`shasum -a 256` verification
4. Re-run confirms green

The strengthened check (haystack = profile's declared VALUES, `vocabulary.names` excluded) lands as part of this change. Sibling (`proposal-implementation`) passes unedited and byte-untouched.

### Other Verified Findings

- **sys.modules caching defect reproduced**: Removing `sys.modules.pop()` calls in test harness causes 14/14 test failures (fresh engine loads under mutated profile silently reuse first-resolved profile). Restored, confirmed byte-identical.
- **Zero engine bytes confirmed with existence checks**: `git cat-file -e` verified both profile trees exist before diffing (avoiding trivial diff-against-nonexistent trap). `git diff --stat` showed zero output.
- **Second seal corpus run live from scratch**: `tests/experiments_seal/` beside (never inside) `tests/seal/`; 12/12 pass on fresh run.
- **D10 guard verified both halves**: New skill cannot declare second document (SingleDocumentGuaranteeTests 2/2); fixtures with two documents still resolve unaffected (tests.test_implementation_pair 23/23).
- **M5 residue independently recomputed**: 74 total / 69 pinned / 5 absent (`formulation`, `mathematical`, `mathematics`, `statistical`, `traced`) — exact match to apply's measurement.
- **Subject-word counts**: Two instruments, two questions: occurrence counts (`experiment` 24, `experiments` 6) via `rg -oi`; line counts (89/30/28) via `rg -c`. Both re-derived and matched.

## Warnings (per verify-report #1751 and orchestrator briefing)

### WARNING W1: Task Count Discrepancy

**Claim**: tasks.md holds **40** tasks
**Measured**: tasks.md holds **33** completed tasks (all checked ✓)
**Source**: Originated in `sdd-apply` commit message, repeated uncritically in verify brief

This is the third inherited count this session that did not survive being counted (earlier: `_POSITION_HEADER_RE` never existed; subject-word counts were 89/30/28, not 88/23/20). The correct count is **33 tasks, all complete**. Bookkeeping numeral nobody verified against the artifact itself.

### WARNING W2: Commit Hygiene

**Observation**: HEAD commit `587399e` bundles:
- Slice A's design-record append
- 371 lines of Slice C's in-flight `proposal.md` (written by parallel planning agent)

**Classification**: Commit hygiene issue, not a scope or engine-neutrality violation. Content not evaluated per explicit scope instruction ("Do not archive it, do not move it, do not touch it").

**Impact**: Nil on this change's closure. Slice C's work is committed and available; provenance is obscured by mingling.

## Stale Intermediate Snapshots (per Final-State Authority)

- **apply-progress**: Intermediate snapshot at apply time; stale claims about pending state now resolved
- **verify-report #1751**: Intermediate snapshot at verify time (2026-09-11 23:59:02); final measurements above supersede stale claims

This archive report is the terminal record. The change is closed.

## Archive Contents Verification

- ✓ proposal.md (openspec/changes/archive/.../proposal.md)
- ✓ specs/experimental-implementation-skill/spec.md
- ✓ specs/implementation-engine-neutrality/spec.md
- ✓ specs/implementation-cli-seal/spec.md
- ✓ design.md (includes D1 revisited section appended in apply)
- ✓ tasks.md (33/33 tasks checked complete)
- ✓ verify-report.md

Active changes directory (`openspec/changes/`) no longer contains `the-second-skill-the-seam-was-for/` — confirmed moved to archive.

Specs merged from main sources:
- ✓ `openspec/specs/experimental-implementation-skill/spec.md` (created)
- ✓ `openspec/specs/implementation-engine-neutrality/spec.md` (updated)
- ✓ `openspec/specs/implementation-cli-seal/spec.md` (updated)

## SDD Cycle Complete

The change has been fully planned (proposal), specified (3 spec files), designed (design.md with 7 measurements), tasked (33 tasks, 4 stacked units), implemented (sdd-apply), verified (sdd-verify PASS), and archived (this report + filesystem moves).

**Ready for the next change.** Recommended next: **Slice C** — the second
document verified on its own terms (the operator's items 2 and 5).

**CORRECTION, applied after this report was first written.** Its original line
named Slice B as the next change and called it "prerequisite for C". **That is
inverted.** B depends on C, not the other way round.

`Data/` becomes demandable when *the document declares a dataset*, and
`**Dataset:**` is enforced only in the experimental deliberation domain — the
mathematical one has none. So B before C would ship a branch no configuration
can reach, which is the exact defect class seven cycles have been paying off.

The real order is **A → C → {B, D}**, and B and D do not depend on each other.
The Slice A proposal's own table lists them A, B, C, D, and that ordering is
what produced this error twice. It is recorded here so a later session reads the
dependency rather than the table.

---

**Archive sealed at**: 2026-09-12 (Engram persisted separately)
