# Writing Readiness Specification

## Purpose

Given the set of satisfied facts and declarations, report every block of every
contract as writable now or blocked by a named missing requirement, and derive
the writing order from the block graph rather than from a literal list. This
spec also pins the two mutations that prove the reader generalizes: an
invented eleventh contract, and a fact outside the closed vocabulary.

## Requirements

### Requirement: Per-Block Readiness

Given a set of satisfied fact ids and a set of satisfied declaration ids, the
reader MUST report every block of every section as either `writable`, or
`blocked` naming each of its still-missing `requires_facts` entries and each
of its still-missing `requires_declarations` entries separately. A block whose
facts are all satisfied but whose declarations are not MUST report `blocked`,
never `writable` — a fact-only check that ignores declarations reports this
case wrong.

#### Scenario: A block with every requirement satisfied is writable

- GIVEN a block requiring `requires_facts: [dataset]` and no declarations, with
  `dataset` in the satisfied-facts set
- WHEN readiness is computed
- THEN the block reports `writable`

#### Scenario: A block blocked only by a declaration is not writable

- GIVEN a block requiring `requires_facts: [dataset]` (satisfied) and
  `requires_declarations: [repository-url]` (not satisfied)
- WHEN readiness is computed
- THEN the block reports `blocked`, naming `repository-url` as the missing
  requirement, even though every fact is satisfied

#### Scenario: Back matter reports zero missing facts and its declarations missing

- GIVEN back matter's blocks, which require no facts and several declarations,
  none of which are satisfied
- WHEN readiness is computed
- THEN each block reports `blocked` with zero missing facts and its
  declarations named as missing

### Requirement: Derived Writing Order

The writing order MUST be derived from the block graph — every block's
`after` edges plus its section's `after` edges and `position` — and never
from a literal, hand-written list. The block graph is authoritative; a
section-level order is a human-readable summary of it. Where the graph
leaves two blocks unordered relative to each other, the derived order MUST
still place them deterministically and reproducibly, without asserting a
dependency the graph does not state. A cycle in the graph MUST refuse
`ORDER_CYCLE` naming the participating blocks.

#### Scenario: Related Work's summary block is ordered correctly

- GIVEN the introduction's blocks 1, 2, and 4a with no `after` edge to
  related-work, and its block 3 with `after: [related-work]`
- WHEN the writing order is derived
- THEN blocks 1, 2, and 4a precede related-work in the order, block 3 follows
  related-work, and the introduction section does not move as a single unit

#### Scenario: A cyclic graph refuses

- GIVEN two blocks whose `after` edges each name the other
- WHEN the writing order is derived
- THEN it refuses `ORDER_CYCLE` naming both blocks

#### Scenario: Position reports rendering order separately from writing order

- GIVEN back matter's `position` naming the document's last rendering place
- WHEN the derived writing order and the rendering order are both reported
- THEN back matter's rendering position is last while its place in the writing
  order is decided only by its (absent) `after` edges, never by `position`

### Requirement: Eleventh Contract Enters With No Code Change

An operator-authored eleventh contract, carrying a valid header, MUST enter
readiness and order computation with zero changes to the reader's code. To
prove generality rather than round-tripping, its declared fact combination or
block ordering MUST be one no shipped contract uses.

#### Scenario: A novel eleventh contract is read correctly

- GIVEN an eleventh contract file added to `sections/`, using a
  `requires_facts` combination absent from all ten shipped contracts
- WHEN readiness and order are computed with no change to the reader's source
- THEN the eleventh contract's blocks report readiness and take their place in
  the derived order like any shipped contract

#### Scenario: A combination reused from a shipped contract proves nothing

- GIVEN a candidate eleventh contract whose fact combination and block
  ordering both already exist among the ten shipped contracts
- WHEN this is checked against the shipped set
- THEN it is rejected as evidence for this requirement's mutation, because it
  proves round-tripping and not generality

### Requirement: A Fact Outside the Ten Refuses

A contract naming a fact outside the closed vocabulary MUST refuse
`UNKNOWN_FACT`, observed by running the reader against that contract rather
than only asserted in prose.

#### Scenario: An out-of-vocabulary fact refuses on execution

- GIVEN a contract whose header declares `requires_facts: [discussion]`
- WHEN the reader is executed against it
- THEN it exits refusing `UNKNOWN_FACT` naming `discussion`, and readiness is
  never computed for that contract
