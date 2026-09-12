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

### Requirement: A Single Document Reproduces The Existing Byte-Identical Guarantee

This skill's profile MUST declare exactly one `documents` entry for Slice A. Under
`len(documents) == 1`, this skill's engine invocations MUST be indistinguishable in
kind from `proposal-implementation`'s own index-0 behavior — the same resolver tier,
the same refusal set, the same digest-moving rules per changed leaf.

#### Scenario: One document behaves like any other skill's index 0
- GIVEN this skill's single `documents[0]` entry
- WHEN a leaf under it is omitted
- THEN the refusal names `documents[0]`, not a bare `documents`, matching the indexed
  behavior already proven for a two-entry profile elsewhere in the engine

#### Scenario: This skill's own directory is scanned for leakage the day it appears
- GIVEN `tests/forge_vocabulary.py::shipped_documents()` walks every file under
  `.claude/skills/`
- WHEN this skill's directory is added
- THEN it is scanned in the same run, with no opt-out
