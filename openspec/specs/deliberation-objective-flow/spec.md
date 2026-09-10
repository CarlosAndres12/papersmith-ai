# Deliberation Objective Flow Specification

## Purpose

The north — why a deliberation session exists and where it must arrive — becomes
a required domain-profile field. Core keeps the north's structure (its shape,
its presence in `STATUS`, its presence on the engine's two CLI-level error
paths) and declares no domain's subject matter itself.

## Requirements

### Requirement: The north's content is profile-supplied, its structure is core's

The engine MUST NOT declare `purpose`, `stages`, or `arrival` text inline. The
domain-profile contract MUST require an `objective` field shaped
`{ purpose, stages: [{ stage, establishes, behindWhen }], arrival, entrances? }`.
A profile missing this field MUST fail closed at load with an explicit refusal
code naming the missing field, before any operation runs. The `validated`
stage's `establishes`/`behindWhen` text for `experimental-deliberation` MUST
name every byte-decidable condition the `validated` stage actually enforces,
including the dataset and validation-scheme rules added by this change,
alongside the protocol/metric/baseline conditions already named.
(Previously: the `validated` stage text named only the protocol, the metric,
and the baseline — not the dataset or the validation scheme, both of which
this change makes byte-decidable canonical-form rules reached before the
`validated` stage can be considered behind the author.)

#### Scenario: A complete profile loads unchanged

- GIVEN `proposal-deliberation/profile.ts` declares today's exact `purpose`,
  `stages`, and `arrival` text
- WHEN the engine loads that profile
- THEN `runStatus` and both CLI-level error paths emit that exact text under
  `objective`, byte-identical to pre-change behavior

#### Scenario: A profile missing the objective field refuses at load

- GIVEN a profile that omits `objective`
- WHEN the engine attempts to load it
- THEN loading fails with an explicit refusal code naming the missing field
- AND no operation runs against a partial north

#### Scenario: The experimental profile declares its own north

- GIVEN `experimental-deliberation/profile.ts` declares
  `bound → validated → deliberated → composed → published` with its own
  purpose and arrival text
- WHEN `experimental-deliberation/cli.mjs` loads that profile
- THEN `runStatus` and both error paths emit the experimental stages, not the
  mathematical ones

#### Scenario: The validated stage's condition text names the dataset and validation-scheme rules

- GIVEN `experimental-deliberation/profile.ts`'s `objective.stages[validated]`
  after this change
- WHEN its `behindWhen` text is read
- THEN it names the missing-dataset condition and the missing/inadequate
  validation-scheme condition, alongside the pre-existing protocol/metric/
  baseline conditions
- AND `SKILL.md`'s stage table row for `validated` carries the identical
  `establishes`/`behindWhen` text, moved together in the same change

### Requirement: The north's documented reach matches its actual reach

The north is emitted at exactly three sites: `runStatus` and the engine's two
CLI-level catch handlers. Typed refusals returned as values from
`tool.execute` carry no objective. A skill's doctrine document MUST NOT claim
a broader reach than these three sites.

#### Scenario: The doctrine states the north's actual reach

- GIVEN `proposal-deliberation/SKILL.md`'s objective-flow section
- WHEN it describes which refusals carry the north
- THEN it names `STATUS` and the two CLI-level error paths
- AND it MUST NOT state that every refusal the engine raises carries it

### Requirement: Structural conformance is verified per loaded profile

The test asserting stage names, stage order, the two-error-path count,
`STATUS` placement, the unmeasurable-stage wording, and the handoff entrance
MUST derive its expected stage list from the loaded profile rather than a
literal array naming one skill's stages. It is NOT required to compare
`purpose` free text, matching today's test. In addition, the doctrine-match
test MUST compare each stage row's `establishes` and `behindWhen` text against
the loaded profile's `objective.stages` entries for that stage, not only the
stage name and order — closing the gap in which a profile's stage content and
`SKILL.md`'s stage table could drift while the existing test stayed green.
(Previously: the equality test extracted only the first backticked token of
each stage-table row — the stage name — via `line.split('`')[1]`, and compared
it against `objective.stages` for name and order only; a separate test
compared only the `**Arrival:**` text. Neither compared `establishes` or
`behindWhen`.)

#### Scenario: The structural test passes against a different profile

- GIVEN a profile declaring different stage names in a different order
- WHEN the structural suite runs against that profile's skill
- THEN it verifies presence, order, the error-path count, `STATUS` placement,
  and the entrance, without asserting a hardcoded stage list

#### Scenario: A drifted establishes or behindWhen cell is caught

- GIVEN a profile's `objective.stages[N].behindWhen` text edited to a new
  value, with `SKILL.md`'s corresponding stage-table cell left unedited
- WHEN the doctrine-match test runs
- THEN it fails, naming the stage and the mismatched column, where
  today's test would pass because it reads only the stage-name token

#### Scenario: Matching establishes and behindWhen text passes

- GIVEN a profile's `objective.stages` and `SKILL.md`'s stage table carrying
  identical `establishes` and `behindWhen` text for every stage, moved
  together in the same commit
- WHEN the doctrine-match test runs
- THEN it passes for both the mathematical and the experimental profile

### Requirement: No core file names a domain's subject matter

A guard MUST scan every `*/profile.ts` under `.claude/skills/`, not one
hardcoded path, and MUST treat each profile's declared `names`, its composed
values, and its `objective` text (purpose, every stage's
`establishes`/`behindWhen`, arrival) as domain vocabulary. Any file under
`.claude/skills/_core/` containing one of another domain's values MUST fail
the guard. A guard that finds nothing to scan (no profiles present) MUST
report not-applicable, never a pass.

#### Scenario: A reintroduced subject word is caught

- GIVEN a core file spells a word appearing only in one profile's
  `objective.purpose` text (for example "mathematics")
- WHEN the guard runs
- THEN it fails, naming the file and the leaked value

#### Scenario: A profile naming its own domain in its own file passes

- GIVEN `proposal-deliberation/profile.ts` declares "mathematics" inside its
  own `objective` field
- WHEN the guard runs
- THEN it does not flag that profile's own file, only files outside its own
  domain's skill directory
