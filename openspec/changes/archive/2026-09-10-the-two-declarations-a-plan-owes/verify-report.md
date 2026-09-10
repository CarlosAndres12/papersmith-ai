```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:10e3d397a458c3a82fe30a78f1bca2a7ce94e7301d50af02e3d7d3caf4541dc9
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 29/29
test_command: npm test
test_exit_code: 0
test_output_hash: sha256:0942e6870c9c1d8e40f1a57350af8de34b31c7aa31076f459c32363e0516a92d
build_command: .venv/bin/python -m unittest discover -s tests
build_exit_code: 0
build_output_hash: sha256:da7ceddd762300b0f8aa795543c57f96f1961e07c8380727710ae3f0e99270e1
```

## Verification Report

**Change**: the-two-declarations-a-plan-owes
**Version**: N/A (openspec delta, no numbered spec version)
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 24 |
| Tasks complete | 24 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: N/A — no separate build step for this stack (TypeScript loaded via jiti, no compile gate)

**Tests**: measured independently at HEAD `0f0f4e28b6a52c7735ae08702e8d35d76f0845cd`, worktree clean, both before and after every mutation spot-check below.

```text
$ npm test
ℹ tests 595
ℹ pass 595
ℹ fail 0
ℹ skipped 0
ℹ duration_ms 36557.6

$ .venv/bin/python -m unittest discover -s tests
Ran 2783 tests in 465.152s
OK (skipped=6)
```

**Baseline** (proposal.md, measured on `e5b0c56`): 559 pass, 0 fail. Net new JS tests this change added: 36 (595 − 559).

**Discrepancy investigated, as instructed**: apply's own report (tasks.md 6.1, apply-progress) claims `npm test` = **593**. I measured **595**, twice, independently of the apply agent. The gap is exactly 2, and it is explained, not papered over: `tests/experimental-deliberation-preservation.test.mjs` contains two "D7 identity" tests (`D7 identity: the four pre-existing violation ids…`, `D7 identity: the five pre-existing atom kinds…`, added at task 5.2) that are **not** present in the 58-test count recorded at task 2.2, nor accounted for in the 593 recorded at task 6.1. Running that one file alone today gives 60/60 — 58 (task 2.2's own count, itself already inclusive of the M12-strengthening test added at 2.4) + 2 (the D7 identity tests). Task 6.1 in `tasks.md` is sequenced *after* task 5.2, so its "593" figure was not re-measured after 5.2 landed (or 6.1 ran before 5.2's tests existed and the ordering in the file does not reflect execution order). This is **not** the benign explanation the launch prompt offered ("counted before adding its final tests… while proving mutation M12") — M12's own extra test is already included in both the 58 and the 593 counts; the actual 2-test gap traces to the D7 identity tests from task 5.2, not M12. **This is a WARNING**: a stale self-reported count in `tasks.md`/apply-progress, not a functional defect — the final committed HEAD is fully green with *more* passing tests than reported, not fewer.

### Spec Compliance Matrix

**Domain: `experimental-plan-declarations`** (7 requirements, 22 scenarios)

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| A document declares exactly one dataset | single line accepted | `preservation.test.mjs:357` | ✅ COMPLIANT |
| | missing line refused | `preservation.test.mjs:361` | ✅ COMPLIANT |
| | two lines refused, not de-duplicated | `preservation.test.mjs:368` | ✅ COMPLIANT |
| | v1 checked, not only successors | `initial-revision.test.mjs:258` | ✅ COMPLIANT |
| A declared dataset is a preservation atom | atom extracted from compliant doc | `preservation.test.mjs:398` | ✅ COMPLIANT |
| | changing dataset between versions is a reportable loss | `preservation.test.mjs:408` (id-equality unit test) | ⚠️ PARTIAL — see note 1 |
| | rewording without meaning change is not a loss | `preservation.test.mjs:414` (id-equality unit test) | ⚠️ PARTIAL — see note 1 |
| A document declares exactly one adequate validation scheme | complete scheme accepted | `preservation.test.mjs:434` | ✅ COMPLIANT |
| | novel legitimate test accepted | `preservation.test.mjs:438` | ✅ COMPLIANT |
| | missing line refused | `preservation.test.mjs:444` | ✅ COMPLIANT |
| | denylisted placeholder refused | `preservation.test.mjs:465` | ✅ COMPLIANT |
| | non-test output alone refused | `preservation.test.mjs:469` | ✅ COMPLIANT |
| | named test without seeds/reps refused | `preservation.test.mjs:495` | ✅ COMPLIANT |
| | seeds/reps without named test refused | `preservation.test.mjs:489` | ✅ COMPLIANT |
| | two lines refused | `preservation.test.mjs:449` | ✅ COMPLIANT |
| | one line, more than one test, cardinality satisfied | `preservation.test.mjs:458` | ✅ COMPLIANT |
| A URL inside a dataset/validation-scheme line still needs its verification tag | untagged URL inside dataset line caught by existing rule | `preservation.test.mjs:325` | ✅ COMPLIANT |
| Tutor doctrine opens from dataset, always proposes validation scheme | bullet voice matches section | source read: `SKILL.md:92-93` | ❌ UNTESTED — see note 2 |
| | distinct validation-scheme bullet present | source read: `SKILL.md:93` | ❌ UNTESTED — see note 2 |
| SKILL.md no longer claims v1 unvalidated | section states true v1-gate reach | source read: `SKILL.md:252-256` | ❌ UNTESTED — see note 2 |
| Both rules proven able to fail | deleting dataset rule caught | design mutation #1, manual, not independently re-run by me | ⚠️ PARTIAL — see note 3 |
| | deleting validation-scheme rule caught | design mutation #8, manual, not independently re-run by me | ⚠️ PARTIAL — see note 3 |

**Domain: `deliberation-objective-flow`** (2 requirements, 7 scenarios)

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| North content is profile-supplied | complete profile loads unchanged | `objective-flow.test.mjs` (pre-existing, re-run green) | ✅ COMPLIANT |
| | profile missing objective refuses at load | pre-existing suite, re-run green | ✅ COMPLIANT |
| | experimental profile declares its own north | `objective-flow.test.mjs:148` | ✅ COMPLIANT |
| | validated stage names dataset + validation-scheme conditions | `objective-flow.test.mjs:217,234` (establishes/behindWhen per-skill) | ✅ COMPLIANT |
| Structural conformance verified per loaded profile | structural test passes against a different profile | `objective-flow.test.mjs:202` (loop over 2 skills) | ✅ COMPLIANT |
| | drifted establishes/behindWhen cell caught | `objective-flow.test.mjs:217,234` — proven by mutation M13/M14 (task 1.4, both RED then reverted) | ✅ COMPLIANT |
| | matching establishes/behindWhen passes | same tests, green today for both skills | ✅ COMPLIANT |

**Compliance summary**: 25/29 COMPLIANT, 3 PARTIAL, 3 UNTESTED (prose-only, see notes) — 0 FAILING.

**Note 1** (dataset-atom-loss scenarios): the two "loss" scenarios are covered only by unit tests comparing `extractAtoms()` id output across two document strings, not by an integration test driving the actual `preview`/`accept` flow's `preservationDelta`/`acknowledgedRemovals` refusal. Verified this is **not a regression unique to this change**: grepping the whole `experimental-deliberation-*.test.mjs` suite, no atom kind — including the five pre-existing ones — has such an integration-level loss test in this domain's own suite; the generic diff/acknowledgment mechanism itself is core-owned and exercised elsewhere. The unit tests do verify the exact precondition (id equality/inequality) that drives that generic mechanism, correctly.

**Note 2** (tutor bullets, stale-section correction): both are prose-only requirements against `SKILL.md`. No automated test in this repository checks SKILL.md bullet "voice" or section wording anywhere (searched the full `tests/*.test.mjs` and `tests/*.py` corpus). This matches established practice in this codebase, not a new gap this change introduced. I verified both by direct source reading: `SKILL.md:92-93` carries the two new bullets in the existing bold-lead/reasoning/failure-consequence shape; `SKILL.md:252-256` no longer claims `initial-revision-creation.ts` "contains no reference to violations" and instead states the true reach ("v1 is checked, not exempt… the same `violations()` check the successor path runs"). See Correctness table below.

**Note 3** (mutations #1/#8 not independently re-run): I independently reproduced 3 of the design's 16 mutations by execution (M12, M15, M16 — see Mutation Proof Verification below), all confirmed real and correctly reverted. I did not personally re-execute mutations #1 (delete the dataset-missing push) or #8 (residue check → non-empty check) specifically. Given the demonstrated integrity of the methodology across the three I did check — including M12, the one case that initially survived and required a genuinely strengthened assertion — I have no measured reason to doubt #1/#8, but I have not proven them myself.

### Byte-For-Byte Guarantee — Re-Proven By Command

Ran independently at HEAD `0f0f4e2`, worktree clean throughout:

```text
$ git diff --name-only e5b0c56 HEAD
.claude/agents/experimental-validation.md
.claude/skills/experimental-deliberation/SKILL.md
.claude/skills/experimental-deliberation/preservation-experimental.ts
.claude/skills/experimental-deliberation/profile.ts
openspec/changes/the-two-declarations-a-plan-owes/design.md
openspec/changes/the-two-declarations-a-plan-owes/exploration.md
openspec/changes/the-two-declarations-a-plan-owes/proposal.md
openspec/changes/the-two-declarations-a-plan-owes/specs/deliberation-objective-flow/spec.md
openspec/changes/the-two-declarations-a-plan-owes/specs/experimental-plan-declarations/spec.md
openspec/changes/the-two-declarations-a-plan-owes/tasks.md
tests/experimental-deliberation-initial-revision.test.mjs
tests/experimental-deliberation-preservation.test.mjs
tests/experimental-deliberation-publish.test.mjs
tests/proposal-deliberation-objective-flow.test.mjs
tests/test_agents.py
```
— exactly the design D7 §1 allowlist plus the one reported addition (`tests/test_agents.py`, ruling 9). No extra path, no missing one.

```text
$ git diff --quiet e5b0c56 HEAD -- .claude/skills/_core && echo CLEAN
CLEAN
$ git diff --quiet e5b0c56 HEAD -- .claude/skills/proposal-deliberation && echo CLEAN
CLEAN
$ git diff --quiet -- .claude/skills/_core .claude/skills/proposal-deliberation && echo "EXIT 0"
EXIT 0
```
Conditions 1-3 hold, independently reproven.

Condition 4 (pre-existing rule ids / atom kinds unrenamed) is asserted by test, not read by eye: `preservation.test.mjs`'s two "D7 identity" tests, executed as part of the 595-pass run above, both pass. Confirmed by source read: all 4 pre-existing rule ids (`baseline-missing-repository-url`, `baseline-missing-venue-year`, `report-table-fabricated-value`, `url-without-verification-marker`) and all 5 pre-existing atom kinds (`baseline`, `figure`, `report-table`, `success-criterion`, `url`) are still produced under their original names.

### Mutation Proof Verification — Independently Reproduced

I did not trust the apply report's mutation narrative; I re-derived and executed 3 of the 16 mutations myself, anchor-count-asserted, fresh process, then reverted — as instructed, including M12.

| # | Mutation reproduced | Anchor before | Anchor after | Fresh-process result | Reverted, GREEN confirmed |
|---|---|---|---|---|---|
| M12 | `isRepetitionsClause`'s keyword+digit check replaced with "≥2 digits anywhere in the value" (the literal defect class design names: "reps check accepts any second digit") | 1 occurrence of the original guard | 0 (replaced), 1 new anchor | 59/60 pass, 1 fail: **exactly** `a second, unrelated digit elsewhere in the value does not stand in for a repetitions clause` — the pre-existing/weaker tests (including `t-test over 5 seeds`) stayed green, confirming they alone would NOT have caught this mutation, matching the apply report's own account that M12 initially survived against the original test set | ✅ yes, 60/60 |
| M15 | deleted `dataset-declaration-missing`, `dataset-declaration-repeated` from the agent's confirming-rules mention | 1 occurrence | 0 | `test_the_validation_agents_rule_enumeration_derives_from_the_module` FAILS: `['dataset-declaration-missing', 'dataset-declaration-repeated'] != []` | ✅ yes, test passes |
| M16 | inserted a brand-new, never-mentioned rule id (`mutant-m16-unmentioned-rule`) push into `violations()` | 0 occurrences of new id | 1 | same test FAILS: `['mutant-m16-unmentioned-rule'] != []` — proves the test catches a genuinely NEW unmentioned rule, not only a deleted mention | ✅ yes, test passes |

Every mutation was applied via a uniquely-anchored `sd` replacement, count-asserted before (1) and after (0 old / 1 new), run in a fresh process (`node --test` / a fresh `.venv/bin/python -m unittest`), then reverted with `git checkout --` and re-confirmed green. `git status --porcelain` was empty before, after each mutation's revert, and at the end of the session. This repo's own prior scars (an anchor that matched but never changed bytes; `sd -s` exiting 0 without moving a byte; a mutation surviving because the asserted property was wrong) did not recur here — anchor counts were asserted every time, never inferred from `git diff --stat`.

### Ruling-by-Ruling Verification (in code, not only in artifacts)

| # | Ruling | Verified how | Result |
|---|---|---|---|
| 1 | Two `**Dataset:**` lines refused | `preservation.test.mjs:368`, re-run green | ✅ HONOURED |
| 2 | Labels anywhere in bytes, no section | `DECLARATION` regex is document-wide (`preservation-experimental.ts:68`), no section-boundary logic exists | ✅ HONOURED |
| 3 | North/table equality extended to `establishes`/`behindWhen` | `objective-flow.test.mjs:217,234`, executed, 17/17 green; mutations M13/M14 in tasks.md's own account | ✅ HONOURED |
| 4 | Dataset gets both hard block + atom; validation scheme gets hard block only | code read: `extractAtoms` has a `dataset` entry (`preservation-experimental.ts:366`), no `validation-scheme` atom kind exists anywhere in the file; `preservation.test.mjs:426` asserts the absence explicitly | ✅ HONOURED |
| 5 | No new URL rule for dataset/scheme lines | no new URL-adjacent rule id in `violations()`; existing `url-without-verification-marker` fires (`preservation.test.mjs:325`) | ✅ HONOURED |
| 6 | Dataset takes the SAME denylist as validation scheme | **directly re-executed**: `**Dataset:** TBD` and `**Dataset:** pending` both produce `dataset-declaration-missing`; `isPlaceholderOnly` (line 435) calls `removePhrases(normalized, PLACEHOLDERS)` — the identical `PLACEHOLDERS` constant `validationSchemeContentViolation` uses, confirmed by source read, not inferred | ✅ HONOURED |
| 7 | Seeds accepts synonyms (`seeds`, `semillas`, `initialisations`, `initializations`, `runs`), each with a digit | **directly re-executed**: `SEEDS_TERMS` (line 148) includes all five plus `seed`/`semilla`/`initialisation`/`initialization`/`run`; digit-bearing synonym forms (`5 semillas`, `5 runs`, `10 random initialisations`) all pass. **But**: the SPELLED-OUT form `"five random initialisations"` — the exact phrase both this launch prompt and proposal.md's own ruling-7 row use as an illustrative "correct line" — is measured **refused** (`validation-scheme-without-seeds`), because the check requires a literal digit token (`/^\d+$/`) and "five" is not one. This is not a code defect relative to the rule as actually written ("each with its digit") or its own shipped test (`10 random initialisations`, a digit form) — it is an inconsistency **inside ruling 7's own prose**, which calls a spelled-out-number example "a correct line" in the same sentence that requires "its digit." `spec.md` does not test this specific case either way (no scenario names a seeds-synonym or spelled-out form). | ⚠️ PARTIALLY HONOURED — see Issues |
| 8 | Ruling-8 gate: STOP if `proposal-deliberation` reddens under the extended guard | gate did not fire (task 1.2); independently reconfirmed: `git diff` on `proposal-deliberation` is empty, and `objective-flow.test.mjs` passes 17/17 against it unmodified | ✅ HONOURED |
| 9 | D6 self-deriving enumeration test exists, works both directions, tolerates the deliberate `report-table-fabricated-value` omission | **directly re-executed both directions** (M15, M16 above); confirmed the test checks presence via backtick mention ANYWHERE in the agent body (inclusion OR explicit exclusion sentence), not membership in the confirming list — `report-table-fabricated-value` IS backtick-mentioned in its own "not this stretch's" sentence (`experimental-validation.md:38-42`), so a naive "every rule must be in the confirming list" check would indeed have gone red on this correct omission, and this is NOT what was built | ✅ HONOURED |

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Tutor bullets (dataset-opens, validation-scheme-always-proposed) | ✅ Implemented | `SKILL.md:92-93`, matches existing 8-bullet voice (bold lead / reasoning / failure consequence), 10 bullets total |
| Stale v1 section corrected | ✅ Implemented | `SKILL.md:252-256`, retitled "Creating v1, checked by the same gate as every successor", no longer claims no `violations` reference exists, and no other SKILL.md text contradicts it (searched for "nothing enforces"/"no reference to"/"unvalidated" — none remain) |
| North text moved together (profile.ts + SKILL.md) | ✅ Implemented | byte-identical `validated.establishes`/`behindWhen` text in both files, confirmed by direct read |
| All 24 tasks checked, match code state | ✅ Confirmed | 24/24 `- [x]`, 0 `- [ ]` |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1-D4 (matcher, cardinality, atom, content decomposition) | ✅ Yes | confirmed by source read and mutation spot-checks |
| D5 (head-equality for `behindWhen`, strict equality for `establishes`) | ✅ Yes | confirmed via `objective-flow.test.mjs:217` (establishes, strict) vs `:234` (behindWhen, head-equality), both green for 2 skills |
| D6 (agent coupling + self-deriving enumeration) | ✅ Yes | 11 rule ids in module, all 11 backtick-mentioned in agent (independently grepped); enumeration test proven both directions |
| D7 (byte-for-byte proof) | ✅ Yes | all 4 conditions reproven by command, above |
| **Deviation 1**: north text reworded to avoid C-3 vocabulary-lock collision | ✅ Acceptable | Confirmed real: the design's literal "Proposed moved text" would have collided with `tests/proposal-deliberation-domain-profile-lock.test.mjs`'s pinned-residue guard (a file **not** in D7's allowlist). The chosen fix stayed inside two already-authorized files (`profile.ts`, `SKILL.md`) and avoided editing a byte-for-byte-protected file. Re-ran the C-3 lock test: 12/12 green. The resulting text is meaning-preserving (drops the bare word "validation", keeps "the scheme"/"a scheme line", matching the `composed` stage's own precedent of saying "the equation" unqualified). This is a sound, narrowly-scoped, honestly-reported deviation — no scope creep, no unauthorized file touched. |
| **Deviation 2**: `tests/test_agents.py` added to D7 diff footprint | ✅ Acceptable | Ruling 9 (dated after design.md's D7 list was written) made task 3.7 mandatory, and `tests/test_agents.py` is this repository's existing, established home for agent-contract tests (it already tests other agent files' structural properties) — there is no other sensible home for the D6 self-deriving enumeration test. Explicitly reported in both tasks.md (5.1) and apply-progress. Minimal, single-file, well-justified. |

### Assertion Quality

Scanned all touched/added test files (`preservation`, `publish`, `initial-revision`, `objective-flow`, `test_agents.py`'s new test) for the banned patterns (tautologies, ghost loops, assertion-without-production-call, ratio abuse). None found. Every new test calls `violations()`/`extractAtoms()`/the orchestrator directly and asserts a specific, non-trivial value (a rule-id list, an atom-id string, a specific text diff). The M12 scar test (`a second, unrelated digit elsewhere…`) is itself evidence of active triangulation discipline, not trivia.

**Assertion quality**: ✅ All assertions verify real behavior

### Issues Found

**CRITICAL**: None

**WARNING**:
1. `tasks.md` task 6.1 and `apply-progress` both record `npm test` = 593 pass; the correct, independently-measured figure at the same HEAD is **595** pass, 0 fail, 0 skipped. The 2-test gap traces to the two "D7 identity" tests added at task 5.2 (sequenced after 2.2's "58/58" but seemingly before 6.1's "593" was actually re-measured). Not a functional defect — the real state is more-tested than reported, not less — but a reporting-accuracy gap worth correcting in the artifact record.
2. Ruling 7's own illustrative text ("the literal form refuses 'five random initialisations', which is a correct line") is internally inconsistent with its own operative clause ("each with its digit") in the same ruling row. Measured: the shipped code implements the operative clause faithfully (digit required; synonym token accepted) and its own test proves the digit form (`10 random initialisations`) passes — but the exact illustrative phrase from the ruling itself, spelled out with "five", is still refused today. `spec.md` does not carry a testable scenario for this case either way, so this is not a spec-compliance failure, but the launch prompt's characterization ("'five random initialisations' must NOT be refused") does not hold under direct measurement.
3. Two spec scenarios (dataset-atom-loss, dataset-atom-not-lost-on-reword) and three prose-only requirements (tutor bullets ×2, stale-section correction) have no covering runtime test in this repository — verified by direct source reading instead. This matches established codebase practice (no other atom kind or SKILL.md prose passage in this domain has such a test either), not a regression unique to this change.

**SUGGESTION**:
1. Consider adding an integration-level test (preview → accept, with an unacknowledged dataset swap) at least once, to directly exercise `preservationDelta`/`acknowledgedRemovals` for the new `dataset` atom kind rather than relying solely on `extractAtoms` id-equality — though this is a suite-wide gap across all six atom kinds, not unique to this change, and out of scope to fix here.
2. Consider correcting `tasks.md`'s 6.1/593 figure for the artifact record, given the measured 595.

### Verdict

**PASS WITH WARNINGS**

Zero CRITICAL findings. All 24 tasks complete and match code state. Both suites independently re-run and green (595/0/0 JS; 2783/0/6-skip Python). All four byte-for-byte conditions reproven by command. Nine operator rulings verified in code, eight fully honoured, one (ruling 7) honoured in its operative clause but with a measured internal inconsistency in the ruling's own illustrative prose that the launch prompt inherited without noticing. Three independently-reproduced mutations (including the required M12) all behaved exactly as the apply report claimed, including M12's initial-survival narrative. Three WARNING-level findings recorded above, none blocking: two are reporting-accuracy gaps in the artifact trail, not functional defects; one is testing-layer thinness consistent with pre-existing codebase pattern. Recommend proceeding to archive.
