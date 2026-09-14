# Delta for implementation-document-binding

## MODIFIED Requirements

### Requirement: A Finding May Name Either Or Both Documents; Impact Class Is Per-Document Representation, Not Verdict

`finding_impact`'s `class` MUST become a per-document mapping under two
documents, each document's class computed using that document's own
resolved `citation_pattern` — never a single citation pattern shared
across every index — and a finding MUST be nameable against either
document or both. This capability MUST emit that mapping as
representation only — it MUST NOT compute, print, or return a single word
describing what a finding against both documents *means*; that judgment
is out of scope. This mapping now has its first real consumer
(`cmd_handoff`'s routing and `cmd_verify`'s local-remedy comprehension,
both taught to read the mapping instead of comparing a scalar); gaining a
consumer does not turn the mapping itself into a verdict — the consumer
decides what to do with each document's class, this capability still
returns only the per-document representation.
(Previously: stated the per-document mapping without requiring a
per-document citation pattern, and without any call site actually reading
it — `cmd_handoff` and `cmd_verify`'s fourth comparison still compared
`impact["class"] == "local"` against what was, until this change, always
a bare string, so every finding against a mapping silently fell to
`False`.)

#### Scenario: A finding against one document maps to that document alone
- GIVEN a two-document profile and a finding naming only the first document
- WHEN `finding_impact` computes its class
- THEN the returned mapping carries a class for that document only

#### Scenario: A finding against both documents carries both classes, uninterpreted
- GIVEN a two-document profile and a finding naming both documents
- WHEN `finding_impact` computes its class
- THEN the returned mapping carries one class per named document, with no
  combined or summarized verdict

#### Scenario: Each named document's citations are matched by its own pattern
- GIVEN a two-document profile where document 0 and document 1 declare
  different `citation_pattern` values
- WHEN `finding_impact` computes classes for a finding naming both
- THEN document 0's class is derived using document 0's own pattern and
  document 1's using its own, never cross-applied

#### Scenario: `cmd_handoff` routes a finding against both documents without silently deferring
- GIVEN a finding naming both documents, each resolving to `"local"`
- WHEN `cmd_handoff` computes routing
- THEN it recognizes the mapping's per-document classes and routes the
  finding, rather than comparing the mapping to the string `"local"` and
  falling to `deferToOwnSession` by default

#### Scenario: `cmd_verify`'s local-remedy comprehension reads the mapping too
- GIVEN a finding whose class mapping reports `"local"` for the document
  it names
- WHEN `cmd_verify` computes `local_remedies_not_written`
- THEN the finding is included on the same evidence `cmd_handoff` now
  uses, not silently excluded by a scalar comparison

#### Scenario: A comparison reverted to a bare scalar check is caught
- GIVEN a mutation reverting any of the four consumer comparisons back to
  `impact["class"] == "local"` against the mapping itself
- WHEN the two-document corpus case naming a `"local"`-classed finding runs
- THEN that finding is silently excluded again, and the corpus case fails,
  naming the reverted comparison

## Boundary (unchanged, discharged elsewhere)

The cross-document agreement verdict — what it means for the two
documents to disagree, and what a discrepancy prints — remains outside
this capability, exactly as before: this capability still computes no
verdict and never did. `implementation-cross-document-agreement` is the
sibling capability this change adds to discharge that boundary; it is
gated separately (it fires only when a discrepancy between the two
documents' own declared/cited claims is detected, not merely because two
documents are declared), and it does not change what this capability
itself returns.
