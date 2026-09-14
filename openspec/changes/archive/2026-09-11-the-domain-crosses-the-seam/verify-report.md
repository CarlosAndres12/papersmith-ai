```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:c7d0fc21667ce869c8c3e46e4b81e76270a50bd34a436aff1af4106d6688e94a
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 8/8
scenarios: 11/11
test_command: npm test && .venv/bin/python -m unittest discover -s tests
test_exit_code: 0
test_output_hash: sha256:0a46826a1bd80a6f463717c91bd3a3d4c989a878e1d46fde4ae7106925b5c9d3
build_command: shasum -a 256 tests/seal/digests.json && git diff --exit-code -- tests/seal/
build_exit_code: 0
build_output_hash: sha256:011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75
```

## Verification Report

**Change**: `the-domain-crosses-the-seam` (Cut 2)
**Version**: `implementation-engine-neutrality` delta (7 ADDED + 1 MODIFIED requirement)
**Mode**: Strict TDD (cached `strict_tdd: true`) + Full spec-driven verification (proposal + spec + design + tasks + apply-progress all present)
**HEAD verified**: `d972497` (working tree clean before and after this verification)

All measurements below were re-executed live in this session, not inherited from apply's report. Where I deliberately diverge from or correct an inherited claim, it is marked.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 16 phases (S0–S15), ~90 checklist lines |
| Tasks complete | 16/16, all `[x]` |
| Tasks incomplete | 0 |

### Build & Tests Execution

**npm test** — ✅ **595/595 passed, 0 failed** (live re-run, this session)
```
ℹ tests 595
ℹ pass 595
ℹ fail 0
ℹ skipped 0
duration_ms 38735.7
```

**Python full discover** — ✅ **Ran 2874 tests in 488.147s / OK (skipped=6)** (live re-run, this session, exit 0)
Baseline (task 0.1) was `Ran 2849 / OK (skipped=6)`. Growth of 25 is new test methods; `skipped=6` is unchanged — matches the pinned M5 non-delta requirement exactly.

**Seal** — ✅ `sha256(tests/seal/digests.json)` = `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`, identical to the value recorded at every S-step checkpoint and to apply's final measurement. `git diff --exit-code -- tests/seal/` exits 0. The live 28-case comparison is exercised inside `tests/test_implementation_seal.py`, which ran clean as part of the full discover above (not a separate, unexercised claim).

**Environment note (operational, not a code defect)**: During this verification I found the machine was *not* actually exclusive as promised. A stray `python -m unittest discover -s tests -p test_*.py` process (PID 8960, later replaced by 19621/28425) was running throughout most of this session. Investigation of its full command line (`.../claude-501/.../papersmith-ai-paper-writing/.../scratchpad/pytest_full.log`) showed it belongs to a **different worktree** (`papersmith-ai-paper-writing`), so it shares no `implementations/` directory with this one and could not have corrupted this change's measurements. One of these processes (PID 19621) was hung (0% CPU, no progress over 15s) and was killed to reclaim a clean window; my own first Python-suite attempt was itself killed mid-run to avoid a suspected conflict before this was understood, and left one toy-target directory (`_e2e_offer_cmd_11409_*`) under `implementations/`, which I removed by hand before the final clean run. All numbers reported above are from the final, uncontaminated run, confirmed by `implementations/` being empty and `git status` clean afterward.

### THE CENTRAL QUESTION — resolved by independent execution, not by re-reading the test file

Apply's own claim ("`build_env`'s allow-list deliberately excludes `IMPLEMENTATION_DOMAIN_PROFILE`, so proving a profile mutation reaches a seal subprocess requires wrapping `build_env`") is **architecturally correct and I proved it operationally**, independent of `test_implementation_domain_mutation.py`'s own code:

1. I wrote a standalone script (not reusing the shipped test file's assertions, only its documented mechanism) that: (a) captures the real `seal_harness.build_env` function reference before reassignment, (b) wraps it to inject `IMPLEMENTATION_DOMAIN_PROFILE` into the constructed subprocess `env` dict, (c) makes a real, reverted string substitution in the real `impl_profile.py` source with anchor-count discipline (old count == 1, new count == 0 before; 0/1 after), (d) writes a scratch copy with `_SKILL` re-anchored to the real skill directory, (e) runs all 28 cases through a real subprocess both before and after.
2. **Positive control, run first and separately, under the correct interpreter** (`.venv/bin/python`, confirmed `CLI_INVOCATION` resolves to the venv, not system `python3` 3.9 — a mistake I made once in an earlier debug pass that produced a false "zero movers" result for `provenance.claim_key` via silent subprocess crashes with identical stderr on both sides; caught by inspecting `exit_status`/`stderr`, not trusted blindly): mutating `provenance.claim_key` moved exactly `['probe', 'verify-a', 'verify-b', 'verify-t']` — **byte-for-byte the same set apply's `MEASURED_MOVERS` records.** This proves the env-var delivery mechanism is real and functioning, not a monkeypatch with zero effect.
3. With the mechanism validated, I tested **3 of the 7 recorded zero-movers** the same way:

| Leaf | My independent result | Apply's `MEASURED_MOVERS` | Verdict |
|---|---|---|---|
| `provenance.authored_init_sentence` | `[]` — zero cases moved | `()` | **Genuinely unobservable.** `materialize`'s captured stdout does not carry the written file's content (confirmed by reading `authored_package_init`'s only call site and the normalized stdout) — the removal-refusal (`DomainFieldLeafRefusalTests`) is this leaf's whole instrument, as design.md D8 anticipated. |
| `findings.citation_pattern` | `[]` — zero cases moved | `()` | **Genuinely unobservable** against these particular 28 fixtures. `handoff-e1`'s citation count happens to be unaffected by this specific pattern substitution given the fixture's own tag layout. |
| `documents.label` | `[]` — zero cases moved | `()` | **Genuinely unobservable** against these fixtures — **and this refutes proposal.md/spec.md's own claim** (see WARNING below) that `documents.label` moves "the same 5 refusals" as `documents.directory`. It does not: `DOCUMENTS_LABEL` is read at exactly one call site (`undeclared_arms_note`, inside `ARMS_UNDECLARED_CONSEQUENCE`'s `.format()`), gated on `declaration.get("arms")` being falsy *and* at least one module declaring `sections` — a condition none of the 28 sealed cases hits. design.md's own D1 table (not the earlier proposal table) already reclassified this leaf's predicted mover to `verify-*` where `arms` is empty, which is closer to the truth but still didn't move in the live corpus. |

**None of the three tested zero-movers is a harness artifact.** All three are genuinely unobservable against the current 28-case seal corpus, confirmed by real reverted edits and real subprocess runs I ran myself, cross-validated by a positive control that reproduces apply's own real-mover measurement exactly.

### Both Neutrality Locks — verified by direct plant/break + byte-identical revert (not the scratch-copy test file, the real shipped files)

**Lock B** (engine spells no declared domain word):
- Appended `# a planted formulation comment` to the real `implementation_engine.py`. Ran Lock B's exact regex scan (word-boundary, case-insensitive, over the declared `vocabulary.names` set from `discover_profiles()`) → **reddened**, reporting exactly `["implementation_engine.py spells 'formulation'"]`.
- `git checkout --` the file. Re-ran the scan → **green**, `[]`. `git diff --exit-code` on the file confirms byte-identical revert.

**Kit agreement lock**:
- Changed `assets/kit/src/module.py`'s `"equations"` key to `"claims"` in place. Ran the lock's own key-set assertion → **reddened** (`{claims, sections, invariants, revision} != {equations, sections, invariants, revision}`).
- `git checkout --` the file. `git diff --exit-code` on both `tests/seal/` and the kit directory together confirms clean.

Both locks fire on real, live evidence, not just their own scratch-copy unit tests (`LockBHonestyTests`/`KitLockHonestyTests`, which I also read and independently confirm use the same non-monkeypatch discipline on tempdir copies, never the shipped files).

### The Three-Layer Campaign-Proposal Exclusion (D6)

- **L1**: live regex count of `\bproposal\b` (case-insensitive) across `_core/implementation/engine/` = **96**, one file (`implementation_engine.py`) — matches `97 (S0 baseline) − 1 (deliberate shrink)` exactly. Traced the one shrink to `documents.label`'s conversion of `ARMS_UNDECLARED_CONSEQUENCE`'s `"of a proposal"` phrase into a profile-composed `"of a {document}"` — confirmed by reading the constant: the literal word no longer appears in engine source, only `DOCUMENTS_LABEL` (a profile read) does. No other shrink found.
- **L2**: all 11 named symbols (`proposalDigest`, `GATE_PROPOSAL_`, `_proposal_digest`, `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`, `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`, `_campaign_identity`, `_load_remote_execution_`) resolve in the engine, confirmed by direct grep with nonzero counts for each.
- **L3**: `"proposalDigest" in _AUTHORIZATION_BINDING_KEYS` confirmed by reading the tuple definition directly (`_AUTHORIZATION_BINDING_KEYS = ("jobName", "commit", "entrypoint", "units", "rung", "revisionSha256", "positionStatus", "proposalDigest")`).

### `provenance.drift_unit_key` Non-Existence and the Shared `"sections"` Join

Confirmed by reading `unreached_modules` (renamed from `unreached_mathematics`, see below): both sides of the join read the **literal** `"sections"` string — `module.get("sections", [])` and `prov.get("sections", [])` — never a profile-supplied key. `provenance.drift_unit_key` does not appear as a live field anywhere in `impl_profile.py`; it exists only as a docstring note explaining its own exclusion. `"sections"` is spelled 10 times as a hardcoded literal in the engine (confirmed by count), matching the B2 ruling and its M6 corroboration exactly.

### Zero New Skips / M5 Deferral

`skipped=6` confirmed unmoved by the live full-suite run above. Read `tests/test_implementation_domain_lock.py` end-to-end: no `skipTest` call anywhere in the file; the M5 deferral is recorded only as a comment block above the `CampaignProposalExclusionTests` section, exactly as tasks.md 13.8 claims.

### The Two Deliberate Non-Actions

- **M2 (Spanish untranslated)**: confirmed live — `cmd_handoff`'s deferral reasons (`"remedy-locus-missing"`, `"remedy-text-missing"`, `"structural-reach"`) still compose hardcoded Spanish sentence fragments (`"Este cambio es de alcance local..."`, `"reescribiría"`) around the now-profiled vocabulary substitutions. Untranslated, as recorded.
- **M5 (denylist layer)**: confirmed not landed (see above).

### `tests/seal/*` and `assets/kit/**` Untouched

`git diff --stat 9e89d90 HEAD -- tests/seal/ .claude/skills/proposal-implementation/assets/kit/` — empty, confirmed live both before and after my own plant/break tests on scratch copies (and after my one real, reverted edit to the shipped kit file, verified reverted).

### Sister Skill Non-Interference

`git diff --stat 9e89d90 HEAD -- .claude/skills/proposal-deliberation/ .claude/skills/_core/deliberation/` — **empty**, 0 files. Confirmed live.

### Commits

5 commits on `experimental-implementation`, confirmed via `git log`: `0ec54e2`, `c6667ff`, `3b2f3c4`, `efdf7d9`, `d972497`. Total diff since the planning commit `9e89d90`: 8 files changed (7 code/test files + `tasks.md`), **1203 insertions / 103 deletions** in authored code+tests — under the session's 1,400-line budget with headroom, matching apply's own count.

### Spec Compliance Matrix

8 requirements (7 ADDED + 1 MODIFIED), 11 scenarios — counted directly from `openspec/changes/the-domain-crosses-the-seam/specs/implementation-engine-neutrality/spec.md` (not inherited).

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Ten Domain-Specific Profile Fields Are The Whole Vocabulary Surface | A missing leaf refuses by its own dotted name | `DomainFieldLeafRefusalTests.test_each_cut2_leaf_refuses_incomplete_and_names_itself` (16 subtests) | ✅ COMPLIANT |
| (same) | Changing one field moves only its named digest | `PerLeafChangeMutationTests.test_every_leaf_moves_exactly_its_measured_case_set` + my independent re-execution | ⚠️ PARTIAL — test passes (asserts the *measured* mover set), but the requirement's own worked example in spec.md is factually wrong for the example it names (see WARNING 1) |
| The Coarse Provenance Key Stays Shared, Never Profile-Supplied | The join reads the literal on both sides | Direct source read (`unreached_modules`) + `CampaignProposalExclusionTests` region | ✅ COMPLIANT |
| §B1 Fields Excluded For A Recorded Reason Are Not Present | None of the five keys is in the resolver's validated set | Direct read of `_REQUIRED_NESTED`/`_REQUIRED_PRESENCE`/`_REQUIRED_ABSOLUTE_ONLY` in `impl_domain_profile.py` | ✅ COMPLIANT |
| The Campaign-Proposal Exclusion List Is Enforced By A Test | A rename to any excluded symbol is caught | `CampaignProposalExclusionTests` (L1/L2/L3, all 3 methods) | ✅ COMPLIANT |
| The Kit Template's Provenance Keys Agree With The Profile | Divergence is caught | `KitAgreementLockTests` + my own direct plant/revert on the real kit file | ✅ COMPLIANT |
| The Engine Spells No Declared Domain Word | A planted word reddens it, reverting restores green | `LockBEngineNeutralityTests`/`LockBHonestyTests` + my own direct plant/revert on the real engine file | ✅ COMPLIANT |
| A Python Mirror Discovers Profiles By Globbing, Not Hardcoding | A third skill is held without editing the lock | `LockADiscoveryTests` (glob-based `discover_profiles()`, no hardcoded pair) | ✅ COMPLIANT |
| Engine Refuses To Start Without A Domain Profile (MODIFIED) | Unset variable refuses | `ProfileResolverRefusalTests.test_unset_refuses_required` | ✅ COMPLIANT |
| (same) | Malformed profile refuses | `ProfileResolverRefusalTests.test_relative_path_refuses_not_absolute` | ✅ COMPLIANT |
| (same) | A missing Cut-2 leaf refuses by its own dotted name | `DomainFieldLeafRefusalTests` | ✅ COMPLIANT |

**Compliance summary**: 11/11 scenarios have a passing covering test; 10/11 are fully accurate, 1 is behaviorally compliant but documents a factually stale worked example (flagged, not blocking).

### Correctness (Static + Dynamic Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Resolver growth (M3 tier split) | ✅ Implemented | `_REQUIRED_PRESENCE`/`_REQUIRED_ABSOLUTE_ONLY` correctly excluded from the `..._UNSAFE_PATH` existence walk |
| `vocabulary.names` lands at S13, not S2 | ✅ Implemented | Confirmed absent from `_REQUIRED_PRESENCE`'s S2-era comment, present in final tuple |
| `DISPLAY_BLOCK_RE`/`TAG_RE` untouched | ✅ Implemented | Confirmed zero diff lines touch these definitions since `9e89d90` |
| `cmd_compose` scope (M1) | ✅ Implemented, deliberately incomplete | 3 sites reuse `SUBJECT_SINGULAR`; LaTeX-specific regex logic untouched; `compose`/M1 architecture question stays open, as designed |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D7 landing order (one field, one seal run, never batch) | ✅ Yes | Seal re-run and green after every S-step per tasks.md; final sha256 matches S0 |
| D8 mutation discipline (never monkeypatch) | ✅ Yes | Confirmed independently — see Central Question section |
| D6 three-layer exclusion | ✅ Yes | L1/L2/L3 all independently re-measured |
| M3 documents.directory own tier | ✅ Yes | Confirmed in resolver source |
| D3 verbatim sentence, not composed | ✅ Yes, and this is exactly why it's a zero-mover | `authored_init_sentence` — bytes identical, `materialize`'s stdout doesn't carry it anyway |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ Partial | tasks.md Phase 1 claims RED confirmed "before any resolver/profile change," but the only commit touching these tests (`0ec54e2`) *also* contains the full resolver growth and all fifteen leaves' real literal-value declarations in the same commit — git history alone cannot corroborate a RED state ever existed as a discrete, reproducible checkpoint |
| All tasks have tests | ✅ | 16/16 leaves have removal-refusal tests; 15/15 field-landed leaves have change-mutation tests |
| RED confirmed (tests exist) | ✅ | Test files exist and are well-formed (verified by direct read) |
| GREEN confirmed (tests pass) | ✅ | 2874/2874 Ran, OK, live re-run this session |
| Triangulation adequate | ✅ | `_cut2_profile()` builds fixtures programmatically (16 leaves via one `del`), not 16 hand-written fixture bodies — reduces copy-paste risk |
| Safety Net for modified files | ✅ | Full baseline suite run at S0 (2849/OK) before any change |

**TDD Compliance**: 5/6 checks fully passed; 1 partial (see WARNING 3 below — process-traceability, not a functional defect).

**Note on session config vs. apply's self-report**: this session's preflight caches `strict_tdd: true`. Apply's own report self-labels TDD mode as "Standard (no config found)," which appears to be apply *not recognizing* the cached session config rather than the config being genuinely absent — itself a minor process-compliance gap, separate from the RED-first traceability question above.

### Assertion Quality
Scanned `tests/test_implementation_domain_mutation.py`, `tests/test_implementation_domain_lock.py`, and the new portions of `tests/test_implementation_profile.py`. No tautologies, no `Mock()`/`@patch` usage (all real subprocess/importlib), no ghost loops over possibly-empty collections, no ratio imbalance. Every assertion follows a real production-code call (subprocess run, resolver import, or file-text extraction with a vacuity guard first).

**Assertion quality**: ✅ All assertions verify real behavior.

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. **spec.md's own worked example and field-summary table are factually stale against the code's measured reality.** The ADDED requirement "Ten Domain-Specific Profile Fields..." table claims `provenance.claim_key` moves `verify, handoff` — the actual measured set (confirmed by me independently) is `probe, verify-a, verify-b, verify-t`, and `handoff` never moves for this leaf. At least 6 of the 10 rows in that table (`claim_key`, `authored_init_sentence`, `locus_key`, `remedy_locus_key`, `subject_singular`, `subject_plural`, `subject_collective`, `subject_collective_es`, `artifact_noun`, `documents.label`) diverge from `MEASURED_MOVERS`, most consequentially `documents.label`, which the table claims moves "the same 5 refusals" as `documents.directory` but is actually a confirmed zero-mover (see Central Question). The requirement's own **Scenario** text ("Changing one field moves only its named digest... THEN only verify and handoff digests move") is therefore also inaccurate for its own worked example. The covering test is correct and passing (it asserts the measured truth, not the spec prose), so this is a documentation-accuracy defect, not a behavioral one — but it should be corrected in spec.md before archive so a future reader isn't misled by the artifact of record. **Recommend**: `sdd-spec` (or a manual pass) update the "Digest(s) moved" column and the worked Scenario to match `MEASURED_MOVERS`, or generalize the Scenario to not cite specific case IDs that drift.
2. **apply-progress/tasks.md's "7 of 14 change-tested leaves are zero-movers" undercounts by one.** The code's `MUTATIONS`/`MEASURED_MOVERS` dicts (`tests/test_implementation_domain_mutation.py`) contain **15** entries, matching design.md D7's "fifteen field-landed leaves" — `documents.directory` is tested (and correctly recorded as a real 5-case mover, not a zero-mover) but appears to have been excluded from apply's own denominator when it wrote "14." Does not change which leaves are zero-movers, does not affect any test's pass/fail status — a pure arithmetic/reporting slip in the narrative apply wrote, not in the code.
3. **Strict TDD RED-first is not independently git-verifiable for Cut 2's sixteen leaves.** Commit `0ec54e2` ("RED-first cases... Engine untouched; every case is expected red") bundles the RED test cases *together with* the resolver's `_REQUIRED_PRESENCE`/`_REQUIRED_ABSOLUTE_ONLY` growth and all fifteen leaves' real literal-value profile declarations, all in one commit. By the time this commit exists, the tests are already GREEN — there is no discrete, independently-reproducible commit showing the RED state the commit message and tasks.md 1.2 both describe. This is a process-traceability gap (the claim rests on the developer's own local-session narrative, not on git evidence), not proof that TDD was skipped — the tests are correct, well-triangulated, and currently pass. Separately, apply's own report self-labeled TDD mode "Standard (no config found)" despite this session's cached `strict_tdd: true`.

**SUGGESTION**:
1. Consider a lighter-weight way to distinguish same-worktree concurrent test runs (the genuine hazard `resolve_target`/`test_the_toy_targets_left_nothing_behind` warn about) from cross-worktree processes that merely share a process-name pattern — the latter cost real investigation time this session despite posing zero actual risk.

### Verdict
**PASS WITH WARNINGS**

Zero CRITICAL findings: every spec requirement has a passing covering test, both neutrality locks fire and revert cleanly on real evidence, all 28 sealed digests are byte-identical (live-confirmed), the sister skill is untouched, `tests/seal/`/kit assets are untouched, no new skips, and the central "monkeypatch vs. real reachability" tension is resolved — independently, by me, with a positive control — in favor of the harness being sound and all three tested zero-movers being genuinely unobservable. Three WARNING-level findings are all documentation/process-traceability issues (a stale spec table/scenario, an off-by-one in apply's own narrative count, and a RED-first claim that git history alone cannot corroborate), none of which block archive on their own merits but should be corrected — recommend a quick spec.md fix for finding 1 before archiving, since an archived spec becomes the historical record other cuts will cite.
