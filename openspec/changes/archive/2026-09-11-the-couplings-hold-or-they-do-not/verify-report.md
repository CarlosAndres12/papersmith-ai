```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:9a37717ea38a7686a8122f00dd1f9ddef6d8939070928caa9276e9dc2c0df935
verdict: pass
blockers: 0
critical_findings: 0
requirements: 18/18
scenarios: 22/22
test_command: "npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'"
test_exit_code: 0
test_output_hash: sha256:df6f7b886386fb41fb09d7d51668a2a6599d3958d31a14fda1f98daf5211aa2e
build_command: "npm run typecheck"
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: the-couplings-hold-or-they-do-not
**Version**: N/A (no version field in specs)
**Mode**: Strict TDD

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 32 |
| Tasks complete | 32 |
| Tasks incomplete | 0 |

### Build & Tests Execution
**Build**: ✅ Passed — `npm run typecheck` exit 0, zero diagnostics.

**Tests**: ✅ 559 npm passed / 3202 Python passed (6 skipped, pre-existing/unrelated) / 0 failed.
```text
npm test: tests 559, pass 559, fail 0, cancelled 0, skipped 0, todo 0
.venv/bin/python -m unittest discover: Ran 3202 tests in 609.292s — OK (skipped=6)
```

**Coverage**: not measured (no coverage tool wired in this repo) — ➖ Not available.

### Spec Compliance Matrix

**coupling-verification** (9 requirements, 11 scenarios)
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Verdict Vocabulary And Classification Field | Classification always present | `ReportShapeTests` (full suite) | ✅ COMPLIANT |
| Coupling 1 — Contribution List Identity | M1 reordered names fail | `CouplingOneTests.test_mutation_1_reordered_names_in_one_block_fails` | ✅ COMPLIANT |
| Coupling 2 — Chain Word Identity | M2 synonym breaks identity | `CouplingTwoTests.test_mutation_2_synonym_at_one_link_fails` | ✅ COMPLIANT |
| Coupling 3 — The Gap Is Assisted | Assisted payload published | `GapTests.test_unmutated_fixture_is_unconditionally_unmeasured_...` + `test_both_full_texts_and_front_lists_are_published` | ✅ COMPLIANT |
| Coupling 4 — Diagram Cell Disjointness | M4a undeclared cell fails | `ArtefactsTests.test_mutation_4a_undeclared_results_cell_fails` | ✅ COMPLIANT |
| Coupling 4 — Diagram Cell Disjointness | M4b shared box fails | `ArtefactsTests.test_mutation_4b_a_contribution_added_to_setup_cells_fails_on_intersection` | ✅ COMPLIANT |
| Coupling 5 — Future Work ⊆ Limitations | M5 unanswered direction fails | `FutureWorkTests.test_mutation_5_a_direction_answering_no_declared_limitation_fails_totality` | ✅ COMPLIANT |
| Declared-Name Literal Presence Limit | Declared name absent from bytes | `CouplingOneTests.test_declared_name_absent_from_block_bytes_fails_distinctly` | ✅ COMPLIANT |
| Declaration Record Presence Gates The Run | M6 empty record refuses | `EvidenceTests.test_mutation_6_absent_declaration_record_refuses_and_writes_nothing` + `test_mutation_6_empty_declaration_record_refuses` | ✅ COMPLIANT |
| Declaration Record Presence Gates The Run | Undeclared block reports unmeasured, not pass | `CouplingOneTests.test_an_undeclared_block_reports_unmeasured_not_pass` + hand-probe (see notes) | ✅ COMPLIANT |
| Fixture-Backed Reachability | Fixture proves both directions | `_build_coupling_paper` + `CouplingOneTests`/`CouplingTwoTests`/`ArtefactsTests`/`FutureWorkTests`/`CouplingVerifyCLITests` (M1/M2/M4/M5/M6 all reachable-fail, unmutated reachable-green) | ✅ COMPLIANT |

**citation-integrity** (4 requirements, 4 scenarios)
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Classification | Classification is data, not prose | `CitationTests` (all) | ✅ COMPLIANT |
| Dangling Citation Is A Hard Failure | M3a dangling cite fails | `CitationTests.test_mutation_3a_dangling_cite_fails_naming_it` | ✅ COMPLIANT |
| Orphan Bib Entry Is Reported, Not Failed | M3b orphan entry listed, not failing | `CitationTests.test_mutation_3b_orphan_entry_is_listed_not_failing` | ✅ COMPLIANT |
| The Two Directions Are Independently Proven | Each direction proven on its own | `test_mutation_3a_...` (orphans==[]) + `test_mutation_3b_...` (dangling==[]) — cross-assertions confirm independence | ✅ COMPLIANT |

**contract-currency** (4 requirements, 4 scenarios)
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| Classification | Classification is data, not prose | `ContractCurrencyTests.test_unmutated_fixture_holds_with_provenance_present` (`classification == "out-of-reach today"`) | ✅ COMPLIANT |
| An Absent Provenance Record Reports Check B Unmeasured | M7 absent record → check B unmeasured, run continues, exit 0 | `ContractCurrencyTests.test_mutation_7_absent_provenance_region_reports_unmeasured_never_zero_stale` | ✅ COMPLIANT |
| Whole-File Hash Semantics Are Inherited, Not Narrowed | One edit flags a whole section | `ContractCurrencyTests.test_one_byte_edit_to_the_shared_contract_file_flags_both_recorded_blocks_stale` | ✅ COMPLIANT |
| verify Never Writes The Provenance Record | A refusal leaves the record untouched | `ReadOnlyTests` (AST lock + content-manifest) + `CouplingVerifyCLITests.test_a_refusal_path_also_writes_nothing_and_exits_two` | ✅ COMPLIANT |

**block-substitution delta** (1 requirement, 3 scenarios)
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| verify Verb Is Registered And Read-Only | A full run leaves main.tex untouched | `CouplingVerifyCLITests.test_a_full_run_leaves_main_tex_untouched_and_exits_zero` | ✅ COMPLIANT |
| verify Verb Is Registered And Read-Only | A refusal path also writes nothing | `CouplingVerifyCLITests.test_a_refusal_path_also_writes_nothing_and_exits_two` | ✅ COMPLIANT |
| verify Verb Is Registered And Read-Only | Existing verbs are unaffected | Full suite green (`ScaffoldTests`/`BlockCoreTests`/`OpenBlockTests` unchanged, 3202 tests OK) | ✅ COMPLIANT |

**Compliance summary**: 22/22 scenarios compliant.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|---|---|---|
| Two-module I/O seam (`paper_coupling_evidence.py` reads, `paper_verify.py` is pure) | ✅ Implemented | Confirmed by source read + AST lock; see Control 5 finding below for a scope gap in that lock |
| `CHECKS`/`_CHECK_FUNCTIONS` closed-roster completeness, both directions | ✅ Implemented, re-verified by hand | Module-level `assert set(_CHECK_FUNCTIONS) == set(CHECKS)` — mutated both directions live (extra `CHECKS` member with no function; extra function with no `CHECKS` member), both raised `AssertionError` immediately |
| Derived block set never reads a record-declared fallback | ✅ Implemented, re-verified by hand | Fed a record carrying its own `block_requirements` key; `blocks_by_fact` ignored it entirely and still derived the 4 real sections-corpus blocks |
| Coupling 3 (`gap`) vocabulary structurally excludes `pass`/`fail` | ✅ Implemented, re-verified by hand (stronger than expected) | Hand-mutated `check_gap` to compute `verdict` from the three clean mechanical sub-results; `_entry`'s own guard (`unmeasured_reason set on a non-unmeasured verdict`) raised `AssertionError` before the false verdict could even be returned — a second, independent test-level catch also fires |
| M6 vs. "one block undeclared" are genuinely distinct tiers | ✅ Implemented, re-verified by hand | Whole-record-absent → `Refused(DECLARATION_RECORD_ABSENT)`, run-level, exit 2. One block's entry stripped from an otherwise-present record → run does NOT refuse; only the dependent checks (`contribution-list`, `artefacts`) go `unmeasured`/`BLOCK_NOT_DECLARED`; independent checks (`chain`, `citations`, `gap`) still report real verdicts |
| M8 (write inside `paper_verify.py` fails content-manifest guard) | ✅ Implemented, test-verified | `ReadOnlyTests.test_mutation_8_a_write_in_paper_verify_fails_the_manifest_guard`, part of the green full-suite run |
| M9 (roster walk reaches `paper_verify.py`) | ✅ Implemented, re-verified by hand this session | Planted a throwaway `Refused("M9_BYHAND_PROBE", ...)` directly into the real on-disk `paper_verify.py`; `RefusalRosterTests.test_every_reachable_refusal_is_classified` went RED naming exactly that code; reverted via `git checkout --`, sha256 confirmed byte-identical to the committed file, full `RefusalRosterTests` class re-ran GREEN. Confirms the disclosed limitation is real: `reachable_paper_refusal_codes()` reads `SKILL_SCRIPTS / f"{name}.py"` by fixed real path, so `_run_against_mutant`'s `sys.modules` substitution genuinely cannot reach it — the by-hand proof was the only available method, and it holds |

### Design Coherence
| Decision | Followed? | Notes |
|---|---|---|
| skill-local modules, an evidence seam, no `_core/` | ✅ Yes | Two modules as designed; `paper_evidence.py` name collision with a landed sibling handled by renaming to `paper_coupling_evidence.py`, disclosed |
| Every side carries its provenance (`derived`/`declared`) | ✅ Yes | `TWO_DECLARED_SIDES` limit is derived from `_entry`'s own sides list, not hand-listed — `test_two_declared_sides_limit_is_derived_never_hand_listed` proves both directions plus the real report |
| One record (`paper/couplings.json`), one grammar, this change writes none of it | ✅ Yes | Confirmed via AST lock + AST-scan for write ops, both zero hits |
| Three tiers of inability are architecturally different (whole record absent / one block absent / provenance absent) | ✅ Yes, re-verified by hand this session | See M6-vs-block-undeclared probe above |
| Read-only proven three ways (AST lock, content manifest, M8) | ⚠️ Partially — see CRITICAL/WARNING below | AST lock only forbids *write* operations in both modules; it does not enforce that `paper_verify.py` never *reads* disk either, despite that module's own docstring and design.md's stronger claim ("no Path, no open, no disk read anywhere in this module") |
| Coupling 3's only verdict is `unmeasured` | ✅ Yes, re-verified by hand, more robust than documented | Enforced by TWO independent mechanisms: `_entry`'s runtime assertion guard, and dedicated tests |
| Spec/design reconciliations (M7 exit-code wording, declarations-region wording) | ✅ Yes | Read both spec files directly; both carry the "Reconciled from..." paragraphs matching the disclosed deviation exactly |

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. The read-only AST lock (`ReadOnlyTests._forbidden_write_calls`, used by `test_ast_lock_finds_no_write_operation_in_either_module`) applies an identical *write-forbidding* rule to both `paper_coupling_evidence.py` and `paper_verify.py`. It does not check for *read* operations in either file, so it does not actually distinguish "the reader that is allowed to read" from "the check that must never touch disk" — both modules pass the same negative scan. `paper_verify.py`'s own guarantee of never touching disk currently holds only because the file happens to import nothing from `pathlib`/`os`/`io` (confirmed: zero references to `Path` anywhere in the file) — a structural fact, not an enforced one. Verified live: injected `from pathlib import Path; _P('/etc/hosts').read_bytes()` into a sandboxed mutant of `paper_verify.py` (via `_run_against_mutant`, never touching the real file) and ran the entire 174-test `test_paper_writing.py` module against it — all 174 passed, including the AST-lock test itself (which reads `SKILL_SCRIPTS / "paper_verify.py"` by a fixed real path and therefore never even saw the mutant's bytes — the same reachability gap already disclosed for M9). No spec requirement is violated by this (the specs and design only require *write*-freedom, which IS proven), but the stronger internal claim in both modules' own docstrings ("no disk read anywhere in this module") is currently unproven by any executable guard.

**SUGGESTION**: None beyond the WARNING above.

### Notes on disclosed deviations (checked, not merely inherited)

All 8 items in tasks.md's "Notes from apply" plus item 5's docstring in `CouplingVerifyCLITests` were checked against the actual source and found accurate:
- Deviation 1 (module rename `paper_coupling_evidence.py`): confirmed — `paper_evidence.py` is a real, distinct, landed module (`no-claim-without-a-source-that-holds-it`'s claim↔source record); both are imported separately at `paper_cli.py` lines 47 and 59.
- Deviation 2 (`ModuleCompletenessTests` forcing the import into Unit 1): confirmed — `git show --stat 05b2eaf` shows both new modules created and `paper_cli.py` touched (+10 lines, imports only) in the first commit; `cmd_verify`/`COMMANDS`/`_COMMANDS` wiring only appears in `52be416`.
- Deviation 3 (`provenance` region / `paper_provenance.py` already landed, check B produces real pass/fail): confirmed by reading `paper_coupling_evidence.py` (imports `paper_provenance.read_provenance`/`drift` directly) and `ContractCurrencyTests.test_unmutated_fixture_holds_with_provenance_present` / `test_one_byte_edit_...` (both real, non-`unmeasured` verdicts).
- Deviation 4 (programmatic fixture builder, not a static `tests/fixtures/` tree): confirmed — `_build_coupling_paper` drives real `paper_scaffold.scaffold`/`paper_block.open_block`/`paper_block.substitute(..., contract=...)` calls.
- Deviation 5 (M9 by-hand, not `_run_against_mutant`): confirmed AND independently re-executed this session (see Correctness table above) — the stated reason (`reachable_paper_refusal_codes()` reads by fixed path, not via `sys.modules`) checks out, and the same limitation was found to also apply to the AST-lock test (see WARNING above), which the apply's own notes did not separately flag.
- Deviation 6 (verdict vocabulary `pass|fail|unmeasured` over design.md's `holds|fails`): confirmed — both spec files use `pass|fail|unmeasured` normatively; `paper_verify.py`'s own docstring states the reconciliation explicitly.
- Deviation 7 (spec reconciliations beyond 3.13's literal scope): confirmed — both `contract-currency/spec.md` and `coupling-verification/spec.md` carry explicit "Reconciled from..." paragraphs, read directly in this session.
- Deviation 8 (`openspec/changes/*` untracked, left for `sdd-archive`): confirmed — `git status --short` shows `openspec/changes/the-couplings-hold-or-they-do-not/` as untracked (`??`), consistent across every sibling change in this repo.
- The `sections/02-experimental-setup.md` `figure.components_from` exclusion: re-confirmed independently this session via `rg -n "figure|components_from|paper_obligation"` over both new modules — zero matches. Also observed the named sibling corrective landing live (uncommitted) in `paper_cli.py` during this verify session, confined entirely to `_check_obligations`'s docstring and `--expected-components`'s help text — it does not touch any line this change owns (imports, `cmd_verify`, `COMMANDS`/`_COMMANDS`, `REFUSAL_CLASSIFICATION`).

### Concurrency note

Diffed this change's five owned files (`paper_verify.py`, `paper_coupling_evidence.py`, `paper_cli.py`, `tests/test_paper_writing.py`, `SKILL.md`) against commit `52be416` (this change's own HEAD) three times across the session: at the start (zero diff on all five), mid-session (zero diff), and at the end (a fourth check just before this report's persistence showed `paper_cli.py`, `SKILL.md`, and `tests/test_paper_writing.py` ALL now carry uncommitted sibling edits (the same `a-diagram-that-compiles-or-says-why` corrective landing live — `render`'s obligation-suite rows in `SKILL.md` at lines 486-548, and `FigureObligationTranscriptionTests` in `test_paper_writing.py` at line 1043, both well outside this change's own sections — SKILL.md's "The couplings hold, or they do not" section and the coupling test classes starting at line 1966 — confirmed by diff hunk line numbers). Zero overlap with this change's own additions on any of the three files, at every checkpoint. This change's own code was never touched by the concurrent sibling.

### Verdict
**PASS**
32/32 tasks complete, 18/18 spec requirements and 22/22 scenarios compliant with passing runtime evidence, 559 npm + 3202 Python tests green (6 pre-existing skips, unrelated), typecheck clean, all nine named mutations (M1–M9) independently re-verified — seven by reading the existing tests plus the full green run, and M9 and the coupling-3-vocabulary guarantee additionally re-proven by hand this session. One WARNING (AST lock does not distinguish read-allowed from read-forbidden; a stronger internal claim in two modules' docstrings is currently unproven by any executable guard) does not block archive — it is a coverage gap in an already-passing guarantee, not a spec violation or a functional defect.
