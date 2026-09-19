# Tasks: A Fact Is Declared Or It Is Produced

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1150–1300 total, split across 4 PRs |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 0 (reconciliation) → PR 1 (grammar) → PR 2 (corpus, atomic) → PR 3 (consumers) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — ask the operator |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

Unit 2 is design-declared atomic (grammar/totality/ordering/corpus land together) and cannot be split further; if it alone exceeds 400 lines, request `size:exception` for PR 2 specifically, independent of whichever chain strategy the operator picks for PR 1/PR 3 (stacked-to-main or feature-branch-chain).

### Suggested Work Units

| # | Unit | Touches | New refusals | Est. lines | Budget risk (vs 1200) | Depends on | Status |
|---|------|---------|---------------|-----------|------------------------|-----------|--------|
| 0 | Reconciliation | `specs/fact-production/spec.md`, `design.md` | none (naming/wording only) | ~50 | Low | — | [x] |
| 1 | Grammar, parser, additive refusals | `paper_contract.py`, `paper_graph.py`, `tests/test_paper_contract.py`, `tests/test_paper_writing.py` | `FACT_SELF_REQUIRED`, duplicate-producer code, route-ambiguity code | ~350 | Low | 0 | [ ] |
| 2 | Corpus edits + totality + ordering (atomic) | `sections/*.md` (05, 06, 04 + edges into 02/03/07), `paper_graph.py`, `tests/test_paper_writing.py` | `FACT_PRODUCER_ABSENT`, `PRODUCER_CHAIN_ABSENT` | ~450 | Medium | 1 | [ ] |
| 3 | Consumers: readiness, declare, cli, verify, coupling evidence | `paper_readiness.py`, `paper_declarations.py`, `paper_cli.py`, `paper_verify.py`, `paper_coupling_evidence.py`, `tests/test_paper_writing.py`, `tests/test_paper_decisions.py`, `tests/test_paper_evidence.py` | `PRODUCED_FACT_UNDECLARABLE` | ~350 | Low | 2 | [ ] |

Focused test / runtime harness / rollback per PR:
- **PR 0**: test = re-run `RefusalRosterTests.test_the_derivation_finds_the_measured_count`; harness = N/A (doc-only); rollback = revert two doc edits.
- **PR 1**: test = `python3.12 -m unittest tests.test_paper_contract tests.test_paper_writing`; harness = N/A reason: additive, corpus carries zero `produces_facts` entries yet; rollback = revert `paper_contract.py`/`paper_graph.py` diffs, no paper affected.
- **PR 2**: test = same suite against the edited shipped corpus; harness = assemble the real `sections/*.md` corpus and run `derive_order`/`derive_waves`; rollback = revert corpus edits + graph totality/reachability code together (atomic — cannot partially revert).
- **PR 3**: test = full paper suite + `test_paper_decisions.py`/`test_paper_evidence.py`; harness = `paper_cli.py readiness --paper <real paper_dir>` after opening `rw-closing`, confirm `gap`-gated blocks flip `writable`; rollback = revert the five consumer-module diffs independently of the corpus.

## Unit 0 — Reconciliation (PR 0)

- [x] 0.1 Measure the baseline roster: `python3.12 -m unittest tests.test_paper_writing.RefusalRosterTests.test_the_derivation_finds_the_measured_count` (expect 127); record it. **Measured: 127 (OK, `.venv/bin/python`, 1 test).**
- [x] 0.2 Amend `specs/fact-production/spec.md`'s "Exactly One Producer Per Fact": a fact may resolve to more than one block producer only when an existing coupling-verification check names that exact pair (e.g. Coupling 3 / `gap`); every other duplicate still refuses. Add the two-legal-producers scenario for `gap`.
- [x] 0.3 Amend `design.md` Decision F and its refusal table for the same carve-out; close the "operator confirmation" open question.
- [x] 0.4 Finalize the six subject-first names against 0.1's roster (no collisions): keep `FACT_SELF_REQUIRED`, `FACT_PRODUCER_ABSENT`, `PRODUCER_CHAIN_ABSENT`, `PRODUCED_FACT_UNDECLARABLE` verbatim; redefine `FACT_PRODUCER_DUPLICATE` to fire only on an *uncorroborated* duplicate; name condition #4 (a `produces_facts` entry naming a declarable fact) — candidate `FACT_ROUTE_AMBIGUOUS`. **Confirmed no collisions with the measured 127-code roster (`rg` against `paper_cli.REFUSAL_CLASSIFICATION`); `FACT_ROUTE_AMBIGUOUS` finalized.**

## Unit 1 — Grammar, parser, additive refusals (PR 1)

- [ ] 1.1 Add `produces_facts` to `paper_contract.py`'s `_TOP_LEVEL_OPTIONAL`/`_BLOCK_OPTIONAL`, reusing `_normalize_requirement_entry`. Test in `tests/test_paper_contract.py`: valid entry parses; missing `value`/`source` refuses `MALFORMED_HEADER`; unknown fact refuses `UNKNOWN_FACT`.
- [ ] 1.2 Add `BlockRecord.produces_facts: tuple = ()` (and the section-level equivalent on `ContractHeader`) in `paper_graph.py`, defaulted so every existing construction site stays green.
- [ ] 1.3 Widen `paper_graph._verify_requirement_transcription`'s tuple to include `produces_facts` at both section and block level. Mutation: fabricate an unbacked quote, confirm `SPAN_NOT_IN_SOURCE` fires (`_run_against_mutant`).
- [ ] 1.4 Implement `FACT_SELF_REQUIRED`: a block whose `produces_facts` and `requires_facts` name the same fact refuses, naming block+fact. Mutation test on a synthetic header; confirm the corrected `rw-closing` shape parses clean.
- [ ] 1.5 Implement route-exclusivity refusal (name per 0.4) for a `produces_facts` entry naming a fact in `paper_declarations.OBSERVABLE_FACTS ∪ STRUCTURAL_FACTS`. Synthetic-header mutation test (e.g. naming `skeleton`).
- [ ] 1.6 Implement the duplicate-producer refusal (name per 0.4): 2+ uncorroborated block producers of one fact refuse; a pair corroborated per 0.2's rule passes. Synthetic-header tests for both branches + mutation.
- [ ] 1.7 Run `python3.12 -m unittest discover tests -p 'test_paper_*.py'`; confirm zero new refusals fire against the unedited shipped corpus (Unit 1 is additive).
- [ ] 1.8 Re-run `RefusalRosterTests`; confirm the four new codes are reachable and classified.

## Unit 2 — Corpus edits, totality, ordering — atomic (PR 2)

- [ ] 2.1 `sections/05-related-work.md`: `rw-closing` gains `produces_facts: [gap]`, drops `requires_facts: [gap]`.
- [ ] 2.2 `sections/06-introduction.md`: `block-3` gains `produces_facts: [gap]` (per operator ruling — not `requires_facts`); `block-2` gains `produces_facts: [problem-statement]`; `block-4b` gains `produces_facts: [contributions]`.
- [ ] 2.3 `sections/04-limitations.md`: `lim-closing` gains `produces_facts: [limitations]`.
- [ ] 2.4 Add the five `after` edges design measured, each with its transcribed quote: `related-work.rw-problem-blocks` after `introduction.block-2`; `experimental-setup.es-assessment` after `introduction.block-3`; `results-and-discussion.rd-contribution-blocks` after `introduction.block-4b`; `conclusions.concl-block-1` after `introduction.block-4b`; `conclusions.concl-block-4` after `limitations.lim-closing`.
- [ ] 2.5 Move each produced-fact consumer row from `### External inputs` to `### Internal chain` in every touched section, sentences verbatim (51 quote anchors are a whole-body substring check).
- [ ] 2.6 Implement `FACT_PRODUCER_ABSENT` totality in `paper_graph.py`: every fact some block requires (excluding `skeleton`) resolves via `FACT_SOURCE_ROOT` or the corroborated producer set from 1.6; else refuse naming the fact. Mutation: delete `rw-closing`'s entry, confirm `FACT_PRODUCER_ABSENT` fires on `gap`.
- [ ] 2.7 Implement `PRODUCER_CHAIN_ABSENT` reachability: cycle-tolerant iterative DFS over `collect_edges`' successors confirming the producer reaches every consumer; refuse naming consumer/fact/producer otherwise. Mutation: delete a row added in 2.5 while its `requires_facts` entry stays; confirm the refusal reads the live row set.
- [ ] 2.8 Synthetic cyclic-corpus test: reachability must still surface `ORDER_CYCLE` at `derive_order`/`derive_waves`, never hang, never misreport here.
- [ ] 2.9 Assemble the real corpus end-to-end; resolve any remaining totality/`PRODUCER_CHAIN_ABSENT` gap the five edges above did not cover (check `rw-synthesis-artefact`'s `contributions` requirement specifically) before closing this unit.
- [ ] 2.10 Re-run `RefusalRosterTests`; confirm both new codes reachable/classified; full paper suite green.

## Unit 3 — Consumers: readiness, declare, cli, verify, coupling evidence (PR 3)

- [ ] 3.1 `paper_readiness.compute_block_readiness` gains `produced_by: dict[fact, tuple[qualified_id]] = None` input and `blocked_on_produced` output naming fact+producer; `produced_by=None` reproduces today's behavior byte for byte. Tests: producer written → `writable`; unwritten → `blocked` naming the producer.
- [ ] 3.2 `paper_declarations.set_fact`/`decline_fact` gain `produced_by: tuple = ()`, refuse `PRODUCED_FACT_UNDECLARABLE` when non-empty, naming fact+producer. Test: declaring `gap` refuses; declaring `formulation` unaffected.
- [ ] 3.3 Enforce the declarations-region carve-out: a produced fact is never read from nor written to that region. Test: `gap` satisfied from `rw-closing`'s written status with no region entry.
- [ ] 3.4 `paper_cli.py`: resolve `produced_by` for `cmd_readiness`/`cmd_phases`/`cmd_declare` from the assembled corpus. Test: `readiness` flips to `writable` once the producer opens, no `--fact` flag repeated.
- [ ] 3.5 Promote `paper_verify._ITEM_RE` to public `item_lines(body) -> list[str]` (allowlist stays `{"re"}`); repoint `paper_cli._resolve_expected_components` (`rw-synthesis-artefact`'s `figure.components_from: "contributions"`) at the producer's rendered body via `item_lines`, reusing `COMPONENTS_FACT_UNRESOLVED`/`COMPONENTS_FACT_NOT_A_LIST` verbatim. Tests: unwritten producer → unresolved; non-list body → not-a-list; written list body → resolves.
- [ ] 3.6 `paper_coupling_evidence.py`: add `Evidence.producers_by_fact`, populated by `gather`; leave `_blocks_by_fact` untouched (no `zip` misalignment in `check_chain`).
- [ ] 3.7 `paper_verify.check_gap`: derive its pair from `producers_by_fact['gap']` (`rw-closing`, `introduction.block-3`), never from consumer-scan. Real-corpus test asserts the published pair excludes `es-assessment`.
- [ ] 3.8 Mutation test: revert `check_gap` to consumer-scan pairing; confirm it fails against the fixture where `es-assessment` also names `gap`.
- [ ] 3.9 Regression: assert `check_chain`/`check_contribution_list`/`check_future_work` still read `_blocks_by_fact` unchanged (link/block alignment).
- [ ] 3.10 Full suite green: `python3.12 -m unittest discover tests -p 'test_paper_*.py'`. Final roster re-measure: bidirectional, count = 0.1's baseline + six new codes.
