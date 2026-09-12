# Delta for experimental-implementation-skill

## MODIFIED Requirements

### Requirement: Two Documents Reproduce Document 0's Byte-Identical Guarantee, Each With Its Own Claim Vocabulary

This skill's profile MUST declare exactly two `documents` entries once this
capability lands: document 0 (the experiments document, unchanged from
Slice A) and document 1 (the mathematical proposal). Document 0 MUST remain
byte-identical in behavior to its pre-capability form — it declares no
per-document vocabulary override, so it keeps resolving from the top-level
`provenance.*`/`findings.*` scalars, the same resolver tier, the same
refusal set, the same digest-moving rules per changed leaf. Document 1 MUST
declare its own per-document claim vocabulary naming the mathematical
proposal's claims as its own kind, never inheriting document 0's
experiments vocabulary by omission passing silently as agreement.
(Previously: this skill declared exactly one `documents` entry for Slice A;
under `len(documents) == 1` its single entry was required to behave like
`proposal-implementation`'s own index-0.)

#### Scenario: Document 0 behaves like index 0, unchanged
- GIVEN this skill's `documents[0]` entry, unchanged from Slice A
- WHEN a leaf under it is omitted
- THEN the refusal names `documents[0]`, not a bare `documents`, and the
  refusal set is unchanged from Slice A

#### Scenario: Document 1 declares and uses its own vocabulary
- GIVEN this skill's `documents[1]` entry declares its own `claim_key`
  naming the mathematical proposal's own claim kind
- WHEN the resolver resolves it and the fold reads it
- THEN document 1's fidelity fold and citation matching use its own
  declared values, never document 0's experiments vocabulary

#### Scenario: This skill's own directory is scanned for leakage the day it appears
- GIVEN `tests/forge_vocabulary.py::shipped_documents()` walks every file
  under `.claude/skills/`
- WHEN this skill's directory (now with two documents) is present
- THEN both documents' declared text is scanned in the same run, with no
  opt-out

## ADDED Requirements

### Requirement: A Two-Document Guarantee Is Proven By Reading, Not By Counting

The mechanism that previously guaranteed a single declared document (a
shipped-surface test asserting every discovered profile declares exactly
one `documents` entry) MUST be deleted and replaced by a check proving
each of this skill's declared documents' own claim vocabulary is actually
read and threaded into that document's own fidelity result and citation
matching. A count-only check (asserting `len(documents) == 2` alone) MUST
NOT stand in as evidence that the per-document read happened.

#### Scenario: The replacement lock demonstrates the read, not the count
- GIVEN this skill's two declared documents, each with its own claim
  vocabulary
- WHEN the replacement lock runs
- THEN it demonstrates, via the drift-control fixture, that document 1's
  fidelity status changes when document 1's own text changes while
  document 0 stays clean

#### Scenario: A reverted fold is caught even though the document count is still two
- GIVEN a mutation that reverts the fold's per-document derivation while
  both documents remain declared
- WHEN the replacement lock runs
- THEN it fails, because a documents-count check alone cannot detect the
  reversion
