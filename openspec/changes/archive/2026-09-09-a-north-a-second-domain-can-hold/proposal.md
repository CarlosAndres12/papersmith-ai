# Proposal: A north a second domain can hold

## Intent

`OBJECTIVE_FLOW` in `.claude/skills/_core/deliberation/engine/cli.mjs` hardcodes a
**mathematical** north: `purpose`, the `composed` stage and `arrival` all name
mathematics. `experimental-deliberation/cli.mjs` launches through that same file, so
the second domain reports the first domain's destination.

`proposal-deliberation/SKILL.md` justifies the placement by claiming a profile "would
say the same north whichever domain asked". Three of the flow's four fields falsify
it. The premise was untestable until a second domain existed; one exists now. The
domain lock cannot catch it — it scans core for values a profile *declares*, and the
north is not one.

## Scope

### In Scope

1. **Parametrize.** Structure stays in core (shape, presence in `STATUS`, presence on
   the engine's error paths). `purpose`/`stages`/`arrival` become a required profile
   field, validated like every other key in `domain-profile.ts`.
   `proposal-deliberation/profile.ts` re-declares today's exact text: behaviour
   unchanged, **files changed** — the first change to touch that skill.
2. **Generalize the test.** `tests/proposal-deliberation-objective-flow.test.mjs`
   derives its stages from the loaded profile rather than naming one skill.
3. **The experimental north.** Candidate `bound → validated → deliberated → composed →
   published`; `validated` sits before the draft, which is why this skill exists.
   `deliberated` stays a person's and unmeasurable.
4. **Two agents.** `experimental-publish` (near-copy of `deliberation-publish`) and one
   owning the external-validation stretch.
5. **A guard for the acceptance criterion** that no core file names a domain's subject
   matter — today nothing enforces it.

### Out of Scope

The eight items carried from the previous change: the unreachable `plannerCalls`
budget; the two `smoke-runner.ts` type errors; `CLOSE_DELIBERATION` having no budget
entry; the single-term lexical tie; the artifact marker still spelled in three core
files; the skill's missing required sources; the merge to `main`; the absent SDD
artifacts for the previous stretch. Tracked, and after this.

## Why the validation stretch is delegable

The doctrine forbids delegating a stage nothing can measure. Validation appears to
fail that test. It does not: `preservation-experimental.ts` already blocks
`url-without-verification-marker`, `baseline-missing-repository-url` and
`baseline-missing-venue-year`, all decidable from the bytes. A convention built to
stop invented URLs turns out to be what makes the stretch safe to hand over. It bounds
the *trace*, not the truth — a tag can be typed without a search — but that is still a
condition, which `deliberated` has none of.

## Why the agent discipline is copied, not extracted

All five existing agents repeat the return contract and "measure before you assert" in
their own bytes; there is no shared fragment. Ours are the sixth and seventh copies.
Extraction was considered and rejected: with copies a test asserts every agent
*carries* the discipline; with a shared file a test can only assert they *reference*
it, and whether one loaded and followed it is unmeasurable — a guard that cannot fire.

## Capabilities

### New Capabilities
- `deliberation-objective-flow`: the north as a profile-declared domain value, its
  required shape, its presence in `STATUS` and on the engine's error paths.
- `deliberation-delegated-stretches`: what an agent definition owes, and which stretch
  may be delegated at all.

### Modified Capabilities
- None. No requirement in the seven existing specs changes.

## Approach

`cli.mjs` already does top-level `await jiti.import(...)` for five engine modules; it
imports `domain-profile.ts` the same way and reads `DOMAIN.objective`. Validation joins
the existing `REQUIRED` list, so an incomplete profile refuses at load rather than
serving a partial north. Red-first per `strict_tdd`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `_core/deliberation/engine/cli.mjs` | Modified | `OBJECTIVE_FLOW` const removed; read from the profile |
| `_core/deliberation/engine/domain-profile.ts` | Modified | `objective` field + validation |
| `proposal-deliberation/profile.ts` | Modified | Declares today's exact text |
| `experimental-deliberation/profile.ts` | Modified | Declares the experimental north |
| `experimental-deliberation/SKILL.md` | Modified | Objective-flow section; delegation table |
| `tests/proposal-deliberation-objective-flow.test.mjs` | Modified | Profile-derived |
| `tests/proposal-deliberation-domain-profile-lock.test.mjs` | Modified | Scan every profile |
| `.claude/agents/experimental-*.md` | New | Two agents |
| `tests/test_agents.py` | Modified | Discipline-present test; a north the seal can read |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `test_agents.py`'s arrival seal reads only Python `OBJECTIVE_FLOW` and looks up a skill directory named after the *agent* — measured, it checks exactly one of five agents and skips `deliberation-publish` | High (already true) | Design phase decides whether to fix the seal here or carry it out; either way, state it |
| A profile-loading failure now precedes the error handler that would report it | Med | The engine already refuses without a profile; keep the refusal message intact |
| The lock reads one hardcoded profile path, so the experimental domain's names are unguarded in core | Med | Scan every `*/profile.ts` |
| Touching `proposal-deliberation` for the first time | Med | Its text is re-declared byte-identically; the generalized test proves it |

## Rollback Plan

Revert the commit range. The north returns to a core const, both skills keep
launching, no artifact on disk carries state from this change.

## Dependencies

None external. Post-merge Python baseline must be re-measured before work starts.

## Review Workload

| Item | Forecast |
|------|----------|
| 1 Parametrize | ~310 |
| 2 Experimental north | ~120 |
| 3 Two agents | ~150 |
| 4 Discipline test + core-subject guard | ~90 |
| **Total** | **~670 of 1400** |

`Decision needed before apply: No`
`Chained PRs recommended: No`
`400-line budget risk: Medium` (against the session budget of 1400: Low)

## Success Criteria

- [ ] No core file names any domain's subject matter, proven by a guard that goes red
      when one does.
- [ ] `proposal-deliberation` behaviour unchanged; its files changed.
- [ ] Node suite ≥ 524 pass / 0 fail.
- [ ] Python suite: post-merge baseline re-measured first, then held.
- [ ] `npm run typecheck` gains no error beyond the two known in `smoke-runner.ts`.
- [ ] Every new guard proven by mutation: break, red, restore, with the anchor count
      measured before and after. An unchanged anchor count means the mutation never ran.
- [ ] No vacuous pass: a check with nothing to check reports not-applicable.

## Proposal question round

Asked because this is interactive mode and the executor has no direct channel.

1. Should `validated` be a north stage at all, or stay the skill-procedure stage it is
   today (`SKILL.md` line 53 says explicitly it "is not an engine stage")? Promoting it
   makes the north claim a sequence the engine does not enforce.
2. Does the north's `entrances` field belong to the experimental domain? The
   mathematical one names a handoff from the implementation skill; the experimental one
   has an inbound dependency on `proposals/` that may or may not be the same shape.
3. Fix `test_agents.py`'s arrival seal inside this change, or record it as a finding?
   Measured, it checks one agent of five.
4. Is a `[verified: YYYY-MM-DD]` tag an acceptable closing condition, given it bounds
   the trace and not the truth?
