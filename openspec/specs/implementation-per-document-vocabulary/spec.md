# implementation-per-document-vocabulary Specification

## Purpose

The five claim-vocabulary leaves the shared implementation engine reads as
module-level scalars — `provenance.claim_key`, `findings.locus_key`,
`findings.remedy_locus_key`, `findings.notation_keys`,
`findings.citation_pattern` — become declarable per `documents[N]`, so a
second declared document can say its own claims are a different kind than
document 0's, and the resolver validates the shape of a resolved
`citation_pattern` regardless of where it was declared. This capability
governs the resolver-side leaves and their validation only; the fold that
consumes them per document belongs to `implementation-document-binding`.

**Budget note**, on the precedent this change's own proposal and
`implementation-document-binding/spec.md` set: this spec exceeds 650 words
because the reconciliation between "overlay, not replace" and "the existing
two-document fixture must keep resolving unedited" cannot be asserted without
being shown.

## Requirements

### Requirement: A Per-Document Vocabulary Leaf Overlays, Never Replaces, The Top-Level One

Each of the five leaves MUST be independently declarable inside any
`documents[N]` entry. When a document declares none of them, resolution MUST
fall back to the existing top-level `provenance.*`/`findings.*` scalar,
unchanged. Declaring a per-document leaf on one entry MUST NOT require any
other entry, or the top-level fields, to be edited or removed.

#### Scenario: A profile declaring no per-document override resolves unchanged
- GIVEN `proposal-implementation/impl_profile.py` and
  `tests/fixtures/two_documents/impl_profile.py`, neither declaring a
  per-document vocabulary override on any entry
- WHEN the resolver validates and resolves them after this capability lands
- THEN every document's vocabulary resolves to the existing top-level
  values, byte-identical to before this capability

#### Scenario: A declared per-document override is used instead of the top-level value
- GIVEN a document entry declaring its own `claim_key`
- WHEN the engine resolves that document's vocabulary
- THEN the declared per-document value is used, never the top-level
  `provenance.claim_key`

### Requirement: A Pre-Existing Profile's Silence On This Leaf Is Not An Error

A profile written before this capability existed, or one that simply
chooses not to declare a per-document override, MUST resolve identically —
there is no way to distinguish "written before this leaf existed" from "this
document has no override" and this capability MUST NOT try to. The remedy
for wanting a document's own vocabulary is declaring the leaf; it is never a
forced edit to an existing profile, and never a resolver refusal for its
absence.

#### Scenario: An old and a new silent profile resolve the same way
- GIVEN one profile that predates this capability and one written after it,
  both declaring no per-document override on any entry
- WHEN both resolve
- THEN both produce the same top-level-derived vocabulary, and neither is
  refused for the leaf's absence

### Requirement: `citation_pattern`'s Group Count Is Validated At Resolve Time, By Name

Wherever a `citation_pattern` resolves — the top-level fallback or a
per-document override — the resolver MUST compile it and refuse when the
compiled pattern does not expose exactly three capturing groups, matching
`_impact_class`'s `match.group(1) or match.group(2) or match.group(3)` read.
The refusal MUST name the exact leaf that failed: `documents[N].citation_pattern`
for a per-document override, `findings.citation_pattern` for the top-level
fallback.

#### Scenario: A two-group pattern refuses by name
- GIVEN a document's resolved `citation_pattern` compiles with two groups
- WHEN the resolver validates it
- THEN it refuses, naming that exact leaf, before any command runs

#### Scenario: A four-group pattern refuses by name
- GIVEN a document's resolved `citation_pattern` compiles with four groups
- WHEN the resolver validates it
- THEN it refuses, naming that exact leaf

#### Scenario: A three-group pattern passes
- GIVEN a document's resolved `citation_pattern` compiles with exactly
  three groups
- WHEN the resolver validates it
- THEN it accepts, and no refusal names that leaf

### Requirement: No Document's Vocabulary Is Inferred From Another Document's

The resolver MUST NOT derive one document's claim vocabulary from another
document's declared, discovered, or resolved value. Each entry's vocabulary
is either its own per-document declaration or the shared top-level fallback
— never a value copied or interpolated from a sibling entry.

#### Scenario: A second document's missing override does not borrow the first's declared value
- GIVEN document 0 declares a per-document `claim_key` override and
  document 1 declares none
- WHEN document 1's vocabulary resolves
- THEN it resolves to the top-level fallback, never to document 0's
  per-document override

### Requirement: A Cross-Document Citation Leaf Is Required Per Entry, Absent Only By An Explicit `None`

Every `documents[N]` entry MUST declare a `cross_citation` leaf, whose value
is either the literal `None` — stating out loud that this document cites no
other document — or a mapping carrying **both** `pattern` (the form this
document uses to cite another document's declared entries, with exactly one
capturing group) and `resolves_against` (the `label` of the document those
citations resolve against). The leaf's silence MUST be refused by its own
indexed name, never read as "this document crosses nothing": a two-document
profile that simply omits the leaf would compute no agreement and read
clean, which is a check measuring nothing rather than a document declaring
nothing.

The leaf is a mapping, not a flat `cross_citation_pattern` string, for a
measured reason: a pattern alone cannot carry its target, and the two ways
of inferring one — "the other document", or `index + 1` — are each undefined
or silently wrong the day a third document is declared. The nested shape and
its exact indexed sub-path refusals follow `documents[N].notation_keys`,
which already ships as a mapping leaf validated sub-key by sub-key
(`_NOTATION_KEYS_REQUIRED`, refusing `documents[N].notation_keys.locus` and
its two siblings by name).

It is NOT a member of `_DOCUMENT_VOCABULARY_LEAVES`: that tuple's
all-or-nothing rule governs five leaves this one overlays nothing of.

#### Scenario: A declared crossing is validated and used
- GIVEN `documents[0]` declares `cross_citation` with a `pattern` and a
  `resolves_against` naming another entry's `label`
- WHEN the resolver resolves it
- THEN the pattern is validated the way `citation_pattern` is — compiled at
  resolve time, refused by name if it does not compile — and used by
  `implementation-cross-document-agreement`'s crossing check

#### Scenario: An explicit `None` is accepted and crosses nothing
- GIVEN `documents[1].cross_citation` is the literal `None`
- WHEN the resolver resolves it
- THEN no refusal names the leaf, and that document participates in no
  crossing in either direction

#### Scenario: Omitting the leaf refuses by its own indexed name
- GIVEN a `documents[N]` entry declaring no `cross_citation` key at all
- WHEN the resolver validates it
- THEN it refuses, naming `documents[N].cross_citation` exactly — never a
  bare top-level name, and never a silent "crosses nothing"

#### Scenario: A malformed mapping refuses at its exact indexed sub-path
- GIVEN `documents[0].cross_citation` declared as a mapping that omits
  `resolves_against`, or whose `pattern` does not compile, or whose
  `pattern` has other than exactly one capturing group, or whose
  `resolves_against` names no declared `label` (or names its own entry)
- WHEN the resolver validates it
- THEN each refuses by name, naming
  `documents[0].cross_citation.resolves_against` or
  `documents[0].cross_citation.pattern` exactly — never the parent leaf
  alone

### Requirement: A Block Locator Is Required And Non-Nullable On Every `documents[N]` Entry

Every `documents[N]` entry MUST declare a `block_locator` carrying all three
sub-keys: `pattern` (how *this* document spells a declared numbered entry,
exactly one capturing group — the value), `block_pattern` (the enclosing
substitutable block), and `identity` (a `str.format` template with exactly
one field, named `value`). A missing sub-key MUST be refused at its exact
indexed path (`documents[1].block_locator.identity`), and a missing leaf at
`documents[N].block_locator`.

**No entry may borrow another entry's locator, and none may fall back to the
engine's own constants.** The engine's `TAG_RE`/`DISPLAY_BLOCK_RE` spell a
LaTeX display block. A document that is not LaTeX, resolved against them,
locates nothing and reports every declared locus unknown — which is exactly
the live defect `implementation-block-locator` exists to close. An optional
leaf whose absence behaviour is the defect is a decorative declaration: the
host that most needs it is the host that can silently omit it.

`None` is not accepted here, unlike `cross_citation`: every document has
declared entries somewhere in its own syntax, so a nullable locator would be
a leaf no profile ever has to mean, and a leaf nothing can be mutated away
from proves nothing.

Exactly **one** capturing group, not `citation_pattern`'s three: the
three-group rule exists because `_impact_class` reads
`group(1) or group(2) or group(3)`. The locator's reader takes one value, so
copying the three-group rule here would enforce a count nothing reads.

#### Scenario: Every shipped entry declares one, and the existing corpus is unmoved
- GIVEN `proposal-implementation`'s single `documents[0]` entry declaring
  today's exact hardcoded bytes as its `pattern`/`block_pattern`/`identity`
- WHEN the resolver resolves it and the locator's consumers run
- THEN behaviour is byte-identical to the pre-capability constants, and
  `tests/seal/`'s digests are unmoved — asserted, never inferred

#### Scenario: A missing sub-key refuses at its exact indexed path
- GIVEN `documents[1]` declares a `block_locator` omitting `identity`, and
  `documents[0]` declares a complete one
- WHEN the resolver validates the profile
- THEN it refuses, naming `documents[1].block_locator.identity` exactly, and
  `documents[1]` neither borrows `documents[0]`'s locator nor falls back to
  the engine's `TAG_RE`/`DISPLAY_BLOCK_RE`

#### Scenario: A wrong-shaped locator refuses by name
- GIVEN a `pattern` that does not compile, or one with zero, two or three
  capturing groups, or an `identity` whose `string.Formatter().parse` yields
  other than exactly one field named `value`
- WHEN the resolver validates it
- THEN each refuses by name at its exact indexed sub-path — including the
  three-group case, so that `citation_pattern`'s rule is not copied here by
  habit

## Boundary (explicitly not built here)

Which document's fold reads which resolved vocabulary, and whether the fold
treats an unresolved per-document value as `drift` or `unknown`, is
`implementation-document-binding`'s requirement, not this one. This
capability guarantees only that the correct value is *resolvable and named*
by index; consuming it per document is out of scope here.
