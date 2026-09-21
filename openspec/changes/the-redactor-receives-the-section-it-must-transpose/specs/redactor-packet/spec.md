# Delta for Redactor Packet

## MODIFIED Requirements

### Requirement: The Packet Carries Contract Prose, Same-Section Style Extracts, And The Block's Own Bound Source Sections

For one block about to be drafted, the packet MUST carry three parts: that
block's own section contract prose (unread-for-meaning header aside — the
human-facing prose); for every `style-reference`-classed `guidance/` entry,
the same section's equivalent block resolved via
`paper_style.resolve_style_set` — whole, never excerpted, per
`style-channel`'s existing requirement; and, for a `transposition`-mode
block only, the block's own bound source sections resolved via the shipped
`paper_source_span.resolve_bound_sections`, shaped identically to
`BlockContract.source_sections`. The packet MUST carry zero content drawn
from any reference's substantive claims, data, or results.

Assembly MUST report a sibling `source_sections_state.state`, one of
`resolved`, `unbound`, `unmeasured`, or `not-applicable`, with a non-null
`reason` for every value except `resolved`. It MUST NOT report an empty
`source_sections` list silently where a named state is owed — an absent or
unreadable paper root is a named state, never a refusal.

(Previously: "The Packet Carries Contract Prose Plus Same-Section Style
Extracts" — two parts only, no bound-section key, no paper-root parameter,
no state vocabulary.)

#### Scenario: A packet for one block assembles both style parts

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

#### Scenario: A transposition block with a resolved binding carries its own section text

- GIVEN a `transposition`-mode block bound to a section of a paper reachable
  through a supplied paper root
- WHEN the packet is assembled
- THEN `source_sections` carries that section's own resolved text and
  `source_sections_state.state` reads `resolved`

#### Scenario: A transposition block with no binding decided reports unbound, not a refusal

- GIVEN a `transposition`-mode block naming no `(fact, lineage, title)`
  triple at all
- WHEN the packet is assembled
- THEN `source_sections` is empty, `source_sections_state.state` reads
  `unbound`, and no refusal is raised

#### Scenario: No paper root reachable reports unmeasured, distinguishable from unbound

- GIVEN the same block, now with a declared triple, assembled with no paper
  root supplied or one that does not resolve
- WHEN the packet is assembled
- THEN `source_sections_state.state` reads `unmeasured`, `reason` names the
  flag or root that would answer it, and this state is distinct from
  `unbound` even though both report an empty `source_sections`

#### Scenario: An argument-mode block reports not-applicable and stays byte-identical

- GIVEN a block whose contract resolves `mode: argument`, with a bound
  section that would otherwise resolve
- WHEN the packet is assembled
- THEN `source_sections_state.state` reads `not-applicable`, `source_sections`
  is empty, and the packet's other three keys are byte-identical to a packet
  assembled before this capability existed

#### Scenario: An unrelated section's defect blocks a transposition block's packet

- GIVEN a `transposition`-mode block with a resolvable binding, and a
  different section file under the same `sections_dir` carrying a malformed
  header
- WHEN the packet is assembled
- THEN assembly refuses on the unrelated section's own corpus-integrity code
  rather than resolving this block's binding — an accepted consequence of
  assembling one corpus for the whole paper, not a defect of this block's
  own binding
