# Delta for Block Substitution

Base spec: `openspec/changes/only-the-block-changes/specs/block-substitution/spec.md`
(not yet archived; treated as the current main spec per this change's
proposal). This delta is purely additive — `--contract` is optional, no
existing `substitute` behavior changes, so only `ADDED Requirements` are
used, per the skill's ADDED-vs-MODIFIED rule.

**Existing-instances check**: `paper_scaffold.py` writes `main.tex` empty,
so no block was ever written with a provenance record before this change
exists — there is no pre-existing shape to migrate and no ambiguity between
"written before this field existed" and "never provenanced": the latter is
the only case that can occur, and it is exactly what `unprovenanced` names
(`contract-provenance`, `Requirement: A Block Written Without --contract Is
unprovenanced`).

## ADDED Requirements

### Requirement: substitute Accepts an Optional --contract Flag

`substitute` MUST accept an optional `--contract <path>`. Supplying it MUST
NOT alter what bytes are written to the target block's region — it only
adds a provenance record (`contract-provenance`,
`Requirement: A Provenance Record Is Written Only at substitute Time`) once
the substitution itself succeeds. `substitute` MUST refuse
`CONTRACT_UNREADABLE` (work-state) when `--contract <path>` is given and
the path cannot be read, and MUST write nothing — neither the block body
nor a provenance record — in that case.

#### Scenario: A provenanced substitution writes the same bytes as an unprovenanced one

- GIVEN identical block content submitted twice, once with `--contract
  sections/intro.md` and once without
- WHEN both substitutions run against otherwise-identical starting files
- THEN the resulting block bytes are identical in both cases; only the
  `provenance` region differs

#### Scenario: An unreadable contract path refuses before any write

- GIVEN `--contract sections/missing.md` names a path that does not exist
- WHEN `substitute` runs
- THEN it refuses `CONTRACT_UNREADABLE`, and neither the block nor the
  `provenance` region is written

### Requirement: --contract Is Additive to the Existing Refusal Roster

Every refusal `substitute` already raises (`BLOCK_ABSENT`,
`BLOCK_HAND_EDITED`, `CONTENT_CARRIES_MARKER`, `SUBSTITUTE_MODE_REQUIRED`,
`ADOPT_BODY_CONFLICT`, `SUBSTITUTION_NOT_LOCAL`, `TEX_MOVED`) MUST still
fire exactly as before when `--contract` is supplied; `CONTRACT_UNREADABLE`
is checked before any of them mutate `main.tex`, and MUST NOT suppress or
reorder any existing refusal that would otherwise fire.

#### Scenario: A hand-edited block still refuses even with --contract

- GIVEN a hand-edited block and a valid `--contract <path>`
- WHEN `substitute` targets that block
- THEN it refuses `BLOCK_HAND_EDITED`, exactly as without `--contract`
