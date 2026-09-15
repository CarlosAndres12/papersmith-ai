# Deliberation Change Header Specification

## Purpose

`CREATE_SUCCESSOR` needs a mandatory record of what changed and why between
revisions. `COMPOSITE_UNTOUCHED_INVARIANT` requires every byte outside the
resolved loci to stay identical between source and candidate, and a header
written into the document body is exactly such a byte. **The placement
mechanism is an open design question** (three candidate resolutions in
`proposal.md`); this spec fixes what must hold regardless of which is chosen,
and marks the placement mechanism itself as pending.

## Requirements

### Requirement: `CREATE_SUCCESSOR` requires a change summary

`CREATE_SUCCESSOR` MUST require a `changeSummary: { what, why }` argument.
Its absence MUST be refused with `CHANGE_SUMMARY_REQUIRED`.

#### Scenario: Missing change summary is refused

- GIVEN a `CREATE_SUCCESSOR` call omitting `changeSummary`
- WHEN the call is processed
- THEN it is refused with `CHANGE_SUMMARY_REQUIRED`
- AND no successor is published

#### Scenario: Present change summary is accepted

- GIVEN a call including `changeSummary: { what, why }` with both fields
  non-empty, and otherwise valid
- WHEN the call is processed
- THEN the successor publishes, carrying the change summary content
  (exact placement per the resolution below)

### Requirement: `COMPOSITE_UNTOUCHED_INVARIANT` MUST NOT be weakened by the header mechanism

Whichever placement resolution design selects, every byte outside the header's
own declared locus or exemption MUST still be checked against the invariant
exactly as before this change. **STATUS: the placement mechanism itself is
UNRESOLVED pending `sdd-design`** — this requirement specifies the constraint
that binds under any of the three candidate resolutions named in
`proposal.md` (receipt/sidecar only; own resolved locus; narrow declared
prefix exemption).

#### Scenario: Resolution (a) — header lives outside the document

- GIVEN resolution (a) is chosen
- WHEN a successor with `changeSummary` is published
- THEN no byte of the `.md` document changes as a side effect of the header
- AND the header content is retrievable from the receipt or sidecar

#### Scenario: Resolution (b) — header is its own resolved locus

- GIVEN resolution (b) is chosen
- WHEN a successor with `changeSummary` is published
- THEN the header locus's byte span is the only one patched for the header
- AND `COMPOSITE_UNTOUCHED_INVARIANT` is checked over every byte outside it,
  unchanged from today's enforcement scope

#### Scenario: Resolution (c) — narrow declared exemption

- GIVEN resolution (c) is chosen
- WHEN a successor with `changeSummary` is published
- THEN only the declared exempted prefix span may change
- AND every other byte is still checked against the invariant

#### Scenario: Invariant enforcement is unchanged when unused

- GIVEN a profile or call that does not exercise the change-header path
- WHEN a successor is published
- THEN `COMPOSITE_UNTOUCHED_INVARIANT` enforcement is byte-identical to
  pre-change behavior

## Acceptance Criteria

- This capability MUST NOT ship until the design phase records which of (a),
  (b), (c) is selected, with evidence.
- Whichever is selected, a fixture MUST prove the invariant still refuses an
  out-of-scope byte change elsewhere in the document.
