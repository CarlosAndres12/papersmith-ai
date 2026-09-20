# Tasks: The Whole Cut Is Argued Before Any Section Is Claimed

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1500 (design's own figure, ~1470, plus rounding) against the owner-raised **1600**-line budget |
| Default 400-line budget risk | High |
| 1600-line budget risk | Medium — ~100 lines of margin, no compression accepted (see design's two named cuts, both rejected) |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: U1 → PR 2: U2 → PR 3: U3+U4 → PR 4: U6 → PR 5: U5, each targeting the previous PR's branch |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — ask the operator which of stacked-to-main / feature-branch-chain to use; design's own "each targeting the previous branch" phrasing reads as feature-branch-chain but was not ruled as a strategy choice |

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High
```

### Suggested Work Units — engine and tests counted separately (owner has ruled three times this split is required)

| Unit | Goal | Engine lines | Test lines | Total | PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|---|---|---|
| GATE-0 | Denylist/leak audit, blocking, before U1 and re-run after U5 | 0 | 0 (runs existing suite) | 0 | — | `.venv/bin/python -m unittest tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests` | N/A — static audit, not a runtime scenario | N/A — no code lands here |
| U1 | `paper_separation.py`: `claimable_sections`, `score_cut` — pure, no CLI, no persistence | ~100 | ~160 | ~260 | PR 1 | `.venv/bin/python -m unittest tests.test_paper_separation` | N/A — pure functions, no CLI invocation yet | `git revert` U1's commit(s); no other module imports it yet |
| U2 | Proposal shape + reader, per-title resolution reuse, `resolve_section_index` extraction, corpus anchoring, `cmd_separate` round-1 path, four codes wired | ~130 | ~200 | ~330 | PR 2 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation` | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py separate --proposal <path>` on the worked-example fixture, round 1 | `git revert` U2's commit(s); `paper_graph.py`'s extraction keeps `_verify_source_section_bindings` behavior unchanged, so reverting drops only `separate` |
| U3 | `separation` record kind, writer, reader, derived numbering, `document_digest`, replay, `SEPARATION_ROUND_ABSENT` | ~105 | ~160 | ~265 | PR 3 (with U4) | `.venv/bin/python -m unittest tests.test_paper_decisions.SeparationRoundTests` | Two independent CLI invocations submitting round 1 then round 2 against the same `paper/` region | `git revert` U3's commit(s); no `bind` path depends on this yet |
| U4 | Concession check, recompute-from-disk, precedence ordering, `SEPARATION_CONCESSION_REGRESSED`, score-is-not-authority mutation | ~90 | ~140 | ~230 | PR 3 (with U3) | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation` | Full negotiation session: round 1 (score 4) → conceded round 2 (score 0) via `separate --proposal <path>` | `git revert` U3+U4's commits together; they share fixture setup and split badly alone |
| U6 | Owner amendment (Decisions I/J): `settled_round_licensing`, `bind_section`'s `BINDING_UNARGUED` guard + `source_base`, `bind --sections`, expiry/scope fixtures for both root kinds, four named mutations, shortcut-closed e2e | ~85 | ~135 | ~220 | PR 4 | `.venv/bin/python -m unittest tests.test_paper_decisions.BindingLicenseTests tests.test_paper_writing.BindCliEndToEndTests` | Settled `separate` → `bind --sections` succeeds; `bind --sections` with no round → `BINDING_UNARGUED` | `git revert` U6's commit(s); every `bind` call site reverts to today's unconditional recording |
| U5 | `SKILL.md` + `references/usage.md` (two-step loop), leak audit re-run, roster re-measured, final e2e session | ~80 (docs) | ~115 | ~195 | PR 5 | Full baseline: `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | `separate` (settled) → `bind --sections` → `write` succeeds, real worked session | `git revert` U5's commit(s); documentation-only plus the roster measurement, no engine change |

**Ordering rationale (each unit independently green):** U1 is inert alone (nothing calls it) but is the cheapest to review in isolation. U2 depends on U1's pure functions and lands the first four `SEPARATION_*` codes and `separate` itself. U3 and U4 share the same round-record fixtures and split badly, so they chain as one PR. **U6 is the unit that makes every existing `bind` invocation with no prior round start refusing** — see Phase 5, task 5.0 — so it lands only after U3 (round records to license against) and U4 (settled-score semantics) exist, and strictly before U5 documents the loop as it will actually behave. U5 lands last because the roster re-measurement and the final leak-audit re-run must see the finished code.

## Concurrency — this change applies FIRST

Do NOT edit `.claude/skills/paper-writing/scripts/paper_leak.py` or
`.claude/skills/paper-writing/scripts/paper_write.py` — the sibling change
`the-tripwire-reaches-the-section-that-feeds-it` applies second and owns them.
Task 2.6 below produces the outline shape (byte offsets, not counts) that sibling
depends on; task 6.6 verifies it stays reachable without duplication. Nothing in
this file deletes a file, and no task edits anything under `sections/`.

## Phase 0: GATE-0 — Vocabulary and Denylist Audit (BLOCKING, before Phase 1)

- [x] 0.1 Run `.venv/bin/python -m unittest tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests` against the current tree, before any new code; confirm zero leaked product names and zero hardcoded product values across `.claude/skills/` and the forge suite, comments and fixtures included. This gate blocks Phase 1 and is re-run at the end of Phase 6 (task 6.4).

## Phase 1: U1 — Pure Core (`paper_separation.py`)

- [x] 1.1 RED: create `tests/test_paper_separation.py` with `claimable_sections` fixtures — title + five siblings (title excluded); three siblings, no title (all claimable); level-3 nested under level-2 under level-1 (generality proof, no engine edit expected); headingless (unmeasured); title-only, empty remainder (unmeasured). Confirm all fail with no implementation present.
- [x] 1.2 Implement `claimable_sections(outline)` in `.claude/skills/paper-writing/scripts/paper_separation.py`: root-span elimination to a fixed point, then the shallowest remaining level, ordered by `byte_start`. No heading-level literal anywhere.
- [x] 1.3 Run 1.1 green.
- [x] 1.4 Generality verification (its own explicit, separately-checkable task): `rg` over `paper_separation.py` for any bare integer heading-level comparison (`level == 1`, `level <= 2`, etc.) used to decide claimability; confirm none exists — the derivation must be structural, never a hardcoded level number.
- [x] 1.5 Mutation: drop root-span elimination (every heading claimable); confirm BOTH the title-claim fixture and the "title is not itself claimable" fixture from 1.1 go red.
- [x] 1.6 RED: `score_cut` fixtures reproducing the worked example exactly — round 1 = 4 (1 overlap + 2 orphans + 1 gap), branch A = 0, branch B = 5; plus a `k=3` overlap fixture (scores 2, distinguishing `k-1` from `min(k,1)`).
- [x] 1.7 Implement `score_cut(claimable, claims_by_block)` in `paper_separation.py` per Decision D; an unanchored assignment's titles clear no orphan and create no overlap or gap.
- [x] 1.8 Run 1.6 green.
- [x] 1.9 Mutation: orphan set forced empty whenever any claim exists; confirm the one-orphan fixture goes red.
- [x] 1.10 Mutation: overlap `k − 1` → `min(k, 1)`; confirm the two-block fixture goes red, and confirm the `k=3` fixture from 1.6 already distinguishes the two forms. **Deviation, reported not silently forced (see report):** mathematically `k - 1 == min(k, 1)` at k=2, so the worked-example two-block fixture cannot and does not go red under this mutation — only the k=3 fixture does. Both outcomes are asserted explicitly and honestly in the suite.
- [x] 1.11 Mutation: gap's interior range `[min, max]` → `[min, min]`; confirm the skip-one fixture goes red.
- [x] 1.12 Run `.venv/bin/python -m unittest tests.test_paper_separation`; confirm green; confirm the module imports no CLI or persistence symbol.

## Phase 2: U2 — Proposal Shape, Resolution, Round-1 Path, Four Codes

- [x] 2.1 RED: shape tests for the proposal file — exact key set `{lineage, assignments}` plus optional `concedes_to_round`; each assignment exactly `{block, fact, sections}`; `sections` a list of unique non-empty strings; a duplicate `(block, fact)` pair; an unknown top-level key; a file whose facts resolve through two source roots.
- [x] 2.2 Implement the proposal reader/validator (`compute_separation`'s shape stage) in `paper_cli.py`; refuse `SEPARATION_REPORT_UNREADABLE` per 2.1, naming the offending key, duplicate, or both roots.
- [x] 2.3 Run 2.1 green.
- [x] 2.4 Mutation: exact key-set check → subset check; confirm the extra-key fixture goes red.
- [x] 2.5 RED: per-title resolution tests reusing `bind`'s existing existence/ambiguity path — a title matching zero headings refuses `SECTION_NOT_IN_SOURCE` BEFORE any scoring runs; a title matching two headings refuses `SECTION_TITLE_AMBIGUOUS`; confirm scoring never runs in either case.
- [x] 2.6 Extract `paper_graph.resolve_section_index(source_roots, root, lineage) -> (path, counts, outline)` from `_verify_source_section_bindings`'s marker → lineage → `segment_markdown` chain; `outline` carries `{title, level, byte_start, byte_end}` per heading — the byte-offset shape the sibling change's dependency needs, never a `{title: count}` memo.
- [x] 2.7 Wire `_verify_source_section_bindings` to call `resolve_section_index`; run the full existing `source-section-binding` suite and confirm zero new failures, behavior and memo semantics unchanged.
- [x] 2.8 Wire `cmd_separate` to call the same `resolve_section_index`; run 2.5 green.
- [x] 2.9 RED: corpus-anchoring tests — an assignment for a `(block, fact)` absent from the assembled corpus's `requires_facts` is reported as unanchored and contributes nothing to coverage.
- [x] 2.10 Wire `separate`'s scoring stage to call `assemble_corpus(enforce_bindings=False)` for anchoring; feed anchored claims into `score_cut`; run 2.9 green.
- [x] 2.11 RED — single-refusal semantics, its own explicit task: a cut carrying overlap AND orphan AND gap simultaneously (the worked-example round 1) raises EXACTLY ONE refusal code, never more than one.
- [x] 2.12 RED — all-classes detail, its own explicit task: that single refusal's detail names EVERY instance of EVERY present class (the overlapping title, both orphaned titles, the gapped block and title) plus all four totals (orphan, overlap, gap, sum); assert on the full detail payload, not just the raised code name.
- [x] 2.13 Implement the fixed-precedence dispatch in `cmd_separate` (`overlap → orphan → gap`): compute all three counts first, then raise ONE code chosen by precedence with a detail built from every counted instance across all classes; confirm 2.11 and 2.12 both green.
- [x] 2.14 RED: orphan-and-gap-with-no-overlap raises `SEPARATION_SECTION_ORPHANED`, naming the gap too; gap-only raises `SEPARATION_NOTATION_GAP`; run green.
- [x] 2.15 RED: `SEPARATION_SECTION_UNCLAIMABLE` fixtures — a named title resolving to a real heading outside the claimable set, and an unmeasured claimable set — both refuse, naming the title/claimable-set or the document/reason respectively.
- [x] 2.16 Wire `SEPARATION_SECTION_UNCLAIMABLE` into `cmd_separate`, checked before overlap/orphan/gap scoring; run 2.15 green.
- [x] 2.17 Register the `separate` subparser, `COMMANDS`/`_COMMANDS` entries, and the `REFUSAL_CLASSIFICATION` entries for the codes landed so far in `paper_cli.py`.
- [x] 2.18 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation`; confirm green. No round persistence yet (Phase 3).

## Phase 3: U3 — Round Record Kind, Persistence, `SEPARATION_ROUND_ABSENT`

- [ ] 3.1 RED: writer/reader tests for `record_separation_round`/`read_separation_rounds` — id shape `separation::{root}::{lineage}::{revision}::round-{n}`, `n` derived (max existing + 1, never supplied), append-only (no reopen), `{}` before `paper/` is scaffolded.
- [ ] 3.2 Implement `record_separation_round`/`read_separation_rounds`/`_separation_record_id` in `paper_declarations.py` — a fourth `declarations`-region record kind through `_set_record`, unchanged; `document_digest` = sha256 of the resolved document's bytes read at scoring time.
- [ ] 3.3 Run 3.1 green.
- [ ] 3.4 RED: replay — a byte-identical, canonicalized cut resubmitted against the latest recorded round for that id prefix records nothing new and returns/re-refuses that same round.
- [ ] 3.5 Implement canonicalization plus the replay check; run 3.4 green.
- [ ] 3.6 RED: `SEPARATION_ROUND_ABSENT` — `concedes_to_round: 7` with no round 7 recorded for this `(root, lineage, revision)` refuses, naming the missing round.
- [ ] 3.7 Wire round lookup and `SEPARATION_ROUND_ABSENT` into `cmd_separate`; run 3.6 green.
- [ ] 3.8 Mutation: a missing round scores 0 instead of refusing (the concede-to-nothing case survives); confirm 3.6's fixture goes red.
- [ ] 3.9 RED: recording ordering — every structurally-valid round records BEFORE the structural refusal fires; the refusal's detail names the recorded round id; a round scoring nonzero (round 1, score 4) is still recorded.
- [ ] 3.10 Wire recording into `cmd_separate` after per-title resolution and claimability, before the overlap/orphan/gap raise; run 3.9 green.
- [ ] 3.11 RED: no-process-state integration — two genuinely separate CLI invocations (the first process has exited); the second reads round 1 from disk alone and scores round 2 correctly.
- [ ] 3.12 Confirm 3.11 passes with no in-process caching leaking state across the process boundary; fix if it does not.
- [ ] 3.13 RED — AST assertion (Decisions F/G): the set of `declarations`-region record kinds reachable from `cmd_separate`'s own call graph is exactly `{"separation"}` — `separate` never records a `binding` under any outcome.
- [ ] 3.14 Confirm 3.13 passes as implemented.
- [ ] 3.15 Mutation: `kind="separation"` → `kind="binding"` in the round writer; confirm the settled-separation-then-`write`-still-refuses-`SECTION_BINDING_ABSENT` e2e test (3.16) goes red under this mutation.
- [ ] 3.16 RED: settled-cut e2e — a cut scoring 0 exits 0, its payload names one `bind` invocation per assignment, no `binding` record exists afterward, and `write` still refuses `SECTION_BINDING_ABSENT`.
- [ ] 3.17 Wire the score-0, exit-0 payload naming every `bind` invocation; run 3.16 green.
- [ ] 3.18 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation`; confirm green.

## Phase 4: U4 — Concession Check, Precedence, `SEPARATION_CONCESSION_REGRESSED`

- [ ] 4.1 RED: concession-recompute tests — `concedes_to_round: n` recomputes BOTH the conceding cut's total and round `n`'s total from disk, never trusting either stored score; an equal-or-lower total is accepted; a strictly higher total refuses `SEPARATION_CONCESSION_REGRESSED` naming both cuts and both totals.
- [ ] 4.2 Implement the concession check in `cmd_separate`, using the round lookup from Phase 3; run 4.1 green.
- [ ] 4.3 RED — ordering, its own explicit, separately-checkable task (Decision E): the concession check runs BEFORE the structural refusal. Construct a conceding cut whose recomputed total is nonzero but not worse than the round it abandons; assert the concession check passes it through to the structural refusal rather than masking it.
- [ ] 4.4 Mutation (proves the ordering is load-bearing, not incidental): swap the call order so the structural refusal runs first; confirm the `SEPARATION_CONCESSION_REGRESSED` fixture from 4.1 becomes structurally unreachable under this mutation — the test exercising it goes red because the structural refusal now intercepts first. This is the ordering defect that is invisible on the happy path alone.
- [ ] 4.5 Restore the correct ordering (concession check first); confirm 4.1 and 4.3 both green again.
- [ ] 4.6 Mutation: `submitted > prior` → `submitted > prior + 1`; confirm the 4→5 fixture goes red (a check that only catches a large jump must not survive an off-by-one weakening).
- [ ] 4.7 RED — stored score is not authority: overwrite a recorded round's stored `score` field to `0` on disk, leaving its `assignments` unchanged; a conceding cut scoring 5 against it still refuses `SEPARATION_CONCESSION_REGRESSED` naming 4 and 5, recomputed from `assignments`.
- [ ] 4.8 Confirm the concession check recomputes strictly from `assignments`, never reading the stored `score` field for comparison; run 4.7 green.
- [ ] 4.9 Mutation: change the comparison to read the stored `score` field instead of recomputing; confirm 4.7 goes red.
- [ ] 4.10 Confirm a regressed concession is never recorded: resubmitting it identically refuses the same way with no growth in round count (extend 3.1's round-count assertions to a refused resubmission).
- [ ] 4.11 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation`; confirm green — the `separate` negotiation loop is complete except the `bind` precondition (Phase 5).

## Phase 5: U6 — Owner Amendment: `BINDING_UNARGUED` Precondition on `bind`

- [ ] 5.0 **Read before starting.** Landing `BINDING_UNARGUED` in `bind_section` makes EVERY existing caller of `bind`/`cmd_bind`/`bind_section` that records without a prior settled round start refusing. Audit every such call site in `tests/test_paper_writing.py` and `tests/test_paper_decisions.py` (the archived `source-section-binding` suite) before writing new tests; each MUST be updated in THIS phase to first record a settled `separate` round (or target an `unmeasured` root) before asserting a successful bind. Getting this wrong reddens the corpus mid-sequence for a reason unrelated to any real defect.
- [ ] 5.1 RED: `settled_round_licensing` tests for all four checks (id/root/lineage/revision match; digest match; score total 0; title-set equality), for both root kinds (`PROSE` via `resolve_lineage`, `INGESTED` via `resolve_ingested_document`).
- [ ] 5.2 Implement `settled_round_licensing(paper_dir, root, lineage, revision, document_digest, qualified_block_id, fact_id, sections)` in `paper_declarations.py`, returning `{"state", "round", "failed_check", "argued_sections", "reason"}`; run 5.1 green.
- [ ] 5.3 RED: no-round-at-all fixture — `bind --sections` with no `separate` round ever recorded for the lineage refuses `BINDING_UNARGUED`, naming the block, fact, root, resolved revision, and the exact `separate --proposal <path>` invocation to run next.
- [ ] 5.4 Add the keyword-only `source_base` param and the `BINDING_UNARGUED` guard to `paper_declarations.bind_section`, gated by `settled_round_licensing`; add `bind --sections` with the same default/help text every sibling subcommand carries; `source_base=None` derives the default and never means "skip the check."
- [ ] 5.5 Run 5.3 green.
- [ ] 5.6 Execute the 5.0 audit: retrofit every existing `bind`/`cmd_bind`/`bind_section` test fixture to first record a settled round via `separate` (or target an unmeasured root); confirm the FULL pre-existing `source-section-binding` suite is green again under the new precondition, with no fixture silently skipped.
- [ ] 5.7 RED: happy-path fixture — a settled round naming the exact `(block, fact)` and the exact title set (order-independent, set equality) licenses the bind; run green.
- [ ] 5.8 RED: scope-mismatch fixtures — a settled round naming a different block, a subset of the argued titles, and a superset of the argued titles each refuse `BINDING_UNARGUED`, naming both title sets verbatim.
- [ ] 5.9 Confirm 5.8 green under the set-equality check (check 4) from 5.2/5.4.
- [ ] 5.10 Mutation (named explicitly, must not be dropped): weaken check 4 from set **equality** to "the argued set is non-empty"; confirm the subset-bind and wrong-block fixtures from 5.8 go red — they are the only fixtures that catch this weakening.
- [ ] 5.11 RED: licence-expiry fixtures — a new revision published under a `PROSE` root voids the licence, naming both revisions; an in-place rewrite of the same filename voids it, naming both digests; an `INGESTED` root's licence expires only by digest, never by revision.
- [ ] 5.12 Confirm 5.11 green under checks 1 and 2.
- [ ] 5.13 Mutation: drop check 2 (digest) from `settled_round_licensing`; confirm the in-place-rewrite fixture (same revision filename, one heading renamed) goes red.
- [ ] 5.14 Mutation: drop check 1 (root/lineage/revision match) from `settled_round_licensing`; confirm the new-revision fixture goes red.
- [ ] 5.15 RED (named explicitly, must not be dropped): call `bind_section` DIRECTLY, bypassing `cmd_bind`/the CLI entirely, with no round recorded; assert it still refuses `BINDING_UNARGUED`.
- [ ] 5.16 Confirm 5.15 passes because the guard lives inside `bind_section` itself, not only in `cmd_bind`. As the mutation proof: temporarily move the check into `cmd_bind` only, confirm 5.15 goes red, then restore the guard to `bind_section`.
- [ ] 5.17 RED: unmeasured-root fixture — a fact whose source root is `unmeasured` records as before with no `BINDING_UNARGUED` refusal, and its payload reports `separation: unmeasured(<reason>)`.
- [ ] 5.18 Confirm 5.17 green; add a dedicated fixture confirming `--reopen` succeeds with no settled round at all, in every state.
- [ ] 5.19 RED: shortcut-closed e2e — `bind` with no round at all refuses `BINDING_UNARGUED`; the same `bind` after a settled `separate` succeeds; `--reopen` succeeds in both states.
- [ ] 5.20 Run 5.19 green; run the full modified `source-section-binding` suite plus the new `BINDING_UNARGUED` tests together.
- [ ] 5.21 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.test_paper_separation`; confirm green, zero new failures beyond the known pre-existing `mechanisms` baseline.

## Phase 6: U5 — Docs, Roster Re-Derivation, Final Gate Re-Run

- [ ] 6.1 Update `.claude/skills/paper-writing/SKILL.md` AND `.claude/skills/paper-writing/references/usage.md` with the two-step loop (`separate` → `bind`) — both files; a doc fix that stops at `SKILL.md` is half a fix (Decision J).
- [ ] 6.2 Confirm both docs use only invented example names — no real lineage, section-title, or paper-id literal.
- [ ] 6.3 Generality sweep: `rg` under `.claude/skills/` and the forge suite for any block id, section title, document filename, paper id, subject word, or revision-pattern literal of the paper being written; confirm empty.
- [ ] 6.4 Re-run `.venv/bin/python -m unittest tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests` (the GATE-0 audit, task 0.1) now that all code has landed; confirm still green.
- [ ] 6.5 Re-derive the refusal roster: execute `reachable_paper_refusal_codes()` and record the MEASURED number in the apply/verify report; never write a predicted number into any artifact ahead of this measurement.
- [ ] 6.6 Confirm `resolve_section_index`'s `outline` return (byte offsets, task 2.6) is importable and callable by a sibling module with no duplication of the marker → lineage → `segment_markdown` chain — a smoke import/call proving the shape, not a behavior change.
- [ ] 6.7 Confirm zero edits landed in `paper_leak.py` or `paper_write.py` — `git diff main -- .claude/skills/paper-writing/scripts/paper_leak.py .claude/skills/paper-writing/scripts/paper_write.py` is empty.
- [ ] 6.8 Confirm nothing was deleted — `git log --diff-filter=D` shows no removed files for this branch.
- [ ] 6.9 Run the Python suite in FOUR chunks (full discover exceeds the 600s foreground timeout, and background runs are killed by memory pressure on this machine): split `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` by module into four roughly-equal chunks and run each in the foreground.
- [ ] 6.10 Run `npm test`; confirm 640/640.
- [ ] 6.11 Confirm the Python result carries exactly ONE known pre-existing failure (`test_proposal_implementation.ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`, over the generic word "mechanisms"); any second failure is this change's and blocks.
- [ ] 6.12 Update `design.md`'s roster line with the measured post-change count (task 6.5's result) and confirm no artifact still carries a forecast number.
