# Style Channel Specification

## Purpose

The style channel supplies register — not content — by resolving and
recording the equivalent block from each style-registered reference. What it
records is the only material the overlap check in `style-leak-detection` may
compare against; an unrecorded sample is unmeasurable and therefore
inadmissible.

## Requirements

### Requirement: Equivalent-Block Resolution

Given the block about to be written, the sampler MUST resolve the equivalent
block in each reference the guidance registry classes `style-reference`.

#### Scenario: A style-reference resolves its equivalent block

- GIVEN a block about to be drafted and one `style-reference`-classed
  guidance entry
- WHEN the sampler resolves it
- THEN it returns that reference's equivalent block

### Requirement: Whole-Block Passing

The sampler MUST pass each resolved reference block whole, never an
extracted sample or excerpt — register lives in whole sentences, not
fragments.

#### Scenario: A resolved block is passed intact

- GIVEN a resolved equivalent block of N sentences
- WHEN the sampler passes it to the redactor
- THEN all N sentences are passed, none extracted or truncated

### Requirement: Recorded Sample Set Is The Only Admissible Reference

The sampler MUST record exactly what it showed the redactor, as the sample
set `R`. Any later check comparing against reference text MUST read only
`R`, never the reference file directly. An unrecorded sample MUST NOT be
treated as part of `R`.

#### Scenario: R contains exactly the shown samples

- GIVEN a drafting run using two style-reference blocks
- WHEN `R` is read back
- THEN it contains exactly those two blocks and nothing read from the
  reference files outside them
### Requirement: The Packet Is A New Consumer Of Equivalent-Block Resolution

`redactor-packet`'s assembly MUST resolve its style extracts by calling
`resolve_style_set` — the same equivalent-block resolution this spec
already defines — never a second, independently written resolution path.
Every requirement this spec already states (equivalent-block resolution,
whole-block passing, `R` as the only admissible reference) applies
unchanged to the packet's extracts.

#### Scenario: The packet's extracts are resolved by the existing sampler

- GIVEN a block about to be drafted and a `style-reference`-classed
  `guidance/` entry
- WHEN the redactor packet is assembled
- THEN its style extract is exactly the block `resolve_style_set` returns
  for that reference, whole and unmodified

#### Scenario: The packet's extracts are recorded into the same R

- GIVEN a packet assembled from two style-reference extracts
- WHEN the sample set `R` is read back
- THEN it contains exactly those two extracts, the same set any other
  consumer of `R` would read
