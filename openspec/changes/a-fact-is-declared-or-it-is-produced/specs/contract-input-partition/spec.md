# Delta for Contract Input Partition

## ADDED Requirements

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
