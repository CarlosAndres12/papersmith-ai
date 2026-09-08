# Deliberation Reference Integrity Specification

## Purpose

Reference resolution — what a document declares as a numbered/named thing,
and what cites it — must be a profile-declared vocabulary, not a hardwired
`\label`/`\tag`/`\eqref`/`(Ec. N)` assumption. On a document with no
declarations and no citations, the check must say so rather than report a
silent pass.

## Requirements

### Requirement: References are profile-declared, not hardwired

`profile.references.{declares, cites}` MUST replace the hardwired
`\label`/`\tag`/`\eqref` and `(Ec. N)` checks in `candidate-validator.ts`,
`reference-index.ts`, and `document-index.ts`. Each profile declares what
counts as a declaration and what counts as a citation of one.

#### Scenario: Mathematical profile behavior is preserved

- GIVEN `proposal-deliberation`'s profile declares `\tag{N}` as `declares` and
  `(Ec. N)` as `cites`
- WHEN a math document with matched tags and citations is validated
- THEN the reported resolution is byte-identical to pre-change behavior

### Requirement: Reference integrity has no vacuous pass

A document with zero declared and zero cited items per the active profile
MUST be distinguishable from a document whose declarations and citations were
checked and found consistent.

#### Scenario: A genuine unresolved citation is caught

- GIVEN a fixture document declaring one numbered item and citing a second,
  undeclared item, per the active profile's vocabulary
- WHEN the candidate is validated
- THEN the check reports the unresolved citation as a violation

#### Scenario: Empty declares/cites reported as not-applicable

- GIVEN a document with zero items matching the profile's `declares` pattern
  and zero matching `cites`
- WHEN the candidate is validated
- THEN the reference-integrity result MUST be reported as "not applicable"
- AND MUST NOT be reported using the same shape as a confirmed-consistent pass

#### Scenario: A duplicate declaration is still caught

- GIVEN a fixture declaring the same numbered item twice per the profile's
  `declares` pattern
- WHEN validated
- THEN the check reports the duplicate as a violation, unchanged from today's
  uniqueness behavior generalized to the profile vocabulary

## Acceptance Criteria

- A fixture with genuinely resolvable and genuinely unresolvable references
  exists for at least one non-mathematical vocabulary shape, proving the check
  is exercised beyond the math profile's own tests.
- `npm test` baseline holds for the mathematical profile.
