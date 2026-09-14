```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:6a6afacc19d4eb797b82ec21adc6db07dd07404d000000000000000000000000
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 7/7
scenarios: 15/15
test_command: npm test && .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256:8d245224f14284fb70ac2aea4c61c71f795620267f0432e29d4a265ab74c05b4
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: the-engine-leaves-its-skill (Cut 1)
**Version**: N/A (new capability `implementation-engine-neutrality`; modified delta on `implementation-cli-seal`)
**Mode**: Strict TDD

All measurements below were re-executed independently at HEAD `6a6afac`, worktree
clean throughout, never inherited from apply's report. Where a number is repeated
from apply, it is because re-execution reproduced it exactly — stated as measured,
not assumed.

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 39 |
| Tasks complete | 39 |
| Tasks incomplete | 0 |

`tasks.md` re-counted directly: `rg -c '^- \[x\]'` → 39, `rg -c '^- \[ \]'` → 0
(Phases 0–7, 32 tasks, plus Phase 8's operator-ruling closure, 7 tasks = 39).

### Build & Tests Execution

**Build**: PASSED — `npm run typecheck` → `tsc -p tsconfig.json`, exit 0.

**Tests**: 595 + 2849 passed / 0 failed / 0 + 6 skipped.
```
npm test:
  tests 595 / suites 0 / pass 595 / fail 0 / skipped 0
  duration_ms 35817.589333

.venv/bin/python -m unittest discover -s tests:
  Ran 2849 tests in 441.237s
  OK (skipped=6)
```
Both baselines held with **zero new failures and zero new skips**, re-run from a
clean worktree, output redirected to files (`rg 'Ran [0-9]+ test'` used to avoid the
fixture-JSON-on-both-streams trap).

**Coverage**: Not available — no coverage tool detected. Reported per protocol, not
a failure.

### Live-Executed Proof (not static replay)

Every item below was **executed by this verify pass**, not read off apply's report.
Full logs preserved in the session scratchpad.

| # | Check | Command | Result | Matches apply's report? |
|---|---|---|---|---|
| 1 | Seal reproduces from scratch, through the new launcher | `unittest tests.test_implementation_seal.{SealComparisonTests,SealEntryPointTests,SealMutationProofTests}` | 3/3 green; `sha256(digests.json)` = `011300df…` — unchanged | Yes, exact |
| 2 | R1 — `SKILL_ROOT` silent failure, real reverted edit | mutate `SKILL_ROOT = Path(__file__).resolve().parent`, re-run `SealComparisonTests` | **exactly 1 case moved: `materialize`**; reverted, byte-identical | Yes, exact |
| 3 | R2/D4 — `CLI_PATH` silent failure, real reverted edit, the highest-value mutation | mutate `impl_profile.py`'s `cli.path` → engine; re-run `SealComparisonTests` + `SealEntryPointTests` + `test_the_prefix_names_a_real_interpreter_and_this_exact_script` | **27/28 sealed cases moved** (every case but `env`) **AND** both required pins went red (`test_the_seal_invokes_the_published_launcher`, `test_the_prefix_names_…`); reverted, byte-identical, all green again | Yes, exact — apply's exact 27/28 + "all except env" reproduced |
| 4 | R3 — `sys.path` loud failure, real reverted edit | restore `parents[2] / "_core" / "implementation"`; run the launcher directly | `ModuleNotFoundError: No module named 'impl_domain_profile'` (an `ImportError` subclass) at import, before any command runs; reverted, exit 0 again | Yes, exact |
| 5 | `objective` mutation | flip one char of `objective.purpose` (`"carry"→"Carry"`); re-run `SealComparisonTests` | **exactly 11/28 cases moved**: `admit-e0, close-e0, close-e1, gate-e0, gate-e1, handoff-e0, offer-e0, position-e0, probe, settle, step` — identical list, identical count; reverted, byte-identical | Yes, exact, case-for-case |
| 6 | Resolver refuses an incomplete `objective` (not vacuously) | `unittest tests.test_implementation_profile` (full module) | 20/20 green — includes `ObjectiveProfileFieldTests` asserting refusal on missing `objective`, missing leaf (`objective.humanStops`), and `stages: []` (the vacuous-presence trap) each named by its own leaf | Count differs — see WARNING-3 |
| 7 | `tests/test_agents.py` green with zero edits | `unittest tests.test_agents` + `git diff --stat 647de2a HEAD -- tests/test_agents.py` | 16/16 green; diff empty | Yes, exact |
| 8 | Non-interference, four proofs | `git diff --name-only c08f436 6a6afac` (the Cut 1 commit's own parent) + path-scoped diffs | Scope = exactly the 12 files in the commit; `.claude/skills/_core/deliberation/**` diff empty; `.claude/skills/proposal-deliberation/**` diff empty; both suites at/above baseline, zero new skips | Yes |
| 9 | 17,045-line verbatim claim | `diff` of the pre-move file (`c08f436`) against the landed engine, hunk-counted by hand | Exactly **61** original lines touched (2 removed `SKILL_ROOT` lines, 1 replaced `sys.path` line, 2 replaced `CLI_PATH` lines, 56 removed `OBJECTIVE_FLOW` lines) → `17106 − 61 = 17045` verbatim, `+20` new lines → `17065` final line count (matches `wc -l`) | Yes, exact, independently re-derived — not merely repeated |
| 10 | `sha256(tests/seal/digests.json)` and its last-touching commit | `sha256sum` + `git log -1 -- tests/seal/digests.json` | `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`; last commit `14d97e9` (the seal's own capture) | Yes, exact |
| 11 | Launcher line count | `wc -l` | 24 | Yes, exact |
| 12 | `SKILL_ROOT` reader-line count | `rg -n SKILL_ROOT` over the engine, excluding the assignment and one comment-only mention | 19 reader lines | Yes, exact |
| 13 | `CLI_INVOCATION` reader count | `rg -n CLI_INVOCATION` over the engine, excluding the definition | 4 (`_cli_command` builder + gate/step/discuss guidance strings) | Yes, exact |
| 14 | `reachable_refusal_codes()` pin | source read | `assertEqual(len(reachable_refusal_codes()), 112)`; source list explicitly `(ENGINE, *CORE_IMPLEMENTATION.glob("*.py"))` — the re-point is real, not incidental | Yes |
| 15 | `CoreNamesNoDomainTests` guard, reproduced by hand | manual scan of every `_core/implementation/*.py` (non-recursive, matching the glob) for `PRODUCT_DIRS`/`SOURCE_ROOTS` members | zero leaks; `impl_domain_profile.py`'s docstring no longer contains the literal `tests` (confirms the collateral-regression fix) | Yes |
| 16 | `materialize.py` consumer, `KIT` test constant | source read | `materialize.py` imports the engine via its own profile mechanism (mirrors the launcher); `KIT` in `test_proposal_implementation.py` now derives from module-level `SKILL_ROOT`, not `impl.__file__` | Yes |

Toy-target hygiene: `implementations/` empty before, during (each mutation cleaned
its own scratch dir), and after this verify pass. `git status --short` empty at the
end.

### Spec Compliance Matrix

**Requirement counts, re-counted directly**: `implementation-engine-neutrality/spec.md`
— 6 requirements, 12 scenarios (`rg -c '^### Requirement:'` / `'^#### Scenario:'`).
`implementation-cli-seal/spec.md` (delta) — 1 requirement, 3 scenarios. **Total: 7
requirements, 15 scenarios** — not inherited from any upstream artifact's count.

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Engine Refuses To Start Without A Domain Profile | Unset variable refuses | `ProfileResolverRefusalTests::test_unset_refuses_required` | ✅ COMPLIANT |
| Engine Refuses To Start Without A Domain Profile | Malformed profile refuses | `ProfileResolverRefusalTests` (relative/unreadable/invalid/incomplete/unsafe, 10 more cases) | ✅ COMPLIANT |
| The Skill Root Resolves From The Host | SKILL_ROOT names the skill directory | `SkillRootValueTests::test_skill_root_names_the_skill_not_the_engines_own_parent` | ✅ COMPLIANT |
| The Skill Root Resolves From The Host | A wrong root is made observable | live R1 mutation (exactly 1 case moved) + `SkillRootValueTests::test_a_wrong_skill_root_silently_breaks_every_kit_source_lookup` | ✅ COMPLIANT |
| The Core Import Path Resolves From The Engine's Own File | Import succeeds through any launcher | full suite green, launcher runs cleanly post-revert | ✅ COMPLIANT |
| The Core Import Path Resolves From The Engine's Own File | A stale relative depth fails loudly | live R3 mutation → `ModuleNotFoundError` | ✅ COMPLIANT |
| The Published CLI Path Names The Launcher | CLI_PATH names the launcher | `PublishedCommandsRunVerbatimTests::test_the_prefix_names_a_real_interpreter_and_this_exact_script` | ✅ COMPLIANT |
| The Published CLI Path Names The Launcher | A wrong CLI_PATH moves the seal | live R2/D4 mutation → 27/28 moved | ✅ COMPLIANT |
| Published Commands Are Proven Against The Launcher | The test asserts the launcher's literal path | `PublishedCommandsRunVerbatimTests` (5/5 green) | ✅ COMPLIANT |
| Published Commands Are Proven Against The Launcher | The guard is reachable | live R2/D4 mutation → test goes red | ✅ COMPLIANT |
| Zero Behavioural Delta | Every case reproduces its golden | `SealComparisonTests::test_every_sealed_case_matches_its_golden`, live | ✅ COMPLIANT |
| Zero Behavioural Delta | A moved digest blocks the change | live R2/D4 + R1 + objective mutations, each reverted | ✅ COMPLIANT |
| Seal Capture Scope | Every subcommand is captured | `SealMembershipTests`/`CoverageTests` (existing, unaffected) | ✅ COMPLIANT |
| Seal Capture Scope | A new subcommand is detected | unchanged mechanism, not touched by this cut | ✅ COMPLIANT |
| Seal Capture Scope | The sealed entry point is the launcher, not the engine | `SealEntryPointTests::test_the_seal_invokes_the_published_launcher`, live, plus live R2/D4 reddening it | ✅ COMPLIANT |

**Compliance summary**: 15/15 scenarios compliant, all backed by a passing runtime
test I executed myself, and 5 of the 6 mutation-bearing scenarios reproduced live
with numbers matching apply's report exactly.

### Correctness (Static Evidence)

| Area | Status | Notes |
|---|---|---|
| Six named refusal codes, exactly | ✅ | `grep -oE 'IMPLEMENTATION_DOMAIN_PROFILE_[A-Z_]+'` → exactly the six named in spec/design, no more, no fewer |
| `objective` validated by leaf, not top-level presence | ✅ | `ObjectiveProfileFieldTests` refuses `stages: []` and a missing `humanStops` leaf specifically, live-executed |
| Resolver raises `ImplementationProfileError(RuntimeError)`, never `Refused` | ✅ | confirmed by source read; `112` pin held live |
| `git mv` rename evidence (design's own predicted mechanism) | ⚠️ WARNING-3 | does not reproduce — see below |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1 — launcher is a launcher, not an alias | ✅ Yes | `test_the_launcher_exposes_no_engine_attribute` green, live |
| D2 — three reaches, three failure modes | ✅ Yes | all three re-executed live with matching results |
| D3 — Cut-1 field set (`kit.root`, `cli.path`, `objective`) | ✅ Yes, in code | not reflected in `spec.md` — see WARNING-2 |
| D4 — seal proof procedure (P0–P5) | ✅ Yes | reproduced live for R2/D4, R1, and objective |
| D5 — `PublishedCommandsRunVerbatimTests` re-pointed by meaning | ✅ Yes | `test_no_publication_point_still_builds_a_bare_script_name` reads `ENGINE.read_text()`, confirmed by source |
| D6 — `Seal Capture Scope` amendment | ✅ Yes, in the delta spec | delta spec's own scenario text still names the flat path — see WARNING-1 |
| D7 — ordering/rollback | ✅ Yes | one commit (`6a6afac`), atomic, no intermediate commits found in range |
| M1 — engine lands in `engine/` subdirectory | ✅ Yes | confirmed on disk, confirmed by the non-recursive-glob reproduction (zero leaks) |
| M2 — three meanings of "CLI path" | ✅ Yes | `CLI`/`ENGINE`/`SKILL_ROOT` constants correctly split across `test_implementation_core.py`, `test_implementation_seal.py`, `test_proposal_implementation.py` |

### Issues Found

**CRITICAL**: None.

**WARNING**:

1. **`implementation-cli-seal/spec.md`'s own delta was not reconciled to the `engine/`
   subdirectory destination.** Its "Scenario: The sealed entry point is the launcher,
   not the engine" still reads: *"GIVEN the engine now lives at
   `_core/implementation/implementation_engine.py`, separate from the per-skill
   launcher"* — the FLAT path that `M1`/task 0.2 ruled unreachable and that
   `implementation-engine-neutrality/spec.md` explicitly corrected via its own
   "Reconciliation note." Task 0.2 says *"Update `spec.md`'s path text to the
   subdirectory form"* (singular), and only one of the two spec files in this
   change actually carries that correction. The implementation and every test are
   correctly pointed at `engine/implementation_engine.py` (verified live above) — this
   is a spec-text accuracy defect, not a behavioral one. **Resolution**: amend the
   scenario text in `specs/implementation-cli-seal/spec.md` to name
   `_core/implementation/engine/implementation_engine.py` before archive.

2. **The governing spec was never amended for the Phase 8 operator ruling that added
   `objective` to the Cut-1 field set.** `design.md` and `tasks.md` were both
   explicitly amended (2026-09-11, recorded in task 8.7) to describe `objective` as
   the field set's third member, its refusal validation, and its mutation proof. This
   session's config states the OpenSpec file is the source of truth (hybrid mode).
   `specs/implementation-engine-neutrality/spec.md`'s Purpose paragraph still says the
   engine "sources `kit.root` and its published CLI path from the host" — no mention
   of `objective` anywhere in the spec text, even though the shipped resolver now
   requires it, refuses six ways without it, and 11/28 sealed cases are provably
   sensitive to its content (all independently reproduced above). **Resolution**:
   amend `spec.md`'s Purpose and add an `objective`-scoped requirement (or fold it
   into the existing "Engine Refuses To Start..." requirement's scenario text) before
   archive, so the spec describes what was actually built and proven.

3. **The design's own predicted rename-detection evidence does not reproduce.**
   `design.md` D7 states *"`git mv` and the five-line reshape land in one commit so
   rename detection sees ~99.97% similarity"*, and task 3.2 claims this was confirmed.
   Re-running `git diff -M c08f436 6a6afac --numstat` (and `--summary`, at every
   threshold down to `-M5%`) on the landed commit shows **no rename pairing at all**:
   the new engine path is a pure create (17065 insertions / 0 deletions) and the
   launcher's own path is a same-path modification (17 insertions / 17099 deletions)
   — because the launcher was written back to the *same* path within the same commit,
   leaving no deletion for git to pair against the engine's creation. This is expected
   git mechanics once understood, but it means the specific process-evidence the
   design predicted and task 3.2 claims to have confirmed is not what the landed
   commit actually shows. It does **not** undermine the zero-behavioural-delta proof,
   which rests entirely on the independently-reproduced seal (verified live above),
   never on rename detection. **Resolution**: correct design.md's D7 claim, or drop
   it as unverifiable evidence for a same-path replacement.

**SUGGESTION**:

1. **Minor test-count drift in three artifacts.** `design.md`, `tasks.md` (task 8.3),
   and `apply-progress` all state "**six** new `ObjectiveProfileFieldTests`." Live
   execution and direct method-count both show **five**:
   `test_a_missing_objective_refuses_incomplete_and_names_it`,
   `test_a_missing_objective_leaf_refuses_incomplete_and_names_it`,
   `test_empty_stages_refuses_incomplete`,
   `test_a_stage_missing_a_required_key_refuses_incomplete`,
   `test_a_complete_objective_resolves_cleanly`. The module's overall total (20/20)
   is correct; only the per-class sub-count is off by one. No functional impact —
   flagged per the "cited symbols are claims, not facts" discipline this project
   holds itself to.

### Verdict

**PASS WITH WARNINGS**

Zero behavioural delta is proven, not merely replayed: all three behavioural
reaches (R1/R2-D4/R3), the objective-field mutation, and the highest-value mutation
were each re-executed live in this verify pass — with numbers matching apply's
report exactly, including the precise case lists for the 27/28 and 11/28 mutations.
`tests/test_agents.py` is green with zero edits, both suites hold their baselines
with zero new failures and zero new skips, and the 17,045-line-verbatim claim was
independently re-derived (not repeated) via a hand-counted hunk diff. The three
WARNINGs are documentation/spec-accuracy gaps — the sealed instrument, the resolver,
and every test pin are all functioning exactly as designed — and none blocks
archive on their own, but the spec/design text should be corrected first so the
artifact trail matches what was actually built and measured.
