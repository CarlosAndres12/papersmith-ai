# Tasks: The Couplings Hold Or They Do Not

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1500–2500 (2 new modules ~600–800, CLI+SKILL.md ~100, tests+fixtures ~900–1500 for 9 mutations) |
| 400-line budget risk | High |
| Session review budget | 1400 lines (per preflight, overrides the skill's default 400) |
| Chained PRs recommended | Yes |
| Suggested split | Unit 1 → Unit 2 → Unit 3 (stacked) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Evidence I/O, record grammar, report shape, read-only lock, M6/M8 | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing.EvidenceTests tests.test_paper_writing.ReportShapeTests tests.test_paper_writing.ReadOnlyTests -v` | `paper_cli.py verify` not yet wired; run `paper_evidence.gather()`/`paper_verify.run()` directly against a minimal fixture skeleton | Revert `paper_evidence.py`, `paper_verify.py` skeleton, new test classes, fixture skeleton; existing four verbs untouched |
| 2 | Checks 1, 2, A + fixture extension | PR 2 | `.venv/bin/python -m unittest tests.test_paper_writing.CouplingOneTests tests.test_paper_writing.CouplingTwoTests tests.test_paper_writing.CitationTests -v` | Same direct-call harness, extended fixture | Revert checks 1/2/A + their fixture rows; Unit 1 unaffected |
| 3 | Checks 3, 4, 5, B; `verify` CLI wiring; roster proof; SKILL.md; spec fix | PR 3 | `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py verify --paper tests/fixtures/paper-verify` | Revert checks 3/4/5/B, `cmd_verify` registration, SKILL.md row, spec wording; CLI reverts to today's four verbs |

## Phase 1: Evidence, Record Grammar, Report Shape, Read-Only Proof (Unit 1)

- [x] 1.1 Create `paper_evidence.py`: `Evidence` dataclass + `gather()`; all disk reads isolated here only. **Deviation, measured**: `paper_evidence.py` was already taken on disk by `no-claim-without-a-source-that-holds-it`'s own claim<->source module before this apply began; shipped as `paper_coupling_evidence.py` instead, with the collision documented in both modules' docstrings.
- [x] 1.2 Parse `paper/couplings.json` (declaration record) and `%% paper-writing provenance` region (disjoint prefix from `paper_block.MARKER_PREFIX`), read-only.
- [x] 1.3 RED: M6 — empty/absent declaration record → run-level `Refused("DECLARATION_RECORD_ABSENT")`, exit 2, nothing written.
- [x] 1.4 GREEN: implement 1.3.
- [x] 1.5 RED: M7 — absent provenance → check B alone `unmeasured` reason `CONTRACT_RECORD_ABSENT`, run exits 0, per design.md's narrowing. Reconciled in 3.13.
- [x] 1.6 GREEN: implement 1.5.
- [x] 1.7 Derive `requires_facts` block set per check via `paper_contract.parse` over `sections/*.md` headers only, never a record fallback; empty/unreadable → `unmeasured` (`NO_BLOCK_REQUIRES_FACT` / `SECTION_CONTRACTS_UNREADABLE`).
- [x] 1.8 Create `paper_verify.py`: `CHECKS`, `UNMEASURED_REASONS` closed rosters; report-object shape (`sides` typed `derived`/`declared`, `limits`, `unmeasured_reason`).
- [x] 1.9 RED/GREEN: report carries exactly one object per `CHECKS` member both directions; `holds+fails+unmeasured == len(CHECKS)`; `unmeasured` never counted in `holds`.
- [x] 1.10 AST lock over `paper_coupling_evidence.py` and `paper_verify.py`: no write-mode `open`, no `write_bytes`/`write_text`/`mkdir`/`unlink`/`replace`/`rename`/`shutil`/`tempfile`, no reference to `paper_block.substitute`/`open_block`.
- [x] 1.11 Content-manifest test: sha256 of the full fixture tree before/after a real `gather()`+`run()` call, equal — never `git status` (`paper/*` is gitignored).
- [x] 1.12 M8: mutate `paper_verify.py` to write one byte; observe 1.11 go red under `_run_against_mutant`; confirm the mutant fails; production file unchanged.

**Measured deviation (`ModuleCompletenessTests`)**: `paper_cli.py`'s own module-level imports for both new scripts landed in Unit 1's commit, not Unit 3's — `ModuleCompletenessTests` (already on disk, unrelated to this change) requires every `.py` file under `scripts/` to be imported by `paper_cli.py` the moment it exists, the same shape already established for `paper_region.py`/`paper_obligation.py`. `DECLARATION_RECORD_ABSENT` is therefore reachable and classified from Unit 1 onward (roster count 93 → 94); `cmd_verify`/`COMMANDS`/`_COMMANDS` wiring itself still waits for Unit 3 (3.8).

## Phase 2: Checks 1, 2, A (Unit 2)

- [x] 2.1 Check 1 `contribution-list`: declared `facts.contributions` vs each dependent block's first-literal-occurrence order; declared-name literal-presence limit stated in payload.
- [x] 2.2 RED/GREEN M1: reordered names → `fails`.
- [x] 2.3 Check 2 `chain`: literal token identity per link + set closure against check 1's document-bound contribution set.
- [x] 2.4 RED/GREEN M2: non-substring synonym at one link → `fails`.
- [x] 2.5 Check A `citations`: two-way `\cite`/`refs.bib` set, both sides derived, no declaration.
- [x] 2.6 RED/GREEN M3a (dangling cite → `fails`) and M3b (orphan entry → reported, `pass` unchanged) as two independent mutations.
- [x] 2.7 Fully-declared green fixture covering checks 1, 2, A. **Deviation, measured**: built as a programmatic fixture builder (`_build_coupling_paper`, `tests/test_paper_writing.py`) driving real `scaffold`/`open`/`substitute --contract` calls, rather than a static `tests/fixtures/paper-verify/` tree — `main.tex`'s marker digests and the `provenance` region's `contract_sha256` must be genuine, and hand-computing sha256 for a multi-block static fixture would drift the moment any block body changed. Matches this file's own pre-existing `_marker_pair`/`_write_fixture` convention.

## Phase 3: Checks 3, 4, 5, B; CLI wiring; roster proof (Unit 3)

- [x] 3.1 Check 3 `gap` (assisted): mechanical sub-checks (both closings present, fronts equal/count), reading sub-check fixed at `unmeasured`/`ASSISTED_READING_REQUIRED`; publish both texts+fronts verbatim; never gated.
- [x] 3.2 Check 4 `artefacts`: methods side derived from check 1's contribution set (never redeclared); results cells vs declared setup cells.
- [x] 3.3 RED/GREEN M4a (undeclared cell → `fails`) and M4b (contribution added to setup cells → `fails` on non-empty intersection).
- [x] 3.4 Check 5 `future-work`: totality + citation-key mechanical; relevance/specificity `out-of-reach`/`unmeasured`, never attempted.
- [x] 3.5 RED/GREEN M5: direction answering no limitation → totality `fails`.
- [x] 3.6 Check B `contract-currency`: per-block provenance hash vs current whole-file contract sha256; one edited block flags its whole section stale. **Measured, not assumed**: `the-paper-carries-its-own-decisions`'s `provenance` region and `paper_provenance.py` (`read_provenance`/`drift`) had already landed on disk by the time this apply ran — reused directly rather than re-implemented; check B produces real `pass`/`fail` verdicts when a paper has been written with `--contract`, not only `unmeasured`.
- [x] 3.7 Confirmed the sibling apply's import-derived `reachable_paper_refusal_codes()`/`paper_cli_imported_modules()` had landed — depended on it, did not re-implement. The `import paper_coupling_evidence`/`import paper_verify` step itself moved to Unit 1 (see above); this task's own dependency note ("do not proceed with 3.7–3.9 until confirmed on disk") was satisfied before Unit 1 started.
- [x] 3.8 Registered `cmd_verify` in `paper_cli.py`: added to `COMMANDS`/`_COMMANDS`/argparse; `DECLARATION_RECORD_ABSENT` (`WORK_STATE`) was already in `REFUSAL_CLASSIFICATION` since Unit 1; reachability asserted via the derived walk (94/94, no missing, no extra).
- [x] 3.9 M9: added one throwaway `Refused` to `paper_verify.py` by hand, observed `RefusalRosterTests.test_every_reachable_refusal_is_classified` go red, removed it, confirmed green — proven both directions during this apply, not shipped as an automated mutation test. **Measured**: `_run_against_mutant` (used for M8) cannot prove this one — `reachable_paper_refusal_codes()` reads each imported module's own bytes from a fixed real path (`SKILL_SCRIPTS / f"{name}.py"`), never through `import`/`sys.modules`, so a `sys.modules`-substituted mutant is invisible to it. `CouplingVerifyCLITests.test_mutation_9_...` instead asserts the static precondition (`paper_verify.py` is a member of the whole-module scan set) and documents the by-hand proof in its own docstring, the same shape `ModuleCompletenessTests`'s own docstring already established for an analogous case.
- [x] 3.10 Extended the fixture for checks 3, 4, 5, B; ran the unmutated pass (green on every mechanical check, `unmeasured` on `gap`) and M1–M7 — M1–M6 as direct pure-function mutations against a hand-modified `Evidence`/record (`dataclasses.replace`), M7 and the full unmutated pass additionally through the real `verify` CLI subprocess (`CouplingVerifyCLITests`).
- [x] 3.11 Updated `SKILL.md`: the `verify` verb row (sixteenth verb, not fifth — fifteen already shipped), the three-value verdict vocabulary, decision gates, and the frontmatter trigger description.
- [x] 3.12 Forge leak guard: `paper_coupling_evidence.py`/`paper_verify.py`/`SKILL.md` are covered automatically by the existing `VocabularyLeakTests` (`tests/test_paper_contract.py`, whole-skill-directory scan); the fixture data (not a `tests/fixtures/` directory — see 2.7's deviation) is covered by a new `CouplingFixtureLeakTests`. Both pass.
- [x] 3.13 Reconciled `specs/contract-currency/spec.md`'s M7 scenario text ("exits non-zero") to match design.md's decision (exit 0, check-B-only `unmeasured`, every other check still reports). **Also reconciled, measured beyond this task's original scope**: `specs/coupling-verification/spec.md`'s "Declaration Record Presence Gates The Run" requirement and Purpose section referenced a `%% paper-writing declarations` region / `paper-declarations, Phase 3` — design.md's own decision reads `paper/couplings.json` instead (a rejected-options table already reasoned through this); the spec wording was stale relative to the design it was meant to describe, not a second real conflict.

## Notes from apply

- The `openspec/changes/*` planning directories in this repository are untracked working files (confirmed via `git ls-files`); this apply's spec-wording reconciliations above are left on disk, uncommitted — archival/commit of that directory is `sdd-archive`'s job, not `sdd-apply`'s, matching how every other currently-in-flight sibling change's own `openspec/changes/` directory is also untracked right now.
- A sibling verify's finding (`sections/02-experimental-setup.md` declaring `figure.components_from: "dataset"`, inverting `paper_obligation`'s own crossing-manifest check) does not reach this change: `paper_coupling_evidence.py`/`paper_verify.py` never read `figure`/`components_from`/`paper_obligation` at all (checked by grep, zero matches), and this change's own fixture never touches the real `sections/` corpus.

## Dependencies and Sequencing Notes

- Unit 3 depends on the sibling apply landing the import-derived `reachable_paper_refusal_codes()` walk (task 3.7) — do not proceed with 3.7–3.9 until confirmed on disk.
- Check B (task 3.6) reads an interface (`the-paper-carries-its-own-decisions`) that has not landed; ships refusing/unmeasured by design, not blocked on it.
- `paper_cli.py`'s existing four verbs are untouched until Unit 3's 3.8 — Units 1–2 ship dead code invisibly, by design, keeping each unit independently revertible.
