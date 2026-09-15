# Delta for Section Contract

## MODIFIED Requirements

### Requirement: Front Matter Schema

Each contract file MUST carry a front-matter header with a mandatory
`section` id, a mandatory `position` (rendering place), an optional `after`
(list of section ids), an optional `mode` (the section-level default drafting
mode), and a mandatory `blocks` list in order. Each block MUST declare `id`,
`requires_facts`, `requires_declarations`, and `citations`; each block MAY
declare `optional`, its own `after`, and its own `mode` (overriding the
section-level default when present). A header missing any mandatory field, or
carrying a key outside this widened schema, MUST refuse `MALFORMED_HEADER`
naming the missing or unknown key. Everything below the header MUST be passed
through unread.

(Previously: `mode` did not exist in the schema at either level; a `mode` key
anywhere refused `MALFORMED_HEADER` as unknown.)

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

## ADDED Requirements

### Requirement: Headers Written Before `mode` Existed

`sections/*.md` carry no front-matter header as committed today — Phase 2's
insertion has not landed. If a header is ever inserted without `mode` before
this widening lands, that header remains schema-valid after this change: an
absent `mode` at both levels is optional absence, not a violation. Such a
block resolves to no effective mode, and `write`'s readiness stage MUST
refuse to draft it rather than assume a mode. The schema alone cannot
distinguish "no mode was ever transcribed" from "a mode was removed" — both
are the same absent key — so the remedy is never a code-guessed value: an
operator transcribes `mode` from the contract's own prose, the same as any
`after` edge, and a header is never silently rewritten by inference.

#### Scenario: A header with no mode at either level cannot be drafted

- GIVEN a block whose header declares no `mode`, at section or block level
- WHEN `write`'s readiness stage evaluates that block
- THEN it refuses rather than assuming a default mode

### Requirement: Closed Mode Vocabulary And Transcription

A `mode` declaration, at either level, MUST be an object carrying `value`
(exactly one of `transposition` or `argument`) and `source` (`{file, quote}`)
— the same shape `_validate_after_list` already enforces for `after` edges.
A `value` outside the pair MUST refuse `UNKNOWN_MODE` naming the offending
value. `mode` MUST be admitted only where the contract's own prose states it,
mirroring the transcription discipline already required of `after` edges.

#### Scenario: A valid mode value parses

- GIVEN a block declaring `mode: {value: transposition, source: {file:
  "01-materials-and-methods.md", quote: "The proposal already exists. This
  section does not choose it, improve it, or argue for it"}}`
- WHEN the reader parses it
- THEN it accepts `transposition` with no refusal

#### Scenario: An invalid mode value refuses

- GIVEN a block declaring `mode: {value: exposition, source: {file: "...",
  quote: "..."}}`
- WHEN the reader parses it
- THEN it refuses `UNKNOWN_MODE` naming `exposition`
