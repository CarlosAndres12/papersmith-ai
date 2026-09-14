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

---

## RE-VERIFY (Cut 3, corrective apply, commit `cf50678` on top of `c2a86c9`) — amendment, prior FAIL preserved above

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:6018619a9fadc9ee9ab709d4f23d10e0f59b1bec
verdict: pass_with_warnings
blockers: 0
critical_findings: 0 (original CRITICAL substantially closed; 2 new WARNING-level residual gaps identified in the same site class, by execution)
requirements: 13/14 (RED-First requirement's literal git-isolation scenario structurally inapplicable to a coverage-only phase; substituted, not satisfied as literally worded)
scenarios: 28/30 (2 scenarios under "A Finding May Name Either Or Both Documents" remain unverified through the real caller-construction path, though verified at the pure-function level)
test_command: .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256(tests/seal/digests.json)=011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75 (unchanged, live-captured twice)
build_command: npm test
build_exit_code: 0
```

### Preflight

`ps aux | rg "unittest discover"` found a live foreign process at the start of this session (PID 70601) and again mid-session (PID 92542). Both resolved via `lsof -p <pid> | rg cwd` to `/Users/diego/.herdr/worktrees/papersmith-ai/paper-writing` — a different worktree, not this one. No concurrency conflict on this repo. No toy-target residue found (`git status --short --ignored=matching implementations/` showed only a live, git-ignored `_e2e_poll_first_piloted_8036/` scratch dir belonging to the in-progress suite run itself, not leftover from a killed process).

### Grep classification, re-verified independently

`grep -n 'len(DOCUMENTS) > 1' .claude/skills/_core/implementation/engine/implementation_engine.py` → **30** matches. Line numbers `514, 4029, 4564, 7875, 13708, 14177` read as docstring/comment prose on direct inspection (backtick-quoted phrases inside triple-quoted docstrings, one `#` comment) — **6**, matching the correction's claim exactly. The remaining **24** line numbers, after removing those six, match tasks.md 16.5's own listed 24 line numbers **exactly**, position for position. The 30/6/24 split is confirmed, independently, not re-read from the correction's own report.

### New test classes: run in isolation

`.venv/bin/python -m unittest tests.test_implementation_pair -v` → **10 tests, all pass, 2.2s** (`AuthorizationBindingKeysPresenceBranchTests` ×2, `TwoDocumentPositionWriteTests` ×1, `TwoDocumentLifecycleTests` ×1, plus the 6 pre-existing Slice A tests, unchanged). `git status --short` clean after the run.

### Mutation proof — five gates, independent of the correction's own named mutation (`_extra_document_revisions`)

Each mutated, run, observed, reverted with `git checkout --`, and confirmed byte-identical (`git status --short` empty, marker `grep -c` zero) before moving to the next:

| Line | Site (design.md class) | Mutation | Result |
|---|---|---|---|
| 518 | C1, `position_state`'s `multi` flag | `multi = len(DOCUMENTS) > 1` → `multi = False` | **Reddened** — `TwoDocumentLifecycleTests`: `AssertionError: 'current' is not an instance of <class 'dict'>` |
| 10836 | C2, `cmd_position`'s header-write gate | `if len(DOCUMENTS) > 1:` → `if False:` | **Reddened** — 2 tests failed (`TwoDocumentLifecycleTests`: `'documents=' not found`; `TwoDocumentPositionWriteTests`: `None != [{...}]`) |
| 7847 | C3, `cmd_admit`'s admissibility write | `if len(DOCUMENTS) > 1 else {}` → `if False else {}` | **Reddened** — `TwoDocumentLifecycleTests`: `'documents' not found in {...}` |
| 15099 | C8, `cmd_verify`'s `fidelityByDocument` fold | `if len(DOCUMENTS) > 1 else {}` → `if False else {}` | **Reddened** — `TwoDocumentLifecycleTests`: `KeyError: 'fidelityByDocument'` |
| **7797** | **C7, `cmd_admit`'s `sources_by_document` construction, feeding `finding_impact`** | `if len(DOCUMENTS) > 1:` → `if False:` | **Did NOT redden.** `tests.test_implementation_pair` (all 10 tests): OK. The full pre-existing `test_proposal_implementation.py` (**1477 tests**, includes `FindingsDocumentRoutingTests`, the file's own direct unit tests of `finding_impact`): **OK (skipped=2)**. Nothing anywhere in the suite noticed. |

4 of 5 independently chosen gates are genuinely reached **and** asserted — real, execution-verified proof, not a repeat of the correction's own claim. The fifth (**7797**) is reached (a real subprocess genuinely executes it — confirmed by reading the mutated-off run's own captured `admit` output during the 7847 mutation run, which showed `"impact": {"class": {"proposal": "local"}, ...}` computed and present, unchecked) but **its output is never asserted by any test, live or unit, anywhere in the suite**. Code inspection shows an identical pattern at **line 14839** (`verify_sources_by_document`, feeding `remedy_compatibility` inside `cmd_verify`) — same site class (C7), same construction-then-drop shape; `rg -n "compatibility" tests/test_implementation_pair.py` returns nothing. Not independently mutated (budget), but structurally the same defect, by inspection.

**Instruction 2's answer, by execution**: the correction's claim "all 24 real code gates are now reached and asserted against" (commit `cf50678` message) is accurate for **22 of 24**. For the remaining **2** (both C7, both feeding `finding_impact`/`remedy_compatibility`'s per-document `class`/compatibility mapping — spec's own "representation only, never a verdict" capability), *reached* is true and *asserted* is false, proven by mutation surviving the entire suite undetected.

### Instruction 1 verdict: is the original CRITICAL closed?

**Yes, for the authorization- and ledger-critical paths (C1–C5); no, not completely, for two representation-only C7 sites — and that residual gap is new information this session found, not carried over from the prior FAIL.**

- C4 (authorization binding growth) and C5 (ledger `documentRevisions` at 8 sites) — the paths that can actually corrupt a minted token or a ledger record — are **fully reached and asserted**, both by the correction's own `TwoDocumentLifecycleTests` (a real minted token, consumed by a real `gate` call, with `documentRevisions` asserted against both the JSON return and the raw `position.jsonl` ledger line) and by my own independent mutations at C1/C2/C3/C8 above.
- C7's two caller-construction sites (7797, 14839) are the only spot where "reached" and "asserted" diverge, and they feed a capability the spec itself scopes as **representation only** (`implementation-document-binding` spec: *"MUST NOT compute, print, or return a single word describing what a finding against both documents means"*) — lower stakes than the ledger/authorization paths, but the spec's own two scenarios under that requirement ("a finding against one document maps alone" / "a finding against both documents carries both classes, uninterpreted") are **not** proven through a real two-document profile's own caller construction, only through a hand-built unit-level call (`test_finding_impact_becomes_per_document_when_sources_given`, pre-existing, not new to this correction).

### Instruction 3 verdict: RED-first's absence, judged

Phase 16 lands as **one** `test(...)` commit, no implementation commit, with no RED phase in the git-verifiable sense the spec's own scenario describes (*"a work unit's test(...) commit, checked out alone... fails, and the following implementation commit turns it green"*). This is **structurally inapplicable** here, not skipped: the implementation these tests exercise already shipped in Slice B: checking out `cf50678` alone would find the tests **green immediately**, since nothing changed under them. There is no prior "RED" state for git isolation to demonstrate.

The correction substitutes a different, execution-based proof (task 16.4: force `_extra_document_revisions` to contribute nothing, watch two classes redden, revert byte-identically) to establish the new tests are not vacuous. **This substitution is sound in principle** — a runtime mutation sweep proves non-vacuousness at least as strongly as git-commit RED isolation does, for coverage-only work where no behavior changes. But the spec's "RED-First Test Commits Are Individually Verifiable" requirement, as literally worded, names no carve-out for coverage-only phases, so this remains a **literal, minor deviation** from a stated MUST — worth a one-line spec amendment naming the exception explicitly (mirroring how `implementation-cli-seal`'s Non-Interference requirement was itself corrected mid-cut to match measured reality), not a defect in the work performed.

### Instruction 4 verdict: the pair-corpus/golden-mechanism argument, judged

**Technically true, over-applied as a blanket excuse.** Reading `tests/seal/harness.py:run_case` directly confirms it: one `subprocess.run` call per case, against a **fresh** scratch target, one digest. It cannot represent a stateful sequence (mint a token in `offer`, consume it in `gate`, read accumulated ledger state in `close`/`admit`/`verify`) — the correction's reason for adding zero cases to `tests/pair/cases.json`/`digests.json` is **sound for the genuinely stateful branches** (C4's live-token binding, C5's cross-call ledger accumulation, the install→unchanged pair).

It is **not fully sound as a justification for adding zero cases across the board.** Some of the 24 gates are single-command-representable — e.g., C1's `probe`-only read (line 518, mutation-proven above) needs no state at all, and C2's absent-branch read (line 10771) fires against an empty target with no prior write. Either could plausibly have been captured as a byte-exact golden the same way most of the existing 28-case corpus already is.

More importantly: **the spec already names the exact escape valve for this situation**, and this codebase already implements it elsewhere. `implementation-cli-seal`'s own scenario reads: *"each pair-shaped case has a digest and exit status, **or is in an explicit unsealed set with a reason**"* — and `tests/seal/unsealed.json` (with its own three-test suite in `test_implementation_seal.py`: `test_every_case_is_either_sealed_or_declared_unsealed`, `test_the_unsealed_set_is_exactly_its_declared_membership`, `test_every_unsealed_entry_states_a_reason`) is that exact sanctioned mechanism, already used for `propose`'s one known non-deterministic case. `tests/pair/` has **no equivalent file** (`ls tests/pair/` → `__init__.py cases.json corpus.py digests.json`, nothing named `unsealed`). The correction explained its reasoning in prose (docstrings, commit message) instead of formalizing it the way this exact codebase already knows how to.

**Verdict on item 4: the argument is directionally correct but was not run through the mechanism the spec itself prescribes for this exact circumstance.** This is a real gap, not a phantom one — but it is a paperwork/formalization gap (add a `tests/pair/unsealed.json`, listing the genuinely-stateful branches with their reasons, and mutation-prove or golden-capture the handful of single-command-representable ones this report just showed are feasible), not a coverage gap — the actual gates ARE reached, by real two-document data, as instruction 1 confirmed.

### Re-confirmations, live

- **Seal digest**: `sha256(tests/seal/digests.json)` = `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` — captured **twice**: once statically before the full suite ran, once again after a **from-scratch, live, full `discover -s tests` run** (not replayed). Both identical, both match the required value. `git diff --exit-code -- tests/seal/` → exit 0, both times.
- **Pair goldens**: `git diff --stat cf50678~1 cf50678 -- tests/pair/` → empty. Untouched, confirmed.
- **`npm test`**: `tests 595 / pass 595 / fail 0 / skipped 0`, exit 0. Exact.
- **Python full suite**: `Ran 2910 tests in 504.481s` / `OK (skipped=6)`, exit 0. `skipped=6` unmoved from the pre-correction baseline (`Ran 2906`/`skipped=6`); `Ran` grew by exactly 4 — the 4 genuinely new test methods across the 3 new classes (`AuthorizationBindingKeysPresenceBranchTests` ×2, `TwoDocumentPositionWriteTests` ×1, `TwoDocumentLifecycleTests` ×1); the other 6 methods in the correction's diff belong to Slice A's pre-existing classes in the same file, already counted. Arithmetic reconciles exactly.
- **Sister directories**: `git diff --stat -- .claude/skills/proposal-deliberation .claude/skills/_core/deliberation` → empty. Untouched.
- **Central question, re-confirmed by static inspection** (no need to re-run the prior session's live mutation — nothing in its dependency chain moved): `_AUTHORIZATION_BINDING_KEYS` is still the literal 8-tuple `("jobName", "commit", "entrypoint", "units", "rung", "revisionSha256", "positionStatus", "proposalDigest")`, read directly at `implementation_engine.py:12859-12862`. `git diff --stat d02496a..HEAD -- tests/test_implementation_domain_lock.py` → **empty across the entire Cut 3 change**, not just the correction (`3b2f3c4`, the file's last touching commit, is a confirmed ancestor of Slice A's own start `f5d2258`). A token minted before this change still validates after it — unmoved.

### Size — measured, not estimated

| | Insertions+deletions (code only, excl. `openspec/`) | vs. 1,400-line budget |
|---|---|---|
| Prior FAIL total (Slice A + B) | 1,895 | +35% |
| This correction (`cf50678`, test-only, 1 file) | +512 | — |
| **New combined total** | **2,407** (2,302 ins + 105 del, 19 files) | **+71.9%** |

The overrun grew from +35% to +71.9% of the session's cached budget. Still not a blocker on its own (same reasoning as the prior report — stacked-PR delivery already executed), but now a materially larger single-session overage than what the first verify flagged, and worth surfacing again rather than silently absorbing.

### SUGGESTION, carried forward

Not addressed. `rg -n "prediction 5|narrowed"  openspec/changes/a-revision-is-two-documents/tasks.md` → no hits. Still open, still low-priority: a one-line note at Phase 16's own close, naming that this corrective phase closes the *reachability* half of the original gap but leaves a *representation-only assertion* half (this session's own new finding) would have been exactly the kind of self-flagging the original SUGGESTION asked for. Recommend folding both into one note if this change gets a Phase 17.

### Issues Found (this re-verify session)

**CRITICAL** (0, down from 1): The original finding — ~20 of 24 gates completely unreached by any two-document configuration — is closed. All 24 are now reached by real two-document subprocess data, confirmed independently (grep classification, 5 independent mutations, cross-checked against the correction's own listed line numbers).

**WARNING** (3, up from 1):
1. **(Carried, worsened) Size**: combined total now 2,407 lines against the 1,400-line budget, +71.9% (was +35%). Not blocking; same stacked-PR mitigation as before.
2. **(New) Two C7 gates reached but unasserted**: lines 7797 and 14839 (`finding_impact`/`remedy_compatibility`'s caller-side `sources_by_document`/`verify_sources_by_document` construction inside `cmd_admit`/`cmd_verify`) execute under a real two-document subprocess but their output is never checked by any test — confirmed for 7797 by mutation surviving the entire 1477+10-test suite undetected; 14839 confirmed identical by code+test-file inspection. **Proposed resolution**: add two assertions to the existing `TwoDocumentLifecycleTests.test_the_full_lifecycle_reaches_every_named_gate` — one on `admit`'s written `record["findings"]["pair-lifecycle-finding"]["impact"]["class"]` (already computed as `{"proposal": "local"}`, observed directly during this session's own mutation run), one on `verify`'s returned `compatibility`/equivalent field. No new test infrastructure needed; both sites are already reached by the existing lifecycle flow.
3. **(New) Pair corpus's "unsealed" escape valve was not used**: the spec's own named mechanism for "a branch that cannot be captured as a byte-exact golden" (`tests/seal/unsealed.json`'s pattern) was not replicated for `tests/pair/`, despite the correction's own valid architectural argument for *why* several branches cannot be sealed that way. **Proposed resolution**: add `tests/pair/unsealed.json` naming the genuinely-stateful branches (C4/C5's live-token mint-and-consume, the install→unchanged sequence) with reasons, mirroring `tests/seal/unsealed.json`'s own three-test enforcement suite; separately evaluate whether the single-command-representable branches (C1's bare `probe` read, C2's absent-branch read) can be added as actual new golden cases rather than exempted.

**SUGGESTION** (1, unchanged): carried forward, unaddressed — see above.

### Verdict

**PASS WITH WARNINGS.**

The CRITICAL this re-verify was launched to judge is substantially closed: all 24 real runtime `len(DOCUMENTS) > 1` gates are now reached by genuine two-document subprocess data (independently re-derived, not re-read from the correction's own report), and — for the authorization- and ledger-critical site classes (C1–C5, C8) — genuinely asserted, proven by 4 of 5 independently chosen mutations reddening exactly the right tests and reverting byte-identically. The fifth mutation (line 7797) surfaced a real, execution-proven residual: 2 of 24 gates, both in the same representation-only site class (C7), are reached without being asserted anywhere in the suite — new information this session found by doing exactly what the launch brief asked ("a test that runs is not a test that asserts"), not a re-statement of the original finding. Combined with a formalization gap around the pair corpus's own "unsealed" mechanism and a materially worsened size overage, this is not a clean close — but it is a real, substantial narrowing of the original CRITICAL (from ~20/24 completely unreached to 2/24 reached-but-unasserted, confined to a non-authoritative capability), and none of today's findings touch the ledger, authorization, or position-header mechanisms the original CRITICAL was most worried about. Both new WARNINGs have small, precisely-scoped, cheap fixes named above.
