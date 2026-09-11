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

## Boundary (explicitly not built here)

The cross-document agreement verdict — what it means for the two documents to
disagree, and what `handoff` prints for a finding against both — is not a
requirement of this capability. Under one declared document there is no pair
to disagree, so a verdict computed here could be exercised only by a fixture
written to satisfy it — a guard validating its own test data. It belongs to
the consuming skill.
