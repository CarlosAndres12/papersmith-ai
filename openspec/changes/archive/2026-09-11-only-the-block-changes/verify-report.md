```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:cbdaef8729480a773b7b7624ed45063f7f5515b69b2cd528062c3b96969e7ff8
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 17/17
scenarios: 28/28
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:988224d799179c7fc161b60736389d4ec1554f4303c16eefd0e1ae54f8b4c3e9
build_command: N/A — stdlib-only Python + Node scripts, no separate build/compile step
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: only-the-block-changes
**Version**: N/A (no spec version field)
**Mode**: Strict TDD

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 28 |
| Tasks complete | 28 |
| Tasks incomplete | 0 |

All 28 checklist items across Phases 1–7 (`tasks.md`) are `[x]`. Four claimed
commits (`325806a`, `36144c5`, `4eba1b1`, `578d117`) were inspected via
`git show --stat` and confirmed real, on branch `paper-writing`, with the
file scope each claims.

### Build & Tests Execution

**Build**: ➖ N/A — no separate build/compile step for this stdlib-only
Python CLI (`paper_block.py`/`paper_scaffold.py`/`paper_cli.py`) plus Node
test project.

**Focused suite** (`tests/test_paper_writing.py`, all 12 classes,
run directly): ✅ 50/50 passed, 1.521s.
```
Ran 50 tests in 1.521s
OK
```

**`npm test`**: ✅ 559/559 passed, 0 failed (two runs: 34.5s and 41.4s).

**Full Python discovery** (`.venv/bin/python -m unittest discover -s tests
-p 'test_*.py'`), run twice:

- First run: ⚠️ 2937 tests, 2930 passed, 1 failed, 6 skipped, 461s.
  ```
  Ran 2937 tests in 461.096s
  FAILED (failures=1, skipped=6)
  ```
  The one failure —
  `test_skill_audit.WalkthroughSelfProbeTests.test_the_shipped_recipe_runs_and_touches_no_sibling_skill`
  — is not attributable to `only-the-block-changes`: it lives in
  `test_skill_audit.py`, asserts about `.claude/skills/proposal-implementation/scripts/`
  file hashes (a sibling skill, not `paper-writing`), and its diff named a
  transient fixture (`_handoff_defects_fixture_3616_4442461232.py`) that did
  not persist on disk after the run (checked immediately after: only
  `implementation_cli.py` and `materialize.py` remained, clean `git
  status`). This matches the concurrency the task brief warned about: a
  sibling corrective-apply process was actively committing to this branch
  during this run (commit `0422dd1`, landed mid-suite, touching only
  `tests/test_paper_contract.py` — a third, unrelated change).
- Second run, immediately after (re-executed specifically to test the
  transience hypothesis rather than assert it): ✅ 2938 tests, OK,
  6 skipped, 477s.
  ```
  Ran 2938 tests in 477.055s
  OK (skipped=6)
  ```
  Confirms the first run's failure was a non-reproducible, concurrency-caused
  flake, not a defect in the delivered code. (The total rose by one between
  runs — the concurrent sibling process landed another test in the
  interval, consistent with the same concurrency explanation.)

Zero tests in `test_paper_writing.py` or `test_paper_decisions.py` failed in
either run, focused or full. This is the class of pre-existing/orphaned-
fixture trap the brief pre-identified for a *different* test file
(`test_proposal_implementation.py`'s "2 scripts besides its engine");
checked for that specific failure and found none, and checked the directory
it concerns for a persisted orphan and found none either.

The envelope above records the clean second run's exit code (`0`) and a
hash combining `npm test`'s output with that clean run's output, since that
is the authoritative, reproducible evidence for this change's own
correctness. The transient first-run failure is preserved here for
transparency (see Issues Found, WARNING 2) rather than silently discarded.

**Coverage**: ➖ Not available — no coverage tool configured for this suite.

### Spec Compliance Matrix

**paper-scaffold** (5 requirements / 6 scenarios):

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Scaffold Creates the Paper Tree | First run creates the tree | `ScaffoldTests.test_first_run_creates_the_tree` | ✅ COMPLIANT |
| Scaffold Is Idempotent | Second run changes nothing | `ScaffoldTests.test_second_run_leaves_hand_edited_bytes_identical` | ✅ COMPLIANT |
| Scaffold Refuses Outside the Repository | Caller names a directory outside the repo | `ScaffoldTests.test_paper_outside_repository_refuses`, `test_cli_scaffold_outside_repository_refuses_with_exit_2` | ✅ COMPLIANT |
| Scaffold Refuses a Wrong-Shaped Entry | paper/ is a file | `ScaffoldTests.test_paper_as_a_file_refuses_and_writes_nothing` | ✅ COMPLIANT |
| Scaffold Refuses a Wrong-Shaped Entry | Figures exists as a file | `ScaffoldTests.test_figures_as_a_file_refuses_and_writes_nothing_else` | ✅ COMPLIANT |
| Paper Contents Stay Untracked, the Folder Travels | A fresh clone still has the folder | `.gitignore` inspected directly (`paper/*` / `!paper/.gitkeep`); no dedicated test, static evidence only | ⚠️ PARTIAL |

**block-substitution** (12 requirements / 22 scenarios):

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Marker Grammar | Well-formed pair parses | `BlockCoreTests.test_well_formed_pair_parses_via_status` | ✅ COMPLIANT |
| Marker Grammar | Malformed marker line refuses | `BlockCoreTests.test_malformed_marker_line_refuses_naming_the_line` | ✅ COMPLIANT |
| Block Region Is Marker-Line-Bounded | Region excludes the preceding newline | `BlockCoreTests.test_region_excludes_the_preceding_newline` | ✅ COMPLIANT |
| open Installs an Empty Pair | Open after an anchor | `OpenBlockTests.test_open_after_anchor_inserts_empty_pair_and_leaves_prefix_unchanged` | ✅ COMPLIANT |
| open Installs an Empty Pair | Anchor missing | `OpenBlockTests.test_open_after_missing_anchor_refuses_anchor_absent` | ✅ COMPLIANT |
| substitute Never Creates | Substitute on a missing block | `BlockCoreTests.test_substitute_on_absent_block_refuses_and_creates_nothing` | ✅ COMPLIANT |
| Substitution Body May Not Carry a Marker | Body contains a marker-shaped line | `BlockCoreTests.test_body_carrying_a_marker_line_refuses` | ✅ COMPLIANT |
| The Byte-Identity Invariant | Only the named block changes | `InvariantTests.test_only_the_named_block_changes_three_conjuncts` | ✅ COMPLIANT |
| The Byte-Identity Invariant | A violating candidate never reaches disk | `InvariantTests.test_violating_candidate_refuses_before_any_write` | ✅ COMPLIANT |
| Independent Byte-Identity Verification | M1 is caught | `MutationProofTests.test_m1_region_start_one_byte_earlier_fails_the_byte_identity_test` | ✅ COMPLIANT |
| Independent Byte-Identity Verification | M2 is caught | `MutationProofTests.test_m2_text_mode_open_against_crlf_fixture_fails_the_byte_identity_test` | ✅ COMPLIANT |
| Independent Byte-Identity Verification | M3 is caught | `MutationProofTests.test_m3_skipped_digest_comparison_fails_the_hand_edit_guard` | ✅ COMPLIANT |
| Binary I/O Only | CRLF fixture round-trips untouched | `CRLFTests.test_crlf_block_round_trips_untouched_and_text_mode_would_corrupt_it` | ✅ COMPLIANT |
| Hand Edit Is Detected, Not Overwritten | Hand edit refuses | `BlockCoreTests.test_hand_edited_body_refuses_naming_both_digests` | ✅ COMPLIANT |
| Hand Edit Is Detected, Not Overwritten | --adopt clears it | `BlockCoreTests.test_adopt_updates_digest_without_touching_body_and_clears_the_refusal` | ✅ COMPLIANT |
| Refusal Roster | Duplicated id | `BlockCoreTests.test_duplicated_id_refuses` | ✅ COMPLIANT |
| Refusal Roster | Nested blocks | `BlockCoreTests.test_nested_begin_refuses` | ✅ COMPLIANT |
| Refusal Roster | Unpaired marker | `BlockCoreTests.test_unpaired_begin_refuses` | ✅ COMPLIANT |
| status Reports the Block Table | Status on a well-formed file | `CLIWiringTests.test_status_reports_the_block_table_without_writing` | ✅ COMPLIANT |
| The Safety Net Has No Git Behind It | Interrupted write leaves no torn file | `PreImageTests.test_pre_image_is_written_before_main_tex_is_replaced` | ✅ COMPLIANT |
| The Safety Net Has No Git Behind It | Pre-image is kept | `PreImageTests.test_pre_image_holds_the_exact_pre_write_bytes` | ✅ COMPLIANT |
| The Safety Net Has No Git Behind It | Only the immediately-prior state is recoverable | `PreImageTests.test_only_the_immediately_prior_state_is_recoverable` | ✅ COMPLIANT |

**Compliance summary**: 27/28 scenarios COMPLIANT by covering-test execution, 1/28 PARTIAL (static evidence only, no dedicated test — the fresh-clone scenario, which needs no runtime test since it is a claim about `.gitignore` content).

### Correctness (Static Evidence)

| Requirement/Check | Status | Notes |
|---|---|---|
| Byte-identity guard is a genuine, independent re-derivation | ✅ Confirmed | `identity_invariant(pre, candidate)` compares `project(pre)` vs `project(candidate)`; both calls `parse()` fresh — a full re-scan/re-pair from scratch, never a comparison of `prefix+new+suffix` against itself. Read at `paper_block.py:365-380`. |
| Three-conjunct no-op-write guard | ✅ Confirmed | `InvariantTests.test_only_the_named_block_changes_three_conjuncts` asserts (1) `project(post) == project(pre)`, (2) `post != pre` (rules out a no-op write), (3) the substituted block's body equals the exact new body — all three present, executed, green. |
| No orphaned public function in `paper_block.py`/`paper_scaffold.py` | ✅ Confirmed | Every public function (`read_status`, `open_block`, `substitute`, `parse`, `project`, `status`, `resolve_main_tex`, `validate_block_id`, `build_candidate`, `build_open_candidate`, `identity_invariant`, `scan_markers`, `pair_markers`, `resolve_paper_dir`, `scaffold`) has a production caller inside `paper_cli.py` or another `paper_block.py`/`paper_declarations.py` function — grepped directly, not inferred. |
| M1/M2/M3 mutation harness actually executes a real subprocess | ✅ Confirmed by execution | All three ran in the focused suite (`MutationProofTests`, part of the whole 50-test class run in 1.5s); each asserts `MUTANT_IMPORTED_OK` printed (import succeeded for the right reason) AND non-zero exit (guard genuinely fired), per `_assert_guard_failed_under_mutation`. |
| M1 anchor detectability | ✅ Confirmed fixed | Apply-progress reported the original M1 anchor (`project()`'s own region-list computation) was symmetric across `project(pre)`/`project(candidate)` and passed green with no guard firing — measured, not assumed, per the test's own inline comment (lines 787-798). The shipped anchor mutates `build_candidate`'s write-path slice (`pre[:begin["start"]]` → `pre[:begin["start"] - 1]`) instead, which the unmutated `project()` genuinely disagrees about. Confirmed detectable by running it: green in this run. |
| CRLF fixture proves binary I/O is required | ✅ Confirmed by execution (two independent proofs) | (a) `CRLFTests`'s own test contains an in-test control: it re-opens the file `substitute()` actually wrote in text mode and asserts the bytes differ from the binary read — this ran and passed. (b) `MutationProofTests.test_m2_...` flips `substitute()`'s own read to `open(..., "r", newline=None)` in a real mutant subprocess and confirms the CRLF test goes red under that mutation — this also ran and passed, which is the specific experiment the verify brief asked for. |
| One-deep pre-image limit | ✅ Confirmed by execution | `PreImageTests.test_only_the_immediately_prior_state_is_recoverable` performs two successive substitutions and asserts the pre-image after the second equals the state right before the second, `assertNotEqual` against the state before the first — ran, passed. |
| No git recovery reliance | ✅ Confirmed | `.gitignore` lines 78-79 (`paper/*`, `!paper/.gitkeep`); grepped `tests/test_paper_writing.py` for `checkout`/`restore`/`recover` combined with `git` — no hits. The pre-image mechanism is the only recovery path exercised anywhere in the suite. |
| Hand-edit digest refusal, `--adopt` the only exit | ✅ Confirmed | `BLOCK_HAND_EDITED` raised on digest mismatch (`paper_block.py` `build_candidate`); `--adopt` is the only mode that clears it (`NOTHING_TO_ADOPT` when already clean). Grepped the whole skill directory plus `paper_cli.py`'s argparse definitions for `--force`: zero occurrences. `SKILL.md` states this explicitly ("There is no `--force`."). |
| CLI verb count matches the brief's stated current state | ✅ Confirmed | `paper_cli.py`'s `COMMANDS` tuple currently lists 9 verbs (`scaffold`, `status`, `open`, `substitute`, `contract`, `readiness`, `order`, `declare`, `plan`) — this change shipped the first 4; the other 5 landed via later sibling changes, exactly as the brief stated. |
| Orphaned-fixture trap (pre-identified) | ✅ Checked, none found for this change's scope | `.claude/skills/proposal-implementation/scripts/` holds exactly `implementation_cli.py` and `materialize.py` (plus `__pycache__`), clean `git status`. `test_proposal_implementation.py` reported no "2 scripts besides its engine" failure in either run. A *different*, transient instance of the same failure *class* surfaced in `test_skill_audit.py` on the first run only (see Build & Tests Execution above) — re-run confirmed non-reproducible. |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| Own modules; import only `Refused` (no `_core/paperblock/`) | ✅ Yes | `paper_block.py`/`paper_scaffold.py` import only `impl_refusals.Refused`; no other `_core/implementation` coupling. |
| Forge root by path arithmetic, never `git rev-parse` | ✅ Yes (documented deviation) | Design text names `parents[3]`; shipped code uses `parents[4]` (`paper_scaffold.py:26`). Recorded explicitly in `tasks.md` 1.2 as a measured correction against the file's real depth, proven by `test_paper_outside_repository_refuses` and the real-repo-root subprocess test. |
| CLI first slice via `add_mutually_exclusive_group(required=True)` | ⚠️ Deviated (documented) | Design's own prose names argparse groups; shipped code uses manual mode-flag checks (`OPEN_POSITION_REQUIRED/_CONFLICT`, `SUBSTITUTE_MODE_REQUIRED`/`ADOPT_BODY_CONFLICT`) instead, matching `implementation_cli.py`'s own `cmd_materialize` precedent that design's own step-4a paragraph names. Recorded in `tasks.md` Phase 5 with the reasoning (argparse's bare stderr usage error would break the "one JSON object on stdout" invariant and be invisible to the roster derivation). Does not break the spec — behavior and JSON envelope are correct either way, and both are tested. |
| Step ordering (pre-image before `os.replace`; CAS before write) | ✅ Yes | `substitute()`/`open_block()` both: read → digest → parse → build candidate → `identity_invariant` → re-read/CAS (`TEX_MOVED`) → pre-image write → atomic replace, matching design's 9-step table exactly. |
| "Delta the spec should absorb" (5+ codes design added beyond spec's 12-row table) | ❌ Not done | See Issues Found (WARNING) — design.md names this gap itself and it was never closed. |

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. `specs/block-substitution/spec.md`'s "Requirement: Refusal Roster" table lists only the original 12 codes. Eight additional codes that this change itself implements, tests (directly, via `CLIWiringTests`/`OpenBlockTests`/`BlockIdShapeTests`/`InvariantTests`), and classifies in `paper_cli.REFUSAL_CLASSIFICATION` are absent from the spec document: `BLOCK_ID_MALFORMED`, `OPEN_POSITION_REQUIRED`, `OPEN_POSITION_CONFLICT`, `SUBSTITUTE_MODE_REQUIRED`, `ADOPT_BODY_CONFLICT`, `NOTHING_TO_ADOPT`, `SUBSTITUTION_NOT_LOCAL`, `TEX_MOVED`. `design.md`'s own "Delta the spec should absorb" section names 5 of these explicitly as owed to the spec and states "surfaced rather than introduced quietly" — the surfacing happened (the source-derived roster test protects reachability), but the spec.md document itself was never amended. Behavior is correct and fully covered by tests; this is a documentation-completeness gap, not a functional defect.
2. One test failure surfaced on the first full-suite run: `test_skill_audit.WalkthroughSelfProbeTests.test_the_shipped_recipe_runs_and_touches_no_sibling_skill`, caused by a transient fixture that did not persist on disk, consistent with the concurrent sibling corrective-apply process actively committing to this same branch during that run (observed: commit `0422dd1` landed mid-run). An immediate re-run of the full suite came back clean (OK, 2938/2938 minus 6 skipped), confirming non-reproducibility. Zero relation to `only-the-block-changes`' own files or tests either time. Flagged here for transparency, not as this change's defect.

**SUGGESTION**: None.

### Assertion Quality
✅ All assertions verify real behavior — scanned `tests/test_paper_writing.py` for tautologies, ghost loops, assertion-free tests, and ratio-heavy mocking; none found. Every `MutationProofTests` case asserts both a positive marker (`MUTANT_IMPORTED_OK`) and a behavioral outcome (non-zero exit), never exit-code-only.

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | `apply-progress` (Engram #1611) names RED/GREEN per phase and the two real mutation-harness bugs found and fixed during Unit 3. |
| All tasks have tests | ✅ | 28/28 tasks map to a named test class/method in `tests/test_paper_writing.py`. |
| RED confirmed (tests exist) | ✅ | All 12 test classes exist and were executed directly (50/50 green). |
| GREEN confirmed (tests pass) | ✅ | 50/50 in the focused run; 0 failures anywhere in `test_paper_writing.py`/`test_paper_decisions.py` across both full-suite runs. |
| Triangulation adequate | ✅ | Multiple cases per requirement (e.g. 3 mutation cases, 2 hand-edit cases, 2 pre-image depth cases). |
| Safety Net for modified files | ➖ N/A | All four files this change touches (`paper_cli.py`, `paper_block.py`, `paper_scaffold.py`, `tests/test_paper_writing.py`) were newly created by this change, not modified pre-existing files. |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 39 | 1 (`test_paper_writing.py`) | stdlib `unittest` |
| Integration (real subprocess against `paper_cli.py` / mutation harness) | 11 | 1 (`test_paper_writing.py`) | stdlib `subprocess` |
| E2E | 0 | — | not applicable to this CLI |
| **Total** | **50** | **1** | |

### Changed File Coverage
Coverage analysis skipped — no coverage tool detected for this Python suite.

### Quality Metrics
**Linter**: ➖ Not available (no linter configured for this Python suite)
**Type Checker**: ➖ Not available

### Verdict
PASS WITH WARNINGS
All 28 tasks complete, all 27/28 spec scenarios directly test-covered (1 PARTIAL, static-evidence-only, appropriately so), zero functional defects found across three targeted execution experiments (identity-guard independence, mutation-harness firing, CRLF text-mode flip) plus two full-repo test runs (one clean, one with a since-confirmed-transient unrelated flake); two WARNINGs recorded — a stale spec.md refusal-roster table design.md itself flagged as owed, and the transient concurrency-caused failure noted above.
