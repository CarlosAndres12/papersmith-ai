# Delta for fact-production

## MODIFIED Requirements

### Requirement: A Produced Fact's Value Is Its Producer's Own Rendered Text

When a downstream block's requirement needs a produced fact's text — not
merely its ordering — that text MUST be read from the producer block's own
rendered content in `main.tex`. No second, separately authored value for a
produced fact may exist anywhere. A fact corroborated by more than one
producer (the `gap` carve-out) yields one body per producer; nothing is ever
concatenated or merged, and no live consumer resolves `gap`'s text this way
today — `check_gap` alone reads both producers' bodies, verbatim, for its
own `unmeasured` coupling verdict. When a producer's own header also
declares `figure.components_from` naming the same fact it itself produces,
resolving that self-referential case is scoped to this change's design
decision (D2) and is not decided by this requirement.
(Previously: no producer declared `components_from` against its own
produced fact; the self-referential case did not exist.)

#### Scenario: A consumer reads the producer's own words

- GIVEN `related-work.rw-synthesis-artefact` needing `contributions`'s text
  for its `figure.components_from` resolution
- WHEN that text is resolved
- THEN it is `materials-and-methods.mm-proposal`'s own rendered content, not
  `introduction.block-4b`'s or a separately declared or authored copy
  (Previously: resolved to `introduction.block-4b`'s rendered content)

## ADDED Requirements

### Requirement: Producer Reassignment Is Read From One Shared Scan, Not Restated Per Guard

A produced fact's current producer identity MUST be read, by every
consumer-facing guard — duplication (`FACT_PRODUCER_DUPLICATE`), totality
(`FACT_PRODUCER_ABSENT`), self-reference (`FACT_SELF_REQUIRED`), route
exclusivity (`FACT_ROUTE_AMBIGUOUS`), chain-row backing
(`CHAIN_ROW_UNBACKED`), and reachability (`PRODUCER_CHAIN_ABSENT`) — from
the same corpus-wide `produces_facts` scan this capability defines, never
from a cached or hand-listed mapping. Reassigning a fact's producer
therefore requires editing only the `produces_facts` declaration(s) that
move; every guard MUST re-derive the new identity on the next assembly,
never trusting a prior pass's result.

#### Scenario: The reassigned producer is exclusive and unrequired-by-itself

- GIVEN `materials-and-methods.mm-proposal` declares `produces_facts:
  [contributions]`, and `introduction.block-4b` drops that declaration
  while gaining `requires_facts: [contributions]`
- WHEN the corpus is assembled
- THEN `contributions` resolves to `mm-proposal` alone, and `block-4b` is
  accepted with no `FACT_SELF_REQUIRED` refusal

#### Scenario: Reviving the old producer duplicates it

- GIVEN `block-4b`'s dropped `produces_facts: [contributions]` entry is
  restored while `mm-proposal`'s own entry stays
- WHEN the corpus is assembled
- THEN it refuses `FACT_PRODUCER_DUPLICATE` naming `contributions` and both
  blocks, uncorroborated since no coupling-verification check names this pair

#### Scenario: Deleting the sole producer leaves the fact unresolved

- GIVEN `mm-proposal`'s `produces_facts: [contributions]` entry deleted with
  no other block producing it
- WHEN the corpus is assembled
- THEN it refuses `FACT_PRODUCER_ABSENT` naming `contributions`, since
  `block-4b` still requires it

#### Scenario: A consumer's stale row or edge is checked against the current producer

- GIVEN any of the seven consumers' `### Internal chain` row or `after`
  edge still names `introduction.block-4b` after the move
- WHEN the corpus is assembled
- THEN it refuses `CHAIN_ROW_UNBACKED` or `PRODUCER_CHAIN_ABSENT` naming
  that consumer and `mm-proposal` as the actual, current producer — never
  silently accepting the stale reference

#### Scenario: `contributions` stays produced, not declarable

- GIVEN `mm-proposal`'s `produces_facts: [contributions]` entry
- WHEN the corpus is assembled
- THEN it is accepted with no `FACT_ROUTE_AMBIGUOUS` refusal, since
  `contributions` is not in `OBSERVABLE_FACTS ∪ STRUCTURAL_FACTS`
