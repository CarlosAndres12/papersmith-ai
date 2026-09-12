# Delta for implementation-cli-seal

## MODIFIED Requirements

### Requirement: Non-Interference With Sibling Suites

The change MUST NOT alter either existing suite's pass/fail outcome beyond F3's
sanctioned delta. `npm test` MUST remain 595/0. The Python suite's pinned invariant
is `skipped=6` and `OK` (no failures, no errors) — `Ran`'s total count MAY grow as
tests are added by this and later cuts and MUST NOT be pinned to a fixed number.
Adding a second skill built on the shared engine MUST NOT move any of
`proposal-implementation`'s 28 sealed digests.
(Previously: stated the invariant generally; did not name a concrete addition this
cut introduces as a case the invariant must survive.)

#### Scenario: Both baselines hold
- GIVEN the change applied after this capability lands
- WHEN both suites re-run, output redirected to files
- THEN `npm test` shows 595 pass/0 fail and the Python suite shows `OK
  (skipped=6)`, with `Ran` at or above its pre-cut count

#### Scenario: `proposal-deliberation` is untouched
- GIVEN the change is scoped to `proposal-implementation`'s shared engine
- WHEN the change's diff is inspected
- THEN no file under `proposal-deliberation` is modified

#### Scenario: A `skipped` count movement is caught
- GIVEN `skipped=6` is the pinned invariant
- WHEN the Python suite runs after this capability lands
- THEN a `skipped` count other than 6 fails the assertion, distinct from `Ran`
  growing, which is expected and unasserted

#### Scenario: Shipping the second skill moves nothing in the existing 28
- GIVEN `experimental-implementation` is added under `.claude/skills/`
- WHEN `proposal-implementation`'s existing 28-case seal is re-compared to its
  committed goldens
- THEN every digest and exit status is byte-identical to its pre-addition golden

## ADDED Requirements

### Requirement: The Second Skill Ships Its Own Seal, Added Beside The Existing One

`experimental-implementation` MUST have its own committed stdout-characterization
seal, capturing digest and exit status for its own single-document corpus, added
beside `tests/seal/` rather than inside it. The existing 28-case corpus and its
goldens MUST remain untouched by this addition.

#### Scenario: The existing corpus is provably untouched
- GIVEN the second skill's own seal is added
- WHEN `git diff --exit-code tests/seal/` runs
- THEN it exits 0, both before and after the addition

#### Scenario: The second skill's own corpus is captured and digested
- GIVEN `experimental-implementation`'s single-document fixture profile and its own
  corpus
- WHEN its seal is captured
- THEN each case has a digest and exit status, or is in an explicit unsealed set
  with a reason

#### Scenario: A one-byte change in the second skill's seal is caught
- GIVEN a stored golden from the second skill's own seal
- WHEN one byte of its captured stdout is mutated and compared
- THEN the comparison goes red
