# implementation-document-binding Specification

## Purpose

The wire shape of every revision binding in the shared implementation
engine — scalar under one declared document, pair under two — and the
stability guarantee for artifacts already committed into target repositories
(`position.jsonl` gate tokens, `admissibility.json`, the `AGREED.md` position
header). `implementation-engine-neutrality`'s Purpose explicitly excludes
this shape ("not … the scalar→pair revision shape (Cut 3)"); this capability
is that exclusion, filled in.

**Scope rule, absolute:** this capability makes a two-document pair
representable and provable. It computes no verdict over whether the two
documents agree — that judgment has no neutral formulation and belongs to
the consuming skill.

**Budget note:** this spec exceeds the default word budget, deliberately, on
the precedent `the-domain-crosses-the-seam` set. The fourth requirement below
is this change's own "spec it first and spec it hard" item; undersizing it
here would repeat the false-guard shape this project has already measured —
a proof demanded and then not actually written down.

## Requirements

### Requirement: Documents Are An Indexed List, Not A Scalar

The profile's `documents` field MUST be a list. The resolver MUST validate
each entry independently, by its index, and MUST name a missing or malformed
leaf by its exact indexed path (`documents[1].directory`), never by the bare
field name.

#### Scenario: A single-document profile validates as before
- GIVEN a profile declaring one document
- WHEN the resolver validates it
- THEN it accepts the same shape it accepted before this cut

#### Scenario: A second document's missing leaf refuses by its indexed name
- GIVEN a two-document profile with `documents[1].directory` omitted
- WHEN the resolver validates it
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming
  `documents[1].directory` exactly, not `documents.directory`

### Requirement: Every Scalar Revision Binding Is Byte-Identical Under One Document

Every site presently reading or writing a scalar `revision`/`revisionSha256`
(the `revisionSha256` sites, the `revision_source(args.revision)` call
sites, `module["stale"]`, `admissibility_record`, `position_state`'s
`boundTo`) MUST produce output byte-identical to its pre-cut behavior when
`len(documents) == 1`. This capability introduces no sanctioned delta at any
of these sites.

#### Scenario: The existing sealed corpus is unaffected
- GIVEN the existing sealed single-document corpus
- WHEN the seal is re-captured after this capability lands
- THEN every digest is byte-identical to its pre-cut golden

### Requirement: A Pair Wire Shape Exists Only Under Two Or More Documents

The same binding sites MUST accept and emit a per-document pair — one
revision and one sha per declared document — when `len(documents) > 1`, and
MUST NOT emit a pair shape under one document.

#### Scenario: Two documents produce two revision/sha pairs
- GIVEN a two-document profile and a case touching a revision-bound command
- WHEN the command runs
- THEN its output carries one revision and one sha256 per document, keyed by
  document identity

#### Scenario: A pair shape leaking under one document is caught
- GIVEN a single-document profile
- WHEN a mutation forces the pair shape at any revision-bound site
- THEN a test comparing output shape against the pre-cut single-document
  golden fails

### Requirement: The Gate Authorization Binding Dict Is Byte-Identical Under One Document, Proven By A Fixture Re-Derivation Test That Lands First

`_AUTHORIZATION_BINDING_KEYS` MUST carry a `revisionSha256` pair only when
`len(documents) > 1`; under one document, the binding dict passed to
`sha256(json.dumps({**own_binding, "session": …, "at": …, "mintOrdinal": …},
sort_keys=True))` MUST be byte-identical, key-for-key and value-shape-for-
value-shape, to its pre-cut form. This is the highest-risk requirement in
this capability: any change to that dict's *value shape* invalidates every
token already minted into a target repository's committed
`.implementation/position.jsonl` — a ledger that travels in clones.

A dedicated test MUST re-derive a gate token from a committed single-document
binding fixture and assert the resulting digest equals a golden captured
before any binding-shape work landed. That test's own `test(...)` commit
MUST precede, in git history, the commit that changes
`_AUTHORIZATION_BINDING_KEYS`'s shape.

#### Scenario: A committed fixture re-derives its exact pre-cut digest
- GIVEN a committed single-document binding fixture and its golden digest
- WHEN the token re-derivation test runs after this capability lands
- THEN the recomputed digest equals the golden, byte-identical

#### Scenario: The re-derivation test predates the binding-shape change in history
- GIVEN the repository's commit log
- WHEN the re-derivation test's commit and the binding-shape commit are
  located
- THEN the test's commit is an ancestor of the binding-shape commit

#### Scenario: A shape change is caught before it reaches a target
- GIVEN `_AUTHORIZATION_BINDING_KEYS`'s value shape is mutated under one
  document
- WHEN the re-derivation test runs
- THEN the digest differs from the golden and the test fails

### Requirement: The Position Header Binds A Revision/Sha Pair Per Document; A Legacy Single-Document Header Still Opens

`impl_position.py`'s header MUST bind N revisions and N shas under N declared
documents. A header written under the pre-cut single-document shape MUST
remain readable by both openers after this capability lands — it is a
pre-existing instance, not an invalid one, and rewriting it to satisfy the
new shape MUST NOT be its remedy.

#### Scenario: A single-document header still opens
- GIVEN an `AGREED.md` position header committed before this capability, in
  the pre-cut single-document shape
- WHEN either opener reads it after this capability lands
- THEN it opens successfully with the same `revision`/`sha256` values

#### Scenario: A two-document header binds both pairs
- GIVEN a two-document profile and a freshly written position header
- WHEN the header is opened
- THEN it carries one revision and one sha256 per declared document

### Requirement: `admissibility.json` Is Keyed By Document, With A Dual-Shape Reader

Newly written `admissibility.json` files MUST key their ruling by document.
An existing `admissibility.json` written in the pre-cut scalar shape MUST
remain valid and readable by a dual-shape reader — it falls outside the new
writer's domain rather than becoming invalid, and no migration MUST edit it
in place.

#### Scenario: A scalar-shape admissibility file still reads
- GIVEN a committed `admissibility.json` fixture in the pre-cut scalar shape
- WHEN it is read after this capability lands
- THEN its existing ruling is returned unchanged

#### Scenario: A two-document ruling is keyed by document
- GIVEN a two-document profile and a freshly recorded ruling
- WHEN `admissibility.json` is written
- THEN each document's ruling is keyed by that document's identity,
  independently readable

### Requirement: `well_formed` Demands `document` Only When More Than One Document Is Declared

`well_formed` MUST demand a non-empty `document` field on a finding only when
`len(documents) > 1`. Under one declared document, a finding without a
`document` field MUST remain well-formed — this is not a migration; every
populated `tests/findings.py` already on disk, including the seal corpus's
own, must continue to validate unchanged.

#### Scenario: A single-document finding without `document` still validates
- GIVEN a one-document profile and a finding lacking `document`
- WHEN `well_formed` checks it
- THEN it is accepted, and the sealed digest touching it is unchanged

#### Scenario: A two-document finding without `document` is refused
- GIVEN a two-document profile and a finding lacking `document`
- WHEN `well_formed` checks it
- THEN it is rejected, naming the missing `document` field

### Requirement: A Finding May Name Either Or Both Documents; Impact Class Is Per-Document Representation, Not Verdict

`finding_impact`'s `class` MUST become a per-document mapping under two
documents, and a finding MUST be nameable against either document or both.
This capability MUST emit that mapping as representation only — it MUST NOT
compute, print, or return a single word describing what a finding against
both documents *means*; that judgment is out of scope.

#### Scenario: A finding against one document maps to that document alone
- GIVEN a two-document profile and a finding naming only the first document
- WHEN `finding_impact` computes its class
- THEN the returned mapping carries a class for that document only

#### Scenario: A finding against both documents carries both classes, uninterpreted
- GIVEN a two-document profile and a finding naming both documents
- WHEN `finding_impact` computes its class
- THEN the returned mapping carries one class per named document, with no
  combined or summarized verdict

### Requirement: `cmd_verify`'s Fidelity Fold Runs Per Document

The four-condition fidelity fold (`stale or missing_provenance or untested or
unreached`) MUST run once per declared document under `len(documents) > 1`,
producing one fidelity result per document, and MUST run exactly as before
under one document.

#### Scenario: A single-document fidelity result is unchanged
- GIVEN a one-document profile
- WHEN `cmd_verify` computes fidelity
- THEN the result and its sealed digest are unchanged from before this
  capability

#### Scenario: A two-document run produces two independent fidelity results
- GIVEN a two-document profile where one document is stale and the other is
  not
- WHEN `cmd_verify` computes fidelity
- THEN each document's result reflects only its own four conditions

### Requirement: A Two-Document Fixture Profile And Pair Corpus Prove Every Pair Branch Before It Ships

A fixture profile declaring two documents, and a corpus exercising it, MUST
exist and MUST reach every branch introduced by `len(documents) > 1` across
the requirements above, each branch named with the case that reaches it. A
branch with no reachable configuration in this repository MUST NOT ship as
provable without this fixture and corpus, which are that reachable
configuration.

#### Scenario: Every pair branch is named and reached
- GIVEN the pair corpus and the list of branches introduced by this
  capability
- WHEN coverage is checked
- THEN every named branch has at least one corpus case reaching it

#### Scenario: A branch removed from the corpus is caught
- GIVEN a corpus case that is the sole reacher of one pair branch
- WHEN that case is removed and coverage is re-checked
- THEN the check fails, naming the now-unreached branch

### Requirement: RED-First Test Commits Are Individually Verifiable

Each work unit in this capability MUST land as two commits: a `test(...)`
commit carrying only the failing test(s), followed by its implementation
commit. The test commit MUST be independently checkoutable with its test
observably red at that exact commit.

#### Scenario: A test commit is red in isolation
- GIVEN a work unit's `test(...)` commit, checked out alone
- WHEN its test is run
- THEN it fails, and the following implementation commit turns it green

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

## Boundary (explicitly not built here)

The cross-document agreement verdict — what it means for the two documents to
disagree, and what `handoff` prints for a finding against both — is not a
requirement of this capability. Under one declared document there is no pair
to disagree, so a verdict computed here could be exercised only by a fixture
written to satisfy it — a guard validating its own test data. It belongs to
the consuming skill.
