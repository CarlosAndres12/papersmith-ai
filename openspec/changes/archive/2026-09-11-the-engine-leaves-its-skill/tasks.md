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

- [x] 0.1 Verify `the-seal-before-the-cut` precondition: goldens committed and non-empty, comparison suite green, mutation proof re-run (one byte flips red). Refuse to start otherwise.
- [x] 0.2 **Reconcile spec/design conflict on the engine's destination.** `specs/implementation-engine-neutrality/spec.md` names the flat `_core/implementation/implementation_engine.py`. `design.md` M1 — independently re-verified here against `tests/test_implementation_core.py::CoreNamesNoDomainTests` (`CORE.glob("*.py")` is non-recursive; the engine defines `PRODUCT_DIRS`) and against `.claude/skills/_core/deliberation/engine/` (confirmed on disk) — requires the `engine/` subdirectory. The flat path breaks the guard with no acceptable repair. Update `spec.md`'s path text to the subdirectory form; if disputed, escalate to `sdd-spec` rather than resolve unilaterally in apply. Already resolved before apply (spec.md carries a reconciliation note); ticked per orchestrator instruction.
- [x] 0.3 Reconcile the smaller mismatch: design D6 asked for a scenario where an engine-resolved invocation is "refused"; the landed `implementation-cli-seal` delta instead wrote "the case's digest would move." Confirm the landed framing is correct (the engine is a valid file, never refused) and record this, rather than treating the two as identical.
- [x] 0.4 Baseline: run the seal comparison suite, `PublishedCommandsRunVerbatimTests`, full `.venv/bin/python -m unittest discover -s tests`, and `npm test`; paste all. Record `sha256(tests/seal/digests.json)`, `wc -l` of `implementation_cli.py`, and anchor counts of the three `Path(__file__).resolve()` sites (`SKILL_ROOT`, `CLI_PATH`, the `sys.path.insert` line).

## Phase 1: RED — Profile Resolver Tests First

- [x] 1.1 Write `tests/test_implementation_profile.py`: the six refusal codes, `setdefault` override semantics (subprocess + tmpdir fixture profile), `test_the_launcher_exposes_no_engine_attribute`. Run; confirm it fails on import (modules don't exist) — RED only, no production code this task.

## Phase 2: Foundation — Resolver and Per-Skill Profile

- [x] 2.1 Create `.claude/skills/_core/implementation/impl_domain_profile.py`: fails closed at import, raises `ImplementationProfileError(RuntimeError)` — never `Refused`/`NameRefused`, or `reachable_refusal_codes()`'s pinned `112` moves. Six named codes, `kit.root` nested-key validation.
- [x] 2.2 Create `.claude/skills/proposal-implementation/impl_profile.py`: `PROFILE = {"kit": {"root": ...}, "cli": {"path": ...}}` only — no other Cut-1 field.
- [x] 2.3 Re-run Phase 1's tests; confirm green and additive-only (nothing else imports these modules yet). Note: 9/11 green at this stage; `test_the_launcher_exposes_no_engine_attribute` and the setdefault-override test are inherently post-move assertions (they probe the LAUNCHER's own shape) and stayed red until Phase 3 landed — documented, not papered over.

## Phase 3: The Move — Atomic Work Unit

- [x] 3.1 One commit, never split: `git mv` the engine to the reconciled destination (task 0.2); reshape exactly 5 lines (delete the old `SKILL_ROOT` assignment, reshape `sys.path.insert` to the engine's own `parents[1]`, add the `PROFILE` import, reassign `SKILL_ROOT`/`CLI_PATH` from `PROFILE` immediately above `CLI_INVOCATION`); write the ~22-line launcher at the unchanged path (design D1). Assert the three `Path(__file__).resolve()` anchor counts before and after; paste both.
- [x] 3.2 Paste `git diff -M --numstat`; confirm rename similarity (~99.97%).

## Phase 4: Re-Point By Meaning

- [x] 4.1 Classify every `CLI`/`CLI_SCRIPT`/`_CLI_SCRIPTS` reader in `tests/` into meaning 1 (published entry point → launcher), 2 (engine source → engine), or 3 (skill root → unchanged), per design M2's table. Derive the list fresh at apply time, never from this document's line numbers. Also found and fixed two non-test production/test consumers design's brief did not enumerate: `scripts/materialize.py`'s own `from implementation_cli import ...` (re-pointed to the engine, mirroring the launcher's own profile mechanism) and a test-local `KIT` constant deriving from `impl.__file__` (re-pointed to the module-level `SKILL_ROOT` constant).
- [x] 4.2 Re-point `reachable_refusal_codes()`'s source list to include the engine's new location; confirm the `112` pin still holds.
- [x] 4.3 Re-point `CoreNamesNoDomainTests._cli_module()` to load the engine from its subdirectory.
- [x] 4.4 Re-point every in-process `import … as impl` route in `tests/` to the engine module (meaning 2).

## Phase 5: Published-Commands and Seal Pins

- [x] 5.1 `test_the_prefix_names_a_real_interpreter_and_this_exact_script`: assert launcher equality **and** `assertNotEqual(Path(tokens[1]), ENGINE)`.
- [x] 5.2 `test_the_script_is_not_executable_so_the_interpreter_is_load_bearing`: assert the **new** launcher file's mode is 644, not assumed from the moved engine.
- [x] 5.3 **Re-point `test_no_publication_point_still_builds_a_bare_script_name` to read the ENGINE's source** (design D5) — left on the launcher it passes vacuously over a 25-line file.
- [x] 5.4 Write `test_the_seal_invokes_the_published_launcher` in `tests/test_implementation_seal.py` (design D6): invoked path equals the launcher, not the engine.
- [x] 5.5 Update `tests/seal/harness.py`'s import route only; confirm argv stays `shlex.split(impl.CLI_INVOCATION)`, unedited.

## Phase 6: Proof

- [x] 6.1 **Measure before asserting (R1)**: run R1's mutation (`SKILL_ROOT` derived from the engine's own `__file__`, not `PROFILE`); record which seal cases' digests move. If none move, write that down rather than strengthening the test to compensate. **Measured**: exactly ONE case moved — `materialize` (exit 1, empty stdout). Every `kitSource`-reading case (`verify-a`, `verify-b`, ...) was UNAFFECTED — design.md's own prediction that the `kitSource` carriers would also move does not hold for this corpus (those fixtures already report `kitSource: null` under the correct root too, since their target files don't byte-match the kit templates). Recorded as a finding, not silently repeated.
- [x] 6.2 Write R1's guards: resolver refusal on absent/relative/nonexistent `kit.root` (`tests/test_implementation_profile.py::ProfileResolverRefusalTests`); `assertEqual(impl.SKILL_ROOT, FORGE/".claude/skills/proposal-implementation")` literal plus `assertNotEqual(impl.SKILL_ROOT, ENGINE.parent)` (`SkillRootValueTests`); seal reachability per 6.1's measured set (`SkillRootValueTests::test_a_wrong_skill_root_silently_breaks_every_kit_source_lookup`, in-process monkeypatch guard — safe permanent regression, unlike the one-time real-file R1 mutation above).
- [x] 6.3 **R2/D4, the highest-value mutation**: a real, reverted file edit to `impl_profile.py`'s `cli.path` → engine (never a monkeypatch — every seal case is a subprocess, blind to it). Assert anchor count moved 1→0/0→1 by reading the file first. Require BOTH a moved digest (record which case ids) AND a red `test_the_sealed_cli_path_names_the_launcher` AND a red `test_the_prefix_names_a_real_interpreter_and_this_exact_script`. Revert; reassert anchors at 1/0; re-run byte-identical. **Measured**: 27/28 sealed cases moved (all except `env`, whose output never embeds `CLI_INVOCATION`); both required pins went red; `test_the_seal_invokes_the_published_launcher` (task 5.4) also went red. Reverted byte-identical, re-confirmed green. **Finding**: design.md D4's literal code snippet (`_SKILL.parents[1] / "_core" / ...`) has an off-by-one path-depth bug — corrected to `_SKILL.parent / "_core" / ...` during the mutation (measured, not assumed); does not change the change's shape.
- [x] 6.4 **R3**: restore the old `parents[2] / "_core" / "implementation"` sys.path form; confirm `ImportError` at import; revert. **Measured**: `ModuleNotFoundError` (an `ImportError` subclass) on `impl_domain_profile`, exactly as predicted. Reverted byte-identical.
- [x] 6.5 **D5 meaning-2 mutation**: plant an `"implementation_cli.py` literal in the engine; show the launcher-pointed variant of the meaning-2 test passes over it (proves the vacuity D5 names); revert both. **Measured**: engine-pointed variant went red (caught); launcher-pointed variant stayed green despite the leak (vacuity proven). Both edits reverted byte-identical.
- [x] 6.6 Re-run the seal comparison suite: 28 digests byte-identical, exits and byte counts unchanged, `sha256(digests.json)` identical to the Phase 0 baseline. Confirm `git diff --exit-code` on `tests/seal/{cases,digests,unsealed}.json`, `corpus.py`, `normalize.py` exits 0. **Confirmed**: sha256 `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`, identical to Phase 0.4 baseline. `git diff --exit-code` exits 0 on all five seal instrument files.
- [x] 6.7 Confirm `test_the_sealed_cli_path_names_the_launcher`'s `carriers` list is non-empty (a vacuous pass over zero carriers is the one way it can lie). Confirmed non-empty and green.

## Phase 7: Non-Interference and Closing Measurements

- [x] 7.1 Re-measure `SKILL_ROOT`'s reader count fresh against the moved engine (design.md reports 19; the brief carried 17); paste the count and report any discrepancy from either number. **Re-measured against the moved engine, post-move: 19 reader lines** (excluding the definition itself), confirming design.md's count and correcting the brief's 17.
- [x] 7.2 Confirm `test_the_core_resolves_the_repository_root_it_actually_lives_in` stays green (`FORGE_ROOT` is `parents[4]` of `impl_layout.py`, unmoved). Confirmed green (`tests.test_implementation_core`, 122/122).
- [x] 7.3 Confirm `LaunchAvailableNoUpwardImportsTests` (scoped to one file, not a directory) is unaffected by the move. Confirmed green, same run.
- [x] 7.4 Verify `SKILL.md`, `references/usage.md`, `README.md`, `remote_cli.py` name only the unchanged launcher path, never the engine's new location, as a source. Confirmed via `rg '_core/implementation/engine|implementation_engine'` over all four — zero matches.
- [x] 7.5 **Was BLOCKED, now resolved by operator ruling (2026-09-11) — see Phase 8.** The `test_agents.py` non-interference finding, unresolved by any of the three closures apply itself could pick, is fixed by moving `objective` into the Cut-1 field set. Re-run after Phase 8: `npm test` 595/595, full Python discover green with zero new failures — see 8.6.
- [x] 7.6 If 6.1's measured result changes any stated expectation, update the Open Questions closure in `design.md`. Updated — the `kitSource`-carrier prediction did not hold; recorded in design.md's Open Questions with the measured result and reasoning.

## Phase 8: Operator Ruling — `objective` Crosses the Seam (2026-09-11)

Closes task 7.5's shape-level finding. `tests/test_agents.py`'s cross-skill north lock
discovers a skill's declared `OBJECTIVE_FLOW` by walking THAT SKILL'S OWN directory tree,
never by importing — Phase 3's move took `OBJECTIVE_FLOW` outside `proposal-implementation/`'s
tree entirely, and none of apply's three self-generated closures (extend an out-of-scope test
file, declare the skill northless, re-expose an engine attribute through the launcher) was
apply's to pick. The operator ruled a fourth: `objective` joins `kit.root`/`cli.path` as the
Cut-1 field set's third member, moved verbatim, mirroring the landed
`2026-09-09-a-north-a-second-domain-can-hold` precedent on the deliberation side.

- [x] 8.1 Move `OBJECTIVE_FLOW`'s 56-line literal (engine lines located by name, never by the
      operator's cited numbers) verbatim into `.claude/skills/proposal-implementation/impl_profile.py`
      as a module-level `OBJECTIVE_FLOW = {...}` (never a derived expression — `tests/
      test_agents.py`'s `ast.literal_eval` walk requires exactly this shape), and add
      `"objective": OBJECTIVE_FLOW` to `PROFILE`. Diffed byte-for-byte against the original
      block before touching the engine: identical, 56/56 lines.
- [x] 8.2 Engine: replace the `OBJECTIVE_FLOW = {...}` literal with `OBJECTIVE_FLOW =
      PROFILE["objective"]` at its own definition site; leave both usage sites
      (`"objective": OBJECTIVE_FLOW`, ×2) untouched by name. Confirmed both still resolve;
      confirmed `test_proposal_implementation.py::ObjectiveFlowTests` (five tests, unedited)
      stays green including its own `'"objective": OBJECTIVE_FLOW'` source-literal check.
- [x] 8.3 `impl_domain_profile.py`: `objective` becomes required, validated exactly as
      `domain-profile.ts`'s `OBJECTIVE_REQUIRED`/`stagesIncomplete` pair — `purpose`, `stages`,
      `arrival`, `humanStops` present, `stages` non-empty with every element carrying `stage`/
      `establishes`/`behindWhen`. Reuses the existing `INCOMPLETE` code (no new refusal code).
      RED-first: `tests/test_implementation_profile.py::ObjectiveProfileFieldTests` (6 new
      tests) written and confirmed failing before the resolver change, green after. Updated
      every pre-existing fixture profile in the same file that would otherwise trip the new
      required field before reaching the refusal code it actually tests (`ProfileResolverRefusalTests`'s
      kit/cli fixtures, `SetdefaultOverrideTests`'s override fixture).
- [x] 8.4 **The mutation `objective` now deserves, one-time and reverted** (never a permanent
      file-mutating test, mirroring the landed F5/R2 precedent): change one character of
      `impl_profile.py`'s `objective.purpose` text (`"carry"` → `"Carry"`), anchor-counted
      before and after. **Measured**: 11 of 28 sealed cases moved (`admit-e0`, `close-e0`,
      `close-e1`, `gate-e0`, `gate-e1`, `handoff-e0`, `offer-e0`, `position-e0`, `probe`,
      `settle`, `step`) — every case that reaches a refusal payload or the other `"objective":
      OBJECTIVE_FLOW` site. Reverted; anchor re-confirmed; seal re-run byte-identical,
      `sha256(digests.json)` unchanged from the Phase 0 baseline.
- [x] 8.5 Re-run `tests/test_agents.py` in full: **16/16 green, zero edits to that file**
      (`git diff --stat tests/test_agents.py` empty throughout) — the three previously-failing
      `AgentBindingTests` pass because `_python_objective("proposal-implementation")` now finds
      the relocated `OBJECTIVE_FLOW` inside the skill's own tree again.
- [x] 8.6 Full re-verification: `tests/test_implementation_profile.py` (20/20, includes the six
      new `ObjectiveProfileFieldTests`), seal comparison suite (28/28 byte-identical, `sha256`
      unchanged from the Phase 0 baseline), `npm test` (**595/595**), full Python discover
      (**Ran 2849 tests in 443.920s — OK (skipped=6)**, zero failures, zero new skips). One
      further finding closed mid-verification: the amended `impl_domain_profile.py` docstring
      re-introduced the literal word "tests" (a `SOURCE_ROOTS` member), tripping
      `CoreNamesNoDomainTests` — reworded, confirmed clean, confirmed green before the final
      discover run above.
- [x] 8.7 Record the scope correction honestly in `design.md` (D2's "five lines"/17,095-verbatim
      claim amended; D3's field-set and rejected-field tables amended; File Changes table
      amended) and in this file, per the operator's explicit instruction not to leave Cut 1
      described as something it no longer is.
