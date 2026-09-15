# Exploration: the-two-declarations-a-plan-owes

**Phase**: explore · **Status**: done · **Next**: sdd-propose
**Branch**: `experimental-implementation` @ `e5b0c56`
**Artifact store**: hybrid (this file is source of truth; Engram topic `sdd/the-two-declarations-a-plan-owes/explore`)

## Why this change exists

`.claude/skills/experimental-deliberation` plans experiments. Two things the
operator requires to ALWAYS hold are doctrine only -- written in prose, enforced
by nothing:

1. **The dataset**, declared once per document.
2. **The statistical validation scheme** -- a named test (t-test, chi-squared,
   Friedman, ...) together with seeds and repetitions.

`SKILL.md` already requires each experiment to state "The data and splits", and
already searches for "seeds and repetitions the area expects, and the
significance test it uses" (line 123, the `validated` stage). Both are lost on
the way into the document. A published plan can name neither its data nor its
test.

## Operator decisions taken before exploration (given, not re-opened)

| Decision | Value |
| --- | --- |
| Severity | Hard block -- no acknowledgment clears it, like the four existing canonical-form rules |
| Scope | Enforced from v1 onward, not only from v2 |
| Dataset cardinality | Once per document |
| Validation scheme content | Named test + seeds + repetitions |
| Also in scope | Two tutor bullets; the north (`objective` in profile.ts) moving with SKILL.md |

Out of scope: `guidance/data-paper/.gitkeep` and clone-travel of source
directories; any routing rule for which document owns an implementation
finding; creating the `experimental-implementation` skill.

## Main finding: the premise behind "from v1" was false, in our favour

The exploration was asked to determine whether `CREATE_INITIAL_REVISION`
validates v1 content at all, because the operator's "from v1" decision depended
on it.

**It does, today.** Verified directly against the engine, not inferred:

- `_core/deliberation/engine/initial-revision-creation.ts:12`
  `import { violations as canonicalFormViolations } from './preservation.js';`
- same file, line 83-84: `const violations = canonicalFormViolations(composed.markdown);`
  then `if (violations.length) return { status: 'blocked', code: 'INITIAL_REVISION_CANONICAL_FORM_VIOLATION', violations };`
  -- checked **before any write**, so nothing is published on violation.
- `_core/deliberation/engine/preservation.ts:51-52` is a one-line passthrough:
  `return DOMAIN.preservation.violations(source);` -- the profile's own function.
- `candidate-validator.ts` (the `CREATE_SUCCESSOR` path) imports violations from
  that same `./preservation.js`.

Proven by an existing passing test:
`tests/experimental-deliberation-initial-revision.test.mjs` --
*"a source fragment carrying a filled report-table cell refuses the first
revision instead of publishing it"* -- drives a real `CREATE_INITIAL_REVISION`
and asserts `status: 'blocked'`, the `INITIAL_REVISION_CANONICAL_FORM_VIOLATION`
code, and nothing written.

**Consequence.** Both new rules added to `preservation-experimental.ts`'s
`violations()` export reach v1 AND every successor through the mechanism the
four existing rules already use. **Zero engine changes.**

## Second finding: SKILL.md carries a false claim that must be corrected here

`SKILL.md` section *"Creating v1, and the gap nothing enforces"* (~line 240-248)
states:

> **Nothing validates that content.** `initial-revision-creation.ts` runs no
> content validation at all -- it contains no reference to `validateCandidate`,
> to `violations`, or to preservation.

Line 12 of that file imports `violations`. The section's title, its claim, and
the hand-obeyed rule it derives ("which you must obey and which nothing
enforces") are all stale. The test file's own header frames this as a past,
fixed defect; SKILL.md was never updated. Correcting it belongs to this change:
a reader who trusts it will hand-guard something the engine already guards, and
will believe v1 is unguarded when adding a rule that depends on v1 being
guarded.

## Recommended shape

Add both as `violations()` rules **only** -- not as new `extractAtoms` kinds.

Rationale: atom-delta acknowledgment is a *weaker* guarantee than an outright
block (a lost atom can be acknowledged and published; a violation cannot). A
hard-block presence rule already makes disappearance impossible in any published
version, so an atom would be redundant and inconsistent with the chosen
severity.

## Affected areas

| Path | Change |
| --- | --- |
| `.claude/skills/experimental-deliberation/preservation-experimental.ts` | two new `violations()` rules |
| `.claude/skills/experimental-deliberation/profile.ts` | `objective.stages[validated]` text |
| `.claude/skills/experimental-deliberation/SKILL.md` | stage table, two tutor bullets, canonical-form section, the stale v1 section |
| `tests/experimental-deliberation-preservation.test.mjs` | new unit tests |
| `tests/experimental-deliberation-initial-revision.test.mjs` | one integration test mirroring the existing filled-cell pattern |

`profile.ts` `objective.stages` and SKILL.md's stage table are only PARTIALLY
held equal. `tests/proposal-deliberation-objective-flow.test.mjs:132-133` takes
the first backticked token of each table row and compares stage NAMES and ORDER
against `objective.stages`; line 141 compares the `**Arrival:**` text. Nothing
compares the `establishes` or `behindWhen` columns -- precisely the cells this
change edits. The two files must still move together, but by doctrine, not
because the suite catches drift. Closing that gap is now in scope (see
decisions below).

## Checkability of the validation-scheme rule

The three parts are not equally decidable, and the rule should treat them
separately rather than as one check.

- **Seeds and repetitions** are numeric. Decidable in bytes with little ambiguity.
- **The named test** is the part that can block legitimate work.

| Option | Mechanism | Cost |
| --- | --- | --- |
| (a) Closed vocabulary | Regex alternation of known test names | Goes stale; refuses legitimate new tests |
| (b) Presence + non-empty | Any non-empty text after the label | Accepts `p-value`, accepts `TBD` -- the faked-gap failure this project warns against |
| (c) Presence + denylist | Non-empty, not reducible to placeholders (`tbd`, `n/a`, `pending`) or known non-test outputs (`p-value`, `significance`) | Incomplete, but needs no upkeep for new legitimate tests and forecloses both named failure modes |

Recommended: **(c)**. The four existing rules are all structure/presence checks
over document bytes; none uses a closed content vocabulary. Requiring seeds and
repetitions on the same declaration further shrinks the gap, because a line that
must also carry two numbers is much harder to satisfy with a placeholder.

Not settled -- the operator rules on it.

## Open decisions for the operator

1. **Exact label wording** for both declarations.
2. **Validation-scheme cardinality.** Dataset is once per document by decision;
   the validation scheme's cardinality was never specified.
3. **Denylist contents**, if option (c) is chosen.

## Risks

- The stale SKILL.md section, left standing, keeps teaching a false fact about
  the very mechanism this change relies on.
- The `profile.ts` / SKILL.md equality test covers stage names and arrival text
  ONLY, never the columns this change edits. Extending it is in scope.
- Three open decisions must be posed, not assumed.

## Decisions taken after exploration (operator, in session)

| Open decision | Ruling |
| --- | --- |
| Label wording | `**Dataset:** …` and `**Validation scheme:** …`, each on its own line -- the exact shape `**Success criterion:**` already uses |
| Validation-scheme cardinality | Once per document, mirroring the dataset. One line may name more than one test |
| Placeholder defence | Option (c): presence + seeds + repetitions + a denylist rejecting `tbd`/`n/a`/`pending` and non-test outputs such as `p-value` |
