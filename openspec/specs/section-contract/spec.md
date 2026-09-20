# Section Contract Specification

## Purpose

Every file under `sections/` carries a machine-readable front-matter header above
its unchanged prose. A reader interprets the header's structure and never the
prose, so a user who rewrites, adds, reorders, or deletes a contract still has a
working skill. This spec pins the header schema, the two closed vocabularies
(facts, declarations), the citations regime, the transcription rule for `after`
edges, and the refusal each violation must raise.

## Requirements

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
### Requirement: Closed Fact Vocabulary

`requires_facts` entries MUST be drawn only from the ten ids: `formulation`,
`contributions`, `problem-statement`, `gap`, `dataset`, `experimental-design`,
`implementation`, `results`, `limitations`, `skeleton`. A fact id outside this
set MUST refuse `UNKNOWN_FACT` naming the offending id, derived from one
declaration so an unclassified value goes red rather than silent.

#### Scenario: A listed fact parses

- GIVEN a block declaring `requires_facts: [results]`
- WHEN the reader parses it
- THEN it accepts `results` with no refusal

#### Scenario: An unlisted fact refuses

- GIVEN a block declaring `requires_facts: [discussion]`
- WHEN the reader parses it
- THEN it refuses `UNKNOWN_FACT` naming `discussion`

### Requirement: Closed Declaration Vocabulary

`requires_declarations` entries MUST be drawn only from: `author-roles`,
`grant-title`, `grant-code`, `repository-url`, `keyword-bounds`,
`classification-line` — operator-supplied inputs derived from no fact. A
declaration id outside this set MUST refuse `UNKNOWN_DECLARATION` naming the
offending id, derived from the same one-declaration mechanism as the fact
vocabulary.

#### Scenario: A listed declaration parses

- GIVEN back matter's Author Contributions block declaring
  `requires_declarations: [author-roles]`
- WHEN the reader parses it
- THEN it accepts `author-roles` with no refusal

#### Scenario: An unlisted declaration refuses

- GIVEN a block declaring `requires_declarations: [reviewer-name]`
- WHEN the reader parses it
- THEN it refuses `UNKNOWN_DECLARATION` naming `reviewer-name`

### Requirement: Closed Citations Regime

Each block's `citations` MUST be exactly one of `discovery`, `resolution`, or
`none`. Any other value MUST refuse `UNKNOWN_CITATIONS_REGIME` naming the
offending value.

#### Scenario: A valid regime parses

- GIVEN a block declaring `citations: discovery`
- WHEN the reader parses it
- THEN it accepts the value with no refusal

#### Scenario: An invalid regime refuses

- GIVEN a block declaring `citations: maybe`
- WHEN the reader parses it
- THEN it refuses `UNKNOWN_CITATIONS_REGIME` naming `maybe`

### Requirement: Byte-Clean Header Insertion

Inserting front matter into the ten shipped contracts MUST NOT change one byte
of the prose below the header. The acceptance evidence is a digest of each
file's body computed before and after insertion, per file, matching exactly.
A visual review is not evidence.

#### Scenario: Digest matches after insertion

- GIVEN the ten `sections/*.md` files as committed before this change, and their
  post-header bodies after this change
- WHEN a digest is computed over each file's body below the header, both before
  and after
- THEN the ten before/after digest pairs are byte-identical

### Requirement: Transcribed `after` Edges Only

An `after` edge MUST be admitted only when the contract's own prose states
it, verified as a literal (whitespace-collapsed, markdown-emphasis-stripped)
substring of the named `source.file`'s prose body — unchanged from before.
The edge count is no longer a fixed number: normalizing all ten contracts'
`### Internal chain` tables into transcribed edges (`internal-chain-edges`)
raises the shipped edge set well past three. What remains invariant instead:
every `after` edge, wherever declared, carries a verified, prose-backed
quote; no edge exists that is not backed by a quote (`SPAN_NOT_IN_SOURCE`
on failure); and no `### Internal chain` row is left unmapped to a backing
edge (`CHAIN_ROW_UNBACKED` on failure, per `internal-chain-edges`). A test
MUST assert both properties hold across the full shipped corpus — never a
fixed cardinality.

(Previously: asserted the shipped edge set is exactly three named edges,
which this change invalidates by construction.)

#### Scenario: Every shipped edge is quote-backed

- GIVEN the ten contracts' parsed headers, normalized under
  `contract-input-partition`
- WHEN every `after` edge, section- and block-level, is collected
- THEN each one's `source.quote` is a verified literal substring of its
  `source.file`'s prose body, with no exceptions

#### Scenario: An invented edge on a shipped contract fails

- GIVEN a shipped contract's header edited to add an `after` edge not
  backed by that contract's own prose
- WHEN the edge-set test runs
- THEN it fails, naming the untranscribed edge

#### Scenario: No internal-chain row is left unmapped

- GIVEN the ten contracts' normalized `### Internal chain` tables
- WHEN every row is checked against the collected edge set
- THEN every row maps to exactly one backing `after` edge; a row with none
  fails the test naming that row

#### Implementation note (recorded at apply, not re-opening the decision)

The `title-and-keywords` after every body-section edge remains
**position-derived**, not enumerated in `title-and-keywords`'s header and
not resolved against the `skeleton` fact — unchanged from the prior note.
This change adds no new special-cased edge of that kind; every additional
edge this change introduces is a literal, header-declared transcription
from an `### Internal chain` row, following the same discipline as the two
pre-existing literal edges.

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
### Requirement: Symmetric Optional Fork For Dataset Placement

The dataset-placement fork — whether the dataset is described in Materials
and Methods or in Experimental Setup — MUST be structurally represented on
both sides: `01-materials-and-methods.md` declares `mm-dataset`
(`optional: true`, `requires_facts: [dataset]`), and
`02-experimental-setup.md` declares a mirroring `es-dataset`
(`optional: true`, `requires_facts: [dataset]`), so `skeleton-startup`'s
disk inference has a branch to read on either side.

#### Scenario: Both sides of the fork exist in the corpus

- GIVEN the shipped corpus after this change
- WHEN `01-materials-and-methods.md` and `02-experimental-setup.md` are
  parsed
- THEN both declare an `optional: true` dataset block requiring `dataset`,
  under ids `mm-dataset` and `es-dataset` respectively

### Requirement: `mm-proposal`'s Facts Match What It Genuinely Needs

`01-materials-and-methods.md`'s `mm-proposal` block MUST declare
`requires_facts: [formulation]` only — `implementation` is dropped, since
the proposal's own formal definition needs no run-time implementation
detail to be drafted.

#### Scenario: mm-proposal no longer requires implementation

- GIVEN `01-materials-and-methods.md` as parsed after this change
- WHEN `mm-proposal`'s `requires_facts` is read
- THEN it contains `formulation` and does not contain `implementation`
