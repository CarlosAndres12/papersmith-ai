# implementation-engine-neutrality Specification

## Purpose

The implementation CLI engine serves no domain of its own. Cut 1 moves the
17,100-line CLI verbatim to `_core/implementation/engine/implementation_engine.py`,
mirroring `_core/deliberation/engine/domain-profile.ts`: it resolves its host
from `IMPLEMENTATION_DOMAIN_PROFILE`, refuses to start without one, and
sources `kit.root` and its published CLI path from the host rather than its
own file location. Governs Cut 1 only — not the 167 domain-specific lines
(Cut 2) or the scalar→pair revision shape (Cut 3).

Four product decisions are deferred to design (whether `kit.root` is a
profile field or launcher-passed; minimal vs. full Cut-1 field set; whether a
Python profile-lock belongs here; whether the `sys.path` site becomes a
profile field). Every requirement below holds under any answer: the host,
never the engine's own file location, supplies the root; an unused field is
not required and is not mutation-provable, so it must not be treated as
satisfying a requirement.

## Requirements

### Requirement: Engine Refuses To Start Without A Domain Profile

The engine MUST fail closed, with a named refusal, when
`IMPLEMENTATION_DOMAIN_PROFILE` is unset, non-absolute, or resolves to a
module missing a required field. It MUST NOT default to any domain.

#### Scenario: Unset variable refuses
- GIVEN `IMPLEMENTATION_DOMAIN_PROFILE` is unset
- WHEN the engine is imported
- THEN it raises a named refusal before any command runs

#### Scenario: Malformed profile refuses
- GIVEN the variable is relative, or the module omits a required field
- WHEN the engine loads it
- THEN it raises a refusal named for that exact case

### Requirement: The Skill Root Resolves From The Host, Never The Engine's Own Location

`SKILL_ROOT` (17 reader sites) MUST resolve from a host-supplied value —
whichever mechanism Cut 1's design settles — and MUST NOT be derived from
`Path(__file__)` inside the moved engine, whose own file now lives under
`_core/implementation`, not under any skill.

#### Scenario: SKILL_ROOT names the skill directory after the move
- GIVEN the engine executes from `_core/implementation/engine/implementation_engine.py`
- WHEN any of the 17 `SKILL_ROOT` readers run
- THEN the resolved value is the skill's own directory

#### Scenario: A wrong root is made observable, not silent
- GIVEN `SKILL_ROOT` is, by mutation, derived from the engine's own `__file__`
- WHEN a reader resolves it
- THEN it resolves to `_core/implementation`, and a test pinning the skill
  directory value goes red

### Requirement: The Core Import Path Resolves From The Engine's Own File

The `sys.path.insert` site locating `_core/implementation` MUST be computed
relative to the moved engine module's own `__file__`, never relative to any
launcher's `__file__`, so the shared core is found identically regardless of
which skill launches it.

#### Scenario: Import succeeds through any launcher
- GIVEN the launcher hands over to the engine
- WHEN the engine computes its own sibling-module path
- THEN the import succeeds without depending on the launcher's directory depth

#### Scenario: A stale relative depth fails loudly
- GIVEN the site were left computed against a launcher's `__file__`
- WHEN the module imports
- THEN it raises `ImportError` immediately — the loud failure mode, distinct
  from `SKILL_ROOT`'s silent one

### Requirement: The Published CLI Path Names The Launcher

`CLI_PATH`, and every value derived from it (`CLI_INVOCATION`, printed or
published commands, `AGREED.md` entries), MUST resolve to the per-skill
launcher's own file, never the engine module's file, regardless of where the
underlying code executes.

#### Scenario: CLI_PATH names the launcher
- GIVEN the launcher hands over to the engine
- WHEN `CLI_PATH` is resolved
- THEN it equals the launcher's own file path, not the engine's

#### Scenario: A wrong CLI_PATH moves the seal
- GIVEN `CLI_PATH` is, by mutation, made to resolve to the engine's file
- WHEN the seal's normalized output is compared to its golden
- THEN every case whose output embeds `CLI_INVOCATION` moves, and comparison
  goes red

### Requirement: Published Commands Are Proven Against The Launcher, Not Assumed

`PublishedCommandsRunVerbatimTests` MUST assert, against the launcher's
literal path, that every printed or published command names a file the
reader was actually given — re-pointed explicitly for this cut, never
inherited unchanged from the pre-move assertion.

#### Scenario: The test asserts the launcher's literal path
- GIVEN the re-pointed test
- WHEN it runs against the moved engine and its launcher
- THEN every published command string contains the launcher's literal path

#### Scenario: The guard is reachable
- GIVEN `CLI_PATH` is mutated to resolve to the engine instead of the launcher
- WHEN the test runs
- THEN it fails, proving the assertion is not vacuous

### Requirement: Zero Behavioural Delta, Proven Against The Existing Seal

Every case captured by `the-seal-before-the-cut` MUST reproduce its stored
digest and exit status byte-identically after the move, run through the
launcher. The committed goldens are not reshaped or reissued by this cut;
they remain the exact contract Cut 1 must satisfy. There is no sanctioned
delta: any digest movement is a defect, and the remedy is reverting the
move, never declaring a new golden.

#### Scenario: Every case reproduces its golden
- GIVEN the 20-subcommand seal corpus and its committed goldens
- WHEN every case is re-run through the launcher after the move
- THEN each normalized digest and exit status is byte-identical to its
  pre-move golden

#### Scenario: A moved digest blocks the change
- GIVEN any case whose digest differs from its golden after the move
- WHEN the seal comparison runs
- THEN the change does not proceed, and the difference is reverted — never
  accepted as a new golden

## Reconciliation note (orchestrator, after design landed)

This spec originally named the engine's destination as the FLAT
`_core/implementation/implementation_engine.py`. That destination is
unreachable, and the correction is recorded here rather than silently applied.

`tests/test_implementation_core.py`'s `CoreNamesNoDomainTests` scans
`CORE.glob("*.py")` — **non-recursive** — and fails any core file whose text
names a member of `PRODUCT_DIRS`/`SOURCE_ROOTS`. The engine **defines**
`PRODUCT_DIRS = ("Notebooks", "Data", "Results", "Models")`, so a flat landing
turns that guard red. Both obvious repairs are worse than the defect: exempting
the engine by name, or weakening the rule, guts a guard covering ~17,100 of
~18,000 core lines.

The destination is therefore the `engine/` **subdirectory**, which the
non-recursive glob does not reach. This is not a new mechanism invented for the
occasion — `.claude/skills/_core/deliberation/engine/` is already exactly this
shape, verified on disk. The precedent this change set out to mirror had already
answered the question.
