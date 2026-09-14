# Delta for implementation-document-binding

## MODIFIED Requirements

### Requirement: `cmd_verify`'s Fidelity Fold Runs Per Document, Derived From Each Document's Own Claim Vocabulary

The four-condition fidelity fold (`stale or missing_provenance or untested or
unreached`) MUST run once per declared document under `len(documents) > 1`,
each run computed against that document's own resolved claim vocabulary
(its own `claim_key`, `locus_key`, `remedy_locus_key`, `notation_keys`),
never against one list shared across every index, producing one fidelity
result per document, and MUST run exactly as before under one document. No
docstring or comment asserting these four conditions are invariant across
documents may remain once this requirement is held.
(Previously: stated the same per-document outcome without requiring
per-document derivation; the shipped engine passed identical `stale`/
`missing_provenance`/`untested`/`unreached` lists to every index beyond 0,
and `_extra_document_fidelity_status`'s own docstring called the four
conditions "document-count-invariant.")

#### Scenario: A single-document fidelity result is unchanged
- GIVEN a one-document profile
- WHEN `cmd_verify` computes fidelity
- THEN the result and its sealed digest are unchanged from before this
  capability

#### Scenario: A two-document run produces two independent fidelity results
- GIVEN a two-document profile where document 0 is stale under its own
  claim vocabulary and document 1 is clean under its own
- WHEN `cmd_verify` computes fidelity
- THEN document 1's status is unaffected by document 0's drift

#### Scenario: The inverse control also holds
- GIVEN the same profile with document 0 clean and document 1 drifted under
  its own claim vocabulary
- WHEN `cmd_verify` computes fidelity
- THEN document 0's status is unaffected by document 1's drift

#### Scenario: A fold that reuses one shared list across indices is caught
- GIVEN a mutation reverting the per-document derivation to one list shared
  across every index
- WHEN the two-document drift-control fixture (either direction) runs
- THEN the comparison against the fixture's expected independent results
  fails, naming the index whose status was wrongly shared

### Requirement: A Finding May Name Either Or Both Documents; Impact Class Is Per-Document Representation, Not Verdict

`finding_impact`'s `class` MUST become a per-document mapping under two
documents, each document's class computed using that document's own
resolved `citation_pattern` — never a single citation pattern shared across
every index — and a finding MUST be nameable against either document or
both. This capability MUST emit that mapping as representation only — it
MUST NOT compute, print, or return a single word describing what a finding
against both documents *means*; that judgment is out of scope.
(Previously: stated the per-document mapping without requiring a
per-document citation pattern; the shipped engine matched every citation
through one module-level `CITATION_RE`.)

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
