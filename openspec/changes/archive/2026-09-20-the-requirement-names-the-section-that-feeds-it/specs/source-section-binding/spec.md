# Source Section Binding Specification

## Purpose

`requires_facts` entries prove, via `source.quote`, that a contract's own
prose asks for a fact (`requirement-transcription`). They have never proved
which part of the real source document answers it. This capability adds
that second half: an optional `document: {lineage, section}` binding
(`section-contract`) naming a document's lineage and the title of the
section — or, when more than one section feeds the same entry, the titles
of the sections — within it that feed one entry. It owns which facts a
binding may name (derived, never listed), lineage resolution to the current
revision on disk off a per-root `.paper-writing.json` marker's own declared
revision grammar, section existence and ambiguity by title (checked
independently per title when a binding names more than one), the report an
unmeasured root produces versus the refusal a document-rooted but
undeclared or malformed marker produces, the property that a version
bump whose bound titles survive costs no edit anywhere, and the report a
bindable-but-not-yet-decided binding produces (`undecided`) versus the
refusal that same binding produces the one time drafting actually depends
on it (`write`). A binding itself is answered by USING the skill — a
dedicated recording verb, never a hand edit to a shipped section contract
and never an agent inferring one from conversation prose — and the corpus
resolves a fact's binding from whichever of two sources (the header's own
shape, or a recorded one) names it, refusing when both name it and
disagree.

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

### Requirement: A Bindable Fact With No Binding Is Undecided, And Refuses Only At `write`

A `requires_facts` entry naming a bindable fact whose source root is
MEASURED but carrying no `document` half is **undecided**: assembling the
corpus for a read-only purpose MUST NOT refuse for it, and MUST instead
report it — the same shape `source_roots` already uses to report an
unmeasured root, never a second, invented reporting convention. A bindable
entry left undecided MUST refuse `SECTION_BINDING_ABSENT` naming the owning
block and the fact id **only** at the one moment that undecided state would
otherwise let a false claim through: `write` assembling the corpus for the
block it is about to draft (`writing-orchestration`, `Requirement: Section
Binding Resolution Gates write`). No other verb — read-only or otherwise —
may turn an undecided binding into this refusal.

An apply agent facing a genuinely undecided binding MUST NOT invent one to
keep the corpus assemblable: reporting `undecided` at read-time, refusing
only at `write`, exists precisely so nothing forces that invention. The
obligation itself stays unconditional — it never consults a block's own
`optional` flag — only WHEN it can fire changed.

#### Scenario: A bound bindable entry parses

- GIVEN a `requires_facts` entry naming `formulation` with a `document` half
- WHEN the corpus is assembled
- THEN it accepts the entry, pending its own resolution checks below

#### Scenario: An unbound bindable entry is reported undecided, not refused

- GIVEN a `requires_facts` entry naming `formulation` with no `document`
  half, under a source root the corpus reports MEASURED
- WHEN the corpus is assembled for a read-only purpose
- THEN it accepts the entry with no refusal, and reports it `undecided`,
  naming the block, the fact id, and the root

#### Scenario: The same unbound entry refuses only when `write` assembles it

- GIVEN the same unbound bindable entry
- WHEN `write` assembles the corpus for the block that entry belongs to
- THEN it refuses `SECTION_BINDING_ABSENT` naming the block and
  `formulation`

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

### Requirement: A Recorded Binding And A Header-Declared Binding Must Agree

The corpus resolves a `requires_facts` entry's binding from two possible
sources: the contract header's own `document` half (`section-contract`),
still a validated, parseable shape, and a binding recorded through the
skill (the requirement above). A fact named by only one source uses that
source. A fact named by BOTH sources MUST name the identical lineage and
the identical set of section titles, or the corpus MUST refuse, naming the
block, the fact, and both sides' own values verbatim — an agreement is
never assumed by precedence, and a disagreement between two sources both
claiming to answer the same question is surfaced, never silently resolved
in favor of either one.

#### Scenario: A header binding and a recorded binding that agree are not a conflict

- GIVEN a `requires_facts` entry whose header names `document: {lineage,
  section}`, and a recorded binding naming the identical lineage and
  section for the same block and fact
- WHEN the corpus is assembled
- THEN it accepts the entry with no refusal

#### Scenario: A header binding and a recorded binding that disagree refuse

- GIVEN the same entry, but the recorded binding names a different section
  title than the header's own `document.section`
- WHEN the corpus is assembled
- THEN it refuses, naming the block, the fact, and both the header's own
  value and the recorded value

### Requirement: Lineage Resolves To The Current Revision On Disk

`document.lineage` MUST resolve to the current revision file under
`FACT_SOURCE_ROOT[fact]`'s own root, matched by a revision pattern read from
an on-disk declaration — never a pattern literal written into the engine. A
lineage that resolves to anything other than **exactly one** matching file
under its root MUST refuse `SOURCE_LINEAGE_UNRESOLVED` naming the lineage,
the root, and every candidate found: zero matches, and two or more matches
(a tie between two spellings of one ordinal, e.g. `r21.md` alongside
`r021.md`) both refuse under this one code, never a seventh.

#### Scenario: A lineage resolves to the latest revision

- GIVEN `proposals/` holding `research-concept-r14` through `research-concept-r21`
- WHEN lineage `research-concept` is resolved
- THEN it resolves to `research-concept-r21`, the current revision

#### Scenario: An unresolved lineage refuses

- GIVEN a `document.lineage` naming a lineage with no matching file under
  its root
- WHEN resolution runs
- THEN it refuses `SOURCE_LINEAGE_UNRESOLVED` naming the lineage and the root

#### Scenario: A tie between two spellings of one ordinal refuses

- GIVEN `proposals/` holding both `research-concept-r21.md` and
  `research-concept-r021.md` — two spellings of the same ordinal
- WHEN lineage `research-concept` is resolved
- THEN it refuses `SOURCE_LINEAGE_UNRESOLVED` naming the lineage and both
  candidates, rather than silently picking either one

### Requirement: A Document-Rooted Source With No Marker Refuses

A root is **document-rooted** when it resolves to a directory under the
source base that contains at least one `*.md` file — a property computed on
disk, never keyed by a fact id. A document-rooted root that carries no
`<root>/.paper-writing.json` marker MUST refuse `SOURCE_REVISIONS_UNDECLARED`
naming the root. A document-rooted root MUST NOT degrade to the `unmeasured`
report for a missing marker: deleting a marker MUST NOT silently switch the
existence guard off.

#### Scenario: A document-rooted root without a marker refuses

- GIVEN `proposals/` holding one or more `*.md` files and no
  `.paper-writing.json` marker
- WHEN a binding under `proposals` is resolved
- THEN it refuses `SOURCE_REVISIONS_UNDECLARED` naming `proposals`

#### Scenario: Deleting the marker does not degrade to unmeasured

- GIVEN `proposals/` already document-rooted and marked, with a binding that
  resolves cleanly
- WHEN the marker file is deleted and the same binding is resolved again
- THEN it refuses `SOURCE_REVISIONS_UNDECLARED`, never a silent `unmeasured`
  report — an unmeasured report is reserved for a root that is not
  document-rooted at all

### Requirement: The Marker Grammar Is Validated, And Disjoint From `guidance/`'s

A `<root>/.paper-writing.json` marker MUST parse as UTF-8 JSON holding
exactly one top-level key, `revisions`, an object holding exactly
`revision_prefix` (string) and `ordinal_digits` (integer) — both required,
no other key admitted at either level. Content that is not valid UTF-8, not
valid JSON, not an object, missing either required key, carrying an unknown
key at either level, or carrying a wrong-typed value for either key MUST
refuse `MALFORMED_SOURCE_MARKER` naming the offending file and the missing,
unknown, or wrong-typed key. The source-root marker reader MUST NOT accept
`guidance/`'s own `class` key, and the `guidance/` marker reader MUST NOT
accept `revisions`: the two markers share a filename but carry disjoint key
sets, and each reader refuses loudly on the other's shape rather than
silently reusing it.

#### Scenario: A valid marker parses

- GIVEN `proposals/.paper-writing.json` holding `{"revisions":
  {"revision_prefix": "r", "ordinal_digits": 2}}`
- WHEN the marker is read
- THEN it parses with no refusal

#### Scenario: A non-JSON marker refuses

- GIVEN a `.paper-writing.json` file whose content is not valid JSON
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming the file

#### Scenario: A marker missing a required key refuses

- GIVEN a marker's `revisions` object carrying `revision_prefix` but no
  `ordinal_digits`
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `ordinal_digits`

#### Scenario: A marker carrying an unknown key refuses

- GIVEN a marker's `revisions` object carrying a third key beside
  `revision_prefix` and `ordinal_digits`
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming the unknown key

#### Scenario: A marker with a wrong-typed value refuses

- GIVEN a marker declaring `ordinal_digits: "2"` (a string, not an integer)
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `ordinal_digits`

#### Scenario: The source-root reader refuses a `guidance/`-shaped marker

- GIVEN a `.paper-writing.json` under a source root carrying `{"class":
  "style-reference"}` — `guidance/`'s own shape — instead of `revisions`
- WHEN the source-root marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `revisions` as missing,
  rather than silently accepting `class`

#### Scenario: The marker's declared prefix and digits drive resolution, never a literal

- GIVEN a marker declaring `{"revisions": {"revision_prefix": "v",
  "ordinal_digits": 3}}` and a root holding `lineage-v007.md`
- WHEN lineage `lineage` is resolved
- THEN it resolves to `lineage-v007.md`, off the marker's own declared
  prefix and digit count — proving no revision-pattern literal governs
  resolution

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

### Requirement: A Binding May Name More Than One Section

`document.section` MAY name more than one section of the same lineage: a
contract's own prose block may draw from several sections of the source
document (for example, a block that borrows both the foundational theory
sections and the proposal sections). Each named title is resolved and
checked independently, exactly as a single-title binding is: a title
matching zero headings MUST refuse `SECTION_NOT_IN_SOURCE` naming that
title specifically, and a title matching two or more headings MUST refuse
`SECTION_TITLE_AMBIGUOUS` naming that title specifically — a refusal MUST
name WHICH title failed, never merely the owning block, and a resolvable
title MUST NOT be masked by a sibling title's own failure. The number of
blocks a contract declares MUST NOT be driven by how many sections a
source document currently has: a binding names as many sections as feed
it, and that block count never moves just because a later revision of the
source document grows or shrinks its own section count.

#### Scenario: A binding naming two sections resolves both

- GIVEN a binding naming lineage `research-concept` and sections `["1.
  Fundamentos de métodos de kernel", "2. Estimación de la entropía de
  Rényi basada en kernels"]`, both present as headings in the resolved
  revision
- WHEN the corpus is assembled
- THEN it accepts the entry with no refusal

#### Scenario: One missing title among several refuses by naming only that title

- GIVEN the same binding, but the resolved revision no longer carries "2.
  Estimación de la entropía de Rényi basada en kernels" as a heading
- WHEN the corpus is assembled
- THEN it refuses `SECTION_NOT_IN_SOURCE` naming that missing title, and
  the detail does not name the sibling title that still resolves

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
