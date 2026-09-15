```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:eb6625ec57ae18f698fc7d0e25c308b5fa0f961ba8b1f3712d63b37c47adbc8e
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 19/19
scenarios: 46/46
test_command: .venv/bin/python -m unittest discover -s tests -p "test_*.py"
test_exit_code: 0
test_output_hash: sha256:0805a349a45c42fd7a6489a00afbe38fc066c8e230756c33d977f6315add14a3
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:c2a7eb80a830d192cf58e61e0853c42919cb8a7737ec5ad5333b0a0f8a766b5e
```

## Verification Report

**Change**: `the-agreement-nothing-computes` (Slice D — D1 through D6, the whole change)
**Repo**: `/Users/diego/.herdr/worktrees/papersmith-ai/experimental-implementation`, branch `experimental-implementation`, HEAD `5bf66ee37b879547dd0fe9037ce771e1b87d070d`. Worktree clean (`git status --porcelain` empty, before and after the full test run).
**Mode**: Full artifact set present and read — proposal.md (including its appended citation-key ruling), six spec deltas, design.md, tasks.md, plus Engram mirrors (`sdd/the-agreement-nothing-computes/{spec,tasks,tasks-amended-r1-r2-resolved,apply-progress}`). Full spec-driven verification performed: completeness, correctness, design coherence, and independent re-derivation of every count the routing brief flagged as previously wrong.

### Re-derived counts (do not inherit)

- **Requirements: 19/19** — `rg -c '^#### Requirement:|^### Requirement:'` per spec: per-document-vocabulary 2, document-binding 1, cli-seal 4, cross-document-agreement 6, block-locator 3, skill 3 = 19.
- **Scenarios: 46/46** — `rg -c '^#### Scenario:'` per spec: cross-document-agreement 13, block-locator 7, document-binding 6, per-document-vocabulary 7, cli-seal 7, skill 6 = 46. Confirms the operator's own "46, re-derive it" instruction and tasks.md's own re-derivation; the routing brief's inherited "52"/"44" are both stale.
- **tasks.md checkbox count: 99/99 checked, not 100/100.** Running tasks.md's own cited derivation command verbatim (`rg -o '^\s*- \[[ x]\] [0-9]+\.[0-9]+[a-z]?' tasks.md | wc -l`) gives **99**, and a raw bracket count (`rg -c '\[x\]'` / `rg -c '\[ \]'`) gives **99 checked / 0 unchecked**. tasks.md's own header (line 8) still asserts "Task count: 100" — that count is now stale by exactly one, because task `1.12/1.13` was written as a single combined checkbox line (the documented Deviation) rather than the two the header's re-derivation assumed. All 99 that exist are checked; none are pending. This is a genuine, independently-found staleness in tasks.md's own bookkeeping that survived Phase 6's own sweep (which caught and corrected two other stale claims, 6.4 and 6.10, but not this one). **WARNING, not CRITICAL** — no task is incomplete; the total is miscounted by one in the artifact's own header.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total (measured, not the header's stale 100) | 99 |
| Tasks complete | 99 |
| Tasks incomplete | 0 |

### Build & Tests Execution (re-run this session, not inherited)

**Build** (`npm test`): ✅ Passed — **596/596**, 0 fail. Confirms the design's stale "595/595" prediction; D2's own negative-control test (2.11) is what grew it, and it has been re-measured identically at D2, D3, D4, D5, apply's Phase 6 sweep, and now independently in this verify session (five independent measurements, one count).

**Tests** (full Python suite, single sequential run — not run concurrently with anything else, per the session's own concurrency warning): ✅ **Ran 3059 tests — OK (skipped=6)**, 0 failures/errors, exit 0. `git status --porcelain` clean after the run (no leftover `implementations/_materialize_*` scratch), `tests/seal/` still byte-identical after the run.

**Coverage**: not available (no coverage tool configured in this project) — informational, not blocking.

### THE FIVE BARS — run directly, not inherited

| Bar | Result |
|---|---|
| `git diff --exit-code tests/seal/` | **exit 0** — both before and after this session's full test run |
| `tests/experiments_seal/` digest movement, whole change | **Exactly 4 movers, matching the brief, no fifth.** Verified by diffing each of the 6 commits that ever touched `tests/experiments_seal/digests.json` against its own parent: `9657a49`(D1)/`9b01534`(D2)/`4955803`(D3)/`993d9f7`(D4) — zero pre-existing movers, only new cases added; `b7240d4`(D5) moved `handoff-e1` alone (a real shape change, `local_reach` replacing the string comparison); `a918526`(D5) moved `verify-a-declared`/`verify-b-declared`/`verify-b-undeclared` together (a real pre-existing bug fix — `both-documents-citation` was wrongly read `local` under `cmd_verify`'s unthreaded `finding_impact` call; the commit message itself documents the bug and the fix). Final corpus: **30 cases, 31 keys** (30 digests + `__corpus_fingerprint__`) |
| `npm test` | **596/596**, exit 0 (design's stale 595 corrected, independently re-confirmed) |
| Full Python suite | **`Ran 3059 tests`, `OK (skipped=6)`**, exit 0. `skipped=6` — unmoved; `rg -n "skipTest"` shows no new skip anywhere in this change's diff |
| `reachable_refusal_codes()` | **116**, confirmed directly (`tests/test_proposal_implementation.py:28727`, `self.assertEqual(len(reachable_refusal_codes()), 116)`), and via the full-suite run's own `GatingRefusalRosterTests` pass |

### The operator's own bar — verified with commands, existence confirmed at both endpoints

A first pass at this check used the wrong (repo-root) paths and produced a **vacuous** 0-exit for `proposal-deliberation/`, `_core/deliberation/`, and `reference-experimental.ts` — exactly the failure mode the routing brief warned about. Corrected to the real paths and re-verified:

| Path | Files at `ba5cde7` (pre-Slice-D) | Files at HEAD | `git diff --exit-code` |
|---|---|---|---|
| `.claude/skills/proposal-deliberation/` | 6 | 6 | exit 0 |
| `.claude/skills/_core/deliberation/` | 56 | 56 | exit 0 |
| `.claude/skills/experimental-deliberation/reference-experimental.ts` | 1 | 1 | exit 0 |
| `tests/seal/` | 7 | 7 | exit 0 |

All four exist with real, non-zero file counts at both endpoints and are byte-unchanged across the whole ten-phase change — a real proof, not a vacuous pass.

`.claude/skills/proposal-implementation/`: `git diff --stat ba5cde7..HEAD` → **exactly 3 files**: `impl_profile.py` (+22/−0, the two sanctioned declarations — `block_locator` today's exact LaTeX bytes, `cross_citation: None` — read directly and confirmed each is exactly what it claims: today's hardcoded values written down, not new behavior), `SKILL.md` (+14/−9, the `GATING_COMMANDS` count sentence 114→116, ten commands not nine, landed inside `a545e7c`'s feature commit), `references/usage.md` (+6/−1, the same count correction plus a clarifying paragraph, commit `362df11`). No fourth file. `.claude/skills/experimental-deliberation/`: `git diff --stat` → **exactly 1 file**, `SKILL.md`, +14/−6 — confirmed prose-only by inspection (the diff replaces the "Known limit" section with "Resolved", no code file in that skill directory was touched).

### M7 — independently re-verified, not accepted on the report's word

Read the actual source, not just the SKILL.md prose:
- `publishSuccessor` (`.claude/skills/_core/deliberation/engine/proposal-workspace-adapter.ts:65`) computes `targetFilename = nextSuccessorTarget(...)`, then `parseManagedRevision(targetFilename)?.revision`.
- `parseManagedRevision` (`artifact-naming.ts:88`) matches `LAX_RE`, built from `REVISION_PREFIX = escapeRegExp(DOMAIN.artifact.revisionPattern)` (`artifact-naming.ts:36`) — **profile-derived**, no hardcoded `-r(\d+)\.md$` anywhere in the file.
- `experimental-deliberation/profile.ts:78` declares `revisionPattern: "v"`.
- Ran `node --test tests/experimental-deliberation-publish.test.mjs` directly: **5/5 pass**, including `"the accepted successor publishes as experiments-<lineage>-v02.md at revision v02"` and `"the accept turn derives the successor label from the profile, so the adapter never refuses INVALID_TARGET_REVISION"`.

**Verdict: the claim holds, independently confirmed at the code level, not merely by re-reading SKILL.md's prose.** The 2026-09-08 "Known limit" diagnosis genuinely does not describe this code — every matcher in the chain derives from the profile's own `revisionPattern`, not from a hardcoded regex.

### Boundary held — the engine refuses and names, never proposes, never infers direction

Read `cmd_agree` directly (`implementation_engine.py:8485-8536`). Its success payload is exactly `{"command", "target", "revision", "status", "crossed", "declared"}`; its two refusal messages (`AGREEMENT_CROSSING_UNDECLARED`, `AGREEMENT_DOCUMENTS_DISAGREE`) name `absent`/`untested`/`unacknowledged` sets and nothing else — no "should," no "is correct," no suggested direction. `tests/test_experiments_seal.py`'s `AgreeSuggestionKeyZ11MutationTests` confirms the anchor text matches the shipped source exactly once (`assertEqual(real_source.count(anchor), 1)`) and that a real subprocess run over a scratch copy adding a `suggestion` key is what the payload key-set lock is built to catch. **One caveat, honestly recorded by apply itself (task 6.4) and confirmed here**: of the two "no verdict word" assertions the proposal's Success Criteria demand be "each proven by mutation," only 5.11 (`AgreeSuggestionKeyZ11MutationTests`) is a literal mutation-reversion proof; 3.11 (`test_the_refusal_names_the_discrepancy_without_judging_it`) is a direct string-absence assertion against the shipped payload, passing "by construction" rather than by reverting a mutation. The **property** holds (confirmed by direct source read — no verdict/resolution/repair-direction language exists in `cmd_agree` or its refusal sites), but the proposal's literal "each proven by mutation" criterion is not literally met for 3.11. **WARNING**, not CRITICAL: the boundary is real and independently confirmed; only the proof *shape* for one of two assertions falls short of what the frozen proposal specified.

### Spec Compliance Matrix (19 requirements / 46 scenarios)

| Spec | Requirements | Scenarios | Status |
|---|---|---|---|
| `implementation-cross-document-agreement` (NEW) | 6 | 13 | All covered — `AgreementCheckTests`, `AgreementDisagreeZ7MutationTests`, `AcknowledgmentTests`, `AcknowledgeZ8MutationTests` all re-run green this session |
| `implementation-block-locator` (NEW) | 3 | 7 | All covered — `LockDDeclaredLocatorTests`, Z1-Z6 mutation tests, `RemedyCompatibilityPerDocumentTests` (4/4 re-run green) |
| `implementation-document-binding` (MODIFIED) | 1 | 6 | Covered — `cmd_handoff`'s `local_reach` at all four sites, `COMPOSE_AMBIGUOUS_DOCUMENT` firing confirmed live in `test_implementation_pair.py:2141` |
| `implementation-per-document-vocabulary` (MODIFIED) | 2 | 7 | Covered — `cross_citation` and `block_locator` per-document leaves, resolver tier tests |
| `implementation-cli-seal` (MODIFIED) | 4 | 7 | Covered — `compose`/`admit` confirmed sealed, `unsealed.json` confirmed to hold exactly 2 entries (`materialize`, `propose`) |
| `experimental-implementation-skill` (MODIFIED) | 3 | 6 | Covered — Flow B and the tutor bullet confirmed authored in `SKILL.md`, "not available yet" section confirmed to no longer list `compose`/`admit` |

**Compliance summary**: 46/46 scenarios have a covering test that passed at runtime this session (full suite green, plus the four spot-checked mjs/py files run individually).

### Correctness (Static + Dynamic Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| `[claims:N]` never joins `cites()` (M6) | ✅ Confirmed | `node --test tests/experimental-deliberation-references.test.mjs` → 8/8, including the negative-control assertion at line 176 |
| `reference-experimental.ts` byte-unchanged | ✅ Confirmed | `git diff --exit-code` exit 0 |
| Fail-closed-once (no per-claim refusal) | ✅ Confirmed | `AgreementCheckTests` re-run green; `cmd_agree` raises `AGREEMENT_CROSSING_UNDECLARED` once, computing neither `absent` nor `untested` first |
| Per-id acknowledgment | ✅ Confirmed | `AcknowledgmentTests`/`AcknowledgeZ8MutationTests` re-run green (4/4) |
| `L1_EXPECTED_COUNT` stays 96 | ✅ Confirmed | full suite includes `CampaignProposalExclusionTests`, green; source shows `L1_EXPECTED_COUNT = 97 - 1` untouched |
| `tests/pair/digests.json` unmoved | ✅ Confirmed | `git diff --exit-code ba5cde7..HEAD -- tests/pair/digests.json` exit 0 |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 block_locator as required triple, never a callable | ✅ Yes | `impl_profile.py` diff confirms triple shape |
| D9 conditional `agree` registration | ✅ Yes | `COMMANDS` spread confirmed at `implementation_engine.py:8485` area; `agree` reachable in roster unconditionally per D9's own design |
| D10 `local_reach` single accessor | ✅ Yes | `local_reach` at `implementation_engine.py:8021`, confirmed sole accessor |
| Refusal pin progression 114→115→117→118 | ❌ **Design prediction wrong, three times** | Measured (independently, via the roster test and full-suite `GatingRefusalRosterTests`): actual progression is **114→116 only**, at D3, unmoved through D4/D5. `COMPOSE_AMBIGUOUS_DOCUMENT` and `HANDOFF_DOCUMENT_UNREADABLE` are raised inside `cmd_compose`/`cmd_handoff`, neither a `GATING_COMMANDS` root, so `reachable_refusal_codes()` structurally cannot see them — confirmed by the roster's own reverse lock (`test_the_roster_classifies_nothing_a_gating_command_cannot_raise`). This is honestly recorded at every phase gate (1.31, 3.15, 5.15) and at apply's own Phase 6 (6.10, which also corrected its own inherited repetition of the wrong numbers) — not laundered. **WARNING**: design.md's own checklist item is objectively unmet as literally worded, but the actual measured behavior is architecturally sound and was never silently asserted as met. |
| M3: D1 moves zero of 24 pre-existing experiments-seal digests | ✅ Confirmed | Verified via commit-by-commit diff of `9657a49` (D1) — zero pre-existing movers |

### tasks.md's own annotated deviations — checked against source, not accepted on the report's word

1. **D1 strict_tdd deviation** — independently confirmed via `git log --reverse ba5cde7..ddc3c67`. Commit `bc85ce9` ("locator indirection at all seven sites, per-document remedy fields") is a pure GREEN commit touching only `implementation_engine.py`; no preceding dedicated RED test commit for tasks 1.10 (six-site RED) or 1.14 (seventh-site RED) exists in D1's own 12-commit range — the closest prior test commit, `60acaf2`, covers a different concern (the `block_locator` tier's own shape validation). This is a real, if minor, TDD-discipline deviation, and it is disclosed rather than hidden (tasks.md line 245's own "Deviation, recorded rather than silent" annotation). D2 through D5 were spot-checked and show the RED-before-GREEN pattern intact (e.g. `2f70434` test → `6c0796d`/`3212aa2` feat for D2).
2. **Tasks 1.12/1.13 substitution** — confirmed at tasks.md:245; the substitution (Z2/Z3 real-subprocess corpus-wide mutation proofs in place of a dedicated single-site-revert unit test) is a stronger, differently-shaped proof, honestly labeled as a deviation rather than silently equated to the original task.
3. **Task 1.15's own false claim** — independently confirmed. `rg -n "COMPOSE_AMBIGUOUS_DOCUMENT" -g '*.py' tests/` shows the only real assertion exercising this refusal is at `tests/test_implementation_pair.py:2141` (`assertEqual(payload["code"], "COMPOSE_AMBIGUOUS_DOCUMENT")`), added in D5 — no assertion existed at the time 1.15 claimed to add one. Correctly self-corrected at tasks.md:1220-1227 (task 5.3's own annotation).
4. **The refusal pin never moved past 116** — see Coherence table above.
5. **Phase 6 corrected two of its own task-text claims** — 6.4 (the uniform "each proven by mutation" framing, corrected for 3.11) and 6.10 (the stale "115, 117, 118" progression) — both confirmed present and accurately self-corrected in tasks.md.

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. tasks.md's own header (line 8) states "Task count: 100"; the actual, re-derivable count is **99** (99 checked, 0 unchecked). Stale by one, caused by the `1.12/1.13` combined checkbox line. No task is incomplete — this is a documentation-count staleness that survived Phase 6's own sweep.
2. Proposal.md's own frozen Success Criteria include two items that are not literally true as worded, though both are architecturally sound and honestly disclosed throughout apply's history rather than silently violated: (a) "No file under `proposal-implementation/`... is modified" — 3 files there were touched, ruled and disclosed as forced by the shared `GATING_COMMANDS`/refusal-count doctrine constant; (b) "Every new refusal code appears in `reachable_refusal_codes`'s roster" — only 2 of 4 new `Refused` codes do; `COMPOSE_AMBIGUOUS_DOCUMENT` and `HANDOFF_DOCUMENT_UNREADABLE` are structurally unreachable from `GATING_COMMANDS` roots, confirmed by the roster's own reverse lock test. Since proposal.md is a frozen planning artifact never edited post-ratification, its checkboxes remain `[ ]` in the file; the substance was measured and ruled at design time (design.md D9, M11), not silently skipped.
3. D1's Strict TDD deviation (RED states verified in test files added later, but not preserved as separate commits ahead of the GREEN commit for tasks 1.10/1.14/1.16) — independently confirmed via git history. Recorded honestly by the change itself; does not affect the shipped behavior, since every claimed RED assertion is present and passing in the final suite.
4. One of the boundary's two "no-verdict" proofs (task 3.11) is a construction-time assertion, not a literal mutation-reversion proof, against the proposal's own "each proven by mutation" Success Criterion. The underlying property is independently confirmed true by direct source inspection this session.

**SUGGESTION**:
1. Consider re-deriving and correcting tasks.md's own header count (99, not 100) and design.md's refusal-pin prediction table before archive, purely for future-reader accuracy — neither blocks this change.
2. Consider authoring a dedicated mutation test for 3.11's boundary assertion (revert a hypothetical "verdict" addition to `cmd_agree`'s refusal `detail` string and confirm 3.11 catches it) to fully close the gap Phase 6 itself flagged, in a follow-up rather than this change.

### Final Verdict

**PASS WITH WARNINGS.** Zero CRITICAL findings. Four WARNING-level findings, all documentation/proof-shape gaps with no functional impact — every one was independently re-derived and confirmed against source and git history in this session, not accepted from the apply report's word. All five bars pass exactly as measured: `git diff --exit-code tests/seal/` → 0; `npm test` → 596/596; full Python suite → `Ran 3059 tests, OK (skipped=6)`; `reachable_refusal_codes()` → 116; the sibling-skill boundary (`proposal-deliberation/`, `_core/deliberation/`, `reference-experimental.ts`, `tests/seal/`) confirmed byte-unchanged with real files existing at both endpoints, not a vacuous path check. M7's reversal of the 2026-09-08 "Known limit" diagnosis is independently confirmed true at the code level. The engine's refuse-and-name boundary is confirmed held by direct source inspection.

Recommended next phase: **sdd-archive**.
