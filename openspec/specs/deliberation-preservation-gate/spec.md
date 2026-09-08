# Deliberation Preservation Gate Specification

## Purpose

The preservation gate — extract atoms that must not vanish silently, report
loss on preview, refuse accept until each loss is acknowledged — is the
engine's best mechanic and it is domain-neutral by construction. Its atom
extractor and rule set must come from the profile, not from a math-specific
module, and the old wire-field names must keep working forever.

## Requirements

### Requirement: Preservation machinery is domain-neutral

`math-integrity.ts` becomes `preservation.ts`. The `atoms`/`delta`/`violations`
machinery MUST be domain-neutral, sourcing its atom extractor and rule set from
`profile.preservation.{extractAtoms, violations}`. The mathematical extractor
and rule set MUST ship as `proposal-deliberation/preservation-math.ts`, wired
through that profile.

#### Scenario: Mathematical profile behavior is preserved by construction

- GIVEN `proposal-deliberation`'s profile wires `preservation-math.ts` as its
  `extractAtoms`/`violations` implementation
- WHEN a math document is previewed and validated
- THEN atoms extracted, deltas reported, and violations raised are
  byte-identical to pre-change behavior

### Requirement: The preservation gate never passes vacuously

A check that finds zero atoms to protect MUST NOT be reported the same way as
a check that found atoms and confirmed none were lost. The distinction MUST be
observable to the caller.

#### Scenario: Genuine loss is caught

- GIVEN a profile-supplied extractor that recognizes atoms in a fixture
  document
- WHEN a candidate successor drops one recognized atom
- THEN `preservationDelta` reports it as lost, and accept is refused until it
  is acknowledged by id

#### Scenario: Empty extraction is reported as not-applicable, not as a pass

- GIVEN a document from which the profile's extractor recognizes zero atoms
- WHEN the preservation check runs
- THEN the result MUST be reported as "not applicable" (no atoms extracted)
- AND MUST NOT be reported using the same shape as a genuine pass with atoms
  confirmed intact

### Requirement: Legacy wire-field names remain permanent accepted aliases

`mathDelta` and `acknowledgedMathRemovals` MUST remain accepted, permanently,
as input and output aliases for `preservationDelta` and `acknowledgedRemovals`
respectively. This alias contract exists so the mathematical SKILL.md never
needs an edit.

#### Scenario: Legacy input alias is accepted

- GIVEN a caller submits `acknowledgedMathRemovals` in an accept request
- WHEN the engine processes the request
- THEN it is treated identically to submitting `acknowledgedRemovals`

#### Scenario: Legacy output alias is present in responses

- GIVEN a preview response is generated for any profile
- WHEN the response is serialized
- THEN it MUST include `mathDelta` populated identically to `preservationDelta`,
  alongside the new field name

## Acceptance Criteria

- A fixture with recognized atoms proves the gate can catch a genuine loss
  (change 4's no-vacuous-pass requirement).
- Both `mathDelta`/`preservationDelta` and
  `acknowledgedMathRemovals`/`acknowledgedRemovals` are exercised by tests in
  both directions.
- `npm test` baseline (386/0) holds unchanged for the mathematical profile.
