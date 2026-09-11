# Tasks: The Domain Crosses The Seam (Cut 2)

> **Size note.** Over the 530-word budget, deliberately, for the same reason
> `design.md` gave: sixteen dotted leaves (fifteen field-landed one-at-a-time per D1/D7,
> plus `vocabulary.names` declared at S13 with the locks it serves), each needing its own
> RED case, its own landing step, its own seal run and its own two-way mutation proof — a
> compressed list is a list apply has to re-expand, and re-expansion is exactly the risk
> D7 exists to remove. Citations verified by symbol name against HEAD `ff566fa` before
> writing (`CITATION_RE`, `finding_impact`, `cmd_handoff`, `cmd_admit`, `cmd_verify`,
> `proposals_root`, `unreached_mathematics`, `_wiring_first_publication`,
> `ARMS_UNDECLARED_CONSEQUENCE`, `authored_package_init`, `remedy_compatibility`,
> `_REQUIRED_NESTED`, `_AUTHORIZATION_BINDING_KEYS`, `reachable_refusal_codes`, the six kit
> files, `tests/seal/*`, `tests/test_implementation_profile.py`,
> `tests/proposal-deliberation-domain-profile-lock.test.mjs`, `impl_profile.py`).

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,050 (±150), per proposal Size Forecast |
| 400-line budget risk | High against the 400 default; **Low against this session's 1,400 line budget** (max ~1,200) |
| Chained PRs recommended | No — fits under the cached 1,400-line budget as one PR |
| Suggested split | Single PR. Contingency only: if S13 overruns, fall back to design D7's separable slice — PR 1 = S0–S9 + D4/D6 locks, PR 2 = S10–S13 (Lock B cannot land before S12's comment sweep) |
| Delivery strategy | single-pr |
| Chain strategy | pending (not activated — see contingency) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | S0–S14 in full sequence, one field per commit, seal green after each | PR 1 (single) | `.venv/bin/python -m unittest tests.seal.harness -v` after every S-step | `.venv/bin/python -m unittest discover -s tests` + `npm test`, both pasted before/after | Each S-step reverts independently (D7); whole change is one revert, `tests/seal/` untouched by construction |
| 1a (contingency) | S0–S9 + D4/D6 locks only | PR 1 of 2, if split triggers | same seal command, scoped to S0–S9 | same | Revert PR 1 alone; PR 2 not yet opened |
| 1b (contingency) | S10–S13, Lock B | PR 2 of 2, if split triggers, based on PR 1 | same seal command, scoped to S10–S13 | same | Revert PR 2 alone; PR 1 stands |

---

## Phase 0 — Baseline (S0)

- [ ] 0.1 Run `.venv/bin/python -m unittest discover -s tests` full discovery (not the stale one-file pattern); paste `Ran <n> ... OK (skipped=6)` verbatim.
- [ ] 0.2 Run `npm test`; paste `595/595` verbatim.
- [ ] 0.3 Run the seal (`tests/seal/harness.py` over `tests/seal/cases.json`'s 29 case ids / 28 digests); paste `sha256(tests/seal/digests.json)` and confirm `git diff --exit-code tests/seal/` exits 0.
- [ ] 0.4 Measure L1's baseline: `\bproposal\b` (case-insensitive) occurrence count and sorted file list across `_core/implementation/engine/`. Record the number — **do not carry forward the design's or measurement's §A figures**, which are stale (taken at `a851390`, engine moved since, F3 closed).
- [ ] 0.5 Re-derive the 88/25/4/10 sub-counts from a fresh Lock B-shaped scan (`names` = the M2 seven vocabulary leaves + `formulation`), not from §A.

## Phase 1 — RED first: one `..._INCOMPLETE` case per leaf (S1)

- [ ] 1.1 In `tests/test_implementation_profile.py`, add one refusal case per leaf, each naming the exact dotted leaf (`findings.locus_key`, not `findings`), for all sixteen: `provenance.claim_key`, `provenance.authored_init_sentence`, `findings.locus_key`, `findings.remedy_locus_key`, `findings.notation_keys`, `findings.citation_pattern`, `vocabulary.subject_singular`, `vocabulary.subject_plural`, `vocabulary.subject_singular_es`, `vocabulary.subject_plural_es`, `vocabulary.subject_collective`, `vocabulary.subject_collective_es`, `vocabulary.artifact_noun`, `vocabulary.names`, `documents.directory`, `documents.label`.
- [ ] 1.2 Confirm each case is RED by design (resolver does not yet require these leaves) — do not make it pass yet.

## Phase 2 — Resolver + profile declaration, engine untouched (S2)

- [ ] 2.1 In `.claude/skills/_core/implementation/impl_domain_profile.py`, grow `_REQUIRED_NESTED` (or an equivalent per-leaf structure) with the non-path leaves from Phase 1.
- [ ] 2.2 Give `documents.directory` its own validation tier per M3: required, absolute, **existence not required** — it must NOT join `_REQUIRED_NESTED`'s `..._UNSAFE_PATH` walk (that walk calls `.exists()`, which would refuse at import on any clone with no `proposals/`).
- [ ] 2.3 Threat-matrix RED test (Path traversal via profile, Yes-applicable): a relative `documents.directory` refuses `IMPLEMENTATION_DOMAIN_PROFILE_UNSAFE_PATH`; a non-existent absolute `documents.directory` imports fine.
- [ ] 2.4 Declare all fifteen field-landed leaves (everything but `vocabulary.names`, held for S13) in `.claude/skills/proposal-implementation/impl_profile.py` with today's exact literal values (D1's Interfaces/Contracts block). Engine source untouched.
- [ ] 2.5 Confirm Phase 1's fifteen relevant cases now GREEN (removal-refusal only; `vocabulary.names` case stays red until S13).
- [ ] 2.6 Seal run: 28/28 byte-identical (schema unread by engine yet, so this should be a no-op check).

## Phase 3 — `provenance.claim_key` (S3)

- [ ] 3.1 Edit the five provenance sites (P1–P5 per design D2): `unreached_mathematics`, `benchmark_unfaithfulness`'s module row, `wiring_proposal`'s module row, `cmd_verify`'s module row, `authored_package_init` — read/write key becomes `PROFILE["provenance"]["claim_key"]`, same literal `"equations"`.
- [ ] 3.2 Kit-lock precondition: do not touch `assets/kit/src/module.py` (asserted against later, D4).
- [ ] 3.3 Seal run: 28/28 byte-identical. Any movement → revert this step only (D7 rollback boundary), do not proceed.

## Phase 4 — `provenance.authored_init_sentence` + `vocabulary.artifact_noun` (S4, D3)

- [ ] 4.1 In `authored_package_init`, replace the hardcoded two-line sentence with `PROFILE["provenance"]["authored_init_sentence"]`, interpolating `PROFILE["vocabulary"]["artifact_noun"]` for `"{name} formulation"`. One step, one output (D3).
- [ ] 4.2 Threat-matrix RED test (Filesystem writes, Yes-bounded): assert `authored_package_init` writes only the profile-supplied sentence into the target's `src/<Package>/__init__.py` — bounded to that string, not the file (D3's rejected "profile-supply the whole `__init__.py` body" option must stay rejected).
- [ ] 4.3 Seal run: 28/28 byte-identical; `materialize` case bytes unchanged (D1 predicted mover).

## Phase 5 — `findings.locus_key` (S5)

- [ ] 5.1 Edit `remedy_compatibility`'s `for field in (...)` loop, `cmd_admit`'s verdict loop, `cmd_handoff`'s item builder, `cmd_verify`'s audit block to read `PROFILE["findings"]["locus_key"]`.
- [ ] 5.2 Seal run: 28/28 byte-identical.

## Phase 6 — `findings.remedy_locus_key` (S6)

- [ ] 6.1 Edit `finding_impact`, `remedy_compatibility`, `cmd_admit`, `cmd_handoff` (including its `selectedEntryId` branch) to read `PROFILE["findings"]["remedy_locus_key"]`.
- [ ] 6.2 Seal run: 28/28 byte-identical.

## Phase 7 — `findings.notation_keys` (S7)

- [ ] 7.1 Edit `finding_impact`'s returned dict, `cmd_handoff`'s item builder, `remedy_compatibility`'s return, `cmd_verify`'s audit block to read `PROFILE["findings"]["notation_keys"]` (`locus`/`remedyLocus`/`unknown`).
- [ ] 7.2 Seal run: 28/28 byte-identical.

## Phase 8 — `findings.citation_pattern` (S8, M1 — the eleventh field)

- [ ] 8.1 Move `CITATION_RE`'s pattern string into `PROFILE["findings"]["citation_pattern"]`; `finding_impact` compiles it from the profile. `DISPLAY_BLOCK_RE`/`TAG_RE` stay untouched (spell no domain word; `compose`/M1 stays out of scope).
- [ ] 8.2 Seal run: 28/28 byte-identical; `handoff-e1` unchanged (D1 predicted mover).

## Phase 9 — `documents.directory` + `documents.label` (S9, M3)

- [ ] 9.1 Edit `proposals_root()`, `revision_source`, `revision_discovery` and the five hardcoded-path refusals to read `PROFILE["documents"]["directory"]` / `PROFILE["documents"]["label"]`.
- [ ] 9.2 Threat-matrix RED test (Environment-variable routing, Yes-applicable): `IMPLEMENTATION_PROPOSALS` override still wins over `documents.directory`, for every one of the five refusal cases.
- [ ] 9.3 Seal run: 28/28 byte-identical; `admit-e0`, `handoff-e0` and the other three refusal cases unchanged.

## Phase 10 — `vocabulary.*` subject leaves, one sub-step per leaf (S10)

- [ ] 10.1 `vocabulary.subject_singular` → `ARMS_UNDECLARED_CONSEQUENCE`. Seal 28/28.
- [ ] 10.2 `vocabulary.subject_plural` → `cmd_admit`'s verdict reason. Seal 28/28.
- [ ] 10.3 `vocabulary.subject_singular_es` → `cmd_handoff`'s `remedy-locus-missing` and `structural-reach` reasons. Seal 28/28.
- [ ] 10.4 `vocabulary.subject_plural_es` → `cmd_handoff`'s `structural-reach` reason and `ECUACIONES A TOCAR:` prompt line. Seal 28/28.
- [ ] 10.5 `vocabulary.subject_collective` → `_wiring_first_publication`. Seal 28/28.
- [ ] 10.6 `vocabulary.subject_collective_es` → `cmd_handoff`'s `remedy-text-missing` reason. Seal 28/28.
- [ ] 10.7 M2 doctrine tension recorded unresolved in a code comment at the Spanish sub-steps (10.3/10.4/10.6): moving the hardcoded Spanish is correct for extraction and hardens `SKILL.md`'s *"Speak the language the user is speaking"* violation into a contract shape. Do not translate. Do not fix here.
- [ ] 10.8 Each sub-step is independently revertible (D7 rollback boundary is per sub-step, not per phase).

## Phase 11 — Four identifier renames, driven by Lock B's failure report (S11)

- [ ] 11.1 Do not rename by list-written-here. First write Lock B (Phase 13) enough to produce its failure report, then rename exactly what it names — `unreached_mathematics` and its three siblings — to what they do.
- [ ] 11.2 Confirm wire keys `unreachedModules`/`armsReached` (produced by `unreached_mathematics`) carry no domain word and do **not** change — no digest moves with this rename (design D5).
- [ ] 11.3 Update every call site, including `tests/test_proposal_implementation.py`, to the renamed identifiers.
- [ ] 11.4 Seal run: 28/28 byte-identical.

## Phase 12 — The comment/docstring sweep (S12)

- [ ] 12.1 Sweep the comment/docstring lines carrying declared `vocabulary.names` words, using the re-derived count from Phase 0.5 as the worklist, not the stale §A figure.
- [ ] 12.2 Assert by seal run, not by inspection, that no executable text was touched.
- [ ] 12.3 Seal run: 28/28 byte-identical.

## Phase 13 — The locks (S13)

- [ ] 13.1 Declare `vocabulary.names` in `impl_profile.py`: `["equation", "equations", "ecuación", "ecuaciones", "mathematics", "matemática", "formulation"]` — from the measurement's own token list, never from what happens to pass.
- [ ] 13.2 Create `tests/test_implementation_domain_lock.py`. Lock A: `discover_profiles()` globs `.claude/skills/*/impl_profile.py`, skips `_core`; asserts at least one profile found, `names` non-empty, no declared leaf blank, every `names` word appears in that profile's own source.
- [ ] 13.3 Lock B: scan every `*.py` under `_core/implementation/engine/`, whole text; fail if any `vocabulary.names` word appears. Word-boundary, case-insensitive.
- [ ] 13.4 Kit agreement lock (D4), six assertions, each with a non-empty extraction guard: (1) `module.py`'s `__provenance__` declares exactly `{"revision", "sections", claim_key, "invariants"}`; (2) `module.py`'s rules docstring names both; (3) `src_benchmark/__init__.py`'s `arms` comment example spells `"sections"`; (4) `tests/findings.py`'s commented keys equal `locus_key`/`remedy_locus_key`; (5) `tests/test_audit.py`'s executable subscript equals `remedy_locus_key`; (6) `nb/verification.ipynb`'s executable subscript equals `claim_key`. No kit file is edited.
- [ ] 13.5 D6 exclusion, three layers: **L1** — `\bproposal\b` occurrence count + sorted file list across `engine/` equals Phase 0.4's measured baseline. **L2** — each of `proposalDigest`, `GATE_PROPOSAL_*`, `_proposal_digest`, `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`, `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`, `_campaign_identity`, `_load_remote_execution_*` still resolves, spelled exactly. **L3** — `"proposalDigest" in impl._AUTHORIZATION_BINDING_KEYS`.
- [ ] 13.6 Record `wiring_proposal`/`_wiring_first_publication` as third-sense `proposal` residue (a draft suggestion) — covered by L1, not L2, not to be "fixed" into `documents.label`.
- [ ] 13.7 Re-assert `reachable_refusal_codes()`'s pin; move it only if a refusal was genuinely added, record the new number.
- [ ] 13.8 Do not implement TS C-3's derived-denylist layer (M5) — record the deferral reason (empty "others" set with one profile) in the same test file; do not write a `skipTest` for it (would move the pinned `OK (skipped=6)`).
- [ ] 13.9 Do not touch `tests/proposal-deliberation-domain-profile-lock.test.mjs` — read for structure only.
- [ ] 13.10 Seal run: 28/28 byte-identical.

## Phase 14 — Mutation proof, both directions, per leaf (S14/D8)

- [ ] 14.1 For each of the sixteen leaves: **removal** — delete from `impl_profile.py`, fresh `importlib` load with controlled `os.environ`, assert `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` names that exact leaf.
- [ ] 14.2 For each leaf with a predicted mover in D1's table: **change** — real reverted edit to `impl_profile.py`, run the seal (subprocess, never a monkeypatch — patching `impl_domain_profile.PROFILE` has zero effect on a subprocess), assert the named digest(s) move and no others do.
- [ ] 14.3 Anchor discipline both directions: before each mutation, assert the anchor count for the old spelling is 1 and the new spelling is 0; after the edit, 0/1; after revert, 1/0 again. An anchor that matched is not a mutation that ran.
- [ ] 14.4 Measure before strengthening: if a predicted mover does not move, record it explicitly as a zero-mover with no seal instrument — its removal-refusal and lock coverage are its whole defence. Do not paper over it; do not hunt for a test that would have moved it.
- [ ] 14.5 Lock B honesty: plant a declared `names` word anywhere in `engine/` (including a comment); Lock B must redden, naming the file and word; revert; green.
- [ ] 14.6 Kit lock honesty: change `module.py`'s `"equations"` key in a **scratch copy**, not the shipped file; the kit lock must redden; discard the scratch copy.
- [ ] 14.7 `git diff --exit-code tests/seal/` exits 0 at the end of this phase.

## Phase 15 — Non-interference & close-out

- [ ] 15.1 Re-run `.venv/bin/python -m unittest discover -s tests`; paste `Ran <n> ... OK (skipped=6)`. `Ran` may grow; `OK` and `skipped=6` must not move.
- [ ] 15.2 Re-run `npm test`; paste `595/595` exactly — any other number is the sister-skill bar failing.
- [ ] 15.3 Confirm `proposal-deliberation/` and `_core/deliberation/` are not written to (diff scope check).
- [ ] 15.4 Final seal check: `sha256(tests/seal/digests.json)` unchanged from Phase 0.3; `git diff --exit-code tests/seal/` exits 0.
- [ ] 15.5 Confirm all five §"What Breaks" Products rows stay true by inspection: targets' `__provenance__`/`findings.py` under old spelling still valid (same literal), `__benchmark__["arms"]` untouched, existing `__init__.py` sentences untouched, `.implementation/position.jsonl` authorizations untouched, `admissibility.json` untouched.
- [ ] 15.6 Commit per-phase with conventional commit messages, no AI attribution; one PR.
