# Tasks: the-comparison-nobody-asked-for

> **Size note.** The `sdd-tasks` skill sets a 530-word default budget. The owner's
> binding directives for this change — full coverage with nothing pending, explicit
> no-regression verification rather than a note pointing at existing tests, and
> chained units rather than reduced coverage against a 3150-line forecast on a
> 1400-line budget — cannot be satisfied inside it. The same explicit-contract
> override the proposal and design took applies here.

**Ordering.** Units are numbered as the design names them (`1`, `2`, `4`, `4b`, `3`)
so every cross-reference to the design and specs stays stable. They are **presented
and MUST be delivered in execution order: 1 → 2 → 4 → 4b → 3.**

**Threat matrix: N/A** (design §9). No routing of untrusted input, shell command,
subprocess, VCS/PR automation, executable-file classification, or process
boundary is introduced or widened. No threat-matrix RED tasks apply.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~3150 (design §10; per-unit sum below ~3160, within rounding) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Unit 1) → PR 2 (Unit 2) → PR 3 (Unit 4) → PR 4 (Unit 4b) → PR 5 (Unit 3) |
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
| 4 | Unit 4b — the acid test | `validation_proposal` (D11), `validate` rung (D12), canonical `premises` key (D14/D14a), D15 invariant | ~650 | `pytest tests/test_proposal_implementation.py -k "validat or PROBE_DRAFTS or NextStep"` | `cmd_probe` → accept acid test → `cmd_step` wiring + running it | Purely additive; D15a+D15b guarantee no on-disk residue — revert unwinds a rung, never a directory |
| 5 | Unit 3 — first flow stops creating the benchmark package | Scaffold/harness list flip; `declare-first` narrows (D4); derived-count sweep (D8); doc sweep close-out | ~800 | `pytest tests/test_proposal_implementation.py` (full) + both seal suites | Full Flow A on a fresh target, E2E | Only unit changing Flow A's on-disk output; revert restores the scaffold list; Units 1/2/4/4b stay correct without it |

---

## Unit 1 — The seal leaves the benchmark package

- [x] 1.1 RED: add a failing test asserting `report_digest._here()` resolves the repo root correctly for a file at `src/<P>/report_digest.py` (today's code assumes the `_Benchmark` suffix).
  - *Measured: `_here()`'s `package_dir.parents[1]` is already correct at the new depth before any edit (D7's own finding — "verified by reading, not assumed"), and `.removesuffix("_Benchmark")` is a no-op on a plain package name, so no behavioural RED was reachable here. `ReportDigestHereRelocationTests` pins the post-relocation behaviour; the genuine RED/GREEN pair is `KitSurfaceLanguageTests.test_the_translation_touched_no_code`, pinned to `_here()`'s own source text, which fails until 1.2's suffix-strip removal lands.*
- [x] 1.2 Simplify `_here()` to `return package_dir.parents[1], package_dir.name` (D7); rewrite its three docstring paragraphs that assert the old location.
- [x] 1.3 Relocate the `report_digest.py` entry in `scaffold_destinations()` and `scaffold_kit_source()` from `src/<P>_Benchmark/` to `src/<P>/`; confirm `KIT_SEAL` (the kit **source**) is unaffected — only the destination mapping moves.
- [x] 1.4 Update `assets/kit/nb/verification.ipynb` and `assets/kit/nb/probe.ipynb`'s import line to `from {{PKG}} import report_digest`; leave `probe.ipynb`'s `HARNESS` path untouched.
- [x] 1.5 Rewrite `scripts/materialize.py`: replace its three imperative sites with one loop over `scaffold_destinations(name)` + `scaffold_kit_source(...)` + `authored_package_init(name)` (D9). Preserve the `writable_at_scaffold_time` filter on `tests/*.py`; resolve kit sources under the caller-supplied `KIT` argument, never `SKILL_ROOT` — `experimental-implementation` ships no kit and must not gain the forge's own fixture content.
  - *Note: D9's rewrite may overlap the in-flight change `the-skill-materializes-not-the-agent` (tasks 4.4/4.5), which proposes deleting `materialize.py` instead. This task encodes D9's rewrite; the owner has not yet ruled on deletion vs. rewrite. Do not block on it.*
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

- [ ] 2.1 Add `IMPLEMENTATION_DECLARATION = "__implementation__"`, `IMPLEMENTATION_BLOCKS = {"revision": "", "premises": {}}`, `resolve_implementation_declaration(target, name)` returning the same `{status, path, detail, contract}` quadruple and `absent`/`undeclared`/`declared` vocabulary as the benchmark resolver (D1). Generalize `_declaration_is_blank` over a blocks mapping rather than an eighth hardcoded shape.
- [ ] 2.2 Add `declaration_root(target, name) -> target / "src" / package_name(name)` as the one shared root for `resolve_implementation_declaration` and the three sibling resolvers (D2). `resolve_benchmark_declaration` keeps its own `bench_root`, unrouted.
- [ ] 2.3 Point `resolve_levels_declaration`, `resolve_steps_declaration`, `resolve_records_declaration` at `declaration_root` (spec "Target's Own Flow Declarations Relocate Alongside The Method's Declaration").
- [ ] 2.4 RED then GREEN: position/pilot-completeness/walk/flow-acts state and a declared step's execution resolve identically for a target with no `_Benchmark` package (spec "First-Flow Commands Do Not Depend On A Benchmark Package").
- [ ] 2.5 Point `_stage_objects`' existence gate at `resolve_implementation_declaration`, keeping the identical `unwritten = [...]` check, refusal code, and per-block message — only the path in the sentence changes (spec "Object-Map Existence Gate... Unchanged"). RED first, against today's benchmark-resolver call site.
- [ ] 2.6 RED then move (highest-risk edit, part 1): `cmd_verify`'s `declared_revision` — source from `resolve_implementation_declaration(...)["contract"]` unconditionally, no longer gated on `status == "declared"` (D3). Write the RED test on a no-benchmark target first.
- [ ] 2.7 RED then move (highest-risk edit, part 2): `cmd_verify`'s `built_against`, `changed_sections(...)`, `staleRevision` — compute from the same relocated literal, report outside the `status == "declared"` branch. Separate RED test from 2.6's.
- [ ] 2.8 Point the `benchmark` block's `absent` note at `structure.harnessGaps` instead of `structure.scaffoldGaps`; confirm it reads as the normal pre-acceptance state, not a defect (spec "revision's Two Independent Readers... Preserved", scenario 2).
- [ ] 2.9 Integration test: on a target with no benchmark package, `latestRevision`, every module's `stale`, and `changedSections` still answer from `__implementation__` — RED against today's code.
- [ ] 2.10 Grow `authored_package_init(name)` with a module-level template prefilling the four literals empty, with guidance comments, following the `_DEFAULT_PYPROJECT` precedent (D10). Order: docstring, `__all__`, `__implementation__`, `__levels__`, `__steps__`, `__records__`.
- [ ] 2.11 Confirm (with a test) that `materialize.py`'s package-init site — driven by Unit 1's D9 loop — picks up the grown template with no further `materialize.py` edits.
- [ ] 2.12 Shrink `assets/kit/src_benchmark/__init__.py`'s declaration from seven blocks to five (`arms`, `search`, `report`, `distribution`, `entry`); the three sibling literals move to the package-init template.
- [ ] 2.13 Rewrite `tests/seal/corpus.py` and `tests/test_implementation_pair.py` fixtures that hand-build a `_Benchmark/__init__.py` carrying `__steps__` to write it (and `__levels__`/`__records__` where present) into the package init instead. Re-run the seal, read the diff, regenerate only the cases that moved.
- [ ] 2.14 Triage the 1 `premises` hit in `tests/test_implementation_domain_lock.py`; confirm the neutrality lock still holds after relocation.
- [ ] 2.15 Rewrite `experimental-implementation/impl_profile.py`'s `OBJECTIVE_FLOW` "standing" stage to describe the relocated gate.
- [ ] 2.16 Update `SKILL.md` step 8 (new path + the `materialize --authored <path>` re-seal instruction — D10), step 9's gate prose, the seven-block declaration table (five blocks + four sibling literals), the Decision Gates row, and fix the `AGREED.md`/`AGREEMENTS.md` naming drift in this same paragraph (pre-existing, unrelated, one line — not a movement of its own).
- [ ] 2.17 Update `references/usage.md`'s `OBJECT_MAP_NOT_APPROVED` refusal-detail row to the new path.
- [ ] 2.18 Regression-verification: explicit tests for the remaining five declaration blocks' `absent`/`undeclared`/`declared` resolution (spec "Remaining Five Declaration Blocks Are Unaffected") and fidelity reporting excluding `absent` while folding in `undeclared` (spec "Fidelity Reporting... Is Unchanged").
- [ ] 2.19 Migration test (concrete fixture, per owner instruction): build a fixture shaped after `implementations/Domain_Adaptation`'s old-home declaration — non-blank `revision`/`premises`, non-empty `__levels__`/`__steps__`/`__records__`, plus one extra literal the forge has no reader for anywhere (mirroring the live target's unread `__environment__`). Assert: (a) a never-declared target refuses `OBJECT_MAP_NOT_APPROVED` exactly as today; (b) an old-home-only declaration refuses by a distinct named code identifying both locations; (c) the one-time `materialize --adopt`-shaped remedy moves all five literals to the new home verbatim; (d) the unread literal survives unchanged even though no forge-owned check would ever report its absence (spec "A Declaration Predating This Change Is Migrated In Full", all four scenarios).
- [ ] 2.20 Document the live-target migration procedure in `SKILL.md` (design §7): scaffold, hand-move the literals including the unread one, `materialize --authored`, delete the orphaned seal copy, re-execute notebooks. State explicitly this repository's commit does not apply the procedure to `implementations/Domain_Adaptation` (a separate repository); the unit closes when the documented procedure and the loud refusal exist.
- [ ] 2.21 Regenerate both sealed corpora if 2.1–2.13 moved any case's digest; read the diff, account for every moved case.
- [ ] 2.22 Run both suites green before closing the unit.

## Unit 4 — A declined comparison is remembered

- [ ] 4.1 Add `_benchmark_offer_question(target, name, baselines)` — the single constructor of the decline question text, embedding target, name, and **sorted** baseline names, never a count (D5a). Route `_benchmark_publication` through it; thread `baselines` via `facts` rather than recomputing.
- [ ] 4.2 Test: `_benchmark_publication`'s question is byte-identical to `_benchmark_offer_question(...)`, plus a source scan proving the ladder calls the constructor rather than a literal (spec "Decline Question Text... Exactly One Place").
- [ ] 4.3 Test: different baseline sets produce different question text; the text never contains a numeral derived from `len(baselines)`.
- [ ] 4.4 Add `previous_implementations()`'s `_Benchmark`-suffix exclusion **in this same commit** as 4.1 (spec migration-consequence requirement — not separable without a window of a knowably-wrong key).
- [ ] 4.5 Test: a scaffolded target with no genuine prior work returns an empty list and the flow reports `nothing-to-compare` for the first time; a real baseline is still found alongside an excluded `_Benchmark` directory.
- [ ] 4.6 Fold `_discussion_buckets` once in `cmd_probe` and hand it to both readers (D6); make `_answered_discussions` a thin wrapper over `_answered_from_buckets(buckets)`; add `_answered_event_from(buckets, question) -> dict | None` (last non-blank-answer event, `None` for never-asked and unanswered alike).
- [ ] 4.7 Add `"declined"` to `PROBE_NEXT_STEPS`: `{"kind": NEXT_STEP_TERMINAL, "wiring": False, "publish": None}` (D5d — still the `wiring` key here; Unit 4b migrates the roster to `drafts`). Assign by a bare string literal inside `cmd_probe` (D5c).
- [ ] 4.8 Wire the ladder branch: `next_step == "benchmark" and resolved["status"] == "absent" and _benchmark_offer_question(...) in answered -> next_step = "declined"` (D5b) — before D4's narrowing and before every repair override.
- [ ] 4.9 Add `cmd_probe`'s `"decisions"` payload key with a `"comparison"` member (`{"state": "answered"|None, "at": ..., "asked": ...}`, always present; `at` display-only, never compared/sorted) (D6/D16 partial — the `"validation"` sibling is Unit 4b's addition to this same key).
- [ ] 4.10 Test: two decline events on identical text within the same second, opposing ledger append order — the later-appended event wins regardless of `at`; the displayed date never changes the winner (spec "Ledger Append Order Decides Ties...").
- [ ] 4.11 Test: re-answering the identical question with acceptance flips the bucket, last-event-wins, no dedicated reopening path (spec "Answering The Same Question Again Reopens...").
- [ ] 4.12 Test: re-running the suite, editing method modules, and re-rendering a report leave the decision settled-declined; a baseline appearing or disappearing re-fires the offer (spec "Offer Re-Fires Exactly When Baseline Name Set Materially Changes", all five scenarios).
- [ ] 4.13 Regression-verification: exercise `nothing-to-compare` and `already-benchmarked` under their own preconditions in isolation after `declined` is added, proving each fires exactly as before (spec "Every Pre-Existing Probe Rung Fires Under Its Exact Prior Condition").
- [ ] 4.14 Migration test: a decline recorded before this change (key embedding the pre-fix baseline set, including the target's own `_Benchmark` package) re-fires exactly once on the first pass after landing; answering it restores stability with no second re-fire from the same migration event (spec "Baseline-Finder Fix Causes Exactly One Expected Re-Fire, Not A Defect", both scenarios).
- [ ] 4.15 Update `references/usage.md`'s terminal-state list to include `declined` (do not yet touch "Three answers reach that point" — `validate` has not landed).
- [ ] 4.16 Regenerate both sealed corpora for the `PROBE_NEXT_STEPS` growth and the `decisions` payload addition (P6, first half — must not land red waiting for Unit 4b's own additions). Read the diff, account for every moved case.
- [ ] 4.17 Run both suites green before closing the unit.

## Unit 4b — The acid test

- [ ] 4b.1 Introduce `PROBE_DRAFTS = {"wiring": wiring_proposal, "validation": validation_proposal}`; migrate `PROBE_NEXT_STEPS`'s `wiring: bool` key to `drafts: tuple[str, ...]` across **every** existing entry (D12). `cmd_probe` builds `{d: PROBE_DRAFTS[d](target, name, facts) for d in entry["drafts"]}`.
- [ ] 4b.2 Test: `cmd_probe`'s public `"wiring"` payload key is byte-identical for every pre-existing rung after the migration; a sibling `"validation"` key is added, always present, `None` when not applicable.
- [ ] 4b.3 Build `validation_proposal(target, name, facts)` (D11): `claim` from `__implementation__["premises"]` + `revision`; `arm` from `wiring_proposal`'s `new` half only, no rival; `data` from `baseline_environment(target, baselines, name)`; `scale` from the target's own `__levels__` (asked when empty); `evidence` an `__records__` entry proposal at a non-comparison-named path; `needs` asking the reference figure and naming which `revision` to read it from. Same `{status: "draft", instruction, …, needs}` envelope as `wiring_proposal`.
- [ ] 4b.4 Test: the draft names the method's own modules as the single arm, real data, a scale from `__levels__`, and quotes `premises` — non-empty content derived from the tree, never a fixed envelope; a second test confirms the rival/`baseline` half is absent even when baselines exist on disk.
- [ ] 4b.5 Add `_validation_offer_question(target, name, revision, premises)` (D14): key = target + name + `revision` + a **canonical rendering** of `premises` — sorted keys of whatever mapping is present, naming none, requiring none, refusing nothing (D14a). Route `_validate_publication` through this same constructor.
- [ ] 4b.6 Test: the acid-test key moves when `revision` or `premises`' value changes; it does **not** move on re-indent, re-quote, reflow, key-reorder, or trailing comma, nor on an unrelated module edit, test write, notebook re-run, seal change, or a baseline appearing/disappearing (spec "Acid-Test Offer Re-Fires Exactly When Revision Or Criterion Changes", all scenarios including "A Stable Key Persists Across A Re-Fire-And-Redecline Of The Comparison Itself").
- [ ] 4b.7 Test (under-fire guard, D14a): adding a **fifth** key to `premises` DOES move the key — the assertion that rejects field-name-aware canonicalization.
- [ ] 4b.8 Canonical-projection test (owner-handed item): a `premises` mapping with unexpected keys, missing the kit's suggested four, or bound to a non-mapping value entirely — the canonical rendering produces output in every case; none refused, none treated as more or less valid (spec "The Canonical Rendering Names No Key And Refuses Nothing"; D14b — "a function that can say no has become a schema").
- [ ] 4b.9 Test: `_validate_publication`'s question is byte-identical to `_validation_offer_question(...)`, plus a source scan proving the ladder calls the constructor.
- [ ] 4b.10 Add `"validate"` to `PROBE_NEXT_STEPS`: `kind = NEXT_STEP_EXPERIMENT`, `choice = NEXT_STEP_EXPERIMENT_CHOICE`, `drafts = ("validation",)` (D12). Assign by bare string literal (D5c).
- [ ] 4b.11 Wire the three-way branch (D13), placed **last** among overrides, after `report-first`, guarded on `resolved["status"] == "absent"`: unanswered comparison → `benchmark`; comparison answered, validation unanswered → `validate`; both answered → `declined`.
- [ ] 4b.12 Shadow-enumeration task (owner-handed item, D13 proof obligation): test walking all six remaining overrides under `status == "absent"` — `declare-first` (both branches), `env-first`, `wiring-first`, `poll-first`, `search-first`, `report-first` — proving each unreachable ahead of `declined`/`validate`, and that `pilot-first`/`pilot-decisions` still outrank the pair. Prove by mutation: invert each guard and watch the test go red.
- [ ] 4b.13 Measurement task (owner-handed item, unresolved in design): measure — do not assume — whether `declare-first`'s second branch (`report.get("live") == "undeclared"`, unconditioned on declaration status) is reachable under `status == "absent"` after Movement 3. If reachable, escalate as a real shadow requiring design revision.
- [ ] 4b.14 Extend `cmd_probe`'s `"decisions"` payload with the `"validation"` member, completing D16: both members always present, `None` when unanswered, `at` display-only in both.
- [ ] 4b.15 Test: the three-way branch end to end — unanswered → `benchmark`; comparison answered → `validate` with a draft; both answered → `declined` with both dates.
- [ ] 4b.16 Test (D15b): answering the acid-test question writes no file, adds no receipt entry, leaves `scaffold_gaps`/`object_gaps`/`harness_gaps` byte-identical (spec "The Acid Test Materializes Nothing Up Front", all three scenarios).
- [ ] 4b.17 Integration test (D15a, stronger than "writes no file"): after answering, wiring, **and running** the acid test — no path under `src/<Package>_Benchmark/` exists, `harness_gaps()` unchanged, no receipt entry carries `stage: "harness"`, no written destination appears in `harness_destinations(name)` — asserted against the list, not a literal path.
- [ ] 4b.18 Naming-leak fix #1 (owner-handed item): rewrite the kit's `__steps__` example (`module: "Example_Method_Benchmark.steps"`) in the guidance shown while wiring an acid test to name the method's own package instead.
- [ ] 4b.19 Naming-leak fix #2 (owner-handed item): rewrite `__records__` path guidance away from the `…/Results/Benchmark/…` habit to a product-folder path that does not borrow the comparison's name.
- [ ] 4b.20 Test: no cross-skill reach — the validation path imports, reads, and invokes nothing outside this skill and the shared engine.
- [ ] 4b.21 Test: the acid-test offer's text ends with the identical `NEXT_STEP_EXPERIMENT_CHOICE` every other experiment offer ends with, names a single arm with no rival and no "already proved" language, and is a prose question, not a menu.
- [ ] 4b.22 Test: the draft asks for the reference figure and names the `revision` to read it from; the engine never parses a figure out of prose.
- [ ] 4b.23 Add `SKILL.md`'s new `### nextStep: "validate"` section: what the acid test is, what it may write to, that it never creates benchmark-named structure. Must **not** join `NO_SECTION`.
- [ ] 4b.24 Update `NextStepSectionCoverageTests.all_next_steps()` / `NO_SECTION`: recovers `declined` and `validate`; `NO_SECTION` grows to include `declined`, explicitly excludes `validate`.
- [ ] 4b.25 Update `NextStepPublicationRosterTests`: experiment-steps assertion grows to four (`validate` joins), docstring updated; terminal-steps assertion grows to three, renamed; roster-shape assertions confirm `drafts` totality on every entry.
- [ ] 4b.26 Update `references/usage.md`'s "Three answers reach that point" and the `wiring` → `drafts`/`validation` payload description.
- [ ] 4b.27 Regenerate both sealed corpora for the roster's `drafts` migration and `decisions.validation` (P6, second half). Read the diff, account for every moved case.
- [ ] 4b.28 Run both suites green before closing the unit.

## Unit 3 — The first flow stops creating the benchmark package

- [ ] 3.1 RED then remove: `src/<Package>_Benchmark/__init__.py` out of `scaffold_destinations()`/`scaffold_kit_source()`, into `harness_destinations()`/`harness_kit_source()` (three entries → four).
- [ ] 3.2 Test: a fresh target completing the scaffold stage has no `<Package>_Benchmark` directory anywhere under `src/` (spec "Fresh Target Has No Benchmark Directory After Scaffolding").
- [ ] 3.3 Test: acceptance materializes the benchmark package only via the wiring-first rung; no fifth materialization stage is invoked (spec "Acceptance Materializes The Benchmark Package Via The Harness Stage").
- [ ] 3.4 RED then narrow: `cmd_probe`'s `declare-first` condition from `resolved["status"] in ("absent","undeclared")` to `"undeclared"` only (D4); confirm `"absent"` targets fall through to `benchmark`/`declined`/`validate` instead.
- [ ] 3.5 Test: an unrecorded `src/<Package>_Benchmark/__init__.py` is flagged `UNRECORDED_SCAFFOLD` against the harness list; `materialize --adopt` records it scoped to the correct stage list (spec "Materialization Receipt Machinery... Against The New Destination Lists", remaining scenarios).
- [ ] 3.6 Apply the derived-count rule (D8): `scaffold_destinations` at ten unconditional entries, `scaffold_gaps`'s maximum at twelve (ten + up to two conditional anchors), computed at read time. Remove every hand-written gap-count/ladder-count literal from engine docstrings (`scaffold_destinations`, `scaffold_structure_gaps`, `all_kit_destinations`, `harness_destinations`, `_stage_objects`, the declaration resolvers) and doctrine prose — the noun replaces the numeral.
- [ ] 3.7 Delete `all_kit_destinations`'s arithmetic-identity docstring assertion ("Eleven + three + three = seventeen").
- [ ] 3.8 Test: a grep-style check that no doctrine file (`SKILL.md`, `references/usage.md`, `README.md`, engine docstrings) states a scaffold-gap or ladder count as a hand-written numeral, and no new numeral replaces it (spec "The Gap Report Is Derived, Not Transcribed").
- [ ] 3.9 Update `SKILL.md`'s step 5 table (benchmark package moves scaffold → harness row), the "Conversion, then benchmark" paragraph, and the Decision Gates row.
- [ ] 3.10 Fix `references/usage.md`'s already-stale ladder sentences ("Eleven values are possible", "The other three have no section", "Nine of the eleven publish resolve", "null only at ... the two answers") — derive rather than transcribe a corrected count; point at `NextStepSectionCoverageTests.test_every_value_the_cli_can_return_is_accounted_for` instead.
- [ ] 3.11 Fix `cmd_probe`'s stale comment ("Two of the eleven answers publish nothing") the same way.
- [ ] 3.12 Update `README.md`'s `nextStep` ladder documentation and `src/` tree to move the benchmark package from scaffold to harness (added by design; not in the proposal's original Affected Areas).
- [ ] 3.13 Regression-verification: exercise `nothing-to-compare`, `already-benchmarked`, `benchmark`, `declined`, `validate` each under its own precondition, confirming none is reordered or shadowed by this unit's list flip (spec "Introducing The Acid-Test Follow-Up Does Not Reorder Or Shadow Any Other Ladder State"; "Every Pre-Existing Probe Rung Fires Under Its Exact Prior Condition").
- [ ] 3.14 Regression-verification: a genuinely owed repair (an unfinished step in the target's own declared flow) still outranks a declined-but-unresolved comparison/acid-test pair — explicit test (spec scenario "A genuinely owed repair still outranks the acid-test offer").
- [ ] 3.15 Complete the bulk update of `tests/test_proposal_implementation.py`'s remaining `_Benchmark`/`report_digest`/`premises` hits not already touched by Units 1, 2, 4, or 4b.
- [ ] 3.16 Complete the `tests/test_remote_execution.py` hits, if any, affected by the scaffold/harness list flip and not already resolved by Unit 1's discovery task.
- [ ] 3.17 Triage and update the 6 `_Benchmark` hits in `tests/test_experimental_implementation.py`.
- [ ] 3.18 E2E test: a fresh Flow A target, end to end — after scaffolding, no `_Benchmark` directory exists; `verification.ipynb` executes and stamps; `previous_implementations()` is empty; the flow reports `nothing-to-compare`.
- [ ] 3.19 Regenerate both sealed corpora for the scaffold/harness list flip and `declare-first`'s narrowing; read the diff, account for every moved case, and confirm the corpora now reflect all five units' cumulative changes.
- [ ] 3.20 Run both suites (`npm test` and the Python unittest suites) green — this closes the change.

---

## Notes carried forward, not tasks

- The `AGREED.md`/`AGREEMENTS.md` naming drift is out of scope; fixed as a one-line edit inside 2.16, the commit that already touches that paragraph.
- D9's `materialize.py` rewrite (1.5) may be superseded by a future owner ruling favoring deletion (`the-skill-materializes-not-the-agent`, tasks 4.4/4.5). Encoded as rewrite here; not blocked on that ruling.
- Design's open questions on D5b, D14a and `__implementation__`'s name were resolved in favor of the design by revision 3 of the spec reconciliation; no divergence remains for `sdd-apply` to arbitrate.
