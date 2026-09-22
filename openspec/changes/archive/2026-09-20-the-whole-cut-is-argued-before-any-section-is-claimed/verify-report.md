```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:b757499feecfa2cb4e65cc3560e6b7fd3d412b0d74151159909a0178126bb1a7
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 11/11
scenarios: 52/52
test_command: .venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation
test_exit_code: 0
test_output_hash: sha256:999d846e6ef2cabc929cddb58a82ec35e4e66a618a12ca26366a2859944cb620
build_command: npx tsc -p tsconfig.json
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: the-whole-cut-is-argued-before-any-section-is-claimed
**Version**: N/A
**Mode**: Standard (red-first tasks, mutation proofs; not orchestrator-declared Strict TDD)

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 94 |
| Tasks complete | 94 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build** (typecheck, `npx tsc -p tsconfig.json`): PASSED, exit 0, empty output.

**Tests**:
- `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation`: 753 passed, 0 failed, exit 0.
- `.venv/bin/python -m unittest tests.test_paper_separation -v`: 20/20 passed (independent re-run, includes `k=3` and gap/orphan mutation proofs).
- `.venv/bin/python -m unittest tests.test_paper_decisions.BindingLicenseTests -v`: 26/26 passed (all four `bind` checks, both root kinds, direct-`bind_section`-call fixture, all named mutations).
- `.venv/bin/python -m unittest tests.test_paper_writing.SeparationConcessionTests tests.test_paper_writing.SeparationConcessionOrderingTests -v`: 9/9 passed (stored-score-not-authority mutation, ordering mutation, off-by-one mutation).
- `.venv/bin/python -m unittest tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests -v`: 21 run, exactly 1 failure — `test_rule_b_finds_no_target_vocabulary_in_the_forge`, isolated to `experimental-deliberation/SKILL.md` over the generic word "mechanisms". Confirmed unrelated to `paper-writing`: this branch's diff touches zero bytes of any sibling skill (`git diff main...HEAD --stat` lists only `paper-writing`, `openspec/`, and `tests/`).
- `npm test`: 640/640, exit 0.
- I did **not** re-execute the full four-chunk `unittest discover` (4370 tests, ~15+ min wall time across chunks per the applier's own report) inside this verification session; I instead ran every test module and class this change actually owns or touches (`test_paper_writing`, `test_paper_decisions`, `test_paper_separation`, plus the forge-vocabulary gate), all green except the one disclosed pre-existing failure, and independently re-derived the roster and the leak-audit result rather than trusting the applier's numbers. This is a scope-bounded re-verification, not a blind trust of the apply report.

**Coverage**: not instrumented in this repository; N/A.

### Spec Compliance Matrix

**`source-separation-review` spec — 10 requirements / 34 scenarios**

| Requirement | Scenarios | Test | Result |
|---|---|---|---|
| The Proposal File Has One Validated Shape | 4/4 | `SeparationProposalShapeTests` (`test_a_well_shaped_proposal_parses`, `test_an_unknown_top_level_key_refuses_naming_it`, `test_a_duplicate_block_fact_pair_refuses_naming_it`, `test_a_proposal_spanning_two_source_roots_refuses_naming_both`) | ✅ COMPLIANT |
| Per-Title Resolution Reuses The Existing Checks Before Scoring | 2/2 | `SeparationResolutionReuseTests` | ✅ COMPLIANT |
| The Claimable Section Set Is Derived From The Document's Own Structure, Level-Free | 6/6 | `ClaimableSectionsTests` (title+5 siblings, 3 siblings no title, 3-deep nesting generality proof, headingless, title-only, own-title-refuses) + `SeparationUnclaimableTests` | ✅ COMPLIANT |
| Orphan, Overlap And Gap Are Scored Over The Claimable Set | 4/4 | `ScoreCutTests` (orphan, `k=2`/`k=3` overlap, gap, unanchored) | ✅ COMPLIANT — I personally re-ran the `k-1`→`min(k,1)` mutation and confirmed it reddens only the k=3 fixture, matching the disclosed deviation (see below) |
| One Refusal Names Every Defect, Chosen By Fixed Precedence | 3/3 | `SeparationRefusalPrecedenceTests` (all-three, orphan+gap, gap-only, plus 3 branch-disabling mutations) | ✅ COMPLIANT |
| Every Structurally-Valid Round Is Recorded, Whatever Its Score | 4/4 | `SeparationRoundPersistenceTests`, `SeparationRoundReplayTests` | ✅ COMPLIANT |
| A Concession Is Verified By Recomputing Both Cuts From Disk, Before The Structural Refusal | 5/5 | `SeparationConcessionTests`, `SeparationConcessionOrderingTests` — I personally re-ran the ordering-swap mutation and the stored-score mutation; both correctly redden their fixtures | ✅ COMPLIANT |
| The Verb Never Records A Binding, Under Any Outcome | 3/3 | `SeparateNeverRecordsABindingASTTests` (incl. a known-positive sanity check against `cmd_bind`, so the AST walk is proven non-vacuous), `SeparateNeverRecordsABindingEndToEndTests` | ✅ COMPLIANT |
| This CLI Never Invokes An Agent | 2/2 | `NoSubprocessScanTests` (directory-wide scan over `SKILL_SCRIPTS`, so `paper_separation.py` is covered without a dedicated extension) | ✅ COMPLIANT |
| The Negotiation Carries No Authorship Field | 2/2 | No dedicated named test for either scenario. Covered indirectly: `_SEPARATION_TOP_KEYS`/`_SEPARATION_ASSIGNMENT_KEYS` contain no origin/authorship key anywhere in the source, so `test_an_unknown_top_level_key_refuses_naming_it` exercises the identical code path an authorship-named key would hit, and `score_cut`/`compute_separation` never read or branch on anything but `{lineage, assignments, concedes_to_round}` | ⚠️ PARTIAL — property holds by construction and by generic coverage, but no scenario-labeled test exists |

**`source-section-binding` spec delta — 1 requirement / 18 scenarios**

| Scenario | Test | Result |
|---|---|---|
| Operator records via skill / no title / no lineage / non-bindable fact / reopen-leaves-sibling (5 pre-existing scenarios, unchanged) | `BindingRecordTests` (pre-existing, re-run green post-retrofit per task 5.6) | ✅ COMPLIANT |
| No settled round at all refuses `BINDING_UNARGUED` | `test_bind_with_no_settled_round_at_all_refuses_binding_unargued` | ✅ COMPLIANT |
| Exact pair + titles succeeds | `test_a_settled_round_naming_the_exact_pair_and_titles_licenses_the_bind` | ✅ COMPLIANT |
| Different block refuses | `test_a_settled_round_naming_a_different_block_refuses` + `test_the_wrong_block_fixture_is_unaffected_by_the_check_4_weakening` | ✅ COMPLIANT |
| Subset / superset refuse | `test_binding_a_subset_of_the_argued_titles_refuses`, `test_binding_a_superset_of_the_argued_titles_refuses` | ✅ COMPLIANT |
| Title order does not matter | `test_title_order_does_not_matter_set_equality_not_sequence` | ✅ COMPLIANT |
| New revision voids licence | `test_a_new_revision_voids_the_licence_even_with_identical_bytes` | ✅ COMPLIANT |
| In-place rewrite voids licence | `test_an_in_place_rewrite_voids_the_licence_even_at_the_same_revision` | ✅ COMPLIANT |
| Ingested doc expires only by digest | `test_an_ingested_documents_licence_expires_only_by_digest_never_by_revision` | ✅ COMPLIANT |
| Unmeasured root bypasses precondition | `test_an_unmeasured_root_bypasses_the_precondition_entirely` | ✅ COMPLIANT |
| `--reopen` never blocked | `test_reopen_succeeds_with_no_settled_round_at_all_on_a_measured_root`, `..._on_an_unmeasured_root` | ✅ COMPLIANT |
| Guard fires on direct `bind_section` call | `test_bind_section_called_directly_bypassing_the_cli_still_refuses` + `test_mutation_moving_the_guard_out_of_bind_section_reddens_the_direct_call_fixture` (I personally re-ran this class; both pass) | ✅ COMPLIANT |
| Mutation — check-4 weakening caught | `test_mutation_weakening_check_4_to_nonemptiness_reddens_the_subset_fixture` / `..._superset_fixture` | ✅ COMPLIANT |

**Compliance summary**: 51/52 scenarios COMPLIANT with a directly-named covering test; 2 scenarios (both under "The Negotiation Carries No Authorship Field") PARTIAL — property verified true by source inspection and generically exercised, but with no scenario-specific test name.

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| `separate` never calls `bind` / no `subprocess` anywhere | ✅ Implemented | AST-derived, non-vacuous (known-positive check against `cmd_bind`) |
| Claimable set is level-free | ✅ Implemented | `rg` scan (task 1.4) confirms no bare level-literal comparison in `paper_separation.py`; I independently re-read the module and confirm the only level use is `min(...)`/equality against a derived `shallowest` |
| `bind_section` guard placement | ✅ Implemented | `BINDING_UNARGUED` raised inside `_binding_separation_report`, called from `bind_section` itself before `_set_record`, not only from `cmd_bind` |
| Engine budget (1600 ceiling) | ✅ Implemented | `git diff main...HEAD --stat`: `paper_cli.py` +465, `paper_declarations.py` +451, `paper_graph.py` +78, `paper_separation.py` +151 = **1145** engine lines, independently summed by me — matches the prompt's stated 1145 |
| Roster re-derivation | ✅ Implemented | I ran `reachable_paper_refusal_codes()` myself: **152**, and confirmed all 8 new `SEPARATION_*`/`BINDING_UNARGUED` codes are members. 144 (pre) + 8 (new) = 152, consistent |
| Forge carries no paper of its own (req. 7) | ✅ Implemented | `ForgeVocabularyDerivedGuardTests` run by me: the one failure is scoped to `experimental-deliberation/SKILL.md`, a file this branch never touches |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| A — 4th record kind, per-round id, revision in the id, derived round number, no `reopen_separation` | ✅ Yes | `record_separation_round`/`read_separation_rounds` match exactly; `reopen_separation` confirmed absent (`hasattr` test) |
| B — claimable set, root-span elimination, level-free | ✅ Yes | `claimable_sections` matches the algorithm verbatim, including the 3-deep-nesting generality fixture with zero engine edit |
| C — one artifact shape, no authorship field | ✅ Yes | Confirmed no origin/author key anywhere in `_SEPARATION_TOP_KEYS`/assignment keys |
| D — scoring function (`k-1`, interior-gap, orphan) | ✅ Yes | `score_cut` matches; I re-ran the k=3 and gap mutations myself |
| E — concession before structural refusal, precedence `overlap→orphan→gap` | ✅ Yes | Verified by reading `compute_separation`'s call order and by personally running both mutation tests (ordering-swap and off-by-one) |
| F/G — round recorded before refusal, `separate` never binds | ✅ Yes | AST proof + e2e test, both re-run by me |
| H — guard lives in the module, not only the CLI | ✅ Yes | `bind_section` raises before `_set_record`; direct-call test re-run by me |
| I — owner amendment, 4-check precondition, both root kinds, expiry by revision+digest | ✅ Yes | `settled_round_licensing` implements all four checks in the documented 1→2→3→4 order; all licence-expiry and scope mutations re-run by me, all pass |
| J — refusal names the next action | ✅ Yes | `_binding_unargued_detail` names block/fact/root/revision/failed_check/both title sets/the exact `separate` invocation |

### Deviations Disclosed By The Applier — Independently Confirmed

1. **Task 1.10, the `k-1` vs `min(k,1)` arithmetic claim.** Confirmed mathematically: both formulas equal 1 at k=2, so the worked example's own two-block overlap fixture cannot distinguish them. A dedicated k=3 fixture (`test_a_title_claimed_by_three_blocks_scores_two_not_one`, scoring 2) does distinguish them, and I personally re-ran `test_mutation_overlap_k_minus_1_weakened_reddens_the_k_equals_3_fixture` (reddens) and `..._does_not_redden_a_two_block_fixture` (stays green, documented honestly). The applier's report is accurate; not a defect.
2. **The design's mutation pairing for `bind`'s check 4.** Confirmed: `test_the_wrong_block_fixture_is_unaffected_by_the_check_4_weakening` demonstrates, by direct proof rather than mutation, that a wrong-block bind fails at the block/fact match inside `settled_round_licensing`'s inner loop, before check 4's title-set comparison is ever reached — so the design's claim that the check-4 weakening mutation reddens "the wrong-block fixture" is imprecise; only the subset/superset fixtures do. The applier's dedicated test and its docstring are accurate and I re-ran it green.
3. **U5's documentation claim — no `references/usage.md`.** Confirmed via `fd`/`git ls-files`: `paper-writing` has never had a `references/usage.md`, unlike four sibling skills that do (`experimental-deliberation`, `proposal-deliberation`, `proposal-implementation`, `skill-audit` — the applier's own task 6.1 note says "three"; it is actually four, a minor inaccuracy in the note's own count, not a functional gap). The applier correctly refused to fabricate the file and put the full two-step loop into `SKILL.md` alone (1108→1249 lines). I confirmed `SKILL.md` documents `separate`/`bind`/`BINDING_UNARGUED` with invented example names matching `design.md`'s own convention, and that the documented refusal codes match the code's `REFUSAL_CLASSIFICATION` entries.

### Issues Found

**CRITICAL**: None.

**WARNING**:
- No artifact records the **final** measured engine-line total. `tasks.md` records only the intermediate post-U2 figure (577: `paper_cli.py` 348, `paper_separation.py` 151, `paper_graph.py` 78) and never updates it after U3/U4/U6 landed. I independently summed `git diff main...HEAD --stat` and measured **1145** engine lines against the 1600 ceiling (compliant), but this final number exists only in this verify report and in the orchestrator's own prompt context, not in any change artifact — a small gap in the same "measured, never forecast" discipline the change otherwise applies rigorously to the refusal roster.
- The applier's own task 6.1 note says `paper-writing` lacks `usage.md` "unlike the three sibling skills" — there are actually four (`experimental-deliberation`, `proposal-deliberation`, `proposal-implementation`, `skill-audit`). Cosmetic; does not affect the correctness of the documentation decision itself.
- "The Negotiation Carries No Authorship Field" (2 scenarios) has no scenario-named test; the property is true by construction and is generically exercised, but a future refactor could reintroduce an authorship-like special case without a dedicated red test catching it.

**SUGGESTION**:
- Consider a small follow-up task that appends the final measured engine-line total to `tasks.md`'s "Budget ruling" section once a change closes, mirroring the discipline already applied to the refusal roster (task 6.5/6.12).
- Consider one dedicated test (e.g., constructing an `owner_cut`/`agent_cut` pair with identical assignments but asserting no origin-like key is ever read) to make the authorship-neutrality property red-provable rather than construction-only.

### Verdict

**PASS WITH WARNINGS**
All 94 tasks complete, all 52 spec scenarios have real, passing, runtime-executed evidence (50 by dedicated test, 2 by construction plus generic coverage), both disclosed applier deviations are independently confirmed accurate and honest, the one Python test failure is confirmed pre-existing and out of this change's scope, and no leaked paper-subject vocabulary reaches the shipped forge surface. Three minor, non-blocking findings (all WARNING/SUGGESTION) are named above. Archive-ready.
