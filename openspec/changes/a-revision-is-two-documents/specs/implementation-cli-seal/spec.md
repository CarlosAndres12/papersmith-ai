# Delta for implementation-cli-seal

## MODIFIED Requirements

### Requirement: Non-Interference With Sibling Suites

The change MUST NOT alter either existing suite's pass/fail outcome beyond
F3's sanctioned delta. `npm test` MUST remain 595/0. The Python suite's
pinned invariant is `skipped=6` and `OK` (no failures, no errors) — `Ran`'s
total count MAY grow as tests are added by this and later cuts and MUST NOT
be pinned to a fixed number.

(Previously: pinned both `Ran 2849` and `skipped=6`. `Ran` was already stale
at `f4e9960` (`Ran 2874`), so the exact-count pin broke on ordinary test
growth across cuts while `skipped=6` held across all three. This corrects
the spec to the invariant that actually survived measurement.)

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
- THEN a `skipped` count other than 6 fails the assertion, distinct from
  `Ran` growing, which is expected and unasserted

## ADDED Requirements

### Requirement: The Two-Document Branch Is Sealed By Its Own Corpus, Separate From The Existing 28

A fixture profile declaring two documents, exercised against a corpus of its
own, MUST capture byte-exact stdout and exit status for every pair-shaped
branch this change introduces, digested and committed the same way as the
existing 28-case corpus. The existing single-document corpus under
`tests/seal/` MUST remain untouched by this addition — `git diff --exit-code
tests/seal/` MUST exit 0 both before and after the two-document corpus is
added.

#### Scenario: The existing 28 digests are unaffected by the new corpus existing
- GIVEN the two-document corpus added alongside `tests/seal/`
- WHEN `git diff --exit-code tests/seal/` runs
- THEN it exits 0 — no existing digest moved

#### Scenario: A pair-shaped branch is captured and digested
- GIVEN the two-document fixture profile and its corpus
- WHEN the two-document seal is captured
- THEN each pair-shaped case has a digest and exit status, or is in an
  explicit unsealed set with a reason

#### Scenario: A one-byte change in a pair-shaped case is caught
- GIVEN a stored two-document golden
- WHEN one byte of its captured stdout is mutated and compared
- THEN the comparison goes red
