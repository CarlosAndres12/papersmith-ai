# Proposal: Generalize the deliberation core for a second domain layer

## Problem Statement

`.claude/skills/_core/deliberation/engine/` is presented as shared, but a second
domain layer cannot sit on it. Three families of coupling block it, all measured
in `exploration.md` (§3, L1–L7):

1. **Namespace.** `research-concept-…` is hardcoded at 14 sites, and at three of
   them it is a TypeScript **literal type** (`revision-domain.ts`,
   `revision-receipt.ts`, `proposal-workspace-adapter.ts`). A second domain
   cannot type-check against it. `proposals/` (12 sites) and
   `.proposal-deliberation/{state,receipts,withdrawn}/` (8 sites) are the same
   problem one level up.
2. **Validation vocabulary.** `candidate-validator.ts` makes LaTeX spelling and
   `\label`/`\tag`/`\eqref` resolution unconditional terms of `ok`. On a
   math-free document these pass **vacuously** — a clean verdict from a validator
   that checked nothing.
3. **Structure.** `EntryType` has no `table` and no `figure_placeholder`, so a
   Markdown table cannot be a locus at all.

The existing lock, `tests/proposal-deliberation-domain-profile-lock.test.mjs`,
is 6/6 green and did not catch any of this: it scans only for the four values
`profile.ts` declares plus `names`. That blind spot is the reason the leaks
survived extraction.

## Scope

### In Scope

The ten core changes of `exploration.md` §5, in the approved order
**1 → 2 → 3 → 6 → 4 → 5 → 7 → 8 → 9 → 10**:

| # | Change | Risk |
| --- | --- | --- |
| 1 | `DeliberationDomainProfile` gains an `artifact` block `{ directory, stem, revisionPattern, revisionLabel, sidecarRoot, marker }`; each added to `REQUIRED` | low |
| 2 | New `artifact-naming.ts`; 14 hardcoded sites and 3 literal types become profile-derived builders | **high** |
| 3 | `proposals/` and `.proposal-deliberation/` routed through the same block | medium |
| 6 | `table` + `figure_placeholder` in `EntryType`; GFM tables in `buildStructuralIndex`; both as `target-resolver.ts` leaves (additive) | medium |
| 4 | `math-integrity.ts` → `preservation.ts`; extractor and rules behind `profile.preservation.{extractAtoms, violations}`; math ships as `proposal-deliberation/preservation-math.ts`; `mathDelta`→`preservationDelta` and `acknowledgedMathRemovals`→`acknowledgedRemovals` **with the old names kept as accepted aliases** | medium |
| 5 | `profile.references.{declares, cites}` replaces the hardwired reference checks | medium |
| 7 | `profile.sources: readonly { path, required }[]`; a missing required source raises `REQUIRED_SOURCE_MISSING` instead of the current silent `return []` | medium |
| 8 | Change-header contract: `CREATE_SUCCESSOR` gains required `changeSummary: { what, why }` — **see Open Design Question** | medium |
| 9 | `profile.sourceAuthority` names ceiling sources; contradicting evidence is refused `SOURCE_AUTHORITY_CONFLICT`. Off by default | medium |
| 10 | Delete the `'sparse'`/`'dispers'` literal from `intent-resolver.ts` | low |

Plus, **inside the same work unit as change 2**, extending the domain lock to
scan core for the newly declared artifact values.

### Out of Scope

- **The experimental-deliberation skill itself.** This change prepares core only.
- Any change to `proposal-deliberation`'s SKILL.md, doctrine, or published bytes.
- Unifying the two domains' notion of *verify* (`exploration.md` §D1: they share
  the writing scaffold and nothing about sufficiency).
- Any stage or pipeline machine in core. §4 measured that the engine governs no
  stage sequence — it exposes unordered operations, ordering is SKILL.md prose.
  This was a false premise in the original brief and must not resurface.

## Capabilities

### New Capabilities

- `deliberation-artifact-namespace`: profile-declared artifact stem, revision
  spelling, directory, sidecar root and marker; no literal names in core.
- `deliberation-structural-entries`: `table` and `figure_placeholder` as
  first-class leaf entry types.
- `deliberation-preservation-gate`: domain-neutral atoms/delta/violations
  machinery over a profile-supplied extractor and rule set, with wire-field
  aliases.
- `deliberation-reference-integrity`: profile-declared `declares`/`cites`.
- `deliberation-required-sources`: declared source set with
  `REQUIRED_SOURCE_MISSING`.
- `deliberation-change-header`: the `changeSummary` contract (open question).
- `deliberation-source-authority`: `SOURCE_AUTHORITY_CONFLICT`.

### Modified Capabilities

None. `openspec/specs/` holds no published spec for the deliberation core.

## Approach

Every generalization is the same move: the structure stays in core, the domain
value moves into `profile.ts`, and `proposal-deliberation`'s profile declares
**exactly today's values**, so its behaviour is preserved by construction rather
than by care. Change 4 additionally keeps the old wire-field names as accepted
aliases so the mathematical SKILL.md needs no edit. Changes 7 and 9 are declared
opt-in: `proposal-deliberation` declares `guidance/paper-guide` as *not*
required and declares no `sourceAuthority`, preserving today's silence.

## Affected Areas

| Area | Impact | Description |
| --- | --- | --- |
| `_core/deliberation/engine/domain-profile.ts` | Modified | `artifact`, `preservation`, `references`, `sources`, `sourceAuthority` blocks + `REQUIRED` |
| `_core/deliberation/engine/artifact-naming.ts` | New | Profile-derived name/path builders |
| `_core/deliberation/engine/preservation.ts` | New (from `math-integrity.ts`) | Neutral atoms/delta/violations |
| `_core/deliberation/engine/{candidate-validator,reference-index,document-index,types,target-resolver,intent-resolver,orchestrator,patch-compiler,revision-receipt}.ts` | Modified | Vocabulary, entry types, gates |
| `_core/deliberation/engine/{revision-domain,proposal-workspace-adapter,proposal-workspace,consistency-audit,document-state,initial-revision-*,revision-lifecycle-store}.ts` | Modified | Namespace de-literalization |
| `.claude/skills/proposal-deliberation/profile.ts` | Modified | Declares today's values |
| `.claude/skills/proposal-deliberation/preservation-math.ts` | New | The math extractor and rule set |
| `tests/proposal-deliberation-domain-profile-lock.test.mjs` | Modified | Scans the new declared values |

## Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Change 2 regresses `proposal-deliberation` naming silently | High | Extend the lock in the same work unit; mutation-prove it goes red |
| A new guard passes vacuously on an empty fixture | High | Every guard needs a fixture where it genuinely has something to find |
| A guard is written but never wired | Medium | Break each guard on purpose, observe red, assert the anchor count |
| Change 8 collides with `COMPOSITE_UNTOUCHED_INVARIANT` | High | Unresolved — see below; design phase decides with evidence |
| Only one of the two suites is run | Medium | Both are mandatory in every acceptance check |

## Open Design Question — change 8

`patch-compiler.ts` and `successor-composite-engine.ts` enforce
`COMPOSITE_UNTOUCHED_INVARIANT`: every byte outside the resolved loci must be
identical between source and candidate. A change header written into the
document body **is exactly such a byte**, so the engine would refuse it. Three
candidate resolutions, none obviously right:

- **(a)** the header lives in the receipt/sidecar and never in the `.md`;
- **(b)** the header is its own resolved locus the successor replaces like any
  other;
- **(c)** the invariant gains a narrow declared exemption for a document prefix.

This is **unresolved**. The design phase must choose with evidence. Do **not**
weaken the invariant by default.

## Acceptance Criteria

- [ ] **`proposal-deliberation` behaviour is byte-identical.** Its `profile.ts`
      declares exactly today's values; every default is preserved.
- [ ] **`npm test` → 386 pass / 0 fail** (~32 s). Note: this command sets
      `DELIBERATION_DOMAIN_PROFILE` to the mathematical profile, so the whole
      node suite runs under one domain today.
- [ ] **`.venv/bin/python -m unittest discover -s tests` → Ran 2718, OK
      (skipped=6)** (~488 s). Use `.venv/bin/python`, never bare `python3`
      (3.9, incompatible).
- [ ] **Both suites are run.** Running only one has hidden a regression before.
- [ ] **The domain lock is extended in the same work unit as change 2** and
      scans core for the newly declared artifact values.
- [ ] **Mutation proof for changes 2 and 4**: each new or extended guard is
      broken on purpose, observed to go red, and the mutation is proven to have
      landed by asserting the anchor count (`git diff --stat` does not prove it
      for untracked files).
- [ ] **No vacuous passes.** Every new guard has a fixture where it genuinely
      has something to find; a pass on an empty fixture counts as a failure.
- [ ] Change 8 ships only after its invariant collision is resolved in design.

## Review Workload Forecast

Forecast against the session budget of **1400 changed lines**
(`additions + deletions`, authored):

| Slice | Changes | Estimate |
| --- | --- | --- |
| 1 — artifact namespace | 1, 2, 3 + extended lock | ~650 |
| 2 — structure + preservation | 6, 4 | ~670 |
| 3 — references + sources | 5, 7 | ~430 |
| 4 — new mechanics + cleanup | 8, 9, 10 | ~460 |

**Total forecast: ~2200 lines — the budget is exceeded.**

- Decision needed before apply: **Yes**
- Chained PRs recommended: **Yes**
- 1400-line budget risk: **High**

Each slice above has a clear start and finish, autonomous scope, both suites as
verification, and an independent revert.

## Rollback Plan

Per slice, on its own branch. Every slice is additive to the profile contract
plus a mechanical substitution in core, so reverting the slice's commits
restores the previous engine exactly; `proposal-deliberation`'s `profile.ts` is
the only file carrying the previously-hardcoded values, and it is reverted with
the same commit. Recovery is confirmed by re-running both suites to the
baselines above. No data migration and no on-disk artifact format change is
introduced by slices 1–3; slice 4 is gated on the design decision.

## Dependencies

- `.venv/bin/python` (3.12) present at the repository root.
- The change-8 design decision must land before slice 4 begins.

## Citation Check

Every symbol cited above was located in the source by name, not by line:
`COMPOSITE_UNTOUCHED_INVARIANT` (`successor-composite-engine.ts`,
`patch-compiler.ts`), the `'research-concept-r01.md'` literal types
(`revision-domain.ts`, `revision-receipt.ts`, `proposal-workspace-adapter.ts`),
`loadGuideDirectoryFragments` (`proposal-workspace.ts`), `REQUIRED` and
`DeliberationDomainProfile` (`domain-profile.ts`), and the 6-test lock. The line
numbers carried by `exploration.md` were **not** reused: `loadGuideDirectoryFragments`
has already moved from the cited position. `REQUIRED_SOURCE_MISSING` and
`SOURCE_AUTHORITY_CONFLICT` do not exist in core — correct, they are new.
