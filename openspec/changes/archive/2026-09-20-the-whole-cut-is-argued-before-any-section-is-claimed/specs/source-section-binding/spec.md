# Delta for Source Section Binding

## MODIFIED Requirements

### Requirement: A Binding Is Recorded By Using The Skill, Never By Editing A Shipped File

An operator answers `SECTION_BINDING_ABSENT` by recording a binding through
a dedicated verb (`bind`) — naming the block, the fact, the source
document's lineage, and one or more section titles — never by hand-editing
a shipped section contract under `sections/*.md`, and never by an agent
inferring a binding from conversation prose. The recorded binding is
stored where the paper's own decisions already live, never in a file that
ships with the forge: `sections/*.md` MUST NOT carry a transcribed
`document` binding as a mechanism for satisfying this obligation. The verb
MUST refuse to record an empty lineage or an empty set of section titles,
and MUST refuse to record a binding for a fact that is not bindable
(`Requirement: Bindable Facts Are Derived, Never Listed`) — recording an
answer to a question that was never asked is itself a defect. A binding,
once recorded, MUST be reversible: reopening it clears its fixed state
without touching any other recorded binding.

For a `(block, fact)` whose source root is **measured**, `bind` MUST also
refuse unless a recorded `separate` round satisfies **all four** checks:
(1) its id matches the root, the given `--lineage`, and the revision
**resolved right now** from disk; (2) its recorded document digest equals
the sha256 of that document's bytes **read right now**; (3) its recorded
score total is **zero** — settled, not merely recorded; (4) its
`assignments` name an entry for exactly this `(block, fact)` whose title
set is **equal**, as a set, to the titles being bound. Any check failing
MUST refuse `BINDING_UNARGUED`, naming the block, the fact, the root, the
resolved revision, **which check failed**, and the exact `separate
--proposal <path>` invocation that would answer it; where a settled round
exists but names a different scope, both title sets are named verbatim;
where a round expired, the revision or digest it was scored against and the
one on disk now are both named. This precondition applies only to
recording (`--sections`); `--reopen` remains unguarded, since withdrawing a
claim never creates one. When the fact's source root is **unmeasured**,
`bind` records as it does today with no precondition, and its payload
reports `separation: unmeasured(<reason>)`. The guard MUST be enforced
inside `bind_section` itself, not only in the CLI command that calls it, so
no caller can route around it by skipping the CLI layer.

(Previously: recording had no precondition beyond an empty lineage, an
empty section set, and fact bindability — any `bind` invocation with valid
inputs recorded immediately, with no requirement that a whole-cut argument
had ever been made.)

#### Scenario: An operator records a binding through the skill

- GIVEN a bindable, measured entry with no binding yet
- WHEN an operator names the block, the fact, a lineage, and one or more
  section titles through the recording verb
- THEN the binding is recorded, and it is not written to any file under
  `sections/`

#### Scenario: Recording with no section title refuses

- GIVEN the recording verb invoked with no section title
- WHEN it runs
- THEN it refuses, naming that a section title is required

#### Scenario: Recording with no lineage refuses

- GIVEN the recording verb invoked with no lineage
- WHEN it runs
- THEN it refuses, naming that a lineage is required

#### Scenario: Recording a binding for a non-bindable fact refuses

- GIVEN a fact absent from `FACT_SOURCE_ROOT` (e.g. a produced fact)
- WHEN the recording verb is invoked naming that fact
- THEN it refuses, naming that the fact is not bindable

#### Scenario: Reopening one binding leaves a sibling binding untouched

- GIVEN two distinct recorded bindings
- WHEN one is reopened
- THEN the other still resolves exactly as it did before

#### Scenario: Recording with no settled round at all refuses `BINDING_UNARGUED`

- GIVEN a measured, bindable entry for `methods.block-b` and `formulation`
  with no `separate` round ever recorded for that lineage
- WHEN an operator invokes `bind --sections` naming that block, fact,
  lineage, and titles
- THEN it refuses `BINDING_UNARGUED`, naming the block, the fact, the root,
  the resolved revision, that no round exists, and the `separate
  --proposal <path>` invocation to run next

#### Scenario: Recording after a settled round naming the exact pair and titles succeeds

- GIVEN a settled `separate` round (total 0) resolved against the current
  revision and digest, whose `assignments` name `methods.block-b` /
  `formulation` with sections `{"2. Alignment estimators", "3. Proposed
  alignment objective"}`
- WHEN `bind --sections` is invoked naming that exact block, fact, and the
  identical title set
- THEN the binding is recorded with no refusal

#### Scenario: A settled round naming a different block refuses, naming both scopes

- GIVEN the same settled round, which names `methods.block-b`, not
  `methods.block-c`
- WHEN `bind --sections` is invoked naming `methods.block-c` for the same
  fact and lineage
- THEN it refuses `BINDING_UNARGUED`, naming that no settled round names
  `methods.block-c` for this fact

#### Scenario: Binding a subset of the argued titles refuses

- GIVEN the settled round above, arguing two titles for `methods.block-b`
- WHEN `bind --sections` is invoked naming only one of those two titles
- THEN it refuses `BINDING_UNARGUED` naming the argued title set and the
  narrower set being bound, verbatim, both

#### Scenario: Binding a superset of the argued titles refuses

- GIVEN the same settled round
- WHEN `bind --sections` is invoked naming both argued titles plus a third
  title the round never assigned to that block
- THEN it refuses `BINDING_UNARGUED` naming both title sets verbatim

#### Scenario: Title order does not matter — set equality, not sequence equality

- GIVEN the same settled round, arguing titles in one document order
- WHEN `bind --sections` is invoked naming the identical two titles in the
  opposite order
- THEN the binding is recorded with no refusal

#### Scenario: A new revision voids the licence

- GIVEN a settled round resolved and digested against `field-survey-r07.md`
- WHEN `field-survey-r08.md` is published and `bind --sections` is invoked
  naming the same block, fact, and titles
- THEN it refuses `BINDING_UNARGUED`, naming the revision the round was
  scored against and the revision resolved now

#### Scenario: An in-place rewrite voids the licence even at the same revision

- GIVEN a settled round resolved against `field-survey-r07.md`, digested at
  scoring time
- WHEN `field-survey-r07.md`'s bytes are rewritten in place under the same
  filename and `bind --sections` is invoked
- THEN it refuses `BINDING_UNARGUED`, naming the recorded digest and the
  digest read from disk now, both different

#### Scenario: An ingested document's licence expires only by digest, never by revision

- GIVEN a settled round scored against an `INGESTED` root's identity-
  resolved document
- WHEN that document is re-ingested with different content under the same
  identity and `bind --sections` is invoked
- THEN it refuses `BINDING_UNARGUED` by digest mismatch alone, with no
  revision-ordinal check ever applying to this root kind

#### Scenario: An unmeasured root bypasses the precondition entirely

- GIVEN a fact whose source root reports `unmeasured`
- WHEN `bind --sections` is invoked naming that fact, with no round ever
  recorded
- THEN it records as before with no refusal, and its payload reports
  `separation: unmeasured(<reason>)`

#### Scenario: `--reopen` is never blocked by this precondition

- GIVEN a recorded binding with no settled round at all
- WHEN `bind --reopen` is invoked for that binding
- THEN it succeeds, since withdrawal creates no claim to argue for

#### Scenario: The guard fires even when `bind_section` is called directly

- GIVEN no settled round recorded, and `bind_section` invoked directly,
  bypassing the CLI's `cmd_bind` entirely
- WHEN it runs
- THEN it still refuses `BINDING_UNARGUED` — a guard reachable only through
  the CLI is a guard an applier can route around

#### Scenario: Mutation — weakening title-set equality to non-emptiness is caught

- GIVEN check 4 mutated from set equality to "the argued title set is
  non-empty"
- WHEN the subset-bind and wrong-block fixtures above are run
- THEN both go red, because a licence for a different scope now passes
