# Tasks: The second document, verified on its own terms — Slice C

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1,850–2,850 (design's floor; A's own estimate came in 43% low) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | C1 → C2a → C2b → C3 (design D8's shape; C2a is closest to budget alone) |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| C1 | Overlay leaves, resolver tier, indexed refusals, `citation_pattern` group count | PR 1 | `python -m unittest tests.test_implementation_profile` | Real subprocess via `_write_scratch_profile` (no shipped profile edited) | `impl_domain_profile.py` diff only; revert leaves 28 digests untouched (branch unreachable) |
| C2a | The real per-document fold; drift-control fixture (C-fwd/C-inv/C-shared) | PR 2 (base: C1) | `python -m unittest tests.test_implementation_pair` | Real subprocess via `_build_env_with_profile_override` on `tests/fixtures/two_documents/impl_profile.py` | `implementation_engine.py` fold rewrite + fixture overlay; revert leaves C1 dormant (`len(DOCUMENTS) > 1` gate) |
| C2b | Remaining 21 reader lines threaded by index (`CITATION_RE`, notation, locus) | PR 3 (base: C2a) | `python -m unittest tests.test_implementation_pair.TwoDocument*` | Same fixture, a finding naming both documents with different citation patterns | Reader-line diff only; revert leaves C2a's fold correct but single-pattern |
| C3 | Declare `documents[1]`; delete D10 lock; second-document seal; `SKILL.md` | PR 4 (base: C2b) | `python -m unittest tests.test_implementation_domain_lock` and `python -m unittest tests.experiments_seal` | Full `implementation_cli.py verify` against the shipped skill with two documents | Revert restores `SingleDocumentGuaranteeTests` and the one-document profile in the same commit |

## Phase 1: C1 — Per-document vocabulary leaves and resolver tier

- [x] 1.1 RED: in `tests/test_implementation_profile.py`, add cases asserting a `documents[N]` entry declaring only one of the five leaves (`claim_key`, `locus_key`, `remedy_locus_key`, `notation_keys`, `citation_pattern`) refuses `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming that exact missing indexed leaf (e.g. `documents[1].notation_keys`) — one case per leaf (5 cases), against the shipped resolver where the leaf does not exist yet, so this is red because the leaf is unrecognized.
- [x] 1.2 GREEN: in `.claude/skills/_core/implementation/impl_domain_profile.py`, extend `_resolve()`'s existing `documents[{index}].directory`/`.label` walk (near the `missing.append(f"documents[{index}].label")` line) with the all-or-nothing check: if any of the five leaves is present on an entry, all five must be present, else `missing.append(f"documents[{index}].<leaf>")` for each absent one, reusing the existing `missing` accumulator so `_resolve()` still raises one `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming all of them.
- [x] 1.3 RED: add a case asserting a `documents[N]` entry declaring none of the five leaves resolves without refusal and without requiring `provenance.*`/`findings.*` edits (spec `implementation-per-document-vocabulary` Requirement "A Per-Document Vocabulary Leaf Overlays, Never Replaces, The Top-Level One").
- [x] 1.4 GREEN: add `document_vocabulary(index)` to `.claude/skills/_core/implementation/engine/implementation_engine.py`, returning the five resolved values — the per-document overlay if declared, else the existing top-level `PROFILE["provenance"]`/`PROFILE["findings"]` scalars (D1/D2).
- [x] 1.5 GREEN: re-derive `CLAIM_KEY`, `LOCUS_KEY`, `REMEDY_LOCUS_KEY`, `NOTATION_KEYS` through `document_vocabulary(0)["..."]` and `CITATION_RE` through `re.compile(document_vocabulary(0)["citation_pattern"])`, replacing the direct `PROFILE[...]` reads at their module-level definitions (D2). Assert byte-identical values in `tests/test_implementation_profile.py` for a profile declaring no overlay (zero-delta proof, not inference).
- [x] 1.6 RED: add cases for `notation_keys` shape validation — a mapping missing `locus`, `remedyLocus`, or `unknown` refuses `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming `documents[1].notation_keys.remedyLocus` (etc., one case per missing sub-key).
- [x] 1.7 GREEN: in `_resolve()`, validate a declared `notation_keys` overlay carries all three sub-keys (`locus`, `remedyLocus`, `unknown`), refusing by the exact indexed sub-path per 1.6.
- [x] 1.8 RED: add four `citation_pattern` group-count cases in `tests/test_implementation_profile.py` — a 2-group pattern and a 4-group pattern, each declared once at the top-level `findings.citation_pattern` and once as a `documents[N].citation_pattern` overlay — each asserting a new `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CITATION_PATTERN` refusal naming the exact leaf and the declared group count (Y2; spec `implementation-per-document-vocabulary` Requirement "`citation_pattern`'s Group Count Is Validated At Resolve Time, By Name").
- [x] 1.9 GREEN: in `_resolve()`, after resolving each `citation_pattern` (top-level fallback and every overlay), compile it and refuse `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CITATION_PATTERN` unless the compiled pattern exposes exactly three capturing groups — apply to the top-level pattern too (D3's rationale: it is document 0's pattern under the fallback).
- [x] 1.10 RED: add a case asserting document 1's missing per-document `claim_key` does not silently borrow document 0's declared per-document override (spec `implementation-per-document-vocabulary` Requirement "No Document's Vocabulary Is Inferred From Another Document's") — document 0 declares an overlay, document 1 declares none, document 1 must resolve to the top-level fallback.
- [x] 1.11 GREEN: confirm `document_vocabulary(index)` (1.4) never reads another index's resolved entry — each index's lookup is independent by construction; add the assertion from 1.10 to lock it.
- [x] 1.12 VERIFY: run `git diff --exit-code tests/seal/` and `python -m unittest tests.seal` — 28 digests byte-identical (C1's branches are unreachable under one document). Run `python -m unittest tests.pair` and confirm `tests/pair/digests.json` unmoved (M5 — measure, do not infer). Run `python -m unittest tests.test_implementation_profile tests.test_implementation_domain_mutation` for the Y1/Y2 mutation rows (below).
- [x] 1.13 MUTATE (Y1): clear `__pycache__`, delete each of the five overlay leaves from a scratch declared overlay one at a time, confirm the anchor (leaf literal) count 1→0 before and after, watch the matching 1.1 case go red, restore.
- [x] 1.14 MUTATE (Y2): declare a two-group and a four-group `citation_pattern` in scratch, top-level and overlay (4 cases total), confirm anchor count, watch the 1.8 cases go red, restore.
- [x] 1.15 MEASURE: `reachable_refusal_codes()` in `tests/test_proposal_implementation.py` — confirm the pin is unmoved (C1's refusals are `ImplementationProfileError`, invisible to that walk per M4). Report the measured number, do not repeat 114 by inheritance.

## Phase 2: C2a — The per-document fidelity fold and its drift control

- [x] 2.1 GREEN (fixture-content, not resolver-required): in `tests/fixtures/two_documents/impl_profile.py`, add a `documents[1]` overlay declaring its own `claim_key`/`locus_key`/`remedy_locus_key`/`notation_keys`/`citation_pattern`, distinct from the inherited `equations` values, so document 1 no longer equals document 0's module scope (M6 — without this the control fixture is unbuildable, independent of the resolver's rule).
- [x] 2.2 RED (structural, the deliverable): in `tests/test_implementation_pair.py`, add `TwoDocumentDriftControlTests` with three separate test methods (never one method with three asserts, per D6):
  - `test_c_fwd_document_one_drifts_document_zero_clean` — document 0's modules bound to its current revision, one document-1 module bound to an older doc-1 revision; expect `fidelityByDocument[0].status == "ok"`, `fidelityByDocument[1].status == "drift"`.
  - `test_c_inv_document_zero_drifts_document_one_clean` (the control) — the inverse assignment; expect `fidelityByDocument[0].status == "drift"`, `fidelityByDocument[1].status == "ok"`.
  - `test_c_shared_missing_provenance_reports_on_both` (negative control) — a module with unreadable `__provenance__`, otherwise clean; expect `fidelityByDocument[0].status == fidelityByDocument[1].status == "drift"`.
  All three run through the file's existing `_build_env_with_profile_override`, real subprocesses (monkeypatching a module attribute has zero effect on a child process). Confirm C-fwd and C-inv are red against the shipped engine for a structural reason — the shipped fold cannot emit two different statuses for two indices at all — not because an assertion was authored to fail.
- [x] 2.3 GREEN: in `.claude/skills/_core/implementation/engine/implementation_engine.py`, build the claim-key module scope `M_N` — modules whose `__provenance__` declares a non-empty list under `document_vocabulary(N)["claim_key"]` (D4) — from a side structure computed inside `cmd_verify`'s existing module loop (rel path → per-index claim lists), built and folded only under `len(DOCUMENTS) > 1`; under one document the existing inline block runs unedited.
- [x] 2.4 GREEN: derive `stale_N` (modules in `M_N` whose `revision` != `document_names[N]`) and `untested_N` (invariants declared by modules in `M_N` with no `test_<name>`) per index; keep `missing_provenance` and `benchmark_undeclared` as the unchanged whole-tree lists, reported on every index (D4 — stated as shared, not split).
- [x] 2.5 GREEN: derive `unreached_N` — `unreached_modules(...)` filtered to `M_N`'s module paths — per index.
- [x] 2.6 GREEN: rewrite `_extra_document_fidelity_status` to take `(doc_revision, index, conditions, benchmark_undeclared)` instead of four pre-computed shared lists; delete its `document-count-invariant` docstring entirely (the property is gone, not softened) — C2's Phase 3 threat-matrix / success-criterion item.
- [x] 2.7 GREEN: add `"conditions"` (additive, under two documents only) to each `fidelityByDocument[N]`: `{"staleModules": [...], "missingProvenance": [...], "invariantsWithoutTest": [...], "unreachedModules": [...]}`. Confirm the four emitted top-level `fidelity.*` lists (`staleModules`, `missingProvenance`, `invariantsWithoutTest`, `drift`, `benchmark`) keep their current whole-tree meaning and shape, unrenamed and unnested (Cut 3's D7 rule, carried).
- [x] 2.8 VERIFY: run `tests.test_implementation_pair.TwoDocumentDriftControlTests` — all three methods green. Run `python -m unittest tests.seal` — 28 digests byte-identical. Run `python -m unittest tests.pair` — `tests/pair/digests.json` unmoved (both sealed cases run `name`, not `verify`, per M5 — measure).
- [x] 2.9 MUTATE (Y4): in the scope builder, replace `claim_key(index)` with the bare `CLAIM_KEY` scalar; confirm both `test_c_fwd...` and `test_c_inv...` go red; confirm `tests/seal/` survives (single-document branch unreachable); restore.
- [x] 2.10 MUTATE (Y5): in the stale derivation, replace `document_names[index]` with the bare `revision`; confirm C-fwd and C-inv go red; confirm seal survives; restore.
- [x] 2.11 MUTATE (Y6): make `missing_provenance` scope by index (fake a per-document split); confirm `test_c_shared_missing_provenance_reports_on_both` goes red — the only case that catches it; confirm C-fwd/C-inv unaffected; restore.
- [x] 2.12 MUTATE (Y7): revert `fidelityByDocument[N]["conditions"]` to reference the old shared lists; confirm the condition-list assertions in 2.2's methods go red while the status-only assertions stay green; restore.
- [x] 2.13 MEASURE: confirm `L1_EXPECTED_COUNT` (96, `\bproposal\b` over `_core/implementation/engine/`) is unmoved by this phase's engine edits — no new prose in `implementation_engine.py` may spell `proposal` (D9); grep before committing each file change in this phase.

## Phase 3: C2b — Per-document citation and notation threading

- [x] 3.1 RED: in `tests/test_implementation_pair.py`, add a case where document 0 and document 1 declare different `citation_pattern` values (already true after 2.1) and a finding names both documents; assert `finding_impact`'s returned mapping computes document 0's class using document 0's own pattern and document 1's using its own — red against the shipped single `CITATION_RE` (spec `implementation-document-binding` Requirement "A Finding May Name Either Or Both Documents..." scenario "Each named document's citations are matched by its own pattern").
- [x] 3.2 GREEN: give `_impact_class` a fourth parameter, the compiled pattern, defaulting to `CITATION_RE` (existing call path byte-unchanged); compile each index's pattern once at import via `document_vocabulary(N)["citation_pattern"]`, never per call (D7 — rejected: recompiling per finding per document).
- [x] 3.3 GREEN: give `finding_impact` the label→index map from `DOCUMENTS` and pass `document_citation_re(index)` for each named document's label, replacing the shared `CITATION_RE` read at this call site.
- [x] 3.4 GREEN: thread the remaining per-document reader lines (`NOTATION_KEYS`, `LOCUS_KEY`, `REMEDY_LOCUS_KEY`) inside the per-document mapping built in Phase 2, so all 21 reader lines (M1's re-derived count, not 26) read through `document_vocabulary(index)` rather than the module-level scalar.
- [x] 3.5 VERIFY: run 3.1's case green. Run `python -m unittest tests.seal` — 28 digests byte-identical. Re-measure `L1_EXPECTED_COUNT` (D9) — this phase edits `implementation_engine.py` prose most directly; confirm no new occurrence of `proposal`.
- [x] 3.6 MUTATE (Y9): in `_impact_class`, ignore the passed pattern and use the module-level `CITATION_RE` regardless of index; confirm 3.1's case goes red; restore.
- [x] 3.7 MEASURE: `reachable_refusal_codes()` — confirm unmoved (C2 adds no refusal; `verify` reads, it does not gate, per M4).

## Phase 4: C3 — Declare the second document and delete the count-only lock

- [x] 4.1 RED: add `Y8`'s ordering proof first — add `documents[1]` to a *scratch copy* of the shipped profile before deleting the lock, and confirm `SingleDocumentGuaranteeTests` (in `tests/test_implementation_domain_lock.py`) still fires through everything shipped in C1 and C2 (the lock must still exist and still fail on a stray second document at this point in history).
- [x] 4.2 RED: write the replacement lock in `tests/test_implementation_domain_lock.py` (spec `experimental-implementation-skill` Requirement "A Two-Document Guarantee Is Proven By Reading, Not By Counting") — it must fail on a mutation that reverts the fold's per-document derivation (from Phase 2) even though `documents` still has two entries, proving it demonstrates the *read*, not the count. Confirm it is red against the *current* (pre-4.3) state, since `documents[1]` does not exist yet.
- [x] 4.3 GREEN: in `.claude/skills/experimental-implementation/impl_profile.py`, add `documents[1]` — the mathematical proposal — with its own `claim_key`/`locus_key`/`remedy_locus_key`/`notation_keys`/`citation_pattern`, distinct from document 0's `experiments` vocabulary declared today. This is the last write of the change (D8 — the ordering IS the safety argument).
- [x] 4.4 GREEN: delete `SingleDocumentGuaranteeTests` from `tests/test_implementation_domain_lock.py`, replaced entirely by 4.2's lock (spec requirement "A Two-Document Guarantee Is Proven By Reading, Not By Counting" — a count-only check must not stand in as evidence).
- [x] 4.5 GREEN: update `.claude/skills/experimental-implementation/SKILL.md` to describe the second document and what `verify` now answers under two declared documents.
- [x] 4.6 GREEN: add at least one sealed two-document case to `tests/experiments_seal/cases.json` exercising `verify` against the now-two-document shipped profile, and regenerate `tests/experiments_seal/digests.json` — read the diff before accepting it (M5 — deliberate movement, this corpus only, never blind-accepted).
- [x] 4.7 VERIFY: `python -m unittest tests.test_implementation_domain_lock` green (4.2's replacement lock). Run `git diff --exit-code tests/seal/` — still 0 (28 digests untouched by C3). Run the full Python suite: `Ran` grown, `OK (skipped=6)`, `skipped=6` unmoved. Run `npm test` — 595/595 unmoved.
- [x] 4.8 MEASURE: re-confirm `L1_EXPECTED_COUNT` and `L1_EXPECTED_FILES` — 4.3/4.5 touch `impl_profile.py` and `SKILL.md`, both outside `_core/implementation/engine/`'s scan (`ENGINE_DIR`), so this phase is predicted immune; measure, do not infer. Confirm `reachable_refusal_codes()` unmoved.
- [x] 4.9 VERIFY: success-criterion sweep — document 1's status changes when document 1's own text changes with document 0 clean (2.2's `test_c_fwd`), the inverse control present (`test_c_inv`), every per-document leaf mutation-proven (1.13/1.14/2.9-2.12/3.6), both citation-pattern group counts refuse by name (1.14), all 28 digests byte-identical after every slice, no file under `proposal-implementation/` or `proposal-deliberation/` modified (`git diff --exit-code` on both trees), `tests/pair/` and the two-document fixture resolve unchanged, no cross-document verdict emitted, slice table records A → C → {B, D}.

## Key Deferred / Out of Scope (do not touch)

- Slice B (`Data/` per product) and Slice D (cross-document agreement) — B depends on C, record the corrected ordering in the proposal's slice table only.
- Any rename of `proposalDigest` or its `_AUTHORIZATION_BINDING_KEYS` relatives.
- F6, the kit crossing the seam, any cross-document verdict or repair-direction inference, any per-document revision pin.
- `proposal-implementation/**`, `proposal-deliberation/**`, `experimental-deliberation/**`, `_core/deliberation/**` — untouched; assert via `git diff --exit-code` after every slice.
