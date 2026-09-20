# Delta for Writing Orchestration

## ADDED Requirements

### Requirement: Section Binding Resolution Gates `write`, Not Only A Read-Only Verb

When `write` assembles the corpus for the block it is about to draft, ANY
refusal this change introduces — `SECTION_NOT_IN_SOURCE`,
`SECTION_TITLE_AMBIGUOUS`, `SECTION_BINDING_ABSENT`,
`SOURCE_LINEAGE_UNRESOLVED`, `SOURCE_REVISIONS_UNDECLARED` or
`MALFORMED_SOURCE_MARKER` — raised by that assembly
(`source-section-binding`) MUST stop `write` before the readiness stage
begins: no draft, evidence-audit, or contract-audit byte MUST be read for
that block, and the block MUST remain absent from `main.tex`. A read-only
verb (for example `phases`) having already reported the same broken binding
MUST NOT be treated as sufficient: `write` MUST perform its own corpus
assembly and raise the refusal itself, never rely on a cached report a
read-only verb produced earlier.

`EVIDENCE_ROOT_AMBIGUOUS` (`source-section-binding` spec, added by U2c) is
computed unconditionally for every root `Corpus.source_roots` names, inside
the SAME corpus assembly the six codes above reach `write` through — it
MUST therefore also stop `write` before the readiness stage begins, under
the identical rule: never reachable only from a read-only verb.

`SECTION_BINDING_ABSENT` (U3b correctness repair) is the one code among the
seven this `write` MUST reach through its own corpus assembly and NOWHERE
ELSE: an undecided binding is reported (`source-section-binding`,
`Corpus.undecided_bindings`) rather than refused everywhere else in the
skill, so `write`'s own assembly is not merely the FIRST place this code is
proven reachable — after U3b it is the ONLY place. This narrower rule does
not weaken the requirement above; it sharpens it for exactly the one code
whose unconditional form (U3's own shipped behaviour) forced an agent to
invent a binding rather than leave any assembly refusing.

#### Scenario: `write` refuses before drafting on an unresolved binding

- GIVEN a block whose bindable requirement's bound section title is absent
  from the resolved revision
- WHEN `write` is invoked for that block
- THEN it refuses `SECTION_NOT_IN_SOURCE` naming the binding, before the
  draft stage runs, and `main.tex` is byte-identical to its state before
  `write` ran

#### Scenario: `write` refuses on a source root whose revision rule is undeclared

- GIVEN a block whose bindable requirement names a lineage under a
  document-rooted source root that carries no `.paper-writing.json` marker
- WHEN `write` is invoked for that block
- THEN it refuses `SOURCE_REVISIONS_UNDECLARED` naming the root, before the
  draft stage runs — the marker codes reach `write` through the same corpus
  assembly as the binding codes, and MUST NOT be reachable only from a
  read-only verb

#### Scenario: A read-only verb's prior report does not excuse `write`'s own check

- GIVEN a corpus whose section binding a read-only verb already reported
  broken, unchanged since that report
- WHEN `write` is invoked afterward without that read-only verb having run
  again
- THEN `write` performs its own assembly and refuses the same way, rather
  than proceeding on the assumption that only the read-only verb needs to
  check

#### Scenario: An undecided binding reads fine and refuses only at `write`

- GIVEN a block whose bindable requirement's source root is measured but
  carries no `document` half at all — `source-section-binding` reports it
  `undecided`, not broken
- WHEN a read-only verb assembles the corpus, and separately `write` is
  invoked for that exact block
- THEN the read-only verb's assembly raises nothing, and `write` refuses
  `SECTION_BINDING_ABSENT` naming the block and the fact id, before the
  draft stage runs

#### Scenario: `write` refuses when more than one `guidance/` folder is classed evidence

- GIVEN more than one folder under `guidance/` classed `'evidence'`
- WHEN `write` is invoked for any block, whether or not it names a
  `dataset` binding
- THEN it refuses `EVIDENCE_ROOT_AMBIGUOUS` naming every candidate folder,
  before the draft stage runs, since `Corpus.source_roots` is computed for
  every root unconditionally as part of the same corpus assembly

#### Scenario: Mutation — wiring the guard only into the read-only verb is caught

- GIVEN the guard implemented so that only the read-only verb calls the
  section-existence check and `write` skips it
- WHEN a test drafts a block whose binding is broken by directly invoking
  `write`, never the read-only verb
- THEN the test fails, since `write` would proceed and draft the block
  instead of refusing

### Requirement: `SECTION_BINDING_ABSENT` Names Its Own Next Action

`SECTION_BINDING_ABSENT`'s own refusal detail MUST name the block, the
fact, and the source root, AND — read from disk at the moment of refusal,
never cached or hand-listed — every lineage that root currently carries,
each one's own current revision (or, for an identity-resolved root, its
own paper), and the section titles that revision actually holds right
now. It MUST also name the exact recording-verb invocation (naming this
refusal's own block and fact) that answers it. A person reading the
refusal MUST be able to answer it without opening anything else.

#### Scenario: The refusal names the block, fact, root and disk-derived candidates

- GIVEN a bindable, measured entry with no binding, under a root carrying
  more than one revision of the same lineage
- WHEN `write` refuses `SECTION_BINDING_ABSENT` for it
- THEN the detail names the block, the fact, the root, the CURRENT
  (highest-ordinal) revision only — never an older one — and every
  section title that revision carries

#### Scenario: Mutation — reverting the detail to a bare message is caught

- GIVEN the refusal detail reverted to name only the block, the fact and
  the root, with no disk-derived candidates
- WHEN a test asserts the detail names a candidate section title read
  from disk
- THEN the test fails, since the bare message carries nothing to answer
  the refusal with
