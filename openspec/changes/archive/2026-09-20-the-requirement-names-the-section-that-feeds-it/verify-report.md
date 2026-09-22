# Verify Report: the-requirement-names-the-section-that-feeds-it

**Change**: `the-requirement-names-the-section-that-feeds-it`
**Branch**: `u1u2-the-section-binding-is-inert` (14 commits ahead of `main`, HEAD `21a0a83`, tree clean)
**Mode**: Full artifact set (proposal, design, tasks, 4 delta specs) — full spec-driven verification
**Verdict**: **PASS WITH WARNINGS**

## Completeness

All 8 work units (U1, U2, U2b, U2c, U2d, U3, U3b, U3c, U3d, U3e — tasks.md numbers them 1–8 across phases) are checked complete in `tasks.md`. No unchecked task found.

## Test Evidence (executed by me, not read from artifacts)

| Command | Result |
|---|---|
| `.venv/bin/python -m unittest discover -s tests -p 'test_paper_*.py'` | **970 OK** |
| `test_agents … test_implementation_domain_lock` (10 modules) | **329 OK** |
| `test_implementation_domain_mutation … test_skill_audit` (8 modules) | **616 OK, 3 skipped** |
| `test_proposal_implementation test_remote_execution` | **2353 run, 1 failure** |
| `npm test` | **640/640 pass** |
| Total | 4268 tests, 1 failure, 3 skipped — reproduces the report's claimed numbers exactly |

The one failure, re-run and inspected directly (`test_rule_b_finds_no_target_vocabulary_in_the_forge`), names: `mechanisms` (pre-existing baseline, in `test_implementation_pair.py`, `test_proposal_implementation.py`, `test_remote_execution.py`, `proposal-implementation/SKILL.md`), plus `data-paper` (`experimental-deliberation/{SKILL.md,profile.ts,references/usage.md}`, and `test_paper_decisions.py` — the latter is the **documented, intentional** exception at task 7.2/design.md Decision I: two assertions legitimately test against the real shipped `guidance/` tree) and `research-concept` (`proposal-deliberation/{SKILL.md,profile.ts,references/usage.md}`, `proposal-implementation/{SKILL.md,references/usage.md}`). Every one of these is named in design.md's Open Questions as a reported-not-fixed, out-of-scope collision. Confirmed: nothing new or hidden here.

## Roster Count — measured, not quoted

Ran `reachable_paper_refusal_codes()` directly:

```
144
```

Matches design.md's claimed final count (140 after U3b/U3c, +4 at U3e for `BINDING_FACT_NOT_BINDABLE`, `BINDING_LINEAGE_REQUIRED`, `BINDING_SECTIONS_REQUIRED`, `SOURCE_BINDING_CONFLICT`).

## Mutation Proofs — spot-checked by executing them, not by reading the roster

1. **`SOURCE_BINDING_CONFLICT`** (`RecordedSourceBindingCorpusTests.test_mutation_collapsing_the_conflict_check_lets_disagreement_pass`) — ran it directly: it invokes `_run_against_mutant` against `paper_graph.py`, collapsing the disagreement comparison to `if False:`, and asserts the mutated process both imports (`MUTANT_IMPORTED_OK`) and exits non-zero (i.e. the base test fails under the mutant). **Executed, passed** — the mutation demonstrably breaks the base assertion when the guard is removed.
2. **`SECTION_BINDING_ABSENT`'s richer detail** (`SourceSectionBindingWriteGateMutationProofTests.test_mutation_reverting_the_refusal_detail_to_bare_fails_the_candidates_test`) — ran it directly against `paper_graph.py`, reverting `_describe_binding_absent`'s call to U3's bare message. **Executed, passed** — confirms `test_section_binding_absent_names_the_block_fact_root_and_candidates` (which asserts the current revision, section titles, and `bind` invocation appear in the refusal text) is load-bearing on the richer detail, not merely on the refusal code firing.

Both proofs are real, executed subprocess-level mutations (`_run_against_mutant`), not descriptions. I did not spot-check the remaining five new/amended codes' mutation proofs individually but confirmed by static inspection that each (`EVIDENCE_ROOT_AMBIGUOUS`, `BINDING_FACT_NOT_BINDABLE`, `BINDING_LINEAGE_REQUIRED`, `BINDING_SECTIONS_REQUIRED`, and the pre-U3e six codes) has a `_run_against_mutant`-based test present in `test_paper_writing.py`/`test_paper_decisions.py`, all of which ran green in the full suite above.

## Spec Compliance Matrix

### `source-section-binding` (new capability) — **SATISFIED**

| Requirement | Status | Evidence |
|---|---|---|
| Bindable Facts Are Derived, Never Listed | Satisfied | `is_bindable_fact`/`bindable_facts` test membership in `FACT_SOURCE_ROOT` only; `BindableFactDerivationTests` incl. the sixth-root mutation, ran green |
| A Bindable Fact With No Binding Is Undecided, Refuses Only At `write` | Satisfied | `Corpus.undecided_bindings`, `enforce_bindings` kwarg confirmed in `paper_graph.py`; `_resolve_write_gate` is the sole `True` caller (confirmed by grep); tests ran green |
| A Binding Is Recorded By Using The Skill, Never By Editing A Shipped File | Satisfied | `bind_section`/`reopen_binding`/`read_bindings` present and match design's docstrings exactly; `BindingRecordTests` (17 tests) green; `sections/*.md` carry zero bindings (`git diff main..HEAD -- sections/` empty) |
| A Recorded Binding And A Header-Declared Binding Must Agree | Satisfied | `_reconcile_source_bindings`/`SOURCE_BINDING_CONFLICT` present; mutation-proved (spot-check 1 above) |
| Lineage Resolves To The Current Revision On Disk | Satisfied | `resolve_lineage`, max-ordinal + tie refusal, Phase 2 tests green |
| A Document-Rooted Source With No Marker Refuses | Satisfied | `SOURCE_REVISIONS_UNDECLARED` distinct from `unmeasured`, Phase 2 tests green |
| The Marker Grammar Is Validated, And Disjoint From `guidance/`'s | Satisfied | `read_revisions_marker`, cross-refusal both directions tested (2.4/2.5) |
| Section Existence And Ambiguity, By Title | Satisfied | `_verify_source_section_bindings`, Phase 2 tests green |
| Publishing A Survived Revision Costs Nothing | Satisfied | Integration test (task 2.22) asserts byte-identical reassembly across a version bump |
| A Binding May Name More Than One Section | Satisfied | `requirement_documents` list expansion, U2d tests green, per-title failure isolation tested |
| An Unmeasured Root Is Reported, Never Silently Passed | Satisfied | `source_root_status`, REPOSITORY/INGESTED/empty-PROSE branches tested |

### `section-contract` (modified) — **SATISFIED**

`_validate_document_object` matches the delta spec's shape exactly (single string or non-empty unique-string list, both keys required together, `document` rejected on `requires_declarations`). All listed scenarios have direct tests in `test_paper_contract.py`, confirmed green in the 970-test run.

### `requirement-transcription` (modified) — **SATISFIED**

The independence of `source.quote` verification from `document` resolution is asserted by name in two scenarios ("A resolved document binding does not excuse a failing quote" / "A verified quote does not excuse an unresolved document half"); both have literal test analogues judging by the corpus-assembly test names in `test_paper_writing.py`, and the full suite (which exercises `assemble_corpus` unconditionally on every command) passed.

### `writing-orchestration` (added) — **SATISFIED**

All seven codes (`SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`, `SECTION_BINDING_ABSENT`, `SOURCE_LINEAGE_UNRESOLVED`, `SOURCE_REVISIONS_UNDECLARED`, `MALFORMED_SOURCE_MARKER`, `EVIDENCE_ROOT_AMBIGUOUS`) are wired through `_resolve_write_gate`'s own `assemble_corpus` call, confirmed by direct grep (line 1253) and by `SourceSectionBindingWriteGateTests`/`SecondProseRootWriteGateTests` running green. The "refusal names its own next action" requirement is satisfied and mutation-proved (spot-check 2 above).

## The Six Hardest Invariants

1. **The forge carries no paper of its own.** `git diff main..HEAD -- sections/` is **empty** — confirmed directly. `rg` for `research-concept|MIL-CREDA|s41597|Rényi|q77213|lumen-thesis|field-log` under `.claude/skills/` returns **zero hits inside `paper-writing/`**; the only hits anywhere under `.claude/skills/` are `research-concept` in `proposal-deliberation/` and `proposal-implementation/`, both pre-existing, unrelated skills' own documented, sanctioned configuration/worked-examples (named in design.md's Open Questions, not this change's surface). `data-paper` has zero hits anywhere under `.claude/skills/`. `subprocess` import check: only `paper_latex.py`'s reserved exception. **Satisfied.**
2. **A decision about the paper is made by USING the skill.** `bind_section`/`reopen_binding` are the only write path into a binding; `sections/*.md` carry none; the corpus reports `undecided` rather than inventing one. **Satisfied**, and this is the one invariant with the most direct historical counter-evidence in this very change (U3/U3b's own apply invented two bindings, which Decision H/I retroactively closed) — the closure is real and verified in code, not merely narrated.
3. **Derived, never listed.** `SourceRoot(name, kind)` has no default for `kind` (confirmed: two positional fields, no `= SourceRootKind.PROSE` default anywhere in the `NamedTuple` definition). `is_bindable_fact` tests dict membership only. `BindableFactDerivationTests.test_a_sixth_root_widens_bindability_with_zero_engine_edit` ran green. **Satisfied.**
4. **Every refusal reachable only from `write` has an executed mutation.** Confirmed for two spot-checked codes by executing the mutation tests myself (not reading source); the remaining five are present as `_run_against_mutant` calls and ran green in the full suite. **Satisfied**, with the caveat that I did not execute all seven's mutation subprocess runs individually — only two, per instruction.
5. **The roster is measured.** Re-derived myself: **144**. Matches the artifact's claim exactly.
6. **No `subprocess` in `paper-writing/scripts/`** except `paper_latex.py`'s reserved exception. **Satisfied**, confirmed by direct grep.

## Artifact/Code Disagreements Found

**CRITICAL-adjacent but not blocking (see verdict rationale below): the `apply-progress` Engram artifact is stale — it does not describe the final, shipped state of the code.**

The Engram observation at topic `sdd/the-requirement-names-the-section-that-feeds-it/apply-progress` (id 1931, last revised 2026-09-19 20:16:22, revision 7 of 7) documents only through **U3d** (commits `877995d`/`3955eeb`/`3e5d5fe`, Phase 7). It contains no mention of **U3e / Phase 8** — the `bind` verb, `_reconcile_source_bindings`, `SOURCE_BINDING_CONFLICT`, the richer `SECTION_BINDING_ABSENT` detail, or the roster's move from 140 to 144 — even though:

- `tasks.md` Phase 8 (all 17 sub-tasks, 8.1–8.17) is checked complete and dated with specific test counts (772/772, roster 144).
- `design.md` documents Decision J in full, with its own File Changes/Interfaces/Refusal-Codes-table updates.
- HEAD (`21a0a83 feat(paper-writing): la skill graba la atadura que exige`) is the U3e commit itself, on top of the four commits the memory does describe.

**Which side is stale**: the Engram `apply-progress` artifact, not the code, `design.md`, or `tasks.md`. I verified U3e's claims directly against source (the `bind_section`/`reopen_binding`/`read_bindings`/`describe_binding_candidates` functions, the `cmd_bind` CLI wiring, the `_reconcile_source_bindings`/`_describe_binding_absent` functions in `paper_graph.py`, and their tests) and against a live measured roster of 144 — all consistent with `design.md`/`tasks.md`, none consistent with the Engram artifact's silence on this entire work unit. This is exactly the class of disagreement the task brief asked me to surface rather than paper over: the hybrid store's two halves (OpenSpec files vs. Engram) have drifted, and whoever reads only the Engram topic for this change's apply history would not learn U3e happened at all.

No other artifact/code disagreement was found. `tasks.md`'s own internal note at 5.10 ("Superseded by Phase 7") and design.md's Decision I/J narrative are both internally consistent with the code as measured.

## Requirements With No Directly-Traced Test

None found. Every requirement in all four delta specs has at least one scenario with a matching, currently-green test, confirmed either by direct execution (Phases/classes named above) or by locating the named test class/function and confirming it ran inside the green full-suite run.

## Does anything about the paper being written still reach the shipped surface?

No, with one qualified exception already fully disclosed by the change's own artifacts, not newly discovered by me: `proposal-deliberation`'s and `proposal-implementation`'s own worked-example documentation (`references/usage.md`, `SKILL.md`) still use `research-concept-rNN.md` as their illustrative convention, and `experimental-deliberation/profile.ts` still hardcodes `guidance/data-paper`. These are two **pre-existing, different skills'** own leaks/conventions, explicitly out of scope for this change, reported to the owner in design.md's Open Questions, and are the direct cause of the one known-red test. Nothing new leaked in the `source-section-binding` surface itself.

## Verdict

**PASS WITH WARNINGS.**

- All tasks complete, all four delta specs satisfied by executed, currently-green tests.
- Roster re-derived independently at 144, matching the artifact.
- Two mutation proofs executed directly by me and confirmed reachable.
- The one known test failure is the pre-existing, disclosed baseline plus its two disclosed, out-of-scope widened hits — not a regression this change introduced.
- The one real gap: the Engram half of the hybrid `apply-progress` artifact never recorded U3e (Phase 8), the change's own final and largest work unit. This is a bookkeeping/traceability defect in the persistence pipeline, not a defect in the shipped code or in the OpenSpec artifacts (`design.md`/`tasks.md` are both current and correct). It should be corrected (re-save `apply-progress` covering U3e) before or as part of archive, but it does not, on its own, misstate what shipped — every claim I could independently verify against source and tests held.

**Recommendation**: safe to proceed toward archive, on the condition that the `apply-progress` Engram record is brought current (or the archive step is told explicitly that Phase 8/U3e's history lives only in `design.md`/`tasks.md` and commit `21a0a83`, not in Engram).
