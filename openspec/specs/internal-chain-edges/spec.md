# Internal Chain Edges Specification

## Purpose

A row in a contract's `### Internal chain` table (`contract-input-partition`)
is a claim about a real graph dependency. This capability closes the gap
between the claim and the graph: every internal-chain row MUST correspond to
a quote-anchored `after` edge the graph actually carries. No persisted
second copy of this data is created — the graph is re-derived and
re-verified from the contracts' own prose on every call, reusing `after`,
`_resolve_target`, and `_verify_after_transcription` unchanged.

## Requirements

### Requirement: Every Internal-Chain Row Has A Backing Edge

For every internal-chain row transcribed under `contract-input-partition`,
an `after` edge MUST exist in the block graph whose `(before, after)` pair
matches the row's own dependency, quote-anchored per `section-contract`'s
transcription discipline. A row with no backing edge MUST refuse
`CHAIN_ROW_UNBACKED` naming the row's holder block and its named dependency.

#### Scenario: A backed row is accepted

- GIVEN `sections/06-introduction.md` block-3's internal-chain row naming
  `related-work` as a dependency, and the existing `after: [related-work]`
  edge on that same block
- WHEN the graph is assembled and checked against the internal-chain table
- THEN the row is accepted with no refusal

#### Scenario: An unbacked row refuses

- GIVEN a contract whose `### Internal chain` table names a dependency on a
  sibling block, but whose header carries no matching `after` edge for that
  pair
- WHEN the graph is assembled and checked against the internal-chain table
- THEN it refuses `CHAIN_ROW_UNBACKED` naming the holder block and the
  missing dependency

### Requirement: No Silent Drop On Transcription

The reader MUST check every internal-chain row before the graph is used for
order, readiness, or verification — it MUST NOT skip, ignore, or continue
past a row it cannot back with an edge.

#### Scenario: One missing edge among many stops the run

- GIVEN a corpus whose internal-chain tables together name ten dependencies,
  nine of which have backing `after` edges and one of which does not
- WHEN the graph is assembled
- THEN it refuses `CHAIN_ROW_UNBACKED` for the one missing edge, and no
  writing order or readiness report is produced from a graph missing that
  edge

#### Scenario: Mutation — deleting a backing edge is caught

- GIVEN a contract whose internal-chain row was backed by a transcribed
  `after` edge, with that edge then removed from the header while the
  internal-chain row is left unchanged
- WHEN the graph is assembled
- THEN it refuses `CHAIN_ROW_UNBACKED`, proving the check reads the live
  edge set rather than a cached result from the row's earlier presence
