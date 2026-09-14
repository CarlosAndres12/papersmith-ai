# Delta for implementation-cli-seal

## ADDED Requirements

### Requirement: The Per-Document Vocabulary Fold Is Sealed By A Drift-Control Fixture

A committed two-document corpus fixture, where document 0's own claim
vocabulary and text are clean while document 1's own claim vocabulary names
a genuinely drifted module, MUST be captured and digested, proving
`fidelityByDocument`'s fold reflects only its own document's four
conditions. The inverse arrangement (document 0 drifted, document 1 clean)
MUST also be captured, as the control proving the fold is not merely
reporting document 0's status twice. The existing 28-case corpus under
`tests/seal/` MUST remain untouched by this addition.

#### Scenario: A clean document 0 beside a drifted document 1 is captured
- GIVEN the drift-control fixture with document 0 clean and document 1
  drifted
- WHEN the two-document seal captures it
- THEN document 0's fidelity status is unaffected and document 1's reports
  drift, both digested

#### Scenario: The inverse control is captured
- GIVEN the same fixture family with document 0 drifted and document 1
  clean
- WHEN the two-document seal captures it
- THEN document 0's fidelity status reports drift and document 1's is
  unaffected, both digested

#### Scenario: The existing 28 remain untouched
- GIVEN the drift-control fixture added alongside `tests/seal/`
- WHEN `git diff --exit-code tests/seal/` runs
- THEN it exits 0

### Requirement: A Declared Second Document's Own Vocabulary Is Exercised, Not Only Its Directory And Label

At least one sealed two-document case MUST exercise a document declaring
its own per-document `claim_key`/`locus_key`/`remedy_locus_key`/
`notation_keys`/`citation_pattern`, distinct from the other document's, so
the seal proves the declared vocabulary is read and threaded — not merely
that a second `documents` entry with its own directory and label resolves.

#### Scenario: A per-document vocabulary difference is observable in the captured output
- GIVEN a two-document fixture where document 1 declares its own citation
  pattern and notation keys, different from document 0's
- WHEN a case touching a citation or notation payload is captured
- THEN the captured output reflects document 1's own declared values for
  document 1, and document 0's own for document 0


## Correction after verify (W1): captured, not digested

The requirement above says the drift-control fixture is "captured and digested",
and the two scenarios say "both digested". **No seal or digest artifact exists
for it, and none should.**

What was built proves the same property by real-subprocess assertion in
`TwoDocumentDriftControlTests`, which is what design.md's own Testing Strategy
classifies it as -- **Integration**, never a planned digest capture. The
implementation matches the design; this spec's wording matched neither.

The distinction is not cosmetic here. A digest proves *these exact bytes did not
move*; an assertion proves *this document's status differs from that one's*. The
drift control needs the second: its whole point is that document 0 stays clean
while document 1 drifts, and a digest of that pair would freeze a difference
rather than demonstrate one. Wording corrected to the mechanism that was built
and is proven, rather than the mechanism the sentence happened to name.
