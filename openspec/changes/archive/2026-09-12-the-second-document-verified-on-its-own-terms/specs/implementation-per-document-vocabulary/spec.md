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

## Boundary (explicitly not built here)

Which document's fold reads which resolved vocabulary, and whether the fold
treats an unresolved per-document value as `drift` or `unknown`, is
`implementation-document-binding`'s requirement, not this one. This
capability guarantees only that the correct value is *resolvable and named*
by index; consuming it per document is out of scope here.
