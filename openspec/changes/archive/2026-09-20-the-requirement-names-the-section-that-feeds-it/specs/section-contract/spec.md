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
`requires_facts` / `requires_declarations` entry MUST be a rich `{value,
source: {file, quote}}` object mirroring `after`'s list-of-objects shape,
where `value` is the fact or declaration id; a bare id string no longer
parses, and an entry missing `value` or `source`, carrying a `null`
`source`, or carrying an unknown key, MUST refuse `MALFORMED_HEADER` naming
the missing or unknown key. A `requires_facts` entry MAY additionally carry
`document: {lineage, section}` — the source document's lineage and the exact
title text of the section (or sections) within that document that feed this
entry. `section` MUST be either a non-empty string (one title) or a
non-empty list of unique non-empty-string titles (more than one section
feeding the same entry); an empty list, a list carrying a repeated title, or
a list entry that is not a non-empty string all refuse `MALFORMED_HEADER`
the same way a malformed single title does. A single string remains valid on
its own — the list shape is never forced onto every binding. Both `lineage`
and `section` are required together whenever `document` is present: an
entry's `document` object missing `lineage` or `section`, carrying a `null`
value for either, or carrying a key outside `{lineage, section}` MUST refuse
`MALFORMED_HEADER` naming the missing or unknown key. `document` is never
accepted on a `requires_declarations` entry — a declaration is
operator-supplied, never document-rooted — and one carrying `document` MUST
refuse `MALFORMED_HEADER` naming `document` as unknown. A `figure` object,
when present, MUST declare `ordered`, `excludes`, `caption_enumerates`,
`caption_decodes`, and `mandatory`; it MAY additionally declare
`components_from`, naming the one fact whose value IS the diagram's full
expected component list — declared only when that equality genuinely holds
(the diagram is that one fact's own list by contract), and omitted (or
explicit `null`) for a block whose diagram is a composite crossing over
several categories of content that no single fact's value can equal. A
header missing any mandatory field, carrying a key outside this widened
schema, or a `figure` object missing any of its five required subkeys, MUST
refuse `MALFORMED_HEADER` (or `MALFORMED_FIGURE_OBLIGATION` for the `figure`
case) naming the missing or unknown key. Everything below the header MUST be
passed through unread.

(Previously: `requires_facts` / `requires_declarations` entries carried only
`{value, source: {file, quote}}`, with no way to name a different source
document or a section within it — `source.file` was, in every shipped
contract, the contract file itself, so byte-identical entries could feed
distinct blocks with nothing to distinguish them. This change adds the
optional `document` half to `requires_facts` entries only; which entries
MUST carry one is a corpus-level obligation, not a schema-level one —
`SECTION_BINDING_ABSENT` in `source-section-binding`.)

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

#### Scenario: A bare-id requirement entry now refuses

- GIVEN a block declaring `requires_facts: [results]` (bare id, no `source`)
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER`; U3 (design.md D3) removed bare-string
  acceptance, so this is a schema-layer refusal, never something left for
  `requirement-transcription`'s corpus-wide gate to decide

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

#### Scenario: A document binding parses

- GIVEN a `requires_facts` entry declaring `document: {lineage:
  research-concept, section: "3. Formulación MIL-CREDA y kernel de bolsas
  ponderado por relevancia"}`
- WHEN the reader parses it
- THEN it accepts the entry with no refusal

#### Scenario: A malformed document binding refuses

- GIVEN a `requires_facts` entry's `document` object with no `section` key
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `section`

#### Scenario: A document binding naming more than one section parses

- GIVEN a `requires_facts` entry declaring `document: {lineage:
  research-concept, section: ["1. Fundamentos de métodos de kernel", "2.
  Estimación de la entropía de Rényi basada en kernels"]}`
- WHEN the reader parses it
- THEN it accepts the entry with no refusal

#### Scenario: An empty section list refuses

- GIVEN a `requires_facts` entry's `document.section` is `[]`
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `section`

#### Scenario: A section list carrying a repeated title refuses

- GIVEN a `requires_facts` entry's `document.section` is a list naming the
  same title twice
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `section`

#### Scenario: A document binding on a declaration entry refuses

- GIVEN a `requires_declarations` entry declaring a `document` key
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `document`
