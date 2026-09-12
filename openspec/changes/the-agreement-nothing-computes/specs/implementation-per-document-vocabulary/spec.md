# Delta for implementation-per-document-vocabulary

> **Tier ruling, 2026-09-12.** Both leaves below were drafted as MAY-declare,
> on the five-leaf claim-vocabulary tier. They are ruled onto
> `dataset_marker`'s **required per-entry** tier instead, measured against
> `impl_domain_profile.py`'s own two silence tiers rather than chosen by
> style. `_DOCUMENT_VOCABULARY_LEAVES`'s silence is safe because its fallback
> is the **host's own** top-level `provenance.*`/`findings.*` values — the
> same host declared them. Neither leaf below has a host-declared fallback: a
> silent `block_locator` falls back to the engine's `TAG_RE`/
> `DISPLAY_BLOCK_RE`, and a silent `cross_citation` falls back to computing
> no agreement at all. Both silences are the shape this forge removes, not
> the shape it tolerates. The two requirements below are therefore written
> against `documents[N].dataset_marker`'s precedent — required, with an
> explicit `None` where "this document owes nothing here" is a real state.

## ADDED Requirements

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

Whether the crossing check refuses, and what it does with a resolved
`cross_citation` or a resolved locator, belongs to
`implementation-cross-document-agreement` and `implementation-block-locator`
respectively — this capability guarantees only that each value is declared,
validated and named by index, the same boundary it already draws for the
five claim-vocabulary leaves and for `dataset_marker`.
