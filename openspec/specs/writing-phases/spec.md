# Writing Phases Specification

## Purpose

`derive_order` already produces one flattened total order over the block
graph. This capability groups that same graph into Kahn frontier waves
1..N — every wave the set of blocks ready at that round — so a phase plan
can be approved once and gated sequentially, instead of the writer treating
a flat 43-block list as one undifferentiated queue.

## Requirements

### Requirement: Wave Grouping Is Frontier-Based

The block graph (`corpus`, `edge_set` from `paper_graph.collect_edges`) MUST
also be reportable as waves 1..N, each wave the set of blocks whose
in-degree in the residual graph reaches zero at that Kahn round, tie-broken
the same way `derive_order` tie-breaks (`position`, `block_index`,
`qualified_id`). Flattening the waves in order MUST reproduce exactly the
node set `derive_order` returns, with no block omitted or duplicated across
waves, and every edge `(before, after)` MUST cross a wave boundary: the
wave index of `before` MUST be strictly less than the wave index of
`after`. A cyclic graph MUST refuse `ORDER_CYCLE`, the same refusal
`derive_order` already raises, naming the participating blocks.

#### Scenario: Waves partition the full node set

- GIVEN the shipped ten-contract corpus and its collected edge set
- WHEN waves are computed
- THEN every block appears in exactly one wave, and the union of all waves
  equals the full set of blocks `derive_order` orders

#### Scenario: An edge never lands inside one wave

- GIVEN a block A with an `after` edge naming block B (B is written after A)
- WHEN waves are computed
- THEN A's wave index is strictly less than B's wave index

#### Scenario: A cyclic graph still refuses under wave computation

- GIVEN two blocks whose `after` edges each name the other
- WHEN waves are computed
- THEN it refuses `ORDER_CYCLE` naming both blocks

### Requirement: Phase N Is Gated On Phase N-1

The skill MUST NOT begin writing any block of wave N while wave N-1
contains an unwritten, non-`optional` block. An attempt to do so MUST
refuse `PHASE_NOT_READY`, naming the blocking wave-(N-1) block.

#### Scenario: A later wave is refused while an earlier one is incomplete

- GIVEN a two-wave plan where wave 1 holds one non-optional block that is
  not yet written
- WHEN `write` is invoked on a wave-2 block
- THEN it refuses `PHASE_NOT_READY` naming the unwritten wave-1 block

#### Scenario: A later wave proceeds once the earlier one is complete

- GIVEN the same two-wave plan, with wave 1's block now written
- WHEN `write` is invoked on the same wave-2 block
- THEN phase gating raises no refusal and the pipeline proceeds

### Requirement: The Operator Approves The Phase Plan Before Writing Starts

The skill MUST present the full wave plan — wave count and the blocks in
each wave — to the operator, and MUST NOT begin writing any block until the
operator has explicitly approved that plan.

#### Scenario: Writing does not start on an unapproved plan

- GIVEN a freshly computed wave plan that has not been approved
- WHEN the skill is asked to begin writing
- THEN it does not invoke `write` on any block and instead reports the plan
  awaiting approval
