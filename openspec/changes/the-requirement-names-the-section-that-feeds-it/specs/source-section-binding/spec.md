# Source Section Binding Specification

## Purpose

`requires_facts` entries prove, via `source.quote`, that a contract's own
prose asks for a fact (`requirement-transcription`). They have never proved
which part of the real source document answers it. This capability adds
that second half: an optional `document: {lineage, section}` binding
(`section-contract`) naming a document's lineage and the title of the
section within it that feeds one entry. It owns which facts a binding may
name (derived, never listed), lineage resolution to the current revision on
disk, section existence and ambiguity by title, the report an unmeasured
root produces, and the property that a version bump whose bound titles
survive costs no edit anywhere.

## Requirements

### Requirement: Bindable Facts Are Derived, Never Listed

A fact is bindable **iff** it resolves through the declarable route and is a
key of `FACT_SOURCE_ROOT`. No engine-side list of fact ids identifies which
facts are bindable; membership in `FACT_SOURCE_ROOT` is the sole and only
test. The four PRODUCED facts (`contributions`, `problem-statement`, `gap`,
`limitations`) and the structural fact `skeleton` MUST NOT be treated as
bindable — they are excluded by their absence from `FACT_SOURCE_ROOT`, not
by a special case naming them.

#### Scenario: A document-rooted fact is bindable

- GIVEN `formulation`, a key of `FACT_SOURCE_ROOT`
- WHEN bindability is computed
- THEN it reports bindable

#### Scenario: A produced fact is never bindable

- GIVEN `gap`, produced by a block and absent from `FACT_SOURCE_ROOT`
- WHEN bindability is computed
- THEN it reports not bindable, with no special-cased exclusion naming `gap`

#### Scenario: Mutation — a sixth root widens bindability with no code change

- GIVEN `FACT_SOURCE_ROOT` extended with a sixth fact/root pair
- WHEN bindability is computed for that sixth fact
- THEN it reports bindable, proving the test is membership in the mapping
  and not a hand-maintained list elsewhere

### Requirement: A Bindable Fact With No Binding Refuses

A `requires_facts` entry naming a bindable fact but carrying no `document`
half MUST refuse `SECTION_BINDING_ABSENT` naming the owning block and the
fact id.

#### Scenario: A bound bindable entry parses

- GIVEN a `requires_facts` entry naming `formulation` with a `document` half
- WHEN the corpus is assembled
- THEN it accepts the entry, pending its own resolution checks below

#### Scenario: An unbound bindable entry refuses

- GIVEN a `requires_facts` entry naming `formulation` with no `document` half
- WHEN the corpus is assembled
- THEN it refuses `SECTION_BINDING_ABSENT` naming the block and `formulation`

### Requirement: Lineage Resolves To The Current Revision On Disk

`document.lineage` MUST resolve to the current revision file under
`FACT_SOURCE_ROOT[fact]`'s own root, matched by a revision pattern read from
an on-disk declaration — never a pattern literal written into the engine. A
lineage matching no file under its root MUST refuse
`SOURCE_LINEAGE_UNRESOLVED` naming the lineage and the root.

#### Scenario: A lineage resolves to the latest revision

- GIVEN `proposals/` holding `research-concept-r14` through `research-concept-r21`
- WHEN lineage `research-concept` is resolved
- THEN it resolves to `research-concept-r21`, the current revision

#### Scenario: An unresolved lineage refuses

- GIVEN a `document.lineage` naming a lineage with no matching file under
  its root
- WHEN resolution runs
- THEN it refuses `SOURCE_LINEAGE_UNRESOLVED` naming the lineage and the root

### Requirement: Section Existence And Ambiguity, By Title

A binding's `section` title MUST match exactly one heading returned by
segmenting the resolved revision's prose. A title matching zero headings
MUST refuse `SECTION_NOT_IN_SOURCE` naming the binding and the title. A
title matching two or more headings MUST refuse `SECTION_TITLE_AMBIGUOUS`
naming the binding and the title.

#### Scenario: A named title resolves

- GIVEN `research-concept-r21`'s headings include
  `3. Formulación MIL-CREDA y kernel de bolsas ponderado por relevancia`, and
  a binding naming that exact title
- WHEN section existence is checked
- THEN it resolves with no refusal

#### Scenario: An absent title refuses

- GIVEN a binding naming a title that matches no heading in the resolved
  revision
- WHEN section existence is checked
- THEN it refuses `SECTION_NOT_IN_SOURCE` naming the binding and the title

#### Scenario: An ambiguous title refuses

- GIVEN a resolved revision whose headings include the same title text twice
- WHEN section existence is checked for a binding naming that title
- THEN it refuses `SECTION_TITLE_AMBIGUOUS` naming the binding and the title

### Requirement: Publishing A Survived Revision Costs Nothing

When a new revision is published under an already-bound lineage and a bound
section's title still exists as a heading in that new revision, resolution
MUST succeed against the new revision with no edit to any existing binding.

#### Scenario: A version bump requires no edit

- GIVEN `mm-proposal`'s binding naming lineage `research-concept` and section
  title `3. Formulación MIL-CREDA y kernel de bolsas ponderado por
  relevancia`, resolved today against `r21`
- WHEN `research-concept-r22` is published with that exact title unchanged
- THEN the corpus assembles against `r22` with no refusal and no edit made
  to `mm-proposal`'s binding

#### Scenario: A version bump that drops the bound title refuses by name

- GIVEN the same binding
- WHEN `research-concept-r22` is published with section 3 split into `3.1`
  and `3.2`, so the exact bound title no longer exists as a heading
- THEN the corpus assembles against `r22` and refuses `SECTION_NOT_IN_SOURCE`
  naming `mm-proposal`'s binding

### Requirement: An Unmeasured Root Is Reported, Never Silently Passed

When `FACT_SOURCE_ROOT[fact]`'s root is absent or empty on disk, resolving
any binding requiring that fact MUST report `unmeasured` — never a refusal,
and never a silent treatment as resolved.

#### Scenario: An empty root reports unmeasured

- GIVEN `experiments/` holding only `.gitkeep` on this checkout, and a
  binding naming `experimental-design`
- WHEN that binding is resolved
- THEN it reports `unmeasured`, distinct from both a refusal and a
  successful resolution

#### Scenario: Unmeasured is never treated as satisfied

- GIVEN the same unmeasured binding
- WHEN a reader asks whether that binding's obligation is cleared
- THEN it reports unmeasured, not satisfied — an empty root never silently
  clears `SECTION_BINDING_ABSENT` or any other obligation
