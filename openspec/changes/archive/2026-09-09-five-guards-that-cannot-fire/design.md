# Design: Five Guards That Cannot Fire

Scope ruled to **three** items: D1, D2 (comment only), D5. D3 and D4 are recorded below as alternatives considered.

## Technical Approach

Each item closes a guard that passes by asserting an absence. The common technique: make the assertion depend on a value only the working path can produce (a status, a *diverging* pair of counts), never on a number both the correct and the broken path emit.

## Architecture Decisions

| # | Decision | Alternatives considered | Rationale |
|---|---|---|---|
| A1 | `smoke-runner.ts` stubs return valid decisions (`'ACCEPT'` / `'APPROVE'`) and the full `TutorAssessment` / `ReviewerAssessment` shape | Cast the stubs `as any` to silence typecheck | A cast clears the errors and leaves the runtime lie intact. |
| A2 | The tutor stub derives `affectedEntryIds` from its own input (`input.context.fragments.map(f=>f.entryId)`), never `[]` | Constant `[]` | `validateTutorAssessment`'s second arm is `affectedEntryIds.some(...)`; on `[]` it is vacuously false. Only a non-empty, input-derived list exercises it. |
| A3 | Add one **REVIEW** turn (`revisa críticamente …`, `selectedEntryId:gamma`) to the smoke | Leave the reviewer stub compile-only | The smoke reaches no REVIEW or reviewer-required branch today, so the reviewer stub's *only* guard would be `tsc`. Half of D1 would ship unguarded at runtime. |
| A4 | The new D1 assertions live in `tests/proposal-deliberation-v2-smoke.test.mjs`; the runner exposes `deliberate` and `review` on its return | Assert inside the runner via `throw` | The runner is the fixture. A guard inside the fixture dies with the fixture; the existing `mutations!==0` throw already showed what an in-fixture check is worth. |
| A5 | D2 ships as a comment with **no new test**, reported as an unguarded change | A test asserting the comment's text | A byte-matching test guards the comment, not the behaviour — the exact vacuity this change exists to remove. `role-budget.ts`'s `BudgetedIntent` and the passing `status==='not_open'` assertion are already the behavioural guard. |
| A6 | D5's fixture lands on **`CANDIDATE_VALIDATION_FAILED`** via `CONCEPTUAL_REVISION` | `NO_MUTATION_PLAN`; `SOURCE_AUTHORITY_CONFLICT`; adapter-throw | See reachability table. |

## D5 — why `CANDIDATE_VALIDATION_FAILED`

`modelCalls` and `plannerCalls` diverge only where a role call joins a planner call. That is the `CONCEPTUAL_REVISION` branch of `execute()` alone: `calls` counts tutor+planner, `plannerCalls` is `buildConceptualPlan`'s own measured count. Every other caller of `publish()` passes them equal (`buildEditPlan` sets both to 1 together; the ambient paths pass `0,0`).

| Blocked return | Divergence reachable? |
|---|---|
| `NO_MUTATION_PLAN` | **No.** `buildConceptualPlan` throws `CONCEPTUAL_PATCH_BUDGET_EXCEEDED` on an empty action list, so the only callers reaching it carry `0/0`. |
| compile-catch | Yes, but needs a `compilePatches` failure mode. |
| `CANDIDATE_VALIDATION_FAILED` | **Yes, cheaply.** ← chosen |
| `SOURCE_AUTHORITY_CONFLICT` (refuse) | Only under a synthesized profile in a spawned child (`proposal-deliberation-source-authority.test.mjs`'s harness). Out of this fixture. |
| adapter-throw | Yes, via a wrapped adapter. Optional second case. |

**The fixture.** New `tests/proposal-deliberation-blocked-return-counts.test.mjs`:

- instruction matching `EXPERT_REQUIRED` (`matem|ecuaci|…`) **and** `conceptual`, and matching none of `reviewer|revisi[oó]n independiente|alto riesgo|varias secciones`;
- `roles.tutor` present, returning `decision:'ACCEPT'`, `riskLevel:'LOW'`, `affectedEntryIds` from its own context;
- a planner returning one `replace` whose `replacementText` contains a `#######` heading line → `validateCandidate`'s `markdown` check is false → `ok:false`;
- budget passes first (`maxModelCalls 2`, `maxPlannerCalls 1`, observed `2`/`1`).

Asserts `status==='blocked'`, `reason==='CANDIDATE_VALIDATION_FAILED'`, `modelCalls===2`, `plannerCalls===1`, and `plannerCalls!==modelCalls`.

## Mutation Plan

Anchors counted by **occurrence** (`rg -o`), never by line — three of the six D5 anchors sit on one physical line.

| Guard | Break | Must go red | Anchor (`rg -o`) |
|---|---|---|---|
| G1 tutor vocabulary | `'ACCEPT'` → `'ALLOW'` in `smoke-runner.ts` | smoke test: `deliberate.status==='deliberated'` | `"'ACCEPT'"` in `smoke-runner.ts`: 1 → 0 |
| G1b allowed-ids arm | `affectedEntryIds:input.context…` → `['not-an-entry']` | same assertion (validation throws → blocked) | `'affectedEntryIds:input\.context'`: 1 → 0 |
| G1c reviewer vocabulary | `'APPROVE'` → `'ALLOW'` | smoke test: `review.status==='deliberated'`; also `tsc` 0 → 1 | `"'APPROVE'"` in `smoke-runner.ts`: 1 → 0 |
| G3 blocked-return count | `plannerCalls:planned.plannerCalls` → `planned.modelCalls` at the `CANDIDATE_VALIDATION_FAILED` site | new test: `plannerCalls===1` | `'plannerCalls:planned\.plannerCalls'` in `orchestrator.ts`: **6 → 5** |
| G2 (D2) | delete the comment | **nothing.** Reported as unguarded per the proposal's own rule | n/a |

## What Breaks

**Producers.** `smoke-runner.ts` (stub shapes, new REVIEW turn, `deliberate`/`review` on the return); `proposal-workspace.ts` (comment); `orchestrator.ts` unchanged by D5 (776eb4f already fixed it — D5 adds only the missing guard); one new test file; the smoke test gains assertions.

**Products.** No managed revision, receipt, manifest or archived report changes shape: the smoke writes into a fresh `mkdtemp` per run and D5's fixture never publishes. Two on-disk *pinned* products do apply: `PROPOSAL_RESIDUE.wordBoundaryCount = 192` and `EQUATION_RESIDUE.substringCount = 124` in `tests/proposal-deliberation-domain-profile-lock.test.mjs` count occurrences across every core file, and both `smoke-runner.ts` and `proposal-workspace.ts` are counted files. **New text in either file must contain no `\bproposal\b` and no `equation` substring, and no word from either profile's north.** These pins are an established decision — raise, never re-baseline to fit a comment.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. The D5 fixture is in-process; no child is spawned.

## Migration / Rollout

No migration. Three independently revertible commits (D1, D2, D5).

## Alternatives Considered (ruled out of scope)

- **D3** — widening `OWN_TERM` to break the single-term tie rescales `confidence` (`score/12`) and the label/tag weight of 8. Weighed and deliberately left by a previous change.
- **D4** — of the three `artifact.marker` sites only `draft-materialization.ts` is safely closeable: `patch-compiler.ts` is byte-frozen, `revision-lifecycle-store.ts` is a deliberate cross-language drift anchor read by `tests/test_proposal_implementation.py`, and `tests/experimental-deliberation-domain-profile.test.mjs` actively asserts all three still spell it. One of three delivers nothing observable.

## Open Questions

- [ ] Extend D5 with the adapter-throw case (fifth site) in the same test file, or leave four of five `publish()` sites unguarded against divergence?
