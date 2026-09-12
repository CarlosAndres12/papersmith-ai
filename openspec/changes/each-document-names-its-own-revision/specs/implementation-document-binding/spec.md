# Delta for implementation-document-binding

**Budget note.** This delta exceeds the default word budget, deliberately, on
the precedent this capability's own base spec already set: the defect this
change amends reads green, and naming the evidence — including the two
mandatory strict-TDD requirements below — is the whole point of writing it
down instead of just fixing code.

## ADDED Requirements

### Requirement: Each Document's Revision Name Is Its Own, Never Shared

The resolver MUST NOT reuse one document's revision name to resolve another
document's revision text. Each entry in `documents` MUST be resolved
against its own directory, under its own naming convention, independently
of every other entry. An explicit revision pin supplied for one document
MUST NOT be inferred for, or applied to, any other document.

#### Scenario: Two unrelated stems resolve independently
- GIVEN a two-document profile whose documents use unrelated naming
  conventions (e.g. `research-concept-r01.md` and
  `experiments-slug-v01.md`) and no cross-document name is asserted
- WHEN a binding-write command runs
- THEN each document's own revision name resolves from its own root, and
  the two resolved names differ

#### Scenario: Pinning one document names only that document
- GIVEN document 0 is pinned by an explicit revision argument and document
  1 is not
- WHEN the command resolves document 1's revision
- THEN document 1's name is resolved from document 1's own root, never
  set to document 0's pinned name

### Requirement: An Unnamed Document's Revision Is Discovered In Its Own Root

On a first invocation, when no carrier has yet recorded a name for a
document and no explicit pin names it, the system MUST derive that
document's revision name by discovery scoped to that document's own
directory — the same family-derivation strategy `revision_discovery`
already applies to document 0 (newest same-family candidate by digit
ordering, ownership decided by the managed-artifact marker when present),
never a hardcoded per-skill naming convention asserted from outside that
document's own data.

#### Scenario: An unpinned second document discovers its own newest candidate
- GIVEN a two-document profile and no `--revision` naming document 1
- WHEN a binding-write command runs
- THEN document 1's revision name is discovered from candidates present
  in document 1's own directory, using document 1's own naming pattern

#### Scenario: An explicit pin is honored verbatim, without discovery
- GIVEN an explicit revision name supplied for a document
- WHEN that document's revision resolves
- THEN the supplied name is used as given; no discovery search runs for
  that document

### Requirement: Revision Discovery And The Verify Fidelity Fold Run Per Document

`revision_discovery`/`latest_revision` MUST accept the index of the
document they resolve against. `cmd_verify`'s per-document fidelity fold
MUST seed each document's own discovery family from that document's own
data (its own declared contract or its own modules' provenance), never
from another document's discovered or pinned name.

#### Scenario: Independent fidelity discovery per document
- GIVEN a two-document profile where document 0's revision has advanced
  and document 1's has not
- WHEN `cmd_verify` computes fidelity by document
- THEN each document's discovered revision is derived from its own
  directory's candidates, never from the other document's

#### Scenario: A newer candidate in one document does not affect the other
- GIVEN document 1's own directory contains a newer same-family candidate
  than the name currently bound, and document 0's directory does not
- WHEN `verify` runs with no explicit pin
- THEN document 1's fidelity reports its own newest candidate,
  independent of what document 0 discovered

### Requirement: An Unreadable Declared Document Refuses At Every Binding-Write Site

When a document beyond index 0 is declared (`len(documents) > 1`) and its
resolved revision name — whether explicit or discovered — does not read
from that document's own root, every binding-write site (`cmd_admit`,
`cmd_position`, `cmd_gate`, `cmd_offer`, `cmd_close`,
`_authorization_binding`) MUST refuse by a named refusal code identifying
the affected document, and MUST NOT write a `sha256: None` (or equivalent
null) entry into any carrier (`documents`/`documentRevisions`, the
position header's `documents=` group, `admissibility.json`). The new code
MUST join `reachable_refusal_codes`'s derived roster. `cmd_verify`'s
per-document fidelity fold MUST NOT refuse for the identical condition —
it already answers the named status `"unknown"`, preserving
`revision_discovery`'s standing "reported, never refused; verify is a
reader" position.

#### Scenario: A binding-write site refuses on an unreadable extra document
- GIVEN a two-document profile where document 1's resolved revision name
  is not readable in document 1's own directory
- WHEN any binding-write command runs
- THEN it refuses by a named code identifying document 1, and no carrier
  gains a `documents`/`documentRevisions` entry with a null sha

#### Scenario: Verify reports the same condition without refusing
- GIVEN the identical unreadable-document condition
- WHEN `cmd_verify` runs
- THEN it reports `"unknown"` for that document's fidelity status and
  does not refuse

### Requirement: A Committed Record Written Under The Shared-Name Assumption Remains Valid, Unedited

Every already-committed `documents`/`documentRevisions` entry — including
one where two entries happen to carry an identical `revision` string,
written before this capability existed — MUST continue to read as a
valid per-document binding after this capability lands. This capability
changes how a NEW entry's name is derived; it MUST NOT change what shape
a reader or validator holds an existing entry to. No already-committed
record MUST be edited, re-digested, or migrated to satisfy this change,
and `_AUTHORIZATION_BINDING_KEYS` MUST remain the literal 8-tuple it is
today — the field a shared old name occupied was always "a string naming
this document's bound revision"; two entries happening to share that
string was always incidental, never load-bearing, and remains so.

#### Scenario: A pre-existing shared-name ledger event still reads
- GIVEN a committed ledger event whose `documentRevisions` entries share
  one identical revision string, written before this capability landed
- WHEN that event is read by any consumer after this capability lands
- THEN it is accepted exactly as before, unedited and unre-digested

#### Scenario: A committed single-document token still re-derives its golden digest
- GIVEN a committed single-document binding fixture and its golden digest
- WHEN the gate authorization token is re-derived after this capability
  lands
- THEN the recomputed digest equals the golden, byte-identical

### Requirement: The Fixture Reshape Reddens The Existing Pair Tests Unassisted

The two-document fixture corpus (`tests/pair/corpus.py`,
`tests/fixtures/two_documents/impl_profile.py`, and the `REVISION`
constants in `TwoDocumentLifecycleTests`/`TwoDocumentPositionWriteTests`)
MUST use two genuinely different stems, two directories, and two version
letters — never one filename written into both document roots.

#### Scenario: The reshape alone reddens the suite, no assertion edited
- GIVEN the fixture reshaped to two distinct names, with the
  per-document resolution capability NOT yet landed
- WHEN the existing pair test suite runs
- THEN it fails, with no test assertion having been edited — proof the
  fixture, not the assertions, was carrying the false guard

#### Scenario: The reshape plus resolution together turn the suite green
- GIVEN the fixture reshaped AND per-document resolution landed
- WHEN the same suite runs
- THEN it passes

### Requirement: The New Refusal Is Reachable By Mutation, Not Only By Construction

A mutation MUST exist that removes or bypasses the new refusal's guard
(reverting to a silent null-sha path) and MUST turn a corpus case
observably red. The corpus case proving this MUST be independent of, and
MUST NOT be satisfiable merely by, fixture data written to pass it — a
weaker lock (one that only asserts the guard's presence in source, or
that runs no genuinely unreadable second document) MUST NOT survive this
mutation.

#### Scenario: Reverting the guard reddens the corpus
- GIVEN the refusal's guard mutated away, reverting to the pre-change
  silent-null behavior
- WHEN the corpus case exercising a genuinely unreadable extra document
  runs
- THEN it fails observably — the refusal is proven reachable, not merely
  present in source

## Boundary (unchanged from this capability's base spec)

The cross-document agreement verdict stays out of scope, as it already
was. Two further items outside this delta, named so a reader does not
wonder: the `vocabulary.names` union collision is the consuming skill's
declaration to narrow, not this engine's; and
`KitAgreementLockTests._profile`'s hardcoded skill name binds only once a
second `impl_profile.py` exists, which the next change introduces — this
delta does not touch it.
