# Proposal: The two declarations a plan owes

**Phase**: propose · **Store**: hybrid (this file is source of truth) · **Base**: `experimental-deliberation` @ `e5b0c56`

## Intent

An `experimental-deliberation` document may today be published naming neither the
data it runs on nor the statistical test that will decide its result. `SKILL.md`
asks for both in prose; nothing in `preservation-experimental.ts` decides either
from bytes. A plan a reviewer cannot check on those two points is not a plan.
Make both hard-blocking canonical-form rules, at the same severity as the four
that already exist.

## Scope

### In Scope

- Two `violations()` rules in `preservation-experimental.ts`: `**Dataset:** …`
  and `**Validation scheme:** …`, each once per document, each on its own line.
- The validation-scheme rule additionally requires seeds and repetitions, and
  rejects a denylist (`tbd`, `n/a`, `pending`, and non-test outputs such as
  `p-value`). No closed vocabulary of test names.
- Two tutor bullets in `SKILL.md`, in the existing bullets' voice: start from the
  dataset; always propose the validation scheme.
- The north: `profile.ts` `objective.stages[validated]` and `SKILL.md`'s stage
  table, moved together.
- Correct `SKILL.md`'s stale section "Creating v1, and the gap nothing enforces":
  `initial-revision-creation.ts` line 12 does import `violations`.

### Out of Scope

- `guidance/data-paper/.gitkeep` and which directories reach a clone.
- Routing rules for which document owns an implementation finding.
- The `experimental-implementation` skill.

## Capabilities

### New Capabilities
- `experimental-plan-declarations`: an experiments document declares its dataset
  and its statistical validation scheme, or it is refused.

### Modified Capabilities
- `deliberation-objective-flow`: the `validated` stage's condition text must name
  every byte-decidable condition of that stage, including the two new ones.

## Approach

`violations()` only — no new `extractAtoms` kinds. A hard block is strictly
stronger than atom-delta acknowledgment (an acknowledged atom loss still
publishes; a violation never does), so an atom would be redundant and
inconsistent with the chosen severity.

Reach is free: `initial-revision-creation.ts` already runs the profile's
`violations()` against composed v1 before any write, and `candidate-validator.ts`
runs the same export on the successor path. **Zero engine changes.**

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/experimental-deliberation/preservation-experimental.ts` | Modified | Two rules added to `violations()` |
| `.claude/skills/experimental-deliberation/profile.ts` | Modified | `objective.stages[validated]` text |
| `.claude/skills/experimental-deliberation/SKILL.md` | Modified | Stage table, two tutor bullets, canonical-form section, stale v1 section |
| `tests/experimental-deliberation-preservation.test.mjs` | Modified | Unit tests per rule, red first |
| `tests/experimental-deliberation-initial-revision.test.mjs` | Modified | One v1 integration test, mirroring the filled-cell case |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A denylist is incomplete by construction; a novel placeholder passes | High | Seeds + repetitions on the same line make a placeholder much harder; the gap is named, not faked |
| Every existing experiments document without both labels is blocked on its next successor | Med | No managed `experiments/*.md` exists in this repo today; document the labels in `SKILL.md` |
| A presence rule can pass vacuously | Med | Mutation proof per rule: delete the rule, the test must go red |
| The `validated` north text and `SKILL.md`'s table columns are **not** tied by any test (verified: the equality test compares stage names and arrival only) | Med | Move both in one commit; see open question 3 |

## Rollback Plan

Single revert of one conventional commit. Additive rules, no engine change, no
stored state, no migration. Reverting restores today's behavior exactly.

## Dependencies

None. Both suites must run: `npm test` and `.venv/bin/python -m unittest
discover -s tests`.

## Success Criteria

- [ ] A document missing either declaration is refused at `CREATE_INITIAL_REVISION`
      and at successor accept, with a rule name and line.
- [ ] A validation scheme naming a test but no seeds, or reducible to a denylist
      term, is refused.
- [ ] A legitimate test name never encountered before is accepted.
- [ ] Each new rule is proven able to fail (mutation), not merely green.
- [ ] `SKILL.md` no longer claims v1 content is unvalidated.
- [ ] Both suites pass.

---

## Decisions taken after the proposal question round (operator, in session)

The five questions this proposal recorded are answered. Four were ruled by the
operator; the fifth was resolved against existing rules and needed no ruling.

| # | Question | Ruling |
| --- | --- | --- |
| 1 | Two `**Dataset:**` lines — refuse, or accept the first? | **Refuse.** "Once per document" means exactly one: not zero, not two. Two lines are an ambiguity about which dataset the plan uses, and the engine must not pick one silently |
| 2 | Must the labels sit in a named section? | **No — anywhere in the bytes.** Matches all four existing rules, which are document-wide byte checks. A named section would need section-boundary machinery and could block a correct declaration for being in the wrong place |
| 3 | Add the missing north/table equality guard here? | **Yes, in this change.** Extend `tests/proposal-deliberation-objective-flow.test.mjs` to compare the `establishes` and `behindWhen` columns, not only stage names and arrival text. This change edits exactly those cells, so this is the moment the gap costs something |
| 4 | Hard block only, or also atoms? | **Both, for the dataset.** Reasoning corrected mid-session: a presence rule guarantees a dataset line EXISTS in every published version, but not that it is the SAME one. Atoms are keyed by text, so a `dataset` atom makes a silent swap between versions surface as a loss that must be acknowledged to publish. This matters here more than anywhere: the skill's own text says a different dataset invalidates everything the `validated` stage searched. **The validation scheme takes the hard block only** — no atom |
| 5 | Does the verification-tag convention touch a dataset line? | **No new rule needed.** `url-without-verification-marker` is already document-wide: any external URL, in a dataset line or anywhere else, already requires its `[pending-verification]` or `[verified: YYYY-MM-DD]` tag. Adding a second rule for the same bytes would duplicate an existing one |

### Consolidated rule set this change ships

| Rule | Kind | Cardinality |
| --- | --- | --- |
| `**Dataset:** …` present | hard-block violation | exactly one per document |
| `dataset` atom | preservation atom, keyed by text | presence-based |
| `**Validation scheme:** …` present, naming a test plus seeds plus repetitions, not reducible to a placeholder or a non-test output | hard-block violation | exactly one per document |

### Correction of record

An earlier framing in this change's own artifacts stated that `profile.ts`
`objective.stages` and SKILL.md's stage table are held equal by a test, full
stop. Measured, the test compares stage names, their order, and the
`**Arrival:**` text — never `establishes` or `behindWhen`. `exploration.md` has
been corrected. Item 3 above closes the gap.

---

## Second decision round (operator, after design)

| # | Question | Ruling |
| --- | --- | --- |
| 6 | `**Dataset:** TBD` passes today while the validation scheme rejects placeholders. Same defence? | **Yes.** The dataset takes the identical denylist (`tbd`, `n/a`, `pending`, …). Without it the rule guarantees a line EXISTS, not that it SAYS anything — the faked gap both rules exist to close |
| 7 | The seeds check demands the literal word `seeds` plus a digit | **Accept synonyms** — `seeds`, `semillas`, `initialisations`, `initializations`, `runs`, `trials`, `folds` — each with its **digit**. CORRECTION (ruling 10, after verify): this ruling's original illustrative example, "five random initialisations", contradicted its own operative clause and is WRONG. A spelled-out number does NOT satisfy the rule and the operator has confirmed it should not: `10 random initialisations` passes, `ten random initialisations` refuses. A spelled-number vocabulary would go stale in exactly the way the closed test-name vocabulary was rejected for. The synonym half of the ruling shipped as intended; only the example was faulty |
| 8 | If the extended objective-flow guard reddens `proposal-deliberation` at apply time | **STOP and ask the operator.** Never pre-edit the mathematical skill, never scope the guard down to hide it. The design believes its head-equality comparison tolerates the measured differences, but it verified that by reading files, not by executing |

## The byte-for-byte rule, as the mathematical deliberator already defines it

The operator's standing constraint is not new doctrine. `proposal-deliberation/SKILL.md:301` already states it:

> Untouched content is byte-identical across a successor version — this is a
> guarantee the engine enforces **structurally, not a courtesy**.

and `:231`:

> Byte coverage guards what lies outside the locus; inside it, this is the guard.

**Applied to this change.** The locus is the declared scope. Everything outside it is byte-identical, and that must be PROVEN by a check that runs, never asserted by the agent that made the edits.

Concretely, apply must satisfy all four:

1. `git diff --name-only` equals the scope's path allowlist **exactly** — no extra path, no missing one.
2. `.claude/skills/_core/**` is untouched. This change needs zero engine changes; that was measured, and a diff there means something went wrong.
3. `.claude/skills/proposal-deliberation/**` is untouched, subject to ruling 8 above.
4. Inside the files that do change, the four pre-existing `violations()` rule ids and the five pre-existing `extractAtoms` kinds are unchanged — asserted by a test, not read by eye.

### Measured baseline, before any edit

`npm test` on `e5b0c56`: **559 pass, 0 fail, 0 skipped**, 39.2 s.

That is the number the change is measured against. The Python suite
(`.venv/bin/python -m unittest discover -s tests`, 3.12) must also be run at
apply: running only one suite has hidden a regression in this repo before.

## Ruling 9 (operator, after tasks)

**The D6 self-deriving enumeration test is IN SCOPE.** Task 3.7, previously
deferred by the tasks phase for lack of a ruling, is now mandatory.

Without it this change fixes the instance and leaves the class open: the next
rule added to `preservation-experimental.ts` desynchronizes
`.claude/agents/experimental-validation.md` in silence — the exact defect this
change found. Mutations 15 and 16 prove both directions.

Constraint: the agent's enumeration is **curated, not exhaustive**. It omits
`report-table-fabricated-value` on purpose, because that rule is not the
`validated` stretch's concern. The test encodes the curation principle D6
derives; a naive "mentions every rule" check would go red on an existing,
correct omission.

**Review Workload Forecast corrected.** The tasks phase graded ~550-650
estimated lines against a 400-line budget and recommended `size:exception`.
This session's budget is **1400** lines, so the estimate sits at 40-46% of it.
No exception, no chaining, `single-pr` stands, and `Decision needed before
apply` is **No**.
