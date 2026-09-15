```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:da30bb0fd4e839946d2172986ba7d50dd8ecc3eeab4ab1b28759bdf800ca2863
verdict: pass
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 15/15
test_command: npm test && .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256:84bd73803319bb37e9a98a8200da8e026a60090e45c7b1fd7885cd64548e46c4
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: the-seal-before-the-cut
**Version**: N/A (new capability — no prior spec version)
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 48 |
| Tasks complete | 48 |
| Tasks incomplete | 0 |

`tasks.md` re-counted directly: `48` lines match `- [x]`, `0` match `- [ ]`.

### Build & Tests Execution

**Build**: PASSED — `npm run typecheck` → `tsc -p tsconfig.json`, exit 0. (The prior verify-report for a sibling change in this same session recorded this command failing with `tsc: command not found`; re-run here resolves cleanly via `npx`'s local `node_modules/.bin` resolution — environment gap, not this change's concern either way.)

**Tests**: 595 + 2826 passed / 0 failed / 0 + 6 skipped (skips are the pre-existing Python baseline, unaffected).
```
npm test:
  tests 595 / pass 595 / fail 0 / skipped 0

.venv/bin/python -m unittest discover -s tests:
  Ran 2826 tests in 453.483s
  OK (skipped=6)
```
Combined command (`npm test && .venv/bin/python -m unittest discover -s tests`) executed as ONE evidence run for `test_output_hash`, exit 0. Re-run independently three separate times during this verification (isolated full discover: `2826/473.509s`; combined run: `2826/453.483s`; isolated seal module alone: `43/5.306s`) — all green, all `OK (skipped=6)`, zero variance in pass/fail/skip counts across runs.

**Coverage**: not measured — no coverage tool configured for this stack (informational only, per strict-TDD module: not blocking).

### Two Orderings — Proven From Git History, Not Prose

```
598735f docs: declare F3's five-site message delta before applying it   <- f3-message-delta.md ALONE
b0913a5 fix: F3 -- name the read directory, not a spelled one            <- F3 code
7f9ee48 docs: N3 CLI_PATH-blindness fix, blocked finding on Data/
e30906a docs: correct the Data/ coverage claim per coordinator decision
14d97e9 feat: the stdout characterization seal, captured                 <- digests.json lands here
5c72ba5 fix: F5 -- PRODUCT_DATA read from the tuple, not spelled twice   <- F5 code (AFTER capture)
5424819 docs: record F5's after-commit sha in f5-zero-delta.md
e0331f8 docs: Phase 9-10 non-interference proof and findings closeout   <- HEAD
```
- `598735f` (delta doc alone) precedes `b0913a5` (F3 code) precedes `14d97e9` (capture). Ordering holds.
- `5c72ba5` (F5 code) lands strictly after `14d97e9` (capture). Ordering holds.
- **F5's zero-delta was re-verified by a REAL LIVE re-capture, not the existing stored digests.json.** I ran `.venv/bin/python tests/seal_capture.py` myself (real double-run, two independently-built corpora, 29 cases × 2), and it wrote `digests.json`/`unsealed.json` byte-identical to the committed versions (`diff` clean, `git diff --stat` empty). This is a stronger proof than replaying the stored bytes: the current CLI, unmodified since `5c72ba5`, reproduces the exact committed goldens from scratch. The zero-delta claim is validated by comparison against an independently regenerated capture, not by construction.

### digests.json / apply's "28/29" — Discrepancy Resolved, Not a Defect

`digests.json` has 29 top-level keys; apply reported "28/29 cases sealed" with `propose` unsealed. Read `tests/seal_capture.py:151`: `digests[CORPUS_FINGERPRINT_KEY] = _corpus_fingerprint()` — the file deliberately holds 28 case digests **plus** a reserved `__corpus_fingerprint__` metadata key (the anti-trim guard, `sha256(corpus.py)`). `28 case digests + 1 fingerprint key = 29 total keys`, coinciding numerically with the 29-case corpus but not the same count. Verified: `digests.keys() - {__corpus_fingerprint__}` == `cases.keys() - {propose}` == 28 members, set-equal. The stored fingerprint (`67cb1a49e868a9b9a395132d53aa83a4fc70188af3b9d80f48e6a8ad013f7865`) matches `sha256(corpus.py)` computed independently. No disagreement between apply's self-report and the file — resolved by reading `seal_capture.py`'s own `capture()` (`print(f"Captured {len(digests) - 1} sealed case(s)...")` — the `-1` is the fingerprint key, explaining the exact wording apply used).

### The Seal Can Actually Fail — Executed, Not Narrated

All of the following were done as **real file edits** (not `SealMutationProofTests`'s in-memory copy), confirmed red, then byte-identically reverted (`diff` against a pre-mutation backup, `git diff --stat` empty after every revert):

1. **Golden byte flip**: flipped one hex digit of `step`'s stored sha256 in the real `tests/seal/digests.json` → `SealComparisonTests.test_every_sealed_case_matches_its_golden` failed naming `case='step'` with a full dict diff. Reverted → green.
2. **`CLI_PATH` mutation (the load-bearing one)**: real subprocess-level — copied `implementation_cli.py` to a decoy filename, monkeypatched `impl.CLI_INVOCATION` to point at the decoy, cleared the process-local capture cache, ran `test_the_sealed_cli_path_names_the_launcher` for real against the mutated launcher → **FAILED** (`AssertionError: [] is not true` — zero captured cases still named the real launcher). Decoy file removed; `git status` clean. This proves the seal catches Cut 1's single silent failure mode (`CLI_PATH` resolving to the wrong file) at the real-subprocess level, not just via the in-process `NormalizerMutationTests.test_a_different_resolved_cli_path_would_have_been_caught`.
3. **Corpus anti-trim guard**: trimmed the last byte of the real `tests/seal/corpus.py` → `CorpusFingerprintTests.test_corpus_fingerprint_matches` failed with the exact two differing hashes. Reverted → green. (The bundled `test_trimming_the_corpus_source_moves_the_fingerprint` test is a weaker, purely-cryptographic sanity check — this execution proves the actual anti-trim guard fires on a real trim, which that test alone does not.)
4. **Unsealed-set exact membership, addition**: added `"walk"` to the real `tests/seal/unsealed.json` without touching `EXPECTED_UNSEALED` → both `test_every_case_is_either_sealed_or_declared_unsealed` and `test_the_unsealed_set_is_exactly_its_declared_membership` failed, naming `'walk'`. Reverted → green.
5. **Unsealed-set exact membership, removal (sealed without unsealing)**: added a fake `propose` entry to the real `digests.json` while leaving it in `unsealed.json` → `test_every_case_is_either_sealed_or_declared_unsealed` failed on the overlap, naming `'propose'`. Reverted → green.
6. **New-subcommand detection**: monkeypatched `impl.COMMANDS` with a 21st fake entry (in-process, no file touched) → `test_the_case_roster_covers_the_command_roster_exactly` failed, naming `'__fake_21st_subcommand__'`.
7. **Dropped corpus case**: removed `admit-e1` from the real `tests/seal/cases.json` → `test_every_f3_site_is_sealed_in_both_env_states` failed, naming the uncovered site (`admit`, missing its `True`/E1 half). Reverted → green.

All seven mutations reddened their target test with the exact expected message; all reverts confirmed byte-identical (`diff`) and `git diff --stat` empty; the only remaining `git status` entries throughout were the two pre-existing, not-mine files from the parallel `the-engine-leaves-its-skill` effort.

### F5's Companion Mutation — Re-Executed At The Real Subprocess Level

Real file edit (`PRODUCT_DATA = PRODUCT_DIRS[2]`, i.e. `"Results"`, wrong on purpose), real capture of `verify-a`/`verify-b` via `seal_harness.run_case` (actual subprocess, no monkeypatching a module attribute — monkeypatching would have zero effect on the subprocess the harness spawns), then reverted:

```
BEFORE (baseline, matches stored digests.json exactly):
  verify-a (case 12): sha256=d3210f72... bytes=19088
  verify-b (case 13): sha256=d3210f72... bytes=19088   (same digest as case 12 — expected: PRODUCT_DATA correct)

AFTER mutation (PRODUCT_DATA = PRODUCT_DIRS[2]):
  verify-a (case 12): sha256=d3210f72... bytes=19088   <- UNCHANGED
  verify-b (case 13): sha256=e626b814... bytes=19111   <- MOVED

AFTER revert: byte-identical to BEFORE; git diff --stat clean.
```
This exactly reproduces `f5-zero-delta.md`'s pasted numbers (19088→19111, same hash prefixes) independently. Case 12 (fixture A, `Data/` present) is structurally blind to `PRODUCT_DATA` via `expected_dirs`'s `or with_data` short-circuit; case 13 (fixture B, `Data/` absent) is the seal's only instrument for a botched F5. Confirmed.

### The Six Normalizers — Reach + Guard Pairs

All twelve reach/guard tests (`NormalizerMutationTests`, N1–N6) executed and passed in the same run as the rest of the seal suite (`43/43 ok`, 5.3s). Two spot-checked beyond the bundled suite, by direct execution against the underlying functions:

- **N3 (interpreter-only)**: confirmed `sys.executable`-only differences collapse to `<PYTHON>` (reach), while a `CLI_PATH` difference (`other.py` vs `another.py`) survives both N3 and N2 (guard) — matches the coordinator-directed narrowing (design.md D4: erase the interpreter token only, never the whole `CLI_INVOCATION`).
- **N3's pinned companion, `test_the_sealed_cli_path_names_the_launcher`**: this is the test independently re-broken via real subprocess mutation above (item 2) — the strongest possible confirmation that the correction holds and the launcher path survives into sealed bytes.
- **Corpus fingerprint (a seventh, undeclared-in-spec guard)**: trimmed for real (item 3 above) — fires correctly.

### The Unsealed Set — Exact Membership, Confirmed By Both Directions Of Mutation

`propose` is the sole entry, with a 20+ character reason (`test_every_unsealed_entry_states_a_reason` enforces the length floor). Both directions of silent growth are caught by real mutation (see items 4 and 5 above): adding an entry without updating `EXPECTED_UNSEALED`, and moving an entry from unsealed to sealed without removing it from `unsealed.json`.

### Corpus Anti-Trim Guard

`sha256(corpus.py)` is stored as `digests["__corpus_fingerprint__"]` and independently verified to match. Fires red on a real one-byte trim (item 3 above).

### Zero New Skips

Baseline `skipped=6`, confirmed unchanged across three independent full-suite runs during this verification (`473.509s`, `453.483s` combined, plus the original apply-time `463.198s` — all `OK (skipped=6)`). The isolated seal module (`tests.test_implementation_seal`, 43 tests) shows zero skips on its own, confirming none of the new tests are gated or skipped.

### The Operator's Standing Constraint — F3 Byte-Identity, Verified By Execution

Direct execution, not inference: with `IMPLEMENTATION_PROPOSALS` unset, `proposals_root()` returns a value string-identical to the old `FORGE_ROOT / 'proposals'` spelling (`True`); with the override set, it diverges to the override path. `rg` confirms `FORGE_ROOT / 'proposals'` now occurs 0 times and `{proposals_root()}` occurs exactly 5 times (the five interpolation sites) in `implementation_cli.py`. `git diff --stat` against `2d8e0dc` for both `.claude/skills/_core/` and `.claude/skills/proposal-deliberation/` is empty (re-confirmed independently).

### Spec Compliance Matrix

9 requirements, 15 scenarios (re-counted directly from `specs/implementation-cli-seal/spec.md`).

| Requirement | Scenario | Test / Evidence | Result |
|---|---|---|---|
| Seal Capture Scope | Every subcommand is captured | `SealMembershipTests.test_the_case_roster_covers_the_command_roster_exactly` + `test_every_case_is_either_sealed_or_declared_unsealed` | ✅ COMPLIANT |
| Seal Capture Scope | A new subcommand is detected | Same test, re-verified by live in-process mutation (fake 21st `impl.COMMANDS` entry → red, named) | ✅ COMPLIANT |
| Corpus Coverage By Construction | Coverage is asserted | `CoverageTests` (5 tests, all executed, all pass) | ✅ COMPLIANT |
| Corpus Coverage By Construction | A dropped case is caught | `test_every_f3_site_is_sealed_in_both_env_states`, re-verified by real file mutation (dropped `admit-e1` from `cases.json` → red, named `admit`) | ✅ COMPLIANT |
| Normalization Before Digesting | A disabled normalizer reddens | `NormalizerMutationTests` N1–N6 (12 tests, all executed pass); CLI_PATH case independently re-broken at real-subprocess level | ✅ COMPLIANT |
| Normalization Before Digesting | Two immediate captures agree | Real live re-run of `tests/seal_capture.py` (double-run, two independently-built corpora) — wrote `digests.json`/`unsealed.json` byte-identical to committed goldens | ✅ COMPLIANT |
| Digests Committed As Generated Goldens | Digests survive a clean checkout | `git ls-files`/`git check-ignore` confirm `digests.json`, `unsealed.json`, `cases.json` are tracked, not gitignored | ✅ COMPLIANT |
| Unsealed Commands Are Explicit And Exact | An unrecorded addition is caught | Real mutation (`unsealed.json` + `walk`, no test change) → red, named | ✅ COMPLIANT |
| Unsealed Commands Are Explicit And Exact | An unrecorded removal is caught | Real mutation (`propose` moved into `digests.json` while still in `unsealed.json`) → red, named | ✅ COMPLIANT |
| Seal Is Mutation-Provable | One byte breaks the seal | Real mutation (flipped one hex digit of `step`'s stored sha256) → red, full diff shown; reverted | ✅ COMPLIANT |
| F3 Declared-Delta Discipline | The delta predates the capture | `git log`: `598735f` < `b0913a5` < `14d97e9`, independently confirmed | ✅ COMPLIANT |
| F3 Declared-Delta Discipline | `cmd_handoff` is unaffected | `cmd_handoff` confirmed absent from the 5 edited sites (`rg` over the 8 `proposals_root()` call sites); `handoff-e0`/`handoff-e1` pass comparison unchanged | ✅ COMPLIANT |
| F5 Zero-Delta Identity Refactor | F5 leaves every digest unchanged | `5c72ba5` lands after `14d97e9`; `SealComparisonTests` (28/28) pass; independent re-execution of the companion mutation reproduces the exact documented 19088→19111 asymmetry | ✅ COMPLIANT |
| Non-Interference With Sibling Suites | Both baselines hold | Independently re-run: `npm test` 595/0/0; Python suite `Ran 2826 ... OK (skipped=6)`, three times | ✅ COMPLIANT |
| Non-Interference With Sibling Suites | `proposal-deliberation` is untouched | `git diff --stat` against `2d8e0dc` empty for `.claude/skills/_core/` and `.claude/skills/proposal-deliberation/`, independently re-confirmed | ✅ COMPLIANT |

**Compliance summary**: 15/15 scenarios compliant.

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| F3's 5-site conversion | ✅ Implemented | `FORGE_ROOT / 'proposals'` count 0, `{proposals_root()}` count exactly 5, `rg`-confirmed |
| F5's identity refactor | ✅ Implemented | `PRODUCT_DATA = PRODUCT_DIRS[1]`, `expected_dirs` reads from it, no bare `"Data"` literal remains in that function's source |
| Harness real-subprocess execution | ✅ Implemented | `full_argv = shlex.split(impl.CLI_INVOCATION) + [command] + argv`, `subprocess.run(..., timeout=120)` |
| Scratch isolation | ✅ Implemented | All writing commands scratch under `implementations/_seal_*`, `rmtree`d in `finally` |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1 — env-var gating rejected, comparison inside `unittest discover` | ✅ Yes | Confirmed: no skip-based gating anywhere in the seal test file; zero new skips |
| D2 — real subprocess, `CLI_INVOCATION`-sourced argv, `str(CLI_PATH)` survives normalization | ✅ Yes | Confirmed by the CLI_PATH mutation re-execution above |
| D3 — corpus built per-run from committed source, anti-trim fingerprint | ✅ Yes | Confirmed by real trim mutation |
| D4 — N3 narrowed to interpreter-token-only (coordinator correction) | ✅ Yes | Confirmed live: `<PYTHON>` collapses interpreter differences only, launcher path text survives |
| D6 — unsealed set as literal frozenset, deliberate friction against silent growth | ✅ Yes | Confirmed by both-direction mutation |
| D8 instrument 4 — F5's asymmetric mutation as the load-bearing proof | ✅ Yes | Independently reproduced, exact byte counts match |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in apply-progress (#1638), 3-row table |
| All tasks have tests | ✅ | F3 (2.3/2.4), F5 identity (8.3), F5 mutation (8.5b) all have test files that exist |
| RED confirmed (tests exist) | ✅ | `F3AnchorTests`, `F5IdentityTests` exist and were re-executed |
| GREEN confirmed (tests pass) | ✅ | All re-run green in this verification |
| Triangulation adequate | ✅ | 43 distinct test cases across 11 classes, varied expected values (not all-empty/all-trivial) |
| Safety Net for modified files | ✅ | `implementation_cli.py` modified; full suite (2826 tests) re-run before/after both F3 and F5 per tasks.md 2.5/7.8/9.5 |

**TDD Compliance**: 6/6 checks passed

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Integration/E2E (real subprocess, real CLI, real git) | 43 | 1 (`tests/test_implementation_seal.py`) | Python `unittest` + `subprocess` |
| **Total** | **43** | **1** | |

All 43 tests are effectively integration/e2e-layer: every assertion either runs the real CLI as a subprocess or exercises `normalize()`/`expected_dirs()` as pure functions directly imported from the production module — none are mocked.

---

### Assertion Quality
✅ All assertions verify real behavior. Scanned for tautologies (`assertTrue(True)`, `assertEqual(1,1)`) — none found. Loop-based assertions (`for case in ...: with self.subTest(...)`) checked for ghost-loop risk — every one has either a preceding non-emptiness assertion (`test_the_sealed_cli_path_names_the_launcher`'s `self.assertTrue(carriers)`) or a companion pinning test guaranteeing non-empty input (`test_n4_no_session_outside_the_pinned_set` iterates 13 real `--session`-bearing cases). Zero `mock`/`Mock`/`patch` usage across the file (72 assertions, 0 mocks) — real subprocess execution throughout.

**Assertion quality**: 0 CRITICAL, 0 WARNING

---

### Quality Metrics
**Linter**: ➖ Not configured for Python; JS linter not run (out of scope — no JS files changed by this change)
**Type Checker**: ✅ No errors (`npm run typecheck` exit 0; this change touches no `.ts` files)

### Issues Found

**CRITICAL**: None

**WARNING**: None

**SUGGESTION**:
- S1 — The `digests.json` 29-key / 29-case coincidence (28 case digests + 1 `__corpus_fingerprint__` metadata key, landing on the same number as the 29-case corpus) is correct but reads as ambiguous to a future maintainer unfamiliar with the fingerprint key. Consider a one-line comment in `digests.json`'s neighborhood (or a `README` in `tests/seal/`) stating "29 = 28 sealed cases + 1 corpus fingerprint" so a future count-based sanity check doesn't repeat this session's momentary confusion. Purely documentation; the mechanism itself is sound and already commented in `seal_capture.py`.
- S2 — `test_trimming_the_corpus_source_moves_the_fingerprint` (the bundled anti-trim sanity test) only proves that two different byte strings hash differently — a general property of SHA-256, not a test of the seal's own trim-detection path. The REAL anti-trim guard (`test_corpus_fingerprint_matches` comparing the stored fingerprint against a freshly-hashed `corpus.py`) is sound and was independently confirmed by a real trim-and-revert in this verification; the bundled companion test is weak but not incorrect, and does not affect the verdict.

### Verdict
**PASS** — 9/9 requirements and 15/15 scenarios compliant, every scenario confirmed by direct execution (in most cases a real file mutation with a confirmed-red test and a byte-identical revert, not static inspection alone); both independent full-suite re-runs (`npm test` 595/0/0, Python `2826/OK skipped=6`, three times) match the change's own claims exactly; the apparent `digests.json` 29-vs-28 discrepancy is fully resolved by reading `seal_capture.py`'s own fingerprint-key mechanism and confirmed by independent hash computation, not a defect; the operator's non-interference constraint holds by direct execution (`git diff --stat` empty for both sibling directories, F3's byte-identity proven live). Two documentation-only SUGGESTIONs, no CRITICAL or WARNING findings.
