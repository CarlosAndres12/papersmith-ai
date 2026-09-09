# Proposal: Five Guards That Cannot Fire

## Intent

A pending-items list grew 8 → 14 and read as scope divergence. Triage found decisions and process notes filed beside real defects. Source measurement of the five alleged defects finds **three of five described inaccurately**. The shared trait of the genuine ones is a guard that *cannot fire*: a check that passes by asserting an absence, so a broken path stays green. Close the real ones; retire the false ones by name so the list stops growing.

## Scope

### In Scope

- **D1 — smoke stubs answer outside both vocabularies.** `smoke-runner.ts` lines 17–18 return `decision:'ALLOW'`, in neither `tutorDecisions` nor `reviewerDecisions`. Fix the stubs and strengthen the smoke's `DELIBERATE` assertion (see Findings).
- **D3 — single-term lexical query ties.** `OWN_TERM=3`/`CONTEXT_TERM=1` vs `ambiguityGate`'s `first.score-second.score<=4`: margin 2 blocks. Decide closeability without rescaling `confidence` (`score/12`) and label/tag weight 8.
- **D5 — no assertion separates `plannerCalls` from `modelCalls` on blocked returns.** Guard the `publish` blocked returns that lack one.
- **D4 (partial) — `draft-materialization.ts` reads `artifact.marker`.** Only the site that is neither byte-frozen nor cross-language-guarded.

### Out of Scope

- **D2 — disproven, not a defect.** No work.
- **D4 for `patch-compiler.ts` (byte-frozen) and `revision-lifecycle-store.ts` (Python drift guard).** Raised, not absorbed.
- Absent experimental-skill sources; merge to `main`; `PINNED_RESIDUE` holding two words; missing SDD artifacts for one delegated stretch; two informational verify warnings; `sd` unsuitability.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
None — behaviour-preserving defect closure plus guards. `deliberation-artifact-namespace` may gain a delta if D4's raised half is approved.

## Approach

Red-first per defect: write the guard, prove it fires by mutation, then fix. Count anchors **by occurrence (`rg -o`), never by line** — the two diverge, so a line-counted anchor can sit still while the mutation ran. A fix that moves no test is reported as an unguarded fix, not a pass.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `_core/deliberation/engine/smoke-runner.ts` | Modified | Valid decisions, `affectedEntryIds`; clears 2 typecheck errors |
| `tests/proposal-deliberation-v2-smoke.test.mjs` | Modified | Assert the `DELIBERATE` turn's status, not only `mutations` |
| `_core/deliberation/engine/target-resolver.ts` | Modified | D3, pending decision |
| `_core/deliberation/engine/draft-materialization.ts` | Modified | Read `artifact.marker` |
| `tests/experimental-deliberation-domain-profile.test.mjs` | Modified | Pins all three literals; must admit one reader |
| D5 test files | New/Modified | Blocked-return count guards |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| D3 rescale perturbs resolved loci | High | Decision gate before code; else defer |
| D4 partial leaves marker indirection unachieved | High | Raise; do not absorb |
| Strengthened smoke exposes further latent blocks | Med | Treat as findings, triage against scope rule |

## Rollback Plan

Per-defect commits, independently revertible. Revert restores baselines: node 558/0, python 2782 OK (6 skipped), 2 typecheck errors.

## Dependencies

User decisions on D3 rescale and D4's raised half.

## Success Criteria

- [ ] D1, D3, D5 closed; each guard proven to fire by mutation, anchor counted by occurrence
- [ ] `npm run typecheck` reaches 0 errors
- [ ] node 558/0 and python 2782 OK (6 skipped) hold or improve
- [ ] `successor-composite-engine.ts` and `patch-compiler.ts` byte-identical
- [ ] Every fix that moved no test reported as unguarded
