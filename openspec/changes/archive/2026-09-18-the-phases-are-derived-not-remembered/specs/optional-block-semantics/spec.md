# Optional Block Semantics Specification

## Purpose

`optional` is already parsed onto every block and stored in the graph, but
read by no consumer. This capability gives it real effect in the three
places that need to distinguish "not yet satisfied" from "this branch of a
fork was never taken": wave gating, per-block readiness, and coupling
verification.

## Requirements

### Requirement: Optional Blocks Do Not Gate Wave Progression

In `writing-phases`' phase gating, an unwritten block declaring
`optional: true` MUST NOT block the start of the next wave. Only an
unwritten `optional: false` (or absent) block does.

#### Scenario: An unwritten optional block does not block the next wave

- GIVEN wave 1 holding one written non-optional block and one unwritten
  `optional: true` block (for example `es-dataset` when the dataset lives
  in Materials and Methods)
- WHEN `write` is invoked on a wave-2 block
- THEN phase gating raises no refusal

#### Scenario: An unwritten non-optional block still blocks

- GIVEN the same wave 1, with its non-optional block now also unwritten
- WHEN `write` is invoked on a wave-2 block
- THEN it refuses `PHASE_NOT_READY` naming the unwritten non-optional block,
  regardless of the optional block's state

### Requirement: Readiness Reports The Optional Flag

Per-block readiness MUST include `optional`, read verbatim from the block's
own declaration, in every block's report, alongside `status`,
`missing_facts`, and `missing_declarations`.

#### Scenario: The optional flag is read verbatim

- GIVEN readiness computed over the shipped corpus
- WHEN `mm-dataset`'s and `es-assessment`'s entries are read
- THEN `mm-dataset` reports `optional: true` and `es-assessment` reports
  `optional: false`

### Requirement: Verify Excuses An Unopened Optional Block

A coupling check whose required evidence comes from a block declaring
`optional: true` that was never opened in `main.tex` MUST report
`unmeasured`, with reason `OPTIONAL_BLOCK_ABSENT`, and MUST NOT report
`fail` for that block's absence. A block declaring `optional: true` that WAS
opened MUST be checked exactly like any other opened block — `optional`
excuses non-existence, never abandonment once opened.

#### Scenario: An unopened optional block reports unmeasured, not fail

- GIVEN `mm-dataset` declared `optional: true` and never opened, because
  the dataset lives in `es-dataset` instead
- WHEN `verify` runs a coupling depending on `mm-dataset`'s content
- THEN it reports `unmeasured` with reason `OPTIONAL_BLOCK_ABSENT`, never
  `fail`

#### Scenario: An opened optional block is checked normally

- GIVEN `mm-dataset` declared `optional: true`, opened, and left unwritten
  past its own wave
- WHEN `verify` runs a coupling depending on `mm-dataset`'s content
- THEN it reports the same outcome an opened non-optional block in the same
  state would report, never `unmeasured` for the sole reason that the block
  is optional
