# Proposal: A `Data/` directory somebody can owe

> **Budget note.** This exceeds the default 450-word artifact budget,
> deliberately, on the precedent Slice C's own proposal records. The overage is
> spent on three things a shorter artifact would have had to assert instead of
> show: the defect re-measured rather than inherited, one inherited claim that
> measurement contradicts, and the proof this change has to pay for.

## Intent

Deliver the operator's **item 6**: make `Data/` **demandable per product
folder**, so a repository whose bound document declares a dataset can be told it
owes one.

## The defect, re-measured this session

`Data/` is already a first-class product category. Every claim in the brief was
re-checked in source, by symbol, this session:

| Already true | Where |
|---|---|
| `Data/` is a product category | `PRODUCT_DIRS = ("Notebooks", "Data", "Results", "Models")` |
| nine data extensions route to it | `DATA_EXT` — `.csv .tsv .parquet .npz .npy .arrow .feather .xlsx .mat`, routed by `classify` |
| references to it are scanned | `REFERENCE_RE`, `PATH_CHAIN_RE`, built by joining `PRODUCT_DIRS` |
| a misnamed one is detected | `detect_product_dir`, `misnamed_product_dir` |
| it is excluded only by a flag | `expected_dirs(name, with_data)` |

**Only demandability is missing**, and the reason is that both producers of
`with_data` derive it from the repository's own contents, never from a
declaration:

- `cmd_verify` — `with_data = (target / name / "Data").is_dir()`. Present →
  expected; absent → not expected. **`verify.structure.missingDirs` can
  therefore never contain a `Data/`.** Nobody can ever be told they owe one.
- `build_plan` — `dir_exists_after(target, f"{name}/Data", renames, name)` **or
  any move landing under `{name}/Data/`**.

### An inherited claim measurement contradicts

**§B4 records "two self-fulfilling producers". `build_plan` is not one.** Its
second disjunct reads the *moves*, so a `.csv` sitting at a repository root is
classified to `{name}/Data/…`, `with_data` goes true, and `{name}/Data` appears
in `plan.createDirs` **today**. The absolute claim holds for `cmd_verify` alone.

This matters twice. It shrinks the defect (`plan` already demands a `Data/` in
one case) and it enlarges the change: whatever `plan` learns, `cmd_apply` and
`_materialize_plan_gate` must learn identically, or their `build_plan` re-derivation
disagrees with the approved plan and every `apply` refuses `PLAN_STALE`.
**A parameter passed by one of three call sites looks exactly like working code.**

### F5's class is not finished

The seal spec's F5 requirement replaced the bare `"Data"` literal in
`expected_dirs` with `PRODUCT_DATA = PRODUCT_DIRS[1]`. **Three bare literals
remain** — in `classify`, in `build_plan` (twice on one expression), and in
`cmd_verify`. B touches two of the three; finishing the class here is an identity
refactor with zero seal delta, exactly as F5 was.

## Why B could not come earlier — state this wherever the order appears

Making `Data/` demandable needs **a document that declares a dataset**.
Measured: `**Dataset:**` is enforced only in the experimental deliberation
domain (`.claude/skills/experimental-deliberation/` — `profile.ts`,
`preservation-experimental.ts`, `SKILL.md`, and
`openspec/specs/experimental-plan-declarations/spec.md`, which makes exactly one
`**Dataset:** …` line a hard block on v1 and every successor). The mathematical
domain has **none**.

Until Slice C the skill could not read that document's vocabulary at all. **B
before C would have shipped a branch no configuration could reach**, and this
project's own scar says such a branch cannot be mutation-proven.

**The order is A → C → {B, D}.** It has been inverted twice already — once in the
Slice A proposal's A/B/C/D listing, once in its archive report — because a
lettered listing reads as a sequence. The evidence above travels with the
statement so the next reader does not have to take it on trust.

## The operator's ruling: per product folder, never one at the root

`Data/` belongs to **each product folder**, not to the repository. The argument,
which must survive into the specs:

1. Experiments bind to **one method**. `--name` already carries that binding.
2. The data may not apply to another method in the same repository.
3. A later paper may move to a different area entirely.

No new machinery is needed: `expected_dirs` already builds `f"{name}/{d}"`, so
the shape is right and only the flag's *source* changes.

## Scope

### In Scope

- **A declared-dataset detector.** One reader that answers "does the document
  bound to this run declare a dataset?" from the document's own bytes, using
  `revision_source` / `document_revision_names` — machinery Slice C already
  built.
- **The marker is profile-supplied, never an engine literal.** `**Dataset:**` is
  one domain's document format; the mathematical domain has no such line. An
  engine literal would be the exact leak the profile seam exists to remove —
  and **no lock would catch it**, because the neutrality lock derives its
  haystack from `vocabulary.names`, which does not and should not contain it.
- **`plan` gets a path to a document.** `--revision` is registered for exactly
  eight commands (`verify`, `admit`, `handoff`, `probe`, `position`, `gate`,
  `offer`, `close`); `plan` is not one. It must reach **all three**
  `build_plan` call sites — `cmd_plan`, `cmd_apply`, `_materialize_plan_gate` —
  not just the first.
- **`cmd_verify`'s `with_data` derived from the declaration**, so
  `missingDirs` can hold a `Data/`, `structure_ok` goes false, and the
  `standing` stage of this skill's own `OBJECTIVE_FLOW` is genuinely held.
- **Finishing F5's class** at the three remaining bare `"Data"` literals.
- **The reaching configuration, and its control.** `tests/experiments_seal/`
  already ships fixture A (`Trial/Data/` present) and fixture B (absent). B adds
  the second axis — a document that declares a dataset and one that does not —
  and proves `missingDirs` moves.

### Out of Scope

- **Slice D** — cross-document agreement, the experiments successor, Flow B to a
  test submission. D does not depend on B; both are proposed in parallel.
- **Any content check on `Data/`.** Presence only, as for the other three
  categories. The skill cannot know which files constitute the dataset.
- **Any refusal.** `verify` reports and never refuses; B is expected to add
  **zero** new refusal codes, so `reachable_refusal_codes`'s derived roster
  should not move. Assert that, do not assume it.
- **Parsing the dataset's identity.** Whether the declared dataset is present,
  correct, or the same one as last revision is `experimental-deliberation`'s
  preservation question, already answered there by the `dataset` atom.
- Any rename of `proposalDigest` or its campaign-proposal relatives — it is in
  `_AUTHORIZATION_BINDING_KEYS`, written into minted tokens in committed ledgers
  that travel in clones.
- **M2** (hardcoded Spanish deferral prose), **F6** (four `MANAGED_ARTIFACT_MARKER`
  spellings), and the kit crossing the seam.

## Capabilities

### New Capabilities

- `implementation-data-demandability`: the profile leaf that names a domain's
  dataset declaration, the detector that reads it, the document path into
  `plan`/`apply`/`materialize`, and the per-product-folder rule with its three
  reasons.

### Modified Capabilities

- `implementation-engine-neutrality`: the new leaf joins the validated-leaf
  table with its own dotted/indexed `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE`
  name and its **measured** mover set in `MEASURED_MOVERS` — measured, never
  forecast, per that spec's own correction note.
- `implementation-document-binding`: `--revision`'s registered command set and
  what a `plan` is bound to.
- `implementation-cli-seal`: the corpus coverage clause already requires
  "`Data/` present and absent"; it gains the declared/undeclared axis. The
  existing 28 stay byte-identical.
- `experimental-implementation-skill`: `SKILL.md` states that a declared dataset
  makes `Data/` demandable, and that it is per product folder.

## Approach

Profile leaf first, detector second, declaration last — and the declaration last
is the whole safety argument, not a convenience.

1. **The leaf and the fixture profile.** A fixture profile that declares a
   dataset marker is the reaching configuration. It lands before the shipped
   profile does, exactly as Slice C's `tests/fixtures/two_documents/` did.
2. **Thread the document, then read it.** `--revision` through all three
   `build_plan` call sites before the detector exists, proven by a test that
   the three agree (the `PLAN_STALE` criterion).
3. **A conditional key, never a new one.** Anything `plan` publishes about which
   document it read must be emitted **only when a document was nameable**, so a
   profile declaring no marker produces byte-identical stdout. The engine
   already uses this idiom — `_bound_to`'s pair shape appears only under
   `len(DOCUMENTS) > 1`.
4. **Declare the real marker on `experimental-implementation`'s `documents[0]`
   last**, after 1–3 are green against the fixture.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `_core/implementation/impl_domain_profile.py` | Modified | The dataset-marker leaf, its validation, its refusal name |
| `_core/implementation/engine/implementation_engine.py` | Modified | `build_plan` signature + 3 call sites; `cmd_verify`'s `with_data`; the detector; parser registration for `plan`/`apply`/`materialize`; F5's three remaining literals |
| `.claude/skills/experimental-implementation/impl_profile.py` | Modified | `documents[0]` declares its dataset marker — **last write of the change** |
| `.claude/skills/experimental-implementation/SKILL.md` | Modified | What `verify` now demands and why it is per product folder |
| `tests/experiments_seal/` | Modified | Second axis in the corpus; `plan`/`verify` cases; **digests move deliberately** |
| `tests/test_implementation_domain_mutation.py` | Modified | `MEASURED_MOVERS` gains the new leaf, measured |
| `tests/seal/`, `proposal-implementation/**`, `proposal-deliberation/**` | **Untouched** | the bar |

## The two bars — they are not the same

- **`tests/seal/` — the sibling's 28 digests — byte-identical.** Eight changes
  have held it. `git diff --exit-code tests/seal/` exits 0. **Any movement is a
  defect, never a new golden.** The structural reason it holds: the sibling's
  profile declares no dataset marker, so the detector can only answer "no", and
  every `with_data` takes the branch it takes today.
- **`tests/experiments_seal/` is the new skill's own corpus and is supposed to
  move** when the new skill's behaviour legitimately changes. It moved
  deliberately in C3 — 6 of 20 cases, each read before being accepted. The same
  discipline: read each moved case, accept it by hand, never regenerate in bulk.

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `--revision` reaches `cmd_plan` only — `apply` then refuses `PLAN_STALE` on every plan | **High** | A test that builds a plan with a revision and applies it; the three call sites asserted to agree |
| A fixture written to satisfy the detector proves nothing | **High** | The control is a second document **without** a dataset line, in the same corpus, whose `missingDirs` must stay empty. One survived a FAIL in this project already |
| A measurement of an absence with no control that could have seen a presence | **High** | The sibling's 28 staying still is the absence. The control that could have seen a presence is `experiments_seal`'s own `plan`/`verify` cases moving. **If none of them moves, the feature is unreachable and the change has proven nothing** |
| `sys.modules` caches `impl_domain_profile` process-wide | **High** | The mutation harness must `pop` it, or every leaf reads as a zero-mover |
| A same-size mutation reuses a stale `.pyc` | Med | Assert the anchor count in the mutated source; `git diff --stat` does not prove it |
| The engine gains a hardcoded `**Dataset:**` and nothing catches it | Med | The leak guard derives from `vocabulary.names`; this word is not in it. The leaf must be profile-supplied by construction, and a test must assert the engine spells no dataset marker |
| A flat `_core/implementation/*.py` detector reddens `CoreNamesNoDomainTests` | Med | That guard scans `CORE.glob("*.py")` **non-recursively** and fails any core file naming a `PRODUCT_DIRS` member. The detector belongs under `engine/`, or names `PRODUCT_DATA` |
| A pre-existing test broken by `build_plan`'s signature change | Med | Only a **full uninterrupted suite run** catches this class |
| An adjacent `sdd-propose` is writing Slice D concurrently | Med | This change writes only inside its own folder; line citations from either trail age immediately |

## Rollback Plan

Revert the change's commits; re-run the sibling's 28-digest seal and require
`git diff --exit-code tests/seal/` to exit 0; restore `tests/experiments_seal/`'s
pre-change `digests.json` **as part of the revert, not afterwards** — a moved
golden left behind survives the rollback silently and becomes the new baseline.
Removing the marker from `impl_profile.py` alone is not a rollback: the leaf's
validation would then refuse the profile.

## Dependencies

- **Slice C landed and archived.** `documents[0]` is the experiments document;
  without its declared vocabulary there is no dataset declaration to read.
- **An experiments document that actually carries a `**Dataset:**` line.**
  `experiments/` holds only `.gitkeep`; **every fixture must be authored from
  nothing**, as `tests/experiments_seal/corpus.py` already does.

## Success Criteria

- [ ] `verify.structure.missingDirs` contains a `Data/` for a target whose bound
      document declares a dataset and whose `{name}/Data/` is absent — shown in
      a real captured case, not asserted.
- [ ] The same target with the same document, `Data/` present → `missingDirs`
      empty. The control.
- [ ] A document declaring **no** dataset → `missingDirs` empty and byte-identical
      to today. The second control.
- [ ] All three `build_plan` call sites agree: a plan built with a revision
      applies without `PLAN_STALE`.
- [ ] The dataset-marker leaf is mutation-proven: removed → refusal naming that
      exact leaf; changed → a named `experiments_seal` case moves, or it is
      recorded as a measured zero-mover with its defence.
- [ ] Zero bare `"Data"` literals remain in the engine outside `PRODUCT_DIRS`.
- [ ] `git diff --exit-code tests/seal/` exits 0.
- [ ] `npm test` 595/595; Python `OK (skipped=6)` with `Ran` grown —
      **`skipped=6` must not move in a ninth change.**
- [ ] `reachable_refusal_codes`'s roster is unchanged, asserted not assumed.
- [ ] The A → C → {B, D} ordering and its evidence appear wherever this change
      states the slice order.

## Size — and how many changes

**Estimate: 450–750 changed lines.**

§B4 and the Slice A proposal both price B at **250–450**. That number prices the
**mechanism** — §B4's own "~2 lines at the decision, ~12 to make the fact reach
both, plus the detector" is roughly 50 lines of engine code — and prices **no
proof at all**: no corpus axis, no control, no mutation harness, no third
`build_plan` call site. Every estimate this session came in over except one, and
that one priced its proof.

| Slice | Delivers | Gate at the end | Estimate |
|---|---|---|---:|
| **B1** | The profile leaf + detector + `--revision` through all three `build_plan` call sites + F5's three literals; a **fixture** profile declaring a marker | 28 sibling digests identical; the `PLAN_STALE` agreement test green; leaf mutation-proven | 300–500 |
| **B2** | Declare the marker on the shipped `documents[0]`; the `experiments_seal` second axis and its deliberately-moved digests; `SKILL.md` | `missingDirs` holds a `Data/` in a captured case, with both controls | 150–250 |
| | | | **450–750** |

**Recommendation: two chained changes, in that order — not one.**

Declaring the shipped marker before the detector is proven is the C3 defect at
smaller scale: a green suite cannot distinguish "the detector reads the
document" from "the fixture was written to pass". B1 ships the reaching
configuration as a fixture, which is what makes B2's declaration a measurement
rather than an assertion.

Both slices fit under `review_budget_lines: 1400`; neither fits the 400-line
default, so neither may merge unstacked.

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
```

## Proposal question round

Interactive mode; this executor cannot prompt. Each question changes the
artifact; the assumption used meanwhile is stated.

1. **Where does the dataset declaration live — per document, or per profile?**
   In `experimental-implementation`, `documents[0]` (experiments) declares a
   dataset and `documents[1]` (the mathematical proposal) never will. *Assumed:
   a per-`documents[N]` leaf, so the placement states which document owes the
   dataset — matching the operator's per-product-folder reasoning, where the
   binding is to one method, not to a repository.*
2. **Is the leaf required of every profile, or optional?** Required makes a typo
   impossible to miss and makes the sibling's silence an explicit "this domain
   demands no data", at the cost of a one-line edit to
   `proposal-implementation/impl_profile.py`. Optional touches nothing but lets
   a misspelled key disable the demand silently. *Assumed: required, because the
   real bar is `git diff --exit-code tests/seal/`, not zero bytes in the
   sibling's tree — and a `None` value takes exactly today's branch.*
3. **What does `plan` do when no document is nameable?** §B4 recommends
   `with_data` unchanged rather than a refusal. The argument for it: `plan` is
   the first command of the flow and runs on a bare clone, before anything is
   bound; refusing would make the flow unenterable. The argument against: an
   operator who forgets `--revision` gets a plan that silently omits a `Data/`
   they owe, and `verify` demands it minutes later. *Assumed: unchanged, **plus**
   a conditional key naming the document `plan` actually read — emitted only when
   one was nameable, so the sibling's digests cannot move. Silence is what makes
   the omission dangerous, not the leniency.*
4. **Does an empty `Data/` satisfy the demand?** Today `expected_dirs` demands
   existence only, so `mkdir Data` clears it. *Assumed: presence only, matching
   `Notebooks/`, `Results/` and `Models/` — named here so "it passed with an
   empty folder" is a recorded decision, not a later surprise.*
5. **Should the demand hold the `standing` stage?** `missing_dirs` feeds
   `structure_ok`, and this skill's `OBJECTIVE_FLOW` puts `structure` reporting
   no gaps in `standing`'s `behindWhen`. *Assumed: yes — the same mechanism that
   already holds `standing` for the other three categories, with no new gate
   invented for this one.*

## Citations checked

Every symbol named above was resolved in source **this session, by name, never
by line, never inherited**: `PRODUCT_DIRS`, `PRODUCT_DATA`, `PRODUCT_NOTEBOOKS`,
`DATA_EXT`, `classify`, `expected_dirs`, `in_place`, `dir_exists_after`,
`detect_product_dir`, `misnamed_product_dir`, `REFERENCE_RE`, `PATH_CHAIN_RE`,
`build_plan`, `cmd_plan`, `cmd_apply`, `_materialize_plan_gate`, `cmd_verify`,
`structure_ok`, `scaffold_gaps`, `present_files`, `revision_source`,
`document_revision_names`, `latest_revision`, `revision_discovery`,
`discover_document_revision`, `_bound_to`, `DOCUMENTS`, `DOCUMENTS_DIRECTORY`,
`DOCUMENTS_LABEL`, `OBJECTIVE_FLOW`, `_AUTHORIZATION_BINDING_KEYS`,
`proposalDigest`, `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE`, `MEASURED_MOVERS`,
`discover_profiles`, `LockBEngineNeutralityTests`, `TwoDocumentReadProvenTests`,
`CoreNamesNoDomainTests`, `PublishedCommandsRunVerbatimTests`,
`reachable_refusal_codes`.

**Three inherited claims were re-measured; one is corrected:**

1. *"Two self-fulfilling producers."* **Corrected.** `cmd_verify`'s `with_data`
   is purely self-fulfilling; `build_plan`'s is not — its move-derived disjunct
   can already put a `Data/` in `createDirs`. The conclusion (nobody can be told
   they owe one *by `verify`*) stands; the attribution did not.
2. *"Nine data extensions."* **Confirmed exactly** — `DATA_EXT` holds nine.
3. *"F5 replaced the bare `Data` literal."* **Scoped.** It replaced the one in
   `expected_dirs`. Three remain, in `classify`, `build_plan` and `cmd_verify`.

**No test suite was run**, per this change's brief: a parallel `sdd-propose` is
writing Slice D. The `595/595` and `Ran 2977, OK (skipped=6)` figures above are
the brief's baseline at `8fb1ff3`, carried forward as a claim to re-measure at
apply, never as a measurement taken here.

---

## The five questions, ruled (orchestrator, after the question round)

All five assumptions stand. Four follow from precedent already set; the second
changes how one bar is proven and is argued at length.

| # | Ruling |
| --- | --- |
| 1 | **Per-`documents[N]` leaf.** Matches Slice C's per-document vocabulary and the fact on disk: `documents[0]` declares a dataset and `documents[1]` never will |
| 2 | **Required.** See below |
| 3 | **`plan` unchanged, plus the conditional key** naming the document it actually read. The addition is the better half of the answer |
| 4 | **Presence only.** Judging whether the data is the *right* data would be an inference, the same reason `missing_provenance` stayed shared in C |
| 5 | **Yes, it holds `standing`** — by the mechanism already holding it for the other three categories, with no new gate invented |

### Why required, and what it costs

Optional is the tempting answer because it touches nothing. It is also the
**unprovable-guard shape this project has spent eight changes removing**: an
optional leaf whose key is misspelled disables the demand **in silence**, and a
demand that silently stops demanding is indistinguishable from one that was never
written. Required turns that same typo into a refusal.

It also buys something real: the sibling declaring `None` **says out loud** that
this domain demands no data. Silence says nothing, and cannot be told from an
oversight.

**The cost is honest and must be named**: one line in
`proposal-implementation/impl_profile.py`. Through eight changes the
non-interference proof has been `git diff --name-only … → 0 files` on the
sibling's tree. Required breaks *that particular proof*, and substitutes the one
the operator's own words always described: *"no puede **afectar** lo que ya
funciona"* — affect, not touch.

So the bar does not relax, it moves to where it belongs: **the 28 sealed digests
byte-identical, `npm test` 595/595, and Python `OK (skipped=6)`.** A `None` value
takes today's exact branch, which apply must prove rather than assert.

What does NOT change: `tests/seal/` stays byte-identical, and every other
directory of the sibling stays at zero files.
