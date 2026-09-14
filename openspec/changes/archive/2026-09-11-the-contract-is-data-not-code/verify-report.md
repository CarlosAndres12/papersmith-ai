```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:a7418e440727985fc0d53ecfedb136395b334cfc9d5cfcca5067bc097b23439e
verdict: fail
blockers: 0
critical_findings: 0
requirements: 10/10
scenarios: 20/20
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:1972eac3f68ffbd2d2a7c3bd5c7582b7b894f7f81504961090583889aaf9cd32
build_command: npm run typecheck
build_exit_code: 127
build_output_hash: sha256:9bafdc78def593e18fc88a6a7e435a843f4e20721282d1334f7f954cb3a5df68
```

## Re-verification Addendum (scoped, 2026-09-11)

**Scope**: this addendum re-checks ONLY the two findings the original pass
below raised (C1, W1), against the corrective commit `0422dd1` ("fix(paper-
writing): the transcription lock reads prose, not its own header",
test-file-only, `tests/test_paper_contract.py` +158/-8 lines). All other
sections of this report (Completeness, static-evidence correctness,
coherence, S1) are UNCHANGED from the original pass and are not re-derived
here; they are carried forward as history below.

**Evidence revision**: `HEAD` at `12ac0b7` (this branch's tip at re-
verification time; `0422dd1` is three commits back, `12ac0b7` two commits
ahead of it and unrelated — a same-branch sibling fix for a different
change, `the-paper-carries-its-own-decisions`). `evidence_revision` above
hashes that `HEAD` commit id.

### C1 — RESOLVED, confirmed by independent mutation, not by re-reading the diff

The corrective adds `OrderTests.test_back_matter_renders_last_while_its_writing_order_place_is_graph_derived_not_fact_derived`,
covering `writing-readiness`'s previously-untested "Position reports
rendering order separately from writing order" scenario (back matter:
`position` is the maximum/last among shipped sections; every back-matter
block requires zero facts; the writing-order derivation must not rank it
ahead of still-fact-blocked blocks despite that).

Per the instruction, this was not accepted on the corrective's own say-so.
Independently, in this session: `paper_graph._sort_key` was monkeypatched
in-memory (no file written, no repo mutation) to `(0, record.block_index,
qualified_id)` — neutralizing `position`'s contribution to the tie-break
while leaving block-index/id ordering intact — and the new test was re-run
against that mutated function alone. It went **red**:

```
AssertionError: 40 not greater than 42 : back-matter.bm-appendices (zero
missing facts) landed before title-and-keywords.title (still fact-blocked)
in the writing order -- readiness, not the graph, appears to be deciding
placement
```

This is the requested falsification: the test measurably depends on
`position` participating in the sort, not merely on the graph shape. With
`_sort_key` restored (unmutated), the same test passes. **C1 is closed** —
the scenario now has a covering test, and that test is proven non-vacuous
by mutation rather than accepted by inspection.

### W1 — RESOLVED, the original vacuity proof re-run against current code and now correctly rejected

The corrective replaces the whole-file substring read
(`Path(source["file"]).read_text()`, header included) with `_quote_in_body`,
which reads only `paper_contract.parse()`'s own parsed prose **body** for
the named file. It also adds
`test_a_fabricated_quote_on_a_self_referential_edge_fails_the_lock`,
replaying the original falsification (a prose-absent, fabricated quote
substituted into `introduction.block-3`'s own `after` entry, on a temp
copy) and asserting the OLD (whole-file) shape still finds it while the NEW
(body-only) shape does not.

Independently, in this session, outside the test file's own helper: the
identical falsification was reproduced from a fresh throwaway script against
the real `sections/06-introduction.md` (never the tracked file) —
substituted the same fabricated sentence into a temp copy's header only,
confirmed it absent from the parsed body, then checked both shapes:

- OLD shape (raw whole-file substring): **found** the fabrication (`True`)
  — reproduces the original vacuity exactly.
- NEW shape (`_quote_in_body`, imported straight from `tests/test_paper_contract.py`,
  not reimplemented): **did not find** it (`False`) — the lock now rejects
  a prose-absent transcription on the one self-referential edge that made
  it vacuous.

**Generalization, checked rather than assumed**: the covering test
(`test_every_transcribed_afters_quote_is_a_substring_of_its_named_file`)
now calls `_quote_in_body` uniformly, inside one loop over every transcribed
`after` entry in the real corpus — no per-edge branch, no special case for
`introduction.block-3`. Ran that same `_quote_in_body` function by hand
against both shipped literal edges: `introduction.block-3` -> `related-work`
(self-sourced, `sections/06-introduction.md`) and `abstract` -> `conclusions`
(cross-sourced, `sections/07-conclusions.md`) — both report `quote_in_body =
True`, both through the identical function. Because the check is keyed only
on `source["file"]`/`source["quote"]` and never on whether that file equals
the holder section's own file, a third self-referential edge added tomorrow
would be checked by the same code path with no additional work — there is
no `introduction`-specific branch left to fall out of sync. `title-and-
keywords`'s third edge is position-derived (computed, not a literal
transcribed quote) and was never in this check's domain either before or
after the fix.

**W1 is closed**: no longer a live hazard, and the fix generalizes across
the whole transcribed-edge set by construction, not by enumeration.

### Test execution for this addendum

Three full-suite runs in this session, `npm test && .venv/bin/python -m
unittest discover -s tests -p 'test_*.py'` (this change's declared
`test_command`), against the live worktree while a concurrent sibling apply
(`no-claim-without-a-source-that-holds-it`) was actively landing uncommitted
changes on the same branch (`paper_cli.py`, `paper_vocabulary.py`,
`tests/test_paper_writing.py`, new `paper_evidence.py`/`paper_resolve.py`):

1. `.venv/bin/python -m unittest discover` alone: `Ran 2938 tests ... OK
   (skipped=6)`, exit 0.
2. Combined `npm test && ... discover`, run ~10 minutes later: `npm test`
   559/559 pass; Python suite `FAILED (failures=2, skipped=6)` — both
   failures in `tests.test_paper_writing.RefusalRosterTests`
   (`test_every_reachable_refusal_is_classified`,
   `test_the_derivation_finds_the_measured_count`), naming
   `DISCOVERY_UNAVAILABLE`/`IDENTIFIER_UNRESOLVED`/
   `PAPERSMITH_CONFIG_UNREADABLE`/`RESOLVER_ROLE_EMPTY` — refusal codes from
   `paper_evidence.py`/`paper_resolve.py`, the sibling apply's own new
   modules, caught mid-write (roster derivation saw the new imports before
   the classification dict / expected-count literal in the sibling's own
   test file had finished landing). **Not this change's scope**: neither
   module, neither test class, nor any of those four codes belongs to
   `the-contract-is-data-not-code`; re-running
   `tests.test_paper_contract.GraphTests`/`OrderTests` and
   `tests.test_paper_writing.RefusalRosterTests` immediately afterward, once
   the sibling's write had settled, both were green again — confirming a
   transient race on files this change does not own, not a regression here.
2. Combined run again, ~8 minutes later, sibling write settled: `npm test`
   559/559 pass; `Ran 2978 tests in 488.288s`, `OK (skipped=6)`, exit 0.
   `test_output_hash` above is this run's.

The rising total test count across these runs (2883 in the original pass ->
2938 -> 2978) is the same concurrent sibling apply committing/landing work,
consistent with the original report's own documented caveat on evidence
purity — not attributable to this change.

**Orphaned-fixture check** (named as a known trap): searched
`.claude/skills/proposal-implementation/scripts/` for
`_open_defect_ladder_fixture_<pid>_*.py` (hidden files included, `.gitignore`
disabled) — none found, and `git status` over that directory is clean. Not
the cause of anything observed here.

### Verdict of this addendum
Both scoped findings from the prior pass are resolved and independently
re-falsified, not merely re-read: **C1** now has a non-vacuous covering
test (proven red under a direct `_sort_key` mutation removing `position`
from the tie-break); **W1**'s lock now correctly rejects the exact
fabricated-quote reproduction that originally proved it vacuous, and the
fix is generalized across the whole transcribed-edge set by one shared
function, not special-cased. No new CRITICAL or blocking finding was
introduced by the corrective. `blockers: 0` and `critical_findings: 0`
above reflect that directly.

**Why the machine-readable `verdict:` field above still reads `fail`,
despite zero blockers and zero critical findings.** `gentle-ai
sdd-verify-validate` was run against this exact report (`--requirements 10
--scenarios 20`) before writing it, per this skill's own admission
discipline. It refuses to admit `pass` or `pass_with_warnings` while
`build_exit_code` is non-zero (`error: verify report admission denied:
passing verdict contradicts failing or incomplete evidence`, reproduced
directly against this tool on a minimal probe report — confirmed by toggling
only `build_exit_code` between `127` and `0` with everything else held
fixed). `build_exit_code: 127` is `npm run typecheck` -> `tsc: command not
found` — W2, the same pre-existing, environment-only gap already recorded
in the original pass, explicitly declared out of scope for this
re-verification by the launching agent's own instructions, and not
attributable to any file `the-contract-is-data-not-code` or its corrective
touches. `verdict: fail` here is therefore a **schema-gate artifact of an
unrelated, undeclared-in-scope environment limitation**, not a statement
that either C1 or W1 is unresolved, and not a statement that this change's
own implementation or tests are failing — they are not; both are green,
independently confirmed above and in the Build & Tests Execution evidence.

**Recommendation**: functionally archivable — every requirement this
change owns has a passing, non-vacuous covering test, and no CRITICAL or
open WARNING traces back to this change's own code. The remaining blocker
to a clean machine `pass` (`W2`/`tsc` missing) predates this change,
predates the corrective, and was already out of scope by explicit
instruction; it should be tracked and resolved as its own environment-setup
item, not treated as a reason to re-open `the-contract-is-data-not-code`.

---

## Original Verification Report (superseded verdict above; body kept as history)

**Change**: the-contract-is-data-not-code
**Version**: N/A (two new capabilities, no prior spec version)
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 23 (1.1-4.6) |
| Tasks complete | 23 |
| Tasks incomplete | 0 |

Note: apply-progress (Engram #1637, #1609) states "26/26 tasks" — the actual
numbered checkbox count in `tasks.md` is 23, all `[x]`. Bookkeeping mismatch
in the memory note, not in `tasks.md` itself; not a functional defect
(SUGGESTION below).

### Build & Tests Execution

**Build**: ❌ Failed (pre-existing environment gap, unrelated to this change)
```text
$ npm run typecheck
> papersmith-ai@0.1.0 typecheck
> tsc -p tsconfig.json
sh: tsc: command not found
```
`devDependencies` (`typescript`) are not installed in this environment. Not
part of the orchestrator-declared test runner for this change
(`npm test && .venv/bin/python -m unittest discover ...`), and unrelated to
`the-contract-is-data-not-code`'s own files. Reported honestly per the report
schema's required `build_*` fields rather than omitted.

**Tests**: ✅ 3442 passed / ❌ 0 failed / ⚠️ 6 skipped (by design, elsewhere in
the suite)
```text
$ npm test
ℹ tests 559 / pass 559 / fail 0

$ .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
Ran 2883 tests in 591.449s
OK (skipped=6)
```
Executed directly, both in full and via targeted class runs (`MutationTests`,
`HeaderInsertionTests`, `GraphTests`, `SchemaTests`, `VocabularyTests`,
`ReadinessTests`, `OrderTests`, `VocabularyLeakTests`, `RefusalRosterTests` —
all green individually as well).

**Caveat on evidence purity**: the working tree was not clean during this
run — a concurrent sibling apply (`the-paper-carries-its-own-decisions`) is
writing uncommitted changes to `paper_cli.py` and `tests/test_paper_writing.py`
on this same branch right now, exactly as flagged by the task. Inspected that
diff directly: it is purely additive (two new imports, `REGION_*`/`GUIDANCE_*`
roster entries for `paper_region.py`/`paper_guidance.py`), touches nothing
`the-contract-is-data-not-code` owns, and does not explain any finding below.
The 2883/559 counts reflect the current working tree (this change's four
committed commits plus that unrelated in-flight work), not an isolated
checkout of only `b1d67dc..afb9077`.

**Coverage**: not measured (no coverage tool configured for this stack) — ➖ Not available

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Front Matter Schema | Valid header parses | `test_paper_contract.py > SchemaTests.test_valid_header_parses_with_no_refusal` | ✅ COMPLIANT |
| Front Matter Schema | Missing mandatory field refuses | `SchemaTests.test_header_missing_position_refuses_naming_position` | ✅ COMPLIANT |
| Closed Fact Vocabulary | Listed fact parses | `VocabularyTests.test_a_listed_fact_parses` | ✅ COMPLIANT |
| Closed Fact Vocabulary | Unlisted fact refuses | `VocabularyTests.test_an_unlisted_fact_refuses_unknown_fact` | ✅ COMPLIANT |
| Closed Declaration Vocabulary | Listed declaration parses | `VocabularyTests.test_a_listed_declaration_parses` | ✅ COMPLIANT |
| Closed Declaration Vocabulary | Unlisted declaration refuses | `VocabularyTests.test_an_unlisted_declaration_refuses_unknown_declaration` | ✅ COMPLIANT |
| Closed Citations Regime | Valid regime parses | `VocabularyTests.test_a_valid_citations_regime_parses` | ✅ COMPLIANT |
| Closed Citations Regime | Invalid regime refuses | `VocabularyTests.test_an_invalid_citations_regime_refuses` | ✅ COMPLIANT |
| Byte-Clean Header Insertion | Digest matches after insertion | `HeaderInsertionTests.test_the_ten_shipped_contracts_carry_headers_matching_the_pre_migration_body_digests` | ✅ COMPLIANT |
| Transcribed `after` Edges Only | Shipped edge set is exactly three | `GraphTests.test_the_shipped_corpus_has_exactly_two_literal_cross_section_after_edges` + `test_title_and_keywords_position_derived_edge_targets_exactly_the_seven_body_sections` | ✅ COMPLIANT |
| Transcribed `after` Edges Only | Invented edge on a shipped contract fails | `GraphTests.test_every_transcribed_afters_quote_is_a_substring_of_its_named_file` | ✅ COMPLIANT as of `0422dd1` (was ⚠️ PARTIAL — see Finding W1, now RESOLVED above) |
| Per-Block Readiness | All-satisfied block is writable | `ReadinessTests.test_a_block_with_every_requirement_satisfied_is_writable` | ✅ COMPLIANT |
| Per-Block Readiness | Blocked only by a declaration | `ReadinessTests.test_a_block_blocked_only_by_a_declaration_is_not_writable` | ✅ COMPLIANT |
| Per-Block Readiness | Back matter: zero missing facts, declarations missing | `ReadinessTests.test_back_matter_reports_zero_missing_facts_and_its_declarations_missing` | ✅ COMPLIANT |
| Derived Writing Order | Related Work summary block ordered correctly | `OrderTests.test_related_work_precedes_introduction_block_3_and_follows_blocks_1_2_4` | ✅ COMPLIANT |
| Derived Writing Order | Cyclic graph refuses `ORDER_CYCLE` | `OrderTests.test_a_two_block_mutual_after_cycle_refuses_order_cycle_naming_both` | ✅ COMPLIANT |
| Derived Writing Order | Position reports rendering order separately from writing order | `OrderTests.test_back_matter_renders_last_while_its_writing_order_place_is_graph_derived_not_fact_derived` | ✅ COMPLIANT as of `0422dd1` (was ❌ UNTESTED — see Finding C1, now RESOLVED above) |
| Eleventh Contract Enters With No Code Change | Novel eleventh contract reads correctly | `MutationTests.test_mutation_a_the_eleventh_contract_is_novel_and_reads_correctly` | ✅ COMPLIANT |
| Eleventh Contract Enters With No Code Change | Reused combination proves nothing | `MutationTests.test_mutation_a...` (`assertNotIn` anti-vacuity guard, same test) | ✅ COMPLIANT |
| A Fact Outside the Ten Refuses | Out-of-vocabulary fact refuses on execution | `MutationTests.test_mutation_b_a_fact_outside_the_vocabulary_refuses_on_execution` | ✅ COMPLIANT |

**Compliance summary (updated)**: 20/20 scenarios fully compliant as of
`0422dd1` (originally 18/20 + 1 PARTIAL + 1 UNTESTED at the prior pass).

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Roster derivation completeness | ✅ Implemented | Measured by execution: `paper_cli_imported_modules()` resolves exactly the 6 sibling scripts under `scripts/` (`paper_block`, `paper_contract`, `paper_graph`, `paper_readiness`, `paper_scaffold`, `paper_vocabulary`) — identical to `scripts/*.py` minus `paper_cli.py` itself; no unimported module, no relocated hole |
| Refusal roster classification | ✅ Implemented | `RefusalRosterTests` green; in-memory inversion (deleted `SECTIONS_OUTSIDE_REPOSITORY` from `paper_cli.REFUSAL_CLASSIFICATION` at runtime, re-ran the derivation) correctly reports it missing — the lock fires, proven, not read |
| Byte-clean header insertion | ✅ Implemented | `test_forced_body_mutation_restores_original_bytes_and_refuses_body_mutated` patches `os.replace` to simulate write-time corruption and confirms `install_header` both detects it (`BODY_MUTATED`) and restores original bytes — the guard can fail, not just pass by construction |
| Validate-before-write | ✅ Implemented | `install_header`'s first statement is `parse_header(header)`, before any `path.read_bytes()`/write. `_atomic_replace` is the only disk writer across `paper_vocabulary.py`, `paper_contract.py`, `paper_graph.py`, `paper_readiness.py`, `paper_cli.py`, and it is only ever called from `install_header`, at both call sites after validation — no sibling writer with the pre-incident shape |
| Commit-history honesty note | ✅ Accurate (final state) | `git show --stat` on `b1d67dc` confirms `tasks.md` already ticked Phase 2 (2.1-2.4) in that commit, while `git show --stat` on `c26f21c` confirms `install_header`'s hardening and all ten `sections/*.md` header insertions landed only in the second commit — exactly as disclosed. Current `tasks.md` (from `c26f21c` onward) accurately reflects code state |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| `title-and-keywords`'s third edge is position-derived (orchestrator settlement, not spec's literal wording) | ✅ Yes | `paper_graph.py`'s `_position_derived_edges`, looked up by section id via `_KEYWORD_BODY_*` constants, never a hardcoded integer — confirmed by `test_position_derived_edge_is_computed_from_looked_up_positions_not_a_hardcoded_integer` (moved abstract's position and watched the body set move with it) |
| One flat id namespace, `ID_COLLISION` on block/section id overlap | ✅ Yes | `GraphTests.test_a_block_id_colliding_with_a_section_id_refuses_id_collision` |
| Roster derived from `paper_cli.py`'s own imports, never a hand-listed tuple | ✅ Yes | `paper_cli_imported_modules()`, AST-walked; confirmed matches disk by execution above |

### Issues Found (original pass; status column added by this addendum)

**CRITICAL**:
- **C1 — Spec scenario has no covering test.** [RESOLVED by `0422dd1` — see
  addendum above.] `writing-readiness` spec, Requirement: Derived Writing
  Order, Scenario "Position reports rendering order separately from writing
  order" (back matter's rendering `position` is last while its writing-order
  place is decided only by its absent `after` edges, never by `position`)
  had no dedicated test anywhere in `test_paper_contract.py` or
  `test_paper_writing.py` — confirmed by grepping both files for
  `back-matter`/`back_matter`; the only hits were digest constants, the
  position-derived-edge anchor lookup, an unrelated alt-corpus fixture, and
  a `ReadinessTests` case (readiness, not order). `paper_graph.derive_order`'s
  own `_sort_key` uses `record.position` as the min-heap tie-break for every
  block, including one with no `after` edges at all — so `position`
  measurably does influence back matter's placement among equally-ready
  blocks, which is exactly the axis this untested scenario existed to pin
  down. Per the skill's own hard rule ("Spec scenario has no passing
  covering test → CRITICAL"), this blocked a clean PASS regardless of
  whether the underlying behavior would turn out correct once tested.

**WARNING**:
- **W1 — The transcription-quote lock is vacuous for a same-file-sourced
  `after` edge, proven by execution.** [RESOLVED by `0422dd1` — see addendum
  above.] `GraphTests.test_every_transcribed_afters_quote_is_a_substring_of_its_named_file`
  read `Path(source["file"]).read_text()` — the WHOLE file, header included
  — and checked `source["quote"]` as a substring. For the
  `introduction.block-3` → `related-work` edge, `source.file` was
  `sections/06-introduction.md`, the SAME file whose own header carries this
  exact `after` entry; the header's JSON always re-serializes `quote`
  verbatim, so the check was tautologically true no matter what the quote
  said. Proven on a throwaway temp copy (never a tracked file): replaced the
  quote with a fabricated sentence ("Purple elephants never write in Related
  Work order at all.") confirmed absent from the file's prose body, re-ran
  the test's own check logic, and it still reported the quote "found" —
  because it matched the header's own JSON, not the prose. The real shipped
  quote WAS genuinely present in the prose too
  (`sections/06-introduction.md:244`), so shipped data was honest — this was
  not a live data-corruption defect — but the lock could not catch a future
  fabrication on this specific edge, contradicting tasks.md 3.2's own claim
  ("an invented edge fails this test"). The `abstract`→`conclusions` edge
  was NOT self-sourced (its `source.file` is `conclusions`' file, different
  from `abstract`'s own) so that half of the lock was genuinely non-vacuous.
- **W2 — `npm run typecheck` fails in this environment**: `tsc: command not
  found` (`devDependencies` not installed). Pre-existing environment gap,
  unrelated to any file this change touches; not part of the orchestrator-
  declared test runner for this change. **Still open — out of this
  addendum's scope per instruction.**

**SUGGESTION**:
- **S1 — Task-count bookkeeping mismatch.** Engram
  `sdd/the-contract-is-data-not-code/apply-progress` (#1637) and `.../tasks`
  (#1609) both state "26/26 tasks" complete; `tasks.md` itself contains 23
  numbered checkbox items (1.1-4.6), all `[x]`. Cosmetic — `tasks.md` itself
  makes no such claim. **Still open — out of this addendum's scope per
  instruction.**

### Original Verdict (superseded — see addendum at top)
FAIL — one CRITICAL (untested spec scenario, `writing-readiness` / Derived
Writing Order) blocked a clean pass; all implemented code and every other
scenario's covering test passed by direct execution, and no CRITICAL finding
named a functional defect in shipped behavior.

**This verdict is superseded by the Re-verification Addendum above, dated
2026-09-11, following corrective commit `0422dd1`: both C1 and W1 are now
RESOLVED (`blockers: 0`, `critical_findings: 0`). The envelope's own
`verdict:` field still reads `fail` only because `gentle-ai
sdd-verify-validate` refuses a passing verdict while `build_exit_code` is
non-zero (W2, pre-existing, out of this addendum's scope) — see "Why the
machine-readable `verdict:` field above still reads `fail`" in the
addendum. Functionally: archivable. Remaining open items (W2, S1) are
non-blocking, pre-existing, and cosmetic respectively.**
