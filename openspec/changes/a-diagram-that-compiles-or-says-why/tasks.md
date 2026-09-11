# Tasks: A Diagram That Compiles, Or Says Why

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 1100–1600 (3 new modules, new test file, CLI/contract/SKILL wiring, agent, 3 section headers) |
| 1400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | 5 stacked units, PR1→PR2→PR3→PR4→PR5 |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High (also at risk against the 1400-line override)

### Suggested Work Units

| Unit | Goal | PR | Focused test | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | `paper_latex.py`: discovery, invocation, log parse, verdict | PR1 | `python -m unittest tests.test_paper_figure.LatexInvocationTests tests.test_paper_figure.LatexAbsenceTests` | Stub-`latexmk` on injected `PATH` (tier 2), emptied `PATH` (tier 3) | Delete `paper_latex.py` and its tests |
| 2 | `paper_figure.py`: layout, manifest cross-check, stop A, ledger | PR2 | `...FigureLedgerTests ...ManifestCrossTests` | Stub-`latexmk` budget scenarios | Delete `paper_figure.py` and its tests |
| 3 | `paper_obligation.py` + `paper_contract.py` figure schema + `sections/01,02,05` `figure:` | PR3 | `...ObligationTests test_paper_writing.ContractHeaderTests` | N/A — pure functions, no process | Revert schema + three section headers |
| 4 | `paper_cli.py` wiring, `REFUSAL_CLASSIFICATION`, roster assertion, `SKILL.md`, `diagram-author` agent | PR4 | `test_paper_writing.RefusalRosterTests test_agents.AgentBindingTests` | `render`/placement verb vs stub `latexmk` | Revert CLI/SKILL/agent adds, verbs disappear |
| 5 | Tier-1 fixture logs + provenance + stop-B `unmeasured` reporting | PR5, stalls if capture unavailable | `...FixtureProvenanceTests` | Real `latexmk` compile, only if captured | Delete fixtures/provenance dir |

## Phase 0: Preconditions (sequencing)

- [x] 0.1 Confirmed: `reachable_paper_refusal_codes()` derives its module scan from `paper_cli_imported_modules()` (`paper_cli.py`'s own module-level imports), not a hardcoded tuple.
- [x] 0.2 Confirmed: `_run_against_mutant` (`tests/paper_mutation.py`) accepts `source_path`, a sibling's own granted exception.
- [x] 0.3 Confirmed: `sections/01,02,05` front matter exists; `_BLOCK_OPTIONAL` had no `figure` key before this change.

## Phase 1: `paper_latex.py`

- [x] 1.1 `LatexAbsenceTests`: `PATH=""` with cwd set to an empty temp dir asserts `LATEX_TOOLCHAIN_ABSENT`.
- [x] 1.2 `LatexInvocationTests`: stub `latexmk` on injected `PATH` records argv/cwd/env; asserts the full flag set, cwd, `-outdir`.
- [x] 1.3 `LatexStaleLogTests`: asserts `-g` is always present in argv.
- [x] 1.4 `VerdictClassificationTests`: verdict disagreement → `unexplained` (pure function over `Diagnostic` tuples).
- [x] 1.5 `paper_latex.py` implemented — injectable `path`, one subprocess call, `FileNotFoundError`-at-spawn → `LATEX_TOOLCHAIN_ABSENT`, log parse (plus `_BARE_PACKAGE_ABSENT_RE`, found via real tier-1 evidence — see Phase 5), three-signal verdict.

## Phase 2: `paper_figure.py`

- [x] 2.1 `ManifestCrossTests`: `DIAGRAM_SOURCE_ABSENT`, both-direction `MANIFEST_SOURCE_MISMATCH`.
- [x] 2.2 Mutation 6 (`DiagramMutationProofTests`): a series plotted → `DIAGRAM_PLOTS_DATA`, executed via `_run_against_mutant(source_path=paper_figure.py)`, confirmed red.
- [x] 2.3 Mutation 8: budget keyed to `(id, sourceDigest)` instead of `id` — four compiles with a source edit before each, fifth refuses `REPAIR_BUDGET_SPENT`; `LATEX_PACKAGE_ABSENT` spends nothing (`FigureLedgerTests`).
- [x] 2.4 `paper_figure.py` implemented — layout resolution, cross-check, stop-A scan, `ledger.json`, `acknowledge_reset`, `place_figure`.

## Phase 3: `paper_obligation.py` + contract schema + section headers

- [x] 3.1 `ContractHeaderTests`: missing subkey → `MALFORMED_FIGURE_OBLIGATION`; unknown `components_from` → `UNKNOWN_FACT`.
- [x] 3.2 `paper_contract.py` — `"figure"` in `_BLOCK_OPTIONAL`, `_parse_figure` validating all six subkeys.
- [x] 3.3 Mutations 1-5 (`DiagramMutationProofTests`): dropped/reordered → `COMPONENT_MISMATCH`; excluded class → `EXCLUDED_COMPONENT`; shared label → `SHARED_COMPONENT`; undecoded encoding → `CAPTION_INCOMPLETE`; `MANDATORY_DIAGRAM_ABSENT` covered directly in `ObligationTests` (no dedicated mutation — the guard is a one-line boolean check with no arithmetic to defeat).
- [x] 3.4 `paper_obligation.py` implemented — pure functions, no disk, no `PATH`.
- [x] 3.5 `figure:` added to `sections/01` (mm-proposal), `02` (es-assessment) and `05` block 5 (rw-synthesis-artefact, `mandatory: false`).
- [x] 3.6 `FigureObligationTranscriptionTests`: each `excludes` entry and `components_from` fact name occurs, whitespace-normalised, in the holder's own prose.
- [x] 3.7 `ObligationTests.test_a_table_choice_for_block_05_carries_no_diagram_obligation`: `05`'s table choice runs zero diagram checks.

## Phase 4: CLI wiring, roster, SKILL.md, agent

- [x] 4.1 `render` + `place` added to `paper_cli.COMMANDS`/`_COMMANDS`; all 14 codes added to `REFUSAL_CLASSIFICATION`.
- [x] 4.2 `RefusalRosterTests.test_the_derivation_finds_the_measured_count`: moved from 79 to 93, measured and documented.
- [x] 4.3 `SKILL.md` updated — verb table, roster, data-figure boundary (corrected against real measurement), `delegates to the \`diagram-author\` agent` line.
- [x] 4.4 `.claude/agents/diagram-author.md` created.
- [x] 4.5 `test_agents.AgentBindingTests` — 15/15 green.

## Phase 5: Tier 1 fixtures + stop-B reporting

- [x] 5.1 **UNBLOCKED, measured rather than assumed.** The orchestrator brief claimed "this machine has no TeX distribution"; measured instead: `/Library/TeX/texbin/latexmk` 4.88 against pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026), tikz/pgfplots/standalone.cls all present. Three raw logs captured from genuine compiles, committed byte-for-byte under `tests/fixtures/paper-figure/{success,failure_error,failure_package}/`, each with `provenance.json` and the `.tex` that produced it. Never hand-authored.
- [x] 5.2 `FixtureProvenanceTests`: every fixture's pdfTeX banner matches its provenance — real assertion, not a stub.
- [x] 5.3 `EndToEndCompileTests`: exercises the genuine pipeline against this machine's real `latexmk`; reports `unmeasured` (never `ok`) on a machine that has none, via the `interpreterMatch: null` idiom, never a skip.
- [x] 5.4 `NoSkipTests`: AST guard — no `skip`/`skipIf`/`skipUnless`/`self.skipTest` anywhere in `tests/test_paper_figure.py`, confirmed.

## Findings beyond the plan

Real tier-1 capture surfaced two things reasoning alone missed:

1. **A missing package's log line carries no `<file>:<line>:` prefix at all** — `! LaTeX Error: File `X.sty' not found.` is emitted before pdfTeX has a current input line, so `-file-line-error` never reformats it. Fixed with `_BARE_PACKAGE_ABSENT_RE`; without it `LATEX_PACKAGE_ABSENT` would never fire and a repair-budget attempt would silently spend on an unfixable error.
2. **`openin_any=p` does not block a literal absolute-path `\input{...}`** on this real TeX Live 2026 engine (confirmed via `-cnf-line=openin_any=p`; the log shows the file opened). `shell_escape=f` does work (confirmed: no `\write18` side effect). Stop A's pre-compile source scan is therefore the primary, load-bearing defense against that vector, not the env var alone — corrected in `SKILL.md` and `paper_latex.py`'s own comments rather than left as an unverified claim.
3. **Self-review before closing out: `paper_figure.acknowledge_reset` and all five `paper_obligation.py` check functions were reachable through the roster's whole-module-import scan but had no real caller outside their own tests** — the exact "wired to nothing" class of defect a sibling's verify found three times already. Fixed in a sixth commit (`73ae901`): `render --acknowledge-reset` and `render --section/--block/--expected-components` now call them for real, each proven by a CLI-subprocess test. No new refusal code; roster stays at 93.

## Phase 6: Corrective batch — `components_from` is load-bearing (verify FAIL, CRITICAL)

`sdd-verify` measured, by direct execution against the real on-disk `es-assessment` obligation,
that `components_from` was read by NOTHING in the production call path — `--expected-components`
(added in the Phase-5 self-review fix above) was an operator-supplied flag never cross-checked
against the fact it claimed to be `_from`, and `es-assessment`'s `components_from: dataset`
silently inverted the Components Check for the one block where it mattered most (a
prose-compliant diagram refused, a degenerate dataset-only one passed). A prior corrective attempt
at this same finding documented the inversion as intended design (a docstring rewrite in
`_check_obligations`) and froze it into a permanent test
(`tests/test_paper_figure.py::ComposedComponentsRealismTests`, its third test asserting the
inversion itself as a target state) — both reverted, not built on, because they made the defect
load-bearing rather than closing it.

- [x] 6.1 Reverted the prior corrective attempt's docstring-only fix in `_check_obligations` and
      deleted `ComposedComponentsRealismTests` in full (its own third test recorded the measured
      inversion as a permanent target state).
- [x] 6.2 `components_from` moved from `_FIGURE_REQUIRED` to `_FIGURE_OPTIONAL` in
      `paper_contract.py` (`ContractHeaderTests.test_a_figure_object_without_components_from_
      parses`, `test_an_explicit_null_components_from_also_resolves_to_none` — same round-trip
      convention `mode` already established).
- [x] 6.3 `paper_declarations.read_fact` (new, read-only) added — the existing declaration-record
      reader, reused rather than reimplemented.
- [x] 6.4 `paper_cli._resolve_expected_components` derives the Components Check's expected list
      from `components_from`'s named fact's declared resolution; `--expected-components` removed
      entirely. `COMPONENTS_FACT_UNRESOLVED`/`COMPONENTS_FACT_NOT_A_LIST` added to
      `REFUSAL_CLASSIFICATION`; roster moved from 94 to 96
      (`RefusalRosterTests.test_the_derivation_finds_the_measured_count`).
- [x] 6.5 `sections/02-experimental-setup.md`'s `es-assessment` block: `components_from: "dataset"`
      removed. Confirmed independent of `the-couplings-hold-or-they-do-not`'s coupling 4 (reads
      only `couplings.json`, never `figure`/`components_from`/`paper_obligation` — grep, zero
      matches).
- [x] 6.6 Reproduced the verifier's own finding the way it measured it, against the REAL
      `sections/02-experimental-setup.md` corpus:
      `CLIWiringTests.test_real_section_02_es_assessment_no_longer_inverts_the_components_check`
      — both the prose-compliant crossing manifest and the degenerate dataset-only one now pass
      (neither can trigger `COMPONENT_MISMATCH`; there is no Components Check left to invert).
- [x] 6.7 Proved the derivation is load-bearing (not merely present):
      `CLIWiringTests.test_editing_components_from_in_the_header_changes_the_verdict` — the SAME
      manifest and declared facts, only the header's own `components_from` string changed from
      `contributions` (passes) to `dataset` (refuses `COMPONENT_MISMATCH`).
- [x] 6.8 `Section02ComponentsCheckOmittedTests` (replacing `ComposedComponentsRealismTests`):
      confirms `es-assessment`'s real contract declares no `components_from`, and that
      `check_excluded`/`check_mandatory` still apply without a Components Check.
      `test_an_undeclared_components_from_fact_refuses_components_fact_unresolved` and
      `test_a_non_json_list_fact_resolution_refuses_components_fact_not_a_list` cover the two new
      refusal codes.
- [x] 6.9 `FigureObligationTranscriptionTests` re-audited: the prose-transcription check now skips
      `components_from` when the block declares none; `es-assessment` moved from `proof:` (citing
      the now-deleted class) to `exempt:` in `_COMPONENTS_REALISM_PROOF`, alongside section 05's
      table-choice exemption.
- [x] 6.10 `SKILL.md`, `.claude/agents/diagram-author.md`, `design.md`, and both delta spec files
      (`section-contract`, `diagram-obligation`) updated to describe the derived-from-declaration
      mechanism and the optional `components_from` schema, replacing every `--expected-components`
      reference.
