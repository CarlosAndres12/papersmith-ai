# Requirement Transcription Specification

## Purpose

`requires_facts` / `requires_declarations` decide what a block is licensed to
write. This spec gives those two fields the same transcription discipline
`after` edges already have: an entry is admitted only when a named contract's
own prose states it, verified as a literal substring — never on executor
judgment. It owns the rich entry's verification, the derived plain tuple
kept for downstream consumers, the cross-file quote case, the corpus-wide
gate, and the executor's reporting obligation for entries with no anchor.

## Requirements

### Requirement: Transcribed Requirement Entries Only

A `requires_facts` / `requires_declarations` entry carrying the rich
`{value, source: {file, quote}}` shape MUST be admitted only when
`source.quote` is a verified literal (whitespace-collapsed,
markdown-emphasis-stripped) substring of `source.file`'s prose body —
self-file or cross-file, reusing `paper_contract.quote_in_body` via
`_validate_source`, exactly as `after` edges are verified. An entry whose
quote is not found in the named file MUST refuse `SPAN_NOT_IN_SOURCE` naming
the entry's owning block and fact/declaration id. This check is unaffected
by an entry's optional `document: {lineage, section}` half
(`source-section-binding`): the two halves prove different claims — this
one that the contract's own prose asks for the fact, the other that a real
document section answers it — and neither's outcome substitutes for the
other. A `document` half that resolves cleanly does not excuse a failing
`source.quote`, and a verified `source.quote` does not excuse an absent or
unresolved `document` half on a bindable fact.

(Previously: this quote check was the only verification any requirement
entry needed; no second, document-rooted half existed to independently
confirm what a bindable fact's binding actually answers.)

#### Scenario: A self-file transcribed entry verifies

- GIVEN a block declaring `requires_facts: [{value: results, source: {file:
  "<own-file>.md", quote: "<verbatim sentence in that file>"}}]`
- WHEN the corpus is assembled
- THEN the entry verifies with no refusal

#### Scenario: A cross-file transcribed entry verifies

- GIVEN `abstract.slot-2` declaring a requirement entry whose `source.file`
  names `06-introduction.md`, mirroring the shipped `after` cross-file
  precedent
- WHEN the corpus is assembled
- THEN the quote is checked against `06-introduction.md`'s body, not
  `abstract`'s own, and verifies with no refusal

#### Scenario: An unverifiable quote refuses

- GIVEN a requirement entry whose `source.quote` is not a substring of
  `source.file`'s body
- WHEN the corpus is assembled
- THEN it refuses `SPAN_NOT_IN_SOURCE` naming the entry

#### Scenario: A resolved document binding does not excuse a failing quote

- GIVEN a bindable-fact entry whose `document` half resolves cleanly (its
  lineage and section both exist), but whose `source.quote` is not a
  substring of `source.file`'s body
- WHEN the corpus is assembled
- THEN it still refuses `SPAN_NOT_IN_SOURCE`; the clean `document`
  resolution does not clear this check

#### Scenario: A verified quote does not excuse an unresolved document half

- GIVEN a bindable-fact entry whose `source.quote` verifies, but whose
  `document.section` names a title absent from the resolved revision
- WHEN the corpus is assembled
- THEN it refuses `SECTION_NOT_IN_SOURCE` (`source-section-binding`); the
  verified quote does not clear that separate check

### Requirement: Derived Plain Tuple For Downstream Consumers

`paper_graph.BlockRecord.requires_facts` and `.requires_declarations` MUST
remain plain tuples of ids, derived from the rich entries in declaration
order, so the seven existing consumers reading them as value sets are
unaffected by this change.

#### Scenario: Derived tuple matches the pre-change value set

- GIVEN a block whose header carries rich requirement entries
- WHEN `BlockRecord` is built
- THEN `.requires_facts` / `.requires_declarations` equal the tuple of
  `value` fields, in the order declared, with no rich shape leaking through

### Requirement: Corpus-Wide Unconditional Transcription Gate

The transcription check for `requires_facts` / `requires_declarations` MUST
run unconditionally inside `paper_graph.assemble_corpus`, on every command
that assembles the corpus — never opt-in, never skippable by flag.

#### Scenario: The gate fires on an ordinary command

- GIVEN any command that assembles the corpus
- WHEN a shipped contract carries an entry that fails verification
- THEN the command refuses; there is no invocation path that assembles the
  corpus while skipping this check

### Requirement: Unanchored Entries Are Reported, Never Resolved By The Executor

When transcribing a declared `requires_facts` / `requires_declarations`
entry, an executor that finds no prose anchor for it anywhere in the
contract MUST report the entry — naming its file, block, and fact or
declaration id — to the operator, and MUST NOT delete the entry from the
header or fabricate a quote to satisfy verification.

#### Scenario: An unanchorable entry is reported

- GIVEN a declared entry with no textual anchor anywhere in its contract
- WHEN the executor transcribes that contract's requirements
- THEN it reports the entry by file, block, and id, and leaves the header
  unmodified pending an operator ruling

#### Scenario: The executor never invents or deletes to clear the gate

- GIVEN the same unanchorable entry
- WHEN the executor prepares its report
- THEN the entry is neither removed from the header nor given a fabricated
  `source.quote`
