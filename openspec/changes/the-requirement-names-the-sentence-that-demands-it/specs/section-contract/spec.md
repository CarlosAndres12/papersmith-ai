# Delta for Section Contract

## MODIFIED Requirements

### Requirement: Front Matter Schema

Each contract file MUST carry a front-matter header with a mandatory `section`
id, a mandatory `position` (rendering place), an optional `after` (list of
section ids), an optional `mode` (the section-level default drafting mode),
and a mandatory `blocks` list in order. Each block MUST declare `id`,
`requires_facts`, `requires_declarations`, and `citations`; each block MAY
declare `optional`, its own `after`, its own `mode` (overriding the
section-level default when present), and a `figure` object. Each
`requires_facts` / `requires_declarations` entry MAY be either a bare id
string (schema-legal, transcription-unverified) or a rich `{value, source:
{file, quote}}` object mirroring `after`'s list-of-objects shape, where
`value` is the fact or declaration id; a rich entry missing `value` or
`source`, or carrying an unknown key, MUST refuse `MALFORMED_HEADER` naming
the missing or unknown key. A `figure` object, when present, MUST declare
`ordered`, `excludes`, `caption_enumerates`, `caption_decodes`, and
`mandatory`; it MAY additionally declare `components_from`, naming the one
fact whose value IS the diagram's full expected component list — declared
only when that equality genuinely holds (the diagram is that one fact's own
list by contract), and omitted (or explicit `null`) for a block whose
diagram is a composite crossing over several categories of content that no
single fact's value can equal. A header missing any mandatory field,
carrying a key outside this widened schema, or a `figure` object missing any
of its five required subkeys, MUST refuse `MALFORMED_HEADER` (or
`MALFORMED_FIGURE_OBLIGATION` for the `figure` case) naming the missing or
unknown key. Everything below the header MUST be passed through unread.

(Previously: `requires_facts` / `requires_declarations` entries were bare id
strings only, with no provenance shape.)

#### Scenario: Valid header parses

- GIVEN a contract file with `section`, `position`, and a `blocks` list where
  every block carries `id`, `requires_facts`, `requires_declarations`, `citations`
- WHEN the reader parses it
- THEN it returns a structured header with no refusal

#### Scenario: Missing mandatory field refuses

- GIVEN a contract file whose header omits `position`
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `position`

#### Scenario: A block inherits the section-level mode

- GIVEN a header declaring `mode` at the top level and a block that declares
  no `mode` of its own
- WHEN the reader resolves that block's effective mode
- THEN it resolves to the section-level `mode`

#### Scenario: A block's own mode overrides the section-level default

- GIVEN a header declaring `mode` at the top level and one block declaring a
  different `mode`
- WHEN the reader resolves that block's effective mode
- THEN it resolves to the block's own `mode`, not the section's

#### Scenario: A valid `figure` object parses

- GIVEN a block declaring `figure: {components_from: contributions, ordered:
  true, excludes: [dataset, baseline], caption_enumerates: true,
  caption_decodes: true, mandatory: true}`
- WHEN the reader parses it
- THEN it accepts the block with no refusal

#### Scenario: A `figure` object missing a subkey refuses

- GIVEN a block's `figure` object with no `caption_decodes` key
- WHEN the reader parses it
- THEN it refuses `MALFORMED_FIGURE_OBLIGATION` naming `caption_decodes`

#### Scenario: A `figure` object without `components_from` parses

- GIVEN a block declaring `figure: {ordered: false, excludes: [], caption_enumerates: true,
  caption_decodes: false, mandatory: true}` (no `components_from` key)
- WHEN the reader parses it
- THEN it accepts the block with no refusal, and `components_from` resolves to `None`

#### Scenario: A bare-id requirement entry still parses

- GIVEN a block declaring `requires_facts: [results]` (bare id, no `source`)
- WHEN the reader parses it
- THEN it accepts the block with no refusal; `requirement-transcription`'s
  corpus-wide gate, not this schema check, decides whether the shipped
  corpus may carry it untranscribed

#### Scenario: A rich requirement entry parses

- GIVEN a block declaring `requires_facts: [{value: results, source: {file:
  "results-and-discussion.md", quote: "<verbatim sentence>"}}]`
- WHEN the reader parses it
- THEN it accepts `results` with no refusal

#### Scenario: A malformed rich requirement entry refuses

- GIVEN a block declaring a `requires_facts` entry that is an object missing
  `source`
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `source`
