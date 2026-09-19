# Fact Production Specification

## Purpose

Every fact in the closed ten-fact vocabulary (`section-contract`) resolves to
exactly one production route: an external source (the existing
`FACT_SOURCE_ROOT` mapping, five facts) or one or more blocks' `produces_facts`
declarations naming it (the four facts a block writes rather than observes). A
fact resolves to more than one block producer only when an existing
coupling-verification check names that exact pair of blocks as the two sides
it verifies agree (`gap` and Coupling 3, today the only such pair); every
other duplicate producer still refuses. This capability adds the
`produces_facts` header field, its transcription discipline, corpus-wide
totality, the refusal for a block that requires what it itself produces, the
refusal for an uncorroborated duplicate producer, and produced-fact
satisfaction read from every one of a fact's producer block(s)' own written
status. The structural fact `skeleton` is untouched — resolved by the
existing skeleton-startup mechanism, out of scope here.

## Requirements

### Requirement: `produces_facts` Field Grammar

A block MAY declare `produces_facts`, a list of rich `{value, source: {file,
quote}}` entries mirroring `requires_facts`'s own shape (`section-contract`),
where `value` is drawn from the closed ten-fact vocabulary. An entry missing
`value` or `source`, or carrying a `null` `source`, MUST refuse
`MALFORMED_HEADER` naming the missing key. A `value` outside the closed
vocabulary MUST refuse `UNKNOWN_FACT` naming the offending id — both reused
from the identical `requires_facts` schema check, not new codes.

#### Scenario: A valid `produces_facts` entry parses

- GIVEN a block declaring `produces_facts: [{value: gap, source: {file:
  "05-related-work.md", quote: "<verbatim sentence>"}}]`
- WHEN the reader parses it
- THEN it accepts `gap` as produced, with no refusal

#### Scenario: An unknown fact id refuses

- GIVEN a `produces_facts` entry naming `discussion`
- WHEN the reader parses it
- THEN it refuses `UNKNOWN_FACT` naming `discussion`

### Requirement: Transcribed `produces_facts` Entries Only

A `produces_facts` entry MUST be admitted only when its `source.quote`
verifies as a literal (whitespace-collapsed, markdown-emphasis-stripped)
substring of `source.file`'s prose body — the same mechanism already
governing `requires_facts` / `requires_declarations` / `after`
(`requirement-transcription`). An entry whose quote is not found MUST refuse
`SPAN_NOT_IN_SOURCE` naming the entry's block and fact id.

#### Scenario: An unverifiable `produces_facts` quote refuses

- GIVEN a `produces_facts` entry whose `source.quote` is not a substring of
  `source.file`'s body
- WHEN the corpus is assembled
- THEN it refuses `SPAN_NOT_IN_SOURCE` naming the entry

### Requirement: Every Producer Is Either Sole Or Corroborated

Every fact id in the closed vocabulary, excluding the structural `skeleton`
fact, MUST resolve to a producer: presence in `FACT_SOURCE_ROOT` (external),
or one or more blocks across the whole corpus whose `produces_facts` names
it. This resolution MUST be derived by scanning the parsed corpus on every
assembly — never a hand-listed fact-to-block mapping. A fact named by zero
blocks and absent from `FACT_SOURCE_ROOT` MUST refuse `FACT_PRODUCER_ABSENT`
naming the fact id. A fact named by two or more blocks' `produces_facts` MUST
refuse `FACT_PRODUCER_DUPLICATE` naming the fact id and the competing block
ids — UNLESS an existing coupling-verification check names that exact pair
of blocks as the two sides it verifies agree (`coupling-verification`'s
Coupling 3, for `gap` and its two producers `related-work.rw-closing` and
`introduction.block-3`, today the only such pair). A corroborated pair MUST
NOT refuse `FACT_PRODUCER_DUPLICATE`; a duplicate naming any block outside
that corroborated pair, or a duplicate for a fact no coupling-verification
check corroborates at all, MUST still refuse.

#### Scenario: Each produced fact resolves to its producer(s)

- GIVEN the shipped corpus, where `contributions`, `problem-statement`, and
  `limitations` each carry exactly one `produces_facts` entry, and `gap`
  carries two — `related-work.rw-closing` and `introduction.block-3`, the
  pair Coupling 3 verifies agree
- WHEN the corpus is assembled
- THEN every one of the ten facts resolves — nine to exactly one block or an
  external source, and `gap` to its corroborated pair — with no refusal

#### Scenario: A fact with no producer anywhere refuses

- GIVEN a fact absent from `FACT_SOURCE_ROOT` and named by no block's
  `produces_facts`
- WHEN the corpus is assembled
- THEN it refuses `FACT_PRODUCER_ABSENT` naming that fact

#### Scenario: Two uncorroborated blocks claiming the same fact refuses

- GIVEN two blocks whose `produces_facts` both name `limitations`, with no
  coupling-verification check naming that pair
- WHEN the corpus is assembled
- THEN it refuses `FACT_PRODUCER_DUPLICATE` naming `limitations` and both
  block ids

#### Scenario: A corroborated pair of producers is legal

- GIVEN `related-work.rw-closing` and `introduction.block-3` both declaring
  `produces_facts: [gap]` — the exact pair `coupling-verification`'s
  Coupling 3 names as the two blocks that must agree on `gap`
- WHEN the corpus is assembled
- THEN it accepts both as producers of `gap`, with no `FACT_PRODUCER_DUPLICATE`
  refusal

#### Scenario: Mutation — deleting the only producer is caught

- GIVEN `limitations.lim-proposal-items`'s `produces_facts: [limitations]`
  entry deleted, with no other block producing `limitations`
- WHEN the corpus is assembled
- THEN it refuses `FACT_PRODUCER_ABSENT` naming `limitations`, rather than
  silently treating `limitations` as satisfied or as externally declared

### Requirement: A Block MUST NOT Require What It Produces

A block whose `produces_facts` and `requires_facts` name the same fact id
MUST refuse `FACT_SELF_REQUIRED` naming the block id and the fact.

#### Scenario: A self-referencing block refuses

- GIVEN a block declaring both `produces_facts: [gap]` and
  `requires_facts: [gap]`
- WHEN the corpus is assembled
- THEN it refuses `FACT_SELF_REQUIRED` naming that block and `gap`

#### Scenario: The corrected `rw-closing` parses

- GIVEN `related-work.rw-closing` declaring `produces_facts: [gap]` and a
  `requires_facts` list that no longer names `gap`
- WHEN the corpus is assembled
- THEN it accepts the block with no refusal

### Requirement: Produced-Fact Satisfaction Derived From the Producer's Written Status

A fact whose producer is one or more blocks (not an external source) MUST be
reported satisfied exactly when every one of those blocks' own written status
(`paper_block.read_status`) reports it opened — never from a `declarations`-
region fact-resolution record (`paper-declarations`). This is the sole
satisfaction signal every reader (`readiness`, `phases`) consults for a
produced fact.

#### Scenario: A produced fact becomes satisfied once every producer is written

- GIVEN `gap`'s two producing blocks, `related-work.rw-closing` and
  `introduction.block-3`, both opened in `main.tex`
- WHEN satisfaction is computed for `gap`
- THEN it reports satisfied, with no `declare` call ever having recorded it

#### Scenario: An unwritten producer leaves the fact unsatisfied

- GIVEN `related-work.rw-closing` opened but `introduction.block-3` not yet
  opened
- WHEN satisfaction is computed for `gap`
- THEN it reports unsatisfied, naming `introduction.block-3` as the block
  that must be written

### Requirement: A Produced Fact's Value Is Its Producer's Own Rendered Text

When a downstream block's requirement needs a produced fact's text — not
merely its ordering — that text MUST be read from the producer block's own
rendered content in `main.tex`. No second, separately authored value for a
produced fact may exist anywhere. A fact corroborated by more than one
producer (the `gap` carve-out) yields one body per producer; nothing is ever
concatenated or merged, and no live consumer resolves `gap`'s text this way
today — `check_gap` alone reads both producers' bodies, verbatim, for its own
`unmeasured` coupling verdict.

#### Scenario: A consumer reads the producer's own words

- GIVEN `related-work.rw-synthesis-artefact` needing `contributions`'s text
  for its `figure.components_from` resolution
- WHEN that text is resolved
- THEN it is `introduction.block-4b`'s own rendered content, not a
  separately declared or separately authored copy
