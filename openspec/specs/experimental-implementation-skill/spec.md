# experimental-implementation-skill Specification

## Purpose

The second skill built on the shared `_core/implementation/engine/implementation_engine.py`.
It ships its own domain profile, its own north, and its own two agents — mirroring
`proposal-implementation`'s Cut-1/Cut-2 shape exactly, the way `experimental-deliberation`
mirrors `proposal-deliberation` on the TS side. This capability governs Slice A only:
a **single** declared document. Per-document claim vocabulary, cross-document agreement,
the experiments-successor composer, and `Data/` per product folder are follow-on work
(changes B, C, D) and are explicitly not governed here — no `documents[1]` entry ships
under this capability.

## Requirements

### Requirement: The Skill Declares Its Own Domain Profile

`experimental-implementation/impl_profile.py` MUST exist and validate against the same
resolver tier `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` enforces for any profile, declaring
its own `kit`, `cli`, `objective`, `provenance`, `findings`, `vocabulary`, and exactly one
`documents` entry. It MUST NOT ship a `profile.ts`.

#### Scenario: The profile resolves and validates
- GIVEN `IMPLEMENTATION_DOMAIN_PROFILE` points at this skill's `impl_profile.py`
- WHEN the shared engine imports it
- THEN every required leaf validates and no refusal is raised

#### Scenario: A missing leaf refuses by its own name
- GIVEN a required leaf omitted from this skill's profile
- WHEN the engine loads it
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming that exact leaf

### Requirement: One Skill, One North — No Dual Declaration

A skill declaring `OBJECTIVE_FLOW` in Python and an `objective` in `profile.ts` MUST be
rejected by `declared_objective`, never silently resolved to one source.

#### Scenario: This skill has no profile.ts to collide with
- GIVEN `experimental-implementation` ships only `impl_profile.py`
- WHEN `declared_objective("experimental-implementation")` runs
- THEN it returns the Python `OBJECTIVE_FLOW`, raising nothing

#### Scenario: A planted profile.ts is caught
- GIVEN a `profile.ts` is added beside this skill's `impl_profile.py`, both declaring an objective
- WHEN `declared_objective` runs
- THEN it raises, naming the skill, before either source is picked

### Requirement: The North Belongs To This Skill Alone

`OBJECTIVE_FLOW` MUST be a module-level literal physically inside this skill's own
directory tree, with stages and an arrival distinct from `proposal-implementation`'s —
never the sibling's stages, never its arrival, and never read from the shared engine.

#### Scenario: Discovery finds this skill's own flow
- GIVEN `tests/test_agents.py`'s cross-skill north lock walks this skill's tree
- WHEN it discovers `OBJECTIVE_FLOW`
- THEN the returned stages and arrival differ from `proposal-implementation`'s

#### Scenario: A missing north is refused, not inherited
- GIVEN `OBJECTIVE_FLOW` is removed from this skill's tree
- WHEN the north lock runs
- THEN `declared_objective("experimental-implementation")` returns `None`, and the
  agent-binding tests for this skill fail — the flow is never silently borrowed from
  the sibling or the engine

### Requirement: The Two Agents Carry No Logic And Bind To This Skill's Own Stage

The build- and walk-equivalent agents MUST each be a thin, ~70-line file with no
executable logic beyond loading this skill's `SKILL.md`. The build-equivalent's
`stretch:` frontmatter value MUST name a stage present in this skill's own
`OBJECTIVE_FLOW`, never a stage from any other skill's north.

#### Scenario: A stretch naming a foreign stage is refused
- GIVEN the build-equivalent agent's `stretch:` names a stage that exists only in
  `proposal-implementation`'s `OBJECTIVE_FLOW`
- WHEN `tests/test_agents.py` validates agent bindings
- THEN it fails, naming the unresolvable stretch

#### Scenario: A correctly bound stretch passes
- GIVEN the `stretch:` value names a stage this skill's own `OBJECTIVE_FLOW` declares
- WHEN agent-binding tests run
- THEN they pass

### Requirement: Two Documents Reproduce Document 0's Byte-Identical Guarantee, Each With Its Own Claim Vocabulary

This skill's profile MUST declare exactly two `documents` entries: document 0
(the experiments document, unchanged from Slice A) and document 1 (the
mathematical proposal). Document 0 MUST remain byte-identical in behavior to
its pre-capability form — it declares no per-document vocabulary override, so
it keeps resolving from the top-level `provenance.*`/`findings.*` scalars, the
same resolver tier, the same refusal set, the same digest-moving rules per
changed leaf. Document 1 MUST declare its own per-document claim vocabulary
naming the mathematical proposal's claims as its own kind, never inheriting
document 0's experiments vocabulary by omission passing silently as agreement.
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
