# Delta for Writing Orchestration

## ADDED Requirements

### Requirement: Section Binding Resolution Gates `write`, Not Only A Read-Only Verb

When `write` assembles the corpus for the block it is about to draft, any
`SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`, `SECTION_BINDING_ABSENT`,
or `SOURCE_LINEAGE_UNRESOLVED` refusal raised by that assembly
(`source-section-binding`) MUST stop `write` before the readiness stage
begins: no draft, evidence-audit, or contract-audit byte MUST be read for
that block, and the block MUST remain absent from `main.tex`. A read-only
verb (for example `phases`) having already reported the same broken binding
MUST NOT be treated as sufficient: `write` MUST perform its own corpus
assembly and raise the refusal itself, never rely on a cached report a
read-only verb produced earlier.

#### Scenario: `write` refuses before drafting on an unresolved binding

- GIVEN a block whose bindable requirement's bound section title is absent
  from the resolved revision
- WHEN `write` is invoked for that block
- THEN it refuses `SECTION_NOT_IN_SOURCE` naming the binding, before the
  draft stage runs, and `main.tex` is byte-identical to its state before
  `write` ran

#### Scenario: A read-only verb's prior report does not excuse `write`'s own check

- GIVEN a corpus whose section binding a read-only verb already reported
  broken, unchanged since that report
- WHEN `write` is invoked afterward without that read-only verb having run
  again
- THEN `write` performs its own assembly and refuses the same way, rather
  than proceeding on the assumption that only the read-only verb needs to
  check

#### Scenario: Mutation — wiring the guard only into the read-only verb is caught

- GIVEN the guard implemented so that only the read-only verb calls the
  section-existence check and `write` skips it
- WHEN a test drafts a block whose binding is broken by directly invoking
  `write`, never the read-only verb
- THEN the test fails, since `write` would proceed and draft the block
  instead of refusing
