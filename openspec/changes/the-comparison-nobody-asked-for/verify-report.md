# Verify Report — `the-comparison-nobody-asked-for`

**Date**: 2026-09-15
**Branch verified**: `unit6b-the-transition-undeclares` (`de92a07`), 12 commits ahead of `main` (`7ef1984`)
**Mode**: full artifact verification (proposal/specs/design/tasks all present)
**Method**: read-only. No source file was modified. No `git checkout`, merge, or push was performed. A disposable `git worktree` against `main` was created under the scratch directory for baseline comparison and removed afterward; the shared working tree was never touched.

## Summary verdict

**NOT clean — one WARNING finding.** Per the owner's own stated policy ("merge and push only if verification produces no findings"), this finding stops the close-out. It is not a functional defect in the shipped behavior — every requirement's own runtime scenario is verified true today — but it is a real gap in one test's forward-looking enforcement, and the instruction was explicit that any finding, however small, must be reported rather than silently waved through.

No CRITICAL issues were found. All 158 tasks are `[x]` and, on inspection, correspond to real, running, tested code — not just checked boxes.

---

## Test suite results

### JavaScript (`npm test`)
`640/640` passing. Untouched by this whole change (every unit's own report says so; confirmed no `.mjs`/`.ts` file appears in any commit's diff across the 12-commit chain).

### Python — `tests.test_proposal_implementation` (the module every unit's own report measures)
Run on **HEAD** (`de92a07`): **1650 tests, 25 failures + 7 errors + 1 skipped = 32 anomalies.** Matches the standard every unit in this chain reported.

Run on **`main`** (`7ef1984`, via a disposable worktree, never the shared tree): **1492 tests, 24 failures + 7 errors + 3 skipped.**

**Regression proof — by membership, not count, as instructed.** The full sorted list of `FAIL:`/`ERROR:` lines from both runs was diffed directly (`diff main_failids.txt head_failids.txt`):

```
30a31
> FAIL: test_verification_notebook_executes_and_stamps (tests.test_proposal_implementation.FreshFlowATargetEndToEndTests.test_verification_notebook_executes_and_stamps)
```

Exactly **one** entry differs. It is a **new test** (`FreshFlowATargetEndToEndTests` is new in this change, added by Unit 3), not a regressed old one, and its traceback is the identical `ModuleNotFoundError: No module named 'numpy'` every one of the other 31 pre-existing failures already carries — confirmed by reading the traceback directly, not by trusting the classification. This matches Unit 3's own report exactly ("the 32nd instance of the one confirmed-pre-existing class"). **Zero unexplained differences. Zero regressions.**

The skip counts differ (main: 3, HEAD: 1) but this was not run down to full resolution — both files have exactly the same two `skipTest` call sites (checked via `rg`), one of which never fires (an `implementations/` repository is present) and one of which always fires in this sandbox (no `torch`). Skips are not failures and do not bear on the regression proof above; noted here as an open, non-blocking observation rather than silently omitted.

### Other Python suites (HEAD, foreground, all green)
- `tests.test_implementation_domain_lock`: 28/28
- `tests.test_implementation_seal`: 44/44
- `tests.test_experiments_seal`: 28/28
- `tests.test_implementation_pair` + `tests.test_experimental_implementation`: 101/101
- `TransitionTests` (Unit 6b's own class), `AcidTestInvariantTests`, `AcidTestLadderThreeWayTests`, `AcidTestShadowEnumerationTests`, `AcidTestRemotePlacementTests`, `AcidTestRemoteExecutionIntegrationTests`, `AcidTestKitGuidanceTests`, `AcidTestNoCrossSkillReachTests`: 33/33
- `ForgeVocabularyDerivedGuardTests` + `ReportFirstSectionProseTests`: 34/34
- `DeclinedComparisonTests` (includes the absent-token migration end-to-end test): 24/24

All of these are subsets of the full 1650-test run above and are broken out here because the task specifically asked they be checked; none surfaced anything the full-suite run did not already show.

---

## Directive 1 — No regression

Verified true, both by the suite-membership diff above and by reading the specific tests that exist to prove each spec's preserved-behaviour requirements would fail if the behaviour broke (not merely "the suite is green"):

- **`implementation-comparison-deferral`**: `MaterializeScaffoldAgreementTests` (both sites agree "by construction" — `scripts/materialize.py` now loops over `scaffold_destinations()` directly rather than re-declaring it — and `test_disagreement_is_caught_and_names_the_divergent_entry` proves the check is reachable-red, not vacuous); `OBJECT_MAP_NOT_APPROVED` is asserted at 16 call sites; the "spurious staleness" scenario has a test citing the spec scenario by name (line 9146); `previous_implementations()`'s own docstring and the exclusion behavior were read directly at source.
- **`implementation-declined-comparison`**: `DeclinedComparisonTests` (24/24, including `test_a_legacy_declined_bucket_with_no_token_stays_declined`, the exact end-to-end proof of the absent-token migration rule); `AcidTestShadowEnumerationTests` (proves a genuinely-owed repair still outranks a declined/unresolved/accepted-but-unbuilt decision — rewritten by Unit 3 specifically to assert the corrected, opposite invariant under renamed tests, not a silently-flipped assertion); `TransitionTests` (13/13, including the source-scan proof that `already-benchmarked` is structurally isolated from the `absent`-status override chain).
- **`implementation-engine-neutrality`**: see the anti-leak section below.

## Directive 2 — No product leakage ("a forge of papers, not of one paper")

**Anti-leak guard results**: `ForgeVocabularyDerivedGuardTests` (Rule A + Rule B) and `ReportFirstSectionProseTests` (Rule C, `FORGE_VOCABULARY_FLOOR`) — **34/34 passing**, including the three mutation-style tests that prove the widening actually bites rather than passing because it still cannot see:
- `test_the_compound_survives_even_though_both_parts_are_admitted` — a target name built from two individually-admitted words (this repository's own case: `Domain_Adaptation` → `domain` + `adaptation`, both legitimately in `FORGE_LEXICON`) is still caught as its own undivided compound.
- `test_the_word_boundary_actually_matches_a_real_compound_mention` — proves `\b` treats `_` as a word character correctly for the compound form.
- `test_rule_b_names_the_file_and_the_word_a_planted_leak_is_in` — a planted leak is caught and named, not silently missed.

Read directly at source (`tests/test_proposal_implementation.py:14378-14558`): `target_words()` adds `target.name.lower()` as an undivided candidate (not only its decomposed parts); `word_appears()` compares with `re.IGNORECASE`; `rule_b_documents()` widens the scan to every `tests/*.py` module's own comments/docstrings (via `tokenize`/`ast`, deliberately excluding ordinary string-literal fixture data) — exactly what design.md D24 and the delta spec claim.

**Independent sweep** (not trusting the guard's own report): read `implementations/` directly, since it is gitignored and a repo-wide `rg` would silently miss it.
- One target present: `implementations/Domain_Adaptation`, with packages `CREDA`, `MIL_CREDA`, `MIL_CREDA_Benchmark`.
- `rg -ni "domain_adaptation|domain adaptation"` across `.claude/` and `tests/`: **zero hits**.
- `rg -ni "\bcreda\b|\bmil\b|mil.creda"` across `.claude/` and `tests/`: the only hits are (a) `.claude/skills/proposal-deliberation/profile.ts`, which is the **declared, argued exemption** in `FORGE_FLOOR_SURFACE_ADMISSIONS["proposal-deliberation/profile.ts"]` (line 8315 of the test file) — the sanctioned domain-profile mechanism, explicitly reasoned and tested from both directions (an admission nobody argued fails one test; an admission whose file no longer carries the word fails the other); and (b) the guards' own fixture vocabulary lists (`tests/forge_vocabulary.py:FORGE_TARGET_PROPER_NOUNS`, `tests/test_remote_execution.py:TARGET_LITERALS`), which exist to prove the guards catch these words if planted — not leaks themselves.

**Result: clean.** No unargued mention of the live target's vocabulary, in any casing, anywhere under `.claude/` or `tests/`.

---

## Specific claims re-measured (not trusted)

1. **Unit 3's ladder-ordering correction still holds; a genuinely owed repair still outranks the offers.** Read `cmd_probe` directly (`implementation_engine.py:3866-4010`): every repair override (`declare-first`, `env-first`, `wiring-first`, `poll-first`, `pilot-first`, `pilot-decisions`, `search-first`, `report-first`) is an `elif` chained on `next_step in ("benchmark", "piloted")`, evaluated **before** the three-way `declined`/`build-first`/`validate` branch, which is gated separately on `next_step == "benchmark" and resolved["status"] == "absent"`. Structurally last, exactly as D13 and Unit 3's own correction state. Confirmed further by `AcidTestShadowEnumerationTests.test_every_repair_override_still_outranks_a_declined_comparison` and `.test_every_repair_override_still_outranks_an_accepted_but_unbuilt_decision`, both green.

2. **`validate` is reachable from `already-benchmarked` only.** Confirmed by source scan, as 6b claims: `next_step` is set to `"already-benchmarked"` exactly once (line 3688), and every override between that point and the new isolated `if next_step == "already-benchmarked" and len(comparison_arms) > 1 and (reuse_question not in answered): next_step = "validate"` (line 4033) is gated on `next_step in ("benchmark", "piloted")` — a condition that is structurally false once `next_step == "already-benchmarked"`. The new branch is a **separate `if`**, never chained onto the `resolved["status"] == "absent"`-guarded `elif` chain, so no existing rung's position moved. `TransitionTests.test_already_benchmarked_is_structurally_isolated_from_the_absent_status_chain` proves this too, green.

3. **The absent-token migration rule does not re-fire a declined offer on an existing target's first pass.** `_decision_token_from_event()` (line 13293) reads `event is None` → `"no"`, and an event with no `decision` field → `"no"` (`event.get("decision") == "yes"` is `False` for a missing key) — both cases preserve exactly what an already-declined bucket reported before this capability existed. `DeclinedComparisonTests.test_a_legacy_declined_bucket_with_no_token_stays_declined` proves this end-to-end: `probe["nextStep"] == "declined"` and both decisions read `"no"`. Green.

4. **Unit 3's derived-count test — does it actually catch a planted literal? Partially, with a specific gap named.**
   - `test_scaffold_gaps_maximum_is_derived_not_transcribed` computes both figures from the live functions (`len(scaffold_destinations("Method")) == 10`; `scaffold_gaps()` run against a real empty directory, asserted `<= 12`), never from a hand-copied list — this genuinely proves the **code** computes the bound rather than transcribing it.
   - `MaterializeScaffoldAgreementTests` proves the two independent destination lists (`implementation_engine.py`'s and `scripts/materialize.py`'s) agree **by construction** (the script now loops over the shared function), with a reachable-red test (`test_disagreement_is_caught_and_names_the_divergent_entry`) proving the comparison is live.
   - **The gap**: `DerivedScaffoldCountSweepTests` (the doctrine-file sweep, `tests/test_proposal_implementation.py:10105-10156`) only denylists the **old, retired** stale numbers — `STALE_COUNT_WORDS = ("eleven", "seventeen", "thirteen")`. It does **not** include `"twelve"` itself. I checked today's doctrine files (`SKILL.md`, `references/usage.md`, `README.md`) by hand for a `"twelve"` beside scaffold/destination/kit context and found none (`references/usage.md`'s one `"Twelve more are reported"` hit is about an unrelated `verify` finding-kind list, not the scaffold gap report) — **so the current state is correct**. But if a future edit hand-writes `"twelve"` into doctrine prose describing the scaffold gap report (exactly the failure mode the spec requirement exists to prevent), this specific sweep test would not catch it, because `"twelve"` was never added to its own denylist. This is the one WARNING this report raises.

---

## Per-spec requirement verdicts

### `implementation-comparison-deferral`
All 15 requirements verified true against running code and passing tests: scaffold stage excludes the benchmark package (10-entry list, confirmed); the declaration lives in the method's own package; `__levels__`/`__steps__`/`__records__` relocate and resolve identically; first-flow commands are unaffected by benchmark-package absence; `revision`'s two readers both preserved (drift + revision-family, spurious-staleness scenario explicitly tested); the existence gate is unchanged in behavior; `premises` stays write-only; the notebook stamps from the new `report_digest.py` location; `harness_destinations()` grew to 4 entries, benchmark package written only on acceptance; the baseline finder excludes `_Benchmark`-suffixed directories; the five remaining declaration blocks keep their three-way resolution; fidelity reporting is unchanged; every pre-existing probe rung fires unchanged; materialization-receipt drift/adopt machinery still operates; both scaffold mappings agree by construction; and the pre-existing-declaration migration is a named, one-time, full-literal-preserving remedy (`OBJECT_MAP_AT_OLD_HOME`, read directly at source, names both locations and explicitly preserves unread literals) — dedicated migration test found at `tests/test_proposal_implementation.py:18414/18511`.

**Unverifiable as written**: none. Every requirement had a locatable, running, passing covering test or a directly-inspectable code path.

**Not met**: none.

### `implementation-declined-comparison`
All requirements verified true, including the reopening/migration/transition requirements added in the seventh spec revision: bare-`discuss`-event persistence; single construction site for both question texts (`test_only_one_place_in_the_engine_builds_this_sentence`, `test_a_single_construction_site_is_enforced`-style tests all green); stability rules for both the comparison and acid-test offers; ledger-append-order tie-breaking; the reopen-on-answer-alone rule and its report-first-guard sibling (both source- and test-verified above); the one-time baseline-finder-fix re-fire; the acid-test offer's full text/cost/placement/job-name/service/remote-routing requirements (`AcidTestRemotePlacementTests`, `AcidTestRemoteExecutionIntegrationTests`, all green); the "materializes nothing up front" and "writes only into the method's own surfaces, never benchmark-named" invariants (`AcidTestInvariantTests`, both local and remote placements, green); the two transition requirements (`TransitionTests`, 13/13 green, including the "evidence is never deleted" requirement).

**Unverifiable as written**: none.

**Not met**: none functionally; see the WARNING above regarding the derived-count enforcement's forward coverage, which is adjacent to (not strictly inside) this spec's own requirement text but was specifically asked to be re-measured.

### `implementation-engine-neutrality` (delta)
Both ADDED requirements verified true: case-insensitive matching (`re.IGNORECASE`, read at source and proven by test) and the widened commentary scan (comments/docstrings under `tests/`, read at source and proven by test) close exactly the measured gap the delta names. Independent sweep (above) found no further leak.

**Unverifiable as written**: none. **Not met**: none.

---

## Overall verdict

**One WARNING, no CRITICAL.** Every requirement in all three delta specs is held true by running, passing tests today, and the two owner directives (no regression, no leakage) both hold under direct measurement — not merely a green suite. The single finding is narrow and forward-looking: `DerivedScaffoldCountSweepTests`'s doctrine sweep does not include `"twelve"` in its own denylist, so it would not catch a *future* hand-written "twelve" describing the scaffold gap report, even though no such literal exists today.

Per the owner's own stated policy, this finding — however small — **stops the close-out**: this change is **not** clear for merge/push until the owner has seen this report and either accepts the residual risk explicitly or asks for `STALE_COUNT_WORDS` to be widened to include `"twelve"` (a one-line, easily-scoped fix, not a design change).

## Citations checked

Every file path, function name, and test-class name cited in this report was located by name in the source and re-read at its current location, not inherited from tasks.md's own "What Unit N reported" prose or from apply-progress. Line numbers cited are as observed during this verification pass on `de92a07` and will drift on the next edit, per the standing convention.
