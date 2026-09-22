# Apply Progress: The Block Asserts Only What Its Section Carries

**Status**: 47/47 tasks complete. All four work units (WU1-WU4) landed as
four chained commits on branch `the-block-asserts-only-what-its-section-carries`,
off `main` at `0b8492e`. Both full suites green. Ready for `sdd-verify`.

## Task 0.1 gate — re-measured, not inherited

The orchestrator reported the sibling `the-redactor-receives-the-section-it-must-transpose`
as merged into `main`. Re-verified directly on disk before touching any
file: `paper_bindings.py:45-55` — `RedactorInput` carries five fields,
`source_sections: tuple = ()` appended fifth. `paper_cli.py:2147-2150` —
`assemble_packet(sections_dir, guidance_dir, section, block_id, *,
corpus=None, paper_dir=None)`. Gate satisfied; proceeded.

## TDD Cycle Evidence (Strict TDD Mode)

| Task(s) | RED | GREEN | REFACTOR |
|---|---|---|---|
| 0.2/0.3 | AST test: bare `ast.Expr` call site found (fail) | `bindings = _stage_evidence_audit(...)` assigns; AST test passes | n/a |
| 0.4 | `KeyError: grounding_account` on signature inspection | keyword-only `grounding_account: dict \| None = None` added | n/a |
| 0.5/0.6 | `ModuleNotFoundError: paper_grounding` (whole-module RED) | `subjects_for` implemented; 5 tests green | n/a |
| 0.7/0.8 | `KeyError: sourceGrounding` | interim `{"status":"unmeasured","subjects":N}` wired, guarded on `contract.source_sections and contract.mode == MODE_TRANSPOSITION` | condition text reordered vs. the verbatim-check's own anchor to keep both mutation-test anchors unique (see Deviations) |
| 0.9 | same as 0.7/0.8 | same | n/a |
| 1.1 | `AttributeError: reconcile_support` | burden-of-proof test green once `reconcile_support` lands | n/a |
| 1.2-1.11 | `AttributeError: reconcile_support`/`source_grounding_report` | full both-direction reconciliation + report shape implemented; 15 tests green | n/a |
| 1.12/1.14 | `AssertionError: Refused not raised` (full guard not yet wired) | guard wired after `check_source_section_verbatim`, before `substitute` | n/a |
| 1.13 | fact-scoped filtering not yet in place | `relevant_entries` filters account entries by `entry["fact"] in subject_facts` before either reconciliation direction runs | n/a |
| 2.8 | `AttributeError: 'Namespace' object has no attribute 'grounding'` (via incidental `MODE_ABSENT` before wiring) | `--grounding` argparse + `cmd_write` resolution/threading added | 8 existing test fixtures updated to carry `grounding=None` |
| 3.1-3.4 | n/a (mutation proofs target already-green code) | all 4 mutants (+1 combined anchor-uniqueness test) confirmed red-under-mutation | n/a |

## Work Unit Evidence

| WU | Focused test command | Result | Runtime harness | Rollback boundary |
|---|---|---|---|---|
| WU1 | `.venv/bin/python -m unittest tests.test_paper_writing` | 603/603 OK | N/A — no real `document`-rooted binding on disk; every fixture is `bind`-recorded, invented names | `git revert` its commit (`47431b8`); deletes `paper_grounding.py`, reverts `paper_write.py:159` and the kwarg default |
| WU2 | `.venv/bin/python -m unittest tests.test_paper_writing` | 621/626 OK, 5 discrepancies all pre-registered as expected (unclassified codes + moved roster count, both resolved by WU3) | N/A, same boundary | `git revert` its commit (`287638a`); `sourceGrounding` is a new key, no prior format touched |
| WU3 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_agents` | 626/626 + 16/16 OK (one pre-existing pinned-count discrepancy, expected until WU4) | N/A — agent never invoked by code (D9); CLI wiring test uses `unittest.mock.patch("paper_write.write_block")`, never a live call | `git revert` its commit (`6f56df4`); import row + classification + roster rows removed together |
| WU4 | Full suite, both runners | `npm test`: 646/646. `unittest discover -s tests -p "test_*.py"`: 4559/4559, skipped=3, 0 failures (the previously-disclosed `ForgeVocabularyDerivedGuardTests` failure did not reproduce — full green) | Mutation harness runs against a temp-tree copy via `_run_against_mutant`, never a real invocation | Test-only; reverting drops the mutation/sweep tests and the updated roster literal |

## Deviation from the WU rollback narrative — disclosed

`ModuleCompletenessTests.test_every_script_on_disk_is_imported_at_module_level_by_paper_cli`
requires every `scripts/*.py` file to be imported at module level by
`paper_cli.py` the instant it exists on disk — stricter than tasks.md's own
WU1 rollback description ("`paper_grounding.py` is deleted" implying the
import row is a later, separately revertible WU3 commit). Task 2.5's import
row was therefore added in WU1's own commit (not WU3's), the moment
`paper_grounding.py` was created, to keep every intermediate checkpoint
green. Task 2.5 is still marked complete at its originally-planned position
in Phase 2 tracking; the row itself landed one commit earlier than tasks.md
narrates. This is the only deviation from the written task order.

## Measured, not forecast

- Refusal roster: **165** (was 161; +4 for `GROUNDING_ACCOUNT_ABSENT`,
  `GROUNDING_SENTENCE_UNKNOWN`, `GROUNDING_VERDICT_MISSING`,
  `SECTION_UNSUPPORTED_CLAIM`), matching the design's own expectation.
  Measured live via `reachable_paper_refusal_codes()` after all engine code
  from Phases 0-2 landed, per task 3.7's own discipline.
- Engine lines under `.claude/skills/paper-writing/scripts/`: **235
  additions** (`paper_cli.py` +33, `paper_grounding.py` +172,
  `paper_write.py` +30 net of 3 deletions) — well under the owner's 1600
  ceiling.
- `.claude/skills/paper-writing/SKILL.md`: +59 lines (docs).
  `.claude/agents/section-grounding-auditor.md`: +123 lines (new agent,
  under `.claude/agents/`, not `.claude/skills/`).
- Whole-change diff: 7 files changed, 1428 insertions(+), 65 deletions(-).
- Zero files deleted (`git diff main --diff-filter=D` empty).
  `paper_leak.py` byte-identical to `main` (D5).

## D2's falsifier — live, unexecuted obligation (task 3.10)

Recorded verbatim in `tasks.md`'s own new closing section and in
`SKILL.md`'s "transposition-grounding guard" section: over ten or more real
`write` runs against genuine document-rooted bindings, if any block reaches
`written` with `downgraded > 0`, or with `subjects > 0` and `decided == 0`,
the no-ratio-threshold ruling is wrong. Unexecutable today — no real
document-rooted binding exists on disk anywhere in this repository. Not
waived; dated and open.

## Generality sweeps (0.10, 1.15, 2.9-adjacent, 3.6)

No block id, section title, document filename, lineage literal, or paper id
found in `paper_grounding.py`, the `paper_write.py`/`paper_cli.py` diffs,
`SKILL.md`'s new section, or `section-grounding-auditor.md` — checked by
direct `rg` sweep at every phase boundary. `ForgeVocabularyDerivedGuardTests`
(rule B, `FORGE_LEXICON`) passes clean (22/22), no new leak.

## Files changed

| File | Action |
|---|---|
| `.claude/skills/paper-writing/scripts/paper_grounding.py` | Created |
| `.claude/skills/paper-writing/scripts/paper_write.py` | Modified |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modified |
| `.claude/agents/section-grounding-auditor.md` | Created |
| `.claude/skills/paper-writing/SKILL.md` | Modified |
| `tests/test_paper_writing.py` | Modified |
| `openspec/changes/the-block-asserts-only-what-its-section-carries/tasks.md` | Modified (47/47 ticked + falsifier tracking) |

## Commits (chained, on this branch)

1. `47431b8` — WU1: ordering gate, thread bindings, subject intersection, interim envelope
2. `287638a` — WU2: reconciliation, four refusals, report shape, full wiring
3. `6f56df4` — WU3: agent file, `--grounding` CLI, classification, SKILL.md
4. `b5c0a3d` — WU4: mutation proofs, generality sweep, roster re-measure, both suites
