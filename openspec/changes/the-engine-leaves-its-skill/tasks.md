# Tasks: The Engine Leaves Its Skill (Cut 1)

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | ~440 authored (resolver ~90, tests ~300, launcher ~22, profile ~25, engine reshape 5) + one `git mv` rename |
| 400-line budget risk | Low — graded against this session's 1400-line budget, not the 400-line default; ~440 sits well inside it |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Whole Cut 1 (Phases 0–7), single PR | PR 1 | `.venv/bin/python -m unittest tests.test_implementation_profile tests.test_proposal_implementation.PublishedCommandsRunVerbatimTests tests.test_implementation_core.CoreNamesNoDomainTests tests.test_implementation_seal -v` | Real subprocess seal comparison suite (`tests/seal/harness.py`, through the launcher) | `git mv` engine back, delete launcher/profile/resolver, revert test edits — no committed ledger touched |

## Phase 0: Preconditions and Artifact Reconciliation (blocking)

- [ ] 0.1 Verify `the-seal-before-the-cut` precondition: goldens committed and non-empty, comparison suite green, mutation proof re-run (one byte flips red). Refuse to start otherwise.
- [ ] 0.2 **Reconcile spec/design conflict on the engine's destination.** `specs/implementation-engine-neutrality/spec.md` names the flat `_core/implementation/implementation_engine.py`. `design.md` M1 — independently re-verified here against `tests/test_implementation_core.py::CoreNamesNoDomainTests` (`CORE.glob("*.py")` is non-recursive; the engine defines `PRODUCT_DIRS`) and against `.claude/skills/_core/deliberation/engine/` (confirmed on disk) — requires the `engine/` subdirectory. The flat path breaks the guard with no acceptable repair. Update `spec.md`'s path text to the subdirectory form; if disputed, escalate to `sdd-spec` rather than resolve unilaterally in apply.
- [ ] 0.3 Reconcile the smaller mismatch: design D6 asked for a scenario where an engine-resolved invocation is "refused"; the landed `implementation-cli-seal` delta instead wrote "the case's digest would move." Confirm the landed framing is correct (the engine is a valid file, never refused) and record this, rather than treating the two as identical.
- [ ] 0.4 Baseline: run the seal comparison suite, `PublishedCommandsRunVerbatimTests`, full `.venv/bin/python -m unittest discover -s tests`, and `npm test`; paste all. Record `sha256(tests/seal/digests.json)`, `wc -l` of `implementation_cli.py`, and anchor counts of the three `Path(__file__).resolve()` sites (`SKILL_ROOT`, `CLI_PATH`, the `sys.path.insert` line).

## Phase 1: RED — Profile Resolver Tests First

- [ ] 1.1 Write `tests/test_implementation_profile.py`: the six refusal codes, `setdefault` override semantics (subprocess + tmpdir fixture profile), `test_the_launcher_exposes_no_engine_attribute`. Run; confirm it fails on import (modules don't exist) — RED only, no production code this task.

## Phase 2: Foundation — Resolver and Per-Skill Profile

- [ ] 2.1 Create `.claude/skills/_core/implementation/impl_domain_profile.py`: fails closed at import, raises `ImplementationProfileError(RuntimeError)` — never `Refused`/`NameRefused`, or `reachable_refusal_codes()`'s pinned `112` moves. Six named codes, `kit.root` nested-key validation.
- [ ] 2.2 Create `.claude/skills/proposal-implementation/impl_profile.py`: `PROFILE = {"kit": {"root": ...}, "cli": {"path": ...}}` only — no other Cut-1 field.
- [ ] 2.3 Re-run Phase 1's tests; confirm green and additive-only (nothing else imports these modules yet).

## Phase 3: The Move — Atomic Work Unit

- [ ] 3.1 One commit, never split: `git mv` the engine to the reconciled destination (task 0.2); reshape exactly 5 lines (delete the old `SKILL_ROOT` assignment, reshape `sys.path.insert` to the engine's own `parents[1]`, add the `PROFILE` import, reassign `SKILL_ROOT`/`CLI_PATH` from `PROFILE` immediately above `CLI_INVOCATION`); write the ~22-line launcher at the unchanged path (design D1). Assert the three `Path(__file__).resolve()` anchor counts before and after; paste both.
- [ ] 3.2 Paste `git diff -M --numstat`; confirm rename similarity (~99.97%).

## Phase 4: Re-Point By Meaning

- [ ] 4.1 Classify every `CLI`/`CLI_SCRIPT`/`_CLI_SCRIPTS` reader in `tests/` into meaning 1 (published entry point → launcher), 2 (engine source → engine), or 3 (skill root → unchanged), per design M2's table. Derive the list fresh at apply time, never from this document's line numbers.
- [ ] 4.2 Re-point `reachable_refusal_codes()`'s source list to include the engine's new location; confirm the `112` pin still holds.
- [ ] 4.3 Re-point `CoreNamesNoDomainTests._cli_module()` to load the engine from its subdirectory.
- [ ] 4.4 Re-point every in-process `import … as impl` route in `tests/` to the engine module (meaning 2).

## Phase 5: Published-Commands and Seal Pins

- [ ] 5.1 `test_the_prefix_names_a_real_interpreter_and_this_exact_script`: assert launcher equality **and** `assertNotEqual(Path(tokens[1]), ENGINE)`.
- [ ] 5.2 `test_the_script_is_not_executable_so_the_interpreter_is_load_bearing`: assert the **new** launcher file's mode is 644, not assumed from the moved engine.
- [ ] 5.3 **Re-point `test_no_publication_point_still_builds_a_bare_script_name` to read the ENGINE's source** (design D5) — left on the launcher it passes vacuously over a 25-line file.
- [ ] 5.4 Write `test_the_seal_invokes_the_published_launcher` in `tests/test_implementation_seal.py` (design D6): invoked path equals the launcher, not the engine.
- [ ] 5.5 Update `tests/seal/harness.py`'s import route only; confirm argv stays `shlex.split(impl.CLI_INVOCATION)`, unedited.

## Phase 6: Proof

- [ ] 6.1 **Measure before asserting (R1)**: run R1's mutation (`SKILL_ROOT` derived from the engine's own `__file__`, not `PROFILE`); record which seal cases' digests move. If none move, write that down rather than strengthening the test to compensate.
- [ ] 6.2 Write R1's guards: resolver refusal on absent/relative/nonexistent `kit.root`; `assertEqual(impl.SKILL_ROOT, FORGE/".claude/skills/proposal-implementation")` literal plus `assertNotEqual(impl.SKILL_ROOT, ENGINE.parent)`; seal reachability per 6.1's measured set.
- [ ] 6.3 **R2/D4, the highest-value mutation**: a real, reverted file edit to `impl_profile.py`'s `cli.path` → engine (never a monkeypatch — every seal case is a subprocess, blind to it). Assert anchor count moved 1→0/0→1 by reading the file first. Require BOTH a moved digest (record which case ids) AND a red `test_the_sealed_cli_path_names_the_launcher` AND a red `test_the_prefix_names_a_real_interpreter_and_this_exact_script`. Revert; reassert anchors at 1/0; re-run byte-identical.
- [ ] 6.4 **R3**: restore the old `parents[2] / "_core" / "implementation"` sys.path form; confirm `ImportError` at import; revert.
- [ ] 6.5 **D5 meaning-2 mutation**: plant an `"implementation_cli.py` literal in the engine; show the launcher-pointed variant of the meaning-2 test passes over it (proves the vacuity D5 names); revert both.
- [ ] 6.6 Re-run the seal comparison suite: 28 digests byte-identical, exits and byte counts unchanged, `sha256(digests.json)` identical to the Phase 0 baseline. Confirm `git diff --exit-code` on `tests/seal/{cases,digests,unsealed}.json`, `corpus.py`, `normalize.py` exits 0.
- [ ] 6.7 Confirm `test_the_sealed_cli_path_names_the_launcher`'s `carriers` list is non-empty (a vacuous pass over zero carriers is the one way it can lie).

## Phase 7: Non-Interference and Closing Measurements

- [ ] 7.1 Re-measure `SKILL_ROOT`'s reader count fresh against the moved engine (design.md reports 19; the brief carried 17); paste the count and report any discrepancy from either number.
- [ ] 7.2 Confirm `test_the_core_resolves_the_repository_root_it_actually_lives_in` stays green (`FORGE_ROOT` is `parents[4]` of `impl_layout.py`, unmoved).
- [ ] 7.3 Confirm `LaunchAvailableNoUpwardImportsTests` (scoped to one file, not a directory) is unaffected by the move.
- [ ] 7.4 Verify `SKILL.md`, `references/usage.md`, `README.md`, `remote_cli.py` name only the unchanged launcher path, never the engine's new location, as a source.
- [ ] 7.5 Run `npm test` and the full Python discover suite; paste both; confirm `proposal-deliberation` baselines hold (595/0, prior `Ran …, OK (skipped=6)`). Never run while another agent exercises the CLI.
- [ ] 7.6 If 6.1's measured result changes any stated expectation, update the Open Questions closure in `design.md`.
