# Delta for implementation-per-document-vocabulary

## ADDED Requirements

### Requirement: A Cross-Document Citation Pattern Is An Independently Declarable Per-Document Leaf

A `documents[N]` entry MAY declare a `cross_citation_pattern` leaf (the
form an experiments document uses to cite a proposal claim). This leaf
follows the same validation architecture as the five existing claim-
vocabulary leaves: presence-checked at resolve time, refused by its exact
indexed path when malformed, and its silence on a profile that predates
this leaf or simply does not declare it MUST NOT be treated as an error —
the same "declaring is the remedy, absence is never a forced edit" rule
`implementation-per-document-vocabulary`'s existing requirements already
hold for the five leaves.

#### Scenario: A declared cross-document pattern is used
- GIVEN `documents[0]` declares a `cross_citation_pattern`
- WHEN the resolver resolves it
- THEN it is validated the same way `citation_pattern` is, and used by
  `implementation-cross-document-agreement`'s crossing check

#### Scenario: An undeclared profile is not refused for the leaf's absence
- GIVEN a profile declaring no `cross_citation_pattern` anywhere
- WHEN it resolves
- THEN no refusal names the leaf, and the profile behaves exactly as
  before this leaf existed

#### Scenario: A malformed pattern refuses by its exact indexed name
- GIVEN `documents[0].cross_citation_pattern` declared but failing to
  compile
- WHEN the resolver validates it
- THEN it refuses, naming `documents[0].cross_citation_pattern` exactly

### Requirement: A Block Locator Is An Independently Declarable Per-Document Leaf

A `documents[N]` entry MAY declare its own block locator (the mechanism
`implementation-block-locator` uses to find and identify that document's
numbered declared entries). Declaring it on one entry MUST NOT require
any other entry to declare one; an entry declaring none MUST resolve
`cmd_compose`/`cmd_admit`/`remedy_compatibility` to the same refusal or
absence behavior a document with no numbered entries had before this leaf
existed — never a forced fallback to another document's locator.

#### Scenario: One document declares a locator, its sibling declares none
- GIVEN `documents[1]` declares a block locator and `documents[0]` declares
  none
- WHEN `cmd_compose`/`cmd_admit` run against each document
- THEN `documents[1]`'s declared locator is used for it, and `documents[0]`
  is unaffected by `documents[1]`'s declaration

#### Scenario: No document's locator is inferred from another's
- GIVEN neither document declares a locator
- WHEN the resolver resolves both
- THEN neither is refused for the leaf's absence, and neither borrows the
  other's

## Boundary (explicitly not built here)

Whether the crossing check refuses, and what it does with a resolved
`cross_citation_pattern` or a resolved locator, belongs to
`implementation-cross-document-agreement` and `implementation-block-locator`
respectively — this capability guarantees only that each value is
resolvable and named by index, the same boundary it already draws for the
five existing claim-vocabulary leaves.
