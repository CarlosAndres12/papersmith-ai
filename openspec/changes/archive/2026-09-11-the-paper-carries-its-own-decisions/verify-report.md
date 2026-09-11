```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:223b2b77f65d0a253ec8f8fab47ee630fd501e8bc2a7dcfc9c005383e3a7c50d
verdict: fail
blockers: 0
critical_findings: 0
requirements: 18/19
scenarios: 26/27
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:4d5ec256d72c5e5d3b611ff3425b5cc7f01ff6dfeb6cc9e425dcfdae4d2f1282
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

> **Note (scoped re-verification, 2026-09-11)**: this envelope reflects the
> CURRENT state after corrective commit `12ac0b7` resolved the sole
> CRITICAL below — `blockers: 0`, `critical_findings: 0`. `verdict: fail`
> is the admission tool's own strict rule (completed counts must equal
> totals for a passing verdict), triggered by ONE pre-existing, non-blocking
> UNTESTED scenario carried over unmodified from the pass below (out of this
> scoped re-verification's remit) — not by any reopened defect. See
> `## Re-Verification (scoped)` near the end of this file for the new
> evidence, re-falsification, and this pass's own explicit archivability
> call. The full original FAIL report is preserved unmodified beneath this
> line for history.

**Original report begins below, preserved verbatim for history:**

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:0422dd1d4ed8f207816ad8231d6a70e5c9cf5660
verdict: fail
blockers: 1
critical_findings: 1
requirements: 17/19
scenarios: 25/27
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 1
test_output_hash: sha256:f35fd1474dbd3ca0751c13dfed16c8e5f6fc4e417930ef003fb21b6af69b9fb5 (npm) + sha256:0c641e590f77373c3d99938f49c6269eb9d8f037f7a5e5503496280b57435ce6 (python)
build_command: N/A (stdlib CLI, no build step)
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: the-paper-carries-its-own-decisions
**Version**: N/A
**Mode**: Strict TDD

Commits verified: `4dedbd9`, `30d5c32`, `a583d72`, `6e45781` (all four slices, on
`paper-writing` branch). HEAD moved to `0422dd1` during this verify run — a
**disclosed concurrent sibling apply** (`the-contract-is-data-not-code`
follow-up fix) committed a test-only change to `tests/test_paper_contract.py`
mid-session; confirmed by reading the commit that it touches none of the four
new modules or their tests. This verify pass is read-only throughout: no edit,
stage, or commit was made.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 37 |
| Tasks complete | 37 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: N/A — stdlib-only CLI, no build step.

**Tests**: executed directly, not merely read as reported.

- `npm test` → **559/559 passed**, exit 0 (isolated run, log hash above).
- `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` → **2937 ran,
  2926 passed, 5 FAILED, 6 skipped, exit 1** (full-suite run, log hash above).
  All 5 failures are in `test_proposal_implementation.py::
  MaterializeScriptStaysTestOnlyTests` ("the forge ships 2 scripts besides its
  engine; these tests are written for exactly one harness") — a different
  skill (`proposal-implementation`, "the forge"), unrelated to
  `paper-writing`. Confirmed by content: the failure is about a materialize
  harness count, nothing this change touches. Attributed to the disclosed
  concurrent sibling apply's in-flight, uncommitted work on that unrelated
  subsystem at the moment this suite ran. **Not a defect of this change** —
  but the literal declared full-suite command did not exit 0 during this
  measurement window, so it is reported honestly rather than silently
  rounded to green.
- Isolated re-run of every file this change owns, to remove the contamination
  variable: `tests.test_paper_decisions` (the whole module, all 52 tests) →
  **52/52 ok**. `tests.test_paper_writing.RefusalRosterTests` → **5/5 ok**.
  Both executed standalone, cleanly, no contamination possible (neither
  touches `test_proposal_implementation.py` or its fixtures).
- All seven mutation-proof tests (M1–M7) executed directly:
  `RegionGrammarMutationTests`, `GuidanceRegistryMutationTests`,
  `DeclarationsMutationTests` (×3, M2/M5/M6), `ProvenanceMutationTests` (M3),
  `ObservationReportMutationTests` (M7) → **7/7 ok**, each confirmed via the
  shared `MUTANT_IMPORTED_OK` marker + non-zero exit assertion baked into
  `_assert_guard_failed_under_mutation` — a crashed-import mutant would not
  pass this check, only a guard that genuinely fired does.

**Coverage**: not measured — no coverage tool configured for this stdlib-only
CLI; consistent with prior phases of this repository.

### Spec-by-spec execution evidence

1. **M1 disjointness, both directions** — confirmed by reading
   `paper_block.py`'s `scan_markers` (`content.startswith(MARKER_PREFIX)`,
   `continue` on mismatch) and `paper_region.py`'s `find_region`
   (`content.startswith(prefix)` per kind, `continue` on mismatch): each
   scanner's own filter is what makes the *other* grammar invisible to it,
   symmetric by construction. `DisjointGrammarTests
   .test_block_is_not_a_region_kind_and_no_kind_prefixes_another` checks
   prefix-relation in both index orders (`i`/`j` swapped) over all three
   tokens (`block` + both kinds). The behavioural test
   (`test_one_block_plus_both_regions_are_seen_by_their_own_parser_only`)
   exercises a `main.tex` with one real block AND both regions present
   simultaneously: `status` finds exactly 1 block (region lines invisible to
   Phase 1), the region parser finds exactly 2 regions (block line invisible
   to it) — genuinely bidirectional, executed, passing.
2. **Vocabulary line** — `contributions` (a fact id) admitted into
   `requires_declarations` at the contract-header level already refuses
   `UNKNOWN_DECLARATION` via `paper_contract.py:145`'s pre-existing call to
   `paper_vocabulary.validate_declaration` (prior phase, out of this
   change's scope but confirmed still wired). At this change's own layer
   (`declare`'s vocabulary boundary), Mutation 6 swaps
   `validate_declaration` for `validate_fact` inside `paper_declarations.py`
   and the `UNKNOWN_DECLARATION` guard fails red — executed, confirmed.
3. **`insumos-observer`'s "decides nothing" boundary** — confirmed as a real
   mechanism, not prose: (a) capability — `tools: Read, Glob, Grep` in the
   frontmatter, no Write/Edit/Bash, asserted by
   `InsumosObserverThreatMatrixTests` (executed, passed); (b) schema — its
   documented return shape (`satisfied: bool` + `evidence: [path, quote]`)
   carries no `value`/`resolution` field, matched by
   `paper_declarations.validate_observation_report`'s own accepted shape;
   (c) observable/derived partition — `OBSERVABLE_FACTS` (5) /
   `DERIVED_FACTS` (4) / `STRUCTURAL_FACTS` (1), held by exact equality
   against `paper_vocabulary.FACTS` and pairwise disjointness, asserted at
   import time in `paper_declarations.py` and pinned by
   `DeclarationsTests.test_the_partition_is_pairwise_disjoint_and_covers_every_fact`
   (executed, passed). `validate_observation_report` refuses
   `NOT_AN_OBSERVABLE_FACT` for any id outside the five, and
   `EVIDENCE_CONFLATED` when `implementation`/`results` share one evidence
   path — both executed (`ObservationReportTests`, Mutation 7).
4. **`MARKER_PREFIX` pin failure message** — read directly:
   `test_marker_prefix_is_pinned_exactly`'s failure message states the pin
   "is pinned exactly, trailing space included, deliberately brittle: a
   legitimate Phase 1 edit to this constant is EXPECTED to redden this test,
   on purpose -- it is not a bug in this test and must not be loosened to
   admit the change silently." Matches the requirement exactly.
5. **Provenance** — `unprovenanced` (no `--contract` at write time) and
   `drifted` (contract byte edited after write) both confirmed by direct
   execution: `ProvenanceTests.test_a_block_written_without_contract_is_unprovenanced`
   and `.test_drift_is_reported_on_a_single_byte_edit_and_block_is_untouched`,
   plus `PlanTests.test_plan_reports_drift_after_a_contract_edit` — all
   passed.
6. **`OBJECTIVE_FLOW` seal** — read `paper_objective.py`'s module-level
   `OBJECTIVE_FLOW` assignment: a pure dict literal, no function calls, no
   f-strings inside nested values beyond plain string concatenation-free
   literals — `ast.literal_eval`-safe, matching `test_agents.py
._python_objective`'s exact extraction method (`ast.parse` + `ast.literal_eval`
   on the `ast.Assign` node). `insumos-observer.md`'s `stretch: declare`
   carries the required disclaimer in its own body ("you do not run `declare`
   ... a human runs `declare`; your report is what they consume to do it") —
   read directly, present, not a completion claim.
7. **Every `scripts/` module is imported at `paper_cli.py` module level** —
   derived independently (AST walk of `paper_cli.py`'s top-level `import`
   statements vs. every `.py` file in `scripts/`): **zero modules
   unimported**. Confirmed both by this independent derivation and by
   `RefusalRosterTests` (executed, passed), which is the test that would
   catch a roster hole if one existed.

### CRITICAL — Reopening does not invalidate anything, despite a passing test

`specs/paper-declarations/spec.md`, **Requirement: Reopening Invalidates
Exactly the Blocks That Named It**: `--reopen <id>` MUST derive the affected
block set and MUST mark stale, **in the provenance region**, exactly that
set.

This is unimplemented. Confirmed by direct execution, not by reading:

- `paper_declarations.reopen()` only rewrites the `declarations` region
  (clears `fixed`, bumps `generation`). It never touches the `provenance`
  region and never calls `affected_blocks()`.
- `paper_provenance.drift()` compares only the persisted `contract_sha256`
  against the contract file's current digest. It takes no corpus, no
  `requires_facts`/`requires_declarations`, and never reads the `generation`
  field it itself persists — that field is written on every provenance
  record and read back by nothing.
- `affected_blocks(corpus, target_id)` — the pure function this requirement's
  mechanism is supposed to be — has **exactly one caller in the entire
  repository**: the test that exercises it directly
  (`DeclarationsTests.test_reopen_narrows_to_exactly_the_naming_blocks`).
  Confirmed by grep across every `.py` file under `scripts/` and every test
  file: zero other call sites.
- **Manually reproduced end-to-end** (script executed, not asserted): scaffold
  a paper, `declare --declaration repository-url`, `open`+`substitute --contract`
  a block whose section contract names `requires_declarations:
  [repository-url]`, `plan` → block reports `"state": "current"`. Then
  `declare --reopen repository-url` (contract file byte-for-byte unchanged).
  `plan` again → block **still** reports `"state": "current"`. The
  declaration that this exact block depends on was just reopened and is no
  longer fixed, and `plan` gives no signal of it whatsoever.

The shipped test
(`DeclarationsTests.test_reopen_narrows_to_exactly_the_naming_blocks`) is
green, and it is exactly the shape flagged for this verify pass: it proves
`affected_blocks()` computes the right *set* in isolation, using synthetic
`BlockRecord`s constructed directly in the test — it never calls `reopen()`,
never calls `plan`, and never observes the `provenance` region at all. The
spec's own scenario text ("WHEN `--reopen repository-url` runs / THEN the two
naming blocks are marked stale") describes a behavior this test does not
exercise. Mutation 5 (which mutates `affected_blocks` itself and confirms
that same isolated test goes red) is real and passes, but it only proves the
orphaned function's own guard fires — it says nothing about whether the
function is reachable from any actual command, because it isn't.

The apply's own progress report concedes this as "deviation #2" (`affected_blocks`
is "a pure function... never a literal write of a 'stale' flag," staleness
"could" be computed later by `plan` from generation comparison) but frames it
as an implementation-detail choice rather than an unmet MUST, and the same
report's "Issues Found: None blocking" is not accurate given this gap — the
"derived read-time property `plan` could compute" was never built; `plan`'s
`drift()` call passes no generation and no corpus, so it cannot derive it
either.

- **Adjudication**: artefact wrong — the spec's MUST clause and the design's
  own "Drift is reported when... or when the block's contract names an entry
  reopened since its recorded generation" are both unimplemented.
- **Evidence**: CONFIRMED by execution (manual end-to-end reproduction above,
  plus the grep confirming zero non-test callers of `affected_blocks`).
- **Remedy scope**: wire `affected_blocks` (or an equivalent generation
  comparison) into either `reopen()`'s own write path or `plan`'s provenance
  loop; the spec's own wording ("MUST mark stale, in the provenance region")
  favors the former.

### WARNING — One untested scenario, two reporting-honesty gaps

- `specs/contract-provenance/spec.md`'s "One edit flags every block of the
  section" scenario (two blocks sharing one contract file, one edit flags
  both) has **no covering test** — `compute_plan` computes `drift()`
  independently per block with no shared/cached state, so the property is
  very likely true by construction, but it is UNTESTED, not COMPLIANT, by
  this skill's own compliance-status rules.
- The 5 unrelated `test_proposal_implementation.py` failures mean the
  literal declared full-suite command did not exit 0 during this
  measurement window. Not a defect of this change (confirmed unrelated by
  content and file scope), but recommend a clean full-suite re-run once the
  concurrent sibling apply settles, before archive.
- The 6 skipped tests in the full run were not independently re-verified by
  name against the apply-progress's "6 pre-existing skips unrelated to this
  change" claim (the non-verbose `discover` run does not print skip names
  without `-v`, and a full `-v` re-run was out of this pass's time budget
  given the 7-9 minute runtime already spent twice).

### Spec Compliance Matrix (abridged — 19 requirements, 27 scenarios total)

| Requirement | Scenario | Test | Result |
|---|---|---|---|
| guidance-registry: Per-Folder Marker File | valid marker classifies | `GuidanceRegistryTests.test_valid_marker_classifies_its_folder` | ✅ COMPLIANT |
| guidance-registry: Per-Folder Marker File | out-of-vocabulary refuses | `test_out_of_vocabulary_class_refuses` | ✅ COMPLIANT |
| guidance-registry: Unmarked → unclassified | fresh clone all unclassified | `test_fresh_clone_reports_every_folder_unclassified_refuses_nothing` + Mutation 4 | ✅ COMPLIANT |
| guidance-registry: Unmarked → unclassified | name-alike stays unclassified | `test_folder_named_like_a_class_stays_unclassified` | ✅ COMPLIANT |
| guidance-registry: No hardcoded path | two arbitrary folders | `test_two_arbitrarily_named_folders_each_classify_from_their_own_marker` | ✅ COMPLIANT |
| paper-declarations: Region Grammar | hand-edited refuses | `test_declarations_hand_edited_refuses_and_writes_nothing` | ✅ COMPLIANT |
| paper-declarations: Invisible to Phase 1 | status sees no block | `DisjointGrammarTests.test_regions_only_file_...` | ✅ COMPLIANT |
| paper-declarations: Invisible to Phase 1 | narrowing caught | `test_marker_prefix_is_pinned_exactly` + part 1-3 | ✅ COMPLIANT |
| paper-declarations: Two Record Kinds | contributions is a fact | `test_recording_a_fact_as_a_declaration_refuses_unknown_declaration` | ✅ COMPLIANT |
| paper-declarations: Two Record Kinds | Mutation 6 | `test_mutation_6_...` | ✅ COMPLIANT |
| paper-declarations: Progressive Filling | fixed refuses overwrite | `test_a_fixed_entry_refuses_a_plain_overwrite` + Mutation 2 | ✅ COMPLIANT |
| paper-declarations: Progressive Filling | reopen admits new value | `test_reopen_then_declare_admits_a_new_value` | ✅ COMPLIANT |
| **paper-declarations: Reopening Invalidates** | **reopen narrows to naming blocks** | `test_reopen_narrows_to_exactly_the_naming_blocks` (tests orphaned `affected_blocks()` only) | ❌ **FAILING** — confirmed by execution, requirement's own MUST clause unimplemented |
| paper-declarations: Reopening Invalidates | Mutation 5 | `test_mutation_5_...` | ⚠️ PARTIAL — proves the orphaned function's own guard, not the requirement |
| paper-declarations: insumos-observer | frontmatter tools | `InsumosObserverThreatMatrixTests` | ✅ COMPLIANT |
| paper-declarations: declare registered | new refusal classified | `RefusalRosterTests` (executed) | ✅ COMPLIANT |
| contract-provenance: Region Grammar | hand-edited refuses | `test_provenance_hand_edited_refuses_and_writes_nothing` | ✅ COMPLIANT |
| contract-provenance: Record Written at substitute | baseline persists | `test_provenanced_write_persists_the_write_time_baseline` | ✅ COMPLIANT |
| contract-provenance: Record Written at substitute | Mutation 3 | `test_mutation_3_...` | ✅ COMPLIANT |
| contract-provenance: Unprovenanced | block reported unprovenanced | `test_a_block_written_without_contract_is_unprovenanced` | ✅ COMPLIANT |
| contract-provenance: Drift Compares Baseline | single byte edit reported | `test_drift_is_reported_on_a_single_byte_edit_and_block_is_untouched` | ✅ COMPLIANT |
| contract-provenance: Whole-File Over-Reports | one edit flags every block of section | none found | ❌ UNTESTED (low-risk by construction) |
| contract-provenance: plan Aggregates | all three concerns, read-only | `PlanTests` (both tests) | ✅ COMPLIANT |
| contract-provenance: plan Registered | new refusal classified | `RefusalRosterTests` | ✅ COMPLIANT |
| block-substitution: --contract optional | identical bytes with/without | `test_provenanced_and_unprovenanced_writes_produce_identical_block_bytes` | ✅ COMPLIANT |
| block-substitution: --contract optional | unreadable path refuses first | `test_unreadable_contract_refuses_before_any_write` | ✅ COMPLIANT |
| block-substitution: additive roster | hand-edited still refuses | `test_hand_edited_block_still_refuses_even_with_contract` | ✅ COMPLIANT |

**Compliance summary**: 25/27 scenarios compliant, 1 FAILING (proven by
execution), 1 UNTESTED.

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Canonical JSON serialization (`sort_keys=True`) | ✅ Implemented | `serialize_body`, read directly |
| No `--adopt` path for either region | ✅ Implemented | confirmed absent in both `paper_declarations.py`/`paper_provenance.py` |
| `.gitignore:78` covers `paper/*` | ✅ Implemented | read directly, matches design.md citation |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| Module layout — four siblings, nothing in `_core/` | ✅ Yes | all four new modules under `scripts/` |
| Digest covers region body, no self-heal | ✅ Yes | confirmed |
| Two grammars coexist by mutual non-prefix | ✅ Yes | confirmed bidirectionally, executed |
| `insumos-observer` cannot decide, by schema+capability | ✅ Yes | confirmed |
| Four stacked slices | ✅ Yes | commits match |
| Mutation harness generalized | ✅ Yes | `tests/paper_mutation.py`, all 7 mutations executed |
| A fact the agent may observe is a partition | ✅ Yes | confirmed, pinned, disjoint |
| **Drift reported when contract digest OR generation-reopen differs** | ❌ **No** | design.md's own text, unimplemented — same gap as the CRITICAL finding above |

### Issues Found

**CRITICAL**:
1. `specs/paper-declarations/spec.md`'s "Reopening Invalidates Exactly the
   Blocks That Named It" requirement is unimplemented at the integration
   level — `declare --reopen` never marks any block stale, `plan` never
   reflects a reopened fact/declaration a written block depends on, and the
   pure function that would compute the affected set (`affected_blocks`) has
   no caller anywhere outside its own isolated test. Confirmed by direct
   end-to-end execution, not by reading.

**WARNING**:
1. `contract-provenance`'s "One edit flags every block of the section"
   scenario (two blocks sharing one contract) has no covering test.
2. The apply-progress artifact's "Issues Found: None blocking" is inaccurate
   given the CRITICAL finding above.
3. The declared full-suite command exited non-zero during this measurement
   window due to 5 failures entirely in an unrelated skill
   (`test_proposal_implementation.py`), attributable to the disclosed
   concurrent sibling apply's in-flight work — recommend a clean re-run
   before archive.

**SUGGESTION**:
1. The 6 skipped tests in the full run were not independently re-verified by
   name in this pass.

### Verdict

**FAIL**

One CRITICAL: a spec MUST clause ("mark stale, in the provenance region")
is unimplemented, masked by a test that proves an orphaned helper function
correct in isolation while the actual `--reopen` → `plan` behavioral chain
was directly, executably shown to give zero signal after a dependency
reopens. Every other requirement across all four spec files was confirmed
compliant by direct execution (52/52 in this change's own test module, all
7 mutation-proof tests, the refusal-roster derivation, and a manual
end-to-end CLI reproduction).

---

## Re-Verification (scoped) — 2026-09-11

**Trigger**: corrective commit `12ac0b7` ("reopening a declaration now unfixes
what plan reports current"), addressing the sole CRITICAL from the pass
above. **Scope**: (1) independently re-falsify that exact CRITICAL, not by
re-reading the new test but by re-driving the real CLI chain myself; (2) rule
on the second orphan (`validate_observation_report`) the corrective found and
deliberately left unfixed, by reading the spec directly rather than trusting
the corrective's own argument; (3) re-run the declared test commands.

This pass ran in two sessions across a usage-limit reset. Between them, three
things changed on disk, none caused by this pass: `npm run typecheck`'s
missing dev dependencies were installed (a non-zero build exit is meaningful
again); two classes of orphaned test debris were cleaned
(`_open_defect_ladder_fixture_<pid>_*.py` under
`.claude/skills/proposal-implementation/scripts/`, and six generated
directories under `implementations/`, now holding only its tracked
`.gitkeep`); and two sibling changes landed on top of this one
(`no-claim-without-a-source-that-holds-it`,
`the-writer-may-assert-only-what-it-was-given`), adding ten new modules, three
new `paper_cli.py` verbs, and growing the refusal roster and its measured-count
pin. That growth is expected and is not drift in this change's own scope —
none of it touches `paper_declarations.py`, `paper_provenance.py`,
`paper_region.py`, `paper_guidance.py`, or this change's own test module.

This pass is read-only throughout: no edit, stage, or commit was made to any
tracked file. One scratch paper/section corpus was created under
`implementations/.verify-reopen-falsify-<pid>/` to drive real `paper_cli.py`
subprocess calls, twice (once per session, against two different HEADs), and
removed after each run — confirmed absent from `git status` and from the
`implementations/` directory listing both times.

### CRITICAL re-falsification — independently reproduced, not merely re-read

Built a 3-block corpus, distinct from the corrective's own end-to-end test,
specifically to exercise the four properties a persisted "stale" flag could
get wrong and the narrowing property a flat "everything since generation N"
implementation would get wrong:

- `sec.a` — `requires_declarations: [repository-url]` (direct channel)
- `sec.b` — `requires_facts: [dataset]` (indirect channel: a *fact*, not a
  *declaration*)
- `sec.c` — `requires_declarations: [grant-title]` (depends on neither id
  touched below — the narrowing control)

All three declared, opened, and `substitute --contract`-written in the same
session (one generation-counter batch). Then, driven as real `paper_cli.py`
subprocesses:

| Step | Action | `sec.a` | `sec.b` | `sec.c` |
|---|---|---|---|---|
| 0 | baseline `plan` | current | current | current |
| 1 | `declare --reopen repository-url` → `plan` | **drifted** | current | current |
| 2 | resubstitute `sec.a` → `plan` | current | current | current |
| 3 | `declare --reopen repository-url` again (double reopen, no intervening `declare`) → `plan` | **drifted** | current | current |
| 4 | resubstitute `sec.a`, then `declare --reopen dataset` (fact, indirect channel) → `plan` | current | **drifted** | current |

Run twice, once on commit `0ea0e7c` (before the usage-limit reset) and once
fresh on commit `f3b3fcf` (after it, with the sibling changes' new verbs and
modules present) — **byte-identical results both times**. Every transition
matched the requirement's own text ("Reopen narrows to the naming blocks...
A block whose contract does not name `<id>` MUST be left untouched")
exactly:

- **Original defect, reproduced fixed**: step 1 reproduces the orchestrator's
  own manual falsification from the FAIL pass above — `declare` →
  `substitute --contract` → `declare --reopen` → `plan` — and this time
  `plan` reports `drifted`, not `current`.
- **Narrowing, not "everything written after"**: `sec.b` and `sec.c` were
  written in the identical generation batch as `sec.a`, yet neither flipped
  when `repository-url` was reopened, because neither names it in its own
  `requires_facts`/`requires_declarations`. This is the case a coarser
  "mark everything written before this generation stale" implementation
  would get wrong and this one does not.
- **A block re-substituted after a reopen** (step 2): staleness cleared
  correctly with no explicit "unmark stale" step anywhere in the code —
  because nothing is persisted to unmark; `plan` simply stops finding the
  block's own fresh provenance generation older than the record's. A
  persisted-flag design would need a resubstitute-clears-flag code path;
  none exists here and none is needed.
- **A declaration reopened twice** (step 3): the shared `generation` counter
  bumps monotonically on every `declare`/`reopen` and the specific record's
  own `generation` field is overwritten to the latest value each time (only
  one record per `kind`+`id` is ever kept) — the second reopen is detected
  exactly as the first was, with no stale first-reopen residue.
- **A block naming the reopened id only indirectly** (step 4): `dataset` is
  a *fact*, reopened through the same `--reopen <id>` verb but matched via
  `requires_facts` rather than `requires_declarations` in
  `affected_blocks`'s `or` check. `sec.b` — the only block naming `dataset`
  — was the only one to flip. Confirmed the two vocabularies
  (`paper_vocabulary.FACTS`, `paper_vocabulary.DECLARATIONS`) are disjoint
  (`DeclarationsTests.test_facts_and_declarations_vocabularies_are_pinned_and_disjoint`,
  read and executed), so this "indirect" channel can never falsely match a
  declaration reopen against a fact-only block or vice versa.

**Read (not merely trusted) design.md lines 219–232**: "Drift is reported
when the recorded `contract_sha256` differs..., or when the block's contract
names an entry reopened since its recorded `generation` — read from Phase
2's parsed `requires_facts` / `requires_declarations`, never from write
order." This is a read-time-derivation decision, made in the accepted
design artifact for this exact mechanism, and it pre-dates the corrective.
The spec's own more literal "MUST mark stale, in the provenance region"
wording is satisfied in effect — `plan`'s own report is the thing an
operator reads as "the provenance region's state," and it now correctly
names the block `drifted`. I am not flagging the write-vs-read mechanism
choice as a deviation: design.md is the more specific artifact governing
this exact mechanism, and its text was written before this corrective and
already pointed at the read side.

Also ran the corrective's own new test in isolation, together with the rest
of the module this change owns, in both sessions:
`.venv/bin/python -m unittest tests.test_paper_decisions -v` →
**53/53 passed** both times (52 pre-existing + 1 new:
`ReopenInvalidatesProvenanceEndToEndTests.test_reopen_then_plan_stops_reporting_current`),
confirming it is genuinely green, not merely claimed in the commit message.

**Verdict on the CRITICAL**: RESOLVED. Confirmed by independent execution
distinct from the corrective's own proof, exercising four edge cases a
persisted flag or a coarser generation cutoff would have gotten wrong, plus
the original disproof case, reproduced identically across two separate HEADs.
No residual gap found in the mechanism itself.

### Second orphan — ruled on by reading the spec, not the corrective's argument

Read `specs/paper-declarations/spec.md`'s own `Requirement: insumos-observer
Reports Fact Satisfaction, Decides Nothing` directly (lines 123–137, quoted
in full below, nothing paraphrased, re-confirmed unchanged after the
sibling changes landed):

> The `insumos-observer` agent MUST read its four declared input sources and
> report, for each of the ten facts, whether it is satisfied. It MUST NOT
> write to the `declarations` region, MUST NOT call `declare`, and MUST NOT
> recommend or select a value. This is a checkable property: an executed
> run of the agent against a fixture repository MUST leave the
> `declarations` region's digest unchanged.
>
> #### Scenario: An observation run changes nothing on disk
> - GIVEN a repository with an existing `declarations` region
> - WHEN `insumos-observer` runs and reports fact satisfaction
> - THEN the `declarations` region's body and digest are byte-identical
>   before and after the run

Every MUST clause describes the *agent's own behavior* (reads sources,
reports, never writes/calls `declare`/recommends), checked via an executed
run leaving the `declarations` region's digest unchanged. **No clause names
`validate_observation_report`, and no clause names any runtime consumer for
the observation report at all** — unlike the CRITICAL above, where
`Requirement: Reopening Invalidates Exactly the Blocks That Named It`
explicitly named the mechanism (`--reopen <id>` MUST derive the affected
block set... and MUST mark stale). This requirement names no equivalent
mechanism for the observation report.

Confirmed by grep across every `.py` file in the repository, re-run after
the sibling changes landed: `validate_observation_report` has exactly two
callers, both inside `tests/test_paper_decisions.py`
(`ObservationReportTests`, `ObservationReportMutationTests`) — zero
production callers. Same orphan shape as `affected_blocks` was, but not a
spec violation, because no MUST clause requires it to be wired into any
command.

**Ruling**: accepted debt, not a second CRITICAL. Recorded here explicitly
so a future verify pass does not rediscover this as a "new" defect — it was
found, considered, and knowingly deferred, with the reasoning on record
(also independently confirmed in `tasks.md`'s own corrective-batch notes and
in `paper_cli.py`'s own comment at the refusal-classification block:
"consumed by a human reading `insumos-observer`'s report, never called from
a [CLI verb]").

### Is the "decides nothing" boundary enforced at all, or only at the edges?

Answered plainly, as asked: **the boundary has exactly one live,
runtime-enforced mechanism today — the agent's own tool grant.**
`insumos-observer.md`'s frontmatter carries `tools: Read, Glob, Grep` and
none of `Write`/`Edit`/`Bash`; this is confirmed real (not merely
documented) by `InsumosObserverThreatMatrixTests` and by the fact that the
agent-runtime's own tool-permission system would refuse a `Write`/`Edit`/
`Bash` call from a process granted only those three tools. This is genuine
capability-level enforcement.

Everything else — the documented return shape (`satisfied`/`evidence`, no
`value`/`resolution` field) and `validate_observation_report`'s own
`NOT_AN_OBSERVABLE_FACT` / `EVIDENCE_CONFLATED` checks — exists **only as a
schema definition exercised by its own unit tests**. At the actual point of
consumption — a human, or some future automated step, reading the agent's
returned report and deciding what to do with it — **there is currently zero
enforcement**: nothing on any executable path validates that the report
stays inside the five `OBSERVABLE_FACTS`, nothing catches evidence
conflation, and nothing would stop a future caller from silently piping the
report into `declare` without ever routing through this validator. The
boundary today is capability-only; the schema half is inert until something
calls it.

**Concrete recommendation, informed by a sibling verify pass**: a sibling
verify reported three CRITICAL findings of the same general shape as the
original CRITICAL here — spec scenarios describing agent-side behavior with
no executing test — and fixed them with tests that *prove an absence*
(e.g., asserting the CLI references no MCP config; asserting a connector is
absent from the resolver set), because there is no running consumer to
observe otherwise. The same pattern fits here and is the honest way to hold
this specific gap without overclaiming: rather than a comment asserting
"never called from a CLI verb," a small static test could assert
`validate_observation_report` is imported/called nowhere in `paper_cli.py`
(or any `cmd_*` function), pinning the *absence* of wiring as a checked fact
rather than an unverified prose claim, until a future change adds a real
consumer and that test is replaced by a positive one exercising it.

### Test re-execution (this pass — clean, post-reset)

- `npm test` → **559/559 passed**, exit 0 (isolated re-run; log hash
  `sha256:f7a9c977209f9933188a4771a6dde1c6180344a8f66cd41d4a3d9d6594eaed07`).
- `npm run typecheck` → **exit 0**, clean. Confirmed genuinely passing by
  direct execution now that the dev dependencies are actually installed —
  a non-zero build exit is a real signal again, not a pre-existing excuse.
- `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` → **3085
  ran, 0 failed, 6 skipped, exit 0** (log hash
  `sha256:3022a1c0fd303416d5654a9fab03b9b0d24c31571ec4629e218b39b8cacda1af`).
  Genuinely clean this time: the leftover-directory count grew across sibling
  changes (3011 → 3085 tests, reflecting the two landed sibling changes'
  own new tests) but nothing failed. The two contamination sources seen in
  this pass's own first session — a leftover `implementations/` directory
  from a killed run, and `RefusalRosterTests` caught mid-edit by a
  then-uncommitted `paper_vocabulary.py` change — are both gone now that the
  debris was cleaned and the sibling changes settled. Combined declared-command
  log hash (`npm test` output + python output, concatenated):
  `sha256:4d5ec256d72c5e5d3b611ff3425b5cc7f01ff6dfeb6cc9e425dcfdae4d2f1282`.
- Isolated re-run of every file this change owns:
  `tests.test_paper_decisions` → **53/53 ok**, run twice across both
  sessions.
- `tests/test_paper_writing.py::RefusalRosterTests` — re-run clean this
  session: 5/5 ok. (This pass's earlier session caught it mid-flight,
  mid-edit, by a different SDD change's uncommitted work on a shared
  vocabulary file; that is resolved now, not a defect of this change either
  way — this change never touches `MODES`/`validate_mode`.)

### Updated Spec Compliance (delta from the pass above)

| Requirement | Scenario | Result (then) | Result (now) |
|---|---|---|---|
| paper-declarations: Reopening Invalidates | reopen narrows to naming blocks | ❌ FAILING | ✅ **COMPLIANT** — re-proven by independent execution above (twice, across two HEADs), plus the corrective's own e2e test, 53/53 |
| paper-declarations: Reopening Invalidates | Mutation 5 | ⚠️ PARTIAL | ✅ **COMPLIANT** — the guard it exercises is no longer orphaned |

`contract-provenance`'s "One edit flags every block of the section" scenario
remains UNTESTED (unchanged from the pass above — out of this scoped
re-verification's remit; still low-risk by construction per the original
report's reasoning, since `compute_plan` computes `drift()` independently
per block with no shared/cached state).

**Updated compliance summary**: 26/27 scenarios compliant, 0 FAILING, 1
UNTESTED (unchanged, non-blocking).

### Issues Found (this pass)

**CRITICAL**: None. The one CRITICAL from the pass above is resolved and
independently re-falsified twice, across two separate commits.

**WARNING**:
1. `contract-provenance`'s "One edit flags every block of the section"
   scenario still has no covering test (unchanged from the original pass;
   low-risk by construction, not re-litigated here).

**SUGGESTION**:
1. `validate_observation_report` is accepted debt (see ruling above) — a
   future change that wires `insumos-observer`'s report into an automated
   consumer should route it through this validator rather than re-deriving
   the check, and should treat that wiring as closing this exact gap.
2. Pin the current absence of a `validate_observation_report` caller with a
   small static test (mirroring the sibling verify's absence-proving-test
   pattern), rather than relying on a source comment alone, so this remains
   a checked fact rather than an unverified claim if it drifts.

### Updated Verdict

**Structured envelope**: `fail` (see the top-of-file note). **Substantive
verdict**: **PASS WITH WARNINGS** — zero blockers, zero CRITICAL findings.

The gap between these two is exact and named, not hand-waved: the admission
tool used to persist this report enforces `completed == total` for both
`requirements` and `scenarios` before it will admit a `pass` or
`pass_with_warnings` verdict, with no severity carve-out — an UNTESTED
scenario blocks a passing verdict exactly as hard as a FAILING one would,
regardless of how low-risk it is judged to be. This pass carries forward
ONE such scenario, unchanged from the pass above and out of this scoped
re-verification's remit (`contract-provenance`'s "One edit flags every
block of the section"). Under that rule, `requirements: 18/19` and
`scenarios: 26/27` — both genuinely short of total by exactly that one
carried-over gap — force `verdict: fail` at the structured-envelope level,
even though `blockers: 0` and `critical_findings: 0` are both true and
independently verified above.

The sole CRITICAL is resolved and independently re-proven twice, across two
separate commits either side of a session reset — not by re-reading the
corrective's own test, but by driving five additional real `paper_cli.py`
subprocess sequences covering the original defect plus four edge cases
(narrowing, resubstitute-after-reopen, double-reopen, and an indirect
fact-channel match) that a less careful fix could have gotten wrong. The
second orphan the corrective found (`validate_observation_report`) is ruled
accepted debt by direct spec reading, not by trusting the corrective's own
argument — no MUST clause names it as a required runtime consumer, unlike
the CRITICAL requirement, which did. The `insumos-observer` "decides
nothing" boundary is enforced today only at the agent's tool-grant
capability level; the schema/validator half is inert until wired, and a
concrete absence-proving-test recommendation is recorded to hold that
honestly. Both declared commands now execute clean (`npm test` 559/559 exit
0; the full Python suite 3085/3085 exit 0; `npm run typecheck` exit 0). The
only remaining issue is the same pre-existing UNTESTED (non-blocking,
low-risk-by-construction) scenario already on record from the pass above —
carried forward, not re-litigated, and it is the sole reason the structured
envelope reads `fail` rather than `pass_with_warnings`.

**Archivable**: yes. Nothing blocking remains for this change; the one open
item is a pre-existing, low-risk-by-construction test gap the original pass
already accepted as non-blocking, and the admission tool's strict
completeness rule — not a substantive defect — is why the structured
verdict field reads `fail`.
