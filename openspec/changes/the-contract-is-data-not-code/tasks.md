# Tasks: The Contract Is Data, Not Code

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1600-2000 (headers ~180, paper_vocabulary.py ~50, paper_contract.py ~280, paper_graph.py ~280, paper_readiness.py ~120, paper_cli.py append ~120, tests/test_paper_contract.py ~650-900) |
| Review budget (project override) | 1400 lines (`review_budget_lines`) |
| 1400-line budget risk | High |
| Chained work units recommended | Yes |
| Suggested split | Unit 1 vocabulary/schema → Unit 2 header insertion → Unit 3 graph/readiness/order → Unit 4 CLI wiring + mutations + roster |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main — sequential commits on `paper-writing`, no GitHub PRs; operator merges to main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High (also High against this project's 1400-line override)

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| 1 | Vocabulary + header schema/refusals, parsed from fixtures only (no shipped files touched) | `.venv/bin/python -m unittest tests.test_paper_contract.SchemaTests tests.test_paper_contract.VocabularyTests -v` | N/A — parses fixtures in `TemporaryDirectory`, no shipped file, no service | `git rm .claude/skills/paper-writing/scripts/paper_vocabulary.py .claude/skills/paper-writing/scripts/paper_contract.py`; nothing else moves |
| 2 | Insert headers into the ten shipped `sections/*.md`, byte-clean, digest-guarded | `.venv/bin/python -m unittest tests.test_paper_contract.HeaderInsertionTests -v` | N/A — filesystem-only, one-shot idempotent write | `git checkout -- sections/` restores headerless prose; Unit 1 stands alone |
| 3 | Block graph, edges (2 literal + 1 position-derived), Kahn sort, cycle report, readiness | `.venv/bin/python -m unittest tests.test_paper_contract.GraphTests tests.test_paper_contract.ReadinessTests tests.test_paper_contract.OrderTests -v` | N/A — pure functions over parsed fixtures | `git rm .claude/skills/paper-writing/scripts/paper_graph.py .claude/skills/paper-writing/scripts/paper_readiness.py`; Units 1-2 stand alone |
| 4 | `paper_cli.py` registration, refusal roster, both mutations, vocabulary guard, SKILL.md append | `.venv/bin/python -m unittest discover -s tests -p 'test_paper_contract*.py'` | N/A — mutation harness runs its own subprocess against a temp copy, no live service | Revert the appended registration entries in `paper_cli.py` and the appended `SKILL.md` section; Units 1-3 stand alone |

Depends on `only-the-block-changes` landing first — `paper_cli.py` and `.claude/skills/paper-writing/` must already exist. Unit 4 appends to that registration list; it does not create the file.

## Phase 1: Vocabulary and Schema (`section-contract` spec)

- [x] 1.1 RED (`tests/test_paper_contract.py::VocabularyTests`): listed fact/declaration/citations-regime parse; `discussion` fact, `reviewer-name` declaration, `maybe` citations each refuse `UNKNOWN_FACT`/`UNKNOWN_DECLARATION`/`UNKNOWN_CITATIONS_REGIME`, derived from one declaration per vocabulary (never hand-listed at the call site)
- [x] 1.2 GREEN: `.claude/skills/paper-writing/scripts/paper_vocabulary.py` — three closed tuples, no I/O, no state
- [x] 1.3 RED (`SchemaTests`): valid header parses; header missing `position` refuses `MALFORMED_HEADER` naming `position`; malformed JSON returns nothing (not merely raises); `--sections` outside the repository refuses `SECTIONS_OUTSIDE_REPOSITORY`
- [x] 1.4 GREEN: `.claude/skills/paper-writing/scripts/paper_contract.py` — front-matter grammar, `json.loads` over the `---` fence, schema validation, root resolution reusing `paper_scaffold.FORGE_ROOT` (`parents[4]` from a script at `.claude/skills/<skill>/scripts/`) rather than a second `parents[3]` constant — measured against the sibling's own convention at apply time; design.md's literal `parents[3]` would have resolved one level short of the repository root

## Phase 2: Header Insertion Into the Ten Shipped Contracts

- [x] 2.1 Author the ten JSON headers (`section`, `position`, optional `after`, `blocks`) per contract's own prose — `title-and-keywords`=1, `abstract`=2, `introduction`=3, `related-work`=4, `materials-and-methods`=5, `experimental-setup`=6, `results-and-discussion`=7, `limitations`=8, `conclusions`=9, `back-matter`=10 (filename order ≠ this order, by design)
- [x] 2.2 RED (`HeaderInsertionTests`): pre-digest each of the ten files via `git show HEAD:sections/<file>` (captured once, at 578d117, and held as `PRE_MIGRATION_BODY_DIGESTS` literal constants rather than re-derived from `HEAD` on every later run — `HEAD` itself carries the header after this change lands, so a dynamic re-read would only prove a file equals itself); assert `HEADER_PRESENT` on a second run; assert a forced body mutation restores original bytes and refuses `BODY_MUTATED`
- [x] 2.3 GREEN: `install_header` in `paper_contract.py` — temp-in-same-dir + `os.replace`, re-read, assert prefix match and `sha256(post[len(header):]) == pre`; run it against the ten files. Hardened during apply to call `parse_header(header)` BEFORE any read/write, after an incident: a test exercising `install_header` with a deliberately malformed header against a still-headerless real shipped file (before the real migration had run) wrote that malformed header to disk, because the original implementation validated nothing before writing. Fixed at the source (validate-before-write) and the file restored via `git checkout HEAD --` (safe here: a tracked file with no other pending edits, restoring to the exact last-committed content); the triggering test was rewritten to operate on a copy, never the real file
- [x] 2.4 Verify: post-digest of each file's body equals its pre-digest; all ten match, zero prose bytes changed (confirmed both by the real migration run's own assertion and by `HeaderInsertionTests::test_the_ten_shipped_contracts_carry_headers_matching_the_pre_migration_body_digests`)

## Phase 3: Block Graph, Readiness, Order

- [ ] 3.1 RED (`GraphTests`): flat id namespace — section id colliding with a block id refuses `ID_COLLISION`; `after` naming a section expands to every block of that section; an `after` target absent from the corpus lands in `danglingEdges`, never refuses
- [ ] 3.2 RED: transcription lock — each literal `after`'s `source.quote` is a whitespace-collapsed substring of `source.file` (may differ from the holder, e.g. abstract-after-conclusions sourced in `07-conclusions.md`); an invented edge fails this test
- [ ] 3.3 RED: exactly two literal cross-section `after` edges (abstract→conclusions, introduction.block-3→related-work), computed by holder-section-vs-target-section, never a hand-list
- [ ] 3.4 RED: `title-and-keywords`'s third ordering constraint is position-derived, not enumerated and not resolved against a `skeleton` fact — the reader computes it as every section whose `position` lies strictly between `title-and-keywords`'s own position and `back-matter`'s position, both looked up by section id, never by filename or a hardcoded integer. 09's "every keyword appears in the body" content half is recorded as a disqualifier/convention, not an `after` input
- [ ] 3.5 GREEN: `.claude/skills/paper-writing/scripts/paper_graph.py` — corpus assembly, both edge kinds above, Kahn sort keyed `(section.position, block_index, block_id)`, min-heap tie-break
- [ ] 3.6 RED: two-block mutual-`after` fixture refuses `ORDER_CYCLE` naming both blocks, via DFS-extracted minimal cycle over the residual subgraph
- [ ] 3.7 RED: determinism (two subprocess runs byte-identical) and rendering-order ≠ filename order (introduction position 3 < related-work position 4, filenames 06 > 05); Related Work precedes introduction block-3 and follows blocks 1/2/4a in the derived writing order
- [ ] 3.8 RED (`ReadinessTests`): facts-satisfied/declarations-missing block reports `blocked` naming only the missing declaration; back matter reports zero missing facts and every declaration missing
- [ ] 3.9 GREEN: `.claude/skills/paper-writing/scripts/paper_readiness.py` — per-block `writable`/`blocked` given satisfied-facts and satisfied-declarations sets

## Phase 4: CLI Wiring, Refusal Roster, Mutations

- [ ] 4.1 Append `contract`/`readiness`/`order` verbs to the existing `.claude/skills/paper-writing/scripts/paper_cli.py` registration list (append-only; do not touch `only-the-block-changes`'s entries)
- [ ] 4.2 RED+GREEN: roster derived from source (shape of `reachable_refusal_codes`) — every code above classified invocation-defect vs work-state, every work-state code publishes a `resolve`
- [ ] 4.3 Mutation A (executed): eleventh-contract fixture — derive the used-shape set from the ten shipped headers on both axes (`frozenset(requires_facts)` per block; graph shape: section+block `after` co-occurrence and any block targeting an earlier-position section); assert the fixture's tuple is absent from both; run it through the CLI as a subprocess against a temp `sections/`, digest-asserting the reader's own source is unchanged before and after
- [ ] 4.4 Mutation B (executed): subprocess against a fixture declaring `requires_facts: [discussion]`; assert exit 2 and `code == "UNKNOWN_FACT"`, readiness never computed for that contract
- [ ] 4.5 Run `tests/forge_vocabulary.py` against every new file under `.claude/skills/paper-writing/`; confirm no target-word leakage and that no new doctrine quotes 09's `transfer`-bearing sentence (`FORGE_VOCABULARY_FLOOR`)
- [ ] 4.6 Append a short section to `.claude/skills/paper-writing/SKILL.md` documenting `contract`/`readiness`/`order`; confirm `tests/test_suite_collects.py` picks up the two new modules

## Notes / Deviations to Flag at Apply

- Implements the orchestrator's settled position-derived resolution for 09's third edge, not the spec's literal "resolve against the skeleton fact" wording and not design's rejected/then-superseded "enumerate seven targets" option. `sdd-apply` should record this as a spec annotation, not re-open the decision.
