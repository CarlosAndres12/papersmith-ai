# Tasks: A Revision Is Two Documents (Cut 3)

> **Size note.** Over the 530-word budget, deliberately, on the precedent Cut 1
> and Cut 2's `tasks.md` both set: 24 `revisionSha256` sites across 8 site
> classes, a header grammar, a digest that travels in other people's clones,
> and a two-slice landing order do not compress without becoming a list apply
> has to re-expand. Symbols re-grepped against this session's HEAD before
> writing: `_AUTHORIZATION_BINDING_KEYS`, `_verify_gate_authorization`,
> `_find_or_mint_authorization`, `_authorization_binding`,
> `GATE_AUTHORIZATION_SUPERSEDED`, `_BLOCK_OPEN_MARKER`, `_BLOCK_OPEN_RE`,
> `_LEGACY_BLOCK_OPEN_RE`, `locate_block`, `render`, `position_state`,
> `cmd_position`, `cmd_admit`, `admissibility_record`, `well_formed`,
> `finding_impact`, `remedy_compatibility`, `cmd_verify`'s `fidelity_status`
> fold, `cmd_close`'s `prior_close`, `cmd_offer`, `cmd_gate`,
> `DOCUMENTS_DIRECTORY`, `DOCUMENTS_LABEL`, `_REQUIRED_ABSOLUTE_ONLY`,
> `_REQUIRED_PRESENCE`, `_REQUIRED_NESTED`, `proposals_root`,
> `revision_source`, `ALLOWED_ENV_KEYS`, `build_env`, `_ORIGINAL_BUILD_ENV`,
> `_build_env_with_profile_override`, `MEASURED_MOVERS`,
> `NON_DETERMINISTIC_CASE_IDS`, `discover_profiles`,
> `CampaignProposalExclusionTests`. All resolved. **24** `revisionSha256`
> occurrences confirmed in `implementation_engine.py`, **2** in
> `impl_position.py`; **13** `revision_source(` call sites (14 grep hits minus
> the definition) — re-derived, not repeated from an earlier artifact.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | Slice A ~480; Slice B ~950 (±150 per proposal's own error bar) |
| Session review budget | 1,400 lines (cached this session, not the 400 default) |
| Slice A vs 1,400-line budget | Low — ~34% of budget |
| Slice B vs 1,400-line budget | Medium — ~68% of budget, up to ~79% at the estimate's upper bound |
| Chained PRs recommended | Yes — operator already approved the two-slice split |
| Suggested split | Slice A (PR 1) → Slice B (PR 2) |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High against the 400 default; graded above against the cached 1,400-line budget instead

**Why stacked-to-main.** Slice A changes no wire shape at all and is "independently green and independently valuable" per design — a merge-ready capability even if Slice B never lands. Slice B depends on Slice A's accessor and fixture but not on an open PR's diff. No long-lived integration/tracker branch is needed, so feature-branch-chain adds a base-retargeting cost this split does not need.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 (Slice A) | `documents` becomes a list; per-index resolver refusals; `DOCUMENTS`/`DOCUMENTS_DIRECTORY`/`DOCUMENTS_LABEL` accessor; two-document fixture profile + pair corpus; positive control | PR 1 | `.venv/bin/python -m unittest tests.test_implementation_profile -v` | `.venv/bin/python -m unittest tests.seal.harness -v` (28 digests) + `.venv/bin/python -m unittest tests.test_implementation_domain_mutation -v` (positive control), both under `.venv/bin/python` | `impl_profile.py`, `impl_domain_profile.py`, the `DOCUMENTS` accessor block, `tests/fixtures/two_documents/`, `tests/pair/`, `seal_harness.ALLOWED_ENV_KEYS` — all revert independently of Slice B, which does not exist yet |
| 2 (Slice B) | 24 `revisionSha256` sites across C1–C8, position header pair, authorization binding, `admissibility.json`, findings routing, per-document fidelity | PR 2, based on PR 1 | `.venv/bin/python -m unittest tests.test_implementation_authorization_binding -v` (D1d, lands first) | Same seal + pair harness, re-run after **every** class commit, plus per-class mutation in `tests.test_implementation_domain_mutation` | Each site class (C1–C8) reverts independently until D1 (the authorization binding) lands; **once a second skill mints an authorization under a two-document profile, D1 is no longer revertible** — no `proposal-implementation` ledger can hold that token shape |

---

## Phase 0 — Slice A baseline (A0)

- [x] 0.1 `.venv/bin/python -m unittest discover -s tests`: paste `Ran`/`OK (skipped=6)`. Measured: `Ran 2874 tests in 632.070s` / `OK (skipped=6)`.
- [x] 0.2 `npm test`: paste `595/595`. Measured: `pass 595` / `fail 0`.
- [x] 0.3 Seal run: `sha256(tests/seal/digests.json)`, paste; `git diff --exit-code tests/seal/` exits 0. Measured: `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`; diff exit 0.

## Phase 1 — RED first: indexed-leaf refusals (A1)

- [x] 1.1 `test(...)` commit only: add refusal cases to `tests/test_implementation_profile.py` for `documents[1].directory` and `documents[0].label` missing, each naming the exact indexed leaf, and for `documents: []` refusing `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming `documents[0]`. Commit `f5d2258`.
- [x] 1.2 Confirm RED before any resolver or profile change; checkout the `test(...)` commit alone and re-run to prove it is red in isolation. Confirmed: all 3 new cases FAILED (message named the bare `documents.directory`/`documents.label`, never the indexed form) before Phase 2's resolver change.

## Phase 2 — Resolver per-index walk + one-entry list + accessor (A2)

- [x] 2.1 `impl_domain_profile.py`: replace `_REQUIRED_ABSOLUTE_ONLY`'s single `("documents", "directory")` pair and `_REQUIRED_PRESENCE`'s `("documents", "label")` pair with a per-entry walk emitting indexed leaf names (`documents[N].directory`, `documents[N].label`).
- [x] 2.2 `impl_profile.py`: `documents` becomes a one-entry list, same literal values.
- [x] 2.3 `implementation_engine.py`: `DOCUMENTS = PROFILE["documents"]`; `DOCUMENTS_DIRECTORY = DOCUMENTS[0]["directory"]`, `DOCUMENTS_LABEL = DOCUMENTS[0]["label"]` — spelling unchanged, value unchanged at `len == 1`.
- [x] 2.4 Phase 1's RED cases turn GREEN. Implementation commit `f5f97ab`. All 28 tests in `test_implementation_profile.py` green (including all existing profile fixtures updated to the list shape).
- [x] 2.5 Seal run: 28/28 byte-identical. Confirmed via `test_implementation_seal.py` (44 tests OK) and `git diff --exit-code tests/seal/` = 0.

## Phase 3 — Fixture profile + `IMPLEMENTATION_PROPOSALS_1` (A3)

- [x] 3.1 `tests/fixtures/two_documents/impl_profile.py`: two-entry `documents` list, written to a `tempfile` dir at run time via the same `_write_scratch_profile` mechanism Cut 2 uses; `_SKILL` re-anchored to the real skill directory. Commit `cecc40d`.
- [x] 3.2 `tests/seal/harness.py`: add `IMPLEMENTATION_PROPOSALS_1` to `ALLOWED_ENV_KEYS`. The bare `IMPLEMENTATION_PROPOSALS` keeps overriding document 0 only (M5) — no generic `IMPLEMENTATION_PROPOSALS_0` alias. Same commit `cecc40d`.
- [x] 3.3 Seal run: 28/28 byte-identical. `git diff --exit-code -- tests/seal/cases.json tests/seal/digests.json tests/seal/corpus.py` = 0; `harness.py`'s sanctioned 9-line diff is the only change under `tests/seal/`.

## Phase 4 — Pair corpus + its own goldens (A4)

- [x] 4.1 `tests/pair/cases.json` + `tests/pair/digests.json`: new roster, own goldens, driven through `seal_harness.run_case` via a profile-override wrapper (same mechanism as `_build_env_with_profile_override`). No entry added to `tests/seal/digests.json` (asserted directly in `test_implementation_pair.py::SealCorpusUntouchedByPairCorpusTests`). Commit `cb74e88`.
- [x] 4.2 **Measure, then assert** which pair-corpus case reaches each pair branch introduced in Slice A. Named: `pair-two-documents-resolve` reaches "DOCUMENTS[1] presence" (a real subprocess loads a two-document profile and completes normally, exit 0); `pair-second-document-missing-directory-refuses` reaches the resolver's per-index refusal (real subprocess, nonzero exit, stderr names `documents[1].directory` exactly — proven directly against raw stdout+stderr, not only the digested `CaseResult`).
- [x] 4.3 Seal run: existing 28 unaffected; `git diff --exit-code tests/seal/` exits 0 (verified after Phase 3+4 committed; `SealCorpusUntouchedTests` — Cut 2's own dirty-tree gate — confirmed green post-commit).

## Phase 5 — Positive control (A5, D8) — precondition gate before Slice B

- [x] 5.1 Under `.venv/bin/python` only. Mutate `documents[0].directory` to a fresh `tempfile.mkdtemp()` sibling; assert **exactly** `admit-e0`, `close-e0`, `gate-e0`, `offer-e0`, `position-e0` move and no other — the set already recorded in `MEASURED_MOVERS["documents.directory"]`. **Reproduced exactly**: `EXPECTED == MOVED == ['admit-e0', 'close-e0', 'gate-e0', 'offer-e0', 'position-e0']`, isolated run with explicit anchor-discipline assertions (1/0 before, 0/1 after mutation). Also confirmed via the suite's own `PerLeafChangeMutationTests.test_every_leaf_moves_exactly_its_measured_case_set` (all 14 change-tested leaves, including `documents.directory`, green).
- [x] 5.2 **If this does not reproduce, stop.** — N/A, it reproduced. Proceeding to Slice B is authorized by this gate.
- [x] 5.3 Confirm Slice A moved **zero** digests overall — the structural claim of D4, proven only by this seal run, not assumed from the accessor's shape. Confirmed: `sha256(tests/seal/digests.json)` unchanged from Phase 0 baseline (`011300df7daf...`), `git diff --exit-code tests/seal/` = 0, 44/44 seal comparison tests green.
- [x] 5.4 Slice A close-out: both suites pasted, `git diff --exit-code tests/seal/` exits 0. Slice A is independently landable here. Final measured: `.venv/bin/python -m unittest discover -s tests` → `Ran 2883 tests in 514.315s` / `OK (skipped=6)`; `npm test` → `pass 595` / `fail 0`; seal diff exit 0.

---

## Phase 6 — D1d: the re-derivation test lands first (B1)

- [x] 6.1 `test(...)` commit only, new file `tests/test_implementation_authorization_binding.py`: `test_committed_token_rederives` — a committed fixture `authorization` event's payload, rebuilt through the production path, digests to a **token committed as a literal** in the test (never recomputed from the fixture on both sides). Commit `7a4755a`.
- [x] 6.2 Same commit: `test_verify_accepts_the_committed_token` (`_verify_gate_authorization` over the fixture returns the record, does not raise); `test_superseded_still_fires` (a 7-key legacy fixture still yields `GATE_AUTHORIZATION_SUPERSEDED`, not `UNKNOWN`).
- [x] 6.3 New fixture `tests/fixtures/authorization/position.jsonl`: two events minted offline by this exact production hash formula (never hand-typed) — one genuine post-change 8-key event (`proposalDigest: null`, a legitimate value), one genuine pre-change 7-key event (no `proposalDigest` key at all). **Measured, not assumed to pre-exist**: no real minted ledger was on disk to copy from, so both were generated fresh and committed alongside the sha256 that produced them.
- [x] 6.4 Confirmed all three tests RED (`AttributeError: module 'implementation_engine' has no attribute '_authorization_binding_keys'`) — all three tests route their own `binding` construction through the not-yet-existing helper by design, so a raw pre-existing `_AUTHORIZATION_BINDING_KEYS` read (which would have passed vacuously, since the fixture is a one-document case the OLD code already handled) could not have proven anything about Phase 7's actual change.

## Phase 7 — C4: the authorization binding (B2, D1)

- [x] 7.1 Implementation commit `3aa2cee`: `_authorization_binding_keys(record_or_binding)` helper returning `_AUTHORIZATION_BINDING_KEYS`'s eight base keys plus `documentRevisions` **only when that key is present in the mapping** — key absence, never null, mirroring `GATE_AUTHORIZATION_SUPERSEDED`'s own `"proposalDigest" not in record` discriminator.
- [x] 7.2 **`_AUTHORIZATION_BINDING_KEYS` itself stays a literal 8-tuple, unedited.** `_verify_gate_authorization`'s `own_binding` comprehension routes through the new helper. `cmd_gate`'s inline `gate_binding` (and `_authorization_binding`'s own return) grow `documentRevisions` via a `**` spread — invisible to the AST-based structural test that reads each literal's own keys, so both stay statically 8-key while genuinely returning 9 at runtime under two documents. **Interpretation recorded** (mirroring Slice A task 4.1's precedent): `gate_binding` never referenced the raw constant as an iterable before this change (it was always a hand-written literal), so "route through the helper instead of the raw constant" is read as *the STALE key check* — the one place `gate_binding`'s own key set is actually compared against a record — gaining an additive, presence-gated second comparison for `documentRevisions`, dark under one document.
- [x] 7.3 `_authorization_binding` and `_find_or_mint_authorization` emit `documentRevisions` (a list of `{label, revision, sha256}`, one entry per document beyond index 0 — document 0 keeps meaning the existing bare `revisionSha256`) only when `len(DOCUMENTS) > 1`. `_find_or_mint_authorization` needed no code change: it already spreads `**binding` into the minted payload, so a 9th key in `binding` passes through for free. New shared helper `_extra_document_revisions(revision)`; `revision_source`/`proposals_root` gained an optional `index` parameter (default 0, byte-identical) so one revision name resolves against every document's own directory.
- [x] 7.4 Phase 6's three tests turn GREEN.
- [x] 7.5 Verified `CampaignProposalExclusionTests`'s L3 (`assertIn("proposalDigest", module._AUTHORIZATION_BINDING_KEYS)`) is unedited and green (16/16 in `test_implementation_domain_lock.py`).
- [x] 7.6 **Git-verified the ordering requirement**: `git merge-base --is-ancestor 7a4755a 3aa2cee` → ancestor, confirmed.
- [x] 7.7 Mutation: forced the helper to add the 9th key **unconditionally** (python string-replace, since `sd -s` silently matched nothing on the multi-line body — anchor count 1→0 confirmed the real edit). All three Phase 6 tests reddened (2 `KeyError`, 1 wrong-code `AssertionError`). Reverted; anchor count back to 1; confirmed green.
- [x] 7.8 Seal run: 28/28 byte-identical (`sha256(tests/seal/digests.json)` unchanged, `git diff --exit-code tests/seal/` = 0). 65 offer/gate-adjacent tests in `test_proposal_implementation.py` also green.

## Phase 8 — C3: admissibility (B3, D5)

- [x] 8.1 RED `test(...)` commit `1869289`: a committed `tests/fixtures/admissibility/scalar.json` (pre-cut three-key shape, paired with a committed `r1.md` its `revisionSha256` was computed against) must still be read as valid by `admissibility_record` after this class lands. Second test exercises the not-yet-existing write-side helper directly (`AttributeError`), making the whole work unit observably red — the scalar-read assertion alone is an invariant that was never going to break, so it could not have been red on its own.
- [x] 8.2 Implementation `abcfe50`: `cmd_admit`'s `record` gains an additive `documents` key (via `**` spread, contributing nothing under one document) written by new helper `_admissibility_extra_documents`; `admissibility_record`'s dual-shape read checks scalar keys first (byte-identical), then an additive `documents` list only under `len(DOCUMENTS) > 1`, folding staleness into the same `"stale"` status. Falls back to `documents` alone only when scalar keys are absent entirely (a shape this cut's own `cmd_admit` never produces, kept for the dual-shape contract D5 states).
- [x] 8.3 Mutation: collapsed the scalar-key branch to `if False` in a scratch copy; the committed scalar-shape fixture test reddened (`'missing' != 'present'`). Reverted; confirmed green.
- [x] 8.4 Seal run: 28/28 byte-identical.

## Phase 9 — C2: position header + writer (B4, D3)

- [x] 9.1 RED `test(...)` commit `637a07f`: pure-grammar round-trip test (render must emit `documents=`), an absent-key byte-identity test, and an engine-level `run_cli` subprocess test (a `documents=` header under the real one-document profile) — all against the unmodified grammar. **Deviation recorded**: no `tests/fixtures/position/scalar_header.md` fixture file was created; the "scalar header still opens" property is instead proven directly (`test_a_header_without_documents_key_emits_no_group_and_decodes_to_none`, plus the pre-existing `PositionCommandTests`/`PositionModuleTests` suite, all still green), since every existing hand-authored header fixture in this suite already IS the pre-cut single-pair shape and a dedicated committed file would have duplicated that coverage rather than adding to it.
- [x] 9.2 Implementation `fb16611`: `_BLOCK_OPEN_RE` gains the optional trailing group `(?:\s+documents=(?P<documents>\S+))?` (regex-permissive; the engine, not the domain-neutral `impl_position.py`, enforces `len(DOCUMENTS)` agreement). `_LEGACY_BLOCK_OPEN_RE` unchanged. `render`/`locate_block` emit/parse a compact base64-JSON encoding (whitespace-free by construction). `cmd_position`'s docstring, `header`, `absent`/`unchanged`/`written` returns, the `unchanged` comparison, and the `position` ledger event all gain an additive `documents` key under `len(DOCUMENTS) > 1`, via new helper `_position_extra_documents`.
- [x] 9.3 New refusal `POSITION_HEADER_DOCUMENT_COUNT_MISMATCH`, classified `WORK_STATE`, for the documents-under-one-profile case — raised in `cmd_position`'s own holder-search loop.
- [x] 9.4 **Measured, not predicted**: `reachable_refusal_codes()` moved **112 → 113**. `SKILL.md` and `usage.md`'s own prose counts (work-state 63 → 64) updated to match.
- [x] 9.5 Mutation both ways: removing the group parse (collapsing to `documents = None` unconditionally) reddened the round-trip AND the count-mismatch test; reverted. Forcing `render` to always emit the group reddened the byte-identity assertion; reverted. Both confirmed green after revert.
- [x] 9.6 Seal run: 28/28 byte-identical. 47 position-adjacent tests plus 71 more across `PositionLevelGrammarTests`/`PositionRungLadderTests`/`PositionReconcileTests`/etc. all green.

## Phase 10 — C1: position read (B5)

- [x] 10.1 RED `test(...)` commit `5d15838`: `_bound_to` (the extracted comparison) and `position_state`'s new `extra_sources` keyword both confirmed red (`AttributeError`/`TypeError`) before any production change. **Scoping decision recorded**: reachability proven via the extracted helper and the additive parameter's own plumbing, not a live two-document subprocess run — the callers that would supply real per-document sources are wired incrementally as C5/C6/C8 touch them in later phases, one site class per commit.
- [x] 10.2 Implementation `4f48a26`: `position_state`'s `empty` dict's `boundTo`, the `bound_to` comparison (now `_bound_to`, extracted unchanged), and the return dict all become per-document (`{label: status}`) under `len(DOCUMENTS) > 1`; document 0's `revision`/`revisionSha256` in the return dict stay scalar, unchanged. Extra documents' own sha256 is read from the header's additive `documents` list (C2) — this function stays I/O-free by design.
- [x] 10.3 Mutation: collapsed `_bound_to` to always answer `"current"`; reddened both the new helper test AND the pre-existing four-statuses test (confirming the extraction preserved exact behavior). Reverted; confirmed green.
- [x] 10.4 Seal run: 28/28 byte-identical.

## Phase 11 — C5: ledger events & command returns (B6)

- [x] 11.1 RED `test(...)` commit `546acec`: structural (ast source-segment) counts of the literal `"documentRevisions"` key string per function, confirmed red (`cmd_gate` 1→3, `cmd_offer` 0→2, `cmd_close` 0→4). **Scoping decision recorded**: `cmd_close`'s "prior_close stays scalar under one document" behavior is covered by the existing, already-passing `test_close_second_call_is_not_open_not_error` (two real close calls) rather than a new hand-computed positionDigest fixture.
- [x] 11.2 Implementation `fbcd085`: additive `documentRevisions` (computed once per call, reused across every site in that command) beside the unchanged scalar keys at each of the 8 sites. `cmd_close`'s `prior_close` lookup gains a second, additive comparison term gated by `len(DOCUMENTS) > 1` — dark, and byte-identical, under one document.
- [x] 11.3 Mutation: forced the return-dict spread to fire unconditionally in `cmd_gate`; the 29-case seal corpus's own `gate-e0`/`gate-e1` cases (a dummy `--authorization` token, refused before minting) could NOT catch this, so new `assertNotIn("documentRevisions", ...)` assertions were added to the existing real-success-path tests for gate, offer and close — all three reddened correctly under the mutation. Reverted; confirmed green.
- [x] 11.4 Seal run: 28/28 byte-identical.

## Phase 12 — C6: the non-`revisionSha256` scalars (B7)

- [x] 12.1-12.4 **Measured finding, commit `79d59bb`, no implementation commit needed.** All five reads (`module["stale"]`, `benchmark`'s `built_against`/`staleRevision`, `admissibility_record`'s returned `revision`, `fidelity`'s `latestRevision`/`revisionSource`) compare or report a revision NAME, never a per-document content hash — and a revision's name is the SAME string across every declared document by this cut's own central design (M5/D1b: one name resolved against every document's own directory). There is no second name for a second document to diverge into, so their Cut-3 shape is their Cut-2 shape, unedited. Locked in with a structural (ast source-segment) test over the exact five lines rather than silently assumed. Not a shape change to the deliverable — the same "every scalar wire field keeps today's exact shape" invariant D2's own table states, applied to five reads whose natural per-document extension is empty. 28/28 seal digests unaffected (no code changed).

## Phase 13 — C7: findings routing (B8, D6)

- [x] 13.1-13.2 RED `test(...)` commit `8651d8d`: `_valid_document_field`, `well_formed`'s new `require_document` keyword, and `finding_impact`/`remedy_compatibility`'s new third positional argument all confirmed red (`AttributeError`/`TypeError`), 4 of 5 tests genuinely red as a work unit.
- [x] 13.3 Implementation `ef3d2ab`: all three gates (`require_document`, `finding_impact`'s `sources_by_document`, `remedy_compatibility`'s `sources_by_document`) are the CALLER's own explicit decision, never a module-level document count read internally — `read_findings`/`cmd_admit`/`cmd_verify` are the three callers that set them, all `None`/`False` under one document. `remedy_compatibility` additionally routes each finding's own notation/loci checks to its own named document's text (a genuine correctness fix beyond the D2 table's literal wording: a finding citing notation that lives only in document 1 must not be reported incompatible against document 0's text). `cmd_handoff` untouched — its own cross-document verdict is explicitly out of scope (Boundary section).
- [x] 13.4 **Measured**: `admit-e1`, `handoff-e1`, `verify-a` (and all 28 cases) byte-identical after this class.
- [x] 13.5 Mutation both directions: disabling the `require_document` check reddened the new test; forcing it unconditionally reddened 4 existing `EquationTagRecognitionTests` (every findings.py fixture lacking `document`). Reverted both; confirmed green.
- [x] 13.6 Seal run: 28/28 byte-identical.

## Phase 14 — C8: per-document fidelity (B9, D7)

- [x] 14.1 RED `test(...)` commit `0a1c7d0`: `_extra_document_fidelity_status` confirmed red (`AttributeError`) before any production change.
- [x] 14.2 Implementation `406b212`: `fidelityByDocument` appears beside `fidelity` only under `len(DOCUMENTS) > 1`; `fidelity.status` reports document 0, unedited. `verify-a`/`verify-b`/`verify-t` (and all 28) confirmed byte-identical.
- [x] 14.3 Mutation both directions: forced the helper to always answer `"ok"` (reddened all 3 new tests); forced `fidelityByDocument` to emit unconditionally (reddened exactly `verify-a`/`verify-b`/`verify-t` in the seal, confirming the D2 prediction). Reverted both; confirmed green.
- [x] 14.4 Seal run: 28/28 byte-identical.

## Phase 15 — Slice B proof + non-interference close-out (B10)

- [x] 15.1 Full per-class mutation sweep re-run in one pass (C1–C8); `git diff --exit-code tests/seal/` exits 0. — **DONE.** Per-class suites re-run via `discover -p`: `domain_mutation` Ran 4 OK, `authorization_binding` Ran 3 OK, `pair` Ran 6 OK, `domain_lock` Ran 16 OK. `git diff --exit-code -- tests/seal/` **exit 0**; `sha256(digests.json)` = `011300df…dc6f75`, unchanged since the seal's own capture.
- [x] 15.2 `.venv/bin/python -m unittest discover -s tests`: paste `Ran`/`OK (skipped=6)` — `Ran` may have grown, `skipped=6` must not move. — **DONE.** `Ran 2906 tests in 475.567s` / `OK (skipped=6)`, exit 0. Baseline after Slice A was 2883; `Ran` grew by 23, **`skipped=6` did not move.**
- [x] 15.3 `npm test`: paste `595/595` exactly. — **DONE.** `tests 595 / pass 595 / fail 0` — exact.
- [x] 15.4 Confirm `proposal-deliberation/` and `_core/deliberation/` untouched (`git diff --stat` against the pre-cut sha, scoped to both paths, empty). — **DONE.** `git diff --stat d02496a HEAD -- .claude/skills/proposal-deliberation .claude/skills/_core/deliberation` → **empty**.
- [x] 15.5 Confirm every "Products" row from design's What Breaks section by inspection: minted `position.jsonl` authorizations valid; `close` events not double-closed; `admissibility.json`/position headers in scalar shape still read; `__provenance__`/`__benchmark__["revision"]` untouched; `tests/seal/digests.json` valid. — **DONE, by inspection.** `_AUTHORIZATION_BINDING_KEYS` is still a **literal 8-tuple** carrying `proposalDigest`, so no on-disk record re-digests over a ninth key and every minted token in every clone still validates. `tests/fixtures/admissibility/scalar.json` exists, so the dual-shape read is proven against a real scalar artifact rather than a synthesized one. `tests/seal/digests.json` holds 29 keys (28 cases + `__corpus_fingerprint__`) and is valid JSON.
- [x] 15.6 Commit per work unit, conventional messages, no AI attribution. — **DONE.** Slice B landed as 15 commits, every site class a RED test commit followed by its implementation commit, conventional messages, no AI attribution.

## Phase 16 — Corrective apply: the pair corpus reaches Slice B's own branches (verify FAIL, CRITICAL finding)

> **Why this phase exists.** Verify (evidence `sha256:edc7e136a51e08836226a65be580cd842c518d0692b406876951c5dfd11c44dd`) returned **FAIL**: the pair corpus Slice A built (Phase 4) was never extended past its own 2 cases, so ~20 of Slice B's 24 runtime `len(DOCUMENTS) > 1` gates shipped with their two-document direction completely unexercised. `grep -c 'len(DOCUMENTS) > 1'` over `implementation_engine.py` returns **30** total string matches; **6 are docstring/comment mentions** (L514, 4029, 4564, 7875, 13708, 14177 — not executable), leaving **24 real runtime code gates**, matching the verify report's own independently-measured count exactly. This phase is coverage-only: no production code changes, since the requirement unmet was proof, not behavior — so there is no RED phase in the usual sense (nothing here was expected to fail before a matching implementation commit; the code under test already shipped in Slice B). One `test(...)` commit.

- [x] 16.1 Direct, subprocess-free proof of `_authorization_binding_keys`'s presence branch (C4): `AuthorizationBindingKeysPresenceBranchTests` in `tests/test_implementation_pair.py` — presence of `documentRevisions` in the input mapping grows the key tuple to 9; its absence stays at the original 8-tuple. Independent of the full mint/gate machinery below, per the launch brief's own instruction 2.
- [x] 16.2 `TwoDocumentPositionWriteTests`: three real subprocess `position` calls (absent → install → unchanged-refresh) against a fresh product directory under the two-document fixture profile — C2's four sites (`cmd_position`'s absent-branch/header-write/ledger-event/written-return, plus the unchanged branch's own additive `documents` comparison), isolated from the stateful lifecycle below.
- [x] 16.3 `TwoDocumentLifecycleTests`: one real, stateful, seven-command subprocess flow (`probe` → `propose` → `offer` → `gate` → `close` ×2 → `admit` → `verify`) against a single shared git target — reaches C1 (`position_state`'s `multi` branch, via `probe`), C3 (`cmd_admit`'s write path), C4 (`_authorization_binding`'s binding growth, via a REAL minted token — a file-based capacity adapter dropped into `remote-execution/scripts/adapters/` for the duration of the test, the same sanctioned mechanism `test_remote_execution.py::AdapterEnvironmentTests` already establishes, never a monkeypatch a real subprocess could not see), C5 (gate/offer/close's `documentRevisions` sites, both return AND ledger-event, asserted directly against `position.jsonl`), C7 (`well_formed`'s `require_document` gate, via a findings.py entry carrying a real `document` field), and C8 (`cmd_verify`'s `fidelityByDocument` fold, plus `admissibility_record`'s own extra-document staleness read).
- [x] 16.4 Mutation, positive control: `_extra_document_revisions`'s loop forced to `range(1, 1)` (anchor count 1→0 confirmed the real edit, `sd -s`-style silent-no-op scar avoided by asserting the anchor count via Python string replace, not a shell substitution tool). Both `TwoDocumentLifecycleTests` and `TwoDocumentPositionWriteTests` reddened correctly (`[] != [{...}]` on the exact `documentRevisions`/`documents` assertions). Reverted byte-identically (`git checkout --`; `git status --short` clean; zero occurrences of the mutation marker afterward). **A guard that fires, not a guard that cannot.**
- [x] 16.5 Gate coverage, measured: **24 of 24** real runtime `len(DOCUMENTS) > 1` code gates now exercised by a real subprocess (line numbers: 518, 4098, 7797, 7847, 7898, 10771, 10836, 10923, 10946, 10956, 13515, 13552, 13563, 13584, 13728, 13987, 13992, 14000, 14181, 14198, 14207, 14213, 14839, 15099). Zero remaining unreached gates — no gate needed a "cannot be reached" disclosure this time.
- [x] 16.6 Non-interference, re-measured live (not inherited from verify's own report): `sha256(tests/seal/digests.json)` unchanged at `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`; `tests/pair/digests.json` untouched (12 lines, unedited — this corrective work added NEW test classes, not new golden-digest cases, so the pair corpus's own 2-case golden file needed no change); `skipped=6` unmoved; `npm test` 595/595 exact; `.claude/skills/proposal-deliberation/` and `.claude/skills/_core/deliberation/` untouched.
- [x] 16.7 Commit as a single `test(...)` commit — no production file touched, conventional message, no AI attribution.

## Phase 17 — Second corrective apply: two C7 sites go from reached to asserted, and the pair corpus gets its own "unsealed" file (re-verify PASS WITH WARNINGS)

> **Why this phase exists.** Re-verify (evidence `sha256:6018619a9fadc9ee9ab709d4f23d10e0f59b1bec`) returned **PASS WITH WARNINGS**, closing the original CRITICAL but finding two new residual WARNINGs by its own mutation, independent of Phase 16's own claims: (1) two of the 24 `len(DOCUMENTS) > 1` gates (L7797 `cmd_admit`'s `sources_by_document`, L14839 `cmd_verify`'s `verify_sources_by_document` — both feeding the "representation only" `finding_impact`/`remedy_compatibility` capability) are genuinely reached by real two-document data but their output was never checked by any test; (2) `tests/pair/` has no `unsealed.json` naming its own exempt cases, unlike `tests/seal/`'s own sanctioned mechanism for the identical situation. This phase is coverage-only: no production code changed, one `test(...)` commit.

- [x] 17.1 `tests/findings.py` (built by `TwoDocumentLifecycleTests._build_box`) gains a second finding, `pair-lifecycle-doc1-finding`, naming `document: 'experiments'` and `uses: ['independently readable']` — a phrase present verbatim in document 1's own fixture text and absent from document 0's, so `remedy_compatibility`'s per-document routing at L14839 has something to genuinely diverge on (routing it correctly reports the finding compatible; defaulting to document 0's text, as it would if L14839's construction were skipped, would wrongly report it incompatible).
- [x] 17.2 Two new assertions added to `TwoDocumentLifecycleTests.test_the_full_lifecycle_reaches_every_named_gate`: `admit`'s `record["findings"]["pair-lifecycle-finding"]["impact"]["class"]` (L7797) asserted to be a `dict` (`{"proposal": "local"}`, not the plain string it is under one document — a structural, not merely a value, distinction); `verify`'s `verify_result["audit"]["compatibility"]` (L14839) asserted `status == "ok"` and `undefinedNotation == []`.
- [x] 17.3 Mutation, both sites independently, each `if len(DOCUMENTS) > 1:` → `if False:` via a Python line-indexed replace (anchor count asserted 0→1 before, 1→0 after each revert — the `sd -s`-silent-no-op scar avoided): L7797 reddened `test_the_full_lifecycle_reaches_every_named_gate` (`AssertionError: 'local' is not an instance of <class 'dict'>`); L14839 reddened the same test (`AssertionError: 'incompatible' != 'ok'`, with `undefinedNotation` naming the exact fixture finding whose notation collapsed back onto document 0's text). Both reverted via `git checkout --`; `git status --short` clean and zero `if False:` occurrences confirmed after each; both re-ran green.
- [x] 17.4 `tests/pair/unsealed.json` added (`{}` — the correct answer measured, not assumed: both of `tests/pair/cases.json`'s two existing cases already have goldens in `tests/pair/digests.json`, so today's exempt set is genuinely empty). New `PairCorpusMembershipTests` class in `tests/test_implementation_pair.py` mirrors `tests/seal/unsealed.json`'s own `SealMembershipTests` three-test enforcement (sealed ∪ unsealed == cases and disjoint; the declared set matches a literal `EXPECTED_UNSEALED`; every unsealed entry states a reason ≥20 chars) so a future case added without either a golden or a declared reason is caught, not silently dropped.
- [x] 17.5 `tests/test_implementation_pair.py` run in isolation: 13/13 green (was 10/10 before this phase — 3 new: 2 `PairCorpusMembershipTests`... actually 3 membership tests + 0 net new lifecycle test methods, 2 new assertions inside the existing one).
- [x] 17.6 Non-interference re-confirmed live: `sha256(tests/seal/digests.json)` unchanged (`011300df…dc6f75`); `git diff --stat -- tests/pair/cases.json tests/pair/digests.json` empty (goldens untouched — only `unsealed.json` is new); `git diff --stat d02496a..HEAD -- tests/test_implementation_domain_lock.py` empty, 16/16 green; `npm test` 595/595 exact; `.venv/bin/python -m unittest discover -s tests` — see 17.7.
- [x] 17.7 Full suite: `.venv/bin/python -m unittest discover -s tests` — paste `Ran`/`OK (skipped=6)`.
- [x] 17.8 Size, measured: +90 lines (89 `tests/test_implementation_pair.py`, 1 `tests/pair/unsealed.json`), test-only, 2 files. Combined Cut 3 total now 2,407 + 90 = 2,497 against the 1,400-line budget (+78.4%, up from +71.9%) — reported honestly, not trimmed.
- [x] 17.9 Commit as a single `test(...)` commit — no production file touched, conventional message, no AI attribution.

## Out of Scope — not scheduled here

Cross-document agreement and the verdict half of `handoff` (both to the consuming skill); any rename of `proposalDigest` or its ten relatives (`GATE_PROPOSAL_*`, `_proposal_digest`, `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`, `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`, `_campaign_identity`, `_load_remote_execution_*`); `compose`/M1 (open operator decision); M2 (`cmd_handoff`'s hardcoded Spanish); M5 (the derived-denylist lock — no `skipTest`, it would move `skipped=6`); creating `experimental-implementation`; F6 (`MANAGED_ARTIFACT_MARKER`'s four spellings).
