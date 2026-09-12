# Tasks: A `Data/` directory somebody can owe — Slice B

> Budget note: over 530 words, on the precedent this change's own proposal/
> design set. Every threat-matrix `Yes` row and every X1–X5 mutation needs its
> own named RED task (strict_tdd); eliding one would hide a case design priced.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 510-800 (B1 340-520, B2 170-280) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | B1 → B2 (sequential, B2 depends on B1) |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 (B1) | Leaf + detector + `--revision` on `plan` + `build_plan`'s 3rd param at all 3 call sites + `cmd_verify` reorder + F5 finish + mutation proof | PR 1 | `python3.12 -m unittest tests.test_experimental_implementation tests.test_implementation_profile tests.test_implementation_domain_mutation tests.test_implementation_core` | Real subprocess `plan --revision X` → approve → `apply`, and `materialize --stage` | Revert commits; `dataset_marker` stays required so a bare key removal alone is not a rollback |
| 2 (B2) | Declare `documents[0].dataset_marker`; `experiments_seal` 2nd axis (D9); `LockCDeclaredMarkerTests`; `SKILL.md` | PR 2 | `python3.12 -m unittest tests.test_implementation_domain_lock` + `tests/experiments_seal` harness | `verify --revision dataset-1.md` against fixture B, captured | Revert B2 commits; restore pre-change `tests/experiments_seal/digests.json` as part of the revert |

## Phase 1: Profile leaf (B1)

- [x] 1.1 RED: `tests/test_implementation_profile.py` — per-index case: a `documents[N]` entry missing `dataset_marker` raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming `documents[N].dataset_marker` exactly.
- [x] 1.2 GREEN: `.claude/skills/_core/implementation/impl_domain_profile.py` `_resolve()` — append a `dataset_marker` required-key check to the per-entry walk, right after the existing `label` check; NOT added to `_DOCUMENT_VOCABULARY_LEAVES`.
- [x] 1.3 `tests/fixtures/two_documents/impl_profile.py` — add two `"dataset_marker": None` lines (fixture edit, not the reaching configuration).
- [x] 1.4 `.claude/skills/proposal-implementation/impl_profile.py` — add the one sanctioned sibling line, `"dataset_marker": None,`.
- [x] 1.5 (finding, closed) `.claude/skills/experimental-implementation/impl_profile.py` — both `documents[N]` entries also need `"dataset_marker": None` in B1, not only in B2: the required-key check would otherwise redden this skill's own `test_the_real_profile_resolves_cleanly`/`LeafRefusalTests`/`PublishedCommandsRunVerbatimTests` the moment it lands, since `_resolve()` validates the REAL shipped profile in those tests. `documents[0]` still gets its real marker only in B2 (task 8.1); `documents[1]` stays `None` permanently.

## Phase 2: Detector (B1)

- [x] 2.1 RED: `tests/test_experimental_implementation.py` — `None` marker never opens a file (revision points at a missing file, detector still returns `False`, no raise).
- [x] 2.2 RED: same file — line-leading match: `lstrip().startswith(marker)` true only when the marker starts the line; a **mid-sentence-only** occurrence answers `False` (the X3 strength case).
- [x] 2.3 RED: same file — a marker containing regex metacharacters (e.g. `.*`) matches only literally (host-supplied-text threat row).
- [x] 2.4 RED: same file — or-fold: a two-document fixture where only index 1 declares still answers demand `True` (kills "read index 0 always").
- [x] 2.5 GREEN: `.claude/skills/_core/implementation/engine/implementation_engine.py` — add the detector, reading each declared document via `revision_source`/`document_revision_names` (no new path-join site), or-folded across `documents[N]`.

## Phase 3: Thread `--revision` through `build_plan` (B1)

- [x] 3.1 RED: `tests/test_experimental_implementation.py` — `plan` with no `--revision` on a target with no documents root exits 0, stdout byte-identical to today (reading-at-plan-time threat row).
- [x] 3.2 RED: same file — the `PLAN_STALE` agreement test: real subprocesses, `plan --revision X` → approve → `apply` exits 0 and `createDirs` contains the declared `Data/`; repeat through `materialize --stage`.
- [x] 3.3 RED: same file — an approved `plan.json` with no `"boundTo"` key still applies (pre-existing-plans data-integrity row).
- [x] 3.4 GREEN: engine `main()` parser registration — add `--revision` on `plan` alone (joins the eight-name set as its own registration, mirroring `walk`'s separate one).
- [x] 3.5 GREEN: `build_plan` gains a third parameter; new disjunct `declared or <existing two>`; `plan["boundTo"]` emitted only when `revision is not None`.
- [x] 3.6 GREEN: `cmd_plan` passes `args.revision`; `cmd_apply` and `_materialize_plan_gate` read the seed from `approved["boundTo"]["revision"]` (never compared in `cmd_apply`'s four-key check) and pass the same seed to `build_plan`.

## Phase 4: `cmd_verify` reorder (B1)

- [x] 4.1 GREEN: `cmd_verify` — move `with_data`, `missing_dirs`, `structure_ok` below `revision = args.revision or discovered` (D5, three statements, no restructure). Measured: `git diff --exit-code tests/seal/` exits 0, sha256 unchanged at `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`, and the sibling's full suite (`test_proposal_implementation.py`, 1477 tests) stays `OK (skipped=2)`.
- [x] 4.2 GREEN: `with_data` becomes `declared or (target / name / "Data").is_dir()`.

## Phase 5: Finish F5 (B1)

- [x] 5.1 GREEN: replace the 3 remaining bare `"Data"` sites (`classify`, `build_plan`'s two-occurrence expression, `cmd_verify`) with `PRODUCT_DATA`.
- [x] 5.2 RED+GREEN: `tests/test_implementation_core.py` — `ZeroBareDataLiteralTests`: `PRODUCT_DATA` taken off the CLI, asserted to appear quoted exactly once in engine source (the `PRODUCT_DIRS` tuple). Measured RED before 5.1 (2 quoted occurrences), GREEN after (1).

## Phase 6: Mutation proof (B1)

- [x] 6.1 RED: X1 — delete `dataset_marker` from one `documents[N]`; assert `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` names that exact index. Already proven by Phase 1's `test_each_cut2_leaf_refuses_incomplete_and_names_itself` (index 0, via `_CUT2_LEAVES`) and `DatasetMarkerLeafOwnTierTests.test_a_second_documents_missing_dataset_marker_refuses_by_indexed_name` (index 1) — no new test needed.
- [x] 6.2 RED: X2 — `tests/test_implementation_domain_mutation.py`: `MUTATIONS["documents.dataset_marker"] = ('"dataset_marker": None,', '"dataset_marker": "## 2",')`; run against the sibling's real corpus. **Measured**: `("verify-b", "verify-t")` moved (matches the design's prediction exactly), recorded in `MEASURED_MOVERS`.
- [x] 6.3 RED: X4 — `OrFoldIndexHardcodeMutationTests`: in the fold, `DOCUMENTS[index]` → `DOCUMENTS[0]`, planted into a scratch copy of the WHOLE `_core/implementation/` tree (never the shipped engine), run directly (not through the launcher). Measured: the document-1-only fixture (2.4's configuration) now answers `False` under the mutation (was `True`); the sibling's own single-document profile answers identically under both engines (`False`), proving the mutation is a no-op there by construction.
- [x] 6.4 RED: X5 — `SeedForcedNoneMutationTests`: `cmd_apply`/`_materialize_plan_gate` forced to pass `None` instead of the `approved["boundTo"]` seed, each in a scratch-forge copy, run via a real `plan`→`apply`/`materialize` flow. Measured: both mutations flip an otherwise-successful call to refuse `PLAN_STALE`.

## Phase 7: B1 non-interference gate

- [x] 7.1 `git diff --exit-code tests/seal/` exits 0. Measured: exit 0, sha256 `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` (unchanged from baseline).
- [x] 7.2 Full suite: `npm test` 595/595; Python `OK (skipped=6)` with `Ran` grown, `skipped=6` unmoved, no `skipTest` added. Measured: `npm test` 595/595; Python `Ran 2996 tests ... OK (skipped=6)` (grown from the 2977 baseline by the 19 new B1 test cases). **Found and fixed a real regression along the way**: `tests/test_experimental_implementation.py`'s `_engine_with_documents` helper set `IMPLEMENTATION_DOMAIN_PROFILE` and mutated `sys.modules["impl_domain_profile"]` without restoring either — leaking into every later-running test file in the same `unittest discover` process and reddening ~110 unrelated cases in `test_proposal_implementation.py`. Fixed by restoring both to their pre-call state in a `finally` block. Also fixed `tests/pair/corpus.py`'s `_SECOND_DOCUMENT_ENTRY`/`_SECOND_DOCUMENT_WITHOUT_DIRECTORY` anchors, stale after task 1.3's fixture edit added a `dataset_marker` line to the second document entry.
- [x] 7.3 Assert `reachable_refusal_codes()`'s derived roster unchanged (zero new refusal codes). Measured: `len(reachable_refusal_codes()) == 114`, matching the pre-change count exactly (the docstring's inherited "112" claim was already stale before this change; 114 is what `test_proposal_implementation.py`'s own pinned assertion holds today, unmoved).
- [x] 7.4 Assert `tests/experiments_seal/digests.json` unmoved (B1 touches zero of its 20 cases). Measured: `git diff --exit-code tests/experiments_seal/` exits 0.

## Phase 8: Shipped declaration (B2)

- [x] 8.1 `.claude/skills/experimental-implementation/impl_profile.py` — declare `documents[0]`'s real `dataset_marker` (last write of the change; `documents[1]` stays `None` permanently). Declared `"**Dataset:**"`, matching the exact literal `experimental-deliberation` already enforces on this domain's own documents.
- [x] 8.2 `.claude/skills/experimental-implementation/SKILL.md` — state the per-product-folder `Data/` demand and its three reasons. Measured green after: `test_experimental_implementation.py` (19/19), `test_implementation_domain_lock.py` (24/24), `test_implementation_domain_mutation.py` (12/12); `tests/seal/` and `tests/experiments_seal/` both git-diff-clean.

## Phase 9: Corpus second axis (B2, D9)

- [ ] 9.1 `tests/experiments_seal/corpus.py` — author `dataset-0.md`/`dataset-1.md`, byte-identical except one `**Dataset:**` line, outside the discovered `trial-(\d+)\.md` family.
- [ ] 9.2 `tests/experiments_seal/cases.json` — add `verify-b-declared`, `verify-a-declared`, `verify-b-undeclared`, `plan-b-declared`.
- [ ] 9.3 RED then GREEN: regenerate `digests.json`; assert **zero** of the existing 20 cases move, only `__corpus_fingerprint__` plus the 4 new entries; read each new digest by hand before accepting (never bulk-regenerate).

## Phase 10: New neutrality lock (B2)

- [ ] 10.1 `tests/test_implementation_domain_lock.py` — `LockCDeclaredMarkerTests`: for every profile `discover_profiles()` finds, for every non-`None` `documents[N].dataset_marker`, assert the literal appears in no file under `ENGINE_DIR`; assert `len(markers) > 0` (non-vacuity, only true after 8.1).

## Phase 11: B2 acceptance gate

- [ ] 11.1 Capture `verify-b-declared`: `missingDirs` contains `Trial/Data`, `structure.status: drift`. Capture both controls (`verify-a-declared` present → empty; `verify-b-undeclared` → empty, byte-identical elsewhere).
- [ ] 11.2 `git diff --exit-code tests/seal/` exits 0 again.
- [ ] 11.3 Full suite re-run: `npm test` 595/595; Python `OK (skipped=6)` unmoved.
