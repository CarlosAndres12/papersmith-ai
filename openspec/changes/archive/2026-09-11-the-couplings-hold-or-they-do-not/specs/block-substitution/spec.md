# Delta for Block Substitution

## ADDED Requirements

### Requirement: verify Verb Is Registered And Read-Only

The system MUST register a `verify` verb inside the existing `paper_cli.py`
front door alongside `scaffold`, `status`, `open`, `substitute`. `verify`
MUST NOT write any byte to `paper/main.tex` or to any file under `paper/`,
under any input, including every refusal path (`DECLARATION_RECORD_ABSENT`,
`CONTRACT_RECORD_ABSENT`, `PAPER_ABSENT`). Exit `0` for any verdict,
findings and `unmeasured` entries included; exit `2` only for inability to
look. No engine change to `open`/`substitute`/`status` accompanies this
addition.

#### Scenario: A full run leaves main.tex untouched

- GIVEN a well-formed `paper/main.tex` with a complete declarations and
  provenance region
- WHEN `verify` runs to completion, findings included
- THEN every byte of `main.tex` is identical before and after, and exit
  code is `0`

#### Scenario: A refusal path also writes nothing

- GIVEN `paper/main.tex` carries no declarations region
- WHEN `verify` runs and refuses `DECLARATION_RECORD_ABSENT`
- THEN `main.tex` bytes are unchanged and exit code is `2`

#### Scenario: Existing verbs are unaffected

- GIVEN the same fixture used by `scaffold`, `status`, `open`, `substitute`
  tests
- WHEN those verbs run exactly as before this change
- THEN their behavior, refusal codes and byte-identity guarantees are
  unchanged
