# Citation Placement Specification

## Purpose

Placement dispatched on the block's `citations` regime, as a table, never one
universal rule — verified against `sections/01-materials-and-methods.md`,
`05-related-work.md`, and `06-introduction.md`.

## Requirements

### Requirement: Placement Dispatches On Regime

Citation placement validation MUST select its rule from the block's `citations`
regime, never apply one universal rule across regimes:

| Regime | Placement rule |
|---|---|
| `discovery` | Citation MUST sit at the end of the sentence it supports |
| `resolution` | Citation MUST attach to the object it credits, wherever that object sits in the sentence |
| `none` | No placement rule applies |

#### Scenario: Discovery citation passes at sentence end

- GIVEN a `citations: discovery` block with a citation at the end of the sentence it
  supports
- WHEN placement is validated
- THEN it passes

#### Scenario: Discovery citation mid-sentence fails

- GIVEN a `citations: discovery` block with a citation placed mid-sentence rather
  than at the end
- WHEN placement is validated
- THEN it refuses, naming the mid-sentence placement

#### Scenario: Resolution citation passes attached mid-sentence

- GIVEN a `citations: resolution` block with a citation attached to the object it
  credits, placed mid-sentence
- WHEN placement is validated
- THEN it passes — the same mid-sentence position that fails under `discovery`

#### Scenario: Resolution citation fails when detached from its object

- GIVEN a `citations: resolution` block with a citation not adjacent to the object
  it credits
- WHEN placement is validated
- THEN it refuses, naming the detached placement

### Requirement: The Noun-Phrase Prohibition Applies Only To `discovery`

A citation used as a noun phrase (e.g. "the work in [N] does X") MUST be rejected
only when the block's regime is `discovery`. Under `resolution`, a noun-phrase
citation MUST NOT be rejected on that basis — attaching to the object it credits is
exactly what the methods contract asks for, and a noun-phrase citation satisfies it.

#### Scenario: Noun-phrase citation fails under discovery

- GIVEN a `citations: discovery` block containing "the work in [N] does X"
- WHEN placement is validated
- THEN it refuses, naming the noun-phrase pattern

#### Scenario: Noun-phrase citation passes under resolution

- GIVEN a `citations: resolution` block containing a noun-phrase citation attached
  to the object it credits
- WHEN placement is validated
- THEN it passes — the noun-phrase prohibition does not apply to this regime

### Requirement: One Sentence, One Attributed Claim (Discovery Only)

Under `citations: discovery`, a sentence requiring support from two distinct claims
MUST be rejected as a single sentence with two citations; the requirement is met only
by splitting into two sentences, each with its own citation.

#### Scenario: Two citations in one discovery sentence fail

- GIVEN a `citations: discovery` sentence carrying two citations for two distinct
  claims
- WHEN placement is validated
- THEN it refuses, naming the multi-citation sentence
