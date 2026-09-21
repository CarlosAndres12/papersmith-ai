```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:e2ee6459c9211af741ec53e93550f70aef0a679774467515e43c6211c0a87280
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 12/12
scenarios: 41/41
test_command: .venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions
test_exit_code: 0
test_output_hash: sha256:a7763aa1255c9a4289932ce5501b2eca3728f13636d8ada5af35f5f8873b253b
build_command: npx tsc -p tsconfig.json
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: the-skill-writes-the-declaration-it-demands
**Branch**: s1-el-estado-de-la-raiz-se-ve (HEAD `bf3a109`, tree clean, merge-base with `main` is `main` itself — this branch's diff IS the whole change)
**Mode**: Standard (red-first tasks, executed mutation proofs; not orchestrator-declared Strict TDD)

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 79 |
| Tasks complete | 79 |
| Tasks incomplete | 0 |

All five units (Phase 0 gate, S1–S5) are committed: `0cf4cf6` (S1), `dc6f4cd` (S2), `a673e78` (S3), `15c950f` (S4), `bf3a109` (S5).

### Build & Tests Execution

**Build** (typecheck, `npx tsc -p tsconfig.json`): PASSED, exit 0, empty output — I ran this myself.

**Tests** (all commands below I ran myself in this verification session, not copied from any artifact):

- `npm test`: **640/640**, exit 0 — matches the applier's own reported number.
- `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions`: **855/855**, exit 0 (this is the envelope's own recorded `test_command`).
- Full Python suite, run in the SAME 5-chunk split `tasks.md` 5.12 records (chunking is load-bearing here — a documented cross-module race, not a convenience):
  1. `tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation tests.test_paper_contract tests.test_paper_citation tests.test_paper_evidence tests.test_paper_figure tests.test_paper_lifecycle` — **1194 OK**
  2. `tests.test_proposal_implementation tests.test_experimental_implementation tests.test_experimental_implementation_mutation tests.test_experiments_seal` — **1745 run, exactly 1 known failure** (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`)
  3. Fourteen remaining forge/implementation/agents modules except `test_remote_execution` — **846 OK, 3 skipped**
  4. `tests.test_remote_execution` alone — **700 OK**
  5. `PYTHONPATH=tests .venv/bin/python -m unittest tests.test_orphan_sweep` — **7 OK**
  - **Total: 4492 tests, exactly 1 known pre-existing failure, 3 skipped** — byte-for-byte matches `tasks.md` 5.12/5.13's own recorded numbers, independently reproduced by me, not trusted from the artifact.
  - No orphaned `implementations/_smokebox_*`/`_materialize_*` directory was left after this run (`find implementations -maxdepth 1 -iname "_smokebox_*" -o -iname "_materialize_*"` → empty).
- I independently re-ran `tests.test_remote_execution.BackendResolutionTests.test_dropping_a_module_into_adapters_becomes_reachable_by_backend_name` standalone: **passes** (part of the 700/700 chunk-4 run above), confirming the applier's disclosure that this is a cross-module ordering artifact in `remote-execution`, not a regression — this change's diff touches zero `remote-execution`/`adapter.py` bytes (`git diff main --stat` confirms).
- `ForgeVocabularyDerivedGuardTests` (21 tests) re-run by me standalone: exactly the one disclosed failure, naming only `experimental-deliberation`/`proposal-deliberation`/`proposal-implementation` over `data-paper`/`research-concept` — `paper-writing` is not named. A direct `rg -n -i -F` sweep of both words across `.claude/skills/paper-writing/` and its own two suites found exactly one hit, a pre-existing negative assertion (`tests/test_paper_decisions.py:3606`, `assertNotEqual(..., "data-paper")`), confirmed present since commit `15fe183` (well before this change's branch point) via `git log -S`.
- `NoSubprocessScanTests` (4 tests): green. `import subprocess` appears exactly once in `paper-writing/scripts/` (`paper_latex.py`), the pre-existing, test-tolerated exception; unrelated to this change.

**Coverage**: not instrumented in this repository; N/A.

### Engine Budget (owner's 1600-line ceiling)

`git diff main...s1-el-estado-de-la-raiz-se-ve --stat -- .claude/skills/paper-writing/scripts/` (I ran this myself; `main` IS the merge-base, so this is the change's entire diff):

```
paper_cli.py           187 (+/-)
paper_declarations.py  288 (+/-)
paper_graph.py            3 (+/-)
paper_guidance.py      190 (+/-)
paper_marker.py         135 (new)
5 files changed, 743 insertions(+), 60 deletions(-)
```

**743 + 60 = 803 engine lines** — matches the number given to me exactly, independently re-derived, not copied. Against the 1600 ceiling: **Low risk, 50% headroom.**

### Spec Compliance Matrix

**`source-declaration-authoring` spec — 8 requirements / 18 scenarios**

| Requirement | Scenarios | Test | Result |
|---|---|---|---|
| A Source Root's Revision Rule Is Recorded And Validated Against Disk By Using The Skill | 3/3 | `DeclareRevisionsTests` (`test_a_matching_declaration_is_recorded`, `test_a_declared_width_matching_nothing_refuses_at_write_time`, `test_a_non_declarable_root_refuses_by_name`) | ✅ COMPLIANT — I ran `declare_revisions` myself against an invented fixture (matching write, then a wrong-prefix refusal naming the prefix/digits/files seen) |
| A Guidance Folder's Class Is Recorded And Validated Against Disk By Using The Skill | 3/3 | `DeclareClassTests` (`test_a_folder_is_classified_and_recorded`, `test_a_folder_absent_under_guidance_refuses_naming_every_folder_present`, `test_classing_a_second_evidence_folder_refuses_ambiguous_before_the_write`) | ✅ COMPLIANT |
| Which Roots And Folders Are Declarable Is Derived, Never Listed | 1/1 | `test_a_sixth_prose_root_widens_the_report_with_zero_engine_edit` (source), `test_mutation_the_declarable_membership_check_is_reachable` | ✅ COMPLIANT |
| A Declaration Is Sealed Against An Unaware Edit, At Exactly Its Real Strength | 2/2 | `SealStrengthFourSurfaceTests` (both tests) | ✅ COMPLIANT — I ran the mutation myself (dropped "not tamper-proofing" from `SEAL_STRENGTH`, harness confirms MUTANT_IMPORTED_OK + nonzero exit) |
| Re-Recording Always Succeeds; There Is No Stuck State | 2/2 | `DeclareRevisionsTests`/`DeclareClassTests` (`test_re_recording_always_succeeds_over_an_existing_sealed_marker`, `test_re_recording_over_a_hand_edited_marker_clears_the_defect`, both mirrored for each marker kind) | ✅ COMPLIANT |
| Absence Is A Reported State; A Broken Seal Refuses Where The Marker Is Read | 2/2 | `PlanSourceRootsTests.test_a_prose_root_with_a_valid_unsealed_marker_reports_declared_unsealed`; `SourceSectionBindingWriteGateTests.test_write_refuses_source_declaration_hand_edited` | ✅ COMPLIANT — I ran the mutation myself (`read_revisions_marker`'s seal comparison → `True`) driven through `cmd_write`; the assertion errors (`Refused` never raised, execution instead falls through to a later, unrelated `FileNotFoundError`), proving the guard is load-bearing on that path, not merely present |
| The Position Report Names Every Declarable Root's And Every Guidance Folder's Declaration State | 4/4 | `PlanSourceRootsTests` (undeclared/n-a/sixth-root), `PlanTests.test_guidance_declaration_widens_to_declared_sealed_one_vocabulary_with_sourceroots` | ⚠️ 3/4 COMPLIANT, 1/4 PARTIAL — see Issues Found: "A malformed marker still refuses through the position verb" has no test driving it through `compute_plan`/`cmd_plan` for the source-root case. I verified the property manually (invented fixture, malformed JSON under a marked root, `compute_plan` raises `MALFORMED_SOURCE_MARKER`) and it holds, but no automated regression test names this exact path |
| Rollback Writes The Pre-Change Grammar, Never An Editor | 1/1 | `test_unsealed_writes_no_seal_key_shape_identical_to_pre_seal_grammar` (both marker kinds) | ✅ COMPLIANT |

**`source-section-binding` spec delta — 2 requirements / 14 scenarios**

| Requirement | Scenarios | Test | Result |
|---|---|---|---|
| A Document-Rooted Source With No Marker Refuses | 4/4 | `SourceRevisionsUndeclaredByteIdentityTests`, `SourceRevisionsUndeclaredMutationProofTests`, `test_deleting_an_already_declared_marker_still_refuses_undeclared` | ✅ COMPLIANT — I ran the byte-identity test AND its mutation myself (inlining a literal at the `bind` raise site reddens the identity assertion) |
| The Marker Grammar Is Validated, And Disjoint From `guidance/`'s | 10/10 | `SourceRevisionsMarkerGrammarTests` (19 tests, run by me — all green) | ✅ COMPLIANT |

**`guidance-registry` spec delta — 2 requirements / 9 scenarios**

| Requirement | Scenarios | Test | Result |
|---|---|---|---|
| Per-Folder Marker File | 6/6 | `ValidateSourceMdGuardTests.test_a_quote_from_a_hand_edited_sealed_evidence_source_refuses`, `GuidanceRegistryTests` seal tests | ✅ COMPLIANT — I ran the `_classify` seal-comparison mutation myself, driven through `cmd_validate` (a gating verb): the test fails with `AssertionError: Refused not raised`, proving the guard is reachable through `validate --source-md`, never only through `plan` |
| An Unmarked Folder Is Reported Unclassified, Never Guessed | 3/3 | `GuidanceRegistryTests`/`GuidanceRegistryMutationTests` (pre-existing, unaffected — confirmed: `unclassified` is unaffected by sealing, `test_an_unsealed_but_valid_marker_still_classifies_not_unclassified`-equivalent coverage present) | ✅ COMPLIANT |

**Compliance summary**: 40/41 scenarios COMPLIANT with a directly-named, executed covering test; 1/41 scenario PARTIAL (property manually verified true, no dedicated automated test).

### Correctness (Static + Runtime Evidence)

| Claim | Status | Notes |
|---|---|---|
| SHOW is proven by running `plan`, not by asserting a field | ✅ Confirmed | I ran `plan` myself against this repository's own real markers: `sourceRoots` and `guidance` both appear, both use the same 4-value vocabulary (`declared-unsealed` for all three real, pre-existing `guidance/` markers and `proposals/`) |
| One vocabulary across both halves (S5 task 5.15) | ✅ Confirmed | `paper_guidance.declaration_state`/`paper_declarations.declaration_state` both return `undeclared`\|`declared-unsealed`\|`declared-sealed`\|`n/a`; `compute_plan` calls both; verified live and via `GuidanceRegistryMutationTests.test_mutation_declaration_state_sealed_branch_is_reachable` |
| Seal stated at exactly its real strength, everywhere | ✅ Confirmed | Byte-identical in `paper_marker.py` docstring, both `*_HAND_EDITED` refusal details, `SKILL.md` (`rg` confirms exact string in all three files); mutation test passes |
| Seal verified inside the reader, never only in `plan` | ✅ Confirmed by mutation, run by me | Both `SOURCE_DECLARATION_HAND_EDITED` and `GUIDANCE_DECLARATION_HAND_EDITED` mutations were driven through `cmd_write`/`cmd_validate` respectively — both reddened as required |
| Migration: existing unsealed markers report, never refuse | ✅ Confirmed live | Ran `plan` on this actual checkout: `data-paper` (evidence), `paper-guide`/`reference-papers` (style-reference), `proposals` — all report `declared-unsealed`, zero refusals |
| Write-time validation refuses at the moment of writing | ✅ Confirmed by me, invented fixture only | `declare_revisions` against a scratch fixture: matching write succeeds; wrong prefix/digits refuses `SOURCE_DECLARATION_UNMATCHED` naming prefix, digits, and both files seen; never touched the repository's real `proposals/`/`guidance/`/`paper/` |
| Forge carries no paper of its own | ✅ Confirmed | `ForgeVocabularyDerivedGuardTests` re-run by me: the one failure names only `experimental-deliberation`/`proposal-deliberation`/`proposal-implementation`, never `paper-writing`. Context (out of scope, not this change's defect): 48 disclosed cross-skill hits live in those three sibling skills |
| Roster measured, never forecast | ✅ Confirmed | I executed `reachable_paper_refusal_codes()` myself: **159**. 154 (pre) + 5 new (`SOURCE_DECLARATION_UNMATCHED`, `SOURCE_DECLARATION_HAND_EDITED`, `GUIDANCE_DECLARATION_HAND_EDITED`, `SOURCE_ROOT_UNDECLARABLE`, `GUIDANCE_FOLDER_ABSENT`) = 159, consistent, matches the suite's own `assertEqual(len(...), 159)` |
| No `subprocess` import joins `scripts/` | ✅ Confirmed | `NoSubprocessScanTests` green; the sole pre-existing exception (`paper_latex.py`) is unrelated and untouched |
| Nothing deletes files; `sections/` untouched | ✅ Confirmed | `git diff main -- sections/` empty; `git diff --summary main` has zero `delete mode` lines |
| `paper_region.py` genuinely untouched | ✅ Confirmed | `git diff main -- .../paper_region.py` is empty |

### Design Coherence

| Decision | Followed? | Notes |
|---|---|---|
| A — marker stays beside its root; seal is a new key inside it (the fork, ruled) | ✅ Yes | `paper_marker.write` writes into the same `.paper-writing.json`; no fifth `declarations`-region record kind exists |
| B — one shared seal module, `paper_marker.py`, never raises a consumer's refusal | ✅ Yes | `seal_shape_error` returns `str \| None`, never raises; both `*_HAND_EDITED` codes are raised by the two consumers themselves |
| C — seal verified in the reader, never in the report alone | ✅ Yes, proven by mutation | See Correctness table above |
| D — one root `mark`, two sub-modes | ✅ Yes | `cmd_mark` dispatches to `cmd_mark_revisions`/`cmd_mark_class` by `args.mark_command` |
| E — re-recording always available, no `--adopt`/`--reopen` | ✅ Yes | Neither verb reads the previous marker; both tests families confirm free re-recording, including over a hand-edited marker |
| F — write-time validation order, per kind | ✅ Yes | `declare_revisions`/`declare_class` match the documented order (membership → shape → disk match/ambiguity → round-trip → write) |
| G — `SEAL_STRENGTH` constant, tested in four places | ✅ Yes | Confirmed byte-identical in all four real surfaces (`references/usage.md` correctly absent — `paper-writing` has never had one, confirmed via `git ls-files`) |
| H — one detail builder, two raise sites | ✅ Yes, proven by mutation | `source_revisions_undeclared_detail` is the sole builder; both `paper_declarations._resolve_bind_document` and `paper_graph.resolve_section_index` call it |
| I — SHOW is a correction, scoped to `plan` | ✅ Yes | `phases`/`contract` untouched by any phase (`git diff main --stat` confirms zero changes to either verb's implementation) |
| J — declarability derived, never listed | ✅ Yes, proven by mutation | `declarable_source_roots()`/`source_roots_report` iterate `FACT_SOURCE_ROOT` by `.kind`; no root name is a literal anywhere in the derivation |
| K — `--unsealed` is the rollback step, never a hand edit | ✅ Yes | Both `mark revisions --unsealed`/`mark class --unsealed` produce shape-identical pre-seal markers, tested and confirmed |

### Disclosures Confirmed

1. **S2's drafting-order disclosure** (`paper_marker.py` drafted before its own RED tests, while wiring into the two readers followed strict red-first). I could **not** independently re-verify the intra-session ordering claim: the Engram `apply-progress` artifact uses a single `topic_key` reused across all five units, so upserts overwrote S2's own disclosure text with S5's — only the final phase's content survives in Engram today. What IS independently verifiable holds: the wiring mutations (2.19/2.15-17, `SOURCE_DECLARATION_HAND_EDITED` through `cmd_write`) are present, load-bearing, and reddened correctly when I mutated them myself, consistent with red-first discipline for the wiring half of the claim.
2. **`test_remote_execution`'s combined-run flake**: confirmed independently — passes 700/700 standalone (chunk 4 above), and this change's diff touches zero `remote-execution` files.
3. **No `references/usage.md` for `paper-writing`**: confirmed via `git ls-files` — no such file exists and none is referenced by any test; `SealStrengthFourSurfaceTests` explicitly documents checking only the four real surfaces.

### Issues Found

**CRITICAL**: None.

**WARNING**:
- Spec scenario "A malformed marker still refuses through the position verb" (`source-declaration-authoring`) has no automated test driving it through `compute_plan`/`cmd_plan` for the source-root case (the guidance-side equivalent is likewise untested through `plan` specifically, though both properties hold — verified manually by me against invented fixtures). The behavior is correct by construction (`declaration_state` calls the reader with no exception-swallowing), but per this skill's own rule ("a spec scenario is compliant only when a covering test passed at runtime"), this scenario is not automatable-proof today.
- The Engram `apply-progress` topic_key is reused (upserted) across all five units of a single change, so only the LAST phase's disclosure text survives retrieval; earlier phases' own disclosures (e.g. S2's drafting-order note) become unverifiable once a later phase's `mem_save` overwrites them under the same key. This is a process/tooling gap in the artifact-store convention, not a defect in this change's code.

**SUGGESTION**:
- Add a dedicated test asserting `compute_plan` propagates `MALFORMED_SOURCE_MARKER`/`MALFORMED_GUIDANCE_MARKER` when a declarable root's/folder's marker is malformed, closing the one PARTIAL scenario above.
- Consider per-phase topic keys (e.g. `sdd/{change}/apply-progress/s2`) for multi-unit changes so later phases do not silently erase earlier phases' own disclosures from Engram.

### Verdict

**PASS WITH WARNINGS**
