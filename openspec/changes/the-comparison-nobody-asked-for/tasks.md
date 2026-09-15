# Tasks: the-comparison-nobody-asked-for

> **Size note.** The `sdd-tasks` skill sets a 530-word default budget. The owner's
> binding directives for this change — full coverage with nothing pending, explicit
> no-regression verification rather than a note pointing at existing tests, and
> chained units rather than reduced coverage against a ~5220-line grand-total
> forecast (design revision 5, Movement 6 included) on a 1400-line budget — cannot
> be satisfied inside it. The same explicit-contract override the proposal and
> design took applies here.

**Ordering.** Units are numbered as the design names them (`1`, `2`, `4`, `4b`, `3`,
`6c`, `6a`, `6b`) so every cross-reference to the design and specs stays stable.
They are **presented and MUST be delivered in execution order:
1 → 2 → 4 → 4b → 3 → 6c → 6a → 6b.** Units 1–3 are applied and green
(`b493151` → `432da9f` → `45eae9d` → `cb965c4` → `330c5f1`); Movement 6 (`6c`,
`6a`, `6b`) is designed against **what that shipped code now is** (design §D17),
not against earlier design prose.

**Threat matrix: N/A** (design §9). No routing of untrusted input, shell command,
subprocess, VCS/PR automation, executable-file classification, or process
boundary is introduced or widened. No threat-matrix RED tasks apply.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | Units 1–3: ~3220 forecast, **~3990 actual** (400 + 750 + 560 + 1805 + 837 — 4b landed 2.5×, 3 landed 1.05×; see each unit's own "reported" section). Movement 6 (design §3c revision 5): **~2000 forecast, treated as a floor, not an estimate** — 6c ~300, 6a ~1000, 6b ~700. **Grand total forecast: ~5220** |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Unit 1) → PR 2 (Unit 2) → PR 3 (Unit 4) → PR 4 (Unit 4b) → PR 5 (Unit 3) → PR 6 (Unit 6c) → PR 7 (Unit 6a) → PR 8 (Unit 6b) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — user decision required before apply |

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High
```

### Suggested Work Units

| PR | Unit | Goal | Forecast | Focused test command | Runtime harness | Rollback boundary |
|----|------|------|----------|----------------------|-----------------|-------------------|
| 1 | Unit 1 — seal leaves the benchmark package | Relocate `report_digest.py`; rewrite `materialize.py` as one loop (D9); triage `test_remote_execution.py` | ~400 | `pytest tests/test_proposal_implementation.py -k "report_digest or scaffold_destinations or materialize"` | Scaffold a fresh target, run `verification.ipynb`, confirm the stamp | Revert restores the old path; idempotent scaffold rerun recovers; seal is kit-sourced, no data loss |
| 2 | Unit 2 — declaration leaves the benchmark package | `__implementation__`, `__levels__/__steps__/__records__` relocation (D1/D2); `cmd_verify`'s two revision readers (D3); migration path | ~750 | `pytest tests/test_proposal_implementation.py -k "declaration or verify or migration"` | `cmd_verify` against a migration-shaped fixture carrying an unread literal | Revert restores bench-package read; gate refuses loudly (`OBJECT_MAP_NOT_APPROVED`), never a silent pass |
| 3 | Unit 4 — a declined comparison is remembered | Question-text constructor (D5a), `declined` terminal, `_Benchmark` exclusion, `decisions.comparison` | ~560 | `pytest tests/test_proposal_implementation.py -k "discuss or declined or previous_implementations"` | `cmd_probe` twice: decline, then re-probe; assert settled-declined | Purely additive; revert loses only the bucket read, ledger event persists |
| 4 | Unit 4b — the acid test | `validation_proposal` (D11) with its `placement` section (D11a–d), `validate` rung (D12), canonical `premises` key (D14/D14a), D15 invariant proved local **and** remote | ~720 | `pytest tests/test_proposal_implementation.py -k "validat or PROBE_DRAFTS or NextStep or placement"` | `cmd_probe` → accept acid test → `cmd_step` wiring + running it, once local, once remote (job-folder generation via `remote_cli generate-job`) | Purely additive; D15a+D15b guarantee no on-disk residue under either placement — revert unwinds a rung, never a directory |
| 5 | Unit 3 — first flow stops creating the benchmark package | Scaffold/harness list flip; `declare-first` narrows (D4); derived-count sweep (D8); doc sweep close-out | ~800 (actual: 837) | `pytest tests/test_proposal_implementation.py` (full) + both seal suites | Full Flow A on a fresh target, E2E | Only unit changing Flow A's on-disk output; revert restores the scaffold list; Units 1/2/4/4b stay correct without it |
| 6 | Unit 6c — the anti-leak lock (Movement 6, Part C) | Derive the compound target-name as its own denylist word (D24); `re.IGNORECASE` in `leaks()`; widen the guard's scan to test commentary; reword the one live instance | ~300 (floor) | `pytest tests/test_implementation_domain_lock.py -k "leak or denylist or compound"` | N/A — no engine/CLI behavior; a test-suite-internal guard fix, no runtime scenario to exercise | Purely additive to the test suite; revert restores the narrower guard and the un-reworded fixture comment, no production code touched |
| 7 | Unit 6a — a decision can be reopened (Movement 6, Part A) | `discuss --decision yes\|no` token (D19); absent-token-reads-as-`no` migration (D20); `build-first` rung as a fourth arm inside Unit 3's existing branch (D21) | ~1000 (floor) | `pytest tests/test_proposal_implementation.py -k "discuss_decision or build_first or DeclinedComparison"` | `cmd_probe` → decline → re-`discuss --decision yes` → confirm `build-first` reported with nothing yet built | Purely additive to `discuss`; `cmd_offer` untouched; revert restores the three-way branch, no ladder position changes |
| 8 | Unit 6b — the transitions (Movement 6, Part B) | Comparison→test reuses D19's token (D22, no new machinery); test→comparison reachability + reporting-state publication (D23a/b); undeclare-not-delete (D23c) | ~700 (floor) | `pytest tests/test_proposal_implementation.py -k "transition or undeclare or already_benchmarked_validate"` | `cmd_probe` on an already-benchmarked target → discuss the acid-test transition → confirm rival arm undeclared, `Results/` untouched | Purely additive; revert leaves both transitions unreachable again, no prior unit's on-disk output affected |

---

## Unit 1 — The seal leaves the benchmark package

- [x] 1.1 RED: add a failing test asserting `report_digest._here()` resolves the repo root correctly for a file at `src/<P>/report_digest.py` (today's code assumes the `_Benchmark` suffix).
  - *Measured: `_here()`'s `package_dir.parents[1]` is already correct at the new depth before any edit (D7's own finding — "verified by reading, not assumed"), and `.removesuffix("_Benchmark")` is a no-op on a plain package name, so no behavioural RED was reachable here. `ReportDigestHereRelocationTests` pins the post-relocation behaviour; the genuine RED/GREEN pair is `KitSurfaceLanguageTests.test_the_translation_touched_no_code`, pinned to `_here()`'s own source text, which fails until 1.2's suffix-strip removal lands.*
- [x] 1.2 Simplify `_here()` to `return package_dir.parents[1], package_dir.name` (D7); rewrite its three docstring paragraphs that assert the old location.
- [x] 1.3 Relocate the `report_digest.py` entry in `scaffold_destinations()` and `scaffold_kit_source()` from `src/<P>_Benchmark/` to `src/<P>/`; confirm `KIT_SEAL` (the kit **source**) is unaffected — only the destination mapping moves.
- [x] 1.4 Update `assets/kit/nb/verification.ipynb` and `assets/kit/nb/probe.ipynb`'s import line to `from {{PKG}} import report_digest`; leave `probe.ipynb`'s `HARNESS` path untouched.
- [x] 1.5 Rewrite `scripts/materialize.py`: replace its three imperative sites with one loop over `scaffold_destinations(name)` + `scaffold_kit_source(...)` + `authored_package_init(name)` (D9). Preserve the `writable_at_scaffold_time` filter on `tests/*.py`; resolve kit sources under the caller-supplied `KIT` argument, never `SKILL_ROOT` — `experimental-implementation` ships no kit and must not gain the forge's own fixture content.
  - *Note: the owner has ruled — `materialize.py` is rewritten (D9's loop), not deleted. Unit 1 shipped this (commit `b493151`). The in-flight change `the-skill-materializes-not-the-agent`'s tasks 4.4/4.5 proposed deletion instead; that proposal did not prevail here and needs no further tracking in this file.*
- [x] 1.6 Test: `materialize.py` writes exactly `scaffold_destinations(name)` — agreement holds when both sites update together, fails and names the divergent list when only one does (spec "Both Scaffold Mappings Agree").
- [x] 1.7 Test: `verification.ipynb` executes and stamps at the new path; stamped content for identical proof inputs is unchanged before/after relocation (spec "First Flow's Verification Notebook Stamps Unaffected").
  - *Satisfied by the existing `NotebookSealAgreementTests` class (already runs the notebook's own cells and compares the stamp to `impl.source_digest`), corrected at its one hardcoded import-module assertion; no new test needed once that assertion named the relocated package.*
- [x] 1.8 Test: a hand-edited `src/<P>/report_digest.py` after materialization reports `SCAFFOLD_DRIFT` at the new location (spec "Materialization Receipt Machinery...", scenario 1).
- [x] 1.9 Discovery task: triage every one of the 123 `_Benchmark` hits in `tests/test_remote_execution.py` — classify each as generic job-folder fixture (no change) or contract-bearing (update). Apply edits to contract-bearing hits found. The unit does not close until every hit is classified.
  - *All 123 hits are the literal string `FEM_TOLLA_Benchmark`: 121 are generic job-folder fixture data (`clonePaths`/`run.module`/`harness.py`, unrelated to `report_digest.py` or `materialize.py`), 2 are `RealDigestLoaderTests` calling the KIT-SOURCE loader (`assets/kit/nb/report_digest.py`, unmoved by D7), and 1 is historical docstring prose about a past production incident. Zero are contract-bearing relative to Unit 1's scope; `harness_destinations()` never included `report_digest.py`. No edits required.*
- [x] 1.10 Update `SKILL.md` step 5's scaffold-file-list table row and `references/usage.md`'s worked scaffold-file-list example to the new path.
- [x] 1.11 Update `README.md`'s kit-source table entry and `src/` tree drawing for the relocated `report_digest.py` (not in the proposal's original Affected Areas — added by design).
  - *Investigated: README.md's kit-source table row for `assets/kit/nb/report_digest.py` (line 1036) never states a destination path, and its `src/` tree drawing is coarse (does not itemize individual scaffold files). Neither location asserts anything D7 makes false. No textual edit was needed; recorded here rather than silently skipped.*
- [x] 1.12 Regenerate `tests/seal/corpus.py` and `tests/experiments_seal/corpus.py`; read the diff and confirm which cases moved; account for every moved case.
  - *`corpus.py` itself needed no code change (neither fixture ever wrote a `report_digest.py`, so the case bodies were already location-agnostic). Regenerated goldens via `seal_capture.py`/`experiments_seal_capture.py`: `tests/seal/digests.json` moved exactly 6 cases (`materialize`, `plan-a`, `plan-b`, `verify-a`, `verify-b`, `verify-t`), `tests/experiments_seal/digests.json` moved exactly 9 comparison cases plus the excluded-from-comparison `propose` entry. Every moved case's raw output was inspected directly; the only byte difference in each is `src/<Pkg>_Benchmark/report_digest.py` -> `src/<Pkg>/report_digest.py`.*
- [x] 1.13 Run both suites (`npm test` and the Python unittest suites — this repository has two) green before closing the unit.

## Unit 2 — The declaration leaves the benchmark package

- [x] 2.1 Add `IMPLEMENTATION_DECLARATION = "__implementation__"`, `IMPLEMENTATION_BLOCKS = {"revision": "", "premises": {}}`, `resolve_implementation_declaration(target, name)` returning the same `{status, path, detail, contract}` quadruple and `absent`/`undeclared`/`declared` vocabulary as the benchmark resolver (D1). Generalize `_declaration_is_blank` over a blocks mapping rather than an eighth hardcoded shape.
- [x] 2.2 Add `declaration_root(target, name) -> target / "src" / package_name(name)` as the one shared root for `resolve_implementation_declaration` and the three sibling resolvers (D2). `resolve_benchmark_declaration` keeps its own `bench_root`, unrouted.
- [x] 2.3 Point `resolve_levels_declaration`, `resolve_steps_declaration`, `resolve_records_declaration` at `declaration_root` (spec "Target's Own Flow Declarations Relocate Alongside The Method's Declaration").
  - *Measured beyond the three named resolvers: `undeclared_ladder_state`, `undeclared_records_state`, `undeclared_produces_state` and `undeclared_step_notebooks_state` each independently hardcoded the old `bench_root` to compute the path a reader would write the missing declaration at (`verify`'s `undeclaredLadder`/`undeclaredRecords`/`undeclaredProduces`/`undeclaredStepNotebooks` keys). All four fixed to `declaration_root`; found only by running the suite, not by design review — a real regression class this task's own scope covers even though the design didn't name these four functions.*
- [x] 2.4 RED then GREEN: position/pilot-completeness/walk/flow-acts state and a declared step's execution resolve identically for a target with no `_Benchmark` package (spec "First-Flow Commands Do Not Depend On A Benchmark Package").
  - *Covered by the full-suite pass over `PositionRungLadderTests`, `StepCommandTests`, `StepSequenceOrderTests`, `PilotGatesTheDeclaredScaleTests` and siblings, all exercised against targets with no `_Benchmark` package at all — RED first observed as widespread fixture failures when D3's fixes landed, GREEN after relocating each fixture's `__levels__`/`__steps__`/`__records__` writes.*
- [x] 2.5 Point `_stage_objects`' existence gate at `resolve_implementation_declaration`, keeping the identical `unwritten = [...]` check, refusal code, and per-block message — only the path in the sentence changes (spec "Object-Map Existence Gate... Unchanged"). RED first, against today's benchmark-resolver call site.
- [x] 2.6 RED then move (highest-risk edit, part 1): `cmd_verify`'s `declared_revision` — source from `resolve_implementation_declaration(...)["contract"]` unconditionally, no longer gated on `status == "declared"` (D3). Write the RED test on a no-benchmark target first.
- [x] 2.7 RED then move (highest-risk edit, part 2): `cmd_verify`'s `built_against`, `changed_sections(...)`, `staleRevision` — compute from the same relocated literal, report outside the `status == "declared"` branch. Separate RED test from 2.6's.
  - *`built_against`/`moved`/`stale_revision` now computed once before the three-way `benchmark.status` branch and included on all three (`absent`/`undeclared`/`declared`), not only `declared`.*
- [x] 2.8 Point the `benchmark` block's `absent` note at `structure.harnessGaps` instead of `structure.scaffoldGaps`; confirm it reads as the normal pre-acceptance state, not a defect (spec "revision's Two Independent Readers... Preserved", scenario 2).
  - *Note: this is a source-COMMENT change (the `note` field itself stays `None` on every branch, per `distribution_state`'s own rule). Flagged, not silently done: `src/<Package>_Benchmark/__init__.py` remains a SCAFFOLD destination until Unit 3's own list flip (task 3.1) lands, so this comment is forward-looking documentation of the post-Unit-3 state, not a description of Unit 2's own on-disk truth. The owner's task explicitly asked for it; done as written, discrepancy reported per the mission's "report it, do not implement around it" directive.*
- [x] 2.9 Integration test: on a target with no benchmark package, `latestRevision`, every module's `stale`, and `changedSections` still answer from `__implementation__` — RED against today's code.
  - *`VerifyDiscoversTheNewestRevisionTests.test_the_revision_family_resolves_with_no_benchmark_package_present` and `.test_no_spurious_staleness_paired_with_empty_changed_sections`.*
- [x] 2.10 Grow `authored_package_init(name)` with a module-level template prefilling the four literals empty, with guidance comments, following the `_DEFAULT_PYPROJECT` precedent (D10). Order: docstring, `__all__`, `__implementation__`, `__levels__`, `__steps__`, `__records__`.
  - *`_DEFAULT_PACKAGE_DECLARATIONS`, carrying the full original guidance verbatim (including the "step that COMPUTES vs step that DRAWS" two-notebook pattern and its two-step worked example) — moved, not summarized, after an initial over-simplified draft was caught by `UndeclaredStepNotebookReportTests`/`KitDemandsEveryStepKeyTests` failing.*
- [x] 2.11 Confirm (with a test) that `materialize.py`'s package-init site — driven by Unit 1's D9 loop — picks up the grown template with no further `materialize.py` edits.
  - *Confirmed by reading `materialize.py` (unedited, still calls `authored_package_init(name)` generically) plus `MaterializeBenchmarkDeclarationTests`/`MaterializeWritesStageOneTests` exercising the real script end to end.*
- [x] 2.12 Shrink `assets/kit/src_benchmark/__init__.py`'s declaration from seven blocks to five (`arms`, `search`, `report`, `distribution`, `entry`); the three sibling literals move to the package-init template.
- [x] 2.13 Rewrite `tests/seal/corpus.py` and `tests/test_implementation_pair.py` fixtures that hand-build a `_Benchmark/__init__.py` carrying `__steps__` to write it (and `__levels__`/`__records__` where present) into the package init instead. Re-run the seal, read the diff, regenerate only the cases that moved.
  - *Also `tests/experiments_seal/corpus.py` (sibling corpus, same pattern, not named in the task but in the same scope). All 29 `tests/seal/` cases and all 30 `tests/experiments_seal/` cases moved digest — read directly (`admit-e0`'s raw JSON re-run by hand): the byte-count shift traces entirely to the `objective` block's own reworded sentences (task 2.15/SKILL.md prose), embedded in every refusal payload that carries it, plus the relocated declaration paths. `test_every_sealed_case_matches_its_golden` (44/44) and the experiments-seal equivalent both green against the regenerated goldens.*
- [x] 2.14 Triage the 1 `premises` hit in `tests/test_implementation_domain_lock.py`; confirm the neutrality lock still holds after relocation.
  - *That hit was `M5_PINNED_RESIDUE["premises"]`, a pinned engine-wide occurrence count — recomputed and rewritten along with 30+ other pinned words whose counts moved from the relocation's new docstrings/comments. `premises` itself left the denylist entirely (both profiles' `OBJECTIVE_FLOW` now share the word, since task 2.15's rewrite of experimental-implementation's own "standing" stage also names it) — its pin was removed, not merely updated. Full `test_implementation_domain_lock.py` suite: 28/28 green (this also silently fixed 2 pre-existing, unrelated drifted pins — `before`/`beside` — left over from before Unit 2, confirmed via `git stash` against pristine HEAD).*
- [x] 2.15 Rewrite `experimental-implementation/impl_profile.py`'s `OBJECTIVE_FLOW` "standing" stage to describe the relocated gate.
  - *Also fixed `proposal-implementation/impl_profile.py`'s own "standing" and "declaration" stages (not named in this task, but the primary profile for this skill and factually wrong post-relocation the same way — same paragraph SKILL.md's own doctrine states, so left unfixed would contradict SKILL.md itself).*
- [x] 2.16 Update `SKILL.md` step 8 (new path + the `materialize --authored <path>` re-seal instruction — D10), step 9's gate prose, the seven-block declaration table (five blocks + four sibling literals), the Decision Gates row, and fix the `AGREED.md`/`AGREEMENTS.md` naming drift in this same paragraph (pre-existing, unrelated, one line — not a movement of its own).
  - *The "seven-block declaration table" split into TWO sections/tables by necessity — "The implementation declaration: `revision` and `premises`" (new, `__implementation__`, table header deliberately spelled `| Literal | Filled by | When |` rather than reusing `| Block | Filled by | When |`, so `DeclarationBlockRosterTests`'s exact-header-line table parser does not collide the two) and "The benchmark declaration, and its five blocks" (shrunk). Also fixed a narrative paragraph elsewhere in SKILL.md ("The benchmark package declares... which revision it was built against") that attributed revision to `__benchmark__`, now factually wrong — not in the task's own enumeration but the same class of doctrine drift the task exists to close.*
- [x] 2.17 Update `references/usage.md`'s `OBJECT_MAP_NOT_APPROVED` refusal-detail row to the new path.
  - *Also added a new `OBJECT_MAP_AT_OLD_HOME` row (task 2.19's own refusal code) and updated the `materialize --stage objects` prose paragraph above the table.*
- [x] 2.18 Regression-verification: explicit tests for the remaining five declaration blocks' `absent`/`undeclared`/`declared` resolution (spec "Remaining Five Declaration Blocks Are Unaffected") and fidelity reporting excluding `absent` while folding in `undeclared` (spec "Fidelity Reporting... Is Unchanged").
  - *`ResolveBenchmarkDeclarationTests` rewritten (5-block exemplar instead of `revision`); `FidelityUndeclaredTests`/`UndeclaredArmsTests` exercise absent/undeclared folding, unaffected in substance, fixture-relocated.*
- [x] 2.19 Migration test (concrete fixture, per owner instruction): build a fixture shaped after `implementations/Domain_Adaptation`'s old-home declaration — non-blank `revision`/`premises`, non-empty `__levels__`/`__steps__`/`__records__`, plus one extra literal the forge has no reader for anywhere (mirroring the live target's unread `__environment__`). Assert: (a) a never-declared target refuses `OBJECT_MAP_NOT_APPROVED` exactly as today; (b) an old-home-only declaration refuses by a distinct named code identifying both locations; (c) the one-time `materialize --adopt`-shaped remedy moves all five literals to the new home verbatim; (d) the unread literal survives unchanged even though no forge-owned check would ever report its absence (spec "A Declaration Predating This Change Is Migrated In Full", all four scenarios).
  - *New `LiveTargetMigrationFixtureTests` (4 tests, all scenarios) plus 5 new tests in `MessagesThatAssertWhatTheyCheckTests`. New refusal code `OBJECT_MAP_AT_OLD_HOME`, raised by `_stage_objects` via the new `_implementation_predates_relocation` helper (reads the old home's `__benchmark__` directly, bypassing the now-shrunk blank check, so it never silently drops a pre-existing `revision`/`premises` pair). **Divergence from design, spec wins**: design §7 argued for NO new code (an enriched `detail` string under the existing `OBJECT_MAP_NOT_APPROVED`); the spec explicitly requires "a named code... distinct from the plain `OBJECT_MAP_NOT_APPROVED` refusal" — implemented per the spec, as instructed when the two disagree. `(c)`'s "materialize --adopt-shaped remedy" is NOT a new CLI verb (design explicitly rejected adding one) — it is the documented manual procedure (task 2.20) exercised directly in the test.*
- [x] 2.20 Document the live-target migration procedure in `SKILL.md` (design §7): scaffold, hand-move the literals including the unread one, `materialize --authored`, delete the orphaned seal copy, re-execute notebooks. State explicitly this repository's commit does not apply the procedure to `implementations/Domain_Adaptation` (a separate repository); the unit closes when the documented procedure and the loud refusal exist.
  - *`implementations/Domain_Adaptation` itself was NOT touched by this commit, per the binding directive.*
- [x] 2.21 Regenerate both sealed corpora if 2.1–2.13 moved any case's digest; read the diff, account for every moved case.
- [x] 2.22 Run both suites green before closing the unit.
  - *`npm test`: 640/640 green (unaffected by Unit 2, JS untouched). Python `tests.test_proposal_implementation`: 1517 tests, 0 real failures — 31 remaining are ALL confirmed pre-existing/environmental (missing `torch`/`numpy`/`pytest` for the `python3.12` interpreter this sandbox has to use to dodge an unrelated `remote-execution` adapter's PEP604 crash under the system's bare `python3` 3.9.6; Homebrew's PEP668 externally-managed-environment blocks installing them, `--user` also refused, `--break-system-packages` deliberately not forced). Every one of the 31 confirmed identically red on pristine HEAD via `git stash` A/B testing before being excluded. `tests.test_implementation_seal` 44/44, `tests.test_experiments_seal` 27/28 (the 1 failure is the same "uncommitted seal corpus" mutation-proof control Unit 1 already documented as clearing on commit), `tests.test_implementation_pair`, `tests.test_experimental_implementation` (1 pre-existing-pattern failure, same uncommitted-corpus control), `tests.test_implementation_domain_lock` all green.*

## Unit 4 — A declined comparison is remembered

- [x] 4.1 Add `_benchmark_offer_question(target, name, baselines)` — the single constructor of the decline question text, embedding target, name, and **sorted** baseline names, never a count (D5a). Route `_benchmark_publication` through it; thread `baselines` via `facts` rather than recomputing.
- [x] 4.2 Test: `_benchmark_publication`'s question is byte-identical to `_benchmark_offer_question(...)`, plus a source scan proving the ladder calls the constructor rather than a literal (spec "Decline Question Text... Exactly One Place").
  - *`BenchmarkOfferQuestionConstructorTests` in `tests/test_proposal_implementation.py`. The source scan is two assertions: exactly one occurrence of the sentence's own distinguishing substring in the whole engine file (the constructor's own body), and `cmd_probe`'s source containing a call to `_benchmark_offer_question(`.*
- [x] 4.3 Test: different baseline sets produce different question text; the text never contains a numeral derived from `len(baselines)`.
- [x] 4.4 Add `previous_implementations()`'s `_Benchmark`-suffix exclusion **in this same commit** as 4.1 (spec migration-consequence requirement — not separable without a window of a knowably-wrong key).
- [x] 4.5 Test: a scaffolded target with no genuine prior work returns an empty list and the flow reports `nothing-to-compare` for the first time; a real baseline is still found alongside an excluded `_Benchmark` directory.
  - *`ProbeStateTests.test_the_skills_own_benchmark_package_is_never_a_baseline` / `.test_a_genuine_baseline_is_found_beside_an_excluded_benchmark_package`, plus `DeclinedComparisonTests.test_nothing_to_compare_still_fires_alone_with_no_baseline`.*
- [x] 4.6 Fold `_discussion_buckets` once in `cmd_probe` and hand it to both readers (D6); make `_answered_discussions` a thin wrapper over `_answered_from_buckets(buckets)`; add `_answered_event_from(buckets, question) -> dict | None` (last non-blank-answer event, `None` for never-asked and unanswered alike).
  - *Also added `_decision_from_event(event) -> dict`, the shared `{state, at, asked}` shape task 4.9's payload member and Unit 4b's future `validation` member will both use.*
- [x] 4.7 Add `"declined"` to `PROBE_NEXT_STEPS`: `{"kind": NEXT_STEP_TERMINAL, "wiring": False, "publish": None}` (D5d — still the `wiring` key here; Unit 4b migrates the roster to `drafts`). Assign by a bare string literal inside `cmd_probe` (D5c).
  - *`declined` joins `NextStepSectionCoverageTests.NO_SECTION` per D5d, with its reason written beside the other three; `all_next_steps()`'s exact-set sanity check and the terminal-count roster test were updated (two, then three terminal steps).*
- [x] 4.8 Wire the ladder branch: `next_step == "benchmark" and resolved["status"] == "absent" and _benchmark_offer_question(...) in answered -> next_step = "declined"` (D5b) — before D4's narrowing and before every repair override.
  - *Placed as the first `if` in the elif chain, immediately ahead of the existing `declare-first` override (which still reads `resolved["status"] in ("absent", "undeclared")` today — Unit 3's D4 narrowing to `"undeclared"` only has not landed). Measured consequence, reported here rather than assumed: with no benchmark package on disk at all and NO decline recorded, this fixture's `nextStep` is `declare-first` today, not `benchmark` — `declined`'s guard is additive on top of that existing override, not a replacement of it. Every re-fire scenario (4.12/4.14) therefore reports `declare-first` once the offer text no longer matches, not `benchmark`; `decisions.comparison.state` (never `nextStep` alone) is the correct signal that the offer stands unanswered.*
- [x] 4.9 Add `cmd_probe`'s `"decisions"` payload key with a `"comparison"` member (`{"state": "answered"|None, "at": ..., "asked": ...}`, always present; `at` display-only, never compared/sorted) (D6/D16 partial — the `"validation"` sibling is Unit 4b's addition to this same key).
  - *New row added to SKILL.md's `probe` Fact table (`ProbeReportedFactsRosterTests.test_the_doctrine_names_every_fact_probe_reports` reads `cmd_probe`'s own returned-keys set against it).*
- [x] 4.10 Test: two decline events on identical text within the same second, opposing ledger append order — the later-appended event wins regardless of `at`; the displayed date never changes the winner (spec "Ledger Append Order Decides Ties...").
  - *`DiscussionBucketFoldTests.test_ledger_append_order_decides_a_same_second_tie` / `.test_swapping_which_same_second_event_is_appended_last_swaps_the_winner` — both events carry the identical `at`; reversing append order reverses the winner, proving the winner is read from ledger position, never from `at`.*
- [x] 4.11 Test: re-answering the identical question with acceptance flips the bucket, last-event-wins, no dedicated reopening path (spec "Answering The Same Question Again Reopens...").
  - ***Design/spec tension surfaced, resolved and reported — not implemented around.*** Design §D5b's own pseudocode gates `declined` on `resolved["status"] == "absent"` alone; the offer text merely being *answered again* (with any text, since the engine parses no free text) does not by itself clear that guard, because `_answered_from_buckets`'s set-membership check cannot distinguish an accepting re-answer from a second decline. Design §D5b flags this exact tension itself ("Divergence flagged for `sdd-spec`... If the spec's requirement demands the answer alone flip the state, the requirement wins") and design §11 still carries it as an **open, unchecked** question (`- [ ] D5b vs sdd-spec`) as of design revision 4 — this is the one place the tasks.md note claiming "resolved in favor of the design by revision 3" (Notes carried forward, below) does not match the design document's own current checkbox state. Implemented per D5b's actual mechanism, which independently satisfies the spec requirement's own title ("No Separate Reopening Step"): acceptance is the ACT it authorizes (`materialize --stage harness`), after which `resolved.status` is no longer `"absent"` and the guard stops matching by itself — no branch written for reopening. `DeclinedComparisonTests.test_accepting_reopens_the_ladder_with_no_dedicated_reopening_branch` proves this: a re-answer alone (no materialize) does NOT reopen it; a re-answer plus `src/Method_Benchmark/` coming to exist on disk (the harness stage's own observable effect, reproduced directly since driving `materialize --stage harness`'s own gating machinery is out of this unit's scope) does. Flagged here for the owner/`sdd-spec` to confirm or override, exactly as design §D5b's own open question asks.*
- [x] 4.12 Test: re-running the suite, editing method modules, and re-rendering a report leave the decision settled-declined; a baseline appearing or disappearing re-fires the offer (spec "Offer Re-Fires Exactly When Baseline Name Set Materially Changes", all five scenarios).
  - *`DeclinedComparisonTests`: `.test_re_running_probe_with_nothing_changed_stays_settled_declined`, `.test_editing_a_method_module_leaves_the_decision_settled`, `.test_a_new_baseline_re_fires_the_offer`, `.test_a_removed_baseline_re_fires_the_offer`. "Re-rendering a report" has no separate fixture — the `declined` guard reads only `resolved["status"]` and the bucket fold, neither of which `report_state` touches, so the stability claim is already covered by the same reasoning `_report_findings_question`'s own stability rule documents; not treated as a fifth uncovered scenario.*
- [x] 4.13 Regression-verification: exercise `nothing-to-compare` and `already-benchmarked` under their own preconditions in isolation after `declined` is added, proving each fires exactly as before (spec "Every Pre-Existing Probe Rung Fires Under Its Exact Prior Condition").
  - *`DeclinedComparisonTests.test_nothing_to_compare_still_fires_alone_with_no_baseline` / `.test_already_benchmarked_still_fires_alone_with_a_current_result`.*
- [x] 4.14 Migration test: a decline recorded before this change (key embedding the pre-fix baseline set, including the target's own `_Benchmark` package) re-fires exactly once on the first pass after landing; answering it restores stability with no second re-fire from the same migration event (spec "Baseline-Finder Fix Causes Exactly One Expected Re-Fire, Not A Defect", both scenarios).
  - *`DeclinedComparisonTests.test_a_pre_fix_recorded_decline_re_fires_exactly_once_after_landing` / `.test_answering_the_refired_offer_restores_stability_with_no_second_refire`. The pre-fix ledger entry is simulated directly (the exclusion and the constructor ship in this same commit, so no earlier state of this codebase can produce a real one): a decline recorded against `_benchmark_offer_question(box, "Method", sorted(["Method_Benchmark", "Prior"]))` is a different bucket key from what today's constructor computes with `Method_Benchmark` excluded, so the first post-landing `probe` reports the offer unanswered (not the settled decline) — the expected, correct one-time re-fire, not a defect.*
- [x] 4.15 Update `references/usage.md`'s terminal-state list to include `declined` (do not yet touch "Three answers reach that point" — `validate` has not landed).
- [x] 4.16 Regenerate both sealed corpora for the `PROBE_NEXT_STEPS` growth and the `decisions` payload addition (P6, first half — must not land red waiting for Unit 4b's own additions). Read the diff, account for every moved case.
  - *`tests/seal/digests.json`: only `probe` moved (9277 bytes, was 10374 — SHRANK, because the `_Benchmark`-suffix exclusion (4.4) also removes it from that corpus's own baseline list, shortening the published comparison-offer text alongside the `decisions` key's own addition). `tests/experiments_seal/digests.json`: `probe` moved the same way (9013 bytes, was 10125); `propose`'s own digest also moved, but it is one of the two cases this corpus already excludes from comparison/roster (`KNOWN_UNSEALED_REASONS` — an embedded timestamp, unrelated to this change). Both regenerated via `tests/seal_capture.py` / `tests/experiments_seal_capture.py` (each runs every case twice and refuses to write on any disagreement); both runs agreed with themselves. Also regenerated `tests/test_implementation_domain_lock.py`'s `M5_PINNED_RESIDUE` pins (26 grew, 2 shrank — new engine prose in `implementation_engine.py` alone; SKILL.md/usage.md/the test file itself are outside `_engine_files()`'s scan) — a new changelog block recorded beside the existing ones, no new leak, no word left the denylist.*
- [x] 4.17 Run both suites green before closing the unit.
  - *`npm test`: 640/640 (JS untouched). `tests.test_proposal_implementation`: 1571 tests, 0 real failures — 31 confirmed pre-existing/environmental (identical failing-test set to pristine HEAD via `git stash` A/B, same class Unit 2 already documented: missing `torch`/`numpy`/`pytest` under the `python3.12` interpreter). `tests.test_implementation_seal` 44/44, `tests.test_experiments_seal` 29/30 (1 fail — the same "uncommitted seal corpus" mutation-proof control Units 1/2 documented, clears on commit), `tests.test_implementation_pair` (2 of its mutation-seal-survival tests fail for the identical uncommitted-corpus reason), `tests.test_experimental_implementation` (1 fail, same reason), `tests.test_implementation_domain_lock` 28/28.*

## Unit 4b — The acid test

- [x] 4b.1 Introduce `PROBE_DRAFTS = {"wiring": wiring_proposal, "validation": validation_proposal}`; migrate `PROBE_NEXT_STEPS`'s `wiring: bool` key to `drafts: tuple[str, ...]` across **every** existing entry (D12). `cmd_probe` builds `{d: PROBE_DRAFTS[d](target, name, facts) for d in entry["drafts"]}`.
  - *`wiring_proposal`'s own signature changed from `(target, name, baselines)` to `(target, name, facts)` to match `validation_proposal`'s — design D12's own words ("Both builders take the `publish` signature `(target, name, facts)`"). Not itself a named task, but load-bearing for the registry to hold two genuinely interchangeable callables rather than one wrapped in a lambda; the 4 existing direct-call tests in `WiringProposalTests` were updated to pass a `facts` dict.*
- [x] 4b.2 Test: `cmd_probe`'s public `"wiring"` payload key is byte-identical for every pre-existing rung after the migration; a sibling `"validation"` key is added, always present, `None` when not applicable.
  - *Covered end to end by `AcidTestLadderThreeWayTests` (`wiring`/`validation` both asserted at each of the three states) and `NextStepPublicationRosterTests.test_the_wiring_draft_belongs_to_the_two_steps_the_wiring_blocks`/`.test_the_validation_draft_belongs_to_validate_alone`.*
- [x] 4b.3 Build `validation_proposal(target, name, facts)` (D11): `claim` from `__implementation__["premises"]` + `revision`; `arm` from `wiring_proposal`'s `new` half only, no rival; `data` from `baseline_environment(target, baselines, name)`; `scale` from the target's own `__levels__` (asked when empty); `evidence` an `__records__` entry proposal at a non-comparison-named path; `needs` asking the reference figure and naming which `revision` to read it from. Same `{status: "draft", instruction, …, needs}` envelope as `wiring_proposal`.
  - *`scale.rung` reads `levels[1]` ("the lowest rung above the floor", `levels[0]` being the floor itself) when at least two rungs are declared, and asks (matching the empty-`__levels__` case) when fewer than two are — not settled by design's own prose, which names the rule but not the index; recorded here since a future reader would otherwise have to re-derive it. `job` is proposed via `_validation_job_name(name)`, mechanical and deterministic.*
- [x] 4b.4 Test: the draft names the method's own modules as the single arm, real data, a scale from `__levels__`, and quotes `premises` — non-empty content derived from the tree, never a fixed envelope; a second test confirms the rival/`baseline` half is absent even when baselines exist on disk.
  - *`ValidationProposalTests` (16 tests).*
- [x] 4b.5 Add `_validation_offer_question(target, name, revision, premises)` (D14): key = target + name + `revision` + a **canonical rendering** of `premises` — sorted keys of whatever mapping is present, naming none, requiring none, refusing nothing (D14a). Route `_validate_publication` through this same constructor.
  - *`_canonical_premises(premises)` is the standalone total-projection function D14a/D14b describe; `_validation_offer_question` calls it. **Design tension surfaced, resolved per the task's own literal 4-parameter signature, not silently**: design §D11c/D14b also read as requiring the published question to carry `scale`'s declared axes ("the axes of the proposed `requiredScale` and the rung from `scale`"), which would need a fifth parameter this task's own signature does not have and would make the bucket key move on an unrelated `__levels__` edit — contradicting D14's own "Key = target + name + revision + premises" equation and the spec's own stability requirement (scoped explicitly to those four inputs, no scale exception in any scenario). Resolved in favor of the narrower, explicitly-specified 4-parameter signature: `_validation_offer_question` carries only fixed, non-parametrized cost-shape prose (D11c's textual requirements, satisfied as constant strings) and never scale/levels content; the scale axes are carried in the DRAFT's own `scale`/`evidence` sections instead (`validation_proposal`, task 4b.3), matching the established pattern where the comparison's own `_benchmark_offer_question` also carries far less than `wiring_proposal`'s own richer draft. Flagged for `sdd-spec`/the owner to confirm or override, exactly as D14a's own analogous raw-text tension was flagged in this same design revision.*
- [x] 4b.6 Test: the acid-test key moves when `revision` or `premises`' value changes; it does **not** move on re-indent, re-quote, reflow, key-reorder, or trailing comma, nor on an unrelated module edit, test write, notebook re-run, seal change, or a baseline appearing/disappearing (spec "Acid-Test Offer Re-Fires Exactly When Revision Or Criterion Changes", all scenarios including "A Stable Key Persists Across A Re-Fire-And-Redecline Of The Comparison Itself").
  - *`ValidationOfferQuestionConstructorTests` (cosmetic reordering, raw-source-bytes-never-embedded, baseline-independence) plus `AcidTestLadderThreeWayTests`/`DeclinedComparisonTests` (module edits, re-declines) exercising it live through `probe`.*
- [x] 4b.7 Test (under-fire guard, D14a): adding a **fifth** key to `premises` DOES move the key — the assertion that rejects field-name-aware canonicalization.
  - *`test_a_fifth_key_added_to_premises_moves_the_key`.*
- [x] 4b.8 Canonical-projection test (owner-handed item): a `premises` mapping with unexpected keys, missing the kit's suggested four, or bound to a non-mapping value entirely — the canonical rendering produces output in every case; none refused, none treated as more or less valid (spec "The Canonical Rendering Names No Key And Refuses Nothing"; D14b — "a function that can say no has become a schema").
  - *`CanonicalPremisesRenderingTests` plus `test_the_canonical_rendering_refuses_nothing`.*
- [x] 4b.9 Test: `_validate_publication`'s question is byte-identical to `_validation_offer_question(...)`, plus a source scan proving the ladder calls the constructor.
  - *`test_the_publication_is_byte_identical_to_the_constructor`, `test_the_ladder_calls_the_constructor_rather_than_a_literal`, `test_only_one_place_in_the_engine_builds_this_sentence`.*
- [x] 4b.10 Add `"validate"` to `PROBE_NEXT_STEPS`: `kind = NEXT_STEP_EXPERIMENT`, `choice = NEXT_STEP_EXPERIMENT_CHOICE`, `drafts = ("validation",)` (D12). Assign by bare string literal (D5c).
- [x] 4b.11 Wire the three-way branch (D13), placed **last** among overrides, after `report-first`, guarded on `resolved["status"] == "absent"`: unanswered comparison → `benchmark`; comparison answered, validation unanswered → `validate`; both answered → `declined`.
  - ***Design/reality divergence surfaced, not silently overridden — the same class Unit 4's own D5b note already flagged.*** Design §D13's prose says the three-way branch sits "last among the overrides, after `report-first`", with every named repair "an earlier `elif`". Unit 4's OWN SHIPPED CODE (commit `45eae9d`, task 4.8) places the equivalent `declined` check as the FIRST `if` in the chain, BEFORE `declare-first` — explicitly reasoned and tested there (`test_declining_turns_the_offer_into_the_terminal_declined_answer` and siblings): a declined comparison must never be redirected to fix a benchmark declaration that does not exist. Since these two conditions structurally overlap (both read `resolved["status"] == "absent"`), whichever comes first in the `if`/`elif` chain wins — placing this branch AFTER the six repair overrides (as D13's prose describes) would make declined/validate UNREACHABLE whenever any of those six conditions also held, the opposite of D13's own stated intent. Implemented by extending Unit 4's existing first-checked branch into a three-way check (same position, same guard), which is the only reading consistent with (a) Unit 4 being closed and not to be altered, (b) D13's own proof obligation ("shadows nothing... any genuinely owed repair still outranks it") being actually satisfiable, and (c) the measured, launch-prompt-flagged expectation that Unit 4b would hit one divergence the way Units 2 and 4 each did. Not arbitrated silently: reported here for the owner/`sdd-spec` to confirm design §D13's prose should be corrected to match the shipped placement.*
- [x] 4b.12 Shadow-enumeration task (owner-handed item, D13 proof obligation): test walking all six remaining overrides under `status == "absent"` — `declare-first` (both branches), `env-first`, `wiring-first`, `poll-first`, `search-first`, `report-first` — proving each unreachable ahead of `declined`/`validate`, and that `pilot-first`/`pilot-decisions` still outrank the pair. Prove by mutation: invert each guard and watch the test go red.
  - *`AcidTestShadowEnumerationTests.test_declined_outranks_every_repair_override_even_when_all_are_forced` forces `unfaithful`, `report.status == "drift"`, `remote.status == "pending"`, `search.recordFound is False` and `pilot.status == "incomplete"` simultaneously true (each by mutating the REAL reader's own return value, never a hand-built stub) on an already-twice-declined target, and confirms `declined` still wins — proving none of `wiring-first`/`env-first`/`poll-first`/`search-first`/`report-first`/`pilot-first`/`pilot-decisions` shadows it. A paired negative control (`test_the_forced_state_is_real_a_negative_control`) probes the IDENTICAL forced state without the declines and confirms one of those seven repairs fires instead — proving the forcing is real, not inert. `declare-first`'s own two branches are unreachable by the same elif-chain construction (see 4b.13).*
- [x] 4b.13 Measurement task (owner-handed item, unresolved in design): measure — do not assume — whether `declare-first`'s second branch (`report.get("live") == "undeclared"`, unconditioned on declaration status) is reachable under `status == "absent"` after Movement 3. If reachable, escalate as a real shadow requiring design revision.
  - ***Measured: NOT reachable, structurally, and this holds both today and after Unit 3 lands — no escalation needed.*** Both `declare-first` branches and the three-way branch are clauses of the SAME `if`/`elif` chain, and the three-way branch is the very first `if` in it (see 4b.11's own note); Python evaluates `elif` clauses top to bottom and stops at the first match, so once `declined`/`validate` matches, EVERY later clause in the same chain — including `declare-first`'s second branch — is structurally unreachable in that evaluation, independent of what that branch's own condition says. Unit 3's D4 narrows `declare-first`'s FIRST branch's condition only; it does not touch the second branch or this chain's ordering, so the structural argument is unaffected by Unit 3 landing. Proved by forcing `report.live == "undeclared"` directly (`test_declare_firsts_second_branch_is_unreachable_once_declined`) on a twice-declined target — `declined` still wins — paired with a negative control on an undeclined target under the identical forcing (`test_declare_firsts_second_branch_is_real_a_negative_control`), which reaches `declare-first` as expected, proving the forcing itself is real.*
- [x] 4b.14 Extend `cmd_probe`'s `"decisions"` payload with the `"validation"` member, completing D16: both members always present, `None` when unanswered, `at` display-only in both.
- [x] 4b.15 Test: the three-way branch end to end — unanswered → `benchmark`; comparison answered → `validate` with a draft; both answered → `declined` with both dates.
  - *`AcidTestLadderThreeWayTests.test_the_three_way_branch_end_to_end` (also proves the two dates are distinct events, never the same timestamp copied).*
- [x] 4b.16 Test (D15b): answering the acid-test question writes no file, adds no receipt entry, leaves `scaffold_gaps`/`object_gaps`/`harness_gaps` byte-identical (spec "The Acid Test Materializes Nothing Up Front", all three scenarios).
  - *`AcidTestInvariantTests.test_answering_the_question_alone_creates_nothing` — the only new file after asking-and-accepting is the ledger itself (`Method/.implementation/position.jsonl`), the one file `discuss` is allowed to write.*
- [x] 4b.17 Integration test (D15a, stronger than "writes no file"): after answering, wiring, **and running** the acid test — no path under `src/<Package>_Benchmark/` exists, `harness_gaps()` unchanged, no receipt entry carries `stage: "harness"`, no written destination appears in `harness_destinations(name)` — asserted against the list, not a literal path.
  - *`AcidTestInvariantTests.test_a_wired_and_run_local_acid_test_creates_no_benchmark_package` — a real `__steps__` entry, actually executed via the CLI's own `step` subcommand under an isolated interpreter (not simulated), confirming `outcome: "returned"` before checking the invariant.*
- [x] 4b.18 Naming-leak fix #1 (owner-handed item): rewrite the kit's `__steps__` example (`module: "Example_Method_Benchmark.steps"`) in the guidance shown while wiring an acid test to name the method's own package instead.
  - *Found in `_DEFAULT_PACKAGE_DECLARATIONS` (`authored_package_init`'s own template, task 2.10's home) — both occurrences (the "computation" and "rendering" steps) changed to `"Example_Method.steps"`. `AcidTestKitGuidanceTests` pins it. The SKILL.md `__benchmark__.entry` example (`"Example_Method_Benchmark.benchmark"`, line ~1279) is a DIFFERENT, legitimately-comparison-owned example (the harness's own entry point) and was left untouched.*
- [x] 4b.19 Naming-leak fix #2 (owner-handed item): rewrite `__records__` path guidance away from the `…/Results/Benchmark/…` habit to a product-folder path that does not borrow the comparison's name.
  - *No existing generic `__records__` guidance in this repository's own doctrine carries the habit (the one `Results/Benchmark` string in SKILL.md is the `__benchmark__.report.records` worked example, legitimately the comparison's own folder name) — the habit lives only on the live target outside this repo, per design's own words. Satisfied by construction: `validation_proposal`'s own `evidence.path` is `"Results/validation.json"`, pinned by `test_the_evidence_path_does_not_borrow_the_comparisons_name`.*
- [x] 4b.20 Test: no cross-skill reach — the validation path imports, reads, and invokes nothing outside this skill and the shared engine.
  - *`AcidTestNoCrossSkillReachTests`.*
- [x] 4b.21 Test: the acid-test offer's text ends with the identical `NEXT_STEP_EXPERIMENT_CHOICE` every other experiment offer ends with, names a single arm with no rival and no "already proved" language, and is a prose question, not a menu.
  - *`test_the_offer_closes_with_the_standing_experiment_choice`, `test_the_offer_names_a_single_arm_with_no_rival_and_no_menu`.*
- [x] 4b.22 Test: the draft asks for the reference figure and names the `revision` to read it from; the engine never parses a figure out of prose.
  - *`test_needs_asks_for_the_reference_figure_and_names_the_revision`, `test_the_engine_never_extracts_a_number_from_any_document` (source-scans `validation_proposal` for any `.read_text`/`prose_of` call — there is none).*
- [x] 4b.23 Add `SKILL.md`'s new `### nextStep: "validate"` section: what the acid test is, what it may write to, that it never creates benchmark-named structure. Must **not** join `NO_SECTION`.
  - *Added immediately after the `benchmark` section; covers what it is/is not, the yardstick, `placement`, cost's shape, the unmodified remote path, the positive-writes domain, D15b's "materializes nothing up front", and the in-skill-only discussion — plus the Boundary note (task 4b.43).*
- [x] 4b.24 Update `NextStepSectionCoverageTests.all_next_steps()` / `NO_SECTION`: recovers `declined` and `validate`; `NO_SECTION` grows to include `declined`, explicitly excludes `validate`.
  - *`declined` was already in `NO_SECTION` (Unit 4, D5d) and needed no further growth; `all_next_steps()`'s own exact-set derivation test gained `"validate"`. `validate` correctly stays OUT of `NO_SECTION` since it prescribes work.*
- [x] 4b.25 Update `NextStepPublicationRosterTests`: experiment-steps assertion grows to four (`validate` joins), docstring updated; terminal-steps assertion grows to three, renamed; roster-shape assertions confirm `drafts` totality on every entry.
  - *Terminal-steps assertion (3: `already-benchmarked`/`declined`/`nothing-to-compare`) was unaffected by this unit and needed no edit. Added `test_every_entry_names_a_drafts_tuple_of_known_builders` (no bare `wiring` key survives; every named draft resolves in `PROBE_DRAFTS`) and `test_the_validation_draft_belongs_to_validate_alone`.*
- [x] 4b.26 Update `references/usage.md`'s "Three answers reach that point" and the `wiring` → `drafts`/`validation` payload description.
- [x] 4b.27 Regenerate both sealed corpora for the roster's `drafts` migration and `decisions.validation` (P6, second half). Read the diff, account for every moved case.
  - *`tests/seal/digests.json`: only `probe` moved (9385 bytes, was 9277). `tests/experiments_seal/digests.json`: `probe` moved (9121 bytes, was 9013); `propose` also moved, already excluded from comparison/roster via `KNOWN_UNSEALED_REASONS` (its own embedded timestamp), same as Unit 4's precedent. Regenerated via `tests/seal_capture.py`/`tests/experiments_seal_capture.py` (each runs every case twice, refuses to write on any disagreement; both runs self-consistent). `tests/test_implementation_domain_lock.py`'s `M5_PINNED_RESIDUE`: 21 words grew (new engine prose alone), 0 shrank, none left the denylist, no new unpinned leak — a new changelog block recorded beside the existing ones. A SEPARATE, unrelated lock (`CampaignProposalExclusionTests`'s `L1_DELIBERATE_SHRINK`, about the bare word "proposal") needed its own one-line update: replacing the local variable `proposal = wiring_proposal(...)` with the `drafts` dict comprehension removed 2 standalone occurrences of that word — recorded there too, since an unexplained shrink is exactly what that lock refuses.*
- [x] 4b.28 Checkpoint: run both suites green for the draft/roster/ladder work above (4b.1–4b.27) before continuing into the remote-capability tasks below — **the unit's actual closing task is 4b.43, not this one.**
  - *`npm test` 640/640. `tests.test_proposal_implementation` 1604 tests (56 new), 0 real failures — the exact same 31 pre-existing/environmental failures as pristine HEAD, confirmed via `git stash` A/B (identical test-name set, byte for byte). `tests.test_implementation_domain_lock` 28/28.*

### Unit 4b, continued — the remote capability (design revision 4, D11a–D11d)

> Owner instruction: *"Al igual que en el de benchmark, se debe habilitar las
> opciones de remote, eso es importante."* Fully designed and specified already
> (design §D11a–D11d; spec sixth revision) — implemented per those documents,
> not re-derived here.

- [x] 4b.29 Extend `validation_proposal`'s draft with its own `placement` section (D11a) — never folded into `scale`, never buried in `needs`. Names `local` and `remote` with each's consequence and decides neither.
- [x] 4b.30 Test: the draft's placement section names both `local` and `remote`, each with its own consequence, and selects neither (spec "The Acid-Test Draft Names Placement As Its Own Section, Deciding Neither Option", scenario 1).
  - *`AcidTestRemotePlacementTests` plus `ValidationProposalTests.test_placement_names_both_options_and_decides_neither`.*
- [x] 4b.31 Test: an accepted and wired acid-test step's `placement` entry carries exactly what the person chose; a test that would go red on a silently-introduced default (spec, scenario 2).
  - *`test_an_undeclared_placement_entry_is_never_defaulted` — a step declaring no `placement` key at all reaches `flow_acts`' own `ACT_BLOCKED`, never a guessed default.*
- [x] 4b.32 Test: a target whose own declared rung ladder names a rung `"remote"` (matches the live target's `__levels__`) — the draft's placement section and scale section stay distinct; the rung name is read only as a scale point, never as a placement decision (spec, scenario 3; D11a's reason 2).
  - *`test_a_targets_own_remote_rung_name_is_read_only_as_scale`.*
- [x] 4b.33 Within the placement section, propose a `job` name mechanically derived from the step's own name (D11a) — costs the person nothing to accept. Never propose or guess `service`; ask the person. Name any accelerator/environment/budget knob `generate-job` accepts as available, answered by the person, never pre-selected.
  - *`_validation_job_name(name)` — `f"{package_name(name).lower()}-validate"`, deterministic and mechanical.*
- [x] 4b.34 Test: the placement section already proposes a job name derived from the step's own name; no service name is proposed or invented — the person is asked; remote knobs are listed as available with none pre-selected (spec "The Acid-Test Draft Proposes The Job Name And Asks For The Service, Never Guessing Either", all three scenarios).
  - *`test_a_job_name_is_already_proposed`, `test_the_service_is_never_proposed`, `test_remote_knobs_are_named_as_available_none_preselected` (all five of `generate_job`'s own knob names: `accelerator_kind`, `accelerator_architectures`, `environment_requirements`, `environment_index_url`, `local_budget_seconds`).*
- [x] 4b.35 State cost's shape, never its magnitude, in the published acid-test question (D11c): real run/machine time; local's machine occupancy; remote's metered quota on a service account; that the offered scale is the small one and a larger run is a separate decision; that declining later costs nothing to unwind (D15a — no comparison-named structure was created). Carry the proposed scale's axes, derived from the declaration. State no duration, no quota figure, no service name — this repository already lived through one forge-invented quota figure that lived in a comment nothing read and did not match reality; do not repeat it.
  - *See task 4b.5's own note: the scale axes are carried in the draft (not the published question), per the resolved signature tension. Everything else in this task is in `_validation_offer_question`'s fixed prose, verbatim.*
- [x] 4b.36 Test: the offer states each placement's cost (machine-time spending, local occupancy, remote metered quota); distinguishes the small offered scale from a larger campaign as a separate decision; contains no invented duration, quota figure, or service name — only the proposed scale's own declared axes (spec "The Acid-Test Offer States Cost's Shape, Never Its Magnitude", all three scenarios).
  - *`test_the_offer_states_costs_shape_never_its_magnitude` — asserts every required phrase present and asserts zero digits anywhere in the fixed cost-shape tail of the sentence.*
- [x] 4b.37 Test (D11d): with `__levels__` empty, a step declaring `placement: "remote"` still routes identically through `flow_acts`; only the walk's grading falls back from by-rung to walked/not-walked. The draft's placement section does not read, or let a reader infer, that an empty ladder rules out a worker (spec "An Empty Declared Rung Ladder Does Not Constrain Placement", both scenarios).
  - *`test_an_empty_ladder_routes_a_remote_step_identically_grading_by_walk`, `test_empty_levels_does_not_rule_out_remote_placement`.*
- [x] 4b.38 Integration test (D11b — measured, not assumed, so the "no new machinery" claim is held by a test rather than left as prose): an acid-test `__steps__` entry with `placement: "remote"` walks `ACT_GENERATE_JOB` → `ACT_REHEARSE` → `ACT_LAUNCH` through the unmodified, generic `flow_acts`; `generate_job` accepts it with one arm's clone paths; assert against `remote-execution` **unchanged** — no acid-test-specific branch anywhere in that path (spec "A Remote Acid-Test Step Reaches A Worker Through The Existing, Unmodified Remote-Execution Path", scenario 1).
  - *`AcidTestRemoteExecutionIntegrationTests.test_flow_acts_routes_a_remote_acid_test_step_generically` (routing) and `.test_a_remote_acid_test_step_generates_a_job_folder_identically` (a REAL `jobfolder.generate_job` call, unedited, `verify_pin_preconditions` mocked out the same way `test_remote_execution.py`'s own `NotebookGenerateJobTests` already does — `ACT_REHEARSE`/`ACT_LAUNCH` themselves are `WALK_STOPS_AT` states this engine never performs by design (`walk` stops at a launch and has no path to `submit`), so the walk-level proof covers generation and the stop, matching every other step's own contract).*
- [x] 4b.39 Test: `resolve_clone_paths()` validates the acid test's smaller single-arm import surface using the identical check every other step uses, with no single-arm branch written (spec, scenario 2).
  - *`test_the_clone_path_check_needs_no_single_arm_branch`.*
- [x] 4b.40 Test: a remote acid-test job folder carries the notebook already chosen for the run via `--run-notebook`, never a second remote-only implementation of it (spec, scenario 3).
  - *`test_the_remote_run_carries_the_notebook_already_chosen`.*
- [x] 4b.41 Confirm and test that `jobfolder.generate_job` writes `tools/<service>/<job-name>/` (`TOOLS_DIRNAME`) — `remote-execution`'s own output root, outside all three `materialize` stage lists — so generating a job folder for an acid test cannot touch `harness_destinations()` even in principle. This extends D15a's positive domain.
  - *`test_the_job_folder_lands_under_tools_outside_every_materialize_stage_list` — checks the generated path against `scaffold_destinations`/`object_destinations`/`harness_destinations` all three, not `harness_destinations` alone.*
- [x] 4b.42 Extend the D15a no-benchmark-structure invariant test (task 4b.17) to run **once with `placement: "local"` and once with `placement: "remote"`**: after accepting, wiring, and running the acid test under each placement — no path under `src/<Package>_Benchmark/` exists, `harness_gaps()` is unchanged, no receipt entry carries `stage: "harness"`, and no written destination — including the generated job folder's own contents — appears in `harness_destinations(name)` (spec "An Accepted Acid Test Writes Only Into The Method's Own Surfaces...", all local/remote scenario pairs — proves the job-folder path is not a back door).
  - *`AcidTestInvariantTests.test_a_wired_and_run_remote_acid_test_creates_no_benchmark_package`, paired with the local test from 4b.17 — both check `harness_gaps` before/after and enumerate the generated job folder's own file contents against `harness_destinations()`.*
- [x] 4b.43 Document the `## Boundary` note in `SKILL.md`'s new `### nextStep: "validate"` section (task 4b.23): the live target's unread `__environment__` literal is almost certainly meant to feed the remote path's environment-provisioning input, but wiring it through is explicitly out of scope for this change — named so the next person finds it, never wired here. Then run both suites (`npm test` and the Python unittest suites) green — **this closes Unit 4b.**
  - *Added as a "Boundary, named rather than built" paragraph inside the `validate` section (not a separate top-level heading — the task's own wording places it IN that section). `npm test` 640/640. `tests.test_proposal_implementation` 1604 tests, 0 real failures (31 pre-existing/environmental, git-stash-confirmed identical to pristine HEAD). `tests.test_implementation_seal` and `tests.test_experiments_seal`: green modulo the single "uncommitted seal corpus" control (clears on commit, Units 1/2/4's own documented pattern). `tests.test_implementation_pair`/`tests.test_experimental_implementation`: 4 of their own mutation-seal-survival tests fail for the identical uncommitted-corpus reason, also clearing on commit. `tests.test_implementation_domain_lock` 28/28.*

## Unit 3 — The first flow stops creating the benchmark package

- [x] 3.1 RED then remove: `src/<Package>_Benchmark/__init__.py` out of `scaffold_destinations()`/`scaffold_kit_source()`, into `harness_destinations()`/`harness_kit_source()` (three entries → four).
  - *`RED` observed via the existing `ScaffoldInstructionsAgreementTests`/`HarnessPlacementTests`/`MaterializeStageHarnessWriterTests` fixtures going red the moment the list moved (see 3.15's own note) — no new RED test needed for the list flip itself since the existing agreement tests already assert `materialize.py` writes exactly `scaffold_destinations`.*
- [x] 3.2 Test: a fresh target completing the scaffold stage has no `<Package>_Benchmark` directory anywhere under `src/` (spec "Fresh Target Has No Benchmark Directory After Scaffolding").
  - *`FreshFlowATargetEndToEndTests.test_no_benchmark_directory_exists_anywhere_under_src` (new, task 3.18's own class) plus `MaterializeBenchmarkDeclarationTests.test_a_fresh_scaffold_does_not_write_the_benchmark_declaration`.*
- [x] 3.3 Test: acceptance materializes the benchmark package only via the wiring-first rung; no fifth materialization stage is invoked (spec "Acceptance Materializes The Benchmark Package Via The Harness Stage").
  - *Already covered end to end by the pre-existing `MaterializeStageHarnessWriterTests` (harness stage, unedited apart from the fixture fix in 3.15) and `_write_kit_stage`'s own shared three-stage machinery — no fourth/fifth stage exists in the engine; `STRUCTURE_GAP_STAGES` still names exactly three.*
- [x] 3.4 RED then narrow: `cmd_probe`'s `declare-first` condition from `resolved["status"] in ("absent","undeclared")` to `"undeclared"` only (D4); confirm `"absent"` targets fall through to `benchmark`/`declined`/`validate` instead.
  - *RED observed directly: `DeclareFirstBeforeTheRunTests`/`DeclinedComparisonTests` immediately reported `report-first` instead of `benchmark` for an "absent, never-offered" fixture once the narrowing landed — see this unit's own report for the follow-on correction this measurement forced (D13 placement, below).*
- [x] 3.5 Test: an unrecorded `src/<Package>_Benchmark/__init__.py` is flagged `UNRECORDED_SCAFFOLD` against the harness list; `materialize --adopt` records it scoped to the correct stage list (spec "Materialization Receipt Machinery... Against The New Destination Lists", remaining scenarios).
  - *`_kit_structure_gaps`'s generic `UNRECORDED_SCAFFOLD` key (reported for scaffold/objects/harness alike, per its own existing docstring) already covers the harness list unedited; `_kit_destination_stage` reclassifies the path to `"harness"` automatically from the list membership alone — confirmed via the regenerated seal corpora's own `unrecordedHarness` entries (task 3.19) rather than a new unit test, since the mechanism is generic and pre-existing.*
- [x] 3.6 Apply the derived-count rule (D8): `scaffold_destinations` at ten unconditional entries, `scaffold_gaps`'s maximum at twelve (ten + up to two conditional anchors), computed at read time. Remove every hand-written gap-count/ladder-count literal from engine docstrings (`scaffold_destinations`, `scaffold_structure_gaps`, `all_kit_destinations`, `harness_destinations`, `_stage_objects`, the declaration resolvers) and doctrine prose — the noun replaces the numeral.
  - *Confirmed by measurement: `len(scaffold_destinations("Method")) == 10`, `len(harness_destinations("Method")) == 4`, `len(all_kit_destinations("Method")) == 17` (unchanged total, redistributed). `DerivedScaffoldCountSweepTests.test_scaffold_gaps_maximum_is_derived_not_transcribed` pins both counts as derived, never a literal.*
- [x] 3.7 Delete `all_kit_destinations`'s arithmetic-identity docstring assertion ("Eleven + three + three = seventeen").
  - *`DerivedScaffoldCountSweepTests.test_all_kit_destinations_docstring_carries_no_arithmetic_identity` pins the deletion.*
- [x] 3.8 Test: a grep-style check that no doctrine file (`SKILL.md`, `references/usage.md`, `README.md`, engine docstrings) states a scaffold-gap or ladder count as a hand-written numeral, and no new numeral replaces it (spec "The Gap Report Is Derived, Not Transcribed").
  - *`DerivedScaffoldCountSweepTests.test_no_doctrine_file_states_the_old_scaffold_or_kit_destination_counts` — scoped by co-occurring keyword (`scaffold`/`destination`/`kit`) rather than a blanket word ban, since "eleven"/"seventeen" also legitimately count unrelated things elsewhere in these same files (CLI subcommand count, a historical shard-clone file count) that this change does not touch. Measured reachable red on pristine HEAD (15 offenders via `git stash`) before the sweep; 0 after.*
- [x] 3.9 Update `SKILL.md`'s step 5 table (benchmark package moves scaffold → harness row), the "Conversion, then benchmark" paragraph, and the Decision Gates row.
  - *Step 5's table row removed; the harness-wiring table (harness stage) gained the `__init__.py` row instead, with its own re-derived prose ("the rows marked `authored:`", no count). "The benchmark declaration, and its five blocks" section, `declare-first`'s own section, and its Decision Gates row all rewritten to state `absent` is the ordinary pre-acceptance state, never routed to `declare-first`.*
- [x] 3.10 Fix `references/usage.md`'s already-stale ladder sentences ("Eleven values are possible", "The other three have no section", "Nine of the eleven publish resolve", "null only at ... the two answers") — derive rather than transcribe a corrected count; point at `NextStepSectionCoverageTests.test_every_value_the_cli_can_return_is_accounted_for` instead.
  - *Rewritten to name the values and point at the derivation test rather than assert any count; also updated the worked scaffold-file list, the `OBJECT_MAP_NOT_APPROVED`/`NOT_A_KIT_DESTINATION` rows, and added the "Materialize the harness" section's own `__init__.py` destination.*
- [x] 3.11 Fix `cmd_probe`'s stale comment ("Two of the eleven answers publish nothing") the same way.
  - *Rewritten to name the mechanism (`NO_SECTION`) and point at the derivation test, no numeral.*
- [x] 3.12 Update `README.md`'s `nextStep` ladder documentation and `src/` tree to move the benchmark package from scaffold to harness (added by design; not in the proposal's original Affected Areas).
  - *`src/` tree diagram and its own paragraph rewritten (in Spanish, matching the document's established register): the benchmark package is a harness-only destination now, and `__implementation__`'s new home is named. **Scope note, reported rather than silently expanded**: README's base `nextStep` ladder enumeration (five rungs + four blocks, missing `declared`/`validate`/`piloted`/`declare-first`/etc. entirely) was already stale before this change (design §1.3) for reasons unrelated to Movement 3 — task 3.12's own wording scopes this unit to "the benchmark package from scaffold to harness", not a full ladder rewrite spanning every prior unit's own additions; left as pre-existing staleness outside this unit's assigned scope, named here rather than silently patched.*
- [x] 3.13 Regression-verification: exercise `nothing-to-compare`, `already-benchmarked`, `benchmark`, `declined`, `validate` each under its own precondition, confirming none is reordered or shadowed by this unit's list flip (spec "Introducing The Acid-Test Follow-Up Does Not Reorder Or Shadow Any Other Ladder State"; "Every Pre-Existing Probe Rung Fires Under Its Exact Prior Condition").
  - *`DeclinedComparisonTests.test_all_five_named_states_fire_under_their_own_precondition_alone` (new), each in its own isolated fixture.*
- [x] 3.14 Regression-verification: a genuinely owed repair (an unfinished step in the target's own declared flow) still outranks a declined-but-unresolved comparison/acid-test pair — explicit test (spec scenario "A genuinely owed repair still outranks the acid-test offer").
  - ***Measured false against Unit 4b's own shipped placement, and corrected here — not implemented around.*** Unit 4b placed the three-way `benchmark`/`validate`/`declined` branch FIRST in `cmd_probe`'s `if`/`elif` chain (task 4b.11's own note), and its own `AcidTestShadowEnumerationTests` proved `declined` wins over every repair unconditionally — the literal opposite of this unit's spec requirement. Measured, not assumed: forcing all six repair preconditions true on a twice-declined target returned `wiring-first` once this unit's own D4 narrowing landed, not `declined`, before any fix. Root cause narrower than Unit 4b's own reasoning assumed: only `report-first` reads the benchmark declaration without already being naturally shielded when `resolved.status == "absent"` (`env-first`/`wiring-first`/`search-first` all read fields that are already falsy/`None` on an absent declaration, measured directly rather than assumed symmetric). Fix: (a) `report-first` gained an explicit `resolved.status != "absent"` guard: without it every first-flow target that had never even been offered a comparison reported `report-first` instead of `benchmark`, reintroducing one state later the exact "a rung whose premise is a document disagreeing with a run, when no report exists yet" accident `declare-first` exists to prevent; (b) the three-way branch moved from first to LAST among the overrides, matching design D13's own literal, never-revised text ("last among the overrides, after `report-first`"). `AcidTestShadowEnumerationTests` rewritten to prove the corrected (opposite) invariant; `test_declare_firsts_second_branch_now_outranks_declined_too` records that `declare-first`'s own second branch outranks `declined` too now, for the identical structural reason. Flagged here for the owner/`sdd-spec`: design §D13's own text was already correct; Unit 4b's applied-phase divergence note (tasks.md, "What Unit 4b reported") should be read as superseded by this correction, not as a standing tension.*
- [x] 3.15 Complete the bulk update of `tests/test_proposal_implementation.py`'s remaining `_Benchmark`/`report_digest`/`premises` hits not already touched by Units 1, 2, 4, or 4b.
  - *Fixtures repaired: `HarnessPlacementTests.copy_step` (the stage-2 table now also stages from `assets/kit/src_benchmark/`, not only `assets/kit/nb/`); `MaterializeStageHarnessWriterTests` (class docstring + the `DESTINATION_CONFLICT` race fixture's missing `mkdir(parents=True)`, since the harness parent directory is no longer created by scaffold); `KitBuiltTargetIntrospectionTests` (the bench `entry`/`report` declaration edit split out of `_declare_object_map` into its own `_declare_benchmark_entry_and_report`, run AFTER `_fully_materialized_all_stages` returns rather than before the harness stage that now creates the file); `FidelityUndeclaredTests` (absent-benchmark note now asserts `structure.harnessGaps`, per D3); `MaterializeBenchmarkDeclarationTests` (rewritten in full — the class's whole premise, "materialize.py creates the bench package", is now false; repurposed to prove the scaffold does NOT write it, the kit source still parses empty with the right shape, and `harness_gaps` — not `scaffold_gaps` — reports it missing); `MaterializeScriptStaysTestOnlyTests` (its own count-matching test conflicted with D8 and is superseded by a no-count assertion); `StageTwoInstructionsTests.COPY_STEP` (gained the `__init__.py` mapping); `DeclinedComparisonTests`/`DeclareFirstBeforeTheRunTests`/`AcidTestShadowEnumerationTests` (D4/D13 correction fallout, task 3.14's own note). All changes confirmed against `git stash`-verified pristine-HEAD baselines before being classified as real (not environmental).*
- [x] 3.16 Complete the `tests/test_remote_execution.py` hits, if any, affected by the scaffold/harness list flip and not already resolved by Unit 1's discovery task.
  - *Re-measured: all 123 `_Benchmark` hits remain the single literal `FEM_TOLLA_Benchmark` (generic job-folder fixture data), matching Unit 1's own task 1.9 finding exactly; grepped for `scaffold_destinations`/`harness_destinations`/`cmd_probe` call sites in this file — none. No edits required. The module itself does not import in this sandbox (`ModuleNotFoundError: No module named 'requests'`) — confirmed pre-existing via `git stash` (identical failure on pristine HEAD), unrelated to this change.*
- [x] 3.17 Triage and update the 6 `_Benchmark` hits in `tests/test_experimental_implementation.py`.
  - *All 6 are hand-built fixtures writing the bench declaration directly to disk (never through `scaffold_destinations`/`materialize.py`), so the list flip does not touch them. Full suite run: 63/63 green, unaffected by the shared-engine ladder correction (task 3.14) either — `experimental-implementation`'s own fixtures never exercise the `"absent"` fall-through state this unit's D4/D13 work touches.*
- [x] 3.18 E2E test: a fresh Flow A target, end to end — after scaffolding, no `_Benchmark` directory exists; `verification.ipynb` executes and stamps; `previous_implementations()` is empty; the flow reports `nothing-to-compare`.
  - *New `FreshFlowATargetEndToEndTests` (4 tests) using the real `scripts/materialize.py` (not a hand-built fixture). Three pass; `test_verification_notebook_executes_and_stamps` hits the identical, already-documented pre-existing environmental wall every `NotebookSealAgreementTests` execution test hits in this sandbox (`ModuleNotFoundError: No module named 'numpy'`, same source line) — the 32nd instance of the same confirmed-pre-existing class, not a new one; the other three assertions (no benchmark directory, empty baselines, `nothing-to-compare`) are unaffected and green.*
- [x] 3.19 Regenerate both sealed corpora for the scaffold/harness list flip and `declare-first`'s narrowing; read the diff, account for every moved case, and confirm the corpora now reflect all five units' cumulative changes.
  - *`tests/seal/digests.json`: `verify-a`/`verify-b`/`verify-t` moved (+4 bytes each); read directly via `test_implementation_seal.py`'s own `_captured_results()` cache rather than assumed — the sole content change is `src/Seal_Benchmark/__init__.py` moving from `structure.unrecordedScaffold` to `structure.unrecordedHarness` in each fixture's own output, exactly the D4 list-flip's intended, measured consequence (spec "An unrecorded benchmark package is flagged"). `probe`/`materialize`/`plan-a`/`plan-b` unmoved — their own fixtures do not exercise the changed paths in a byte-visible way. `tests/experiments_seal/digests.json`: `verify-a`/`verify-a-declared`/`verify-b`/`verify-b-declared`/`verify-b-undeclared`/`verify-t` moved the identical way (+4 bytes each); `propose` also moved but stays excluded from comparison/roster via `KNOWN_UNSEALED_REASONS` (its own embedded timestamp, Units 4/4b's own precedent). Regenerated via `seal_capture.py`/`experiments_seal_capture.py` (each runs every case twice and refuses to write on any disagreement; both runs self-consistent).*
- [x] 3.20 Run both suites (`npm test` and the Python unittest suites) green — this closes the change.
  - *See this unit's own closing report for full numbers.*

---

## Movement 6 — a decision already taken can change

> Design §3c, revision 5 (D17–D24). Designed against **what units 1–3 shipped**
> (`b493151` → `432da9f` → `45eae9d` → `cb965c4` → `330c5f1`), not against earlier
> design prose — three corrections in D17 are load-bearing: the three-way branch
> sits last among the overrides **only because Unit 3 moved it there**; D5b's
> "acceptance = materializing the harness" **is shipped**, and is exactly the hole
> Part A below fills; and the published acid-test question does **not** carry
> `scale`'s axes (a literal 4-parameter signature, unlike D11c/D14b's prose).
>
> **Standing constraints, binding on every task below:**
> - The engine interprets no free text, ever. The only new surface is one closed
>   `yes`/`no` token on `discuss` (D19) — `cmd_offer`'s `OFFER_ANSWER_NOT_A_TOKEN`
>   is **precedent only**; `cmd_offer` itself MUST NOT be reused (its own
>   docstring states no code path ever reads an offer event's fields back into a
>   later decision, and reuse would mint a launch authorization for a decline).
> - **Absent-token migration rule (D20):** a legacy answered bucket with no
>   `decision` field reads as `no`. Reading it as undecided would re-fire a
>   declined offer on every existing target on the first pass.
> - **Unit 3's ladder ordering is not to be touched.** The three-way branch stays
>   last, `report-first`'s `resolved.status != "absent"` guard stays. `build-first`
>   is a fourth arm inside that existing branch, never a new position, never a
>   reorder.
> - **A transition undeclares; it never deletes.** No destructive filesystem act
>   may be justified by an assumption about recoverability the forge cannot check.
> - No `Co-Authored-By` or AI attribution in any commit this movement produces.
>
> **Forecast discipline (owner's own instruction):** treat ~300/~1000/~700 as
> **floors**, not estimates. In this chain 4b landed at 2.5× its forecast and 3 at
> 1.05×; none has landed under. Test ripple through already-shipped classes
> (`DeclinedComparisonTests`, `AcidTestShadowEnumerationTests`,
> `DeclareFirstBeforeTheRunTests`, both roster classes, both sealed corpora) is
> what blew every prior forecast, and Part A's token changes the *meaning* of an
> already-answered bucket — the exact profile that produced 4b's 2.5×.

### Unit 6c — the anti-leak lock (Part C, ~300 floor — lands first, independently)

> Touches no engine code, no ladder, no corpus. Closes a measured leak that is
> open right now. No reason to hold it behind the two larger units.

- [x] 6c.1 Fix the compound-word gap (D24, layer 1): wherever `target_words` calls
      `words.update(self.split(target.name))`, also add the **undivided compound**
      `target.name` itself (normalized) as its own candidate word — each split
      part's lexicon admission was argued on its own merits, and those arguments
      do not extend to the whole.
      - *`words.add(target.name.lower())`, right beside the existing split call.*
- [x] 6c.2 Test: a target named from two ordinary, individually-admitted words
      (shaped after `Domain_Adaptation`) survives into `derived_denylist()`'s
      output as its own compound word, even though both of its parts are
      individually subtracted by `FORGE_LEXICON`.
      - *`test_the_compound_survives_even_though_both_parts_are_admitted`, plus
        the pre-existing `test_rule_b_names_the_file_and_the_word_a_planted_leak_is_in`
        now asserting `nimbus_benchmark` too — shaped after `Domain_Objective`
        (two real `FORGE_LEXICON` words), never the live target's own name.*
- [x] 6c.3 Fix the case gap (D24, layer 2): add `re.IGNORECASE` to `leaks()`'s
      `re.search(rf"\b{re.escape(word)}\b", text)` so a title-cased or
      differently-cased mention still matches the lowercased denylist entry.
      - *Extracted into `word_appears(word, text)`, carrying `re.IGNORECASE`
        itself rather than trusting every caller to pre-lower `text` — load-bearing
        once 6c.7's widened surface stopped lowering test-file commentary.*
- [x] 6c.4 Explicit test, not an assumption (owner's own instruction — `\b` treats
      `_` as a word character): once the compound is in the denylist, `leaks()`'s
      `\b...\b` boundary actually matches a real `Domain_Adaptation`-shaped
      mention. Do not infer this from the parts' own boundary behavior.
      - *`test_the_word_boundary_actually_matches_a_real_compound_mention`
        (positive: matches inside a real sentence; negative: does not fire
        inside a longer compound merely sharing a prefix).*
- [x] 6c.5 Test: a mention cased differently from the denylist's own lowercased
      entry is still caught (spec "The Anti-Leak Guard's Word Comparison Does Not
      Depend On Matching Case", scenario 1).
      - *`test_a_differently_cased_mention_is_caught_regardless_of_the_denylists_own_case`,
        proven directly against `word_appears` rather than through
        `scannable_text`'s own incidental lowering.*
- [x] 6c.6 Test: a hypothetical second live target's compound name, planted in any
      casing into a forge file as a test, is caught with no per-target exemption
      list required (spec, scenario 2 — "the fix closes the class, not the one
      instance").
      - *`test_a_second_targets_compound_needs_no_exemption_list` — two scratch
        targets, second one's compound (`LOCAL_PIPELINE`, uppercase) caught by
        the identical derivation, no list anywhere names it.*
- [x] 6c.7 Fix the scan-surface gap (D24, layer 3): widen the guard's scan (today
      `SCAN_ROOT = SKILLS_ROOT`, `.claude/skills/` only) so test-file commentary —
      fixture descriptions, comments, string content not meant as a neutral
      placeholder — is included. Scope narrowly to commentary/fixture-description
      content, not every string literal in every test, to avoid a false-positive
      machine.
      - *New `rule_b_documents(root, tests_root)` (kept apart from the shared
        `guarded_documents`, so rules A/C stay unwidened) adds every `*.py` under
        `tests/`, THIS file included — the measured leak sat in its own fixture
        commentary. New `commentary_text()` extracts only `tokenize` COMMENT
        tokens and `ast.get_docstring` text, never an ordinary string literal —
        `test_a_neutral_fixture_name_is_not_mistaken_for_a_leak_by_the_widened_scan`
        pins the exemption directly, planting the real denylist word as a bare
        string-literal fixture value beside a comment saying so, and confirms it
        is not flagged.*
- [x] 6c.8 Test: a live target's repository directory name in a test file's own
      comment is caught by the widened guard, naming the file and the word (spec
      "No Live Target's Own Name Appears Anywhere In This Forge, In Any Casing",
      scenario 1).
      - *`test_a_live_targets_name_in_a_test_comment_is_caught_by_the_widened_scan`
        — a synthetic compound (`Domain_Objective`) in a scratch module's own
        docstring, never the real target's name planted a second time.*
- [x] 6c.9 Test: a neutral, invented fixture name is not mistaken for a leak by the
      widened scan (spec, scenario 2).
      - *`test_a_neutral_fixture_name_is_not_mistaken_for_a_leak_by_the_widened_scan`
        (see 6c.7's own note — same test covers both).*
- [x] 6c.10 Remove and reword the one measured instance: the fixture comment Unit 2
      added in `tests/test_proposal_implementation.py`, naming `Domain_Adaptation`
      — reword to say "a live target", never which. Zero occurrences under
      `.claude/` already; this is the test-surface instance, not a doctrine leak.
      - *`LiveTargetMigrationFixtureTests`'s own class docstring reworded.
        Measured, not assumed: mutation-tested by temporarily restoring the old
        wording in a throwaway copy of the file and confirming the widened scan
        (task 6c.7) genuinely catches it before the reword, and confirming
        `test_rule_b_finds_no_target_vocabulary_in_the_forge` is green against
        the real repository only after it.*
- [x] 6c.11 Run both suites (`npm test` and the Python unittest suites) green,
      confirming the corrected guard passes on the repository as it now stands.
      - *`npm test`: 640/640 (JS untouched). `tests.test_proposal_implementation`:
        1619 tests, 32 pre-existing/environmental failures (25 failures + 7
        errors) — identical set reproduced on pristine HEAD via `git stash` A/B
        (same class every prior unit documented: missing `torch`/`numpy`/`pytest`
        under the required `python3.12` interpreter), 0 new. Zero new
        `FORGE_LEXICON` admissions were needed — measured before writing any
        test: the widened scan's only real hit anywhere in the whole forge was
        the one instance this unit's own task 6c.10 reworded.
        `tests.test_implementation_domain_lock`: 28/28 (unaffected — a
        different lock, `M5_PINNED_RESIDUE`, over the engine directory, not
        this test-suite-internal guard). `ForgeVocabularyDerivedGuardTests`
        itself: 18/18.*

### Unit 6a — a decision can be reopened (Part A, ~1000 floor)

> Depends on nothing but the shipped chain (Units 1–3). Delivers D19–D21 whole —
> splitting the token from `build-first` would ship a `yes` nobody can act on.

- [x] 6a.1 Add an optional `decision` field to `discuss`: closed domain
      `yes`/`no`, refusing a new code `DISCUSS_DECISION_NOT_A_TOKEN` for anything
      else — `cmd_offer`'s exact refusal shape and closed domain, reimplemented on
      `discuss` (D19), never by reusing `cmd_offer`.
- [x] 6a.2 Test: `discuss --decision yes` / `discuss --decision no` are accepted
      and recorded on the ledger event; any other value is refused
      `DISCUSS_DECISION_NOT_A_TOKEN`, never interpreted (spec "A Declined Decision
      Reopens On Its Own Answer Alone...", scenario "An answer outside the closed
      domain is refused, never interpreted").
- [x] 6a.3 Test: `cmd_offer` itself is untouched by this unit — no code path reuses
      it, and its own documented "never read back" invariant still holds.
      - *`test_cmd_offer_is_untouched_by_the_discuss_decision_capability`:
        static-source check (`cmd_discuss`'s own source never calls
        `cmd_offer(...)` or reuses `"OFFER_ANSWER_NOT_A_TOKEN"`) plus a
        confirmation that `cmd_offer`'s own write-only-history docstring
        invariant is still stated.*
- [x] 6a.4 Add the absent-token migration rule (D20) to `_answered_event_from`/the
      bucket reader: an answered event with no `decision` field reads as `no`.
      Test: a legacy answered bucket with no `decision` field is read as declined,
      not undecided, on the first pass after landing — no re-fire from the
      migration itself.
      - *Implemented as a new pure reader, `_decision_token_from_event`, rather
        than inside `_answered_event_from` itself — `_answered_event_from`
        already has a stated, narrower contract (the bucket's own last event or
        `None`) that several other callers depend on unchanged; the migration
        rule lives one layer above it, in the function that actually interprets
        the token.*
- [x] 6a.5 Test: no existing ledger event is reinterpreted or rewritten (P4 still
      holds) — the migration rule changes only how an absent field is read.
      - *`test_reopening_appends_never_rewrites_the_original_decline_event`
        asserts the original decline's own ledger line is byte-identical after
        a reopening answer is appended (append-only, never an edit-in-place).*
- [x] 6a.6 Grow `decisions.comparison` and `decisions.validation`'s payload shape
      with a `decision` member beside `state`/`at`/`asked`, carrying
      `"yes"`/`"no"`/`None` — the same payload key Units 4 and 4b shipped keeps
      its shape and name, only grows.
- [x] 6a.7 Test: `decisions.comparison.decision` / `decisions.validation.decision`
      report `"yes"`/`"no"`/`None` correctly across unanswered / declined /
      accepted-not-built states.
- [x] 6a.8 Add the `"build-first"` rung: `kind = NEXT_STEP_REPAIR`,
      `choice = NEXT_STEP_REPAIR_CHOICE`; `drafts = ("wiring",)` when the
      comparison's own decision is `"yes"`, `drafts = ("validation",)` when the
      acid test's is — bare-literal assigned (D5c), the routing fact threaded from
      the branch rather than recomputed (`_declare_first_publication`'s own
      precedent, D21).
      - *Divergence, measured and reported, not implemented around: a literal
        reading of "`drafts` = `("wiring",)` or `("validation",)`" cannot be the
        roster's own STATIC `PROBE_NEXT_STEPS["build-first"]["drafts"]` tuple,
        because `NextStepPublicationRosterTests.test_every_entry_names_a_drafts_tuple_of_known_builders`
        holds every entry to one fixed tuple, known at module-definition time —
        and mutating that shape-lock test was out of this unit's own mandate
        (D19-D21 only). Resolved by keeping the roster's own tuple empty
        (`declare-first`'s own precedent: a repair whose published TEXT already
        varies by a branch-threaded fact while its roster `drafts` stays `()`)
        and resolving the ONE actual draft dynamically in `cmd_probe`, from the
        identical `facts["buildFirstArm"]` fact `_build_first_publication`
        itself reads. The OBSERVABLE behaviour matches the design's plain-English
        sentence exactly — `test_build_first_never_publishes_both_drafts_at_once`
        proves exactly one of `wiring`/`validation` is non-`null` at this rung,
        never both — only the roster's own static declaration differs from a
        literal-tuple reading. `NextStepPublicationRosterTests` needed zero
        changes as a result (confirmed green, unmodified).*
- [x] 6a.9 Wire the four-way branch as a **fourth arm inside Unit 3's existing
      last-among-the-overrides branch** — same position, same
      `resolved["status"] == "absent"` guard, **never a new position**:
      unanswered → `benchmark`; decision "no", acid test open → `validate`;
      decision "no", both settled → `declined`; decision "yes", nothing built →
      `build-first`. Unit 3's `report-first` guard and this branch's own position
      are **not to be touched** — the one thing this movement must not do.
      - *Verified untouched: `report-first`'s own `resolved["status"] != "absent"`
        guard and every repair override's own `elif` line above the four-way
        branch are byte-identical to Unit 3's own shipped code — the diff for
        this task touches only the one `elif`/branch body that was already
        `benchmark`/`validate`/`declined`.*
- [x] 6a.10 Test: no reordering occurred — the shadow-enumeration class still
      proves every repair override outranks the four-way branch, evaluated last,
      exactly as Unit 3 left it.
      - *`AcidTestShadowEnumerationTests.test_every_repair_override_still_outranks_an_accepted_but_unbuilt_decision`
        (new): every repair guard forced true simultaneously on a target that
        already accepted the comparison (`decision: "yes"`, nothing built) still
        reports the owed repair, never `build-first`.*
- [x] 6a.11 Test: answering `decision: "yes"` reopens the decision immediately,
      with nothing yet built — reported as accepted, not declined, not silent
      about the contradiction (spec scenarios "Accepting reopens the decision
      before anything is built", "An accepted-but-unbuilt decision is never
      reported as declined").
- [x] 6a.12 Test: answering `decision: "no"` again after a prior `"yes"` leaves it
      declined (spec scenario "Declining again leaves it declined").
- [x] 6a.13 Add `SKILL.md`'s new `### nextStep: "build-first"` section: what it
      means, which draft it carries, that it prescribes work. Must **not** join
      `NO_SECTION`.
- [x] 6a.14 Update `NextStepSectionCoverageTests.all_next_steps()`,
      `NextStepPublicationRosterTests` (repair-step count grows by one;
      `build-first` correctly excluded from `NO_SECTION`), and
      `references/usage.md`'s ladder documentation for the new rung.
      - *`all_next_steps()` itself needed no change (it scrapes `cmd_probe`'s own
        source); only the explicit expected-set literal in
        `test_every_value_the_cli_can_return_is_accounted_for` gained
        `"build-first"`. `NextStepPublicationRosterTests`'s own assertions ran
        green with zero edits — see 6a.8's own note for why the roster-shape
        tests never needed to move. `references/usage.md`: the section list, the
        `wiring`/`validation` reporting paragraph (now three/two answers, exactly
        one non-`null` at `build-first`).*
- [x] 6a.15 Record the D5b supersession explicitly (owner's own instruction — do
      not answer this silently): update this file's "Notes carried forward" / "What
      Unit 4 reported" annotations to state that **D5b is superseded by D19, not
      merely amended.** Unit 4's "acceptance = materializing the harness" was
      correct for a prose answer and is exactly the hole this unit fills — once
      the closed token exists, `decision: "yes"` reopens the decision **without**
      the structure existing first. Flag for the owner/`sdd-spec` to confirm this
      reading rather than treating design's own still-unchecked `D5b vs sdd-spec`
      open question as live.
      - *Recorded under "What Unit 4 reported", below its own D5b note, per this
        task's own instruction — see that section.*
- [x] 6a.16 Regenerate both sealed corpora for the token field, the `build-first`
      rung, and the four-way branch — budget for this being the heaviest ripple in
      the unit (the same profile that produced 4b's 2.5×): expect
      `DeclinedComparisonTests`, `AcidTestShadowEnumerationTests`,
      `DeclareFirstBeforeTheRunTests`, and both roster test classes to move. Read
      the diff, account for every moved case.
      - *Measured, not the forecast: the "heaviest ripple" landed narrower than
        expected. `DeclinedComparisonTests` needed two dict-literal updates
        (the new `decision` member); `AcidTestShadowEnumerationTests`,
        `DeclareFirstBeforeTheRunTests` and both roster test classes needed
        ZERO changes — every pre-existing assertion in those five classes
        passed unmodified, because none of them compares the full `decisions`
        dict by equality and the roster's own `build-first` entry carries an
        empty `drafts` tuple (6a.8's note). Only `probe`/`discuss` moved in
        either sealed corpus (`tests/seal/digests.json`,
        `tests/experiments_seal/digests.json`) — regenerated via
        `tests/seal_capture.py`/`tests/experiments_seal_capture.py`, diff read
        case by case, nothing else moved.*
- [x] 6a.17 Run both suites green before closing the unit.
      - *See "What Unit 6a reported" below for full verification evidence.*

### Unit 6b — the transitions (Part B, ~700 floor)

> Depends on 6a: D22 *is* 6a's token, and D23's down direction records its
> decision with the same field. Chaining after 6a keeps this unit small enough to
> be one.

- [ ] 6b.1 Test (D22 — hold the "no new machinery" claim to a test, not prose):
      re-answering the comparison bucket with `decision: "yes"` on a target whose
      acid test has already run routes to `build-first` → `materialize --stage
      harness`, using only 6a's token and rung — no new constructor, no new
      state (spec "Adding A Comparison After An Acid Test...", scenario "Wanting a
      comparison after a run acid test is discussed, not automatic").
- [ ] 6b.2 Test: the acid test's own record is neither deleted nor overwritten
      when a comparison is subsequently built and run, and continues to answer
      the question it was run to answer (spec, scenario "The acid test's own
      record survives the addition of a rival").
- [ ] 6b.3 Measurement task (owner-handed, design's own open question, D23a — do
      not assume, this chain has been burned twice by assumed answers): measure
      whether `validate` should become reachable **only from `already-benchmarked`**
      (a current, complete record) or from **any state with a benchmark package
      present**, including a stale or piloted record. Design ruled the narrower
      reading but explicitly did not settle the stale/piloted case; the spec does
      not settle it either. Escalate to the owner/`sdd-spec` for an explicit
      ruling before 6b.4 lands; do not silently pick one.
- [ ] 6b.4 Make `validate` reachable from `already-benchmarked` (the narrower,
      designed reading, pending 6b.3's confirmation) with a comparison-present
      precondition (D23a).
- [ ] 6b.5 Reshape what `validate` reports when reached from a completed
      comparison (D23b): **not** an offer to build a run — a reporting state that
      names where the answer already lives (the comparison's own record and the
      arm that is the method) and asks whether to change the question being asked
      of it. Branched publication under the same rung name, the
      `_declare_first_publication` precedent again.
- [ ] 6b.6 Test: the acid-test question, asked after a comparison has already run,
      is answered from the comparison's own existing record with no new run
      required (spec "Treating An Existing Comparison As Also Answering The Acid
      Test...", scenario "The acid-test question is answered from the existing
      comparison record").
- [ ] 6b.7 Implement the down-transition (D23c): accepting the "treat the
      existing comparison as also answering the acid test" discussion
      **undeclares** the rival arm — removes its entry from
      `__benchmark__["arms"]` — and does nothing else. Never delete
      `<Name>/Results/…`, executed notebooks, stamps, or ledger events. Discussed
      via a `discuss` bucket with its own one-spelling constructor and 6a's token
      — never automatic.
- [ ] 6b.8 Test: undeclaring the rival arm makes it invisible to
      `armsReached`/`unreachedModules` going forward, while its own recorded
      output remains exactly where it was on disk, untouched (spec "The rival's
      arm is not removed by the transition").
- [ ] 6b.9 Test: the transition never deletes, relocates, or overwrites any record
      or arm's output a prior run already produced, in **either** direction —
      test → comparison and comparison → test (spec "A Completed Run's Evidence
      Is Never Deleted When The Question Being Asked Changes", both scenarios).
- [ ] 6b.10 Regression-verification: the forge performs no destructive filesystem
      act on the strength of an assumption about recoverability it cannot check
      (D23c's second reason) — assert undeclaring an arm issues no delete/move/
      overwrite call anywhere in its own code path (source scan), and that the
      untouched files' own mtimes/hashes are unchanged before and after.
- [ ] 6b.11 Test: both transitions are discussed, never automatic — no code path
      performs either transition without an explicit `discuss` event recording it
      first (spec scenario "Wanting a comparison after a run acid test is
      discussed, not automatic").
- [ ] 6b.12 Update `SKILL.md`'s `### nextStep: "validate"` (and/or
      `"build-first"`) section(s) to describe both transitions, the
      undeclare-not-delete rule, and `validate`'s branched reporting-state
      publication when reached from a completed comparison.
- [ ] 6b.13 Update `references/usage.md` and roster tests for `validate`'s
      widened reachability precondition and its branched publication shape.
- [ ] 6b.14 Regenerate both sealed corpora for the widened `validate` reachability
      and its branched reporting-state publication. Read the diff, account for
      every moved case.
- [ ] 6b.15 Run both suites green — **this closes Movement 6 and the change.**

---

## Notes carried forward, not tasks

- The `AGREED.md`/`AGREEMENTS.md` naming drift is out of scope; fixed as a one-line edit inside 2.16, the commit that already touches that paragraph.
- D9's `materialize.py` rewrite is settled: the owner ruled rewrite over deletion, and Unit 1 (`b493151`) already shipped it. `the-skill-materializes-not-the-agent`'s deletion proposal (tasks 4.4/4.5) did not prevail here; no open decision remains to track.
- Design's open questions on D5b, D14a and `__implementation__`'s name were resolved in favor of the design by revision 3 of the spec reconciliation; no divergence remains for `sdd-apply` to arbitrate.
  - **Correction, Unit 4 apply pass: D5b is NOT settled in the design document itself.** `__implementation__`'s name reads as genuinely resolved (Unit 2 shipped it, matching the design's own choice). But design.md §11 ("Open questions") still carries `D5b vs sdd-spec` as an unchecked `- [ ]` item as of design revision 4, worded as a live question the design itself has not closed. Task 4.11 below implements per D5b's own stated mechanism (which independently satisfies the spec requirement's stated shape — see 4.11's own note) and flags the discrepancy for the owner/`sdd-spec` rather than silently trusting this note's own prior claim.
- **Revision 4 (this pass): Unit 4b gains the remote capability.** The owner asked for parity with the comparison's own remote support — *"Al igual que en el de benchmark, se debe habilitar las opciones de remote, eso es importante."* Design revision 4 (D11a–D11d) and the spec's sixth revision (5 new requirements, one extended with local/remote scenario pairs, plus a `## Boundary` section) cover it in full; tasks 4b.29–4b.43 below implement it. No new machinery is required (D11b, evidence-backed) — the remote path is documentation plus one draft section, held to that claim by an integration test (4b.38) rather than left as prose. Unit 4b's forecast moves from ~650 to ~720; the change's total moves from ~3150 to ~3220.

### What Unit 1 and Unit 2 reported, recorded here so it is not lost

- **Unit 1** (`b493151`) and **Unit 2** (`432da9f`) are committed; their task items are marked done.
- **Unit 2 found and fixed four production bugs beyond the design's own scope**, discovered by test triage rather than design review: `undeclared_ladder_state`, `undeclared_records_state`, `undeclared_produces_state`, and `undeclared_step_notebooks_state` all still hardcoded the old benchmark root for their "where would this be written" path. Fixed alongside the D2 relocation.
- **One spec/design discrepancy surfaced and was resolved in the spec's favour**, per this file's own contract ("where design and spec disagree, the spec's requirement wins"): task 2.19(b)'s migration refusal. Design §7 called for no new code — an enriched detail folded into the existing `OBJECT_MAP_NOT_APPROVED` refusal. The spec required a **distinct named code**. Unit 2 implemented the spec's requirement: a new refusal code, `OBJECT_MAP_AT_OLD_HOME`, naming both the old and new locations. Recorded here so the design/spec divergence is visible at verify time, not only in commit history.

### What Unit 4 reported

- **Unit 4** is committed on branch `unit4-a-declined-comparison-is-remembered`, chained off Unit 2 (`432da9f`). All 17 tasks (4.1–4.17) done.
- **A design/spec tension on D5b was found and flagged, not silently resolved either way** — see task 4.11's own note above and the correction added to this file's earlier "resolved... no divergence remains" claim. Design revision 4's own `## 11. Open questions` still carries `D5b vs sdd-spec` unchecked; implemented per D5b's stated mechanism (acceptance = the harness stage materializing, which clears the `resolved.status == "absent"` guard by itself — genuinely "no dedicated reopening step", matching the spec requirement's own title), proved by a test that also proves a bare re-answer ALONE does not reopen it. The owner/`sdd-spec` should confirm this reading or override it; not arbitrated silently here.
  - **Unit 6a resolution (owner instruction, task 6a.15): D5b is SUPERSEDED by D19, not merely amended.** D19 (design revision 5) introduces a closed `discuss --decision yes|no` token, read by the engine directly — the counter-example to Unit 4's own rev-2 reasoning that "the engine never parses free text" ruled reopening out entirely. D5b's "acceptance = materializing the harness" reading was CORRECT for a prose answer, and remains correct for one: it is exactly the hole D19's token exists to fill, not a mechanism D19 replaces for prose. Once the closed token exists, `decision: "yes"` reopens the standing decision by the answer alone, immediately, with nothing yet built — the opposite of D5b's "acceptance is expressed only by the act it authorizes" reading, for the one input D5b never covered (a closed token, as opposed to free text). The still-unchecked `D5b vs sdd-spec` open question in design.md §11 should now be read as closed by this supersession, not as a question `sdd-spec` still owes an answer to independent of Unit 6a's own landing.
- **A measured, not assumed, consequence of D5b's guard ordering**: with no benchmark package on disk at all (`resolved.status == "absent"`) and no decline recorded, `probe`'s `nextStep` is `declare-first` today, not `benchmark` — the pre-existing `declare-first` override (still unnarrowed; Unit 3's D4 has not landed) already claims that state. `declined`'s own guard runs strictly before it and only intercepts once the exact current offer text has been answered; every "re-fire" scenario therefore reports `declare-first` again once the offer text stops matching, never `benchmark`. `decisions.comparison.state` (not `nextStep` alone) is the correct, stable signal that the offer stands unanswered — used throughout the re-fire and migration tests for exactly this reason.
- **Both sealed corpora's `probe` case SHRANK, not grew**, despite the `decisions` payload key's own addition: the `_Benchmark`-suffix exclusion (4.4) also drops the corpora's own benchmark package out of their baseline lists, shortening the comparison offer's own published text by more bytes than the new key adds. Read directly, not assumed — see task 4.16's own note.

### What Unit 4b reported

- **Unit 4b** is committed on branch `unit4b-the-acid-test`, chained off Unit 4 (`45eae9d`). All 43 tasks (4b.1–4b.43) done, including the remote-capability tasks (4b.29–4b.43).
- **Two divergences surfaced and flagged, not silently resolved** — the same discipline Unit 4's own D5b note established:
  - Task 4b.5's own note: design §D11c/D14b read as requiring the published acid-test question to carry `scale`'s declared axes, which conflicts with `_validation_offer_question`'s own literal 4-parameter signature (this task's own spec) and with D14's "Key = target + name + revision + premises" equation and the spec's own stability requirement (no scale exception in any scenario). Resolved per the narrower, explicitly-specified signature: the published question carries only fixed cost-shape prose, never scale content; the scale axes live in the draft instead. Flagged for the owner/`sdd-spec`.
  - Task 4b.11's own note: design §D13's prose places the three-way branch "last among the overrides"; Unit 4's own shipped code (which this unit extends rather than reorders) places the equivalent check FIRST, and the elif chain's structure means placing it last (as D13's prose describes) would make it unreachable whenever any repair override's own condition also held — the opposite of D13's stated intent. Implemented at Unit 4's existing (first) position; flagged for the owner/`sdd-spec` to confirm design §D13's prose should be corrected to match.
- **Task 4b.13's measurement, done rather than assumed**: `declare-first`'s second branch is NOT reachable once `declined`/`validate` matches, today or after Unit 3 lands — a structural consequence of the elif chain's ordering (see 4b.11), not a claim resting on Unit 3's own narrowing. No escalation needed.
- **`validation_proposal`'s `scale.rung` reads `levels[1]`** ("the lowest rung above the floor", `levels[0]` being the floor), asking when fewer than two rungs are declared — design names the rule ("the lowest rung above the floor") but not the index; this reading is recorded in task 4b.3's own note so a future reader does not have to re-derive it.
- **Both sealed corpora's `probe` case GREW this time**, unlike Unit 4's shrink: the `decisions.validation` and `validation` (draft) payload keys' own new bytes are not offset by anything shrinking. `tests/seal/digests.json` 9277→9385 bytes; `tests/experiments_seal/digests.json` 9013→9121 bytes (`propose` also moved there, already excluded from comparison via `KNOWN_UNSEALED_REASONS`).
- **A second, unrelated domain lock needed a one-line update beyond `M5_PINNED_RESIDUE`**: `CampaignProposalExclusionTests`'s `L1_DELIBERATE_SHRINK` (the bare word "proposal", tracked separately since design.md D6/task 0.4) moved from 2 to 4 — removing the local variable `proposal = wiring_proposal(...)` in favour of the `PROBE_DRAFTS` dict comprehension's `drafts` variable dropped 2 standalone occurrences of the word. Found only by running the full suite, not by design review.

### What Unit 3 reported — the change's last unit

- **Unit 3** is committed on branch `unit3-flow-a-stops-creating-the-benchmark-package`, chained off Unit 4b (`cb965c4`). All 20 tasks (3.1–3.20) done. This closes `the-comparison-nobody-asked-for`.
- **The one real divergence, measured and corrected, not implemented around — task 3.14's own note has the full account.** D4's narrowing (`"absent"` no longer routes to `declare-first`) surfaced that Unit 4b's shipped placement of the three-way `benchmark`/`validate`/`declined` branch — FIRST in `cmd_probe`'s `if`/`elif` chain — makes `declined` win over every repair unconditionally, contradicting this unit's own spec requirement ("A genuinely owed repair still outranks the acid-test offer") and design §D13's own literal, never-revised text ("last among the overrides, after `report-first`"). Fixed by (a) an explicit `resolved.status != "absent"` guard on `report-first` alone — the one repair override that reads the benchmark declaration without already being naturally shielded when absent — and (b) moving the three-way branch to last among the overrides, matching D13's original placement. `AcidTestShadowEnumerationTests` (Unit 4b's own class) rewritten to prove the corrected, opposite invariant; both of its prior tests are RENAMED, not merely re-asserted, so a reader sees the reversal rather than a silently flipped assertion under an unchanged name.
- **Consequence measured across five already-closed units' own suites, not bulk-updated.** Every test asserting `declare-first`/`declined` for a "no benchmark package, never offered" fixture was individually re-verified and corrected to `benchmark` where D4 now makes that the honest answer (`DeclareFirstBeforeTheRunTests`, `DeclinedComparisonTests` — 7 tests total). Each correction is a one-line assertion change with an updated comment; none was bulk-renamed or bulk-reworded.
- **The `_Benchmark`/`report_digest`/`premises` sweep found no further production bugs** (unlike Unit 2's four) — every remaining test-file fixture break was a direct, mechanical consequence of the list flip itself (a parent directory no longer pre-existing, a stage-2 doctrine table gaining a row, a declaration edit that now has to happen after the harness stage rather than before it), not a latent defect the flip exposed elsewhere.
- **README.md's own `nextStep` ladder enumeration is still stale beyond this unit's assigned scope** (five base rungs + four blocks, missing over half the values this change alone added: `declare-first`, `env-first`, `pilot-first`, `pilot-decisions`, `declined`, `validate`). Task 3.12's own wording scopes README's sweep to "the benchmark package from scaffold to harness" — done — not a full ladder rewrite spanning every prior unit's own additions. Named here per the mission's own "report it, don't implement around it" instruction rather than silently left or silently expanded past the assigned task.
- **Both sealed corpora moved by the smallest margin yet**: `verify-a`/`verify-b`/`verify-t` (`tests/seal/`) and six `verify-*` cases (`tests/experiments_seal/`) each moved by exactly +4 bytes — read directly via `test_implementation_seal.py`'s own result cache, not assumed: the sole content change in every case is `src/<Package>_Benchmark/__init__.py` moving from `structure.unrecordedScaffold` to `structure.unrecordedHarness`, the precise, intended consequence of the list flip. `probe` itself did not move in either corpus — its own fixtures never exercise a byte-visible consequence of this unit's changes.
- **One new environmental failure, confirmed same-class rather than assumed**: `FreshFlowATargetEndToEndTests.test_verification_notebook_executes_and_stamps` hits the identical `ModuleNotFoundError: No module named 'numpy'` at the identical source line every `NotebookSealAgreementTests` execution test already hits in this sandbox — the 32nd instance of the one confirmed-pre-existing class (missing `torch`/`numpy`/`pytest`/`requests`), not a new one. `test_remote_execution.py` itself does not import in this sandbox at all (`ModuleNotFoundError: No module named 'requests'`), confirmed identical on pristine HEAD via `git stash` — its 123 `_Benchmark` hits remain, re-measured, the single generic fixture literal Unit 1's own task 1.9 already found.
- **This was the last unit of the originally-scoped change** — Movement 6 (below)
  was added afterward, by the owner, as a distinct follow-on scope. Unit 3's own
  "this closes the change" note (task 3.20) predates Movement 6 and should be read
  as "closes the originally-scoped five units," not as a claim that no further
  scope exists.
- **Full verification**: `npm test` 640/640 (JS untouched throughout the whole change). `tests.test_proposal_implementation`: 1613 tests, 32 confirmed pre-existing/environmental failures (31 inherited + the one same-class notebook-execution instance above), every one individually confirmed via `git stash` A/B against pristine HEAD before exclusion — zero unexplained failures. `tests.test_implementation_seal` 72/72, `tests.test_experiments_seal` 71/72 (the one failure is the same "uncommitted seal corpus" mutation-proof control every prior unit documented, clears on commit). `tests.test_implementation_pair` 38/38. `tests.test_experimental_implementation` 63/63 green — its own `CrossingStateTests` mutation-proof control also referenced the uncommitted `tests/seal/` corpus and clears on commit identically. `tests.test_implementation_domain_lock` 28/28, `M5_PINNED_RESIDUE` recomputed twice (once for the main sweep, once more after the final `report-first` guard comment added one more `benchmark` occurrence after the first computation — caught by re-running the suite, not assumed stable).
- **Authored-line count**: `git diff --stat` (staged, pre-commit) totals 875 changed lines (599 insertions/276 deletions) across 9 files; excluding the two generated-goldens seal corpora (38 lines, mechanically regenerated, not authored) that is **837 authored lines against the ~800 forecast** — about 5% over, the smallest overrun of any unit in this chain (Unit 4b landed at ~1805 against ~720). Most of it (446 lines) is `tests/test_proposal_implementation.py`: the D13 placement correction's own ripple (task 3.14) touched seven pre-existing tests across two classes plus one class rewrite (`AcidTestShadowEnumerationTests`), and the fixture repairs (task 3.15) touched five more classes individually — proportionate to the correction's real blast radius, not padding.

### Movement 6 — added by the owner after Unit 3 closed

- **This is a distinct follow-on scope, not a correction to Units 1–3.** Design §3c
  (revision 5, D17–D24), the spec's seventh revision, and a new delta spec
  (`implementation-engine-neutrality`, 2 requirements) all landed after the
  original five units were applied and green. Movement 6 is designed against what
  that shipped code **now is** (D17), with three corrections load-bearing: the
  three-way branch sits last only because Unit 3 moved it there; D5b's
  "acceptance = materializing" is shipped and is the hole Part A fills; and the
  published acid-test question does not carry `scale`'s axes (a literal
  4-parameter signature).
- **Two open questions are deliberately left as tasks, not answers**: task 6a.15
  records that D5b is superseded by D19 (not amended) and asks the owner/`sdd-spec`
  to confirm; task 6b.3 is an explicit measurement of whether `validate` should be
  reachable from `already-benchmarked` only or from any state with a benchmark
  package present — design named this as unsettled rather than guessing, and this
  file preserves that posture rather than silently picking one.
- **Forecast discipline**: Movement 6's ~2000-line forecast (300 + 1000 + 700) is
  stated as a **floor**, per the owner's own instruction, because every prior
  forecast in this chain has landed low (4b at 2.5×, 3 at 1.05×) and none has
  landed high. `sdd-apply` should expect Unit 6a in particular to blow its own
  forecast the way 4b did — Part A changes the *meaning* of an already-answered
  bucket, read by four already-shipped test classes and both sealed corpora, the
  exact ripple profile that produced 4b's 2.5×.

### What Unit 6a reported

- **Unit 6a** is committed on branch `unit6a-saying-yes-reopens`, chained off
  Unit 6c (`f5c3511`), itself on Movement 6's planning commit (`8886fae`), on
  top of Unit 3 (`330c5f1`). All 17 tasks (6a.1–6a.17) done.
- **The forecast overshot the other direction this time, measured rather than
  assumed.** Every prior unit in this chain landed AT or OVER its own
  forecast (3 at 1.05×, 4b at 2.5×) — Unit 6a landed UNDER its own ~1000-line
  floor. See task 6a.16's own note for the mechanism: the "heaviest ripple"
  the design forecast against four already-shipped test classes plus both
  roster classes materialized in only ONE of them
  (`DeclinedComparisonTests`, two dict-literal updates for the new
  `decision` member); `AcidTestShadowEnumerationTests`,
  `DeclareFirstBeforeTheRunTests`, `NextStepSectionCoverageTests`'s own
  roster test and `NextStepPublicationRosterTests` all passed with either
  zero changes or one literal-set addition, because none of their existing
  assertions compares the full `decisions` payload by equality and the new
  `build-first` rung's own roster entry carries an empty `drafts` tuple
  (task 6a.8's own note). The full suite was run twice, not once, to confirm
  this rather than trust a partial read — see "Full verification" below.
- **One divergence surfaced and flagged, not implemented around — task
  6a.8's own note has the full account.** Design's literal "`drafts` =
  `("wiring",)` or `("validation",)` by which was accepted" cannot be the
  roster's own static `PROBE_NEXT_STEPS["build-first"]["drafts"]` tuple,
  because `NextStepPublicationRosterTests.test_every_entry_names_a_drafts_tuple_of_known_builders`
  holds every roster entry to exactly one fixed tuple — a shape-lock test
  outside this unit's own mandate to alter. Resolved by keeping the
  roster's own tuple empty (`declare-first`'s own precedent for a repair
  whose published text already varies by a branch-threaded fact while its
  roster `drafts` stays `()`) and resolving the one actual draft
  dynamically in `cmd_probe`, from the identical `facts["buildFirstArm"]`
  fact the publish function itself reads. The OBSERVABLE behaviour matches
  the design's plain-English sentence exactly (`test_build_first_never_publishes_both_drafts_at_once`
  proves it) — only the roster's own static declaration differs from a
  literal-tuple reading.
- **D5b is recorded as superseded by D19, not amended** (task 6a.15,
  owner's own instruction) — see "What Unit 4 reported" above, where the
  note now lives beside Unit 4's own original D5b account rather than
  replacing it.
- **Both sealed corpora moved by exactly two cases each**: `probe` and
  `discuss` in both `tests/seal/digests.json` and
  `tests/experiments_seal/digests.json` — regenerated via
  `tests/seal_capture.py`/`tests/experiments_seal_capture.py`, diff read
  case by case. Nothing else moved in either corpus.
- **`M5_PINNED_RESIDUE` (the derived-vocabulary domain lock,
  `tests/test_implementation_domain_lock.py`) needed eighteen pins
  recounted, zero new admissions and zero removals**: `actually`,
  `after`, `against`, `answered`, `before`, `beside`, `check`, `empty`,
  `experiment`, `invariant`, `longer`, `makes`, `rather`, `recorded`,
  `reported`, `value`, `whose`, `write` all grew by the new engine prose
  (the closed-token discipline, the migration rule, the `build-first`
  rung); `test_2_no_unpinned_denylist_word_appears_in_the_engine` confirmed
  no new unpinned leak before any pin was touched.
- **Full verification, run twice**: `npm test` 640/640 (JS untouched). The
  full `tests.test_proposal_implementation` suite: 1636 tests, 32
  confirmed pre-existing/environmental failures (25 failures + 7 errors) —
  the exact same 32 test IDs, individually re-run against a `git stash`-clean
  pristine HEAD, reproduced the identical 25 failures + 7 errors, 0
  differing, confirming zero regressions. `tests.test_implementation_seal`
  72/72, `tests.test_experiments_seal` 71/72 (the one failure is the same
  "uncommitted seal corpus" mutation-proof control every prior unit
  documented, clears on commit). `tests.test_implementation_domain_lock`
  28/28 after the pin recount above.
- **Authored-line count**: `git diff --numstat` totals 682 changed lines
  (604 insertions/78 deletions) across 8 files; excluding the two
  generated-goldens seal corpora (18 lines, mechanically regenerated, not
  authored) that is **664 authored lines against the ~1000 floor** —
  roughly two-thirds of the floor, not an overrun. Reported honestly
  rather than padded: this unit's own measured ripple (above) was
  genuinely smaller than the design's own worst-case forecast, which the
  design itself named as a floor precisely because it could not rule out
  the opposite.
