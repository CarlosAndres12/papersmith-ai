```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:b23a49d2d81aeccef3c062aff45002cf04cc2325ca8a457ed43fde4143675830
verdict: fail
blockers: 1
critical_findings: 1
requirements: 16/16
scenarios: 25/25
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:4d26fe65a1dc27479f817bcb810bb667947b7f77a068d880d64c0f8acf79e0af
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:8bd85f405729b87471efb01c69c541f2195dc6c57426774a3eaf4e8b4cd5b596
```

## Verification Report

**Change**: a-diagram-that-compiles-or-says-why
**Version**: N/A (single-version spec)
**Mode**: Strict TDD
**Evidence pin**: 73ae90159a96f044d896650a7e08a650ef5d040f (this change's own last commit; verified clean against the live worktree at every check via `git diff 73ae901 -- <owned files>` — zero bytes of drift throughout this verify, despite a concurrent sibling apply writing elsewhere on the same branch)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 23 (Phase 0–5, tasks.md) |
| Tasks complete | 23 |
| Tasks incomplete | 0 |

### Build & Tests Execution
**Build**: ✅ Passed
```text
$ npm run typecheck
> papersmith-ai@0.1.0 typecheck
> tsc -p tsconfig.json
(exit 0, no output)
```

**Tests**: ✅ 559 passed (npm) + 3160 passed, 6 skipped, pre-existing (python) / ❌ 0 failed
```text
$ npm test            → tests 559, pass 559, fail 0
$ .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
  → Ran 3160 tests in 467.5s, OK (skipped=6)
```
Also independently re-ran, targeted, with real execution evidence (not just discovery):
- `LatexAbsenceTests`, `LatexInvocationTests`, `LatexStaleLogTests`, `FigureLedgerTests`,
  `ManifestCrossTests`, `FixtureProvenanceTests`, `RealLogParsingTests`, `EndToEndCompileTests`,
  `DiagramMutationProofTests` (all 8 mutations), `NoSubprocessScanTests`, `test_agents.AgentBindingTests`,
  `RefusalRosterTests`, `VocabularyLeakTests`, `FigureObligationTranscriptionTests`, `ContractHeaderTests`
  — all green, individually confirmed.

**Coverage**: not available (no coverage tool detected in this stack)

### Independent measurement beyond the named scenarios (per verify brief)

1. **`openin_any=p` vs. absolute-path `\input{}`** — reproduced independently (own scratch
   compile, real `latexmk`/pdfTeX, TeX Live 2026, sandbox env identical to `paper_latex.py`'s
   `_SANDBOX_ENV`): a `\input{<absolute path outside paper/Figures/>}` **is read and compiled
   successfully** under `openin_any=p` (exit 0, PDF produced, log shows the external file
   opened). Then confirmed `paper_figure.scan_data_boundary` refuses this exact source with
   `DIAGRAM_PLOTS_DATA` before any compile is attempted. **The apply's claim is correct and
   independently reproduced**: stop A (source scan) is the load-bearing defense; stop B
   (`openin_any=p`) alone does not catch it.
2. Planted three further stop-A vectors and confirmed each refuses `DIAGRAM_PLOTS_DATA` by
   direct call: a `\usepackage{pgfplots}` load, a `\pgfplotstableread{data.csv}` external-table
   read, and a 6-point `coordinates{...}` series over the illustrative threshold.
3. **Repair budget survives edits between attempts**: re-ran `FigureLedgerTests` and
   `DiagramMutationProofTests.test_mutation_8...` directly — the mutation that re-keys the
   budget to `(id, sourceDigest)` is confirmed to turn the guarding test red, and the real
   source file is restored byte-identical afterward (`git status --short` clean before and
   after).
4. **`latexmk -g` presence**: confirmed present in `_LATEXMK_FLAGS` and asserted by
   `LatexStaleLogTests` (own re-run: pass).
5. **`shutil.which` empty-`PATH` + empty cwd**: confirmed `LatexAbsenceTests` chdirs into a
   fresh empty temp dir before asserting `LATEX_TOOLCHAIN_ABSENT` with `PATH=""` — the correct
   defense against `shutil.which("", path="")` resolving a relative name against `cwd`.
6. **Fixture provenance**: independently recompiled all three committed `.tex` fixtures against
   this real machine's `latexmk`/pdfTeX; the regenerated logs match the committed ones on
   banner, package-load order and versions, byte-for-byte modulo timestamps and memory-usage
   counters — consistent with genuine capture, not hand-authoring. **However**, see CRITICAL/
   WARNING finding on `shell_escape` capture-environment mismatch below.
7. **Section 05 "a legal table triggers nothing"**: confirmed structurally — `render` requires
   `<id>.tex` to exist (else `DIAGRAM_SOURCE_ABSENT`) and `_check_obligations` is only invoked
   from inside a successful `render` call, so a table choice (no `<id>.tex` written for that
   block) has no code path that can reach any obligation check at all. `mandatory: false` on
   `sections/05` block `rw-synthesis-artefact` confirmed by direct contract parse.
8. **Results-locatability stays out of scope**: confirmed no reference to "results" or section
   03 anywhere in `paper_obligation.py`, `paper_figure.py`, or the new `paper_cli.py` wiring —
   `<id>.diagram.json` is left as the durable manifest for a later phase to read, exactly as
   design.md states.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|---|---|---|---|
| authored-diagram: Source Layout | Manifest without source refuses | `ManifestCrossTests.test_manifest_without_matching_source_refuses_diagram_source_absent` | ✅ COMPLIANT |
| authored-diagram: Standalone Compile | Clean compile produces PDF | `EndToEndCompileTests.test_a_real_clean_compile_succeeds_or_reports_unmeasured` (real compile, this machine) | ✅ COMPLIANT |
| authored-diagram: Standalone Compile | Error mapped to source line | `RealLogParsingTests.test_the_undefined_control_sequence_fixture_maps_to_its_real_source_line` | ✅ COMPLIANT |
| authored-diagram: Toolchain Absence Refusal | Empty PATH refuses by name | `LatexAbsenceTests.test_empty_path_with_cwd_in_an_empty_dir_refuses_latex_toolchain_absent` | ✅ COMPLIANT |
| authored-diagram: Package Absence Spends Nothing | Missing package refuses w/o spend | `FigureLedgerTests.test_a_missing_package_refuses_and_spends_nothing` | ✅ COMPLIANT |
| authored-diagram: Repair Budget Ledger | Budget survives edits, 5th refuses | `FigureLedgerTests.test_the_budget_survives_edits_between_attempts_and_the_fifth_refuses` + mutation 8 (re-run, confirmed) | ✅ COMPLIANT |
| authored-diagram: Repair Budget Ledger | Acknowledgement clears ledger | `FigureLedgerTests.test_acknowledge_reset_clears_a_spent_ledger`, `...through_the_cli` | ✅ COMPLIANT |
| authored-diagram: Data-Figure Boundary | Plotting package refuses pre-compile | `DiagramMutationProofTests` mutation 6 + own independent plant (pgfplots/pgfplotstable/coordinates/absolute-`\input`) | ✅ COMPLIANT |
| authored-diagram: Data-Figure Boundary | Unreachable results path fails independently | design/threat-matrix reasoning + stop-B measured limit documented and reproduced | ✅ COMPLIANT |
| authored-diagram: No-Skip Test Evidence | Every tier runs, none skipped | `NoSkipTests` AST guard (re-run, confirmed) | ✅ COMPLIANT |
| authored-diagram: No-Skip Test Evidence | Unmeasured real compile never reads as pass | `EndToEndCompileTests` (this machine: real compile, reports `ok`, never a skip) | ✅ COMPLIANT |
| authored-diagram: Fixture Log Provenance | Fixture carries capture provenance | `FixtureProvenanceTests` (re-run, confirmed) + own independent recompile cross-check | ✅ COMPLIANT (see WARNING on env fidelity) |
| diagram-obligation: Obligations Read From Contract | Deleting figure: removes obligation | `ContractHeaderTests.test_no_figure_key_resolves_to_none` | ✅ COMPLIANT |
| diagram-obligation: Components Check | Methods diagram matches contribution list | `ObligationTests.test_matching_ordered_components_pass` (section 01 config) | ✅ COMPLIANT |
| diagram-obligation: Components Check | Dropped component refuses | `ObligationTests.test_a_dropped_component_refuses_component_mismatch` + mutation 1/2 | ✅ COMPLIANT (mechanism correct; see CRITICAL below re: section 02's own wiring) |
| diagram-obligation: Manifest Crossed, Both Directions | Undeclared node refuses | `ManifestCrossTests.test_a_node_in_source_absent_from_manifest_refuses_manifest_source_mismatch` | ✅ COMPLIANT |
| diagram-obligation: Separation Check | Dataset in methods diagram refuses | mutation 3 (re-run, confirmed) | ✅ COMPLIANT |
| diagram-obligation: Separation Check | Shared label across two diagrams refuses | mutation 4 (re-run, confirmed) | ✅ COMPLIANT |
| diagram-obligation: Caption Check | Undecoded encoding refuses | mutation 5 (re-run, confirmed) | ✅ COMPLIANT |
| diagram-obligation: Mandatory Diagram Presence | Mandatory diagram missing refuses | `ObligationTests` (direct, no mutation per design.md's own note — one-line boolean check) | ✅ COMPLIANT |
| diagram-obligation: Conditional Synthesis Artefact | Table choice carries no obligation | `test_a_table_choice_for_block_05_carries_no_diagram_obligation` | ⚠️ PARTIAL — asserts only `mandatory == False`, not the full "no check runs" behavior; that behavior is real and confirmed by code-path analysis (§ point 7 above), not by this test |
| section-contract: Front Matter Schema (MODIFIED) | Valid header parses | `ContractHeaderTests` | ✅ COMPLIANT |
| section-contract: Front Matter Schema (MODIFIED) | Missing mandatory field refuses | (pre-existing sibling coverage, unchanged) | ✅ COMPLIANT |
| section-contract: Front Matter Schema (MODIFIED) | Valid figure object parses | `ContractHeaderTests.test_a_valid_figure_object_parses` | ✅ COMPLIANT |
| section-contract: Front Matter Schema (MODIFIED) | Figure object missing subkey refuses | `ContractHeaderTests.test_a_figure_object_missing_a_subkey_refuses_malformed_figure_obligation` | ✅ COMPLIANT |

**Compliance summary**: 25/25 scenarios have a passing covering test. One (Conditional Synthesis Artefact) is PARTIAL — real behavior confirmed by code-path reasoning, not directly exercised by its own named test.

### Correctness (Static + Executed Evidence)
| Requirement | Status | Notes |
|---|---|---|
| `paper_latex.py` sole subprocess holder | ✅ Implemented | `NoSubprocessScanTests` re-run green; `subprocess`/`shutil.which` confined to this one file |
| Roster completeness (14 new codes) | ✅ Implemented | `RefusalRosterTests` re-run green; all 14 codes present in `REFUSAL_CLASSIFICATION` |
| Real production callers for every public function | ✅ Confirmed | Traced every non-private symbol in all three new modules to a real call site in `paper_cli.py`/`paper_figure.py` (not merely a test) — `acknowledge_reset` and all five `paper_obligation.py` checks now have real CLI-driven callers (`cmd_render`'s `--acknowledge-reset` and `--section/--block/--expected-components` branches), proven by CLI-subprocess tests, closing the self-caught "wired to nothing" defect from `73ae901` |
| No function reachable only via module-level import | ✅ Confirmed | Same trace as above; nothing in `paper_latex.py`/`paper_figure.py`/`paper_obligation.py` is reachable solely through `paper_cli.py`'s top-level `import` statements |
| `sections/02` `figure.components_from: "dataset"` | ❌ **CRITICAL defect** | See below |
| Fixture logs' capture environment vs. production sandbox | ⚠️ WARNING | See below |
| `diagram-author.md`/`SKILL.md` never surface `--section/--block/--expected-components` | ⚠️ WARNING | See below |

### Coherence (Design)
| Decision | Followed? | Notes |
|---|---|---|
| Three skill-local modules, `paper_latex` sole subprocess holder | ✅ Yes | Confirmed by AST scan and by reading all three files |
| Verdict never comes from the parser alone (3-signal) | ✅ Yes | `classify_verdict` matches design.md exactly |
| Budget keyed to id alone, survives edits | ✅ Yes | Confirmed by reading + mutation 8 |
| Two independent data-figure-boundary stops, stop A load-bearing | ✅ Yes, and independently reproduced | See measurement #1 above |
| Obligations read only from `figure:`, no hardcoded section/block id | ✅ Yes | Confirmed by reading `paper_obligation.py` (takes `figure`/`manifest`/`fact_value` dicts and lists only) |
| `05`'s table-or-diagram choice expressed by artifact presence, not a new key | ✅ Yes | Confirmed structurally |

### Issues Found

**CRITICAL** (1):
1. **`sections/02-experimental-setup.md`, block `es-assessment`: `figure.components_from: "dataset"` does not honestly encode this block's own diagram obligation.** The section's own prose (`## The closing diagram`) states the mandatory (`mandatory: true`) diagram must show: which data enter, against which methods the comparison runs, over which axes it is swept, which metric comes from each crossing, where qualitative instruments attach, and the repetition unit — six kinds of content. `components_from: "dataset"` wires the mechanical `check_components` to require the diagram's manifest labels equal *only* the `dataset` fact's resolved value list. Measured directly by execution (`paper_obligation.check_components`): a manifest containing the full, prose-compliant set of boxes (datasets + methods + axes + metric + instrument + repetition unit) is refused `COMPONENT_MISMATCH` (`extra=[...]` naming every non-dataset label); a degenerate manifest containing *only* the dataset boxes (which fails the section's own stated obligation outright) passes cleanly. As wired, the one existing safeguard — `FigureObligationTranscriptionTests` — only asserts the literal word "dataset" occurs in the block's prose (trivially true), never that the named fact's value actually represents what the diagram must contain. The apply's own `design.md` flagged this choice as an unresolved "documented judgment call" ("somewhat imperfectly ... the closing diagram is richer than a single fact's list"), not a solved problem — and direct measurement confirms the imperfection is not cosmetic: the check as configured blocks the correct diagram and admits the wrong one for the one block in this change where `mandatory: true` and the content demanded is richest. No spec scenario names this exact case (the spec's own worked example is section 01, which is correctly configured with `components_from: contributions`), so this did not register as an UNTESTED scenario — it is a real-data wiring defect the spec-scenario matrix cannot see on its own.
   - Remedy is a design decision, not a one-line fix: either (a) accept that `components_from` can only pin one sub-list and scope 02's mechanical Components Check to the dataset sub-set alone (loosening the block's own prose promise that the *whole* crossing is checked), or (b) extend the closed six-subkey `figure` schema with a new mechanism for a multi-fact/composite obligation (a real schema change, out of this change's stated scope), or (c) accept `components_from: "dataset"` as intentionally partial and say so explicitly in the contract/design rather than leaving it silently able to refuse a correct diagram.

**WARNING** (2):
1. **Fixture logs' capture environment does not match the production sandbox for the specific claim it is cited to support.** `paper_latex.py`'s own comments and `SKILL.md` both state: *"`shell_escape=f` genuinely blocks `\write18`, confirmed by a real compile attempt producing no side-effect file"* — presented as "measured against a real TeX Live 2026 install." Independently reproduced the underlying fact and confirmed it is **true**: setting `shell_escape=f` as an environment variable on this real engine does disable `\write18` (`Package shellesc Warning: Shell escape disabled...`). However, the two committed tier-1 fixture logs that this same commentary sits beside (`success.log`, `failure_package.log`) show `restricted \write18 enabled` — TeX Live's *default* (`shell_escape=p`) behavior, not the `f`/disabled behavior the production `_SANDBOX_ENV` sets. Confirmed by independently recompiling both fixtures' own `.tex` sources under (a) no `shell_escape` var and (b) `shell_escape=f`: only (a) reproduces the committed log lines. `provenance.json` records only `distribution`/`pdftexBanner`/`latexmkVersion`/`argv`/`capturedAt`/`os` — no env vars — so nothing in the committed evidence trail actually demonstrates the `shell_escape=f` claim; it rests on an unrepeated, uncommitted ad hoc measurement from the apply session. (The `openin_any=p` claim, by contrast, IS independently reproduced above with matching methodology.) Tier-2's `LatexInvocationTests` does catch a regression to the *value* passed (it asserts the exact env dict reaches the stub), but proves nothing about the real engine honoring it.
2. **`diagram-author.md` and `SKILL.md`'s `render` verb row never mention `--section`/`--block`/`--expected-components`.** The fix in `73ae901` gave `acknowledge_reset` and the five `paper_obligation.py` checks real production callers, proven by CLI-subprocess tests — closing the letter of the self-caught "wired to nothing" defect. But the one artifact that actually drives `render` in ordinary operation, the `diagram-author` agent, is never told these flags exist; it is instead told to "measure before you assert" by manually reading and comparing the `figure:` declaration itself. In practice the mechanical obligation-check code path may run only inside its own tests, never during real diagram authoring, unless a human operator discovers the flags by reading `paper_cli.py`'s own `argparse` help.

**SUGGESTION** (1):
1. `test_a_table_choice_for_block_05_carries_no_diagram_obligation` only asserts `figure.mandatory == False` for section 05's `rw-synthesis-artefact` block; it does not itself execute the "no check runs" scenario the spec names (the behavior is real, confirmed above by code-path reasoning: no CLI path exists that can invoke an obligation check without a `<id>.tex` existing). A stronger test would assert directly that `_check_obligations` (or the underlying checks) are never reached for a table choice, rather than relying on the caller's structural guarantee alone.

### TDD Compliance
| Check | Result | Details |
|---|---|---|
| TDD Evidence reported | ✅ | tasks.md's per-phase items each name their own test class and, per Phase 5's "Findings beyond the plan," the self-caught defect and its fix |
| All tasks have tests | ✅ | 23/23 |
| RED confirmed (tests exist) | ✅ | `tests/test_paper_figure.py` (906 lines, 68 tests) verified on disk |
| GREEN confirmed (tests pass) | ✅ | 3160/3160 python + 559/559 npm, this session, both re-run |
| Triangulation adequate | ✅ | 8 executed mutations independently re-confirmed red-then-restored; multiple test cases per behavior (success/failure/package/unexplained/reset for the ledger; 1–2 scenarios per obligation check) |
| Safety Net for modified files | ✅ | `paper_cli.py`/`paper_contract.py` modifications covered by `RefusalRosterTests`/`ContractHeaderTests`, both re-run green |

**TDD Compliance**: 6/6 checks passed

### Assertion Quality
No tautologies, no assertion-free tests, no ghost loops, and no mock usage found in `tests/test_paper_figure.py` (906 lines) — every test drives either a real CLI subprocess, a real pure-function call, or a real (temp-copy) source mutation.

**Assertion quality**: ✅ All assertions verify real behavior

### Verdict
**FAIL** — one CRITICAL finding (sections/02's `components_from: "dataset"` inverts the correctness of its own mandatory Components Check) blocks a clean pass; all 25 named spec scenarios have passing covering tests, and the remaining two WARNINGs concern evidence rigor and operational reachability rather than broken mechanisms. Everything else measured — including the hardest, most consequential claim in the brief (`openin_any=p` vs. stop A) — is independently reproduced and correct.
