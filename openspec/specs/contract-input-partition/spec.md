# Contract Input Partition Specification

## Purpose

Every contract's prose carries real dependency data — which facts and
declarations reach it from outside, and which sibling blocks it depends on —
but today that data lives only in prose tables the reader never opens. This
capability makes the partition explicit and machine-addressable: every
contract states its external inputs and its internal chain under two fixed
headings, and every internal-chain row names its dependency using the
corpus's own qualified block-id vocabulary, never a paraphrase.

## Requirements

### Requirement: Two-Heading Partition

Every `sections/*.md` contract's prose MUST carry a `### External inputs`
heading and a `### Internal chain` heading. A contract with no internal
dependencies MUST still carry the `### Internal chain` heading, stating it
is empty, rather than omitting it. A contract missing either heading MUST
refuse `INPUT_PARTITION_ABSENT` naming the missing heading.

#### Scenario: A partitioned contract parses

- GIVEN `sections/06-introduction.md`, which already carries `### External
  inputs` and `### Internal chain`
- WHEN the reader parses its prose
- THEN it accepts the partition with no refusal

#### Scenario: A flat, unpartitioned contract refuses

- GIVEN `sections/02-experimental-setup.md` as committed today, whose prose
  carries one flat `## Inputs` table and no `### Internal chain` heading
- WHEN the reader parses its prose
- THEN it refuses `INPUT_PARTITION_ABSENT` naming `### Internal chain`

### Requirement: Internal-Chain Rows Name Qualified Block Ids

Each row of `### Internal chain` MUST name the block(s) it depends on using
the corpus's qualified `<section>.<block-id>` vocabulary — the same
vocabulary `after.target`, `derive_order`'s output, and `open --block`
already use — never a free-text paraphrase of the block's function. A row
the reader cannot map onto exactly one qualified id MUST refuse
`CHAIN_ROW_UNRESOLVED` naming the row's own text.

#### Scenario: A row naming a qualified id maps

- GIVEN an internal-chain row reading "**2** — depends on:
  `introduction.block-4` (partial)"
- WHEN the reader transcribes internal-chain rows
- THEN it resolves the dependency to `introduction.block-4` with no refusal

#### Scenario: A row naming only a paraphrase refuses

- GIVEN an internal-chain row reading "depends on: the announcement of the
  count", naming no qualified block id anywhere in the row
- WHEN the reader transcribes internal-chain rows
- THEN it refuses `CHAIN_ROW_UNRESOLVED` naming that row's text

#### Scenario: Mutation — a row edited to drop its qualified id is caught

- GIVEN a previously-mapping internal-chain row whose qualified id is edited
  out, leaving only prose
- WHEN the transcription runs again
- THEN it refuses `CHAIN_ROW_UNRESOLVED` rather than silently reusing the
  previous mapping
### Requirement: A Produced-Fact Dependency Is An Internal-Chain Row

For every fact whose producer is a block (`fact-production`), every OTHER
block whose `requires_facts` names that fact MUST carry an `### Internal
chain` row resolving to the producer's qualified block id, under this
capability's own row-resolution rule, in turn backed by an `after` edge
(`internal-chain-edges`). A consumer requiring a produced fact with no such
row MUST refuse `PRODUCER_CHAIN_ABSENT` naming the consumer block, the fact,
and its producer.

#### Scenario: A producer→consumer row is accepted

- GIVEN `introduction.block-3` requiring `gap` (produced by
  `related-work.rw-closing`), and its `### Internal chain` naming
  `related-work.rw-closing`, backed by an `after` edge
- WHEN the corpus is assembled
- THEN the row is accepted with no refusal

#### Scenario: A missing producer row refuses

- GIVEN a block requiring a produced fact whose `### Internal chain` table
  carries no row naming that fact's producer
- WHEN the corpus is assembled
- THEN it refuses `PRODUCER_CHAIN_ABSENT` naming the consumer, the fact, and
  the producer

#### Scenario: Mutation — removing the row after it existed is caught

- GIVEN a consumer's producer-naming internal-chain row deleted while its
  `requires_facts` entry for that produced fact remains
- WHEN the corpus is assembled again
- THEN it refuses `PRODUCER_CHAIN_ABSENT`, proving the check reads the live
  row set rather than a cached prior pass
