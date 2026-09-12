# implementation-block-locator Specification

## Purpose

The numbered-entry locator `cmd_compose`, `cmd_admit`, and
`remedy_compatibility` use to find and identify a document's declared
entries becomes profile-supplied rather than a hardcoded module-level
`TAG_RE`/`DISPLAY_BLOCK_RE` pair — mirroring the precedent
`preservation-math.ts`/`preservation-experimental.ts` already set on the
deliberation side for the identical problem (M1: composition cannot be
mirrored by parameterizing a regex, because an experiments document has no
LaTeX display blocks at all). This capability also closes the defect the
current hardcoding causes: `remedy_compatibility`'s field lookup reading
document 0's scalar keys regardless of which document a finding names.

## Requirements

### Requirement: The Locator Is Profile-Supplied, Not A Hardcoded Module Constant

`cmd_compose`'s, `cmd_admit`'s, and `remedy_compatibility`'s identification
of a document's numbered declared entries MUST resolve through the
profile rather than the engine's own `TAG_RE`/`DISPLAY_BLOCK_RE`
constants, so a document whose declared form is not `\tag{}`/`$$…$$` can
supply its own locator without touching the shared engine.

#### Scenario: The existing single-document corpus is unaffected
- GIVEN `proposal-implementation`'s profile, whose declared form is
  `\tag{}`/`$$…$$`
- WHEN the locator resolves for it
- THEN it behaves byte-identically to the pre-capability hardcoded
  `TAG_RE`/`DISPLAY_BLOCK_RE`, and `tests/seal/`'s 28 digests are unmoved

#### Scenario: A document whose declared form is not LaTeX supplies its own locator
- GIVEN a profile declaring a locator matching its own document's real
  numbered-entry form
- WHEN `cmd_compose`/`cmd_admit`/`remedy_compatibility` run against that
  document
- THEN entries are located and identified using the declared locator, not
  the LaTeX-shaped one

### Requirement: All Three `TAG_RE` Readers And The One `DISPLAY_BLOCK_RE` Reader Are Repointed Together

`remedy_compatibility`, `cmd_compose`'s tag identification, `cmd_admit`,
and `cmd_compose`'s display-block matching MUST all resolve through the
same profile indirection. None of the four MUST continue reading the
module-level constant directly once this capability lands — a locator
change repointing three of the four and leaving the fourth on the old
constant is not a complete migration.

#### Scenario: A locator change is observed uniformly at all four sites
- GIVEN a profile's locator is changed
- WHEN each of the four consumer sites runs against the same document
- THEN all four reflect the new locator; none still reads the old
  module-level constant

#### Scenario: A site left on the old constant is caught
- GIVEN a mutation that reverts one of the four sites to the old
  module-level `TAG_RE`/`DISPLAY_BLOCK_RE` while the other three resolve
  through the profile
- WHEN a case exercising a non-LaTeX locator runs against that one site
- THEN it disagrees with the other three, and a comparison test fails,
  naming the site still reading the old constant

### Requirement: `remedy_compatibility`'s Field Lookup Uses The Named Document's Own Keys

When a finding names a document beyond index 0, `remedy_compatibility`'s
locus-field lookup MUST use that document's own resolved
`locus_key`/`remedy_locus_key` (its own per-`documents[N]` vocabulary),
never document 0's module-level `LOCUS_KEY`/`REMEDY_LOCUS_KEY` scalars.
This closes the defect where a finding naming `documents[1]` had its
fields looked up under document 0's keys, found nothing, and read as
compatible.

#### Scenario: A finding naming a second document is checked against its own keys
- GIVEN a finding naming `documents[1]`, whose own vocabulary declares
  `equations`/`remedy_equations`, and a `remedy_equations` locus absent
  from the proposal
- WHEN `remedy_compatibility` runs
- THEN the absence is reported, where before this capability it read as
  compatible

#### Scenario: The single-document behavior is unchanged
- GIVEN a one-document profile
- WHEN `remedy_compatibility` runs
- THEN its output is byte-identical to before this capability

#### Scenario: A mutation reverting to document-0 keys is caught
- GIVEN a mutation that reverts the lookup to the module-level
  `LOCUS_KEY`/`REMEDY_LOCUS_KEY` scalars for every document
- WHEN the `documents[1]`-naming case above runs
- THEN it reads compatible again and the corpus case fails, naming the
  reverted lookup

## Boundary (explicitly not built here)

Whether a document declares any locator at all — a document with no
numbered display entries may legitimately declare none — and what
`compose`/`admit` do for such a document are governed by
`implementation-per-document-vocabulary` and `experimental-implementation-skill`
respectively, not by this capability, which governs only how a declared
locator is found and used once it exists.
