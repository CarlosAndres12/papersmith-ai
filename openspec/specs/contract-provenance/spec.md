# Contract Provenance Specification

## Purpose

`main.tex` carries a `provenance` region recording, per written block, the
contract digest and declaration generation it stood on at write time.
Provenance is written once, at `substitute` time, and never reconstructed
afterward. `plan` reads it, names drift, and rewrites nothing.

## Requirements

### Requirement: Provenance Region Grammar

A single `provenance` region MUST exist as `%% paper-writing provenance
begin sha256=<hex>` … `%% paper-writing provenance end`, sharing the exact
marker grammar of the `declarations` region (`sdd/.../paper-declarations`),
distinguished only by its `<kind>` token. Its digest MUST be checked before
every write; a mismatch MUST refuse `PROVENANCE_HAND_EDITED` (work-state)
and MUST NOT overwrite the region. Its marker lines MUST NOT start with
Phase 1's `MARKER_PREFIX` (`b"%% paper-writing block"`), proven disjoint by
the same mutation-proof test required of the `declarations` region.

#### Scenario: A hand-edited provenance region refuses

- GIVEN a `provenance` region whose body was edited outside `substitute`
- WHEN a write targets it
- THEN it refuses `PROVENANCE_HAND_EDITED` and writes nothing

### Requirement: A Provenance Record Is Written Only at substitute Time

When `substitute --block <id> --contract <path>` succeeds, it MUST record,
for `<id>`, the sha256 digest of `<path>`'s bytes as read at that moment
and the `declarations` region's current generation. This baseline MUST be
persisted verbatim and MUST NOT be recomputed from later state. A
`substitute` call without `--contract` MUST record no provenance entry for
that block.

#### Scenario: A provenanced write persists its baseline

- GIVEN `substitute intro --body b.tex --contract sections/intro.md` succeeds
- WHEN the `provenance` region is read afterward
- THEN it holds `intro`'s contract digest as measured at that write and the
  declaration generation then current

#### Scenario: Mutation 3 — a recomputed baseline is caught

- GIVEN the write path is mutated to recompute the contract digest at read
  time instead of persisting the write-time digest
- WHEN the drift-detection test runs against a contract edited after the
  write
- THEN it fails red — drift becomes structurally undetectable, which the
  test must catch

### Requirement: A Block Written Without --contract Is unprovenanced

`plan` MUST report a block with no provenance entry as `unprovenanced`. An
`unprovenanced` block MUST NOT be reported or treated as current; it is
reported as a distinct, named state, never silently assumed current.

#### Scenario: An unprovenanced block is named, not assumed current

- GIVEN block `methods` was written by a plain `substitute` with no
  `--contract`
- WHEN `plan` runs
- THEN `methods` is reported `unprovenanced`, never `current`

### Requirement: Drift Compares the Persisted Baseline Against Current Bytes

`plan` MUST compute the current sha256 of each provenanced block's recorded
contract path and compare it against the persisted write-time baseline —
never against another freshly computed digest. A mismatch MUST be reported
as drift, naming the block id, the recorded digest, and the current one.
`plan` MUST NOT rewrite any block on finding drift.

#### Scenario: A single byte edit is reported, block untouched

- GIVEN block `results` was provenanced against `sections/results.md`, and
  one byte of that file changes afterward
- WHEN `plan` runs
- THEN `results` is reported drifted, naming both digests, and its body on
  disk is byte-identical to before `plan` ran

### Requirement: Whole-File Hashing Over-Reports by Design

The contract digest MUST be computed over the entire contract file's
bytes, never per block. Editing any byte of a contract file MUST be
reported as drift for every block whose provenance names that file, even a
block whose own referenced guidance text was untouched. Under-reporting
(a real drift going unreported) MUST NOT occur; over-reporting is the
accepted, deliberate direction, because per-block delimiting inside a
hand-authored contract file is unavailable without restructuring it, and a
missed drift is a block silently standing on bytes that no longer exist.

#### Scenario: One edit flags every block of the section

- GIVEN `sections/results.md` backs two written blocks, `results-a` and
  `results-b`
- WHEN one byte of `sections/results.md` changes and `plan` runs
- THEN both `results-a` and `results-b` are reported drifted

### Requirement: plan Aggregates Registry, Declarations, and Provenance

`plan` MUST report, in one call: every `guidance/` folder's class or
`unclassified`; every declaration and fact-resolution record's fill/fixed
state; and every written block's provenance state (`current`, `drifted`,
or `unprovenanced`). `plan` MUST NOT write to `main.tex`, the declarations
region, the provenance region, or any guidance marker.

#### Scenario: plan is read-only across all three concerns

- GIVEN a repository with mixed classified/unclassified guidance folders,
  some fixed and some unfilled records, and a mix of current/drifted/
  unprovenanced blocks
- WHEN `plan` runs
- THEN it reports all three concerns in one call and no file changes

### Requirement: plan Is Registered Into paper_cli.py

`plan` MUST be added as a subcommand of `paper_cli.py`'s existing
dispatch, returning the same `{"status": "ok"|"refused", ...}` JSON shape.
Every refusal code it can raise (including `PROVENANCE_HAND_EDITED`) MUST
appear in `paper_cli.REFUSAL_CLASSIFICATION`, classified and held to the
same roster-derivation test as the other verbs.

#### Scenario: A new plan refusal is classified

- GIVEN `plan` raises `PROVENANCE_HAND_EDITED`
- WHEN the roster-derivation test runs
- THEN it is present in `REFUSAL_CLASSIFICATION`, classified `work-state`

## Acceptance Criteria

- Editing one contract byte makes `plan` name every block written against
  the old bytes, and rewrites none — proven by the whole-file scenario
  above, not asserted.
- A block written without `--contract` is reported `unprovenanced` and
  never treated as current.
- Recomputing the baseline at read time (Mutation 3) is proven to make
  drift structurally undetectable, and the guard test catches it.
- `plan` never mutates `main.tex`, any guidance marker, or either region,
  under any reported state.
