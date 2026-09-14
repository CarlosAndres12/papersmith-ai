# Citation Validation Specification

## Purpose

The verdict, decided by execution against a stored verbatim span, and the bounded
search loop that never lets a half-cited block reach disk.

## Requirements

### Requirement: Three Verdicts, `insufficient` Is Not Lenient

Validation MUST return exactly one of `holds`, `does-not-hold`, or `insufficient`.
`insufficient` MUST fail the citation and consume a search-round iteration exactly as
`does-not-hold` does — it MUST NOT be treated as a soft `holds` anywhere in the
pipeline.

#### Scenario: A genuinely supported citation holds

- GIVEN a claim↔source record whose verbatim span supports the claim text
- WHEN it is validated
- THEN the verdict is `holds`

#### Scenario: A planted false citation is rejected

- GIVEN a claim↔source record whose verbatim span does not support the claim text
- WHEN it is validated
- THEN the verdict is `does-not-hold`, observed by executing the validator

#### Scenario: Insufficient consumes an iteration like a failure

- GIVEN a record classified `insufficient` (see `evidence-set`'s spanless-record
  rule)
- WHEN it is counted against the block's search-round budget
- THEN it consumes one round exactly as a `does-not-hold` verdict would

### Requirement: The Verdict Is Decided Against the Stored Span

A verdict of `holds` or `does-not-hold` MUST cite the exact stored verbatim span it
was decided against. A verdict produced with no span reference MUST be `insufficient`
by construction, never `holds` or `does-not-hold`.

#### Scenario: A holds verdict carries its span

- GIVEN a `holds` verdict
- WHEN the verdict record is inspected
- THEN it references the exact verbatim span it was decided against

### Requirement: Three Search Rounds Per Block, Then Exhaustion

Each block MUST be allowed at most three search rounds to find support for its
claims. On exhaustion, the system MUST refuse `EVIDENCE_EXHAUSTED`, naming the
specific claims that found no support, and the block MUST NOT be written to
`paper/main.tex`.

#### Scenario: A block resolves within budget

- GIVEN a block whose claims all reach `holds` within two search rounds
- WHEN the block is finalized
- THEN it is written, having used at most three rounds

#### Scenario: Exhaustion blocks the write

- GIVEN a block with one claim that remains `does-not-hold` or `insufficient` after
  three search rounds
- WHEN the block is finalized
- THEN it refuses `EVIDENCE_EXHAUSTED`, names that claim, and the block is not
  written — no half-cited block reaches disk
