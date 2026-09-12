# Proposal: The second skill the seam was for

## Intent

Five cycles moved the implementation CLI behind a profile seam so a second
skill could be thin. Build it: `experimental-implementation`, carrying its own
north, verifying code against **both** the latest mathematical proposal and the
latest experiments document, publishing an experiments successor when the code
contradicts it, and reaching a test submission through Flow B's existing paths.

## Measured before proposing

Symbols were resolved in source, never inherited. Three inherited claims moved.

| Claim | Measured at HEAD | Consequence |
|---|---|---|
| `unreached_mathematics` crosses the join | **Does not exist.** Cut 2 renamed it `unreached_modules` (wire `unreachedModules`). Still named 2× in the **live** `implementation-engine-neutrality/spec.md` | A live spec carries a dead symbol. Correct it here. |
| Cut 3 made the pair addressable | `revision_source(revision, index)` = `proposals_root(index) / revision` — **one filename in N roots**. `revision_discovery` takes **no index** (reads `proposals_root()`). `--revision` is one scalar token for the eight commands that register it; `plan` still registers none (F4 holds). | See below. |
| `acknowledgedRemovals` is the precedent | Lives in `_core/deliberation/engine/orchestrator.ts` — **TypeScript**. The Python engine has no analogue. | It is a shape to copy, not code to port. |

**The blocking finding.** `proposal-deliberation` publishes
`proposals/research-concept-<slug>-r01.md`; `experimental-deliberation`
publishes `experiments/experiments-<slug>-v01.md` (`stem`, `directory`,
`revisionPattern: "v"`). The two documents **can never share a filename**, so
Cut 3's join cannot bind them. `_extra_document_revisions` answers `sha256:
None` for an unreadable index and does not refuse — "reported, never refused".
Operator items 2 and 5 are therefore **not reachable by configuration**, and
their failure mode is the one this project keeps paying for: a check that reads
green because it measured nothing. Cut 3's own fixture writes `r1.md` into both
roots, so the fixture does not expose it either.

**The second blocking finding.** `LockBEngineNeutralityTests` unions **every**
profile's `vocabulary.names` and scans the engine. Measured in
`implementation_engine.py`: `experiment(s)` **30**, `benchmark(s)` **89**,
`baseline|ablation|protocol|metric|sweep` **39**. This domain's subject words
cannot enter `names`. Both precedents already answer it —
`experimental-deliberation` declares `names: ["experimental-deliberation"]`
(its namespace only), and `documents.label: "proposal"` is governed by a
three-layer exclusion test instead. Follow them; record the collision.

## Scope

### In Scope
- Per-document revision addressing (indexed discovery, independent naming, per-index refusals, no silent `None`).
- The `experimental-implementation` skill: `impl_profile.py` with its own `OBJECTIVE_FLOW` and two `documents`, launcher, two ~70-line agents, `SKILL.md`, its own sealed corpus.
- `Data/` demandable **per product folder** (`--revision` on `plan`, `source` threaded into `build_plan`, plus the detector; `with_data` is self-fulfilling at both producers today).
- The two mechanical cross-document refusals + per-discrepancy acknowledgment.
- The experiments-successor composer, with its block locator shipped **beside the profile** (operator ruling: option A).
- Flow B's existing paths through to a test submission.
- **M5 becomes landable**: it was deferred only because "the others set is empty" with one profile. This change creates the second. Land it as its own unit.

### Out of Scope
- Any rename of `proposalDigest` or its ten campaign-proposal relatives; F6; **M2** (`cmd_handoff`'s hardcoded Spanish, still unresolved).
- Judging whether an experiment's metric or protocol *corresponds* to a claim. Tutor bullet in `SKILL.md`, never a check — it would block correct work and pass broken work.
- Any engine-generated resolution proposal. The engine refuses and names the discrepancy; the agent proposes in conversation; the operator decides.

## Capabilities

### New Capabilities
- `experimental-implementation-skill`: the second skill's own surface — north, agents, profile leaves, launcher, seal corpus.
- `implementation-cross-document-agreement`: the two refusals, per-discrepancy acknowledgment, and the explicit non-verdict boundary.
- `implementation-product-data`: `Data/` demandable per product folder.

### Modified Capabilities
- `implementation-document-binding`: per-document revision addressing; the silent-`None` tolerance becomes a named refusal.
- `implementation-engine-neutrality`: the `names` collision ruling; M5; correct the dead `unreached_mathematics` citation.
- `implementation-cli-seal`: the second skill's corpus; non-interference extended.

## Approach

Mirror the seam, do not fork it. One command roster, one refusal vocabulary,
one place the flow is described. The engine refuses and names; judgment stays
with the operator.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `_core/implementation/engine/implementation_engine.py` | Modified | Indexed revision addressing, `Data/` demandability, the two cross-document refusals |
| `.claude/skills/experimental-implementation/` | New | Profile, launcher, `SKILL.md`, block locator |
| `.claude/agents/implementation-*` (two new) | New | ~70 lines each, no logic |
| `tests/test_implementation_domain_lock.py` | Modified | `KitAgreementLockTests._profile()` hardcodes `proposal-implementation`; it must glob like `discover_profiles()` |
| `tests/seal/` | Added beside | Existing 28 untouched; `git diff --exit-code tests/seal/` exits 0 |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A `names` word reddens the engine on 158 sites | **High** | Declare the namespace word only; record the collision |
| Second document binds to `None` and reads green | **High** | Replace the tolerance with a named refusal; mutation-prove it |
| Engine edits move a sibling digest | Med | All 28 byte-identical; `skipped=6` unmoved |
| `L1_EXPECTED_COUNT = 96` / `L1_EXPECTED_FILES` pin breaks | Med | Any new engine file spelling `proposal` reddens it |
| A branch no configuration reaches (Cut 3 shipped 24) | Med | Name the reaching case per branch before writing the assertion |
| `declared_objective` raises on both norths | Low | The new skill declares `OBJECTIVE_FLOW` and **no** `profile.ts` |
| The agreement stage is unmeasurable | Med | If its `behindWhen` matches `UNMEASURABLE`, every bound agent must name it (`test_an_unmeasurable_stage_is_never_delegated`) |

## Size — and one change or three

Cut 3 estimated ~1,400 and measured **2,497 (+78%)**. Anchors measured here:
`proposal-implementation/SKILL.md` is **2,854 lines**; the second *deliberation*
skill cost ~1,112 authored lines **with zero engine changes** — and this one
needs engine changes.

| Slice | Delivers | Estimate |
|---|---|---|
| A — per-document revision addressing (engine) | Makes items 2 and 5 reachable at all | 600–900 |
| B — the skill, thin | Items 1, 2, 5, 6; M5 | 1,800–2,600 |
| C — agreement + successor + Flow B | Items 3, 4 | 1,500–2,200 |
| | | **~4,000–5,700** |

**Recommendation: three chained changes, not one and not two.** Slice A is
engine work under the byte-identical bar and belongs with the cuts, not with
authoring. B is independently useful the moment it lands — a running second
skill. C is the only judgment work and should not be rushed behind B's bulk.
Two is the minimum honest split (A+B, then C); three is what the numbers say.
Against a `review_budget_lines: 1400`, one change is not deliverable.

## Rollback Plan

Each slice is its own branch. B and C are additive — delete
`.claude/skills/experimental-implementation/`, the two agent files, and the new
seal corpus, and the sibling is untouched by construction. A is the only slice
that edits shared code; revert it and re-run the 28-digest seal, which is the
existing proof that the revert was complete.

## Dependencies

- `experimental-deliberation` must be able to publish an experiments document. `experiments/` holds only `.gitkeep` today, and `proposals/` likewise — **there is no corpus in this worktree**, so every fixture must be authored.
- `_core/deliberation/engine/orchestrator.ts` as the shape source for acknowledgment.

## Success Criteria

- [ ] All 28 sealed digests byte-identical; `npm test` 595/595; Python `OK (skipped=6)` with `Ran` grown, not pinned.
- [ ] The second document's revision is named independently of the first, and an unresolvable one **refuses by name** rather than reporting `None`.
- [ ] Both cross-document refusals are mutation-proven, each with the corpus case that reaches it named.
- [ ] The engine emits no resolution proposal — only the named discrepancy.
- [ ] `verify.structure.missingDirs` can contain a `Data/`.
- [ ] M5 landed as a real test, not a `skipTest` (which would move `skipped=6`).
- [ ] No file under `proposal-implementation/` or `proposal-deliberation/` is modified.

## Proposal question round

Interactive mode; this executor cannot prompt. Four questions whose answers
change the artifact, with the assumption used in the meantime.

1. **The join.** The ruling says the documents "cross mechanically", but
   `reference-experimental.ts` documents `[tests:X]` as citing an experiment
   `[exp:X]` declares in the **same** document, while the proposal declares
   `\tag{}`/`\label{}`. What is the actual cross-document key? *Assumed: a new
   explicit citation form is required; without one, refusal kind 1 fires on
   every document from day one.*
2. **Naming the second revision.** Given the two documents can never share a
   filename: a second flag (`--experiments-revision`), or per-index discovery
   with no flag at all? *Assumed: discovery, with a flag as override.*
3. **Three slices or two?** *Assumed: three.*
4. **`documents[1].label`.** `"experiments"` is the Cut-3 fixture's literal. Is
   that this skill's real label? *Assumed: yes.*

**Citations checked.** Every symbol named above was resolved in source by name
this session. `unreached_mathematics` did not resolve and is reported as a
defect rather than repeated.
