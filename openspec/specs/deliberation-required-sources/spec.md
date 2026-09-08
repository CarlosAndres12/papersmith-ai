# Deliberation Required Sources Specification

## Purpose

A domain layer may depend on read-only reference sources loaded once before
the first revision renders. Today an absent source silently returns nothing.
A layer whose sources are load-bearing (a data paper as a hard ceiling on
claims) needs an absent *required* source to block, not to be silently
ignored.

## Requirements

### Requirement: Sources are declared with a required flag

The profile MUST declare `sources: readonly { path, required }[]`. The
fragment loader MUST read this list instead of a single hardcoded path.

#### Scenario: A declared, present source loads as before

- GIVEN a profile declaring one source whose path exists on disk
- WHEN `CREATE_INITIAL_REVISION` runs
- THEN its fragments are loaded and injected into v1 exactly as today

### Requirement: A missing required source refuses initial revision creation

`CREATE_INITIAL_REVISION` MUST fail with `REQUIRED_SOURCE_MISSING` when any
source declared `required: true` is absent from disk. No v1 MUST be rendered
in that case.

#### Scenario: Missing required source blocks the draft

- GIVEN a profile declaring a source with `required: true` whose path is
  absent
- WHEN `CREATE_INITIAL_REVISION` runs
- THEN it fails with `REQUIRED_SOURCE_MISSING`
- AND no v1 document is created

### Requirement: A missing optional source preserves today's silence

A source declared `required: false` that is absent MUST NOT block revision
creation and MUST NOT be reported as an error, preserving
`proposal-deliberation`'s current behavior exactly.

#### Scenario: proposal-deliberation's guide remains optional

- GIVEN `proposal-deliberation`'s profile declares `guidance/paper-guide` with
  `required: false`, and that path is absent
- WHEN `CREATE_INITIAL_REVISION` runs
- THEN v1 renders silently, with no fragments injected and no refusal —
  identical to pre-change behavior

#### Scenario: Multiple sources, one required and missing

- GIVEN a profile declaring two sources, one `required: true` (absent) and one
  `required: false` (present)
- WHEN `CREATE_INITIAL_REVISION` runs
- THEN it fails with `REQUIRED_SOURCE_MISSING`, regardless of the second
  source's presence

## Acceptance Criteria

- Both the refusal path (required + absent) and the silent path (optional +
  absent) are exercised by fixtures.
- `proposal-deliberation`'s existing behavior with its guide absent is proven
  unchanged.
