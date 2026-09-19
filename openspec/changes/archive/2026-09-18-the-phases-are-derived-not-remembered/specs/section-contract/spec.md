# Delta for Section Contract

## MODIFIED Requirements

### Requirement: Transcribed `after` Edges Only

An `after` edge MUST be admitted only when the contract's own prose states
it, verified as a literal (whitespace-collapsed, markdown-emphasis-stripped)
substring of the named `source.file`'s prose body — unchanged from before.
The edge count is no longer a fixed number: normalizing all ten contracts'
`### Internal chain` tables into transcribed edges (`internal-chain-edges`)
raises the shipped edge set well past three. What remains invariant instead:
every `after` edge, wherever declared, carries a verified, prose-backed
quote; no edge exists that is not backed by a quote (`SPAN_NOT_IN_SOURCE`
on failure); and no `### Internal chain` row is left unmapped to a backing
edge (`CHAIN_ROW_UNBACKED` on failure, per `internal-chain-edges`). A test
MUST assert both properties hold across the full shipped corpus — never a
fixed cardinality.

(Previously: asserted the shipped edge set is exactly three named edges,
which this change invalidates by construction.)

#### Scenario: Every shipped edge is quote-backed

- GIVEN the ten contracts' parsed headers, normalized under
  `contract-input-partition`
- WHEN every `after` edge, section- and block-level, is collected
- THEN each one's `source.quote` is a verified literal substring of its
  `source.file`'s prose body, with no exceptions

#### Scenario: An invented edge on a shipped contract fails

- GIVEN a shipped contract's header edited to add an `after` edge not
  backed by that contract's own prose
- WHEN the edge-set test runs
- THEN it fails, naming the untranscribed edge

#### Scenario: No internal-chain row is left unmapped

- GIVEN the ten contracts' normalized `### Internal chain` tables
- WHEN every row is checked against the collected edge set
- THEN every row maps to exactly one backing `after` edge; a row with none
  fails the test naming that row

#### Implementation note (recorded at apply, not re-opening the decision)

The `title-and-keywords` after every body-section edge remains
**position-derived**, not enumerated in `title-and-keywords`'s header and
not resolved against the `skeleton` fact — unchanged from the prior note.
This change adds no new special-cased edge of that kind; every additional
edge this change introduces is a literal, header-declared transcription
from an `### Internal chain` row, following the same discipline as the two
pre-existing literal edges.

## ADDED Requirements

### Requirement: Symmetric Optional Fork For Dataset Placement

The dataset-placement fork — whether the dataset is described in Materials
and Methods or in Experimental Setup — MUST be structurally represented on
both sides: `01-materials-and-methods.md` declares `mm-dataset`
(`optional: true`, `requires_facts: [dataset]`), and
`02-experimental-setup.md` declares a mirroring `es-dataset`
(`optional: true`, `requires_facts: [dataset]`), so `skeleton-startup`'s
disk inference has a branch to read on either side.

#### Scenario: Both sides of the fork exist in the corpus

- GIVEN the shipped corpus after this change
- WHEN `01-materials-and-methods.md` and `02-experimental-setup.md` are
  parsed
- THEN both declare an `optional: true` dataset block requiring `dataset`,
  under ids `mm-dataset` and `es-dataset` respectively

### Requirement: `mm-proposal`'s Facts Match What It Genuinely Needs

`01-materials-and-methods.md`'s `mm-proposal` block MUST declare
`requires_facts: [formulation]` only — `implementation` is dropped, since
the proposal's own formal definition needs no run-time implementation
detail to be drafted.

#### Scenario: mm-proposal no longer requires implementation

- GIVEN `01-materials-and-methods.md` as parsed after this change
- WHEN `mm-proposal`'s `requires_facts` is read
- THEN it contains `formulation` and does not contain `implementation`
