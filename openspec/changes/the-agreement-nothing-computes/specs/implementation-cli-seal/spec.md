# Delta for implementation-cli-seal

## ADDED Requirements

### Requirement: `compose` And `admit` Leave The Unsealed Set

Once `implementation-block-locator` resolves correctly for a document
declaring `\tag{}`-shaped entries (this domain's `documents[1]`, the
mathematical proposal), `compose` and `admit` MUST be removed from
`tests/experiments_seal/unsealed.json` and become sealed cases with their
own digests — their prior exclusion (`design.md D8/D11`: "this domain does
not build a locator for the shape it does not have") no longer holds once
a locator is declared.

#### Scenario: `compose` and `admit` are no longer in the unsealed set
- GIVEN this capability landed
- WHEN `tests/experiments_seal/unsealed.json` is read
- THEN it contains neither `compose` nor `admit`

#### Scenario: Both have digests like every other sealed command
- GIVEN the second skill's seal is recaptured
- WHEN `compose`'s and `admit`'s cases run
- THEN each has a digest and exit status, not an unsealed-set entry

### Requirement: Every Digest That Moves When The Locator Starts Matching Is Individually Read Before Acceptance

`verify-a`/`verify-b` were previously sealed against a locator (`TAG_RE`)
that matched nothing in this domain's document, so every declared locus
read as `unknown_loci`. Once the locator resolves correctly, these
digests — and any other case whose output changes because loci now
resolve — MUST be recaptured, and each moved digest MUST be read and
defended by hand in the verify report before being committed, mirroring
the discipline already exercised on 6 of 20 cases moved by a prior slice.
Bulk regeneration without individual review MUST NOT be treated as
acceptance.

#### Scenario: A moved digest is named and its content read
- GIVEN `verify-a`/`verify-b` move because the locator now finds real
  tags instead of reporting every locus as unknown
- WHEN the verify report is written
- THEN it names each moved case and states what the new output shows,
  before the new digest is committed

#### Scenario: A digest regenerated without individual review is caught
- GIVEN a bulk regeneration that updates every digest without any moved
  case being named or read
- WHEN the verify report is checked against the moved-digest list
- THEN the gap is caught — a moved digest with no accompanying reading is
  not an accepted seal

### Requirement: The Crossing Check's Refusals Are Added As Their Own Sealed Cases

`implementation-cross-document-agreement`'s two refusal kinds, the
no-crossing-declared refusal, and the per-discrepancy acknowledgment MUST
each be exercised by at least one case in the second skill's seal,
digested and committed the same way as every other sealed case.

#### Scenario: Each new refusal kind has a sealed case
- GIVEN the crossing check's refusal kinds
- WHEN the second skill's seal is captured
- THEN each kind has at least one case with its own digest

### Requirement: The Sibling's 28 Digests Remain Untouched

`tests/seal/`'s existing 28-case corpus MUST be byte-identical after this
capability lands, exactly as every prior addition to
`tests/experiments_seal/` has left it.

#### Scenario: The sibling's seal is unaffected
- GIVEN this capability's complete diff
- WHEN `git diff --exit-code tests/seal/` runs
- THEN it exits 0

#### Scenario: Both suite baselines hold
- GIVEN this capability applied
- WHEN both suites re-run
- THEN `npm test` remains 595/0 and the Python suite remains `OK
  (skipped=6)`, with `Ran` at or above its pre-capability count
