# Tasks: The two declarations a plan owes

**Baseline**: `npm test` on `e5b0c56` = 559 pass, 0 fail, 39.2s. Measure before touching anything.

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | ~550-650 (preservation ~135, profile.ts ~6, SKILL.md ~30, agent ~15, 4 test files ~365) |
| Review budget risk (session budget: 1400 lines) | Low — estimate is 40-46% of budget |
| Chained PRs recommended | No — atomic cross-file coupling (D7 byte-for-byte + D5 doctrine equality span multiple files at once; splitting leaves red intermediate states) |
| Suggested split | Single PR, internal work units below |
| Delivery strategy | single-pr |
| Chain strategy | not applicable — no chaining, no exception |

Decision needed before apply: No — corrected by the orchestrator; the session review budget is 1400 lines, not 400, so the estimate sits well inside it
Chained PRs recommended: No
Chain strategy: not applicable
Review budget risk: Low against the session's 1400-line budget

### Suggested Work Units (internal sequencing inside the one PR)

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|
| 1 | Objective-flow guard rewrite (D5), run against untouched profiles | `npm test -- tests/proposal-deliberation-objective-flow.test.mjs` | N/A — pure test rewrite | revert test file only |
| 2 | Preservation rules + atom (D1-D4) | `npm test -- tests/experimental-deliberation-preservation.test.mjs` | N/A — unit | revert `preservation-experimental.ts` |
| 3 | North/doctrine text move + SKILL.md prose + agent coupling | `npm test -- tests/proposal-deliberation-objective-flow.test.mjs tests/test_agents.py` | N/A — docs/config | revert 3 files together |
| 4 | Fixture repair (publish, initial-revision) | `npm test -- tests/experimental-deliberation-publish.test.mjs tests/experimental-deliberation-initial-revision.test.mjs` | child-process integration (existing harness) | revert fixture edits |

## Phase 1: Cross-domain guard rewrite — highest risk, gate before all else

- [x] 1.1 RED: write `parseDoctrineTable`/triple-match `parseObjective` rewrite per design D5 (row parsing, profile parsing, head-equality comparison) in `tests/proposal-deliberation-objective-flow.test.mjs`, run against **current unmodified** `profile.ts`/`SKILL.md` in both skills.
- [x] 1.2 GATE (ruling 8): if `proposal-deliberation` reddens here, STOP, report to operator, make no further edits. Do not pre-edit the math skill, do not scope the guard down. — GATE DID NOT FIRE: both domains passed unmodified (17/17), proven by executing `node --test tests/proposal-deliberation-objective-flow.test.mjs` directly.
- [x] 1.3 GREEN: confirm both domains pass unmodified — proves parser correctness before any content change. — confirmed, 17/17 pass.
- [x] 1.4 Mutation M13/M14 (design.md): one-word mutation to `experimental` `validated.establishes` and to `proposal-deliberation` `composed.behindWhen`; both tests must go RED; revert — proposal-deliberation file ships unchanged. — anchor count asserted before/after both mutations (rg), fresh-process run went 15/17 (2 failing: the mutated establishes test and the mutated behindWhen test), reverted, `git diff --stat` on proposal-deliberation/profile.ts empty, re-run 17/17 green.

## Phase 2: Preservation rules + atom (D1-D4)

- [x] 2.1 RED: add scenarios in `tests/experimental-deliberation-preservation.test.mjs` for `dataset-declaration-missing`/`repeated`, `validation-scheme-declaration-missing`/`repeated`, `validation-scheme-without-test`, `-without-seeds`, `-without-repetitions`, denylist (`TBD`, `p-value`), novel-test-accepted, seeds-synonym-accepted (ruling 7), dataset-denylist-refused (ruling 6).
- [x] 2.2 GREEN: implement `DECLARATION` factory, `declarations()`, both rule pairs, validation-scheme decomposition (a/b/c) in `preservation-experimental.ts` per D1-D2, D4. — 58/58 green, fresh process.
- [x] 2.3 RED then GREEN: `dataset` atom extraction + normalization (D3) — extract, lose-on-swap, reword-not-loss, verification-tag-strip scenarios. — all four scenarios present and green.
- [x] 2.4 Mutations M1-M12 (design.md table): each edits source, asserts anchor replaced exactly once, fresh-process RED, revert by inverse edit (not `git checkout --`, since the file already carries uncommitted D1-D4 work), GREEN. Do not skip any. — all 12 done. **M12 initially SURVIVED** (0 failures) with the original test set; per this repo's own scar ("a surviving mutation has two explanations"), the test suite was measurably too weak (only ever tested a single stray digit), not the implementation wrong — added `a second, unrelated digit elsewhere in the value does not stand in for a repetitions clause`, re-ran against the still-mutated source (RED), then reverted (GREEN, 58/58). All other 11 mutations went RED on first attempt, confirmed by the specifically targeted test(s), then reverted with `MUTATED`-string grep proving zero leftover artifacts.

## Phase 3: North + SKILL.md + agent coupling

- [x] 3.1 Move `validated.establishes`/`behindWhen` text (design D5 "Proposed moved text") into `profile.ts` and `SKILL.md`'s stage table row together, same commit.
- [x] 3.2 Re-run Phase-1 guard: must pass for both domains now with new text reflected. — 17/17 green.
- [x] 3.3 Add two tutor bullets to `SKILL.md` (dataset-opens, validation-scheme-always-proposed), matching existing 8-bullet voice; carry `renderFromIdea` finding — v1 injects no skeleton, both declarations must already exist in idea/sources.
- [x] 3.4 Correct stale "Creating v1, and the gap nothing enforces" section: retitled "Creating v1, checked by the same gate as every successor"; states `initial-revision-creation.ts` imports and runs `violations()` before any write, same gate as the successor path — verified by reading `initial-revision-creation.ts` itself (line 12 import, lines 83-84 the call), not by trusting the earlier claim.
- [x] 3.5 Update `.claude/agents/experimental-validation.md`: description, end condition, rule enumeration (3 pre-existing + 7 new = 10, grouped by concern rather than a flat count claim), per D6's three edits.
- [x] 3.6 Checked `.claude/agents/experimental-publish.md`: design's finding CONFIRMED by reading it — `stretch: terminal`, enumerates no rule ids, description carries `objective.arrival` verbatim (this change edited only `establishes`/`behindWhen`, not `arrival`). No edit made.
- [x] 3.7 D6 self-deriving enumeration test: added `test_the_validation_agents_rule_enumeration_derives_from_the_module` to `tests/test_agents.py`, deriving the rule-id set from `RULE_ID_LITERAL` regex over `preservation-experimental.ts` (refactored the two cardinality-check call sites so all 11 rule ids appear as literal `rule: "<id>"`, matching this module's own established style) and requiring each to be backtick-mentioned anywhere in the agent body (inclusion OR explicit exclusion) — never requiring every rule to be in the *confirming* list, which would wrongly redden on `report-table-fabricated-value`'s correct omission. Mutations 15 (deleted `dataset-declaration-missing` from the agent) and 16 (added an unmentioned rule id to the module) both proven RED then reverted GREEN.

## Phase 4: Fixture repair — three files, cross-cutting break

- [x] 4.1 `tests/experimental-deliberation-preservation.test.mjs`: `RICH` gains both declaration lines + `kinds(RICH)` gains `'dataset'`; add `otherRules()`/`otherViolations()` filter used only by pre-existing tests, never by new ones (design's named regression-hiding boundary); `PLAIN` gets dedicated two-missing-ids assertion. — done together with Phase 2 (interdependent); 58/58 green.
- [x] 4.2 `tests/experimental-deliberation-publish.test.mjs`: `SEED` fixture gains both declaration lines, placed in their own `## Data and validation` section (outside the `## Protocol` locus the stub planner's replace action targets, so they survive the edit unchanged). 5/5 green.
- [x] 4.3 `tests/experimental-deliberation-initial-revision.test.mjs`: `PROPOSAL_FRAGMENT` gains both lines as extra lines; added `PROPOSAL_FRAGMENT_WITHOUT_DECLARATIONS` and a new v1-blocked-on-missing-declaration integration test mirroring the filled-cell pattern. 8/8 green.

## Phase 5: Byte-for-byte proof (D7) — a check that runs

- [x] 5.1 `git status --porcelain` equals exactly the path allowlist (design D7 §1) — no extra, no missing path. **One deliberate, reported addition beyond design.md's literal D7 list: `tests/test_agents.py`**, required by ruling 9 (task 3.7, dated AFTER design.md and its D7 allowlist), which has no other sensible home for the D6 self-deriving enumeration test — see apply report.
- [x] 5.2 Assert (test, not eyeball) the 4 pre-existing violation ids and 5 pre-existing atom kinds still produced, unrenamed. — added `D7 identity` tests to `tests/experimental-deliberation-preservation.test.mjs`, both green.
- [x] 5.3 `git diff --quiet -- .claude/skills/_core .claude/skills/proposal-deliberation` exits 0 (unless ruling-8 STOP already fired). — exit 0, confirmed; ruling-8 gate never fired (Phase 1).

## Phase 6: Full verification

- [x] 6.1 `npm test` — full suite, compare against 559-pass baseline. — **595 pass, 0 fail, 0 skipped** (corrected: the figure first recorded here was 593, measured before task 5.2's two D7-identity tests landed; 595 was re-measured independently at HEAD by the orchestrator and again by verify).
- [x] 6.2 `.venv/bin/python -m unittest discover -s tests` (3.12, not bare `python3`). — 2783 pass, 6 skipped, 0 fail.
- [x] 6.3 Both must be green before commit. One conventional commit, no AI attribution.
