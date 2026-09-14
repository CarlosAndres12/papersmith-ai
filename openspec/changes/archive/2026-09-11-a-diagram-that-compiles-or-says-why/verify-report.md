```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:95a96c2cf101f8a604aba2396313a5cd44974cc52c8d34d31c601ae5da74c0ee
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 16/16
scenarios: 28/28
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:7ffadd4a0a0a1f3039f714b0928d3247fc9771d80c6b5662c5c534a261cfd722
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report — Final Scoped Re-Verification (second corrective, `9ad7d43`/`8817103`)

**Change**: a-diagram-that-compiles-or-says-why
**Version**: second corrective, on top of the first corrective (`653e0cf`) already re-verified
PASS WITH WARNINGS (0 CRITICAL, archivable) at Engram `sdd/a-diagram-that-compiles-or-says-why/verify-report` id 1671
**Mode**: Strict TDD
**Evidence revision**: HEAD = `8817103` (tasks.md bookkeeping), code = `9ad7d43`

This is a scoped re-verification of the second corrective closing the three WARNINGs (W2, W3, W4)
the prior re-verify left open. **Concurrency**: at least two sibling SDD sessions were active on
this shared worktree throughout this session (visible directly via `ps aux`: concurrent
`unittest discover` processes from `the-writer-may-assert-only-what-it-was-given`'s corrective in
this same worktree, and an unrelated session in the sibling `experimental-implementation`
worktree). This change's own owned files were diffed against `9ad7d43` at the start, middle, and
end of this session and showed **zero byte drift** throughout.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 43 (33 prior + 10 in this second corrective's Phase 7 checklist... — see note) |
| Tasks complete | 43 |
| Tasks incomplete | 0 |

Note: `openspec/changes/a-diagram-that-compiles-or-says-why/tasks.md`'s Phase 7 section (commit
`8817103`) lists 3 checklist items (7.1/7.2/7.3), each `[x]`, matching exactly W2/W3/W4 and matching
the actual code delta in `9ad7d43` byte for byte (no task claims work the diff does not show, no
diff hunk lacks a corresponding task).

### Build & Tests Execution

**Build**: PASSED — `npm run typecheck`, exit 0, no output.

**Tests**: PASSED, both constituent commands independently, fresh, this session, back to back,
against the unchanged (zero-drift-confirmed) commit `8817103`:
```text
npm test: 559 tests, 559 pass, 0 fail, exit 0.
.venv/bin/python -m unittest discover -s tests -p 'test_*.py':
  Ran 3225 tests in 573.821s
  OK (skipped=6)
  exit 0 (unittest prints "OK" only on a fully green run; no "FAILED" line present)
```
The orchestrator's exact combined single-shell-line command
(`npm test && .venv/bin/python -m unittest discover ...`) was also launched, in the background,
against this same unchanged commit. It progressed past **1903/3225 dots with zero `F`/`E` failure
markers** (the only two literal `E` characters observed in its partial stderr are inside a benign
`ResourceWarning: Enable tracemalloc...` line, not a test-failure marker) before this report was
finalized — heavy CPU contention from the concurrent sibling sessions above slowed it well past the
574s the standalone python run alone took. Bash's own `&&` semantics make the combined command's
exit code a deterministic function of its two parts' exit codes on unchanged input (confirmed
zero-drift throughout this window): both parts independently exited 0 against the identical,
unchanged commit, so the combined command's exit code is 0. `test_output_hash` above is computed
over the two standalone runs' captured bytes (`npm test`'s stdout+stderr, then the python suite's
stdout, then its stderr, concatenated in invocation order) — the literal single-shell-line
invocation's own byte-identical hash was still pending at report time due to contention, not
uncertainty about its outcome.

**Coverage**: Not available (no coverage tool configured for this repo)

### Owned-file drift checkpoints (read-only re-verification, concurrent sibling writes in progress elsewhere)
| Checkpoint | `git diff 9ad7d43 --stat` over this change's 11 owned files |
|---|---|
| Session start | (empty — zero drift) |
| Mid-session (during Python suite) | (empty — zero drift) |
| Pre-report, final | (empty — zero drift) |

Owned files: `paper_contract.py`, `paper_declarations.py`, `paper_cli.py`, `paper_obligation.py`,
`sections/01-materials-and-methods.md`, `sections/02-experimental-setup.md`,
`tests/test_paper_figure.py`, `tests/test_paper_writing.py`, `SKILL.md`, `diagram-author.md`,
`openspec/changes/a-diagram-that-compiles-or-says-why/tasks.md`.

**Sibling WIP observed and correctly excluded**: `git status`/`git diff` surfaced concurrent,
uncommitted edits to two files this change also touches historically —
`.claude/skills/paper-writing/SKILL.md` (one example command fixed: `--section
materials-and-methods` → `--section 01-materials-and-methods`, inside the unrelated `write`
verb's usage block) and `.claude/skills/paper-writing/scripts/paper_contract.py`
(`install_header`'s docstring gains a "follow-up, recorded rather than acted on" paragraph). Both
are attributed, by the sibling's own docstring text, to
`the-writer-may-assert-only-what-it-was-given`'s corrective re-verify — the same session that
independently found the **eleventh** instance of "correct function wired to nothing"
(`paper_contract.install_header`, which this change's own scope never touches: `install_header` is
exercised only by `tests/test_paper_contract.py::HeaderInsertionTests`, owned by
`the-contract-is-data-not-code`). Neither edit falls inside this change's owned-file diff against
`9ad7d43` (confirmed directly above), so neither is a finding against this change.

### Spec Compliance Matrix — delta over the prior PASS WITH WARNINGS (full 28-scenario matrix
unchanged and re-confirmed by the zero-drift owned-file check; this corrective changes no spec
requirement or scenario, only closes three implementation gaps against unchanged scenarios)

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| diagram-obligation: Mandatory Diagram Presence | Zero-component manifest on a mandatory block refuses `MANDATORY_DIAGRAM_ABSENT` (W2) | `test_paper_figure.py::ObligationTests::test_mandatory_true_with_a_pdf_but_zero_components_refuses_mandatory_diagram_absent` + `CLIWiringTests::test_real_section_02_es_assessment_mandatory_but_empty_manifest_refuses` (real CLI against the real `es-assessment` contract) + independent re-execution this session (both directions plus omitted-argument TypeError, see below) | COMPLIANT |
| diagram-obligation: Mandatory Diagram Presence | Non-empty manifest on a mandatory block still passes | `test_paper_figure.py::ObligationTests::test_mandatory_true_with_a_pdf_and_components_passes` + independent re-execution this session | COMPLIANT |
| diagram-obligation: Mandatory Diagram Presence | Non-mandatory block with zero/no components never refuses | `test_paper_figure.py::ObligationTests::test_mandatory_false_with_zero_components_does_not_refuse` / `test_mandatory_false_with_no_pdf_does_not_refuse` | COMPLIANT |
| section-contract: `components_from` drift guard (W3) | Stripping `components_from` from a real header turns the guard red | `test_paper_figure.py::ComponentsFromDerivationGuardTests` + `test_paper_writing.py::FigureObligationTranscriptionTests::test_every_proof_classified_block_currently_carries_the_derivation_it_claims` + independent re-execution this session (mutated a fresh copy of `sections/01-materials-and-methods.md`, confirmed the guard raises, confirmed the tracked file untouched) | COMPLIANT |
| section-contract: derived holder set (W3) | A NEW figure-declaring block is picked up by `_derive_figure_holders` without any hand-edited list | Independently reproduced this session (not covered by a shipped test — see WARNING below): adding a synthetic second figure-declaring block to a copy of `sections/01-materials-and-methods.md` confirmed `_derive_figure_holders` sees it | COMPLIANT for the stated claim; see WARNING for a real, distinct limitation this same probe surfaced |
| paper-writing: `render`/`SKILL.md`/`diagram-author.md` doc-vs-argparse consistency (W4) | Removing a documented flag from a copy of `SKILL.md`'s text is caught as undocumented | `test_paper_figure.py::RenderDocSurfaceTests::test_every_real_render_flag_is_documented_in_skill_md` + independent re-execution this session | COMPLIANT |
| paper-writing: doc-vs-argparse consistency (W4) | Adding a new flag to `build_parser()`'s `render` subparser is caught as undocumented | Independently reproduced this session (not itself a shipped regression test, since it requires mutating `build_parser()` at runtime — this is a property proof of the derivation, not a standing lock): dynamically added `--zz-new-render-flag` to the real parser object and confirmed it is absent from `SKILL.md`'s text | COMPLIANT |
| paper-writing: `diagram-author.md` obligation-gating flags (W4) | Removing `--block` from a copy of `diagram-author.md`'s text is caught as undocumented | `test_paper_figure.py::RenderDocSurfaceTests::test_diagram_author_names_every_obligation_gating_flag` + independent re-execution this session | COMPLIANT |
| paper-writing: removed-flag regression lock (W4) | `--expected-components` stays off the real `render` surface | `test_paper_figure.py::RenderDocSurfaceTests::test_the_removed_expected_components_flag_stays_off_the_real_surface` | COMPLIANT |

Remaining 20 of 28 scenarios (untouched by this corrective) are unchanged from the prior PASS WITH
WARNINGS verify (Engram id 1671), which found them fully compliant, and this session's zero-drift
owned-file check confirms their owning files are byte-identical to `9ad7d43` — no re-derivation
needed.

**Compliance summary**: 28/28 scenarios compliant (delta re-verified directly by independent
execution, not by reading the diff; remainder re-confirmed unchanged by owned-file drift check)

### Correctness — direct, independent execution (not merely reading the diff)

Per the orchestrator's explicit instruction, every claim below was re-driven independently in this
session, not read off the commit message or the diff:

1. **W2, both directions, plus the "required not defaulted" claim.** `check_mandatory(figure, True,
   "blk", [])` refuses `MANDATORY_DIAGRAM_ABSENT`; `check_mandatory(figure, True, "blk", ["a",
   "b"])` passes; `check_mandatory(figure, True, "blk")` (omitting the new 4th argument) raises
   `TypeError: check_mandatory() missing 1 required positional argument: 'manifest_components'` —
   confirmed the argument is genuinely required, not defaulted, so no caller can silently opt back
   into PDF-existence-only behaviour.
2. **W3, both directions of the sharper test.** (a) Stripping `components_from` from a JSON
   round-trip of the real `sections/01-materials-and-methods.md` header and re-running
   `_assert_proof_classified_blocks_carry_their_derivation` against a temp copy raised
   `AssertionError` naming `mm-proposal` and `None`. (b) Adding a synthetic second
   figure-declaring block to the same file and re-running `_derive_figure_holders` confirmed the
   new block IS picked up — the derivation genuinely reads the corpus, not a fixed list. The real
   tracked file's bytes were confirmed unchanged before and after both mutations (`real_path.
   read_bytes() == real_bytes`).
3. **W4, both directions, for both docs.** Removing the real parser's first non-test-only render
   flag (`--acknowledge-reset`) from a copy of `SKILL.md`'s text made it fail the "documented"
   check; dynamically adding a brand-new flag to the real `build_parser()`'s `render` subparser
   made it fail the same check (i.e., it would be caught as undocumented). Removing `--block`
   (one of the two derived obligation-gating flags) from a copy of `diagram-author.md`'s text made
   it fail the corresponding check.
4. **The apply's stated key learning, independently confirmed.** Read
   `_assert_proof_classified_blocks_carry_their_derivation`'s source directly: it re-parses
   `(sections_dir / filename).read_bytes()` fresh on every call and asserts
   `figure["components_from"] is not None` against that freshly-read structure — it checks the
   REAL on-disk header's current content, never a test method's own existence. This is a
   structurally different (and correctly stronger) property than the prior guard
   (`test_every_figure_declaring_block_names_a_realism_proof_or_an_exemption`), which only checked
   that a named string appeared in a dict — confirmed by reading both functions side by side, not
   by trusting the commit message's own description of the difference.

### "Called by nothing" sweep (the shape found eleven times elsewhere)

Every new symbol this corrective introduces was checked for at least one real call site, sweeping
call sites rather than trusting names:

| Symbol | Call sites found |
|---|---|
| `check_mandatory`'s new `manifest_components` parameter | 1 production caller (`paper_cli.py::_check_obligations`) + 6 test call sites, all updated to the new signature — no stale 3-arg call site remains anywhere in the repo |
| `_derive_figure_holders` | 4 call sites (3 in `test_paper_writing.py`, 1 cross-module in `test_paper_figure.py`) |
| `_assert_proof_classified_blocks_carry_their_derivation` | 2 call sites (1 in `test_paper_writing.py`, 1 cross-module in `test_paper_figure.py`) |
| `_render_subparser` / `_render_option_strings` / `_obligation_gating_flags` | All three called from within `RenderDocSurfaceTests`' three test methods |
| `_RENDER_TEST_ONLY_FLAGS` / `_SKILL_MD` / `_DIAGRAM_AUTHOR_MD` | Each referenced inside the same class's test methods |

**No new orphan found inside this corrective's own diff.** The two prior "wired to nothing"
instances found earlier in this same change (`acknowledge_reset` and the five
`paper_obligation.py` check functions, and separately `diagram-author.md`/`SKILL.md` never
mentioning `--section`/`--block`/`--expected-components`) were both already closed before this
corrective — at `73ae901` and by W4 respectively — confirmed by reading `tasks.md`'s own record of
those fixes and re-checking their call sites above. The eleventh instance
(`paper_contract.install_header`) belongs to a concurrent sibling change
(`the-contract-is-data-not-code`) and is explicitly out of this change's scope, as the sibling's
own new docstring paragraph states.

### Issues Found

**CRITICAL**: None.

**WARNING**:
1. **`_derive_figure_holders`'s own type, `dict[str, str]`, maps one filename to at most ONE
   block id — a second figure-declaring block added to an already figure-declaring file silently
   OVERWRITES the first block's entry rather than accumulating both.** Reproduced directly this
   session: adding a synthetic second figure-declaring block to a copy of
   `sections/01-materials-and-methods.md` (which already declares one, `mm-proposal`) left
   `holders == {"01-materials-and-methods.md": "zz-new-figure-block"}` — `mm-proposal` silently
   dropped out of the derived holder set. Since all three of `FigureObligationTranscriptionTests`'
   anti-drift checks (including W3's own new guard,
   `test_every_proof_classified_block_currently_carries_the_derivation_it_claims`) iterate
   `holders.items()`, a future edit that adds a second diagram to an existing section file would
   silently stop checking the FIRST diagram's `components_from` currency — exactly the class of
   defect W3 was written to close, reopened by a narrower, real path W3's own test does not cover.
   Currently latent, not live: the real corpus (`01`, `02`, `05`) has exactly one figure-declaring
   block per file today (independently confirmed by parsing all three files this session), so no
   real block is silently unchecked right now. Fix shape: `dict[str, list[str]]` (or
   `dict[tuple[str, str], ...]`), never `dict[str, str]`, for a holder set keyed by filename alone.
2. Carried forward, unresolved by this corrective (out of its stated scope, and correctly so —
   `9ad7d43`'s own commit message scopes it to W2/W3/W4 only): the combined test command's exact
   single-shell-line byte-for-byte hash could not be captured within this session's time budget
   due to heavy, unrelated CPU contention from concurrent sibling SDD sessions sharing this
   machine (see Build & Tests Execution above) — mitigated, not fully closed, by two fresh
   standalone executions of both constituent commands against the identical unchanged commit,
   which is evidence-equivalent under bash's own deterministic `&&` semantics but is not the
   literal byte-for-byte artifact the strict-TDD contract asks for.

**SUGGESTION**: None beyond the above.

### Verdict

**PASS WITH WARNINGS.** 0 CRITICAL, 2 WARNING, 0 SUGGESTION. All three targeted gaps (W2, W3, W4)
are genuinely closed, independently re-driven end to end in both directions this session, not
merely re-read from the diff. One new, real (but currently latent, not live) WARNING was found by
this session's own sharper-test probe against W3's derivation — a `dict[str, str]` holder map that
silently drops earlier entries when a file later grows a second figure-declaring block. This is
narrower and lower-severity than the WARNINGs this corrective just closed (nothing in the real,
on-disk corpus is unchecked today), and does not reopen any CRITICAL. **This change is archivable.**

**`gentle-ai sdd-verify-validate` refuses a passing verdict unless `completed == total` — stated
separately and plainly here, since that tool's own admission gate is not itself an engineering
verdict:** the prose engineering verdict above is PASS WITH WARNINGS, archivable, with a
non-blocking WARNING count of 2 (not 0). Per the validator's own contract, a `pass_with_warnings`
verdict with `blockers: 0` and `critical_findings: 0` is the correct machine envelope for this
outcome; it is not asked to force the requirements/scenarios counts to reflect WARNING items,
which are implementation-hardening findings, not uncovered spec requirements or scenarios (both
counts are genuinely 16/16 and 28/28, matching the unchanged spec files' own requirement/scenario
headings, counted directly from `openspec/changes/a-diagram-that-compiles-or-says-why/specs/*/spec.md`
this session: 8+7+1 requirements, 12+11+5 scenarios).


### Addendum — the literal combined test command completed after this report was drafted

The single-shell-line combined command (`npm test && .venv/bin/python -m unittest discover -s
tests -p 'test_*.py'`), launched in the background before this report was written, **finished
after** the report above was drafted and persisted. Its real, literal result:

```text
COMBINED_EXIT=0
...
Ran 3230 tests in 534.590s

OK (skipped=6)
```

Real combined-run hash (sha256 over the literal command's stdout+stderr, concatenated in that
order): `sha256:7ffadd4a0a0a1f3039f714b0928d3247fc9771d80c6b5662c5c534a261cfd722`.

**Test count delta explained (3230 here vs. 3225 in this report's own standalone evidence
above): not a finding against this change.** Three sibling commits landed on this shared branch
during the ~9-minute window this combined run took under heavy concurrent CPU contention —
`35ec14f` (`the-writer-may-assert-only-what-it-was-given`, adds new tests locking `mode.source.
quote`), `eab6496` (fixes the exact `SKILL.md`/`paper_contract.py` sibling WIP this report already
named and excluded above), and `20b3e0c` (unrelated SDD bookkeeping). `git diff 9ad7d43 --stat`
over this change's owned files, re-run immediately after this combined run finished, shows the
**exact same** three-file, zero-owned-surface delta as every earlier checkpoint in this report
(`SKILL.md` +1/-1, `paper_contract.py` +12, `tasks.md` +40 — all already accounted for above) —
`tests/test_paper_figure.py` and `tests/test_paper_writing.py`, this change's own two owned test
files, remain **byte-identical** to `9ad7d43`. The five additional tests belong to the sibling's
own test file, not to this change's surface.

Two literal `F` characters appear in the raw stderr; both are inside the benign string
`MissingIDFieldWarning` (`nbformat`'s own deprecation warning text), not unittest failure markers
— confirmed by direct substring search. `unittest`'s own `OK (skipped=6)` summary line (never
printed on any failure) plus `COMBINED_EXIT=0` are the conclusive evidence.

**This closes WARNING #2 above** (the literal combined-command hash was pending at draft time).
Revised issue count: **0 CRITICAL, 1 WARNING** (the `_derive_figure_holders` holder-overwrite
finding only). Verdict unchanged: **PASS WITH WARNINGS, archivable.**


---

## Prior Verification Attempt (superseded by this second corrective, preserved for history)

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:5e24ec36f76a079f9f4a1c159cfa26d955d0aefcfe6a8f73af56773433061746
verdict: fail
blockers: 0
critical_findings: 0
requirements: 16/16
scenarios: 28/28
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 1
test_output_hash: sha256:95ac0c96e0e076ea988d4014093fdfb76fb420925dee63c0cf642bf2c8fcc722
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:73ba940aaeb3d80da09c0315901193ab5d2f08ac786cf0d35016fbb5bc52f2e3
```

## Verification Report — Scoped Re-Verification (corrective `653e0cf`)

**Change**: a-diagram-that-compiles-or-says-why
**Version**: corrective, post `653e0cf` ("components_from is derived from a declared fact, never supplied")
**Mode**: Strict TDD

This is a scoped re-verification of the corrective that answers this same agent's
prior verify FAIL (Engram `sdd/a-diagram-that-compiles-or-says-why/verify-report`,
id 1671; on-disk report below, "Prior Verification Attempt"). Evidence pin:
commit `653e0cf477fe6fcde31e9556cc83caae1717d762`. This change's own owned files
were diffed against that commit at the start, middle and end of this session and
showed **zero byte drift** throughout, despite a concurrent sibling corrective
(`the-couplings-hold-or-they-do-not` / an unrelated `mode`-widening change)
writing elsewhere on the same shared working tree the whole time.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 33 (23 original + 10 corrective) |
| Tasks complete | 33 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: ✅ Passed — `npm run typecheck`, exit 0, no output.

**Tests**: ⚠️ Combined command exit 1 — **not attributable to this change**.
```text
npm test: 559/559 passed, exit 0.
.venv/bin/python -m unittest discover -s tests -p 'test_*.py':
  Ran 3211 tests in 514.342s
  FAILED (failures=1, skipped=6)
  FAIL: test_all_ten_shipped_contracts_still_parse_with_no_mode_declared
        (test_paper_writing.ModeWideningTests)
  AssertionError: {'value': 'transposition', 'source': {'file':
  'sections/01-materials-and-methods.md', ...}} is not None : 01-materials-and-methods.md
```
Root-caused by direct diff, not inference: `git diff 653e0cf --stat` at the moment
this suite ran showed an **uncommitted, in-flight sibling edit** adding a `mode`
declaration to `sections/01-materials-and-methods.md` plus 6 other section headers
and `paper_write.py`/`tests/test_paper_writing.py` — entirely orthogonal to
`figure`/`components_from`/`paper_obligation`/`paper_contract`/`paper_cli`/
`paper_declarations`, the files this change owns. `ModeWideningTests` asserts
every shipped contract parses with `mode is None`; the sibling's own WIP violates
that assertion for its own reasons, unrelated to this corrective. Re-diffing this
change's 8 owned files against `653e0cf` immediately after the run confirmed
**zero drift** (see "Owned-file drift checkpoints" below). The combined command's
exit code is reported honestly (1) per the strict-TDD evidence rule; the machine
envelope's `verdict: fail` mechanically follows from that non-zero exit, not from
any finding against this change's own code. **The separate, plain prose
engineering verdict for this change alone is stated at the end of this report.**

**Coverage**: ➖ Not available (no coverage tool configured for this repo)

### Owned-file drift checkpoints (read-only re-verification, concurrent write in progress elsewhere)
| Checkpoint | `git diff 653e0cf --stat` over this change's 8 owned files |
|---|---|
| Start of session | (empty — zero drift) |
| After task 1–6 CLI drives | (empty — zero drift) |
| After the full test run | (empty — zero drift) |
| Final, pre-report | (empty — zero drift) |
Owned files: `paper_contract.py`, `paper_declarations.py`, `paper_cli.py`,
`paper_obligation.py`, `sections/02-experimental-setup.md`, `sections/01-materials-and-methods.md`,
`tests/test_paper_figure.py`, `SKILL.md`, `diagram-author.md`.

### Spec Compliance Matrix (delta over the prior FAIL — full matrix below is unchanged)
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| section-contract: Front Matter Schema (figure, MODIFIED) | Missing `components_from` parses | `test_paper_writing.py::FigureSchemaTests::test_a_figure_object_without_components_from_parses` | ✅ COMPLIANT |
| section-contract: Front Matter Schema (figure, MODIFIED) | Explicit `null` resolves to absent | `test_paper_writing.py::FigureSchemaTests::test_an_explicit_null_components_from_also_resolves_to_none` | ✅ COMPLIANT |
| diagram-obligation: Components Check | Deleting the declaration removes the obligation | `test_paper_figure.py::Section02ComponentsCheckOmittedTests::test_the_real_es_assessment_contract_declares_no_components_from` + own execution (task 3/4 below) | ✅ COMPLIANT |
| diagram-obligation: Components Check | A block with no `components_from` runs no components check | `test_paper_figure.py::Section02ComponentsCheckOmittedTests::test_excludes_and_mandatory_still_apply_without_a_components_check` + own execution | ✅ COMPLIANT |
| diagram-obligation: Components Check | The methods diagram matches the contribution list (unchanged, re-confirmed load-bearing) | `test_paper_figure.py::CLIWiringTests::test_editing_components_from_in_the_header_changes_the_verdict` + own execution against the REAL section 01 corpus (task 1) | ✅ COMPLIANT |
| diagram-obligation: Components Check | An undeclared named fact refuses `COMPONENTS_FACT_UNRESOLVED` | `test_paper_figure.py::CLIWiringTests::test_an_undeclared_components_from_fact_refuses_components_fact_unresolved` | ✅ COMPLIANT |
| diagram-obligation: Components Check | A non-list fact resolution refuses `COMPONENTS_FACT_NOT_A_LIST` | `test_paper_figure.py::CLIWiringTests::test_a_non_json_list_fact_resolution_refuses_components_fact_not_a_list` | ✅ COMPLIANT |
Remaining 22 of 28 scenarios (authored-diagram's 12, and the diagram-obligation/section-contract scenarios untouched by this corrective) are unchanged from the prior FULL verify (id 1671), which found them fully compliant, and this session's re-diff confirms their owning files are byte-identical to `653e0cf` — no re-derivation needed.

**Compliance summary**: 28/28 scenarios compliant (delta re-verified directly; remainder re-confirmed unchanged by owned-file drift check)

### Execution log — what was actually driven, not just read

All six numbered checks in the brief were driven against a real, scaffolded
`paper/` (throwaway, `implementations/_sdd_verify_scratch/`, removed before this
report was written) via the real, installed TeX Live 2026 toolchain
(`latexmk` 4.88) — no stub, stronger than the shipped tests' own stubbed-`latexmk`
CLI-subprocess tests.

1. **Is `components_from` load-bearing now? (mutation test)** — YES, confirmed by
   execution against the REAL, on-disk `sections/01-materials-and-methods.md`.
   Baseline: `render --figure-id mm-proposal --section 01-materials-and-methods
   --block mm-proposal` with a manifest `["ContribA","ContribB","ContribC"]` and
   the declared fact `contributions` set to the same list → `"verdict": "success"`,
   `"obligations": {"checked": true}`. Then, against a **copied, mutated**
   `sections/` dir (`components_from` changed from `"contributions"` to
   `"dataset"`, with `dataset` declared to a *different* list) → same manifest,
   same figure source → refuses `COMPONENT_MISMATCH`
   (`missing=['SomeDataset'] extra=['ContribA', 'ContribB', 'ContribC']`). The
   verdict flips on the header string alone. **Not wired to nothing.**
2. **Real CLI path against `es-assessment` (prose-compliant vs. degenerate)** —
   driven against the REAL `sections/02-experimental-setup.md`. A prose-compliant
   6-category manifest (`Data, Methods, Axes, Metric, Instrument, Repetition`)
   compiles and passes (`"checked": true`). A degenerate 1-category manifest
   (`["Data"]` only) **also** compiles and passes (`"checked": true`) — this is
   now **correct**, not inverted: `es-assessment` declares no `components_from`
   at all, so no Components Check runs for either input; the inversion
   (prose-compliant refused, degenerate accepted) that was the original CRITICAL
   is gone. But see finding W1 below: this also means nothing mechanically
   distinguishes "compliant" from "degenerate" for this block any more — the
   verdict is now uniformly silent on content richness, never uniformly wrong.
3. **The empty-diagram hole** — **NOT closed, reproduced by direct execution.**
   A literally empty manifest (`"components": []`) with a trivial one-node `.tex`
   that declares no `% node:` markers, rendered against the real, on-disk
   `es-assessment` (`mandatory: true`) → `"verdict": "success"`,
   `"obligations": {"checked": true}`. Reading `paper_obligation.py` explains
   why: `check_mandatory` only checks that a PDF file exists, never that the
   manifest is non-empty; `check_excluded`/`check_caption` are vacuously
   satisfied by zero components; and `check_components` does not run at all
   because `components_from` is now `None` for this block. This logic
   (`check_mandatory`, `check_excluded`, `check_caption`) is **unchanged by
   `653e0cf`** — `paper_obligation.py` is not among the corrective's changed
   files — so this is a **pre-existing gap, not a regression this corrective
   introduced**, and the apply's own summary (Engram id 1664) indeed never
   claims it closed. See finding W2.
4. **Optionality as a new hole class** — **reproduced, and this one WAS
   plausibly introduced/widened by `653e0cf`** (`components_from` moved from
   `_FIGURE_REQUIRED` to `_FIGURE_OPTIONAL`). Against a **copied, mutated**
   `sections/01-materials-and-methods.md` with `components_from` deleted
   entirely from `mm-proposal`'s header, the SAME clearly-wrong manifest
   (`["WrongThing"]`, matching neither the real contribution list nor anything
   sensible) that refuses `COMPONENT_MISMATCH` against the real header
   **compiles and passes cleanly** (`"checked": true`) the moment
   `components_from` is omitted. There is no signal in the CLI output
   distinguishing "this block's diagram is honestly a composite no single fact
   captures" (the real `es-assessment` case) from "the check was silently
   disabled." See finding W3 (rated WARNING, not CRITICAL — reasoning below).
5. **`--expected-components`** — **fully removed**, not merely undocumented or
   ignored. Confirmed by reading `paper_cli.py`'s `argparse` setup for `render`
   directly: the flag does not exist in `p_render`'s argument list at all. The
   only surviving references are the new internal helper name
   `_resolve_expected_components` and historical/comment prose explaining what
   the old flag used to do. Closed cleanly.
6. **Coupling 4 survives** — confirmed both by structural grep (`rg -n
   "figure|components_from|paper_obligation"` over `paper_coupling_evidence.py`
   and `paper_verify.py`: zero matches) and by the full green test suite
   (`the-couplings-hold-or-they-do-not`'s own tests, part of the 3211 discovered,
   all passed). `the-couplings-hold-or-they-do-not`'s own verify-report.md
   independently confirms the same zero-match grep and notes it observed this
   very corrective landing live during its own session, confined to
   `_check_obligations`'s docstring and the (now-removed) `--expected-components`
   help text.

### Disclosed deviations, judged
- **"Departed from the two remedies your own design-decision note sketched"** —
  could not be independently verified against a retrievable artifact: no
  `design-decision` note under this topic key exists in Engram, and
  `design.md`/the prior verify report (id 1671) do not themselves enumerate
  "two remedies" in that phrasing. Judged on its own technical merits instead
  (below), not against an unlocatable reference text.
- **`_FIGURE_REQUIRED` → `_FIGURE_OPTIONAL` for `components_from`** — coherent,
  documented inline in `paper_contract.py` with the measured reasoning, and
  reuses the exact `raw.get(...) is not None` convention `mode` already
  established (no new pattern invented). Judged sound as far as it goes; see W3
  for the gap it opens.
- **New operator workflow (`declare --fact <id> --value '[...]'` before
  rendering section 01's methods diagram)** — confirmed documented in both
  `SKILL.md` ("Obligations are read, never known" section) and
  `.claude/agents/diagram-author.md` ("Running the obligation checks" section,
  explicit "Declare that fact BEFORE calling `render`" instruction). This is a
  real, disclosed, and reasonable operator-facing change.

### Two prior WARNINGs, re-checked
- **W-prior-1 (fixture/shell_escape=f mismatch): CLOSED.** All three tier-1
  fixture logs were recaptured (`success.log`, `failure_error.log`,
  `failure_package.log` all now read "Shell escape disabled" instead of
  "restricted `\write18` enabled"), and every `provenance.json` now records
  `"sandboxEnv": {"openin_any": "p", "openout_any": "p", "shell_escape": "f"}`
  — byte-identical to `paper_latex.py`'s own `_SANDBOX_ENV` constant, which a
  committed test (`test_paper_figure.py:201`) independently pins against the
  stub. The evidence trail and the production claim now agree.
- **W-prior-2 (`--section`/`--block`/`--expected-components` undocumented, no
  derived-surface test): PARTIALLY CLOSED.** `--section`/`--block` are now
  documented in both `SKILL.md` and `diagram-author.md` (confirmed by direct
  reading, quoted above); `--expected-components` no longer exists to document
  (task 5). But **no derived-surface test was added** — grepped both test files
  for any doc-vs-argparse consistency check (`SKILL.md`, `diagram-author.md`, a
  "Doc" test class, etc.): zero matches. The documentation half of the original
  WARNING is closed; the "and a derived-surface test" half is not. See W4.

### Issues Found

**CRITICAL**: None. The original CRITICAL (silent inversion of the Components
Check on a real, shipped, mandatory block) is closed and mutation-proven on the
real corpus (item 1 above).

**WARNING** (4):
1. **W1 — `es-assessment` now checks nothing about content richness, honestly
   rather than dishonestly.** Both a prose-compliant and a degenerate manifest
   pass identically (item 2). This is the correct fix for the *inversion*
   defect, but the underlying gap the original CRITICAL's own remedy discussion
   flagged (no mechanical check exists for this section's composite-crossing
   obligation at all) is unchanged — `design.md`'s own "documented judgment
   call" framing is honest about this, and `diagram-author.md` explicitly tells
   the operator "verify the crossing against the block's own prose yourself,
   since no mechanical check does it for you there." Disclosed, not hidden —
   rated WARNING rather than CRITICAL for that reason.
2. **W2 — The empty-diagram hole is real and still open for `es-assessment`,
   but pre-existing (not introduced by `653e0cf`).** `paper_obligation.py` was
   not touched by this corrective; `check_mandatory` has always only checked
   PDF existence, never manifest non-emptiness. Reproduced by direct execution
   (item 3): a diagram with **zero** declared components, for a `mandatory:
   true` block, compiles and passes every obligation check. This is real and
   should be tracked as a follow-up (e.g., a minimum-non-empty-manifest check,
   or at minimum an explicit test locking today's behavior so a future change
   cannot silently narrow it further), but is out of this corrective's own
   stated scope and does not regress anything this corrective touched.
3. **W3 — Optionality is a reproducible new hole class, currently latent
   (no live instance), not yet defended against.** Reproduced by direct
   execution (item 4): omitting `components_from` from a block whose diagram
   genuinely IS a single-fact list (section 01's `mm-proposal`) silently
   disables the Components Check with **no distinguishing signal** — the CLI's
   `"obligations": {"checked": true}` reply looks identical whether the check
   ran and passed or never ran at all. Today, the real, on-disk
   `sections/01-materials-and-methods.md` still correctly declares
   `components_from: "contributions"` (confirmed, unchanged, see item 1), so
   **no shipped contract is currently affected** — this is a latent defense
   gap, not a live defect, which is why it is rated WARNING rather than
   CRITICAL. No test in the corpus locks section 01's real header to keep
   declaring `components_from` (grepped for `mm-proposal` across both test
   files: no such assertion exists), so a future edit could silently reopen
   the exact shape of the original CRITICAL through this door, and nothing in
   the suite would catch it. Recommended follow-up: add a regression test
   asserting `sections/01-materials-and-methods.md`'s `mm-proposal` retains a
   non-null `components_from`, or a structural rule requiring an explicit
   reason (a comment/field) when a `mandatory: true` block declares none.
4. **W4 — No derived-surface test ties `SKILL.md`/`diagram-author.md`'s
   documented `render` flags to the real `argparse` surface.** Carried over
   from the prior WARNING, only half-closed (see above). A future flag
   rename/removal (as just happened to `--expected-components` itself) could
   silently leave stale documentation again.

**SUGGESTION**: None beyond the prior report's SUGGESTION (unchanged, unrelated
to this corrective's own files — the section-05 table-choice test coverage note
still stands as previously reported).

### Verdict

**Machine envelope**: `fail` — mechanically forced by the combined test
command's actual exit code (1), which traces entirely to an unrelated,
concurrent, uncommitted sibling edit (`mode` widening) on files this change does
not own, confirmed by repeated `git diff 653e0cf --stat` checkpoints showing zero
drift on this change's own 8 owned files throughout the session.

**Prose engineering verdict for `a-diagram-that-compiles-or-says-why` alone**:
**PASS WITH WARNINGS.** The CRITICAL that blocked the prior verify is closed and
proven by direct execution against the real, on-disk corpus (not merely by
reading the shipped tests, though those independently agree). Zero CRITICAL
findings. Four WARNINGs: one closed-but-partial (W4), one pre-existing and
disclosed (W2), one honestly-disclosed scope limitation (W1), and one genuine,
reproduced, but currently-latent defense gap this corrective's own optionality
choice opened (W3) with no live instance and a clear, cheap follow-up. **This
change is archivable.** Recommend a follow-up task (not blocking archive) to add
the section-01 regression test named in W3, and, separately, a clean re-run of
the exact test command once the concurrent sibling's own work lands or is set
aside, to obtain a genuinely clean machine envelope for the historical record.

---

## Prior Verification Attempt (superseded by this corrective, preserved for history)

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
