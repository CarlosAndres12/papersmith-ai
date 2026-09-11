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
section ids), and a mandatory `blocks` list in order. Each block MUST declare
`id`, `requires_facts`, `requires_declarations`, and `citations`; each block MAY
declare `optional` and its own `after`. A header missing any mandatory field, or
carrying a key outside this schema, MUST refuse `MALFORMED_HEADER` naming the
missing or unknown key. Everything below the header MUST be passed through
unread.

#### Scenario: Valid header parses

- GIVEN a contract file with `section`, `position`, and a `blocks` list where
  every block carries `id`, `requires_facts`, `requires_declarations`, `citations`
- WHEN the reader parses it
- THEN it returns a structured header with no refusal

#### Scenario: Missing mandatory field refuses

- GIVEN a contract file whose header omits `position`
- WHEN the reader parses it
- THEN it refuses `MALFORMED_HEADER` naming `position`

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

An `after` edge MUST be admitted only when the contract's own prose states it.
Across the ten shipped contracts exactly three edges exist: section `abstract`
after section `conclusions` (conclusions' own prose: "The abstract is written
after this section, because it compresses it"); the introduction's block 3
after section `related-work` (introduction's own prose: "When a Related Work
section exists, this block is written after it"); and section
`title-and-keywords` after every section the `skeleton` fact declares as body
(title-and-keywords' own prose: "Every keyword appears in the body" resolved
against the skeleton's body-section list). A test MUST assert the shipped edge
set is exactly these three; a fourth or different edge on any shipped contract
fails that test.

#### Scenario: The shipped edge set is exactly three

- GIVEN the ten contracts' parsed headers
- WHEN every `after` edge, section- and block-level, is collected
- THEN the collected set contains exactly the three transcribed edges above and
  no other

#### Scenario: An invented edge on a shipped contract fails

- GIVEN a shipped contract's header edited to add a fourth `after` edge not
  backed by that contract's own prose
- WHEN the edge-set test runs
- THEN it fails, naming the untranscribed edge

#### Implementation note (recorded at apply, not re-opening the decision)

The third edge above — `title-and-keywords` after every section the
`skeleton` fact declares as body — is implemented as **position-derived**,
not enumerated in `title-and-keywords`'s header and not resolved against the
`skeleton` fact. Measured at design time: `skeleton` occurs exactly once
across all ten contracts (`sections/06-introduction.md`, unblocking
introduction block 6) and names no body-section list anywhere, so the literal
resolution this scenario's parenthetical describes has nothing to read. The
reader instead computes "the body" as every section whose `position` is
strictly between `abstract`'s and `back-matter`'s (positions 3–9), looked up
by section id and never by a hardcoded integer or a filename — the same
seven targets design.md's rejected "enumerate seven targets" option would
have named. `tests/test_paper_contract.py::GraphTests` therefore holds two
separate assertions rather than one three-element set: exactly two literal,
header-declared cross-section `after` edges (`abstract`→`conclusions`,
`introduction.block-3`→`related-work`), and the third edge proven separately
as a property of the derived writing order. This document's scenario above
is left as written, historically accurate about the intended data-vs-code
split; this note is the correction for a reader implementing it today.
