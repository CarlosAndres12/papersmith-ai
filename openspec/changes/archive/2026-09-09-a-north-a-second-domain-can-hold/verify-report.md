# Verification Report: a-north-a-second-domain-can-hold

**Change**: `a-north-a-second-domain-can-hold`
**Mode**: Full artifacts (proposal, design, specs, tasks all present)
**Verified against**: HEAD `9d4e198`, clean tree, branch `experimental-deliberation`

## Completeness

All 6 phases (0-5) in `tasks.md` are marked `[x]`. Cross-checked against the actual
diff (`git diff 31a7b71..HEAD --shortstat`: 34 files changed, 2014 insertions(+), 243
deletions(-)) and against source inspection below — the `[x]` marks correspond to real,
present changes in every case I checked. Two deviations from tasks.md's literal wording
are documented inline in tasks.md and in the apply-progress record, and both are
measurement-driven corrections (task 4.3's `stretch: terminal` count 3→2; task 5.2's
"2778 held" baseline corrected to 2779 with a stated +1 delta). Both deviations verified
sound (see "Measured state" and "Traceability" below).

**Note on the launch brief's scenario count**: I was asked to verify "8 requirements and
17 scenarios." I count 8 requirements and exactly **14** scenarios in the two spec files
(confirmed by `rg -c '^#### Scenario:'` → 7 + 7). This is a discrepancy in the count I was
given, not a defect in the artifacts — noted so it isn't silently carried forward.

## Measured state (re-run myself, not re-derived from the apply report)

| Command | Claimed | Measured | Match |
|---|---|---|---|
| `npm test` | 548 pass / 0 fail | 548 pass / 0 fail | ✅ |
| `.venv/bin/python -m unittest discover -s tests` | Ran 2779, OK (skipped=6) | Ran 2779 tests in 446.806s, OK (skipped=6) | ✅ |
| `npm run typecheck` | exactly 2 errors, both `smoke-runner.ts` | exactly 2 errors, both `smoke-runner.ts` (TutorAdapter/ReviewerAdapter) | ✅ |

Tree was clean before and after every run (`git status --porcelain` empty).

## Requirement-to-test traceability

### Domain: `deliberation-objective-flow` (4 requirements, 7 scenarios)

| # | Scenario | Test | Status |
|---|---|---|---|
| 1.1 | A complete profile loads unchanged | `proposal-deliberation-objective-flow.test.mjs` (static: doctrine-vs-profile text match, C-1 absence scan, error-path/STATUS regex on `cli.mjs` source) | **WARNING** — see below |
| 1.2 | A profile missing the objective field refuses at load | `proposal-deliberation-domain-profile-objective.test.mjs` (7 live-process tests, synthetic `TESTDOMAIN` profile through the real `domain-profile.ts` validator) | ✅ COVERED |
| 1.3 | The experimental profile declares its own north | `experimental-deliberation-domain-profile.test.mjs`: `runStatus on the experimental CLI emits the experimental stages...` and `a malformed request... still carries the experimental north` — spawns the **real** `experimental-deliberation/cli.mjs` end to end | ✅ COVERED, real runtime |
| 2.1 | The doctrine states the north's actual reach | *(none found)* | **CRITICAL — UNTESTED**, see below |
| 3.1 | The structural test passes against a different profile | `proposal-deliberation-objective-flow.test.mjs`'s per-pair loop, run against 2 real profiles with genuinely different stage sets (4 vs 5 stages) | ✅ COVERED |
| 4.1 | A reintroduced subject word is caught | `proposal-deliberation-domain-profile-lock.test.mjs`: `C-3: no NEW subject word...` | ✅ COVERED + **CONFIRMED by my own mutation** (added "mathematics" to `edit-planner.ts`, reproduced the exact spec example, restored) |
| 4.2 | A profile naming its own domain in its own file passes | No dedicated assertion; true by construction — `profile.ts` files live outside the scanned `CORE_DIR` (`.claude/skills/_core/deliberation/engine`), so they are never in the leak-scan input at all | ✅ Sound by scope, not exercised by a positive-case test |

### Domain: `deliberation-delegated-stretches` (4 requirements, 7 scenarios)

| # | Scenario | Test | Status |
|---|---|---|---|
| 1.1 | The validation stretch is delegated | `experimental-deliberation-preservation.test.mjs` (pre-existing mechanism, `violations()` for all 3 named rules); `experimental-validation.md` correctly names the same 3 rules (verified by reading) | ✅ COVERED (mechanism); agent-text correctness verified by reading, not automated (see note below) |
| 1.2 | The deliberated stage is never delegated | *(none found)* | **CRITICAL — UNTESTED**, see below |
| 2.1 | A new agent carries the discipline in its own bytes | `test_agents.py::test_every_agent_carries_the_shared_role_discipline` | ✅ COVERED, ran and passed (12/12 in `test_agents.py`) |
| 2.2 | Domain-bound lines are adapted, not copied verbatim | *(none found)* | **CRITICAL — UNTESTED**, see below |
| 3.1 | An agent bound to a TypeScript-declared north is checked | `test_agents.py::test_a_description_carries_the_arrival_its_skill_declares` | ✅ COVERED + **CONFIRMED** (see "The seal" below) |
| 3.2 | Every pre-existing agent bound to a declaring skill is checked | same test, coverage-equality assertion | ✅ COVERED + **CONFIRMED** |
| 4.1 | Zero north-declaring skills reports not-applicable | Code path exists (`self.skipTest(...)` at line 321-323 when `expected` is empty) | Sound by inspection; cannot be exercised at runtime without a contrived repo state — not a real gap, just inherently hypothetical |

**On the 3 CRITICAL-UNTESTED findings**: in every one of these three cases I read the
actual file and independently confirmed the underlying claim is **true right now** —
`proposal-deliberation/SKILL.md` and `deliberation-publish.md` both correctly state the
3-site reach and say nothing broader; `deliberation-publish.md` and `experimental-publish.md`
both state the `deliberated` stage is not theirs; `experimental-publish.md`'s "Agreement is
not arrival" section correctly says "this domain loses work" rather than copying
`deliberation-publish.md`'s "this pair of skills loses work" verbatim. These are not
behavioral bugs. They are pure regression-coverage gaps: nothing in the automated suite
would catch a future edit that reintroduced the false "every refusal carries it" claim, or
let a future agent silently drop the `deliberated` disclaimer, or let a future
template-copy paste "this pair of skills" into a domain with no such pair. Per this skill's
own decision gate ("Spec scenario has no passing covering test → CRITICAL"), I am
reporting them as CRITICAL rather than downgrading them myself — the correction is cheap
(3 short `assert.match`/`assertIn` additions) and the change should not be considered
fully closed while these three scenarios have no test standing behind the `[x]` in
tasks.md.

## Hardest checks, in the order requested

### 1. Requirement-to-test traceability — see table above.

3 of 14 scenarios have zero covering test (CRITICAL, behavior verified true by hand but
unprotected). 1 scenario has meaningfully weaker coverage than its sibling (WARNING). 1
scenario is sound-by-construction rather than test-exercised. 1 scenario is inherently
untestable at the current repo's real state. The remaining 8 are solidly covered,
several by real end-to-end process spawns rather than static text matching.

### 2. The seal — measured myself, not read from the claim

Ran this directly against the real `test_agents.py`:

```
total agents: 7
expected (checked) count: 6
['deliberation-publish', 'experimental-publish', 'experimental-validation',
 'implementation-build', 'implementation-walk', 'paper-ingestion']
```

Confirms **6 of 7** exactly as claimed, with `audit-report` (bound to `skill-audit`)
correctly excluded — `skill-audit` has no `profile.ts` and no `OBJECTIVE_FLOW` in its one
Python script (`audit_cli.py`), verified by `rg`.

**The exclusion is derived, not a hand-written escape hatch.** I mutation-tested this
directly: added `"proposal-deliberation"` (a skill that genuinely declares a north) to
`NORTHLESS_SKILLS`. The seal did not silently accept the widened exemption — it failed
loudly:
```
AssertionError: {...objective dict...} is not None : proposal-deliberation is listed in
NORTHLESS_SKILLS but declares an objective -- remove it from the map
```
So a maintainer cannot widen `NORTHLESS_SKILLS` to silence a real leak; the map is
checked against measured reality on every run (`self.assertIsNone(declared_objective(skill), ...)`
at test_agents.py:328-332). Restored and re-verified green (12/12) after the mutation.

### 3. Guards that cannot fire — C-1 mutation-tested directly

Appended `// purpose: "mutation test literal"` to `.claude/skills/_core/deliberation/engine/cli.mjs`
(cp-aside first). `C-1: no core file declares a north's text, only its structure` died
exactly as expected:
```
+ [ 'cli.mjs spells a purpose/arrival/behindWhen string literal' ]
- []
```
Restored; `git diff --stat` on the file showed empty afterward, confirming exact restoration.

**`PINNED_RESIDUE` is a measured pin, not a silent allowlist.** `PINNED_RESIDUE =
new Set(['equation', 'proposal'])` only suppresses the *derived-denylist* C-3 test for
those two words — it does NOT touch the two dedicated pin tests
(`the pinned "equation" residue is measured...`, `the pinned "proposal" residue is
measured...`), which independently re-grep every core file and assert an **exact**
`assert.equal(total, PINNED_COUNT)` plus an exact sorted file list. I proved this by
adding a fresh, unrelated "equation" occurrence to `artifact-naming.ts` (a file not in
the pinned list): the residue test died with `125 !== 124`. Restored, re-verified green.
So adding a new occurrence of a pinned word — anywhere in core, in any file — reddens the
suite; the pin can only "shrink deliberately" in the sense that a real shrink *also*
reddens the test and requires a deliberate constant update, exactly as the code comments
claim. This is not a decorative allowlist.

### 4. The false claim — corrected in both places, and true

Read both files directly:
- `proposal-deliberation/SKILL.md` lines 14-19: "`STATUS` reports it above the inventory,
  and both of the engine's CLI-level error paths carry it too — that is its complete
  reach. A typed refusal returned as a value from `tool.execute` does not carry it..."
- `.claude/agents/deliberation-publish.md` lines 39-42: "`STATUS` reports the `objective`
  block above the inventory, and both of this skill's CLI-level error paths carry it too
  — that is its complete reach. A typed refusal returned as a value from the engine does
  not..."

Neither file contains "every refusal ... carries it" anymore (`rg` confirmed absence in
both).

**Verified the correction is actually true**, not just consistent: `rg -n "objective"
.claude/skills/_core/deliberation/engine/cli.mjs` shows exactly 3 sites —
`runStatus` (line 282), and the two `--serve`/inline catch handlers (lines 387, 397).
Read `run()` (lines 339-345): a `tool.execute` result is returned directly
(`result.details ?? result`) with **no** wrapping — an `objective` field is attached
only inside a `catch` block, i.e., only when the call *threw*. A refusal returned as a
plain value (e.g. `status: 'blocked'`) from `tool.execute` therefore reaches the
success-path `process.stdout.write` unmodified, carrying no `objective`. This is exactly
what the corrected sentence claims.

**This exact claim's own regression protection is the CRITICAL-UNTESTED finding above
(scenario 2.1)** — the text is correct today, but nothing in the suite would catch it
drifting back to the false claim.

### 5. `proposal-deliberation` unchanged in behaviour

- `git diff 31a7b71..HEAD -- .claude/skills/proposal-deliberation/profile.ts` shows a
  pure **addition** of the `objective` block (no line inside the pre-existing profile
  content changed). Diffed the new `objective` text against the pre-change `OBJECTIVE_FLOW`
  literal in `git show 31a7b71:.claude/skills/_core/deliberation/engine/cli.mjs` — byte-identical
  aside from quote style (`'` vs `"`, not a content difference).
- Manually invoked the real CLI end to end (`node .claude/skills/proposal-deliberation/cli.mjs
  '{"operation":"STATUS"}'` against a fresh temp project root) and confirmed the `objective`
  field in the live JSON response matches the design's declared text exactly, including
  `entrances`.
- The new `entrances` field is declared in the TypeScript type
  (`domain-profile.ts:188`) but **never read by any engine runtime code** — `rg -n
  "entrances"` across the engine finds only that one type declaration; the field is
  consumed only by tests (the doctrine/entrance-consistency checks). So its presence
  cannot have changed `proposal-deliberation`'s runtime behavior.

### 6. Scope discipline

`git diff 31a7b71..HEAD -- .claude/skills/_core/deliberation/engine/successor-composite-engine.ts
.claude/skills/_core/deliberation/engine/patch-compiler.ts` produced **no output** (exit 0,
empty diff) — both files are confirmed byte-identical to the pre-change merge commit.
Read-only git diff only, no checkout/restore/stash used anywhere in this verification.

## Not findings (per instructions, not re-reported)

Confirmed present and out of scope as stated: 2 `smoke-runner.ts` type errors, `equation`/
`proposal` pinned residue, and the 8 items carried from the previous change.

## Issues

### CRITICAL

1. **Scenario "The doctrine states the north's actual reach" has no covering test.**
   `proposal-deliberation/SKILL.md`'s objective-flow section is correct today (verified),
   but no test reads its prose to assert the false "every refusal... carries it" claim
   has not returned. File: `tests/proposal-deliberation-objective-flow.test.mjs` (no such
   assertion exists anywhere in it or any other test file — confirmed by grep).

2. **Scenario "The deliberated stage is never delegated" has no covering test.**
   Both `deliberation-publish.md` and `experimental-publish.md` correctly state the
   `deliberated` disclaimer today (verified by reading), but no `test_agents.py`
   assertion checks for it, unlike the sibling "shared role discipline" fragments which
   ARE mechanically checked.

3. **Scenario "Domain-bound lines are adapted, not copied verbatim" has no covering
   test.** `experimental-publish.md` correctly avoids copying `deliberation-publish.md`'s
   "this pair of skills" phrase (verified by reading), but nothing asserts this — a future
   template-copy of another domain-bound line could reintroduce a false statement silently.

### WARNING

4. **Scenario "A complete profile loads unchanged" has materially weaker coverage than
   its experimental sibling.** `experimental-deliberation-domain-profile.test.mjs` spawns
   the real CLI end-to-end and asserts the live JSON `objective` field
   (`runStatus on the experimental CLI emits...`). No equivalent test exists for
   `proposal-deliberation` — coverage there is static (profile-text-vs-SKILL.md-text
   comparison plus source-level regex on `cli.mjs`), not a live CLI invocation checking
   the actual STATUS response. I manually ran the real CLI and confirmed the behavior is
   correct (see "Hardest checks" §5), so this is not a behavioral defect, but it is a
   real asymmetry in regression protection between the two domains this change was
   supposed to treat identically.

5. **The launch brief's scenario count (17) does not match the actual spec files (14).**
   Not a code defect — informational, so the discrepancy is not silently carried forward
   into future artifacts referencing this change.

### SUGGESTION

6. Scenario "A profile naming its own domain in its own file passes" has no positive-case
   test proving the exemption logic — it holds by construction (profile files are outside
   the scanned directory), so there is nothing to exempt in code, but a reader auditing
   test coverage against the spec text alone would not find where this is proven.

## Design coherence

Checked against `design.md`'s own File Changes table, Decision A/B/C, and Mutation plan.
All mutation-plan rows I sampled (M3a, M3c, M6a-equivalent, plus my own independent C-1
and residue-pin mutations) reproduce as claimed. Design's own documented deviation
(task 3.1's C-1 placement moved from the lock test into the objective-flow test, contrary
to tasks.md's literal wording) is real and correctly resolved in favor of design.md, which
is what the apply record states and what I found on disk.

## Verdict

**PASS WITH WARNINGS**, blocked from a clean PASS only by the three CRITICAL-UNTESTED
scenarios above. Every measured claim in the apply record reproduced exactly under my own
re-execution (test counts, the seal's 6/7 coverage, both mutation-fire proofs I repeated
independently, the byte-identical scope-discipline files, the byte-identical
`proposal-deliberation` behavior). The guards that matter most — C-1 absence, C-3 derived
denylist, the residue pin, and the seal's `NORTHLESS_SKILLS` escape-hatch resistance — all
fired correctly under my own independent mutation, not just the apply report's claim of
having fired once. The three CRITICAL findings are coverage gaps, not behavioral defects:
in every one of the three, I independently confirmed by reading the actual file that the
claim the scenario describes is true on disk today. The change is sound; it should not be
archived as fully verified until those three scenarios have a real test behind them,
because nothing today would catch a regression in any of the three.
