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

- [ ] 0.1 `.venv/bin/python -m unittest discover -s tests`: paste `Ran`/`OK (skipped=6)`.
- [ ] 0.2 `npm test`: paste `595/595`.
- [ ] 0.3 Seal run: `sha256(tests/seal/digests.json)`, paste; `git diff --exit-code tests/seal/` exits 0.

## Phase 1 — RED first: indexed-leaf refusals (A1)

- [ ] 1.1 `test(...)` commit only: add refusal cases to `tests/test_implementation_profile.py` for `documents[1].directory` and `documents[0].label` missing, each naming the exact indexed leaf, and for `documents: []` refusing `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming `documents[0]`.
- [ ] 1.2 Confirm RED before any resolver or profile change; checkout the `test(...)` commit alone and re-run to prove it is red in isolation.

## Phase 2 — Resolver per-index walk + one-entry list + accessor (A2)

- [ ] 2.1 `impl_domain_profile.py`: replace `_REQUIRED_ABSOLUTE_ONLY`'s single `("documents", "directory")` pair and `_REQUIRED_PRESENCE`'s `("documents", "label")` pair with a per-entry walk emitting indexed leaf names (`documents[N].directory`, `documents[N].label`).
- [ ] 2.2 `impl_profile.py`: `documents` becomes a one-entry list, same literal values.
- [ ] 2.3 `implementation_engine.py`: `DOCUMENTS = PROFILE["documents"]`; `DOCUMENTS_DIRECTORY = DOCUMENTS[0]["directory"]`, `DOCUMENTS_LABEL = DOCUMENTS[0]["label"]` — spelling unchanged, value unchanged at `len == 1`.
- [ ] 2.4 Phase 1's RED cases turn GREEN. Implementation commit.
- [ ] 2.5 Seal run: 28/28 byte-identical.

## Phase 3 — Fixture profile + `IMPLEMENTATION_PROPOSALS_1` (A3)

- [ ] 3.1 `tests/fixtures/two_documents/impl_profile.py`: two-entry `documents` list, written to a `tempfile` dir at run time via the same `_write_scratch_profile` mechanism Cut 2 uses; `_SKILL` re-anchored to the real skill directory.
- [ ] 3.2 `tests/seal/harness.py`: add `IMPLEMENTATION_PROPOSALS_1` to `ALLOWED_ENV_KEYS`. The bare `IMPLEMENTATION_PROPOSALS` keeps overriding document 0 only (M5) — no generic `IMPLEMENTATION_PROPOSALS_0` alias.
- [ ] 3.3 Seal run: 28/28 byte-identical.

## Phase 4 — Pair corpus + its own goldens (A4)

- [ ] 4.1 `tests/pair/cases.json` + `tests/pair/digests.json`: new roster, own goldens, driven through `seal_harness.run_case` via `_build_env_with_profile_override`. No entry added to `tests/seal/digests.json`.
- [ ] 4.2 **Measure, then assert** which pair-corpus case reaches each pair branch introduced in Slice A (resolver per-index refusal, `DOCUMENTS[1]` presence). Name the reaching case per branch — do not assert first and hunt for a case.
- [ ] 4.3 Seal run: existing 28 unaffected; `git diff --exit-code tests/seal/` exits 0.

## Phase 5 — Positive control (A5, D8) — precondition gate before Slice B

- [ ] 5.1 Under `.venv/bin/python` only. Mutate `documents[0].directory` to a fresh `tempfile.mkdtemp()` sibling; assert **exactly** `admit-e0`, `close-e0`, `gate-e0`, `offer-e0`, `position-e0` move and no other — the set already recorded in `MEASURED_MOVERS["documents.directory"]`.
- [ ] 5.2 **If this does not reproduce, stop.** Every zero-mover reading in this session becomes void; do not proceed to Slice B until it reproduces under `.venv/bin/python` (never system `python3`, which breaks `CLI_INVOCATION` and crashes both sides identically).
- [ ] 5.3 Confirm Slice A moved **zero** digests overall — the structural claim of D4, proven only by this seal run, not assumed from the accessor's shape.
- [ ] 5.4 Slice A close-out: both suites pasted, `git diff --exit-code tests/seal/` exits 0. Slice A is independently landable here.

---

## Phase 6 — D1d: the re-derivation test lands first (B1)

- [ ] 6.1 `test(...)` commit only, new file `tests/test_implementation_authorization_binding.py`: `test_committed_token_rederives` — a committed fixture `authorization` event's payload, rebuilt through the production path, digests to a **token committed as a literal** in the test (never recomputed from the fixture on both sides).
- [ ] 6.2 Same commit: `test_verify_accepts_the_committed_token` (`_verify_gate_authorization` over the fixture returns the record, does not raise); `test_superseded_still_fires` (a 7-key legacy fixture still yields `GATE_AUTHORIZATION_SUPERSEDED`, not `UNKNOWN`).
- [ ] 6.3 New fixture `tests/fixtures/authorization/position.jsonl`: a real minted `authorization` event, copied from a real run or minted once with a pinned `session`/`at`/`mintOrdinal` and committed. **Measure which it is** — do not assume one exists.
- [ ] 6.4 Confirm all three tests RED (no production change yet, since `_authorization_binding_keys` helper does not exist). Verify by checkout that this `test(...)` commit is individually red.

## Phase 7 — C4: the authorization binding (B2, D1)

- [ ] 7.1 Implementation commit: add `_authorization_binding_keys(record_or_binding)` helper returning `_AUTHORIZATION_BINDING_KEYS`'s eight base keys plus `documentRevisions` **only when that key is present in the mapping** — key absence, never null, mirroring `GATE_AUTHORIZATION_SUPERSEDED`'s own `"proposalDigest" not in record` discriminator.
- [ ] 7.2 **`_AUTHORIZATION_BINDING_KEYS` itself stays a literal 8-tuple, unedited.** `_verify_gate_authorization`'s `own_binding` comprehension and `cmd_gate`'s inline `gate_binding` route through the new helper instead of the raw constant.
- [ ] 7.3 `_authorization_binding` and `_find_or_mint_authorization` emit `documentRevisions` (a list of `{label, revision, sha256}`) only when `len(DOCUMENTS) > 1`.
- [ ] 7.4 Phase 6's three tests turn GREEN.
- [ ] 7.5 Verify `CampaignProposalExclusionTests`'s L3 (`assertIn("proposalDigest", module._AUTHORIZATION_BINDING_KEYS)`) is unedited and green.
- [ ] 7.6 **Git-verify the ordering requirement**: the Phase 6 `test(...)` commit is an ancestor of this implementation commit (`git merge-base --is-ancestor <phase6-sha> <phase7-sha>`).
- [ ] 7.7 Mutation: add a 9th key **unconditionally** to `_authorization_binding_keys` in a scratch copy; `test_committed_token_rederives` must redden. Revert; confirm green.
- [ ] 7.8 Seal run: 28/28 byte-identical.

## Phase 8 — C3: admissibility (B3, D5)

- [ ] 8.1 RED `test(...)` commit: a committed `tests/fixtures/admissibility/scalar.json` (pre-cut three-key shape) must still be read as valid by `admissibility_record` after this class lands.
- [ ] 8.2 Implementation: `cmd_admit`'s `record` and `admissibility_record`'s `record.get("revisionSha256")` comparison gain a dual-shape read — scalar keys first; an additive `documents` list written **beside** them only under `len(DOCUMENTS) > 1`, falling back to `documents` only when scalar keys are absent.
- [ ] 8.3 Mutation: collapse to a two-document-only write path in a scratch copy; the scalar-shape fixture test reddens. Revert; confirm green.
- [ ] 8.4 Seal run: 28/28 byte-identical.

## Phase 9 — C2: position header + writer (B4, D3)

- [ ] 9.1 RED `test(...)` commit: committed `tests/fixtures/position/scalar_header.md` (pre-cut single-pair header) must still open under both `_BLOCK_OPEN_RE` and `_LEGACY_BLOCK_OPEN_RE` after this class lands. Add a case for the new refusal: a header carrying `documents=` read under a one-document profile.
- [ ] 9.2 Implementation: `_BLOCK_OPEN_RE` gains one optional trailing group after `target=`: `(?:\s+documents=(?P<documents>\S+))?`, matched only under `len(DOCUMENTS) > 1`. `_LEGACY_BLOCK_OPEN_RE` unchanged — the frozen pre-`target=` grammar. `render` and `locate_block` updated to emit/parse the group. `cmd_position`'s docstring, `header`, `absent`, `unchanged` comparison/return, `position` ledger event, `written` return become document-aware, scalar under one.
- [ ] 9.3 New refusal `POSITION_HEADER_DOCUMENT_COUNT_MISMATCH` for the documents-under-one-profile case.
- [ ] 9.4 **Measure and record** `reachable_refusal_codes()`'s new pinned count (moved by exactly this one added refusal). Never predict it.
- [ ] 9.5 Mutation both ways: removing the group parse reddens the two-document case; forcing the group to emit under one document reddens the byte-identity assertion.
- [ ] 9.6 Seal run: 28/28 byte-identical.

## Phase 10 — C1: position read (B5)

- [ ] 10.1 RED `test(...)` commit for `position_state`'s per-document `boundTo` mapping under two documents, scalar `"current"`/`"stale"`/`"unknown"` unchanged under one.
- [ ] 10.2 Implementation: `position_state`'s `empty` dict, `bound_to` comparison (`hashlib.sha256(source…)`), and return dict become per-document under `len(DOCUMENTS) > 1`.
- [ ] 10.3 Mutation both directions; anchor counts asserted before/after.
- [ ] 10.4 Seal run: 28/28 byte-identical.

## Phase 11 — C5: ledger events & command returns (B6)

- [ ] 11.1 RED `test(...)` commit for `cmd_gate`'s `gate` event/return, `cmd_offer`'s `offer` event/return, `cmd_close`'s `prior_close` comparison, `not_open` return, `close` event, `closed` return — pair shape under two documents only.
- [ ] 11.2 Implementation: additive `documentRevisions` beside the unchanged scalar key at each site. `cmd_close`'s `prior_close` lookup (`e.get("revisionSha256") == revision_sha256`) stays a scalar comparison under one document — asserted against a committed prior-close fixture, not assumed.
- [ ] 11.3 Mutation both directions.
- [ ] 11.4 Seal run: 28/28 byte-identical.

## Phase 12 — C6: the non-`revisionSha256` scalars (B7)

- [ ] 12.1 RED `test(...)` commit for `cmd_verify`'s `module["stale"]` (over `prov.get("revision")`), `built_against`/`staleRevision`, `admissibility_record`'s returned `revision`, `fidelity`'s `latestRevision`/`revisionSource` becoming per-document reads.
- [ ] 12.2 Implementation: each site reads per-document; scalar emitted unchanged under one document.
- [ ] 12.3 Mutation both directions.
- [ ] 12.4 Seal run: 28/28 byte-identical.

## Phase 13 — C7: findings routing (B8, D6)

- [ ] 13.1 RED `test(...)` commit: `well_formed` demands `document` only when `len(DOCUMENTS) > 1` — a single-document finding without `document` still validates; a two-document finding without it is refused, naming the missing field.
- [ ] 13.2 RED: `finding_impact`'s `impact["class"]` (today `"local" if local else "structural"`) becomes a per-document mapping only under `len(DOCUMENTS) > 1`, representation only — no combined verdict word. `remedy_compatibility(findings, revision)` and `admissibility_record(target, revision)` take the documents.
- [ ] 13.3 Implementation for both.
- [ ] 13.4 **Measure**: confirm `admit-e1`, `handoff-e1`, `verify-a` are byte-identical after this class — the branch most likely to move a digest, per design's own prediction list.
- [ ] 13.5 Mutation both directions.
- [ ] 13.6 Seal run: 28/28 byte-identical.

## Phase 14 — C8: per-document fidelity (B9, D7)

- [ ] 14.1 RED `test(...)` commit: `cmd_verify`'s `fidelity_status` fold (`stale or missing_provenance or untested or unreached`) becomes a function of one document, applied N times; a sibling `fidelityByDocument` list appears beside `fidelity` only under two documents; `fidelity.status` reports document 0.
- [ ] 14.2 Implementation. `verify-a`, `verify-b`, `verify-t` — the three most-covered seal cases — asserted unchanged.
- [ ] 14.3 Mutation both directions.
- [ ] 14.4 Seal run: 28/28 byte-identical.

## Phase 15 — Slice B proof + non-interference close-out (B10)

- [ ] 15.1 Full per-class mutation sweep re-run in one pass (C1–C8); `git diff --exit-code tests/seal/` exits 0.
- [ ] 15.2 `.venv/bin/python -m unittest discover -s tests`: paste `Ran`/`OK (skipped=6)` — `Ran` may have grown, `skipped=6` must not move.
- [ ] 15.3 `npm test`: paste `595/595` exactly.
- [ ] 15.4 Confirm `proposal-deliberation/` and `_core/deliberation/` untouched (`git diff --stat` against the pre-cut sha, scoped to both paths, empty).
- [ ] 15.5 Confirm every "Products" row from design's What Breaks section by inspection: minted `position.jsonl` authorizations valid; `close` events not double-closed; `admissibility.json`/position headers in scalar shape still read; `__provenance__`/`__benchmark__["revision"]` untouched; `tests/seal/digests.json` valid.
- [ ] 15.6 Commit per work unit, conventional messages, no AI attribution.

## Out of Scope — not scheduled here

Cross-document agreement and the verdict half of `handoff` (both to the consuming skill); any rename of `proposalDigest` or its ten relatives (`GATE_PROPOSAL_*`, `_proposal_digest`, `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`, `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`, `_campaign_identity`, `_load_remote_execution_*`); `compose`/M1 (open operator decision); M2 (`cmd_handoff`'s hardcoded Spanish); M5 (the derived-denylist lock — no `skipTest`, it would move `skipped=6`); creating `experimental-implementation`; F6 (`MANAGED_ARTIFACT_MARKER`'s four spellings).
