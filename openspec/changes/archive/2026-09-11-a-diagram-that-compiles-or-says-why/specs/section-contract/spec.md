# Delta for Section Contract

This delta extends `section-contract` as proposed by the sibling change
`the-contract-is-data-not-code` (unlanded). It has no existing on-disk
instances to migrate: `sections/*.md` carries no front matter today, so the
`figure:` field being added has never been written in the old shape.

## MODIFIED Requirements

### Requirement: Front Matter Schema

Each contract file MUST carry a front-matter header with a mandatory `section`
id, a mandatory `position` (rendering place), an optional `after` (list of
section ids), and a mandatory `blocks` list in order. Each block MUST declare
`id`, `requires_facts`, `requires_declarations`, and `citations`; each block
MAY declare `optional`, its own `after`, and a `figure` object. A `figure`
object, when present, MUST declare `ordered`, `excludes`, `caption_enumerates`,
`caption_decodes`, and `mandatory`; it MAY additionally declare
`components_from`, naming the one fact whose value IS the diagram's full
expected component list — declared only when that equality genuinely holds
(the diagram is that one fact's own list by contract), and omitted (or
explicit `null`) for a block whose diagram is a composite crossing over
several categories of content that no single fact's value can equal. A
header missing any mandatory field, carrying a key outside this schema, or a
`figure` object missing any of its five required subkeys, MUST refuse
`MALFORMED_HEADER` (or `MALFORMED_FIGURE_OBLIGATION` for the `figure` case)
naming the missing or unknown key. Everything below the header MUST be
passed through unread.
(Previously: blocks MAY declare `optional` and `after` only; no `figure`
field existed, and no diagram obligation could be read from the contract.
`components_from` was originally required on every `figure` object; widened
to optional by this change's own corrective amendment, verify FAIL,
CRITICAL finding on `es-assessment`.)

#### Scenario: Valid header parses

- GIVEN a contract file with `section`, `position`, and a `blocks` list where
  every block carries `id`, `requires_facts`, `requires_declarations`,
  `citations`
- WHEN the reader parses it
- THEN it returns a structured header with no refusal

#### Scenario: Missing mandatory field refuses

- GIVEN a contract file whose header omits `position`
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `position`

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
