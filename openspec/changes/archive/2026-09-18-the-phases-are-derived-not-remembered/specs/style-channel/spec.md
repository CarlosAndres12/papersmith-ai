# Delta for Style Channel

## ADDED Requirements

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
