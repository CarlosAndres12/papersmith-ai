```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:48d91e52bd3ffda598a4f916e67eb7dc74144ca920e849339938e5329dbeb754
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 2/2
scenarios: 6/6
test_command: .venv/bin/python -m unittest discover -s tests -p "test_*.py"
test_exit_code: 0
test_output_hash: sha256:261d9ffbbccd6dc8aaba961f71ce1d1419f6ce5d1fa104e0cc163af826cb219a
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:1647b36997492b53714f51f6d31c7301cd9018e101823bf22f00fa6fc49fa28b
```

# Verification Report: the-methods-section-produces-the-contributions

**Change**: `the-methods-section-produces-the-contributions`
**Mode**: Full artifacts (proposal, delta spec, design, tasks) + Strict TDD active (data-only header/prose change; no Python engine changes, per design.md)
**Verifier**: sdd-verify, independent re-measurement (nothing inherited from apply's report without re-running it)
**Tree**: `main` @ `6f44fa2` (clean before and after verification; byte-identical hashes of every touched file confirmed pre/post both suite runs)

## Verdict: PASS WITH WARNINGS

**0 CRITICAL / 2 WARNING / 3 SUGGESTION**

## Task Completeness

All 27/27 tasks in `tasks.md` are marked `[x]` across Phases 1-6. Independently spot-checked against the actual `sections/*.md` bytes (not just the checkbox), see Correctness section below — every checked task's claimed edit is physically present in the shipped corpus.

## Test Evidence (both suites, run in the foreground, redirected to file, verdict lines only — full logs available at the paths below)

### Python suite

```
$ PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p "test_*.py"
----------------------------------------------------------------------
Ran 4584 tests in 829.494s

OK (skipped=3)
```
Exit code: 0. Matches apply's claim exactly (4584 tests, OK, skipped=3; pre-change baseline was 4577/OK/skipped=3, so +7 new tests, 0 regressions — matches the 7 new test methods added in Phase 4: 3 mutation, 2 D2-falsifier, 1 property, 1 integration).

### JavaScript suite (this repo has two suites; both were run, per MANTENIMIENTO history of one-suite blind spots)

```
$ npm test
ℹ tests 646
ℹ suites 0
ℹ pass 646
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
```
Exit code: 0. Matches apply's claim exactly (646/646).

### Integrity of the evidence

- `shasum` of all 10 `sections/*.md`, `SKILL.md`, `tests/test_paper_writing.py`, `tests/test_paper_contract.py`, and `openspec/specs/fact-production/spec.md` taken before launching either suite and re-checked after both completed: **all 14 files byte-identical** (`shasum -c` reported `OK` for every file). The suite that ran is the suite that was read.
- Both suites executed in the foreground as separate processes; exit codes captured directly, not inferred from log tail text.
- JSON lines printed by the Python suite after the `OK (skipped=3)` line are refusal-envelope stdout from unrelated remote-execution fixtures in the same repo (`test_the_declared_accelerator_...`-style tests) — normal output, not suite output, and appear *after* the authoritative `Ran N / OK` lines, never instead of them.

## Independent Re-Measurement (`phases`, `order`)

Ran directly, not copied from apply's report:

```
$ PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py phases
```
Counted blocks per wave from the raw JSON: wave 1=21, wave 2=3, wave 3=6, wave 4=10, wave 5=2, wave 6=2, wave 7=1, wave 8=1, wave 9=1. **Total 47 blocks, 9 waves, shape 21/3/6/10/2/2/1/1/1 — confirms apply's claim exactly**, and confirms `SKILL.md:225-227`'s dated claim ("measured directly ... dated 2026-09-21") reads back true against a fresh run today.

```
$ PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py order
```
`danglingEdges: []`, 47/47 blocks ordered — acyclic, confirmed.

Direct Python check against the live module (not the CLI wrapper):
```python
producers_by_fact(corpus)["contributions"] == ("materials-and-methods.mm-proposal",)  # True
order.index("materials-and-methods.mm-proposal") < order.index("introduction.block-4b")  # True (5 < 7)
```

## Obligation-by-Obligation Verification

1. **All 8 chain rows + 6 retargeted `after` edges, none left on `block-4b` for `contributions`.** Confirmed by direct `rg` over all 8 touched files: `introduction.block-4b`'s own header (lines 129-163) now `requires_facts: contributions` + `after: mm-proposal`; `mm-proposal`'s header (lines 58-104) carries `produces_facts: contributions`. All 7 consumer `### Internal chain` rows (block-2, es-assessment, rd-contribution-blocks, rw-synthesis-artefact, concl-block-1, slot-2, title) plus block-4b's own new 8th row all read `materials-and-methods.mm-proposal` as the dependency. No leftover row or `after` edge targets `introduction.block-4b` for `contributions`. **Confirmed, no issue.**

2. **No `sections/*.md` quoted byte span changed (`SPAN_NOT_IN_SOURCE` never fires).** `_verify_after_transcription`/`_verify_requirement_transcription` run unconditionally inside `assemble_corpus` (`paper_graph.py:366-367`). Both direct `phases`/`order` CLI runs against the real corpus above completed with `"status": "ok"` and no exception — if any quote's byte span had drifted, these two commands would have raised `SPAN_NOT_IN_SOURCE` before returning. **Confirmed structurally, no issue.**

3. **`sections/` vocabulary leakage grep (operator's hard constraint).** Grepped all 10 shipped `sections/*.md` files against `tests/forge_vocabulary.py`'s `FORGE_VOCABULARY_FLOOR` (`kaggle`, `t4`, `ceiling`, `ramp`, `transfer`, `latent`, `creda`, `milcreda`, word-boundary, plural-tolerant): **one hit** — `sections/09-title-and-keywords.md:91`, the word "transfer" in "*the work does not transfer beyond it*". Traced via `git show <pre-change-commit>:sections/09-title-and-keywords.md` — **this hit already existed before this change** (introduced in commit `630f0d4`, 2026-09-08, six weeks before this change). It is ordinary English usage ("does not generalize beyond it"), not a real paper's contribution/dataset/method/metric name, and the diff for `09-title-and-keywords.md` in this change's own commit (`6f44fa2`) touches only line 154 (the chain-row retarget) — nowhere near line 91. **This change introduces zero new vocabulary hits, but the task brief's premise that the baseline held zero hits is factually incorrect — flagged as WARNING, not CRITICAL, since it predates and is untouched by this change.**

4. **D2 falsifier proof method (task 4.4).** Apply is correct that `paper/main.tex` carries `mm-proposal` as an empty block today (verified: no `render` output exists to test against). The tests (`ComponentsCheckSelfReferenceFalsifierTests`) call `paper_cli._resolve_expected_components` and `paper_obligation.check_components` directly — but these are the **exact same two calls** the real `render` pipeline makes (`paper_cli.py:2662-2663`, confirmed by direct read), against a synthetic rendered body built with the same `_marker_pair`/`_write_fixture` helpers other tests in this suite use to simulate real `main.tex` output. This is adequate proof of the mechanism (mutating one roster item flips `check_components` from silent to `COMPONENT_MISMATCH`, and the resolution is keyed off current producer identity via `producers_by_fact`, so it applies identically whichever consumer calls it). **Judgment: adequate, not a gap** — it is a justified unit-level substitute for an end-to-end run that literally cannot exist yet, and it is honestly disclosed as such in both `design.md` and the test's own docstring. Flagged only as a SUGGESTION to re-run through the real `render` CLI once `paper/main.tex:mm-proposal` carries real content.

5. **4 pre-existing tests + golden digest table.** Read the actual diff for all 4 corrected tests (`InputPartitionTests.test_introduction_block_4_is_two_blocks_not_one_composite`, `test_the_internal_chain_of_the_introduction_is_acyclic`, `InternalChainTests.test_the_introductions_three_chain_rows_become_three_after_edges`, `OrderCliFrontDoorTests.test_cmd_order_returns_...`). In every case the diff **adds** assertions (new edge pairs, `len(rows)` raised from 4→5, new `assertLess` ordering checks) — no assertion was deleted or loosened, and every pre-existing DAG/no-reverse-edge invariant survives unchanged. This is a genuine re-measurement, not a weakened guard. Independently recomputed SHA-256 of the post-header body for `01`, `06`, `09` and got an exact byte-for-byte match against the new `PRE_MIGRATION_BODY_DIGESTS` literals in the diff. **Confirmed genuine, no issue.**

## Spec Compliance Matrix (delta spec, `openspec/changes/.../specs/fact-production/spec.md` — 2 requirements, 6 scenarios)

| Requirement | Scenario | Status | Covering evidence |
|---|---|---|---|
| MODIFIED: A Produced Fact's Value Is Its Producer's Own Rendered Text | A consumer reads the producer's own words | PASS | `ComponentsCheckSelfReferenceFalsifierTests` (resolves via current producer identity, fact-keyed not consumer-keyed) + `ProducerMoveIntegrationTests` (`mm-proposal` sole producer) |
| ADDED: Producer Reassignment Is Read From One Shared Scan | The reassigned producer is exclusive and unrequired-by-itself | PASS | `ProducerMoveIntegrationTests` (real corpus assembles clean, no `FACT_SELF_REQUIRED`) |
| ADDED: (same) | Reviving the old producer duplicates it | PASS | `test_reviving_block_4b_as_a_second_producer_refuses_duplicate` (4.3, RED confirmed against mutated copy, GREEN against real corpus) |
| ADDED: (same) | Deleting the sole producer leaves the fact unresolved | PASS | Pre-existing generic `FactTotalityTests.test_a_required_fact_with_no_producer_anywhere_refuses` (`FACT_PRODUCER_ABSENT`, synthetic fixture; the requirement's own text says guards are shared/generic, not restated per fact, so this is the correct evidence class) |
| ADDED: (same) | A consumer's stale row/edge is checked against the current producer | PASS | `test_deleting_block_4b_new_row_refuses_producer_chain_absent` (4.1) + `test_deleting_a_retargeted_after_edge_refuses_chain_row_unbacked` (4.2), both RED-then-GREEN |
| ADDED: (same) | `contributions` stays produced, not declarable | PASS | Pre-existing generic `FACT_ROUTE_AMBIGUOUS` tests (`tasks.md` unit 0.4) + real-corpus `assemble_corpus` succeeding with `mm-proposal`'s `produces_facts: contributions` entry present |

All 6 scenarios have a currently-green, runtime-executed covering test. 3 of 6 rely on pre-existing generic guard tests rather than change-specific new tests — correct per the ADDED requirement's own architectural point (guards must not be restated per fact), noted for transparency rather than as a gap.

## Design Coherence

- D2 (Components Check self-reference): design.md's forced choice (roster mandate, `components_from` stays on both blocks, intra-block vs cross-section reading stated in prose) is implemented exactly as decided. Verified the "intra-block drift" prose exists in `01-materials-and-methods.md` and the "referent moved" prose exists in `05-related-work.md`.
- D3/D4/D5 (retarget not duplicate, reuse verbatim quotes, no wave-count test) all verified true by direct inspection above.

## Issues

### CRITICAL (0)

None found.

### WARNING (2)

1. **Vocabulary-leak baseline claim is inaccurate.** The task brief's premise "before the change there were ZERO [hits]" does not hold: `sections/09-title-and-keywords.md:91` ("transfer") predates this change by six weeks. This change introduces no new hits, but the record should say "0 new, 1 pre-existing and unrelated," not "0."
2. **`size:exception` authorization is self-asserted only in the apply commit message** ("size:exception autorizada por el dueño del repositorio: 472 líneas contra 400"). 472 changed lines exceeds the session's declared 400-line review budget. I have no artifact independent of the commit message text itself proving the repository owner actually granted this exception in conversation. Recommend the orchestrator confirm this was a real, explicit grant before treating the budget overage as resolved.

### SUGGESTION (3)

1. `design.md`'s "Open Questions" section still lists "Wave shape is unmeasured in this phase" as open, even though `SKILL.md` now carries the dated, measured answer (9 waves, confirmed above) — stale bookkeeping in `design.md` itself, not a functional defect (the consumed doc, `SKILL.md`, is correct).
2. `proposal.md`'s "Success Criteria" checklist (5 items) is still entirely unchecked (`- [ ]`) despite every criterion being independently confirmed true in this report (corpus assembles with sole producer; all 7 consumers carry row+edge; `phases` re-measured and quoted; D2 decided and recorded; removing any new row reds under mutation). Cosmetic only.
3. The D2 falsifier tests (obligation 4 above) are a justified but real substitute for an end-to-end `render` CLI run; re-run through the real CLI once `paper/main.tex:mm-proposal` carries actual rendered content, per design.md's own noted limitation.

## Canonical Spec Merge (informational, not a defect)

`openspec/specs/fact-production/spec.md` (canonical, 181 lines) still reads the **pre-change** text at its own lines 164-181 ("...it is `introduction.block-4b`'s own rendered content..."), and does not yet carry the ADDED "Producer Reassignment..." requirement at all. Confirmed via `git show 6f44fa2 --stat`: this commit did not touch the canonical spec file. This is the expected OpenSpec lifecycle (delta lives under `openspec/changes/{change}/specs/` until archive merges it into canonical) — flagged here only so `sdd-archive` knows the merge is still pending, not as a verify-phase defect.

## Final Verdict

**PASS WITH WARNINGS** — 0 CRITICAL, 2 WARNING, 3 SUGGESTION. All 27 tasks independently confirmed complete and physically present in the shipped corpus; both suites reproduce apply's exact reported numbers under a byte-identical tree; all 6 delta-spec scenarios have currently-green covering tests; no weakened guards found in the 4 corrected pre-existing tests. The two WARNINGs are process/record-accuracy items for the orchestrator, not functional defects, and do not block archive.
