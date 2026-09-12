# implementation-cross-document-agreement Specification

## Purpose

Detects when the experiments document and the mathematical proposal
contradict each other — one document tests a claim the other no longer
declares — and refuses, naming the discrepancy. The engine computes no
verdict over which document is right and proposes no resolution; the
operator decides, in conversation, after the agent reads both documents.
This is the discharge of `implementation-document-binding`'s own Boundary
section, which named this exact judgment "the consuming skill['s]" to build.

**Budget note**, on the precedent every capability in this change sets:
this spec exceeds 650 words because "the engine refuses and names; it
never proposes" is exactly the kind of boundary this project has measured
collapsing under a shorter artifact, and each of its three failure
directions (silent pass, engine-authored verdict, batching N refusals into
one that hides which N) needs its own scenario to be provable by mutation.

## Requirements

### Requirement: A New Cross-Document Citation Form Resolves An Experiment Against A Proposal Claim

An experiments document MAY cite a claim the proposal declares, using a
form distinct from the existing within-document `[tests:X]`/`[exp:X]`
pair — the proposal's own already-declared numbered claims (`\tag{N}`)
are the resolution target; nothing about how the proposal declares a claim
changes. This form MUST be validated by the per-`documents[N]`
`cross_citation` leaf `implementation-per-document-vocabulary` defines — a
mapping of `pattern` and `resolves_against`, required per entry and absent
only by an explicit `None` — whose own absence is refused by its exact
indexed name, on `documents[N].dataset_marker`'s tier rather than the
silence-tolerating five-leaf claim-vocabulary tier.

#### Scenario: A citation resolving against a declared claim is accepted
- GIVEN an experiments document citing a claim the proposal's current
  revision declares
- WHEN the crossing resolves
- THEN it is accepted, and the existing `[tests:X]`/`[exp:X]` resolution
  inside either document is unaffected

#### Scenario: The new leaf's absence refuses by its own indexed name
- GIVEN a two-document profile omitting the new leaf
- WHEN the resolver validates it
- THEN it refuses, naming the leaf's own indexed path, never a bare
  top-level name

### Requirement: Refusal Kind 1 — A Cited Claim The Proposal No Longer Declares

When an experiments document cites a claim the proposal's current bound
revision does not declare, the system MUST refuse by a named code
identifying both the citing experiment and the missing claim.

#### Scenario: A citation to a removed claim refuses
- GIVEN an experiment citing claim N, and the proposal's current revision
  declares no matching claim N
- WHEN the crossing check runs
- THEN it refuses, naming the experiment and claim N

#### Scenario: A citation matching a declared claim does not refuse
- GIVEN the identical citation, with claim N still declared
- WHEN the crossing check runs
- THEN it does not refuse for that citation

### Requirement: Refusal Kind 2 — A Declared Claim No Experiment Tests

When the proposal declares a claim no experiment in the experiments
document cites, the system MUST refuse by a named code identifying the
untested claim.

#### Scenario: An untested declared claim refuses
- GIVEN the proposal declares claim M and no experiment cites it
- WHEN the crossing check runs
- THEN it refuses, naming claim M

#### Scenario: A claim cited by at least one experiment does not refuse
- GIVEN claim M is cited by one experiment among several
- WHEN the crossing check runs
- THEN it does not refuse for claim M

### Requirement: A Document Declaring No Crossing At All Refuses Once, Not Once Per Claim

When an experiments document declares zero citations of the new form
while the proposal declares one or more claims (or the reverse: the
proposal declares zero claims while the experiments document cites the
new form at least once), the system MUST refuse by a single named code
distinct from Kind 2's per-claim code — never one Kind-2 discrepancy per
declared claim.

#### Scenario: Zero crossings against a 39-claim proposal refuses once
- GIVEN an experiments document with no citations of the new form and a
  proposal declaring 39 claims
- WHEN the crossing check runs
- THEN it refuses exactly once, by the no-crossing-declared code — not 39
  times

#### Scenario: At least one crossing switches to the per-claim refusal path
- GIVEN the identical proposal, with one experiment now citing one of its
  39 claims
- WHEN the crossing check runs
- THEN the no-crossing-declared code does not fire, and any remaining
  untested claims refuse under Kind 2, individually named

### Requirement: Each Discrepancy Is Acknowledged By Its Exact ID; A General Continue Clears Nothing

Mirroring `acknowledgedRemovals`'s shape — a refusal carrying an
`unacknowledged` list, cleared only by ids echoed back — an unresolved
crossing discrepancy MUST be acknowledgeable individually, by its exact
id. An acknowledgment call naming fewer ids than are outstanding MUST
leave every un-named id blocking; a call naming none MUST clear nothing.

#### Scenario: Two discrepancies, one acknowledged, one still blocks
- GIVEN two named discrepancies
- WHEN one is acknowledged by its exact id
- THEN the refusal persists, naming only the still-unacknowledged one

#### Scenario: Both acknowledged, both clear
- GIVEN the same two discrepancies
- WHEN both are acknowledged by their exact ids
- THEN neither blocks the next command

#### Scenario: A general "continue" with no ids clears nothing
- GIVEN the same two discrepancies
- WHEN a call is made that acknowledges neither by id
- THEN both remain in the refusal's `unacknowledged` list

### Requirement: The Engine Emits No Verdict, No Resolution Proposal, And No Repair Direction

The refusal's output MUST name the discrepancy (the claim, the citing or
missing experiment, the kind) and MUST NOT contain a word or field stating
which document is correct, a suggested edit to either document, or a
computed "the code should follow the proposal" / "the proposal should
follow the code" direction. This judgment stays with the agent reading
both documents in conversation and, ultimately, the operator.

#### Scenario: A refusal names the discrepancy without judging it
- GIVEN an unresolved crossing
- WHEN the refusal is emitted
- THEN its output contains no verdict field or word, and a test asserting
  the field's absence passes

#### Scenario: A mutation adding a verdict field is caught
- GIVEN a mutation that adds a computed "which document is right" field to
  the refusal output
- WHEN the absence-of-verdict test runs
- THEN it fails, naming the field that should not exist

## Boundary (explicitly not built here)

Which direction a discrepancy is repaired — treating the code as ahead of
the proposal, or the proposal as ahead of the code — is never inferred
here, the same way `proposal-implementation`'s Flow B step 5 already asks
rather than decides. An agent proposing a resolution happens in
conversation, outside this capability; nothing here authors that
resolution or writes it into either document.
