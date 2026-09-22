```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:bb9e40ace62f84744bf597e2d7c5364f0bb0a153334c2859e4376bc785d2b5bc
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 24/24
test_command: .venv/bin/python -m unittest discover -s tests -p "test_*.py"
test_exit_code: 0
test_output_hash: sha256:b573da013c3727236e4a3b45d847f6c03ee8003102c19060c804676198edd331
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:35be24e50a18f4b7635b1c779ff81de6d8e8333ff88674e477b2c6b6b015e55d
```

## Verification Report

**Change**: the-block-asserts-only-what-its-section-carries
**Version**: N/A (single-version capability spec)
**Mode**: Strict TDD (RED/GREEN evidence recorded for every task in apply-progress.md)
**Commit**: `046fe96` (5 chained commits ahead of `main`@`0b8492e`, branch `the-block-asserts-only-what-its-section-carries`)

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 47 |
| Tasks complete | 47 |
| Tasks incomplete | 0 |

All 47 tasks re-checked against the actual diff and running code, not read off
the checkbox alone: ordering gate (0.1), the four RED-first guard tasks
(0.2/0.5/0.7/0.9/1.1/1.6/1.7/1.9/1.10/1.11/1.13/1.14/2.8), the four mutation
proofs (3.1-3.4), the generality sweeps (0.10/1.15/3.6), the roster
re-measure (3.7), the zero-deletions/untouched-`paper_leak.py` check (3.8),
and both full suites (3.9) all independently reproduced below.

### Build & Tests Execution

**Build**: N/A — no compiled artifact; `npm test` below is this repository's
JS-side test runner, not a build step.

**Tests — JS suite**: ✅ 646 passed / 0 failed / 0 skipped
```text
$ npm test
ℹ tests 646
ℹ pass 646
ℹ fail 0
ℹ skipped 0
ℹ duration_ms 43627.26
[exit 0]
```

**Tests — Python suite (full discover, both runners named in tasks.md 3.9)**:
✅ 4559 passed / 0 failed / 3 skipped (pre-existing, unrelated)
```text
$ .venv/bin/python -m unittest discover -s tests -p "test_*.py"
Ran 4559 tests in 668.120s
OK (skipped=3)
[exit 0]
```
The one previously-disclosed failure this repository carries
(`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`)
did **not** reproduce — full green, matching apply's own claim.

**Grounding-specific test classes** (39 tests, run individually and inside
the full discover pass): `SubjectsForTests` (5),
`ArgumentModeBlockHasNoSubjectsTests` (1), `InterimSourceGroundingEnvelopeTests`
(2), `WriteBlockGroundingAccountKeywordTests` (2),
`ReconcileSupportBurdenOfProofTests` (1), `ReconcileSupportTests` (6),
`SourceGroundingReportTests` (4), `WriteBlockGroundingWiringTests` (3),
`GroundingScopeBoundaryTests` (3), `CmdWriteGroundingWiringTests` (3),
`GroundingMutationProofTests` (6) — all green.

**Coverage**: not measured by this repository's tooling (no coverage command
configured); not a project convention, so ➖ Not available.

### Spec Compliance Matrix — `transposition-grounding`, 9 requirements, 24 scenarios

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Subject Set Is An Intersection | A licensed fact with a bound section is a subject | `SubjectsForTests.test_a_licensed_fact_with_a_bound_section_is_a_subject` | ✅ COMPLIANT |
| Subject Set Is An Intersection | An evidence-bound sentence is never a subject | `SubjectsForTests.test_an_evidence_bound_sentence_is_never_a_subject` | ✅ COMPLIANT |
| Subject Set Is An Intersection | A structural sentence is never a subject | `SubjectsForTests.test_a_structural_sentence_is_never_a_subject` | ✅ COMPLIANT |
| Subject Set Is An Intersection | A fact-bound sentence whose fact carries no bound section is never a subject | `SubjectsForTests.test_a_fact_bound_sentence_whose_fact_has_no_bound_section_is_never_a_subject` | ✅ COMPLIANT |
| Subject Set Is An Intersection | An argument-mode block has no subjects | `ArgumentModeBlockHasNoSubjectsTests.test_argument_mode_never_calls_subjects_for` + `GroundingScopeBoundaryTests.test_an_argument_mode_block_never_reaches_reconciliation_through_write` | ✅ COMPLIANT |
| An Absent Account Refuses | No account, subjects exist | `ReconcileSupportTests.test_no_account_with_subjects_refuses_account_absent_never_verdict_missing` | ✅ COMPLIANT |
| An Absent Account Refuses | No account, no subjects | `ReconcileSupportTests.test_no_account_and_no_subjects_raises_nothing` | ✅ COMPLIANT |
| An Absent Account Refuses | Mutation — absent-account refusal reachable | `GroundingMutationProofTests.test_mutation_1_treating_an_absent_account_as_empty_fails_the_account_absent_guard` | ✅ COMPLIANT (re-run myself, red-under-mutation confirmed) |
| Account Reconciled, Both Directions | Account entry naming unsegmented sentence refuses | `ReconcileSupportTests.test_an_account_entry_naming_an_unsegmented_sentence_refuses` | ✅ COMPLIANT |
| Account Reconciled, Both Directions | Subject absent from account refuses | `ReconcileSupportTests.test_a_subject_with_no_account_entry_refuses_verdict_missing` | ✅ COMPLIANT |
| Account Reconciled, Both Directions | Mutation — each direction independently reachable | `GroundingMutationProofTests.test_mutation_2a_...` + `test_mutation_2b_...` | ✅ COMPLIANT (re-run myself, both directions confirmed independent) |
| Permissive Verdict Carries Burden Of Proof | Byte-present span passes | `ReconcileSupportTests.test_a_byte_present_span_in_its_own_section_passes` | ✅ COMPLIANT |
| Permissive Verdict Carries Burden Of Proof | Absent span downgrades | `ReconcileSupportBurdenOfProofTests.test_a_supported_verdict_with_an_empty_span_never_passes_as_supported` | ✅ COMPLIANT |
| Permissive Verdict Carries Burden Of Proof | Different fact's section downgrades | `ReconcileSupportTests.test_a_different_facts_section_also_downgrades` | ✅ COMPLIANT |
| Permissive Verdict Carries Burden Of Proof | Mutation — downgrade caught only by span reconciliation | `GroundingMutationProofTests.test_mutation_3_removing_the_byte_presence_re_read_fails_the_downgrade_guard` | ✅ COMPLIANT — **THE load-bearing property, re-run and independently reproduced by direct execution myself (see Issues, below the matrix)** |
| An Unsupported Claim Refuses | Unsupported claim refused with full identification | `ReconcileSupportTests.test_unsupported_refuses_naming_all_five_fields` | ✅ COMPLIANT |
| An Unsupported Claim Refuses | Mutation — unsupported refusal reachable | `GroundingMutationProofTests.test_mutation_4_disabling_the_unsupported_branch_fails_its_own_scenario` | ✅ COMPLIANT (re-run myself) |
| Undecidable Never Blocks Alone | All-undecidable-or-downgraded does not block | `SourceGroundingReportTests.test_an_all_undecidable_or_downgraded_account_does_not_block` | ✅ COMPLIANT |
| Undecidable Never Blocks Alone | Downgrade never counted as agent-returned undecidable | `SourceGroundingReportTests.test_downgraded_and_agent_returned_undecidable_never_merge` | ✅ COMPLIANT — re-run myself, both counts confirmed separate (1/1) |
| A Sibling Check, Never An Extension | Verbatim paste and unsupported claim are two distinct refusals | `WriteBlockGroundingWiringTests.test_a_draft_failing_both_checks_names_the_verbatim_refusal` + `test_unsupported_refuses_naming_all_five_fields` (independent reachability) + static: `paper_leak.py` byte-identical to `main` | ⚠️ PARTIAL — see SUGGESTION below; property proven by composition of tests, no single test literally names both codes firing from one draft in two separate runs |
| Guard Fires After Verbatim, Before Substitution | Unsupported claim refused by real write invocation | `WriteBlockGroundingWiringTests.test_an_unsupported_claim_refuses_through_a_real_write_call` | ✅ COMPLIANT — proves `main.tex` bytes unchanged |
| Guard Fires After Verbatim, Before Substitution | Draft failing both checks names verbatim refusal | `WriteBlockGroundingWiringTests.test_a_draft_failing_both_checks_names_the_verbatim_refusal` | ✅ COMPLIANT — confirmed by reading `paper_write.py:238-276`, verbatim check precedes and can raise before grounding block ever runs |
| A Block With No Decided Subject Reports Unmeasured | No subjects reports unmeasured/0 | `InterimSourceGroundingEnvelopeTests` (both tests) | ✅ COMPLIANT |
| A Block With No Decided Subject Reports Unmeasured | Subjects exist, none decided reports unmeasured/N | `SourceGroundingReportTests.test_subjects_exist_but_none_decided_reports_unmeasured_nonzero` | ✅ COMPLIANT |

**Compliance summary**: 24/24 scenarios covered by a passing test (23 fully
COMPLIANT, 1 PARTIAL — see SUGGESTION).

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Four refusal codes, all `WORK_STATE` | ✅ Implemented | `paper_cli.py:564-567`, matches design.md §1's table exactly |
| Import row for roster derivation | ✅ Implemented | `paper_cli.py:75-...`, landed in WU1's commit (disclosed deviation, confirmed — see below) |
| Every `Refused(...)` first arg a string literal | ✅ Implemented | `rg "raise Refused(exc.code"` returns zero matches across all three touched files |
| `paper_leak.py` untouched | ✅ Confirmed | `git diff main -- .../paper_leak.py` is byte-empty |
| Zero file deletions | ✅ Confirmed | `git diff main --diff-filter=D` is empty |
| Engine lines under `.claude/skills/` | ✅ Confirmed | 235 (paper_cli.py +33/-1, paper_grounding.py +172/-0, paper_write.py +30/-2) — well under the 1600 ceiling |
| Refusal roster count | ✅ Confirmed | `reachable_paper_refusal_codes()` pinned and asserted at 165 (`test_paper_writing.py:7975`) |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1 — inverted burden of proof | ✅ Yes | `supported` requires byte-present span; `unsupported` needs none |
| D2 — no ratio threshold, falsifier recorded | ✅ Yes | `downgraded`/`undecidable` counted separately; falsifier text present verbatim in `SKILL.md:1258-1262` and `tasks.md`'s closing section |
| D3 — subject set as byte-derived intersection | ✅ Yes | `subjects_for` is exactly the intersection design.md specifies, no literal decides membership |
| D4 — thread bindings, no re-segmentation | ✅ Yes | `paper_write.py:159` single-line fix, `_stage_evidence_audit` still has exactly one caller |
| D5 — sibling module, `paper_leak.py`/`check_source_section_verbatim` untouched | ✅ Yes | confirmed by diff |
| D6 — fires after verbatim, before substitute | ✅ Yes | confirmed by reading `paper_write.py:238-278` — verbatim raises before grounding block executes |
| D7 — absent account refuses, not a silent pass; CLI reuses `PAPER_OUTSIDE_REPOSITORY` | ✅ Yes | `CmdWriteGroundingWiringTests.test_a_grounding_path_outside_the_repository_refuses` green |
| D8 — report shape mirrors `source_fidelity_report`/`style_channel_report` | ✅ Yes | `source_grounding_report` matches the table in design.md exactly |
| D9 — agent file's shipped obligations, role discipline copied not referenced | ✅ Yes | `tests.test_agents` 16/16 green, including `test_every_agent_carries_the_shared_role_discipline` |
| Seam with sibling — ordering gate | ✅ Yes | re-verified myself: `RedactorInput` carries 5 fields, `assemble_packet` accepts `corpus=None, paper_dir=None` |

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. **The byte-presence check does not exclude the section's own markdown
   heading line from "grounded" text, so a `supported` verdict citing only
   the heading title passes reconciliation with no real body support.**
   `resolve_bound_sections`' `"text"` field is sliced from `heading["byte_start"]`
   (`paper_source_span.py:66-67`), and `segment_markdown` sets that
   `byte_start` to the ATX heading match's own start (`paper_guidance.py:422`)
   — so the heading line itself is part of the "re-derived text" the spec's
   own `Requirement: The Permissive Verdict Carries The Burden Of Proof`
   defines as the comparison target. I reproduced this directly (not by
   reading, by running): a subject sentence asserting an unrelated claim,
   with an account entry `supported` whose span is only the section title
   `"3. Calibration Regime"`, reconciles to `supported` unchanged — no
   downgrade, no refusal. No test in the 39 new grounding tests exercises
   this shape: the shared `_bound_section` fixture (`test_paper_writing.py:13343`)
   never includes a heading line in its `text` field, unlike the real
   `resolve_bound_sections` output. This does not violate the letter of any
   of the 24 scenarios or design.md's written decisions — the heading line
   genuinely is part of "the section's own bytes" as `resolve_bound_sections`
   defines it — but it is a real, untested gap in the property this whole
   change exists to make load-bearing (D1). Fixing it correctly (stripping
   the heading line from the comparison text, or requiring a minimum span
   length) would mean changing `resolve_bound_sections`' shared semantics in
   `paper_source_span.py`, which also backs the already-shipped
   `transposition-fidelity`/`SOURCE_SECTION_VERBATIM` check — out of this
   change's stated scope (D5: "paper_leak.py is touched by this change not
   at all"; no file change here touches `paper_source_span.py`). Reported,
   not fixed, to avoid widening the change.

**SUGGESTION**:
1. Requirement "A Sibling Check, Never An Extension Of The Verbatim Or Leak
   Checks", Scenario "A verbatim paste and an unsupported claim are two
   distinct refusals" has no single test that literally demonstrates both
   codes firing from the same draft shape in two separate invocations. The
   property is proven in composition (ordering test + independent
   reachability of `SECTION_UNSUPPORTED_CLAIM` + the static
   `paper_leak.py`-untouched diff), which is sufficient evidence, but a
   future session adding one explicit two-refusal test would close the gap
   between the scenario's literal wording and its test coverage.
2. Archive needs to know this ahead of time, not discover it: `openspec/specs/transposition-grounding/`
   has **no canonical file yet** — `gentle-ai sdd-archive-compose --canonical
   /dev/null --delta .../spec.md --output -` fails with `canonical spec has
   no "### Requirement:" headings to compose against`, as expected for a
   genuinely new capability. This is not a defect: the prior archived change
   `2026-09-20-the-tripwire-reaches-the-section-that-feeds-it` shipped the
   same shape for its own new capability (`transposition-fidelity`) — a
   delta spec with `## Purpose` + `## Requirements` directly, no
   `## ADDED Requirements` marker — and its canonical file at
   `openspec/specs/transposition-fidelity/spec.md` was later created (not
   composed) with that exact same shape. `transposition-grounding/spec.md`
   in this change already matches that working precedent byte-for-byte in
   structure. Archive should **create** `openspec/specs/transposition-grounding/spec.md`
   directly from this change's delta rather than invoke the compose tool in
   merge mode.

### Verdict
**PASS WITH WARNINGS**
All 47 tasks complete and verified against running code; both full suites
green (646/646 JS, 4559/4559 Python with 3 pre-existing unrelated skips);
all four mutation proofs re-run and confirmed red-under-mutation myself,
including the load-bearing byte-presence check (D1); `downgraded` vs.
agent-returned `undecidable` counted separately and confirmed by direct
execution; scope boundary (`evidence:`/`argument`-mode) proven by a lock,
re-run myself; roster at 165, engine lines at 235, zero deletions,
`paper_leak.py` untouched — all independently re-measured, not taken from
apply's report. One WARNING (an untested degenerate-span acceptance gap,
out of this change's stated scope to fix) and one SUGGESTION (a scenario
covered in composition rather than by one literal test) keep this from a
clean PASS; neither blocks archive.
