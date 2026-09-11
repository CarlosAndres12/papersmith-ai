"""This skill's own Cut-1 domain profile for the shared implementation
engine (`_core/implementation/engine/implementation_engine.py`).

Mirrors `domain-profile.ts`'s `artifact.directory`-style resolution: every
value here is computed from THIS file's own location, which moves as one
unit with the skill -- never from the engine's location, which the launcher
(`scripts/implementation_cli.py`) sets `IMPLEMENTATION_DOMAIN_PROFILE` to
point at.

Cut-1 field set (design.md D3, amended 2026-09-11 -- operator ruling on task
7.5's non-interference finding), each earning its place by being read:

- `kit.root` -> the engine's `SKILL_ROOT` (19 reader lines). Non-optional:
  `SKILL_ROOT` breaks the instant the engine moves, and breaks silently.
- `cli.path` -> the engine's `CLI_PATH` -> `CLI_INVOCATION` -> 4 message
  builders. Cut 1's single silent failure mode, and the mutation surface for
  R2/D4: one line in this file, instead of an edit inside 17,100.
- `objective` -> the engine's `OBJECTIVE_FLOW`, moved here VERBATIM (the
  text does not change; this is a relocation, not a rewrite). Read TWICE
  from outside the engine: stamped into every refusal this skill's engine
  invocation raises (`impl_domain_profile.py`'s own module docstring), and
  discovered by `tests/test_agents.py`'s cross-skill north lock, which walks
  THIS SKILL'S OWN directory tree (never the engine's) for a literal
  module-level `OBJECTIVE_FLOW` assignment -- which is exactly why it must
  physically live here and not in the shared engine: a second skill built on
  this same engine needs its OWN north, different stages, different
  arrival, and cannot get one by editing the engine, which is precisely what
  this seam exists to prevent (see the archived
  `2026-09-09-a-north-a-second-domain-can-hold` precedent on the
  deliberation side, where `proposal-deliberation/profile.ts` and
  `experimental-deliberation/profile.ts` each declare their own `objective`
  and `_core/deliberation/engine/domain-profile.ts` hardcodes neither).

Nothing else. `documents`, `provenance`, `document_reader`, `findings`,
`vocabulary`, `cli_invocation` are out of scope for Cut 1 -- each would be a
profile field nothing here reads, and an unprovable field is the shape of a
false guard.
"""
from __future__ import annotations

from pathlib import Path

_SKILL = Path(__file__).resolve().parent

#: WHY THIS SKILL WAS INVOKED, AND WHERE IT HAS TO ARRIVE.
#:
#: Declared, invariant, and deliberately independent of anything on disk.
#: Every other reading the engine does answers *where am I* by measuring
#: products -- `walk` the ledger, `flowActs` what is owed, `flowDestination`
#: the rung. This answers a question none of them can: *what is this for*.
#: A session that hits an error, an interruption, or a gap consults it,
#: locates itself, resolves what blocks, and rejoins -- rather than
#: improvising forward, which is what an agent does when a blocker detaches
#: it from the purpose.
#:
#: **It is not the agreements and does not replace them.** What the
#: mathematics says lives in the managed revision; what was settled about
#: this repository lives in its `AGREED.md`. This says only what the skill
#: is FOR, which is the one thing neither of those states and no artefact
#: implies.
#:
#: Each stage names what it establishes and how a reader knows it is behind
#: them. The conditions are written to be READ, not computed: a stage
#: derived from products would make the purpose depend on the products,
#: which is exactly the dependency this exists without.
#:
#: Discovered by `tests/test_agents.py::_python_objective` as a module-level
#: literal named exactly `OBJECTIVE_FLOW` -- never wrap this in a function
#: call or a derived expression, or that AST-literal walk stops finding it.
OBJECTIVE_FLOW = {
    "purpose": (
        "carry the agreed formulation as far as complete runs that can be "
        "reported -- not a green verification, not a passing rehearsal"),
    "stages": [
        {"stage": "standing",
         "establishes": "a repository to write the mathematics into: isolated "
                        "under `implementations/` with an interpreter of its "
                        "own, laid out the way this skill expects, the kit's "
                        "destinations materialized, and the map from "
                        "mathematical object to module approved",
         "behindWhen": "`structure` reports no scaffold gaps and the benchmark "
                       "declaration carries the revision and premises the map "
                       "was approved with -- which is what `materialize "
                       "--stage objects` refuses without"},
        {"stage": "fidelity",
         "establishes": "the code says what the bound revision says, and every "
                        "claim it makes carries an invariant with a test",
         "behindWhen": "`fidelity` is clean and the target's own suite is green "
                       "under its own interpreter"},
        {"stage": "audit",
         "establishes": "what the formulation gets wrong, established over the "
                        "declared sweep, with each remedy ruled admissible "
                        "before it is measured and validated after",
         "behindWhen": "`audit` is no longer `incomplete`"},
        {"stage": "declaration",
         "establishes": "what the experiment compares, over which statistical "
                        "unit, by which metric, and what it produces",
         "behindWhen": "the benchmark declaration is answered rather than "
                       "sitting at its scaffolded empty value"},
        {"stage": "rehearsal",
         "establishes": "the declared flow runs end to end with its own "
                        "notebooks, and the document a person reads agrees "
                        "with the run",
         "behindWhen": "the pilot is complete and `report` is `ok`"},
        {"stage": "full-scale",
         "establishes": "every step routed to where it was decided to run, and "
                        "executed there at the scale the protocol declares",
         "behindWhen": "this is the arrival; it is behind nobody"},
    ],
    "arrival": (
        "complete runs at the declared scale, local or remote as each step "
        "declares, with the record they leave"),
    # Said here because a blocked agent needs it most: some stops are not
    # defects and must not be repaired. Publishing a commit and authorizing a
    # launch are decisions a person owes, and an agent that treats them as
    # blockers to resolve will either stall on them or take them.
    "humanStops": [
        "authorizing that code be written at all, which nothing below the gate "
        "may start without",
        "approving the map from mathematical object to module, and the "
        "revision and premises recorded beside it",
        "publishing the commit a worker would clone",
        "authorizing a launch, which is hours of somebody's quota",
    ],
}

PROFILE = {
    "kit": {"root": _SKILL},
    "cli": {"path": _SKILL / "scripts" / "implementation_cli.py"},
    "objective": OBJECTIVE_FLOW,
}
