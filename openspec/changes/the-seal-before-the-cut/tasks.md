# Tasks: The Seal Before The Cut

> **Size note.** This exceeds the usual 530-word budget deliberately, matching design.md's
> own exception. Full ordering (declare → F3 → harness → capture → F5 → non-interference)
> is the change; compressing it is how a task list loses the ordering that is the point.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~450–750 authored (harness, corpus, normalizers, mutation tests) + ~10 modified production lines (F3+F5); digests.json/cases.json are generated goldens, excluded |
| 1400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending (fits within budget; no size:exception needed) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low (graded against session's 1400-line budget)

### Suggested Work Units (same PR, independent rollback boundaries per proposal)

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | F3: 5 refusal sites → `proposals_root()` | PR 1 (single) | `python -m unittest tests.test_implementation_seal.F3AnchorTests` | Real subcommand run (`admit` under E0/E1) | `git revert` restores all 5 strings; independent of seal/F5 |
| 2 | Seal harness + capture (corpus, normalizers, cases, digests) | PR 1 (single) | `.venv/bin/python -m unittest discover -s tests` | `tests/seal_capture.py` (real subprocess ×2 per case) | Delete `tests/seal/`, `tests/seal_capture.py`, `tests/test_implementation_seal.py`; both suites return to baseline |
| 3 | F5: `PRODUCT_DATA` constant + `expected_dirs` | PR 1 (single) | `python -m unittest tests.test_implementation_seal.F5IdentityTests` | Seal comparison on cases 3/4/12/13 | Revert constant + comparison line; restores bare `"Data"` |

## Phase 1: F3 — Declare Before Applying

- [x] 1.1 Assert (paste): `implementation_cli.py` source has `FORGE_ROOT / 'proposals'` × 5, `{proposals_root()}` × 0. Verified live: 5/0.
- [x] 1.2 Write `f3-message-delta.md`: before/after text for all 5 sites (`cmd_admit`, `cmd_position`, `cmd_gate`, `cmd_offer`, `cmd_close`), per design D7 table; unchanged second-line continuations noted; `cmd_handoff` noted as untouched precedent.
- [x] 1.3 Commit the delta doc alone; record its sha (feeds task 6.2). **sha `598735f315d3122e984c33d61935af6f7c717e6f`**

## Phase 2: Apply F3

- [x] 2.1 Edit the 5 sites — re-locate by the string `FORGE_ROOT / 'proposals'`, not by line — to `{proposals_root()}`; preserve each site's own indentation.
- [x] 2.2 Assert (paste) flipped counts: `FORGE_ROOT / 'proposals'` × 0, `{proposals_root()}` × 5. Verified live: 0/5.
- [x] 2.3 RED→GREEN: add permanent `test_no_refusal_names_a_directory_the_code_never_read` (count == 0). Mutation-proven: reverted site 1 → both F3 tests red (`AssertionError: 1 != 0`); restored → green.
- [x] 2.4 RED→GREEN: add `test_a_refusal_under_an_override_names_the_override` — `admit` with `IMPLEMENTATION_PROPOSALS` pointed at an empty dir; message contains that dir, not `FORGE_ROOT / "proposals"`. Same mutation proof as 2.3.
- [x] 2.5 Run python suite; confirm no failures, skip count unchanged at this point. `Ran 2785 tests in 528.710s` / `OK (skipped=6)` — 2783 baseline + 2 new F3 tests, 0 failures, skips unchanged.

## Phase 3: Harness Scaffolding (no production code)

- [ ] 3.1 Create `tests/seal/__init__.py`.
- [ ] 3.2 Create `tests/seal/corpus.py`: `build(root) -> Roots`; fixtures A (provenance+findings+PRODUCT_DIRS tree, declared family `seal-1.md`), B (A minus `Data/`, same declared family — this is the load-bearing F5 instrument, see design.md D3/D8, keep it), T (case 14 only: `__benchmark__` undeclared, module provenance declares family `draft-1.md`, falling back exactly like the existing precedent `test_a_directory_nobody_manages_behaves_exactly_as_it_did` — `verify`'s discovery/tied fields derive solely from the target's own declared revision, never from `--revision`, so case 14 cannot share fixture A's family), P (marker-owned `seal-1/2.md`, hand-authored `draft-1.md`/`draft-01.md` tie), `plan.json` template (target path injected per-case by the harness, not static — see `<PLAN>` placeholder, task 3.6); `git init` with pinned identity/`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`; `CORPUS_FINGERPRINT_SOURCE`.
- [ ] 3.3 Create `tests/seal/normalize.py`: N1 `iso8601_timestamps`, N2 `absolute_roots`, N3 `cli_invocation` (interpreter token ONLY — `shlex.quote(sys.executable or "python3")` → `<PYTHON>`; NOT the whole `CLI_INVOCATION` value, so `str(CLI_PATH)` survives into N2 as `<FORGE>/.../implementation_cli.py`), N5 `git_shas`; `NORMALIZERS = (N3, N2, N1, N5)`, order pinned (N3 before N2 — the venv interpreter itself resolves under `FORGE_ROOT`, so N2 would mangle N3's match if it ran first). **Design correction, applied before capture**: the original N3 erased the whole `CLI_INVOCATION` including the launcher path, which would have hidden Cut 1's `CLI_PATH`-misresolution failure mode; narrowed per design.md D4 update.
- [ ] 3.4 Create `tests/seal/cases.json`: 29 cases per design D3 table, all 20 `COMMANDS`; `<TARGET>`/`<PROPOSALS>` placeholders; `--session` literals restricted to `{"seal-s1","seal-s2"}`.
- [ ] 3.5 Build constructed-env allow-list: `PATH`, `HOME`, `PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1`, `LC_ALL=C.UTF-8`, `TZ=UTC`, `NO_COLOR=1`, `COLUMNS=80`, `GIT_CONFIG_GLOBAL`/`SYSTEM=/dev/null`, `IMPLEMENTATION_PROPOSALS` only when case says.
- [ ] 3.6 Create `tests/seal_capture.py`: argv = `shlex.split(impl.CLI_INVOCATION) + case_argv`, `shell=False`, `timeout=120`, per-case `copytree` scratch; run each case twice, refuse-and-write-nothing + unified diff on disagreement. Third placeholder `<PLAN>` beside `<TARGET>`/`<PROPOSALS>` (apply/materialize cases only): harness writes a small `plan.json` sibling to (never inside) the case's copied git target, with `"target"` injected as that case's own resolved scratch path and the other four `build_plan()` fields at their fixed (empty) values — never a statically committed plan.json, since the exact-string `target` match in `_materialize_plan_gate`/`cmd_apply` would only ever match one specific tmpdir.

## Phase 4: Threat-Matrix RED Tests (before capture runs live)

- [ ] 4.1 Roster validator refuses a case whose argv contains a shell metacharacter.
- [ ] 4.2 Env-builder test: emits no key outside the allow-list.
- [ ] 4.3 Writing-case guard: refuses a case whose `--target` is not under the scratch root.
- [ ] 4.4 Confirm every `subprocess.run` call carries `timeout=120`; a timeout is a hard failure, never routed to `unsealed.json`.

## Phase 5: Normalizer Mutation Proofs (RED before GREEN, D4 table)

- [ ] 5.1 N1 reach: disable N1 → two timestamp-only-differing samples stay distinct (red); re-enable → collapse (green). Guard: `2026-09-10` vs `2026-09-11` stay distinct.
- [ ] 5.2 N2 reach/guard: tmpdir-only difference collapses; `src/Seal/__init__.py` vs `steps.py` and `/usr/bin/x` stay distinct.
- [ ] 5.3 N3 reach/guard: interpreter-token-only difference collapses (two samples differing only in `sys.executable`'s path collapse to `<PYTHON>`); `python3 other.py` vs `python3 another.py` stay distinct — proving a `CLI_PATH` difference survives both N3 and N2. PLUS `test_the_sealed_cli_path_names_the_launcher`: pinned assertion (N4's idiom) that every `CLI_INVOCATION`-derived case's normalized text contains the literal `<FORGE>/.claude/skills/proposal-implementation/scripts/implementation_cli.py`; mutation — substitute a different resolved path into the raw pre-normalization text → red. This is the change's single most load-bearing mutation (design.md D4).
- [ ] 5.4 N4 pinned-not-erased: change one case's `--session` literal → its digest moves (proves reach); assert no value outside `{"seal-s1","seal-s2"}` appears.
- [ ] 5.5 N5 reach/guard: 40-hex collapses to `<GITSHA>`; a 64-hex `sha256` survives; no 7–12 hex short sha in any golden.
- [ ] 5.6 N6 (deliberately unnormalized): flip one byte in `src/Seal/__init__.py` inside the corpus → case-12 digest moves; a future `<DIGEST>` normalizer would make this red.
- [ ] 5.7 `test_normalizer_order_is_pinned`: `NORMALIZERS` identity tuple, N3 before N2.

## Phase 6: Capture The Seal (post-F3 code)

- [ ] 6.1 Run `tests/seal_capture.py`; paste full output; on success it writes `tests/seal/digests.json` and `tests/seal/unsealed.json` (`{}` today) — commit both.
- [ ] 6.2 Confirm ordering: `f3-message-delta.md` commit (1.3) predates the digests commit; paste `git log --oneline` evidence.

## Phase 7: Comparison Suite, Coverage, Membership

- [ ] 7.1 `tests/test_implementation_seal.py`: run each of 29 cases once, normalize, compare to `digests.json`.
- [ ] 7.2 Coverage tests (over captured *output*, not fixture): `test_provenance_reaches_the_output`, `test_findings_reach_the_output` (all 3 of inline/deferred/settled + `introduces`), `test_corpus_provably_exercises_data_present_and_absent` (construction-level: fixture A's `Seal/Data/` exists, fixture B's does not — replaces the falsified `test_data_absence_is_visible`, per coordinator decision and design.md D3's correction), `test_both_revision_families_and_a_tie_are_exercised`, `test_every_f3_site_is_sealed_in_both_env_states` (exact set `{admit,position,gate,offer,close}×{E0,E1}`).
- [ ] 7.3 Membership tests: `test_every_case_is_either_sealed_or_declared_unsealed`, `test_the_unsealed_set_is_exactly_its_declared_membership` (`EXPECTED_UNSEALED = frozenset()`), `test_the_case_roster_covers_the_command_roster_exactly`, `test_every_unsealed_entry_states_a_reason`.
- [ ] 7.4 `test_corpus_fingerprint_matches`: `sha256(corpus.py)` vs stored; trim a case → red.
- [ ] 7.5 **Seal mutation proof**: flip one byte of one stored golden stdout → comparison goes red; demonstrate, paste, then revert the mutation.
- [ ] 7.6 Measure discover-delta: `time` `unittest discover -s tests` before/after this phase; paste both; ceiling ≤60s (if exceeded, cut duplicate cases only, never covered commands).
- [ ] 7.7 Open question — `materialize` (case 28): run once; if slow or writes outside scratch, pin at a refusal leg like `step`/`env` and update `cases.json`; else keep its current non-destructive leg. Record the decision in design.md's Open Questions.
- [ ] 7.8 Confirm python suite: `Ran 2783+K ... OK (skipped=6)`, zero new skips, zero failures; paste.

## Phase 8: Apply F5 (after capture only)

- [ ] 8.1 Add `PRODUCT_DATA = PRODUCT_DIRS[1]` beside `PRODUCT_NOTEBOOKS`, with the D8 comment.
- [ ] 8.2 Edit `expected_dirs`: `d != PRODUCT_DATA or with_data`.
- [ ] 8.3 RED→GREEN: `test_the_data_category_is_read_from_the_tuple` (`PRODUCT_DATA == "Data"`, `is PRODUCT_DIRS[1]`, not literal in `expected_dirs` source).
- [ ] 8.4 RED→GREEN: pinned-literal `expected_dirs(with_data=True/False)` outputs (not derived from `PRODUCT_DIRS`).
- [ ] 8.5 Re-run comparison suite (7.1) against the **existing** `digests.json` (no recapture): cases 3, 4, 12, 13 must be byte-identical; paste. Any other case moving is a hard failure — F5 is not applied correctly.
- [ ] 8.5b **The mutation that matters** (coordinator decision, design.md D8 instrument 4): temporarily set `PRODUCT_DATA = PRODUCT_DIRS[2]`; re-run the comparison; assert case 13's digest MOVES and case 12's does not (fixture A is structurally blind to `PRODUCT_DATA` — the `or with_data` short-circuit — so only case 13 can see it); paste before/after digests. Revert; re-assert zero delta (8.5).
- [ ] 8.6 Write `f5-zero-delta.md`: commit sha before/after F5, pasted comparison output both sides, plus 8.5b's reach/revert pair.

## Phase 9: Non-Interference Proof (structural, per operator's constraint)

- [ ] 9.1 `git diff --name-only` (against pre-change HEAD) equals the scope allowlist exactly (`implementation_cli.py`, `tests/test_implementation_seal.py`, `tests/seal/**`, `tests/seal_capture.py`, the two `openspec/changes/the-seal-before-the-cut/*.md` delta docs); paste.
- [ ] 9.2 `git diff --stat -- .claude/skills/_core/` is empty; paste.
- [ ] 9.3 `git diff --stat -- .claude/skills/proposal-deliberation/` is empty; paste.
- [ ] 9.4 Final `npm test`; paste; must show 595 pass / 0 fail.
- [ ] 9.5 Final `.venv/bin/python -m unittest discover -s tests`; paste; must show `Ran 2783+K ... OK (skipped=6)`, K named exactly (new test count from this change).

## Phase 10: Findings Judgment Checkpoint

- [ ] 10.1 At each phase boundary: close a finding inline (fix + note) unless it would change corpus coverage, the normalizer set, or the F3/F5 ordering — then stop, report the finding, and wait rather than absorbing it silently.

  **Fired during Phase 3 research (pre-capture), 2026-09-11.** Two findings surfaced while
  validating fixtures empirically against the real CLI, before writing `corpus.py`/
  `cases.json`:

  1. **Closed inline** (design-only correction, no coverage change): N3's CLI_PATH
     blindness, per the coordinator's own directed fix — see design.md D2/D4, applied
     before any capture ran. Recorded in apply-progress.
  2. **STOPPED, reported — RESOLVED by coordinator decision, 2026-09-11.** The `Data/`
     present/absent coverage cell: apply's byte-equality measurement was confirmed correct
     (`verify`'s output IS identical between the two fixtures today), but the conclusion
     was wrong — case 13 is not there to show a missing `Data/` today, it is the only case
     where a BOTCHED F5 becomes visible at all, because `expected_dirs`'s `or with_data`
     short-circuit makes fixture A structurally blind to `PRODUCT_DATA`'s value. **Both
     fixtures stay.** `test_data_absence_is_visible`'s false claim is replaced, not
     deleted, by `test_corpus_provably_exercises_data_present_and_absent` (7.2) plus a new
     F5-phase mutation proof (8.5b) that sets `PRODUCT_DATA` to a wrong `PRODUCT_DIRS`
     member and requires case 13's digest to move. See design.md D3 (corrected claim with
     its refutation beside it) and D8 instrument 4. Case 14's fixture-family tension is
     closed inline per the coordinator's direction (task 3.2): its own fixture variant,
     not shared with fixture A's declared family.
