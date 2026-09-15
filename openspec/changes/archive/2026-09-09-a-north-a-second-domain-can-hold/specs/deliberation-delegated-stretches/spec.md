# Deliberation Delegated Stretches Specification

## Purpose

What an agent definition owes, copied into its own bytes rather than
referenced; and which stretch of a deliberation domain may be delegated to an
agent at all, decided by whether its closing condition can be measured from
the candidate's bytes.

## Requirements

### Requirement: A stretch is delegable only if its closing condition is decidable from bytes

An agent MUST NOT be delegated a stage with no measurable closing condition.
`validated` MAY be delegated: `preservation-experimental.ts::violations`
already decides it from the document's bytes (`url-without-verification-marker`,
`baseline-missing-repository-url`, `baseline-missing-venue-year`, all blocking
outright). `deliberated` MUST NOT be delegated to any agent: nothing measures
it, and an agent able to close it would be approving its own proposal.

#### Scenario: The validation stretch is delegated

- GIVEN a candidate experimental document with an unmarked external URL, or a
  baseline missing a repository URL or venue year
- WHEN the validation-owning agent runs the check
- THEN `violations` reports the specific rule broken, and publish is refused
  until it is resolved

#### Scenario: The deliberated stage is never delegated

- GIVEN an agent operating within
  `bound → validated → deliberated → composed → published`
- WHEN it reaches the `deliberated` stage
- THEN its own definition states this stage is not its own and only the
  operator closes it — the same reasoning `deliberation-publish` states for
  its own `deliberated` stage

### Requirement: Every agent copies the shared return-contract discipline in its own bytes

Every `.claude/agents/*.md` MUST carry, in its own bytes and not by reference
to a shared fragment: a `## What you return` section naming `did`,
`stoppedAt`, `state`, `owed`; the "return facts that can be measured again,
never conclusions" discipline; and "measure before you assert". Each new
agent MUST name its own file in frontmatter and a skill that exists. Where a
new agent is authored from an existing agent as a template, every domain-bound
line — the frontmatter `description`, the `Skill:` path, and any prose naming
another skill's handoff shape — MUST be rewritten for the new domain's own
shape, not copied verbatim.

#### Scenario: A new agent carries the discipline in its own bytes

- GIVEN `experimental-publish` and the external-validation agent
- WHEN `test_agents.py`'s discipline tests run
- THEN both pass without either agent referencing a shared file, because the
  assertions read each agent's own bytes

#### Scenario: Domain-bound lines are adapted, not copied verbatim

- GIVEN `experimental-publish.md` is authored using `deliberation-publish.md`
  as a template
- WHEN its frontmatter `description`, its `Skill:` path, and its
  "Agreement is not arrival" section are written
- THEN all three name the experimental domain and its own entrance shape (or
  state it has none), not the mathematical domain's implementation-skill
  handoff

### Requirement: The arrival seal checks every agent whose bound skill declares a north

The seal MUST resolve the skill an agent is bound to from the agent's own
declared binding (the `.claude/skills/{name}/SKILL.md` path already asserted
elsewhere in the same file), not by guessing a directory from the agent's
filename. It MUST read the declared north from wherever the profile expresses
it, in whichever source language, not only Python `ast`-parseable
`OBJECTIVE_FLOW` assignments.

#### Scenario: An agent bound to a TypeScript-declared north is checked

- GIVEN an agent whose bound skill's north lives in a `.ts` profile
- WHEN the arrival seal runs
- THEN that agent is included in the checked set, not silently skipped

#### Scenario: Every pre-existing agent bound to a declaring skill is checked

- GIVEN the five agents that existed before this change
- WHEN the arrival seal runs
- THEN every agent bound to a skill with a declared north is checked, and the
  checked count is not limited to the single agent whose filename happens to
  match a Python-declaring skill directory

### Requirement: No vacuous pass

Any check with nothing to check — no agent bound to a north-declaring skill,
no baseline to validate, no URL to mark — MUST report not-applicable, never
the same shape as a genuine pass.

#### Scenario: Zero north-declaring skills reports not-applicable

- GIVEN a repository state where no agent is bound to a skill declaring a
  north
- WHEN the arrival seal runs
- THEN it reports not-applicable rather than silently passing an assertion
  that nothing exercised
