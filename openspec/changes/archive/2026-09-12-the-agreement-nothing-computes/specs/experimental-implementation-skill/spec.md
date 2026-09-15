# Delta for experimental-implementation-skill

## ADDED Requirements

### Requirement: `SKILL.md` No Longer Lists `compose`/`admit` As Unavailable

`SKILL.md`'s "Which commands are not available yet, and why" section MUST
drop its `compose`/`admit` entry once this domain declares a block locator
and those two commands become sealed cases. The section's remaining entry
(`materialize --stage scaffold`, which reads `assets/kit/`, unrelated to
the locator) MUST remain, since this change does not add a kit.

#### Scenario: The compose/admit entry is gone
- GIVEN this capability landed
- WHEN `SKILL.md`'s "not available yet" section is read
- THEN it no longer names `compose`/`admit`, and the stated reason matches
  what the shipped profile actually declares

#### Scenario: The stated availability matches what runs
- GIVEN `SKILL.md`'s updated text
- WHEN `compose`/`admit` are invoked against this skill's target
- THEN they run, rather than refusing as an unavailable command

### Requirement: `SKILL.md` Carries A Tutor Bullet For The Third, Unchecked Discrepancy Kind

`SKILL.md` MUST document, as guidance for the reading agent rather than as
a mechanical check, the third disagreement kind: an experiment's metric or
protocol does not correspond to what the claim it cites actually asserts.
No check MUST attempt to judge this — it requires reading both documents'
prose, and a check that tried would block correct work as often as it
caught broken work.

#### Scenario: The bullet exists and names no check
- GIVEN `SKILL.md`'s updated text
- WHEN it is read
- THEN it states the third kind as something for the agent to notice
  while reading, and no requirement in any capability of this change
  implements it as a refusal

#### Scenario: A metric/protocol mismatch does not refuse
- GIVEN an experiment whose declared metric does not match its cited
  claim's actual assertion, with the citation itself otherwise resolving
- WHEN the crossing check runs
- THEN it does not refuse for this mismatch — only Kind 1, Kind 2, and the
  no-crossing-declared code refuse

### Requirement: `SKILL.md` Documents Flow B's Existing Path Through To A Test Submission

`SKILL.md` MUST document that this skill reuses `proposal-implementation`'s
existing Flow B — the same gate at its drift step (asking whether the user
made the changes, never inferring it), the same path from a green suite
through to a submission — rather than defining a second, competing flow
for the experiments document. No new flow step MUST be invented here that
duplicates a decision Flow B already asks.

#### Scenario: The documented flow points at the existing one
- GIVEN `SKILL.md`'s updated text
- WHEN it describes the path from implementation to a test submission
- THEN it names Flow B's existing steps and gate, not a new parallel
  sequence

#### Scenario: The drift gate is not duplicated
- GIVEN a code/proposal discrepancy reaches the point where repair
  direction matters
- WHEN the flow is followed
- THEN the same "did the user make this change" gate Flow B's drift step
  already asks is the one exercised — no second gate asks it again
