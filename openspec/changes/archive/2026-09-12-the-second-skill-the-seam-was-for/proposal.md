# Proposal: The second skill the seam was for

> **This supersedes an earlier version of this file.** The earlier version was
> built on a premise that has since been **fixed in code**, not merely
> re-judged. It held that "Cut 3's pair cannot bind these two real documents" —
> `revision_source` resolved one filename against every declared document's
> root, and the two publishers can never share a filename. The archived change
> `2026-09-11-each-document-names-its-own-revision` closed that: each document
> now discovers its own name in its own root, and an unreadable one refuses.
> The earlier version's **slice A (600–900 lines) is therefore already
> delivered**, and its ~4,000–5,700 estimate and three-change recommendation
> derived from a burden that no longer exists. Both are re-derived below.
> Two of its other measured claims also went stale: `unreached_mathematics` is
> gone from the live spec (only an `impl_profile.py` comment still names it),
> and its "~1,112 authored lines" anchor for the second deliberation skill was
> wrong by 2.8×.

## Intent

Build `experimental-implementation`: the second skill the profile seam was cut
for. Its own north, verification against **both** the latest mathematical
proposal and the latest experiments document, an experiments successor when the
code contradicts it, and a test submission through Flow B's existing paths.

## Measured at `b3ca9aa` — every symbol grepped this session

| Claim inherited | Measured | Consequence |
|---|---|---|
| The document pair cannot bind | **Fixed.** `discover_document_revision(index)`, `document_revision_names(revision)`, `_DOCUMENT_NAME_CACHE`; `revision_source(revision, index)` is a dumb reader; `DOCUMENT_REVISION_UNREADABLE` refuses. `_document_extra_sources` wired at **9** `position_state` call sites | The old slice A is done. Drop it. |
| `unreached_mathematics` sits in a live spec | **No longer.** `openspec/specs/implementation-engine-neutrality/spec.md` spells `unreached_modules` twice. One stale mention survives, in `impl_profile.py`'s `provenance` comment | One comment line, not a spec correction. |
| Engine subject-word collision | **Stands.** Occurrences in `implementation_engine.py`, case-insensitive, word-boundary: `benchmark(s)` **89**, `experiment(s)` **30**, `baseline(s)` **28** (the brief's 88/23/20 were lines, or an older count) | `vocabulary.names` gets the namespace word only. |
| `KitAgreementLockTests._profile()` hardcodes `proposal-implementation` | **Stands**, while `discover_profiles()` globs `.claude/skills/*/impl_profile.py` | A second kit is unheld. |
| M5 deferred for want of a second profile | **Stands.** No stub exists, deliberately — a `skipTest` would move `skipped=6` | Landable here. |

### The finding that now drives the shape

**The claim vocabulary is a module-level scalar, one layer above the revision
scalar that was just fixed.** `CLAIM_KEY`, `LOCUS_KEY`, `REMEDY_LOCUS_KEY`,
`NOTATION_KEYS` and `CITATION_RE` are read once from `PROFILE[...]`, not from
`documents[N]`. `documents[N]` validates exactly two leaves — `directory` and
`label`. So document 1 can name its own root, its own label and its own
revision, and still cannot say that **its** claims are experiments rather than
equations.

The consequence is already visible: `_extra_document_fidelity_status` folds
four conditions its own docstring calls *document-count-invariant* —
`stale`, `missing_provenance`, `untested`, `unreached`, all about the shared
source tree — plus one per-document fact, whether the revision resolves. So a
second document reports `drift` when **document 0** drifted. Declare the
experiments document today and item 2 is a check that reads green having
measured nothing: the exact failure class six cycles have been paying off.
`with_data` is the same shape at both producers (`build_plan`, `cmd_verify`):
derived from the directory's own existence, so `missingDirs` can never hold a
`Data/`.

## Scope

### In Scope
- `experimental-implementation`: `impl_profile.py` with its own `OBJECTIVE_FLOW`
  and no `profile.ts` (`declared_objective` raises on both), launcher, `SKILL.md`,
  two ~75-line agents, its own sealed corpus.
- Per-document claim vocabulary, and a per-document fidelity fold that reads
  document N's **own** content.
- `Data/` demandable **per product folder**.
- The two mechanical cross-document refusals + per-discrepancy acknowledgment,
  mirroring `acknowledgedRemovals` (`_core/deliberation/engine/orchestrator.ts`).
- The experiments-successor composer, block locator **beside the profile**
  (ruling A). Note `TAG_RE` is read by `remedy_compatibility` and `cmd_admit`
  too, not only `cmd_compose` — the locator's reach is wider than M1 recorded.
- Flow B's existing paths through to a test submission.
- **M5**, and `KitAgreementLockTests._profile()` globbing like `discover_profiles()`.

### Out of Scope
- Any rename of `proposalDigest` or its ten campaign-proposal relatives; **M2**; F6.
- Judging whether an experiment's metric or protocol *corresponds* to a claim —
  tutor bullet in `SKILL.md`, never a check.
- Any engine-generated resolution proposal, and any inference of repair
  direction: that stays the gate Flow B step 5 already asks.

## Capabilities

### New Capabilities
- `experimental-implementation-skill`: north, agents, profile leaves, launcher, seal corpus.
- `implementation-cross-document-agreement`: two refusals, per-discrepancy
  acknowledgment, the explicit non-verdict boundary.
- `implementation-product-data`: `Data/` demandable per product folder.

### Modified Capabilities
- `implementation-document-binding`: claim vocabulary per document; a fidelity
  status that reads its own document.
- `implementation-engine-neutrality`: the `names` collision ruling; M5.
- `implementation-cli-seal`: the second skill's corpus; non-interference extended.

## Approach

Mirror the seam, do not fork it. One command roster, one refusal vocabulary,
one place the flow is described. Every new pair is gated on
`len(DOCUMENTS) == 1` behaving byte-identically — the bar all 28 digests hold.
The engine refuses and names; judgment stays with the operator.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `_core/implementation/engine/implementation_engine.py` | Modified | Per-document claim vocabulary, real per-document fidelity, `Data/` demandability, the two refusals |
| `_core/implementation/impl_domain_profile.py` | Modified | New per-`documents[N]` required leaves and their validation tier |
| `.claude/skills/experimental-implementation/` | New | Profile, launcher, `SKILL.md`, block locator |
| `.claude/agents/implementation-*` (two new) | New | ~75 lines each, no logic |
| `tests/test_implementation_domain_lock.py` | Modified | `_profile()` globs; M5 lands as a real test |
| `tests/seal/` | Added beside | Existing 28 untouched; `git diff --exit-code tests/seal/` exits 0 |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Second document's fidelity reads green having measured nothing | **High** | Slice C is the whole answer; no `documents[1]` entry ships before it |
| A `names` word reddens the engine on 147 occurrences | **High** | Namespace word only; it need only appear in the profile's own source text, which `test_every_declared_name_really_is_that_domain_speaking` checks |
| `L1_EXPECTED_COUNT = 96` / `L1_EXPECTED_FILES` pin breaks | Med | Any new engine file spelling `proposal` reddens it |
| Engine edits move a sibling digest | Med | All 28 byte-identical; `skipped=6` unmoved |
| A branch no configuration reaches | Med | Name the reaching case per branch before writing the assertion |
| A method halts before its second mechanism | Med | `subTest` or separate methods, per `b3ca9aa` |
| No corpus exists to author fixtures from | **High** | `proposals/` and `experiments/` hold only `.gitkeep` |

## Size — and how many changes

Two anchors, measured here, both worse than the old proposal's:

- The second **deliberation** skill cost **1,536 skill lines + 1,593 test lines
  = 3,129**, with zero engine changes. The old proposal's "~1,112" was wrong.
- A second skill's `SKILL.md` is **not** thinner than its sibling's:
  `experimental-deliberation/SKILL.md` is **383** against
  `proposal-deliberation/SKILL.md`'s **322**. On this side the sibling is
  `proposal-implementation/SKILL.md` at **2,854**.
- Cut 3 came in **+78%**; only the amendment hit its estimate (865 vs ~870).

| Slice | Delivers | Estimate |
|---|---|---|
| A — the skill, **one** document | Item 1 identical; M5; the kit-lock glob | 1,500–2,400 |
| B — `Data/` demandable per product folder | Item 6 | 250–450 |
| C — the second document verified on its own terms | Items 2, 5 | 900–1,500 |
| D — agreement + successor + Flow B to a submission | Items 3, 4 | 1,200–1,900 |
| | | **~3,850–6,250** |

**Recommendation: four chained changes. One is not deliverable and two is not
honest.** The ordering is deliberate and differs from the superseded proposal's:
**A goes first with a single-document profile**, because that configuration is
byte-identical engine behaviour, it delivers operator item 1 exactly, and it
puts the second profile on disk that M5 and the kit lock have been waiting for.
B is small, independent of the pair, and cheap to review. C is the new scalar→pair
and must land before any `documents[1]` entry ships, or item 2 ships as a check
that measured nothing. D is the only judgment work and must not be rushed behind
A's bulk. Against `review_budget_lines: 1400`, A alone likely needs stacking.

## Rollback Plan

Each slice is its own branch. A, B and D are additive — delete
`.claude/skills/experimental-implementation/`, the two agent files and the new
seal corpus, and the sibling is untouched by construction. C is the only slice
that reshapes shared reads; revert it and re-run the 28-digest seal, which is
the existing proof the revert was complete.

## Dependencies

- `experimental-deliberation` must publish an experiments document
  (`experiments/experiments-<slug>-v01.md`). `experiments/` and `proposals/`
  hold only `.gitkeep` here — **every fixture must be authored**.
- `_core/deliberation/engine/orchestrator.ts` as the shape source for
  acknowledgment (TypeScript; a shape to copy, not code to port).

## Success Criteria

- [ ] All 28 sealed digests byte-identical; `npm test` 595/595; Python `OK (skipped=6)` with `Ran` grown, not pinned.
- [ ] Document 1's fidelity status changes when **document 1's own text** changes, proven by a fixture where document 0 is clean.
- [ ] Both cross-document refusals are mutation-proven, each with the corpus case that reaches it named.
- [ ] The engine emits no resolution proposal and infers no repair direction.
- [ ] `verify.structure.missingDirs` can contain a `Data/`.
- [ ] M5 lands as a real test, not a `skipTest`.
- [ ] `KitAgreementLockTests` holds the second skill's kit without being edited again.
- [ ] No file under `proposal-implementation/` or `proposal-deliberation/` is modified.

## Proposal question round

Interactive mode; this executor cannot prompt. Questions whose answers change
the artifact, with the assumption used meanwhile. Two of the old four are now
answered by the fix and are dropped.

1. **The cross-document key.** `reference-experimental.ts` documents `[tests:X]`
   as citing an `[exp:X]` declared in the **same** document; the proposal
   declares `\tag{}`/`\label{}`. What key crosses them? *Assumed: a new explicit
   citation form is required; without one, refusal kind 1 fires on every
   document from day one.*
2. **Where per-document claim vocabulary lives.** New leaves on `documents[N]`
   (`claim_key`, `locus_key`, `citation_pattern`), or a parallel list beside
   `provenance`? *Assumed: on `documents[N]`, since that is the tier already
   validated per index.*
3. **Four slices, and A shipping single-document first?** *Assumed: yes to both.*
4. **`documents[1].label`.** `"experiments"` is the Cut-3 fixture's literal. Is
   it this skill's real label? *Assumed: yes.*

**Citations checked.** Every symbol above was resolved in source by name this
session, never by line number and never inherited. `unreached_mathematics` was
re-checked and found only in an `impl_profile.py` comment and in prose
artifacts; it is reported, not repeated as live.
