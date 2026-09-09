# Tasks: Five Guards That Cannot Fire

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~60 (dense one-statement-per-line style) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR, 3 independently revertible commits (D1, D5, D2) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | PR | Focused test | Runtime harness | Rollback boundary |
|------|------|----|--------------|-----------------|--------------------|
| 1 D1 | Valid stub decisions + REVIEW turn | PR 1 | `node --test tests/proposal-deliberation-v2-smoke.test.mjs` | Smoke is the real scenario (mkdtemp, real orchestrator) | revert `smoke-runner.ts` + smoke test |
| 2 D5 | Guard `CANDIDATE_VALIDATION_FAILED`'s `plannerCalls` | PR 1 | `node --test tests/proposal-deliberation-blocked-return-counts.test.mjs` | New test only; no production diff (776eb4f already fixed it) | delete new test file |
| 3 D2 | Document unreachable throw | PR 1 | N/A — comment only (A5) | N/A | revert comment hunk |

## Phase 1: D1 — Smoke Stub Vocabulary + REVIEW Turn (RED-first)

- [x] 1.1 RED: `tests/proposal-deliberation-v2-smoke.test.mjs` — assert `result.deliberate.status==='deliberated'`; failed pre-fix (stub `'ALLOW'` → blocked)
- [x] 1.2 GREEN: `smoke-runner.ts` tutor stub → `decision:'ACCEPT'`, full `TutorAssessment` shape, `affectedEntryIds:input.context.fragments.map(f=>f.entryId)`
- [x] 1.3 GREEN: reviewer stub → `decision:'APPROVE'`, full `ReviewerAssessment` shape
- [x] 1.4 RED: added REVIEW turn (`revisa críticamente Gamma paragraph.`, `selectedEntryId:gamma`) in `runProposalDeliberationSmoke()`; exposed `deliberate`/`review` on return; asserts `result.review.status==='deliberated'`
- [x] 1.5 Confirmed 1.1 and 1.4 pass together
- [x] 1.6 Mutation G1: `'ACCEPT'`→`'ALLOW'`; `rg -o "'ACCEPT'"` 1→0; 1.1 failed (`deliberate.status:'blocked'`); restored
- [x] 1.7 Mutation G1b: `affectedEntryIds:input.context…`→`['not-an-entry']`; `rg -o` 1→0; 1.1 failed (`deliberate.status:'blocked'`); restored
- [x] 1.8 Mutation G1c: `'APPROVE'`→`'ALLOW'`; `rg -o "'APPROVE'"` 1→0; 1.4 failed (`review.status:'blocked'`); `tsc` 0→1; restored
- [x] 1.9 Confirmed edits add no `\bproposal\b` word / `equation` substring (domain-profile-lock 12/12 pass, both pins unchanged)
- [x] 1.10 UNPLANNED FIX, in-scope: the smoke reused a stale `gamma` entryId across the content-mutating "revisión conceptual…" turn into the DELIBERATE turn. Entry IDs are `sha256(parentType:ordinal:sha256(text))` (`document-index.ts`), content-dependent, so after the conceptual-revision turn rewrote the paragraph text the old `gamma` id no longer existed in the rebuilt index. `resolveTargets` fell through its `byId` lookup to a free-text fuzzy match on the stale id string itself, producing `status:'ambiguous'` — BEFORE the tutor was ever invoked, and regardless of stub decision validity. This is pre-existing and disproves design's D1-ripple claim for the real end-to-end smoke. Fixed by re-fetching `gamma=await paragraph(root,'Gamma')` right after the conceptual-revision turn, before the DELIBERATE turn — the same refetch pattern the script already used elsewhere after every content-mutating turn. See "Deviations" below.

## Phase 2: D5 — plannerCalls Divergence Guard (RED-first, test-only)

- [x] 2.1 RED→GREEN: new `tests/proposal-deliberation-blocked-return-counts.test.mjs` — instruction `'revisión conceptual teórico de la ecuación.'` matches `EXPERT_REQUIRED`+`conceptual`, no reviewer trigger; `roles.tutor`→`decision:'ACCEPT'`,`riskLevel:'LOW'`,input-derived `affectedEntryIds`; planner returns one `replace` action with a `#######` heading (fails `validateCandidate`'s markdown check); asserts `status==='blocked'`, `reason==='CANDIDATE_VALIDATION_FAILED'`, `modelCalls===2`, `plannerCalls===1`, `plannerCalls!==modelCalls`
- [x] 2.2 Confirmed 2.1 passes against unmodified `orchestrator.ts` (776eb4f already fixed it; no production edit)
- [x] 2.3 Mutation G3: at the `CANDIDATE_VALIDATION_FAILED` site only, `plannerCalls:planned.plannerCalls`→`planned.modelCalls`; 2.1 failed (`2 !== 1`); `rg -c -o 'plannerCalls:planned\.plannerCalls' orchestrator.ts` 6→5 confirmed (plain `rg -c` wrongly reads 4→4 — verified, never used for the pass/fail call); restored via a copy made before mutating; `git diff` confirms byte-identical to HEAD afterward
- [x] 2.4 Report: the other 4 `publish()` sites and the adapter-throw site stay unguarded by design (reachability table), not an oversight

## Phase 3: D2 — Document the Unreachable Throw (unguarded, per A5)

- [x] 3.1 `proposal-workspace.ts`: added an 11-line comment above `if(params.operation==='CLOSE_DELIBERATION')` in the `CHAT_DELIBERATION` route stage naming why this early return makes `resolveEffectiveOperationProfile`'s excluded-intent throw (`UNSUPPORTED_OPERATION_PROFILE`, via `role-budget.ts`'s `BudgetedIntent` excluding `CLOSE_DELIBERATION`) unreachable here
- [x] 3.2 Confirmed the comment spells no `\bproposal\b` word / `equation` substring (domain-profile-lock 12/12 pass, both pins unchanged)
- [x] 3.3 Reported as unguarded — no test asserts comment text; `BudgetedIntent` plus the existing behavioral assertions remain the guard

## Phase 4: Verification

- [x] 4.1 `npm run typecheck` → 0 errors (confirmed after every TS edit and after every mutation restore)
- [x] 4.2 `npm test` → 559 pass / 0 fail (558 baseline + 1 new D5 test)
- [x] 4.3 `.venv/bin/python -m unittest discover -s tests` → see apply report for the verbatim result line
- [x] 4.4 Confirmed `successor-composite-engine.ts` and `patch-compiler.ts` byte-identical (never touched, `git diff` empty); `orchestrator.ts` (mutated then restored for G3) also confirmed byte-identical via `git diff` against HEAD
- [x] 4.5 Re-ran `proposal-deliberation-domain-profile-lock.test.mjs` after every production/comment edit — 12/12 pass each time; `EQUATION_RESIDUE` (124) and `PROPOSAL_RESIDUE` (192) unchanged
- [x] 4.6 No pin needed re-baselining — nothing raised

## Deviations from design/tasks (report this, do not silently absorb)

Design's ripple claim for D1 ("the ONLY observable change is that turn's own
status: blocked -> deliberated") does not hold for the real end-to-end smoke
run. A pre-existing bug (stale, content-hashed `gamma` entryId reused across
a content-mutating turn — see 1.10) meant the DELIBERATE turn was actually
resolving to `status:'ambiguous'` before any of this change's edits, not
`status:'blocked'`/`INVALID_TUTOR_ASSESSMENT` as measured/claimed in
design.md. This was fixed inside `smoke-runner.ts` (already an in-scope D1
file) with a one-line entryId refetch, mirroring the file's own existing
convention; no protected file (`orchestrator.ts`, `successor-composite-engine.ts`,
`patch-compiler.ts`) was touched to do it.
