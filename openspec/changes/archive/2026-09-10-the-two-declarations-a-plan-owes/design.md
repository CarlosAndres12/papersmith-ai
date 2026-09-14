# Design: The two declarations a plan owes

**Phase**: design · **Store**: hybrid (this file is source of truth) · **Base**: `experimental-deliberation` @ `e5b0c56`

## Technical Approach

Everything lands in `preservation-experimental.ts`: one label-matcher factory, one
shared `declarations()` traversal used by both `extractAtoms` and `violations`,
seven new violation ids, one new atom kind. Zero engine changes (verified: the
`violations` import in `initial-revision-creation.ts` exists by name, and
`preservation.ts` in the core is a one-line passthrough to `DOMAIN.preservation`).
The north text and the doctrine table move together, and the test that holds them
equal is widened to the two columns this change edits. The agent that owns the
`validated` stage is updated with them, because a stretch that reports done while two
rules still block publication is worse than an unguarded one.

## D1 — The matcher

One factory, reused by both labels. It takes a **literal** label; never caller text.

```ts
/** A declared label, in the exact shape `SUCCESS_CRITERION` already uses, plus one
 *  widening: the colon may sit inside or outside the bold, and is not captured. */
const DECLARATION = (label: string) =>
    new RegExp(`^[ \\t]*(?:[-*+][ \\t]+)?\\*\\*${label}:?\\*\\*:?[ \\t]*(.+?)[ \\t]*$`, "gmu");
const DATASET = DECLARATION("Dataset");
const VALIDATION_SCHEME = DECLARATION("Validation scheme");

type Declared = { readonly value: string; readonly line: number };
function declarations(source: string, pattern: RegExp): Declared[] { /* matchAll + lineAt */ }
```

| Question | Decision | Why |
| --- | --- | --- |
| Bold required? | **Yes, bold only** | The operator ruled "the exact shape `**Success criterion:**` already uses". A bare `Dataset: x` in prose or a table cell would count, and under exactly-one cardinality an accidental second match becomes a **refusal**. Bold is a deliberate authoring act. |
| Leading list bullet? | **Allowed** (`-`, `*`, `+`) | Byte-identical to the precedent; the tutor bullets are written as list items. |
| Colon | **Either side, not captured** | `**Dataset**: CIFAR-10` and `**Dataset:** CIFAR-10` must key the same atom. The precedent (`\*\*Success criteri(?:on\|a):?\*\*`) captures a leading `": "` for the outside-colon spelling; that asymmetry is left alone here (it would change an existing atom key) and recorded as an open question. |
| Case | **Sensitive** | Case-folding makes a heading `**dataset:**` plus a bullet `**Dataset:**` a duplicate refusal. The cost — a lowercase author sees "missing" — is paid in the message, which spells the exact expected label. |
| Empty value | **Not a declaration** | `(.+?)` requires non-empty, exactly as the precedent. A label with nothing after it reports *missing*, and its detail says so verbatim. This keeps both matchers identical and keeps the id count down. |

`SUCCESS_CRITERION` stays byte-identical. Do not refactor it onto the factory in
this change.

## D2 — Cardinality: two failures, two ids

Zero and two are different facts and get different ids, in the existing
`<subject>-<predicate>` style (`report-table-fabricated-value`,
`baseline-missing-repository-url`).

| Count | Rule id | `line` | Detail shape |
| --- | --- | --- | --- |
| 0 | `dataset-declaration-missing` | `1` | ``an experiments document declares its data once, as `**Dataset:** <name and split>` on its own line; a label with nothing after it declares nothing`` |
| ≥2 | `dataset-declaration-repeated` | line of the **second** occurrence | ``declared on lines 4, 9; exactly one `**Dataset:**` line is required, and the engine must not pick one silently`` |
| 0 | `validation-scheme-declaration-missing` | `1` | names the label, a test, seeds and repetitions |
| ≥2 | `validation-scheme-declaration-repeated` | second occurrence | same shape as the dataset's |

`line: 1` for an absence: there is no offending line, `violations()` sorts by line,
and a missing declaration then sorts first, which is the right reading order. One
violation for the repeat case, not N−1 — the fact is "this document declares more
than one", and the detail carries every line.

## D3 — The `dataset` atom key

Follows the `url` precedent verbatim (`url:https://…`): **keyed by its own text**,
because the id is what a caller echoes back to authorise a loss, and a name is
legible where a digest is not. Id: `dataset:cifar-10 (train/test split as distributed)`.
`atom.text` keeps the original casing; the key is normalized in four steps, each
with a precedent in this file, each meaning-preserving:

1. **Strip verification tags** (`VERIFICATION_TAG_ANYWHERE`). Load-bearing: the
   URL rule *forces* a tag onto any dataset line citing a URL, so re-verifying
   would flip `[pending-verification]` → `[verified: 2026-09-09]` and a real
   re-check would read as a dataset **swap**. `baselineViolations` already strips
   for this same class of reason.
2. **Strip trailing sentence punctuation** (`/[.,;:!?]+$/u`, the class
   `externalUrls` already uses). Internal punctuation stays — a `/` split spec is
   meaning-carrying.
3. **Collapse whitespace** (`collapse`). A reflow is not a swap.
4. **Case-fold**. `ImageNet` and `imagenet` are never two datasets, so folding only
   merges; it can never split a real swap, and it stops a cosmetic recapitalisation
   from reading as one.

Nothing else is normalized. Dropping punctuation or tokens beyond this would let a
genuine change of split (`CIFAR-10 (train/test)` → `CIFAR-10 (train/val)`) pass as
unchanged, which is the failure that matters.

The validation scheme takes **no atom** (ruled). Assert that absence explicitly.

## D4 — The validation-scheme check, decomposed

Run only when exactly one declaration exists. Value is normalized first: lowercase,
hyphens between letters folded to spaces (`p-value` ≡ `p value`, `t-test` ≡ `t test`),
then split into clauses on `[,;]`.

### (a) The named test — *reduction*, not vocabulary

No closed list of test names, and no positive "is a test" decision is claimed. The
check is whether the value is **reducible to nothing**. Delete, by token/phrase (never
substring — `ci` lives inside `decide`, and this project has already been burned by
substring stopwords):

| Set | Contents | Bias when stale |
| --- | --- | --- |
| Placeholders | `tbd`, `to be decided`, `to be determined`, `tba`, `n/a`, `na`, `none`, `pending`, `todo`, `xxx`, `?`, `-` | toward **block** — keep short, all unambiguous |
| Non-test outputs | `p value`, `pvalue`, `significance`, `statistical significance`, `confidence interval`, `effect size` | toward **block** — deliberately minimal; **not** `alpha`, `mean`, `ci` |
| Connectives | `a an the and or with over across on in at per of for from using use used to by plus then each` | toward **accept** — an incomplete list lets a bad line pass, it never blocks a good one |
| Numerals, the matched seeds/reps clauses, punctuation | — | — |

If **no token survives** → `validation-scheme-without-test`, and it **short-circuits**
(b) and (c): a declaration that names no test cannot be judged for its seeds.

**A line containing `p-value` alongside a real test PASSES.** `Wilcoxon signed-rank
test, p-value < 0.05, over 10 seeds with 3 repetitions` leaves `wilcoxon signed rank
test` standing. Refusing it would make the rule unobeyable for the ordinary way this
is written; the denylist decides *reducibility*, never vocabulary hygiene, and never
emits a violation of its own.

### (b) Seeds — `validation-scheme-without-seeds`

One clause must contain both a `seed`/`seeds` token **and** a digit. Clause-scoped,
not value-scoped, so "fixed seeds" in one clause cannot borrow the "3 repetitions"
digit from another.

### (c) Repetitions — `validation-scheme-without-repetitions`

One clause must contain a digit and one of `repetition(s)`, `repeat(s)`, `repeated`,
`replicate(s)`, `replication(s)`, `run(s)`, `trial(s)`, `fold(s)`.

### Which part carries the false-block risk

**(b), by a distance.** It requires the literal word *seeds* and a literal digit: "over
ten seeds" and "five random initialisations" are both refused. That is faithful to the
operator's ruling (seeds were named as a requirement), and the detail message states
the exact obligation with an example. (c) is next, and its wide keyword list biases it
toward accept. (a) is the safest of the three because every list inside it either
biases toward accept or is short and unambiguous.

### What this does not buy — stated, not implied

It cannot tell a well-chosen test from a badly-chosen one. `t-test over 5 seeds, 3
repetitions` publishes on paired ordinal data where a Friedman test was owed. That is
the tutor's job — the two `SKILL.md` bullets — and no byte rule in this change
approaches it. The denylist is also incomplete by construction; a novel placeholder
carrying a digit-bearing seeds clause passes.

## D5 — The objective-flow column guard, and the cross-domain hazard

**This test does not test one skill.** `discoverPairs()` walks
`.claude/skills/*/profile.ts`, keeps every profile declaring an `objective`, and the
suite asserts `pairs.length === 2`; the per-skill tests run in a `for` loop over
`proposal-deliberation` **and** `experimental-deliberation`. So widening the comparison
reaches the mathematical domain, which this change must otherwise leave byte-for-byte
alone (D7).

The two domains disagree today in three distinct classes, all confirmed in source:

| Class | Where | Table | Profile |
| --- | --- | --- | --- |
| Case only | `bound`, `published` establishes, both skills | `Which revision is current…` | `which revision is current…` |
| Encoding | `composed` establishes, math | `— the equation, with its tag —` | `-- the equation, with its tag --` |
| **Genuine content** | `deliberated` behindWhen, **both** skills | `**the user said so** — nothing here measures it, and nothing may` | `THE USER SAID SO. Nothing here measures it, and nothing may: an agent that could close this stage on its own word would be approving its own proposal` |

**Normalization alone cannot close the third class, and this design does not pretend
it can.** Case-folding, whitespace collapse, `--`↔`—` and markdown-bold stripping all
close classes 1 and 2 and leave the profile's entire trailing clause standing. Any
equality rule reddens both skills instantly.

| Option | Cost | Verdict |
| --- | --- | --- |
| (a) Normalize harder, then require equality | Still fails `deliberated` in both skills. Nothing about the clause is cosmetic. | Rejected — it does not work, not merely expensive |
| (b) Plain containment (table cell ⊆ profile field) | Green today, but the profile may then grow a condition the table never gains — **exactly this change's drift**, since it appends to `validated.behindWhen`. A guard that cannot catch the thing it was added for. | Rejected |
| (c) Scope the new columns to `experimental-deliberation` only | Green, no math edit, and **half a guard**: it says nothing about the domain where the gap is equally open, and it is the kind of scoping this project has been burned by (a guard that cannot fire for half its subjects). | Rejected, but honestly the cheapest |
| (d) **Head-equality** (recommended) | Compare against the profile field's *head*: everything before the first `": "` not inside a backtick span. Measured green today for all 9 rows across both skills, because the only divergence is a colon-introduced rationale the table legitimately omits — the same shape in both domains. Residual gap: a future profile could still hide a condition *after* a colon. | **Recommended** |
| (e) Make the math skill's north text agree | Correct in the abstract, but it is an edit to `proposal-deliberation` — outside this change's scope and against the operator's byte-for-byte rule. | **Operator's ruling, not mine** |

(d) is recommended because it is the only option that both stays green without touching
the math domain **and** bites on the drift this change actually creates: the new
conditions appended to `validated.behindWhen` carry no colon, so the head grows and the
doctrine cell must be edited or the test goes red. It is structured containment with a
boundary derived from the text, not a chosen per-stage exemption.

**Needs the operator's ruling** (do not let apply decide it): if the operator prefers
(e) — one north, one text, equality — then `proposal-deliberation/SKILL.md`'s
`deliberated` row is edited to carry the full clause, and the byte-for-byte constraint
is amended to name that file. Until then, apply implements (d) and edits nothing under
`.claude/skills/proposal-deliberation/`.

Two parser changes, both needed regardless of which option is ruled:

**Row parsing.** Replace the backtick split with one `parseDoctrineTable(skillSource)`
used by the existing stage test *and* the two new ones: keep the existing slice between
`## The objective flow` and `**Arrival:**`, take lines starting with ``| ` ``, split on
`/(?<!\\)\|/`, drop the outer empties, require exactly 3 cells, unescape `\|`. Cell text
containing backticks then parses correctly — `` `STATUS` named the latest… `` is a cell
today, and it is the cell this parser must not choke on.

**Profile parsing.** Replace the three independent regexes in `parseObjective` with one
per-stage triple match (`stage` → `establishes` → `behindWhen`) and assert
`triples.length === stages.length`, so a stage that omits a field fails loudly instead
of silently misaligning the index-paired arrays.

**Comparison.** Normalize both sides: unescape TS string escapes, strip `` ` `` and `*`,
fold `—`/`–`/`--` to a space, lowercase, replace every remaining non-alphanumeric with a
space, collapse, trim.

| Column | Rule | Measured today |
| --- | --- | --- |
| `establishes` | **strict normalized equality** | Holds for all 5 experimental and all 4 proposal rows (differences are class 1 and 2 only). |
| `behindWhen` | **head-equality**, option (d) | Holds for every row in both skills. |

Note the asymmetry is deliberate: `establishes` supports the tighter rule today, so it
gets the tighter rule. Do not level them down for symmetry.

Proposed moved text (profile and table, same bytes modulo case):

- `validated.establishes`: *the protocol, the metric, the baseline, the dataset and the validation scheme are declared and came from a search, not a guess*
- `validated.behindWhen`: ``a URL with no dated tag, a baseline with no repository or venue year, a missing or repeated `**Dataset:**` line, or a `**Validation scheme:**` line naming no test, no seeds or no repetitions, stops this stage``

## D6 — The agent system must couple

`.claude/agents/experimental-validation.md` (`stretch: validated`) owns exactly the
stage these declarations belong to. Measured today it describes its stretch as
"protocol, accepted metrics, current baselines" — no dataset, no seeds, no
repetitions, no significance test — ends when "no external URL lacks a dated tag and
no baseline lacks a repository or venue year", and enumerates the rules that confirm
its stage closed as exactly three. Left alone it reports `validated` done while two
rules still block publication.

**Do both new rules belong to this stretch?** Yes, and the enumeration's existing
exclusion supplies the principle rather than an ad-hoc call:

> This stretch owns the rules whose satisfaction depends on **a search having
> happened**. It does not own rules about how the composer writes.

`report-table-fabricated-value` is excluded because an empty cell is a composition
property — no search closes it. Both new rules are on the other side: the validation
scheme *is* "the seeds and repetitions the area expects, and the significance test it
uses", which is the search this stretch performs; and the dataset is what
`guidance/data-paper/` bounds, which this agent has `Read`/`Glob`/`Grep` to check. The
agent has no `Write` and composes nothing, so its obligation is **verification, not
authoring**: it confirms exactly one dataset is declared and that the data paper backs
it, and if the dataset is still undecided that is an `owed` entry, not a closed stage.

Three edits, and no more:

| Part | Change |
| --- | --- |
| frontmatter `description` | add the dataset and the validation scheme to what it searches for: "…its accepted metrics, its current baselines, the dataset the plan runs on, and the seeds, repetitions and significance test the area expects…". Keep the existing ending clause verbatim. |
| "Your stretch, and its two ends" | extend the end condition: "…and no baseline missing a repository URL or a venue year, and the document declaring exactly one dataset and one validation scheme naming a test, its seeds and its repetitions." |
| the rule enumeration | three → seven ids, plus one sentence naming `report-table-fabricated-value` as **deliberately not this stretch's**, so the curation is stated instead of inferred from an absence. |

**Recommended, and it is new work: make the enumeration derive itself.** A prose list
that was right when written is exactly what drifted here. Add one assertion — collect
every `rule: "<id>"` literal in `preservation-experimental.ts` and require each to
appear in `experimental-validation.md` either in the enumeration or in an explicitly
named not-this-stretch line. A rule added later then goes red until somebody classifies
it, instead of silently orphaning the stretch again. Cost: one new test; benefit: this
exact defect cannot recur. Flag to the operator as an addition, not a hidden extra.

**`.claude/agents/experimental-publish.md`: examined, no change needed.** It is
`stretch: terminal`, enumerates no rule ids, and its description carries
`objective.arrival` verbatim — which `tests/test_agents.py::test_a_description_carries_the_arrival_its_skill_declares`
holds equal. This change edits `validated.establishes`/`behindWhen` and **not**
`arrival`, so that test stays green and the publish agent stays byte-identical. Its
generic "When something refuses" path already handles a new rule id.

`tests/test_agents.py` also asserts, for every agent, `You begin`/`you end`, the four
returned fields, "never conclusions"/"measured again", and — for delegating skills —
`Measure this before delegating` in `SKILL.md`. The edits above must keep all of them
true, which is one more reason both suites are mandatory.

## D7 — Proving the untouched parts are untouched

The operator's standing rule is byte-for-byte identity for everything not in scope.
Make apply **prove** it, not claim it:

1. **Path allowlist.** `git status --porcelain` must list only:
   `.claude/skills/experimental-deliberation/{preservation-experimental.ts,profile.ts,SKILL.md}`,
   `.claude/agents/experimental-validation.md`,
   `tests/experimental-deliberation-{preservation,publish,initial-revision}.test.mjs`,
   `tests/proposal-deliberation-objective-flow.test.mjs`, and this change's
   `openspec/` artifacts. Anything else — above all any path under
   `.claude/skills/proposal-deliberation/` or `_core/` — fails the change.
   Untracked files do not appear in `--stat`, so use `--porcelain`, which lists them.
2. **Identifier identity.** Assert the four pre-existing violation ids
   (`report-table-fabricated-value`, `url-without-verification-marker`,
   `baseline-missing-repository-url`, `baseline-missing-venue-year`) and the five
   pre-existing atom kinds (`report-table`, `baseline`, `success-criterion`, `figure`,
   `url`) are all still produced, by the existing tests that already name them — none
   of which may be deleted or renamed. A rename would otherwise pass an allowlist.
3. **Zero core diff.** `git diff --quiet -- .claude/skills/_core .claude/skills/proposal-deliberation` must exit 0.

## What breaks — producers AND products

**Products: none exist.** Verified on disk, not inherited: `experiments/` contains only
`.gitkeep`. No managed revision is invalidated, so there is no migration and no
historical record to edit.

**Producers** — the fixture breakage is the real cost, and no upstream artifact named it:

| File | Break | Resolution |
| --- | --- | --- |
| `tests/experimental-deliberation-preservation.test.mjs` | ~11 assertions deep-equal `violations(…)` to `[]` or to one rule; every one now also carries the two `*-declaration-missing` violations | `RICH` gains **both** declaration lines (so the genuine-pass assertion stays unfiltered and end-to-end) and `kinds(RICH)` gains `'dataset'`. The rule-specific fixtures keep their intent via a `otherRules()` helper that filters the seven declaration ids — used **only** by the pre-existing tests, never by the new ones. `PLAIN` is untouched and gains a dedicated assertion that it yields exactly the two missing-declaration ids. |
| `tests/experimental-deliberation-publish.test.mjs` | `SEED` (the v01 on disk) declares neither → every successor preview/accept is now refused | `SEED` gains both lines. **Not listed in the proposal's affected areas.** |
| `tests/experimental-deliberation-initial-revision.test.mjs` | `clean()` asserts `status: 'created'`; `renderFromIdea` composes v1 from the idea plus verbatim source fragments and **injects no skeleton** (read: `initial-revision-renderer.ts`), so v1 now blocks | `PROPOSAL_FRAGMENT` gains both lines as extra lines (the `written.includes(PROPOSAL_FRAGMENT)` assertion still holds). Plus the new blocked-v1 integration test mirroring the filled-cell case. |
| `tests/proposal-deliberation-objective-flow.test.mjs` | parser and profile-parser rewrite | D5 |
| `.claude/skills/experimental-deliberation/SKILL.md` | stage table, canonical-form section, two tutor bullets, the stale "gap nothing enforces" section | — |
| `.claude/skills/proposal-deliberation/SKILL.md` | **must not** break under D5 option (d) — measured green. If it reddens, stop and report; editing it needs the operator's ruling (D5(e)) and breaches the byte-for-byte rule | run it, never pre-edit |
| `.claude/agents/experimental-validation.md` | closes `validated` while two rules still block publication | D6 — three edits, plus the derived-enumeration test |
| `tests/test_agents.py` | must stay green across the agent edit (both suites) | no edit expected; if the description grows past a limit it asserts, report rather than trim the content |

**Consequence worth stating out loud:** because v1 has no template, both declarations
must already exist in the caller's idea or in a required source (`proposals/`,
`guidance/data-paper/`) before `CREATE_INITIAL_REVISION` can succeed at all. The two
tutor bullets must say this; a template placeholder is not an option, since a
`**Validation scheme:** TBD` skeleton would block every v1 forever.

## Mutation proof — one per rule, chosen so a weaker lock dies

Procedure (three prior burns close here): edit the source file, **assert the anchor was
replaced exactly once** (`git diff --stat` proves nothing for untracked files, and a
successful unrelated edit masks a failed one), re-run the named test in a **fresh**
node process, confirm RED, `git checkout` the file, confirm GREEN.

| # | Mutation | Test that must go RED |
| --- | --- | --- |
| 1 | delete the `dataset-declaration-missing` push | `a document declaring no dataset is refused` |
| 2 | `found.length > 1` → `found.length > 2` | `two dataset lines are refused, not silently reduced to the first` (a suite testing only 0 and 1 survives this) |
| 3 | drop `\\*\\*` from `DECLARATION` | ``a bare `Dataset:` line without bold does not satisfy the rule`` |
| 4 | `line: 1` → `line: 0` | `a missing declaration reports line 1 and sorts first` |
| 5 | drop the verification-tag strip from the dataset key | `the same dataset re-verified on a later date keeps its atom id` |
| 6 | key by `short(...)` instead of the text | ``the atom id is `dataset:<name>`, echoable by a caller`` |
| 7 | add a `validation-scheme` atom kind | `kinds(RICH)` exact-list test |
| 8 | residue check → non-empty check | ``**Validation scheme:** TBD over 5 seeds, 3 repetitions is refused as naming no test`` |
| 9 | make a non-test-output term push a violation | ``a scheme naming a real test *and* a p-value publishes`` |
| 10 | seeds check clause-scope → value-scope | `paired t-test with fixed seeds, 3 repetitions` → `validation-scheme-without-seeds` |
| 11 | drop `repetition` from the reps keywords | `…, 3 repetitions` no longer satisfies (c) |
| 12 | reps check accepts any second digit | `t-test over 5 seeds` → `validation-scheme-without-repetitions` |
| 13 | one word of `profile.ts` `validated.establishes` | experimental establishes-equality test |
| 14 | one word of `proposal-deliberation` `composed.behindWhen` | proposal behindWhen-head test — **proves the guard covers both skills**, which no assertion about the experimental skill alone can. Revert it; this file ships unchanged (D7) |
| 15 | delete one rule id from `experimental-validation.md`'s enumeration | the derived-enumeration test (D6) |
| 16 | add a rule id to `preservation-experimental.ts` that the agent never mentions | same test — proves it catches a *new* rule, not only a deleted mention |

Vacuity guards, not optional: the objective-flow tests assert `rows.length ===
stages.length` and count the comparisons made; `violations(RICH)` is asserted unfiltered.

## Testing Strategy

| Layer | What | How |
| --- | --- | --- |
| Unit | 7 violation ids, cardinality, matcher shape, atom key/normalization, denylist accept **and** refuse cases | in-process via jiti, `tests/experimental-deliberation-preservation.test.mjs` |
| Contract | doctrine table ≡ profile, both columns, both skills | `tests/proposal-deliberation-objective-flow.test.mjs` |
| Contract | the validation agent's rule enumeration ≡ the rules the module declares | new assertion (D6) |
| Integration | v1 refused when a source declares neither | child process, `…-initial-revision.test.mjs` |
| Identity | untouched paths and pre-existing ids unchanged | D7 — `git status --porcelain` allowlist, `git diff --quiet` on core and the math skill |
| Mutation | table above, 16 entries | manual, anchor-count asserted, fresh process |

Both suites must pass: `npm test` **and** `.venv/bin/python -m unittest discover -s tests`.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary. The change adds pure functions over
document bytes; the child processes the tests spawn are pre-existing harness.

## Migration / Rollout

None. No stored state, no managed document exists, single-commit revert restores
today's behaviour exactly.

## Open Questions

- [ ] **Operator's ruling required (D5).** Head-equality (d) is recommended and stays
      inside scope. If the operator prefers one north with one text (e), the math
      skill's `deliberated` row is edited and the byte-for-byte constraint must be
      amended to name `.claude/skills/proposal-deliberation/SKILL.md`. Apply must not
      decide this.
- [ ] **Operator's call (D6).** The self-deriving rule enumeration is an addition to
      scope — one new test that makes this class of agent drift impossible. Accept or
      decline; the three prose edits stand either way.
- [ ] Should `**Dataset:** TBD` be refused too? The denylist is ruled in for the
      validation scheme only, and the dataset's settled row is presence/cardinality.
      Not invented here. Deferred, named, not faked.
- [ ] `SUCCESS_CRITERION` captures a leading `": "` for the `**Success criterion**: x`
      spelling; the new factory does not. Widening it would change an existing atom
      key and belongs to its own change.
