```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:edc7e136a51e08836226a65be580cd842c518d0692b406876951c5dfd11c44dd
verdict: fail
blockers: 1
critical_findings: 1
requirements: 9/14
scenarios: 25/30
test_command: .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256:2cba8cac5f3fe0a28ba19d84a5f82dc994b01f21ad09642e6c1291c73734a471
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:3ee3fb490b97e3bdf6ee15680a0bd73b4a6b208e84e193ba25fdebc9087b3b51
```

## Verification Report

**Change**: `a-revision-is-two-documents` (Cut 3)
**Version**: Both slices landed — Slice A (`f5d2258`…`caf2f5f`, 5 commits) + Slice B (`7a4755a`…`406b212`, 15 commits) + `c2a86c9` (Phase 15 proof, orchestrator-authored)
**Mode**: Strict TDD, hybrid persistence (OpenSpec is source of truth)

All measurements below were re-executed by this verify session, from a clean worktree, against HEAD `c2a86c9`. Nothing from Phase 15's self-reported table was inherited without re-running it.

### Completeness (tasks.md)
| Metric | Value |
|--------|-------|
| Tasks total | 60 |
| Tasks complete | 60 (`[x]`, verified by reading tasks.md directly) |
| Tasks incomplete | 0 |

### Build & Tests Execution — RE-RUN, not inherited
**npm test**: ✅ 595 passed / 0 failed / 0 skipped (32.2s)
```text
$ npm test
ℹ tests 595
ℹ pass 595
ℹ fail 0
ℹ skipped 0
```

**Python suite**: ✅ 2906 passed, 0 failed, 0 errors, 6 skipped (478.6s)
```text
$ .venv/bin/python -m unittest discover -s tests
Ran 2906 tests in 478.585s
OK (skipped=6)
```
`skipped=6` — unmoved from the pre-cut baseline (`Ran 2874`/`skipped=6`) across both slices. **Zero new skips, confirmed live.**

**Seal digest, captured live (not replayed)**: `test_implementation_seal.py`'s own `SealComparisonTests` re-runs all 28 cases as real subprocesses inside this exact suite run (module-scope `seal_harness.run_case(...)` capture, not a stored-bytes replay) and compares to the committed golden.
```text
sha256(tests/seal/digests.json) = 011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75
```
Unchanged from the pre-cut baseline. `git diff --exit-code -- tests/seal/` → exit 0 (checked before and after this suite run). `git status --short` after the full run → clean (no toy-target residue).

**Operational note (not a defect in the change)**: mid-session, a second, independent `unittest discover -s tests` process (PID 66121, a different shell session's own bash-tool invocation, not spawned by this verify session) was found already running against this same shared worktree/`FORGE_ROOT`. Per this change's own concurrency-safety rule, I killed my own concurrent duplicate immediately, waited for the foreign process to exit cleanly, and only then ran the measurements reported above from a single, exclusive process. Reported for transparency; it produced no corruption (`git status --short` clean throughout, digests unchanged).

### Central Question — verified by execution, not by reading

**Would a token minted before this change still validate after it? Yes — and I made an old token fail on purpose to prove the guard, not just read the code.**

1. **`_AUTHORIZATION_BINDING_KEYS` is still a literal 8-tuple carrying `proposalDigest`.** Read directly: `implementation_engine.py:12859-12862`. `CampaignProposalExclusionTests`'s L3 (`assertIn("proposalDigest", module._AUTHORIZATION_BINDING_KEYS)`) is **unedited**: `git diff --stat d02496a..HEAD -- tests/test_implementation_domain_lock.py` → **empty**, confirmed directly (not inherited).
2. **`test_committed_token_rederives` carries a committed literal digest**, not a double-recompute. Read `tests/test_implementation_authorization_binding.py`: `EXPECTED_EIGHT_KEY_TOKEN` is a hardcoded literal (`"999f0ca3...c7a"`); it is looked up against the fixture's own committed `token` field (`tests/fixtures/authorization/position.jsonl`, `jobName: "job1"`) — the two literals were independently confirmed to match — and `_verify_gate_authorization` internally re-derives the digest from the record's OTHER 8 fields via production code and compares. Two independent committed literals agreeing, plus one live production recomputation: the "green because nothing happened" shape does not apply here.
3. **`7a4755a` (the re-derivation test's RED commit) is a git ancestor of `3aa2cee` (the binding-shape commit)**: `git merge-base --is-ancestor 7a4755a 3aa2cee` → confirmed (exit 0).
4. **I mutated the binding shape for real.** I edited `_authorization_binding_keys` to add the 9th key (`documentRevisions`) **unconditionally**, ran `test_implementation_authorization_binding.py`: all 3 tests reddened —
   - `test_committed_token_rederives` → `KeyError: 'documentRevisions'`
   - `test_verify_accepts_the_committed_token` → `KeyError: 'documentRevisions'`
   - `test_superseded_still_fires` → `AssertionError: 'GATE_AUTHORIZATION_UNKNOWN' != 'GATE_AUTHORIZATION_SUPERSEDED'`
   Then reverted byte-identically (`git checkout -- implementation_engine.py`; `git status --short` clean) and re-ran: all 3 green again. **The guard fires. It is not a guard that cannot fire.**

**Verdict on the central question: PASS, unconditionally.** All four sub-checks hold.

### Spec Compliance Matrix

Requirement/scenario counts, counted directly from the three spec files: **14 requirements, 30 scenarios** (`implementation-document-binding`: 11 req / 21 scen; `implementation-engine-neutrality`: 1 req / 3 scen; `implementation-cli-seal`: 2 req / 6 scen).

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Documents Are An Indexed List | single-doc validates as before | `IndexedDocumentsLeafRefusalTests` + full profile suite | ✅ COMPLIANT |
| Documents Are An Indexed List | 2nd doc missing leaf refuses by indexed name | `IndexedDocumentsLeafRefusalTests` | ✅ COMPLIANT |
| Byte-Identical Under One Document | sealed corpus unaffected | live seal re-capture, 28/28 | ✅ COMPLIANT |
| Pair Wire Shape Only Under Two+ | two docs → two rev/sha pairs (live command output) | **none found** | ❌ **UNTESTED** |
| Pair Wire Shape Only Under Two+ | leak under one document is caught | `assertNotIn("documentRevisions",...)` on gate/offer/close real paths | ✅ COMPLIANT |
| Gate Authorization Binding Byte-Identical | fixture re-derives exact digest | `test_committed_token_rederives` | ✅ COMPLIANT (verified live, see above) |
| Gate Authorization Binding Byte-Identical | RED commit predates binding-shape commit | git ancestor check | ✅ COMPLIANT (verified live) |
| Gate Authorization Binding Byte-Identical | shape change caught before reaching target | live mutation, all 3 tests reddened | ✅ COMPLIANT (verified live, see above) |
| Position Header Pair Per Document | single-doc header still opens | `PositionModuleTests` + suite | ✅ COMPLIANT |
| Position Header Pair Per Document | two-doc header binds both pairs | `test_a_documents_group_round_trips_through_render_and_locate_block` (real 2-entry round trip through `render`/`locate_block`) | ✅ COMPLIANT |
| `admissibility.json` Dual-Shape | scalar-shape file still reads | `AdmissibilityDualShapeReadTests`, committed `scalar.json`+`r1.md` fixture (sha256 cross-checked, matches) | ✅ COMPLIANT |
| `admissibility.json` Dual-Shape | two-doc ruling keyed by document, independently readable | **none found** — `_admissibility_extra_documents` tested only for `len==1` (returns `[]`) | ❌ **UNTESTED** |
| `well_formed` Conditional On `document` | single-doc finding without `document` still validates | `test_well_formed_demands_document_only_when_required` | ✅ COMPLIANT |
| `well_formed` Conditional On `document` | two-doc finding without `document` refused | same test, `require_document=True` branch | ✅ COMPLIANT |
| Finding Names Either/Both, Impact Per-Document | finding against one document maps alone | `FindingsDocumentRoutingTests` | ✅ COMPLIANT |
| Finding Names Either/Both, Impact Per-Document | finding against both, uninterpreted | `FindingsDocumentRoutingTests` | ✅ COMPLIANT |
| `cmd_verify` Fidelity Per Document | single-doc result unchanged | seal `verify-a`/`verify-b`/`verify-t` byte-identical | ✅ COMPLIANT |
| `cmd_verify` Fidelity Per Document | two-doc run, two independent results | **none found** — `_extra_document_fidelity_status` unit-tested directly, never via `cmd_verify` dispatched under a real 2-doc profile | ❌ **UNTESTED** |
| Fixture + Pair Corpus Proves Every Branch | every pair branch named and reached | `tests/pair/` still has exactly the 2 Slice-A cases — see finding below | ❌ **FAILING** |
| Fixture + Pair Corpus Proves Every Branch | branch removed from corpus is caught | `test_every_case_has_a_golden_and_every_golden_has_a_case` (covers only those same 2 cases) | ⚠️ PARTIAL — mechanism exists, coverage it protects is incomplete |
| RED-First Commits Individually Verifiable | RED commit red in isolation, GREEN turns it green | 7 pairs spot-checked (`git merge-base --is-ancestor`, all test-only diffs) | ✅ COMPLIANT |
| Ten Domain Fields, Indexed (engine-neutrality) | missing leaf refuses by dotted/indexed name; changing one field moves only its digest; 2nd doc indexed refusal | full suite + `IndexedDocumentsLeafRefusalTests` | ✅ COMPLIANT |
| Non-Interference (cli-seal) | both baselines hold; sister dirs untouched; skipped-count pin | live `npm test`+Python suite, `git diff --stat d02496a..HEAD -- proposal-deliberation _core/deliberation` empty | ✅ COMPLIANT |
| Two-Document Branch Sealed By Own Corpus | existing 28 unaffected | live seal re-capture | ✅ COMPLIANT |
| Two-Document Branch Sealed By Own Corpus | every pair-shaped branch captured/digested | Slice A's 2 branches only; Slice B's ~20 new branches never added | ❌ **FAILING** (same root cause as above) |
| Two-Document Branch Sealed By Own Corpus | one-byte mutation in a pair golden is caught | manually confirmed, task 4.1 (reverted before commit) | ✅ COMPLIANT (for the 2 existing cases) |

**Compliance summary**: 25/30 scenarios compliant. **5 scenarios untested/failing, all one root cause.**

### THE finding: the pair corpus was never extended past Slice A — every Slice B branch's positive (two-document) direction shipped unproven

This is exactly the risk the proposal itself named "High" likelihood and built the fixture+corpus specifically to prevent (*"a branch no reachable configuration takes cannot be mutation-proven... an unprovable branch is the same defect one level up"*), and it is exactly what the launch brief asked me to check by execution. I did, and it does not hold for Slice B.

**What I measured, by name:**
- `tests/pair/cases.json` has exactly the same 2 cases it had after Slice A (`pair-two-documents-resolve`, `pair-second-document-missing-directory-refuses`), both driving the `name` command only. `tests/test_implementation_pair.py` is unchanged since Slice A (216 lines, same 4 classes). Slice B touched neither file.
- `grep -rn "two_documents" tests/` → the fixture is referenced **only** from `tests/pair/corpus.py`. No Slice B test (`test_proposal_implementation.py`, `test_implementation_authorization_binding.py`) ever loads it.
- `grep -n "impl.DOCUMENTS\s*=\|patch.object(impl, .DOCUMENTS.\|setattr(impl, .DOCUMENTS." tests/test_proposal_implementation.py` → zero hits. `DOCUMENTS` is never monkeypatched either.
- I count **24** `if len(DOCUMENTS) > 1:`-gated code sites across the engine (`position_state`'s `multi` branch — L637-654; `read_findings`'s `well_formed` call; `cmd_admit`'s `sources_by_document`/`documents` write — L7797, L7847; `admissibility_record`'s extra-documents read — L7898; `cmd_position` — L10771/10836/10923/10946/10956; `cmd_gate`/`cmd_offer`/`cmd_close` — L13515-14213; `cmd_verify`'s fidelity dispatch — L14839/15099). **None of these gates is ever exercised with `DOCUMENTS` genuinely holding 2 entries, anywhere in the test suite.**
- I read `position_state`'s own `if multi:` block (L637-654) directly: it is real, new, per-document logic (a `bound_to` mapping keyed by label, reading the header's additive `documents` list). The only test naming it, `test_position_state_accepts_extra_sources_and_stays_scalar_under_one_document`, exercises the **`else` branch only** — its own name says so.
- `_authorization_binding_keys`'s presence-triggered branch (`if "documentRevisions" in record_or_binding: return ... + ("documentRevisions",)`) is never called with a mapping that actually carries `documentRevisions`, anywhere — not even at the unit level. Both committed fixture events in `position.jsonl` are one-document (7-key/8-key) records.
- `_admissibility_extra_documents` is asserted only for the `len==1` case (`self.assertEqual(impl._admissibility_extra_documents("r1.md"), [])`).

**What this means concretely.** The "byte-identical under one document" direction — protecting every existing target's clone, today — is proven exhaustively, live, and by real mutation. The "produces a correct pair under two documents" direction — the entire *point* of this cut, the thing `experimental-implementation` is being built to eventually use — has not been run once, end to end, with a real two-document profile, for 6 of 8 site classes (C1, C3-write, C4's presence branch, C5, C7's caller gate, C8's caller gate). Only C2 (the `impl_position.py` grammar, which is domain-neutral and doesn't read `DOCUMENTS` at all) and C7/C8's pure downstream helpers (deliberately caller-gated, tested directly with hand-built pair-shaped arguments) are genuinely proven for both directions.

**This is disclosed, not hidden** — every affected test class's own docstring says so plainly (`LedgerDocumentRevisionsWiringTests`: *"a live two-document process cannot be reached inside this shared test session"*), and tasks.md records each as a deliberate "scoping decision." I record that candor. It does not change my reading that spec Requirement 10's MUST — *"the corpus... MUST reach every branch introduced by `len(documents) > 1`"* — is unmet for everything past Slice A's own two branches.

**Proposed resolution** (not applied — reporting only, per the verify contract): extend `tests/pair/cases.json`/`digests.json` with cases that drive `gate`/`offer`/`close`/`admit`/`position`/`verify` through a real subprocess against the two-document fixture profile (the same `_build_env_with_profile_override` wrapper Slice A's own pair driver already uses), and add a direct unit call to `_authorization_binding_keys` with a `documentRevisions`-carrying mapping. Until then, the two-document path this whole cut exists to enable is unverified in the one way this project has, by its own repeated statement, declared acceptable.

### Correctness (Static + Dynamic Evidence)
| Requirement | Status | Notes |
|---|---|---|
| RED-first git verifiability | ✅ Verified | 7 of 22 test/impl pairs spot-checked with `git merge-base --is-ancestor`; every RED commit touches test files only |
| No AI attribution in commits | ✅ Verified | `git log --format="%H %s" f5d2258^..c2a86c9` scanned, zero matches |
| Assertion quality (new/modified test code) | ✅ Verified | scanned full Slice A+B test diff (1455 diff lines) for tautologies/TODO/bare `pass` — zero hits |
| `discover_profiles()` doesn't pick up the fixture as a 3rd skill | ✅ Verified | globs `.claude/skills/*/`; fixture lives under `tests/fixtures/two_documents/`, outside that glob |
| `reachable_refusal_codes()` count is measured, not predicted | ✅ Verified | derived via AST closure-walk (not hardcoded); `assertEqual(len(reachable_refusal_codes()), 113)`; `SKILL.md` prose updated to 64 work-state codes |

### Six Design Predictions ("apply must measure, not repeat")
| # | Prediction | Measured? | Result |
|---|---|---|---|
| 1 | Five `documents.directory` movers reproduce as positive control | ✅ Yes (tasks.md 5.1) | Held exactly — `['admit-e0','close-e0','gate-e0','offer-e0','position-e0']` |
| 2 | A real minted authorization event exists or is minted with pinned session/at/mintOrdinal | ✅ Yes (tasks.md 6.3) | Neither existed; both fixture events freshly minted offline and committed |
| 3 | `reachable_refusal_codes()`'s new count | ✅ Yes (tasks.md 9.4) | 112 → 113, asserted in a derived (not hardcoded) test |
| 4 | Slice A moves zero digests | ✅ Yes (tasks.md 5.3) | Confirmed by seal re-run, not assumed from the accessor's shape |
| 5 | Which pair-corpus case reaches each new branch | ⚠️ Partial | Measured and named for Slice A's 2 branches only (task 4.2) — **never extended to Slice B's ~20 new branches; this is the root cause above, and the prediction was not carried forward, not flagged as dropped** |
| 6 | `well_formed`'s conditional leaves `admit-e1`/`handoff-e1`/`verify-a` identical | ✅ Yes (tasks.md 13.4) | Confirmed byte-identical across all 28 cases |

5 of 6 held cleanly. Prediction 5 is the one that quietly narrowed in scope without being named as narrowed — which is itself a smaller instance of the same pattern the design's own precedent (Cut 1's dropped predictions) warns against.

### Size — measured, not estimated

| Slice | Estimate | Actual (insertions+deletions, code only, excludes `openspec/`) | vs. estimate |
|---|---|---|---|
| Slice A (`f5d2258^..caf2f5f`) | ~480 ± 150 | **668** (621 ins + 47 del, 11 files) | Over upper bound (630) by 38 lines |
| Slice B (`caf2f5f..406b212`) | ~950 ± 150 | **1,227** (1,169 ins + 58 del, 9 files) | Over upper bound (1,100) by 127 lines |
| **Combined** | ~1,400–1,500 ± 150 | **1,895** (1,790 ins + 105 del, 19 files) | Over the cached **1,400-line session budget** by 495 lines (+35%) |

Generated-golden exclusion (`tests/pair/digests.json`, 12 lines) does not materially change this. Both slices individually exceeded their own error bar, and the combined total exceeds the session's cached review budget by more than a third — this is a real, measured overage, not the estimate holding. It does not block delivery on its own: `delivery_strategy: auto-chain` with a stacked-to-main chain was already decided and executed (2 separate PRs, each independently reviewable and independently under the 1,400 budget on its own — Slice A at 48%, Slice B at 88%). Flagged as WARNING so the reviewer of Slice B specifically knows it is the largest single PR this project has shipped under this budget, non-trivially over its own estimate.

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1a/D1c: `_AUTHORIZATION_BINDING_KEYS` stays a literal 8-tuple | ✅ Yes | Verified live, see Central Question |
| D1d: re-derivation test lands first | ✅ Yes | Git-ancestor verified |
| D2: site-class ordering (C4 first, then disk artifacts, then reads) | ✅ Yes | Commit order matches: `3aa2cee`(C4) → `abcfe50`(C3) → `fb16611`(C2) → `4f48a26`(C1) → `fbcd085`(C5) → structural-only(C6) → `ef3d2ab`(C7) → `406b212`(C8) |
| D3: position header optional trailing group, legacy opener frozen | ✅ Yes | Round-trip test confirms |
| D4: Slice A accessor keeps spelling, pure zero-delta | ✅ Yes | Seal unchanged after Slice A |
| D5: admissibility dual-shape read from a committed pre-cut fixture | ✅ Yes | `scalar.json`/`r1.md` sha256-consistent |
| D6: findings routing, verdict stays out | ✅ Yes | `finding_impact` returns uninterpreted per-document mapping only |
| D7: fidelity sibling key, never renaming | ✅ Yes | `fidelityByDocument` additive |
| D8: positive control runs first, under `.venv/bin/python` | ✅ Yes | Confirmed exact 5-id set |
| D9: fixture profile sanctioned location, pair corpus additive | ✅ Yes, but incomplete | Location/mechanism correct; **corpus itself never grown past Slice A — see finding above** |
| Testing Strategy row: "the pair corpus — every pair branch named, with the case id that reaches it" | ❌ **Not followed for Slice B** | The one design commitment this report finds unmet |

### Issues Found

**CRITICAL** (1):
- **The pair corpus was never extended past Slice A's 2 cases.** Every `len(DOCUMENTS) > 1` runtime branch introduced by Slice B (C1's `position_state` multi-document mapping, C3's admissibility write, C4's `_authorization_binding_keys` presence branch, C5's ledger `documentRevisions` spread at 8 sites across `cmd_gate`/`cmd_offer`/`cmd_close`, C7's `cmd_admit` caller gate, C8's `cmd_verify` caller gate — ~20 of the 24 engine-level `len(DOCUMENTS) > 1` gates) has never been exercised with a real two-document profile, by any test, at runtime. Spec Requirement "A Two-Document Fixture Profile And Pair Corpus Prove Every Pair Branch Before It Ships" is unmet as literally written. Disclosed candidly in test docstrings and tasks.md, but disclosure is not the same as the requirement being satisfied. **Resolution proposed, not applied**: extend `tests/pair/` with subprocess cases against the two-document fixture for `gate`/`offer`/`close`/`admit`/`position`/`verify`, plus a direct unit call proving `_authorization_binding_keys`'s presence branch.

**WARNING** (1):
- **Size**: both slices individually exceeded their own ±150 estimate upper bound, and the combined total exceeds the cached 1,400-line budget by 35%. Not blocking given the already-executed stacked-PR delivery strategy, but Slice B (1,227 lines) is a large single PR under any budget and should be reviewed as such.

**SUGGESTION** (1):
- Design's own "Six predictions apply must measure" item 5 quietly narrowed from "every new branch" to "Slice A's 2 branches" without being recorded as narrowed anywhere in tasks.md's own prediction tracking. A one-line note at Phase 15 close ("prediction 5 answered for Slice A only; Slice B deferred") would have surfaced the CRITICAL finding above at apply time instead of at verify time.

### Verdict

**FAIL.**

The central question this verify session was asked to spend its effort on — *would a token minted before this change still validate after it* — is answered **yes, unconditionally**, proven by live execution including a real forced mutation that reddened the guard and a byte-identical revert. Every other measured claim in Phase 15's self-report reproduced exactly under independent re-execution: 595/595, `Ran 2906`/`OK (skipped=6)`, 28/28 byte-identical seal digests captured live, sister directories untouched, RED-first git-verifiable, no AI attribution, zero trivial assertions.

The FAIL verdict rests entirely on one finding, orthogonal to the central question: this change's own explicit, repeatedly-stated acceptance bar — *a branch no reachable configuration takes cannot be mutation-proven, and an unprovable branch is the same defect one level up* — was met for Slice A and not for Slice B. The infrastructure Slice A built specifically to meet that bar (the two-document fixture profile and its pair corpus) was never extended into Slice B, so roughly 20 of Slice B's 24 new runtime branches ship with their two-document direction completely unexercised. This is not a guess about what might be wrong; it is a direct, named absence of coverage against this project's own spec-level MUST.
