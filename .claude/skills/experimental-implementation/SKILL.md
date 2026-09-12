---
name: experimental-implementation
description: "Trigger: turn the latest experiments protocol into working Python against a target repository, run its declared measurements, and verify an existing implementation's layout and revision fidelity against that same protocol. Isolated venv, keyless, fail-closed. The second host on the shared implementation engine (change `the-second-skill-the-seam-was-for`) -- change A, single document, zero engine bytes."
---

# Experimental Implementation

Turn the current experiments revision (`experiments/experiments-<slug>-vNN.md`)
into Python that runs, in a target repository, and prove it: complete runs whose
own record agrees with what the protocol says.

## Scope: change A only, and what that means in practice

This skill is the SECOND host built on the shared implementation engine
(`_core/implementation/engine/implementation_engine.py`) -- the same engine
`proposal-implementation` already serves, changed by **zero bytes** to add this
domain. Everything here is a profile
(`.claude/skills/experimental-implementation/impl_profile.py`), a byte-identical
launcher copy, this doctrine, two agents, and this skill's own sealed corpus.

**One declared document.** `documents[0]` is `experiments/`, label `experiments`
-- the experiments document this skill verifies. There is no second document
yet: cross-document agreement against the mathematical proposal, a claim
vocabulary per document, and a successor composer are follow-on changes (B, C,
D), not built here. Consequence, recorded honestly rather than discovered
later: after this change, this skill does what `proposal-implementation`
already does, against a different document. New capability -- cross-document
agreement, a submission through Flow B -- arrives at change C/D, not here.

## This domain's own claim vocabulary

Where `proposal-implementation` reads `equations`/`ecuación`/`formulation`, this
skill reads its own words, declared in its own profile:

| Profile leaf | This domain's value |
| --- | --- |
| `provenance.claim_key` / `findings.locus_key` | `experiments` |
| `findings.remedy_locus_key` | `remedy_experiments` |
| `vocabulary.subject_singular` / `_plural` | `experiment` / `experiments` |
| `vocabulary.subject_singular_es` / `_plural_es` | `experimento` / `experimentos` |
| `vocabulary.subject_collective` / `_collective_es` | `experimentation` / `experimentación` |
| `vocabulary.artifact_noun` | `protocol` |
| `documents[0].directory` / `.label` | `experiments/` / `experiments` |

A module's own `__provenance__` here declares an `"experiments"` key (never
`"equations"`), and every invariant listed there needs a matching test under
`tests/`, exactly as the sibling's own doctrine requires for its own claim key.

## The objective flow

**Why this skill was invoked, and where it has to arrive.** Declared here and in
`OBJECTIVE_FLOW`, held equal by a test, and deliberately independent of anything
on disk -- the same property `proposal-implementation`'s own north has, and for
the same reason: a session that hits an error, an interruption or a gap
consults it, locates itself, resolves what blocks, and rejoins.

**Purpose:** carry the declared experiments protocol as far as complete runs
whose own record agrees with what the protocol says -- not a green
verification, not a passing rehearsal.

| Stage | Establishes | Behind you when |
| --- | --- | --- |
| `standing` | A repository set up the way this skill expects, with an interpreter of its own and the protocol's declared steps laid out as runnable commands | `structure` reports no scaffold gaps and the protocol the run answers to is named and readable |
| `binding` | The code that runs says what the bound experiments revision says, every declared step traced to a runnable command | `fidelity` is clean against the bound experiments revision and the target's own suite is green under its own interpreter |
| `instrumentation` | Every measurement the protocol declares has a place to land -- a metric, a record, a check that can fail | every declared measurement resolves to something that can actually be run and read back |
| `rehearsal` | The declared flow runs end to end at a small scale, and the record it leaves agrees with the document a person reads | the rehearsal is complete and its own report is `ok` |
| `full-scale` | Every step routed to where it was decided to run, and executed there at the scale the protocol declares | this is the arrival; it is behind nobody |

**Arrival:** complete runs at the protocol's declared scale, with a record
checkable against the experiments revision.

**Four stops are a person's, not defects to repair:** authorizing that code be
written at all; approving the map from the protocol's declared steps to
runnable commands; publishing the commit a worker would clone; authorizing a
launch, which is hours of somebody's quota.

This north declares no stage nothing measures, and no `entrances` at all --
declaring an entrance nothing produces would be a claim with no producer, the
same reasoning `experimental-deliberation`'s own profile records for itself.

## What this skill delegates, and to whom

Two stretches of this flow are mechanical from end to end, each carried out by
its own agent. What moves is EXECUTION, never doctrine: every rule stays here,
and each agent's first instruction is to load this file.

| Stretch | Delegated to | Begins after | Ends at | Measure this before delegating |
| --- | --- | --- | --- | --- |
| Build | this skill delegates to the `experiments-build` agent | the object-to-map is approved | every declared measurement has a place to land (`instrumentation`) | `verify` -- the protocol's declared steps must already be traced to runnable commands |
| Walk | this skill delegates to the `experiments-walk` agent | each step's placement is decided | the launch the operator must authorize | `verify` -- `undeclaredPlacement` is empty, so every step says where it runs |

Each agent also refuses from inside when it finds itself before its own start --
the backstop, not the rule.

## Entry command

```bash
.claude/skills/experimental-implementation/scripts/implementation_cli.py <command> [args...]
```

A concrete, runnable example -- this exact line runs verbatim, unedited, from
the forge's own root (`tests/test_experimental_implementation.py`'s own
published-commands test proves it):

```bash
.claude/skills/experimental-implementation/scripts/implementation_cli.py name --name Trial
```

The launcher is a byte-for-byte copy of `proposal-implementation`'s own launcher
(design.md D4): every value inside it is derived from its own location, so the
same 24 bytes, placed under this skill's own `scripts/`, resolve to THIS
skill's own profile without a single domain-specific line. Every argument,
subcommand and exit code is the shared engine's; nothing here re-documents them.

## Which commands are not available yet, and why

This domain ships no `assets/kit/` at all (measured this session: the kit
sibling ships is ~99% general machinery, and copying ~2,000 lines to change the
~20 that are not would be the exact duplication the operator refused for the
CLI, one directory over). Consequence, stated rather than discovered:

- **`compose` and `admit`** read `\tag{}` (LaTeX display-equation tags) and the
  block locator built for that shape. This domain's own documents carry no such
  tags, and building a locator for a shape this domain does not have is out of
  scope for this change (deferred; see design's own D11).
- **`materialize --stage scaffold`** and any other stage that copies kit
  destinations reads `assets/kit/`, which this skill does not ship. A target
  scaffolded under this domain needs its object-to-module map approved and
  written by hand, or from a kit a later change adds.

Every other published command runs exactly as `proposal-implementation`'s own
doctrine describes it, against this domain's own profile leaves instead of the
sibling's.

## What this skill has not written down

Same as the sibling's own recorded gap: `.implementation/` is a required
`.gitignore` entry, so neither a launch authorization nor a deliberation
record reaches a clone. Nothing here separates the two; recorded rather than
resolved, for the same reason the sibling records it rather than fixing it
here.

## Non-negotiable isolation

Every run works inside `implementations/<repo>/` and uses that repository's own
`.venv`. Never the forge's virtualenv, never system Python for target code.
`implementations/` is gitignored; the CLI refuses any target outside it, and
refuses to create a venv from a forge interpreter -- exactly as the sibling's
own doctrine states, because this is the shared engine's own behaviour, not a
domain-specific one.
