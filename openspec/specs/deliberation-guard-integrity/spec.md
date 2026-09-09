# Deliberation Guard Integrity Specification

## Purpose

A guard that asserts an absence is only a guard if it can be made to fail.
This change closes three such sites: a smoke stub answering outside its own
decision vocabulary, a blocked-return field with no assertion able to tell
it from a copy-pasted value, and an unreachable throw with no comment
marking it intentional. Nothing here changes production behavior; every
requirement is a guard, a fix, or documentation.

## Requirements

### Requirement: Guard Regression Is Provable By Mutation

Every guard this change adds MUST be proven able to fail before its fix
lands: revert the target to its defective shape, show the guard fails, then
apply the fix. Occurrence counts MUST be measured by pattern match (e.g.
`rg -o`), never by line. A fix that lands without moving any test MUST be
reported as unguarded, never as a pass.

#### Scenario: A guard is shown to fail before the fix lands

- GIVEN a new guard for D1, D5, or D2, and a proposed fix with no test moved
- WHEN the target is reverted to its pre-fix shape
- THEN the guard's test fails; a fix moving no test is reported as unguarded

### Requirement: Smoke Stub Decisions Belong To Their Declared Vocabulary

`smoke-runner.ts`'s `tutor` and `reviewer` stubs MUST answer with a `decision`
that is a member of `tutorDecisions` and `reviewerDecisions` respectively.
`npm run typecheck` MUST report zero errors once this requirement is met —
these two stubs are the project's only two outstanding typecheck errors.

#### Scenario: The stubs answer inside both vocabularies

- GIVEN the smoke's `tutor` and `reviewer` stub objects
- WHEN their `decision` fields are checked against `tutorDecisions` and
  `reviewerDecisions`
- THEN both are members, and `npm run typecheck` reports 0 errors

### Requirement: The DELIBERATE Smoke Turn Asserts Reaching Deliberation

The smoke's `delibera sobre Gamma paragraph.` turn MUST assert that
`orchestrator.execute`'s DELIBERATE branch actually validated a tutor
assessment and returned `status:'deliberated'`, not only that
`mutations===0`. A blocked return (the outcome of a stub decision failing
`validateTutorAssessment` and being caught) MUST NOT satisfy this assertion,
because a blocked return also has `mutations===0`.

#### Scenario: A blocked DELIBERATE turn fails the smoke

- GIVEN the tutor stub answers a decision outside `tutorDecisions`
- WHEN the smoke runs the DELIBERATE turn
- THEN the smoke fails on that turn's status, not silently on a later step

#### Scenario: A genuinely deliberated turn passes

- GIVEN the tutor stub answers a decision inside `tutorDecisions`
- WHEN the smoke runs the DELIBERATE turn
- THEN `status==='deliberated'` and the smoke's assertion passes

### Requirement: Blocked Publish Returns Assert plannerCalls Independently Of modelCalls

At least one blocked return from `publish` other than `PLANNER_BUDGET_EXCEEDED`
MUST have a test asserting its `plannerCalls` value, and that test MUST cover
a turn where `plannerCalls` and `modelCalls` diverge (the turn also consulted
a tutor or reviewer, so `modelCalls > plannerCalls`). A test where the two
values are equal MUST NOT be treated as covering this requirement, since equal
numbers cannot distinguish a correct field from a copy-pasted one.

#### Scenario: A diverging blocked turn is asserted correctly

- GIVEN a turn that calls a tutor or reviewer before hitting a blocked return
  inside `publish`
- WHEN the blocked result's `plannerCalls` and `modelCalls` are compared
- THEN `plannerCalls < modelCalls`, and a test asserts the exact `plannerCalls`
  value, not merely that a `plannerCalls` field is present

### Requirement: The Unreachable CLOSE_DELIBERATION Throw Is Documented At Its Guard Site

The `CLOSE_DELIBERATION` early return inside `proposal-workspace.ts`'s
CHAT_DELIBERATION route stage MUST carry a comment stating that this early
return is why `resolveEffectiveOperationProfile`'s throw for an excluded
intent is unreachable for `CLOSE_DELIBERATION`, so a future reader does not
re-file it as a live defect. No behavior changes.

#### Scenario: A reader finds the reason at the guard site

- GIVEN the `if(params.operation==='CLOSE_DELIBERATION')` early return
- WHEN a reader reaches it while investigating the excluded-intent throw
- THEN a comment there names the reason, without needing to cross-reference
  `role-budget.ts` or `operation-spec.ts` to learn it

### Requirement: Unrelated Byte-Frozen Files And Baselines Stay Untouched

`successor-composite-engine.ts` and `patch-compiler.ts` MUST remain
byte-identical to their pre-change state. `npm test` MUST hold at 558
passing / 0 failing, and `.venv/bin/python -m unittest discover -s tests`
MUST hold at 2782 run / OK / 6 skipped.

#### Scenario: Frozen files and baselines are untouched or improved

- GIVEN the pre-change bytes of `successor-composite-engine.ts` and
  `patch-compiler.ts`, plus the 558/0 node and 2782 OK/6-skipped python
  baselines and 2 typecheck errors
- WHEN this change's guards and fixes land
- THEN both files stay byte-identical, node stays 558/0, python stays 2782
  OK/6 skipped, and typecheck drops to 0 errors

## Out of Scope

D3 (single-term lexical tie) and D4 (`artifact.marker` outside
`draft-materialization.ts`) are deferred, raised not absorbed. D2's
underlying budget-defect claim is disproven; only its documentation gap is
in scope.
