# Delta for implementation-cli-seal

## MODIFIED Requirements

### Requirement: Corpus Coverage By Construction

The corpus MUST provably exercise: all 14 provenance sites; all 14 findings
sites (populated `tests/findings.py`: `remedy_block`, `adoption`, `uses`,
`introduces`); the 5 hardcoded-path refusals with and without
`IMPLEMENTATION_PROPOSALS`; `Data/` present and absent, crossed with a
document declaring a dataset and a document declaring none (the
declared/undeclared axis); a marker-owned and a hand-authored revision
family; a tie.
(Previously: `Data/` present and absent was a single axis, with no case
distinguishing a declared-dataset document from one declaring none.)

#### Scenario: Coverage is asserted

- GIVEN the corpus
- WHEN a coverage test runs
- THEN it confirms every site above is reached by at least one case,
  including all four combinations of the `Data/`-presence ×
  dataset-declared axis

#### Scenario: A dropped case is caught

- GIVEN a corpus case covering one refusal's `IMPLEMENTATION_PROPOSALS` state
  is removed
- WHEN the coverage test runs
- THEN it fails, naming the uncovered site

#### Scenario: A dropped declared/undeclared case is caught

- GIVEN the corpus case exercising a dataset-declared document with `Data/`
  absent is removed
- WHEN the coverage test runs
- THEN it fails, naming that uncovered combination

## ADDED Requirements

### Requirement: The Required Leaf's One-Line Sibling Cost Is A Declared, Bounded Exception

`proposal-implementation/impl_profile.py` MUST gain exactly one line per
`documents[N]` entry declaring `dataset_marker: None`, and this is the only
sanctioned edit to the sibling's tree under this capability. The bar this
capability is held to is no longer `git diff --name-only … → 0 files` on
that tree; it is that `tests/seal/`'s 28 digests stay byte-identical,
`npm test` stays 595/595, and the Python suite stays `OK (skipped=6)`.

#### Scenario: The one declared line does not move a digest

- GIVEN `proposal-implementation/impl_profile.py` with its `dataset_marker:
  None` line added
- WHEN `tests/seal/`'s 28-case corpus re-runs
- THEN `git diff --exit-code tests/seal/` exits 0

#### Scenario: Every other sibling directory stays at zero files

- GIVEN this capability's complete diff
- WHEN every path under `proposal-implementation/` other than
  `impl_profile.py` is inspected
- THEN none of them appear in the diff

### Requirement: The Second Skill's Own Seal Gains The Dataset-Declared/Undeclared Axis, Read Before Accepted

`tests/experiments_seal/` MUST add cases exercising `documents[0]`'s real
declared dataset marker present and absent in its bound document's bytes,
crossed with `Data/` present and absent. Digests in this corpus MAY move
when this capability's behavior legitimately changes; each moved digest
MUST be read and accepted by hand before being committed, never regenerated
in bulk. `tests/seal/`'s existing 28 digests remain untouched by this
addition.

#### Scenario: A new declared-dataset case is captured and its digest accepted by hand

- GIVEN `documents[0]`'s real dataset marker landed and a corpus case
  exercising `Data/` absent for that same document
- WHEN the second skill's seal is captured
- THEN the new case has a digest, and its content was read before being
  committed

#### Scenario: The sibling's 28 are unaffected by the new axis

- GIVEN the dataset axis added to `tests/experiments_seal/`
- WHEN `git diff --exit-code tests/seal/` runs
- THEN it exits 0
