# Redactor Packet Specification

## Purpose

Before a block is drafted, the redactor needs two things and nothing else:
its own section's contract prose, and how every reference paper under
`guidance/` wrote the same section — for register, never for content. This
capability assembles that packet from existing machinery
(`paper_guidance.read_registry`, `paper_style.resolve_style_set`, the
`style-sampler` agent, `paper_leak`'s tripwires) and guards it against
becoming a content channel in disguise.

## Requirements

### Requirement: The Packet Carries Contract Prose Plus Same-Section Style Extracts

For one block about to be drafted, the packet MUST carry that block's own
section contract prose (unread-for-meaning header aside — the human-facing
prose) plus, for every `style-reference`-classed `guidance/` entry, the
same section's equivalent block resolved via `paper_style.resolve_style_set`
— whole, never excerpted, per `style-channel`'s existing requirement. The
packet MUST carry zero content drawn from any reference's substantive
claims, data, or results.

#### Scenario: A packet for one block assembles both parts

- GIVEN a block about to be drafted and two `style-reference`-classed
  `guidance/` entries, each resolving an equivalent block
- WHEN the packet is assembled
- THEN it contains the block's own contract prose and both resolved
  reference extracts, and nothing else drawn from `guidance/`

#### Scenario: A reference with no equivalent block contributes nothing

- GIVEN one `style-reference` entry for which the sampler reports
  `noEquivalent`
- WHEN the packet is assembled
- THEN that reference contributes no extract to the packet, and assembly
  does not refuse on its account

### Requirement: The Leak Tripwires Gate The Packet, Not Only The Draft

Before a packet is handed to the redactor, the same guards
`style-leak-detection` already defines — the eight-token `STYLE_OVERLAP`
tripwire, register-distance, and relative-overlap proofs — MUST be capable
of running against the packet's own extracts, using exactly the recorded
sample set `R` `style-channel` already requires. The packet MUST NOT be
assembled from any reference material outside `R`.

#### Scenario: A packet built from recorded samples passes the tripwire

- GIVEN a packet whose extracts are exactly the sample set `R` a
  `style-sampler` run recorded
- WHEN the leak tripwire is checked against the packet
- THEN it reports no `STYLE_OVERLAP` violation attributable to material
  outside `R`

#### Scenario: A packet is refused if it draws from outside R

- GIVEN an attempt to add reference material to the packet that was not
  part of the recorded sample set `R`
- WHEN the packet is assembled
- THEN it refuses rather than admitting reference text unmeasured by the
  leak tripwires
