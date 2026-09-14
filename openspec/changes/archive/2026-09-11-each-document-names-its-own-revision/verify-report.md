```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:6ef28514f2b7b82dd7b82d3313d388e90d2321ce187d82585f8548db8ac95b22
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 8/8
scenarios: 14/14
test_command: npm test && .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256:9cb85a976d7edc5545409344640c9f7ba2109d2fa44f8d0a9a04b599f0918e59
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: each-document-names-its-own-revision
**Version**: N/A (amends `implementation-document-binding`; delta on an already-shipped capability, Cut 3)
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 33 |
| Tasks complete | 33 |
| Tasks incomplete | 0 |

`tasks.md` re-read directly: all 33 checkboxes are `[x]`, each carrying measured evidence inline, not a bare tick.

### Build & Tests Execution

**Build**: PASSED — `npm run typecheck` (`tsc -p tsconfig.json`), exit 0. No TypeScript file is touched by this change; run for parity with this project's prior verify reports.

**Tests**: re-run from scratch at HEAD `3cfdf34` (not inherited from apply's report):

```text
npm test: tests 595 / pass 595 / fail 0 / cancelled 0 / skipped 0
.venv/bin/python -m unittest discover -s tests: Ran 2923 tests in 495.062s — OK (skipped=6)
```

Both figures match apply's own claim exactly (baseline 595/595 and 2913→2923, skipped=6 unmoved).

**Coverage**: not available — no coverage tool detected in this project's cached capabilities.

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Each Document's Revision Name Is Its Own, Never Shared | Two unrelated stems resolve independently | `TwoDocumentLifecycleTests.test_the_full_lifecycle_reaches_every_named_gate`, `TwoDocumentPositionWriteTests.test_absent_install_then_unchanged_all_carry_the_documents_group` — re-run fresh, both green | ✅ COMPLIANT |
| Each Document's Revision Name Is Its Own, Never Shared | Pinning one document names only that document | Same two classes; `--revision` pins document 0 only, document 1 resolves independently via `discover_document_revision` | ✅ COMPLIANT |
| An Unnamed Document's Revision Is Discovered In Its Own Root | An unpinned second document discovers its own newest candidate | `DiscoverDocumentRevisionTests` (5 cases: empty/hand-authored-max/tie/marker-owned/not-a-directory) — re-run fresh, green | ✅ COMPLIANT |
| An Unnamed Document's Revision Is Discovered In Its Own Root | An explicit pin is honored verbatim, without discovery | `document_revision_names` — index 0 path unchanged; verified by reading `document_revision_names`/`revision_source` source directly | ✅ COMPLIANT |
| Revision Discovery And The Verify Fidelity Fold Run Per Document | Independent fidelity discovery per document | `ExtraDocumentFidelityStatusTests` (pre-existing, still green); direct function-level re-derivation of `_extra_document_fidelity_status` confirmed `"unknown"` for a shared-name miss | ✅ COMPLIANT |
| Revision Discovery And The Verify Fidelity Fold Run Per Document | A newer candidate in one document does not affect the other | `DiscoverDocumentRevisionTests.test_a_hand_authored_root_picks_the_digit_tuple_max`, per-index seed confirmed in `cmd_verify` source | ✅ COMPLIANT |
| An Unreadable Declared Document Refuses At Every Binding-Write Site | A binding-write site refuses on an unreadable extra document | `TwoDocumentAmbiguousFamilyRefusesTests.test_ambiguous_families_refuse_naming_both` — re-run fresh, green, exit 2, code + both families named | ✅ COMPLIANT |
| An Unreadable Declared Document Refuses At Every Binding-Write Site | Verify reports the same condition without refusing | `_extra_document_fidelity_status` never calls `_extra_document_revisions`; confirmed by reading `cmd_verify`'s call graph directly | ✅ COMPLIANT |
| A Committed Record Written Under The Shared-Name Assumption Remains Valid, Unedited | A pre-existing shared-name ledger event still reads | M3 containment re-confirmed: `_AUTHORIZATION_BINDING_KEYS` untouched literal 8-tuple; presence-gated 9th key | ✅ COMPLIANT |
| A Committed Record Written Under The Shared-Name Assumption Remains Valid, Unedited | A committed single-document token still re-derives its golden digest | `tests/seal/` 28/28, re-run from scratch, `sha256(digests.json)` = `011300df7d...` byte-identical (measured twice, independently) | ✅ COMPLIANT |
| The Fixture Reshape Reddens The Existing Pair Tests Unassisted | The reshape alone reddens the suite, no assertion edited | Independently reproduced in a scratch worktree at `bec4d12`: both lifecycle/position-write tests FAIL at their first (sha) assertion — confirmed by re-running the exact committed test file, no test-file edits made by this verification | ✅ COMPLIANT (see RED-control finding below — WARNING, not a compliance failure) |
| The Fixture Reshape Reddens The Existing Pair Tests Unassisted | The reshape plus resolution together turn the suite green | Same two classes at HEAD `3cfdf34`, re-run fresh, both green | ✅ COMPLIANT |
| The New Refusal Is Reachable By Mutation, Not Only By Construction | Reverting the guard reddens the corpus | `AmbiguousFamilyMutationProvesReachabilityTests` re-run at HEAD: real, reverted engine-file edit; engine file confirmed byte-identical (sha256 diff) before/after; ambiguous fixture silently succeeds under mutation, unambiguous fixture unaffected, only the refusal-specific test tells them apart. A second, independent manual mutation (same anchor, applied outside the test harness) confirmed the lifecycle/position-write sha assertions ALSO still pass under the mutation | ✅ COMPLIANT |
| The Coarse Provenance Key Stays Shared, Never Profile-Supplied (implementation-engine-neutrality) | The join reads the literal on both sides, unaffected by an unread key | `rg unreached_mathematics openspec/specs/` → 0 matches (re-run); text-only correction, no behavior change, pre-existing `unreached_modules` tests still green in the full suite | ✅ COMPLIANT |

**Compliance summary**: 14/14 scenarios compliant.

### Correctness (Static + Executed Evidence)

| Requirement / Claim | Status | Notes |
|---|---|---|
| `reachable_refusal_codes()` 113 → 114 | ✅ Confirmed | `GatingRefusalRosterTests` (18/18, re-run) + `GATING_REFUSALS` len == 114 (measured directly via import) |
| Doctrine counts (49 invocation / 65 work-state / 114 total) | ✅ Confirmed | SKILL.md L2788/2792 read directly: "49 codes"/"65 codes"; usage.md L2227: "Sixty-five codes" |
| `_AUTHORIZATION_BINDING_KEYS` literal 8-tuple | ✅ Confirmed | Read directly at L13065-13068; presence-gated 9th key at L13092-13094 |
| No shipping profile declares `len(documents) > 1` | ✅ Confirmed | `proposal-implementation/impl_profile.py` declares exactly one `documents` entry |
| `tests/pair/digests.json` unmoved | ✅ Confirmed | `PairCorpusComparisonTests` re-run from scratch, 2/2 green |
| `skipped=6` unmoved | ✅ Confirmed | Fresh full-suite run: `OK (skipped=6)` |
| Size ~865 changed lines | ✅ Confirmed | `git diff --shortstat e1c4005 96a4363` over the six changed code/test files (excluding tasks.md): 790 insertions + 75 deletions = 865, exactly |
| `admissibility_record`'s second (scalar-into-wrong-directory) defect | ✅ Confirmed fixed | Diffed `bec4d12..67d07b2`: old code read `revision_source(revision, index)` (the shared scalar); new code resolves `document_revision_names(revision)` per label |
| `remedy_compatibility` None-join crash | ✅ Confirmed real, and fixed correctly | Independently reproduced the exact `TypeError` at `bec4d12` via a real subprocess pipeline (probe, non-persisted); confirmed the HEAD fix filters `None` before joining and reads unresolved-but-named documents as empty text, never crashing and never silently falling back to document 0 |
| `position_state`'s never-recorded/stale conflation | ✅ Confirmed real, and fixed correctly | Reproduced the pre-fix code path directly: with `entry=None` and a resolved `extra_source`, `_bound_to` returns `"stale"` (would trip `POSITION_STALE` in `cmd_gate`/`cmd_offer`/`cmd_close`, confirmed by reading the refusal call site at L13550); the shipped `entry is None → "unknown"` branch avoids it |
| D9 non-additions | ✅ Confirmed | Zero matches for `--revision-`/`revision_1`-as-flag and `proposalDigest` in the engine diff; zero diff on `test_implementation_domain_lock.py` |
| `git diff --exit-code 4dd91df HEAD` for deliberation/seal paths | ✅ Confirmed | Re-run against the real, existing paths (`.claude/skills/{proposal,experimental}-deliberation/`, `.claude/skills/_core/deliberation/`, `tests/seal/`) — exit 0. Note: the orchestrator's own cached pre-measurement table used bare, non-existent path spellings (`proposal-deliberation/`, etc.), which exit 0 trivially regardless of content; apply's own task 4.3 already used the correct resolved paths, and this verification re-confirmed against those same correct paths |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1 (directory-seeded discovery, index > 0 only) | ✅ Yes | `discover_document_revision` matches design exactly; document 0 path untouched |
| D2 (dumb per-index reader + process-memoized resolver, keyed on revision+roots) | ✅ Yes | `document_revision_names`, `_DOCUMENT_NAME_CACHE` keyed as designed; `DocumentRevisionNamesMemoTests` green |
| D3 (`DOCUMENT_REVISION_UNREADABLE`, WORK_STATE, raised only inside `_extra_document_revisions`) | ✅ Yes | Confirmed by source read and roster tests |
| D4 (fixture reshape reddens unassisted) | ⚠️ Partially — see WARNING below | The reshape does reproduce red #1 unassisted; reds #2/#3 are NOT independently observable from the single committed test run (structural masking); apply disclosed this, did not hide it |
| D5 (mutation a weaker lock survives) | ✅ Yes | Independently reproduced with a real reverted edit; also independently re-verified the lifecycle-class sha assertions survive the mutation |
| D6 (discovery as a staleness input, no new code) | ✅ Yes | `GATE_AUTHORIZATION_STALE`/`prior_close` unchanged, confirmed by source read |
| D7 (wire `extra_sources` at all 9 sites) | ✅ Yes | `_document_extra_sources` used at all 9 call sites; `DocumentOneBoundToTests` (current→stale) re-run, green |
| D8 (`admissibility_record` pairs by label) | ✅ Yes | Confirmed by source read; matches `position_state`'s own `header_documents` pairing |
| D9 (no `--revision-<index>`, no `proposalDigest` rename, `KitAgreementLockTests._profile` deferred) | ✅ Yes | Confirmed by diff, zero matches |

### RED-Control Finding (spend-your-effort item 1) — WARNING

**Independently re-checked out `bec4d12` in a scratch worktree** (never this one; removed after use) and ran the exact committed pair suite unmodified.

**What the committed RED commit itself proves**: both `TwoDocumentLifecycleTests.test_the_full_lifecycle_reaches_every_named_gate` and `TwoDocumentPositionWriteTests.test_absent_install_then_unchanged_all_carry_the_documents_group` FAIL, each halting at its *first* reached assertion — the sha256 comparison against `_doc1_sha256()` (red #1: `sha256: None` vs. a real hash). This is genuine, mechanical, and demonstrated by the committed artifact alone: no probe, no inheritance.

**What the committed RED commit does NOT prove**: reds #2 and #3 are never reached in that same run. `TwoDocumentLifecycleTests`'s single test method contains all three assertions in sequence; Python's `assertEqual` raises immediately at the first failure, so the method body never reaches the later `gate`/`close`/`admit`/`verify` calls where reds #2/#3 would fire. `TwoDocumentPositionWriteTests`'s test method never reaches a `verify` call at all.

**Independent re-derivation of reds #2 and #3** (own scratch probe, non-persisted, deleted after use — not apply's probe, not inherited):

- **Red #2 holds exactly as predicted.** Calling `_extra_document_fidelity_status` directly with the same shared-name inputs `bec4d12` would have produced returns `"unknown"` — confirmed by direct function call against the real `bec4d12` checkout.
- **Red #3 does NOT hold as predicted.** Running the real subprocess pipeline (`probe → propose → offer → gate → close → admit → verify`) against `bec4d12` reaches `verify`, which **crashes** with an unhandled `TypeError: sequence item 0: expected str instance, NoneType found` inside `remedy_compatibility`'s `"\n".join(texts)` — never a clean `compatibility["status"] != "ok"` assertion failure. This crash occurs in `cmd_verify` *before* `fidelityByDocument` is even computed (confirmed by reading `cmd_verify`'s line order: `remedy_compatibility` at L14844, `fidelityByDocument` at L15092+), meaning red #2 is *also* structurally unreachable through the real command path at `bec4d12` — it can only be observed by calling the helper function directly, bypassing the crash.

**Assessment**: apply's own report is accurate and transparent about this — it explicitly states reds #2/#3 were checked via "a throwaway, non-persisted probe" and that red #3 "did not hold as predicted." This verification confirms that characterization by independent re-derivation, including the additional fact that red #3's crash *masks* red #2 in the real command path (not only in the single test method). The shipped fix is correct and the refusal is separately, robustly mutation-tested (D5, confirmed above) — so no functional defect ships. But the design's own success criterion ("Red first... that red IS the control this project keeps asking for") is only fully met for mechanism #1. Mechanisms #2 and #3 were real, but the persisted RED commit by itself cannot demonstrate them, now or on any future re-checkout — they require a hand-written, disposable probe every time. **WARNING, not CRITICAL**: the underlying refusal and fidelity-status behavior are independently correct and separately tested at HEAD; the gap is in what the RED artifact itself can prove, not in the shipped behavior.

### Extra-Defect Findings (spend-your-effort item 2) — informational, both confirmed genuine and correctly scoped

1. **`remedy_compatibility` None-join crash.** Confirmed real (independently reproduced, see above), confirmed unreachable before this change (every document previously shared one filename, so `sources_by_document[label]` was never `None` for a *named* label), and confirmed the fix is correct: filters `None` before `"\n".join`, treats an unresolved-but-named document as absent text (`"unknown"`-shaped), never silently substitutes document 0's text.
2. **`position_state`'s never-recorded/stale conflation.** Confirmed real by direct reproduction of the pre-fix code path: with a document never recorded in the header (`entry is None`) and a now-resolved `extra_source` (only possible after D7's wiring), the naive code computes `_bound_to(revision, extra_source, None)` → `"stale"`. Confirmed this reaches a real refusal: `cmd_gate` reads `position["status"]` through `impl_availability.launch_available`, and `"stale"` there raises `POSITION_STALE` (`implementation_engine.py:13550`), which would have blocked a legitimate first-time `gate`/`offer` on a document simply never yet probed. Confirmed the shipped fix (`entry is None → "unknown"`) avoids it. Both defects were genuinely latent (invisible while `extra_sources` was always `None`, i.e. before this change's own D7 wiring) — not something an earlier change could have caught, and correctly scoped as "a direct consequence of the exact code being touched."

### D5 Mutation Finding (spend-your-effort item 3) — confirmed by independent execution

Re-ran `AmbiguousFamilyMutationProvesReachabilityTests` at HEAD: engine file's sha256 confirmed byte-identical before and after the test run (real mutation, guaranteed reverted). Additionally performed a second, fully independent manual mutation (own edit, own revert via `git checkout --`) of the identical ambiguity branch and confirmed: (a) the previously-ambiguous fixture now succeeds with a real sha, (b) `TwoDocumentLifecycleTests`/`TwoDocumentPositionWriteTests` (the unambiguous fixtures) still pass unaffected under the mutation — matching the design's claim that "every sha/documents assertion in the lifecycle classes still passes" and only the dedicated refusal test (`TwoDocumentAmbiguousFamilyRefusesTests`) can tell the two behaviors apart. No issue found.

### Task 2.8 Deviation Judgment (spend-your-effort item 4) — sound, not a convenience

`DiscoverDocumentRevisionTests` (direct unit tests against `discover_document_revision`, using `IMPLEMENTATION_PROPOSALS_1` env overrides) instead of new `tests/pair/cases.json` golden-digest entries. Confirmed: `tests/pair/cases.json` holds exactly 2 cases, both `"command": "name"` — the `name` command never reads a revision, so extending its digest machinery would indeed invent a new digested-command shape the design does not otherwise need. Confirmed the cited precedent (`ExtraDocumentFidelityStatusTests` in `test_proposal_implementation.py`) is real and uses the identical direct-call, env-override style for the sibling per-document function. This matches design.md's own Testing Strategy row verbatim ("Unit | discover_document_revision | marker-owned / hand-authored / tie / empty / ambiguous"). Judgment: sound engineering, not a convenience.

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. The RED control (slice 1) fully demonstrates only 1 of 3 predicted independent mechanisms via the persisted, committed test artifact in a single run; mechanisms #2 and #3 require a disposable, non-persisted probe to check (this verification independently reproduced both, confirming apply's own disclosure was accurate — including that red #3 is a crash, not the predicted assertion failure, and that this crash masks red #2 in the real command path too). No functional defect ships; the refusal itself is separately and robustly mutation-tested.

**SUGGESTION**:
1. `tests/test_proposal_implementation.py::GatingRefusalRosterTests::test_the_derivation_finds_the_measured_one_hundred_and_thirteen` — the test method's *name* is now stale (asserts `114`, named after the prior `113` milestone); its docstring correctly narrates the history including "one hundred and fourteen." Cosmetic only; the assertion is correct and passes.
2. `_shared/tools/check_citations.py` reports 2 false-positive unresolved citations against `proposal.md` (`TwoDocumentLifecycleTests.REVISION`, `TwoDocumentPositionWriteTests.REVISION`) and 1 against `design.md` (a markdown filename, `AGREED.md`, misparsed as `Class.member`). Manually confirmed both classes' `REVISION` class attributes exist in `tests/test_implementation_pair.py`. Tool limitation with class-level constants and backtick-quoted filenames, not a real dangling citation — worth a future fix to the shared tool, out of scope here.

### Verdict

**PASS WITH WARNINGS**

All 33 tasks complete and independently re-verified; both test suites pass fresh from scratch (`npm test` 595/595, Python `Ran 2923, OK (skipped=6)`); all 28 seal digests byte-identical (measured twice, independently); `tests/pair/digests.json` unmoved; the D5 mutation and the two extra-defect fixes were independently reproduced and confirmed correct; the size claim (~865 lines) was independently re-measured and matches exactly. The one WARNING is an honest, apply-disclosed epistemic gap in what the persisted RED commit itself can prove for 2 of 3 predicted mechanisms — not a functional defect, since the shipped behavior for all three is independently correct and separately tested at HEAD.
