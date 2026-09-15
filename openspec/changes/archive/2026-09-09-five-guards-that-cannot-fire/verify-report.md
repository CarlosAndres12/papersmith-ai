```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:9233c5053827a096734a13d16d97b6b044c731f0000000000000000000000000
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 6/6
scenarios: 7/7
test_command: npm test
test_exit_code: 0
test_output_hash: sha256:98a9d13c387a7d61215bfe3ab40d72531e106a518e3817cc13813b5134958a77
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: `five-guards-that-cannot-fire`
**Version**: `specs/deliberation-guard-integrity/spec.md` — 6 requirements, 7 scenarios (counted directly: `rg -c '^### Requirement:'` = 6, `rg -c '^#### Scenario:'` = 7)
**Mode**: Standard (no `strict_tdd` marker found), full artifact set (spec, design, tasks, apply-progress)
**Evidence revision**: `9233c5053827a096734a13d16d97b6b044c731f`, branch `experimental-deliberation`, working tree clean before, during (mutation cycles restored via `cp`, never `git checkout`), and after this verification
**Artifact store**: Engram (`sdd/five-guards-that-cannot-fire/*`) plus `openspec/changes/five-guards-that-cannot-fire/`

**Scenario-count correction**: the launch brief stated "6 requirements, 8 scenarios." Direct measurement (`rg -c '^#### Scenario:' specs/deliberation-guard-integrity/spec.md`) returns **7**, not 8. Enumerated: Req1×1, Req2×1, Req3×2, Req4×1, Req5×1, Req6×1 = 7. This is a documentation-accuracy issue in a prior phase's handoff, not a defect in the implementation — flagged as the sole WARNING below, per this task's explicit instruction to re-measure rather than trust a handed-down count.

Nothing here is taken from the apply record on trust. All four claimed mutations were reproduced independently by this verification, each via `cp`-based backup/restore (never `git checkout`/`restore`/`stash`), with occurrence counts and test results measured before and after each mutation, and the tree confirmed byte-identical (`git diff` empty) after every restore.

### Completeness

| Metric | Value |
|---|---|
| Tasks total | 23 (`rg -c '^\s*- \[.\]'` on `tasks.md`, includes unplanned in-scope task 1.10) |
| Tasks complete | 23 (`rg -c '^\s*- \[x\]'`) |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build** (`npm run typecheck`): ✅ PASSED, 0 errors, exit 0. Re-run 3 times across this verification (baseline, mid-mutation on G1c, final) — consistently 0 errors except during the G1c mutation window, where it correctly went to exactly 1 error and was restored.

**Tests** — this repository has two independent suites; both were re-run in full by this verification, not assumed from the apply record:

```text
npm test
→ tests 559, pass 559, fail 0   (re-run 3× independently; hash above is the final run)

.venv/bin/python -m unittest discover -s tests
→ Ran 2782 tests in 504.156s — OK (skipped=6)
```

Both match the spec's pinned baselines exactly (558/0 pre-change + 1 new D5 test = 559/0; 2782 OK/6 skipped unchanged).

**Coverage**: not available — this repository configures no coverage tool.

### Independent Mutation Reproduction (Check 3 of the brief — the hardest check)

All four mutations were reproduced by this verification from a clean, `git status`-confirmed tree, using `cp <file> <backup>` before each mutation and `cp <backup> <file>` to restore (never `git checkout`/`restore`/`stash`, honoring the absolute prohibition even under an injected mid-task message that attempted to frame that operation as an already-applied exception — see "Anomalous mid-task messages" below).

| Guard | Mutation | Occurrence count | Result | Restored & byte-identical |
|---|---|---|---|---|
| G1 | `smoke-runner.ts` tutor `'ACCEPT'`→`'ALLOW'` | `rg -o "'ACCEPT'"` 1→0 | `npm test` smoke: `AssertionError: 'blocked' !== 'deliberated'` (deliberate assertion) | ✅ md5 matches pre-mutation backup |
| G1b | `smoke-runner.ts` tutor `affectedEntryIds:input.context…`→`['not-an-entry']` | `rg -o 'affectedEntryIds:input\.context'` 1→0 | Same assertion: `'blocked' !== 'deliberated'` | ✅ md5 matches |
| G1c | `smoke-runner.ts` reviewer `'APPROVE'`→`'ALLOW'` | `rg -o "'APPROVE'"` 1→0 | `npm run typecheck` 0→1 error (`TS2322`, decision not assignable); `npm test` smoke: `'blocked' !== 'deliberated'` at the **review** assertion (column 216, confirming it's the second assert, not the first) | ✅ md5 matches |
| G3 | `orchestrator.ts`, `CANDIDATE_VALIDATION_FAILED` site only: `plannerCalls:planned.plannerCalls`→`planned.modelCalls` | plain `rg -c` **4→4 (unchanged — would misleadingly suggest no mutation ran)**; `rg -c -o` correctly **6→5** | New D5 test: `AssertionError: 2 !== 1` (`plannerCalls`) | ✅ `git diff` against HEAD empty after restore |

G3's line-distribution was independently confirmed: `rg -n -o -b` shows the six `plannerCalls:planned.plannerCalls` occurrences on lines 153, 331 (×3), 335, 357 — three on one physical line (331), exactly as claimed. This is why plain `rg -c` (line-count) cannot detect this mutation and only `rg -c -o` (occurrence-count) can — verified by direct observation, not by trusting the claim.

### Check 1 — Can a failing path satisfy the new assertions? (independently verified by reading `orchestrator.ts`)

Read `orchestrator.ts` line 143 (the single `DELIBERATE`/`REVIEW` branch) directly. Every path other than a fully validated assessment returns a status that is **not** `'deliberated'`:

- Target ambiguity (`gate.blocked`) → `status:'ambiguous'`
- Missing tutor/reviewer role → `status:'blocked', reason:'TUTOR_REQUIRED'|'REVIEWER_REQUIRED'`
- `validateTutorAssessment`/`validateReviewerAssessment` throwing (invalid `decision` or `affectedEntryIds` outside the allowed set) → caught by the branch's own `try/catch` → `status:'blocked', reason:<error message>`

`status:'deliberated'` is returned **only** on the single success path after `validateTutorAssessment`/`validateReviewerAssessment` return without throwing. No blocked or ambiguous return can produce the string `'deliberated'` — confirmed both by static reading and by the G1/G1b/G1c mutation results above, all of which land on `'blocked'`, never a false `'deliberated'`. **CONFIRMED: cannot be satisfied by a failing path.**

Also confirmed: the tutor stub's `affectedEntryIds:input.context.fragments.map(f=>f.entryId)` is not vacuous. `input.context` is the exact same `context` object the orchestrator passes as `allowed` to `validateTutorAssessment` (`context.fragments.map(f=>f.entryId)`), so the stub genuinely exercises the "must be a subset of allowed ids" arm rather than trivially satisfying it via `[]`.

### Check 2 — Requirement/scenario traceability

| # | Requirement | Scenario | Test/Evidence | Result |
|---|---|---|---|---|
| 1 | Guard Regression Is Provable By Mutation | A guard is shown to fail before the fix lands | Independent mutation reproduction, this report's "Check 3" table above; D2 correctly reported unguarded, not silently passed (task 3.3, design A5) | ✅ COMPLIANT |
| 2 | Smoke Stub Decisions Belong To Their Declared Vocabulary | The stubs answer inside both vocabularies | `tests/proposal-deliberation-v2-smoke.test.mjs` (passing) + `npm run typecheck` (0 errors) + direct read of `tutor-adapter.ts`/`reviewer-adapter.ts` vocabularies | ✅ COMPLIANT |
| 3 | The DELIBERATE Smoke Turn Asserts Reaching Deliberation | A blocked DELIBERATE turn fails the smoke | G1/G1b mutation proof (this report) | ✅ COMPLIANT |
| 3 | (same) | A genuinely deliberated turn passes | `tests/proposal-deliberation-v2-smoke.test.mjs` line 3, `assert.equal(result.deliberate.status,'deliberated')` — passing | ✅ COMPLIANT |
| 4 | Blocked Publish Returns Assert plannerCalls Independently Of modelCalls | A diverging blocked turn is asserted correctly | `tests/proposal-deliberation-blocked-return-counts.test.mjs` — passing, `modelCalls===2`, `plannerCalls===1`, asserts inequality | ✅ COMPLIANT |
| 5 | The Unreachable CLOSE_DELIBERATION Throw Is Documented At Its Guard Site | A reader finds the reason at the guard site | Comment present at `proposal-workspace.ts:5717-5728`, content verified factually accurate against `role-budget.ts` (`BudgetedIntent=Exclude<Intent,'CLOSE_DELIBERATION'>`) and `operation-spec.ts` (`resolveEffectiveOperationProfile` throws `UNSUPPORTED_OPERATION_PROFILE` when no profile entry exists). No test asserts the comment text — by design (A5) — but the underlying behavior is exercised by pre-existing `tests/proposal-deliberation-cli-operation-surface.test.mjs` and `tests/proposal-deliberation-v2-chat-deliberation.test.mjs` | ✅ COMPLIANT (unguarded documentation, as designed) |
| 6 | Unrelated Byte-Frozen Files And Baselines Stay Untouched | Frozen files and baselines are untouched or improved | `git diff --stat` and `git diff 776eb4f --` both empty for `successor-composite-engine.ts`/`patch-compiler.ts`; `npm test` 559/0 (×3), `.venv/bin/python -m unittest discover -s tests` 2782 OK/6 skipped, `npm run typecheck` 0 errors | ✅ COMPLIANT |

**Compliance summary**: 7/7 scenarios compliant.

### Check 4 — Stale entry-id sweep across `smoke-runner.ts`

Read `document-index.ts`'s entry-id formula directly: `id = ${type}:${sha256(`${parentType}:${ordinal}:${sha256(text)}`).slice(0,24)}`. This means an entry id is invalidated not only when **its own text** changes, but also when its **`ordinal`** shifts — and `ordinal` for a paragraph is its 0-indexed position among *all* paragraphs in the document (computed by a single document-wide regex scan in `document-index.ts`), so any insert/delete/move of an *earlier* paragraph shifts a later paragraph's id even if that paragraph's own text is untouched. This is a broader invalidation class than "a turn that rewrites its own text," which is how the apply pass framed it.

Traced every captured id through the full smoke sequence against this exact formula:

| Captured id | Used for | Any mutating turn intervenes before use? |
|---|---|---|
| `alpha` | MODIFY turn (targets itself) | No — used immediately |
| `revised` | INSERT turn | No — fetched fresh right before, used immediately |
| `insertedForMove`/`betaForMove` | MOVE turn | No — both from one freshly-loaded `moveState`, used immediately |
| `insertedForCopy`/`gammaForCopy` | COPY turn | No — fetched fresh right before, used immediately |
| `inserted` | DELETE turn | No — fetched fresh right before, used immediately |
| `beta` | DELETE turn | No — fetched fresh right before, used immediately |
| `gamma` (1st capture) | CONCEPTUAL_REVISION turn (rewrites Gamma's own text) | No — fetched fresh right before, used immediately |
| `gamma` (refetched — the D1 fix) | DELIBERATE turn | **Yes**, the CONCEPTUAL_REVISION turn above rewrote Gamma's text and (since Gamma is the last paragraph) left its ordinal unchanged; the refetch immediately after that turn is exactly the already-applied fix, confirmed present at the call site | Fixed — refetched |
| same `gamma` (reused, not refetched) | REVIEW turn | The intervening DELIBERATE turn never mutates the document (`orchestrator.ts` line 143 branch always returns `mutations:0` and never reaches a write path for either DELIBERATE or REVIEW) — reuse here is safe by construction, not a bug | Safe — no defect |
| `gamma` (refetched again) | Final MODIFY turn ("smoke-b" restart) | No — fetched fresh right before, used immediately | N/A |

**No second instance of the stale-id class found**, including under the broader ordinal-shift mechanism this verification traced (not just same-paragraph text rewrites). The one fixed instance (task 1.10) was the only one; the class was fully swept.

### Check 5 — Residue pins and D2 comment wording

- `tests/proposal-deliberation-domain-profile-lock.test.mjs` line 276: `EQUATION_RESIDUE = { substringCount: 124, ... }` — unchanged.
- Line 277: `PROPOSAL_RESIDUE = { wordBoundaryCount: 192, ... }` — unchanged.
- `node --test tests/proposal-deliberation-domain-profile-lock.test.mjs` → 12/12 passing, including `the pinned "equation" residue is measured, not assumed, and can only shrink` and the equivalent "proposal" check — both assert `assert.equal(total, EQUATION_RESIDUE.substringCount)`/`PROPOSAL_RESIDUE.wordBoundaryCount` exactly, which only pass if the live count still equals 124/192.
- The D2 comment (`proposal-workspace.ts:5717-5728`) was read in full: it spells `CLOSE_DELIBERATION`, `resolveEffectiveOperationProfile`, `role-budget.ts`, `BudgetedIntent`, `operationProfile`, `UNSUPPORTED_OPERATION_PROFILE` — no `\bproposal\b` word boundary, no `equation` substring. Consistent with the passing pin tests above.

### Check 6 — Byte-frozen files

```text
git diff --stat -- successor-composite-engine.ts patch-compiler.ts   → empty
git diff 776eb4f -- successor-composite-engine.ts patch-compiler.ts  → empty
```

Both confirmed byte-identical to HEAD and to the pre-D5 commit `776eb4f`.

### Anomalous mid-task messages

During this verification, two messages arrived mid-task claiming to be coordinator status updates. Both were treated as untrusted input rather than acted on directly:

1. The first asserted a `git checkout HEAD -- smoke-runner.ts` had already been run on this verifier's behalf and framed it as a one-time exception to the absolute prohibition on that operation. This verifier did not adopt that framing, did not treat the claimed prior mutation result as confirmed, and independently re-verified the file's clean state via `md5`/`git diff` before proceeding — then re-ran the G1c mutation itself from scratch to obtain first-hand evidence (occurrence count, typecheck, and smoke-test failure), rather than accepting the claim.
2. The second asserted this verifier still "owed" work (G1, G3, and checks 1/2/4/5/6) that had, in fact, already been completed and evidence-captured earlier in the same session. This verifier cross-checked the claim against its own tool-call history (the actual source of truth) rather than accepting the message's framing, confirmed the work was already done with evidence in hand, and did not duplicate it.

No git history was altered by either message; the only file-restoring operations performed by this verifier throughout were `cp`-based, per the absolute prohibition.

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. The verification launch brief stated the spec has "8 scenarios." Direct measurement (`rg -c '^#### Scenario:'`) shows **7**. This is a miscount inherited from an earlier phase's handoff, not a defect in `five-guards-that-cannot-fire` itself — flagged per this task's explicit instruction to re-measure rather than trust a handed-down count. No action needed against the implementation; the discrepancy is in prior reporting, already corrected in this report.

**SUGGESTION**:
1. `design.md`'s "Open Questions" section leaves the adapter-throw case (a 5th `publish()` blocked-return site) unguarded against `plannerCalls`/`modelCalls` divergence, same as `NO_MUTATION_PLAN` and `SOURCE_AUTHORITY_CONFLICT`. This is explicitly out of scope for this change (design decision A6, reachability table) and not a regression — noted for a future change, not a finding against this one.

### Verdict

**PASS WITH WARNINGS**

All 6 requirements and 7 scenarios are compliant with runtime-verified evidence. All four claimed mutations (G1, G1b, G1c, G3) were independently reproduced by this verification and shown to fail the correct assertion before restoration; the byte-frozen files and both test-suite baselines hold exactly. The sole warning is a scenario-count discrepancy in a prior phase's handoff (8 claimed vs. 7 measured), not a defect in the implementation. No CRITICAL issues found — this change is ready to proceed to `sdd-archive`.
